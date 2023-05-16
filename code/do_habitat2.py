import numpy as np
import pandas as pd
from osgeo import gdal,osr,gdal_array,gdalconst
import geopandas as gpd
import os
import sys
import shutil

gdal.UseExceptions()
srs=osr.SpatialReference()
srs.ImportFromProj4('+proj=lcc +lat_0=0 +lon_0=105 +lat_1=30 +lat_2=62 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +type=crs')

patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
anitypes=['AMPHIBIAN','BIRD','MAMMALS','REPTILES']
fields=['binomial','sci_name','binomial','binomial']
LCtifpath='/root/work/BIO/new_code/res/cuttif_lam'
DEMpath='/root/work/BIO/new_code/res/cutdem_lam'
infopath='/root/work/BIO/new_code/res/bioversity'
savepath='/root/work/BIO/new_code/res/ani_range_fix'

animal_shps={}
# for anitype in anitypes:
#     animal_shps[anitype]=gpd.read_file(f'/root/work/BIO/new_code/data/china_{anitype}.shp')


'''
值:1 Cropland 耕地
值:2 Forest 林地
值:3 Shrub 灌木
值:4 Grassland 草地   
值:5 Water 水体 
值:6 Sonw/Ice 雪\冰     
值:7 Barren 荒地
值:8 Impervious 不透水面 
值:9 Wetland 湿地 
'''

def gethabitat(habitats):
    if habitats!=habitats:
        return []
    habitats=habitats.split('_')
    res=[]
    for ha in habitats:
        if ha=='Cro':
            continue
        elif ha=='For':
            res.append(2)
        elif ha=='Shr':
            res.append(3)
        elif ha=='Gra':
            res.append(4)
        elif ha=='Wat':
            res.append(5)
        elif ha=='Bar':
            res.append(6)
            res.append(7)
        elif ha=='Imp':
            continue
        elif ha=='Wet':
            res.append(9)
    return res

def getinfo(data):
    col=data.RasterXSize
    row=data.RasterYSize
    tr=data.GetGeoTransform()
    minx=tr[0]
    maxy=tr[3]
    pixelW=tr[1]
    pixelH=tr[5]
    maxx=minx+col*pixelW
    miny=maxy+row*pixelH
    info={}
    info['minx']=minx
    info['maxx']=maxx
    info['miny']=miny
    info['maxy']=maxy
    info['pixelW']=pixelW
    info['pixelH']=pixelH
    info['row']=row
    info['col']=col
    return info

def delete(path,name):
    paths=os.listdir(path)
    for p in paths:
        if p.startswith(name):
            u=os.path.join(path,p)
            os.remove(u)

midani_shp='/root/work/BIO/new_code/mid/midani_shp'
def get_habitat(ID,savepath,type='ALL',year=1990):
    LC=gdal.Open(os.path.join(LCtifpath,str(ID),f'bio_{year}.tif'))
    DEM=gdal.Open(os.path.join(DEMpath,f'DEM{ID}.tif'))
    info=pd.read_csv(os.path.join(infopath,f'{ID}.csv'))
    LCdata=LC.ReadAsArray(0,0)
    DEMdata=DEM.ReadAsArray(0,0)

    if type!='ALL':
        info=info[info['type']==type]

    uinfo=getinfo(LC)
    res=np.zeros((uinfo['row'],uinfo['col']))
    
    for i,item in info.iterrows():

        name=item['name']
        ani_shp=animal_shps[type]
        cho=ani_shp[ani_shp['binomial' if type!='BIRD' else 'sci_name']==name]
        id_no=cho['id_no'].tolist()[0]

        # ani_shp=animal_shps[type][animal_shps[type]['binomial' if type!='BIRD' else 'sci_name']==name]
        # ani_shp=ani_shp.to_crs(patchs.crs)
        # pat=patchs[patchs['ID']==ID]
        # try:
        #     ani_shp=ani_shp.dissolve()
        # except:
        #     pass
        # print(pat)
        # try:
        #     ani_shp=gpd.clip(pat,ani_shp)
        # except:
        #     print('ValueError')
        #     pass
        
        # midshppath=os.path.join(midani_shp,f'{name}_{ID}.shp')
        # ani_shp.to_file(midshppath)

        midtifpath=os.path.join(midani_shp,f'{name}_{ID}.tif')
        gdal.UseExceptions()
        ds=gdal.Rasterize(
                midtifpath,
                f'/root/work/BIO/new_code/data/china_{type}_lam.shp',
                format='GTiff',
                creationOptions=['COMPRESS=LZW'],
                outputType=gdalconst.GDT_Byte,
                noData=0,
                outputBounds=[uinfo['minx'],uinfo['miny'],uinfo['maxx'],uinfo['maxy']],
                xRes=30,
                yRes=30,
                # outputSRS=srs,
                # transformerOptions=['resampleAlg=gdalconst.GRA_NearestNeighbour'],
                # width=uinfo['col'],
                # height=uinfo['row'],
                SQLStatement=f"SELECT * from china_{type}_lam WHERE id_no={id_no}",
                # attribute=field,
                burnValues=1,
                initValues=0,
                )
        ds=None
        
        #第一步掩膜(找到范围)
        mask1=gdal_array.LoadFile(midtifpath)
        habitat_choice=LCdata*mask1
        mask1=None

        # delete(midani_shp,f'{name}_{ID}.')
        os.remove(midtifpath)

        habitats=gethabitat(item['habitat'])
        ele_upper=item['ele_upper']
        ele_lower=item['ele_lower']
        category=item['category']
        #第二步掩膜（找到地物类型）
        habitat_choice=np.isin(habitat_choice,habitats)
        #第三步掩膜（找到海拔范围）
        if ele_upper==ele_upper and ele_lower==ele_lower:
            DEM_choice=(DEMdata>=ele_lower)&(DEMdata<=ele_upper)
            mask=habitat_choice*DEM_choice
        else:
            mask=habitat_choice
        res+=mask
    

    driver = gdal.GetDriverByName("GTiff") 
    ds=driver.Create(savepath,uinfo['col'],uinfo['row'],1,gdal.GDT_Int32,options=['COMPRESS=LZW'])
    band=ds.GetRasterBand(1)
    band.SetNoDataValue(0)
    band.WriteArray(res,0,0)
    transform=[uinfo['minx'],uinfo['pixelW'],0,uinfo['maxy'],0,uinfo['pixelH']]
    ds.SetGeoTransform(transform)
    ds.SetProjection(LC.GetProjection())
    ds=None

    

            

    # print(LC.RasterXSize,LC.RasterYSize)
    # print(DEM.RasterXSize,DEM.RasterYSize)

if __name__=="__main__":
    anitype=sys.argv[1]
    animal_shps[anitype]=gpd.read_file(f'/root/work/BIO/new_code/data/china_{anitype}_lam.shp')
    # for anitype in anitypes:
    apath=os.path.join(savepath,anitype)
    if os.path.exists(apath):
        shutil.rmtree(apath)
    os.mkdir(apath)
    for ID in patchs['ID']:
        get_habitat(ID,os.path.join(apath,f'Habitat_{ID}.tif'),type=anitype)
        print(f'\r doing-{anitype}-{ID}',end='',flush=True)
