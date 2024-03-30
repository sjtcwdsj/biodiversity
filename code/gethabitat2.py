
# Calculate the new habitat range based on the extracted initial habitat
# Habitat range was extracted on the grid scale by the species' suitable habitat type and suitable poster range
import sys
import numpy as np
import pandas as pd
import os
from osgeo import gdal,gdalconst,gdal_array
import geopandas as gpd
from shapely import Polygon
'''
1: Cropland 耕地
2: Forest 林地
3: Shrub 灌木
4: Grassland 草地   
5: Water 水体 
6: Sonw/Ice 雪\冰     
7: Barren 荒地
8: Impervious 不透水面 
9: Wetland 湿地 
'''
def gethabitat(habitats):
    if habitats!=habitats:
        return []
    habitats=habitats.split('-')
    res=[]
    for ha in habitats:
        if ha=='Cro':
            continue
        elif ha=='For':
            #林地
            res.append(2)
        elif ha=='Shr':
            #灌木
            res.append(3)
        elif ha=='Gra':
            #草地
            res.append(4)
        elif ha=='Wat' or ha=='Wet':
            #湿地
            res.append(5)
            res.append(9)
        elif ha=='Bar':
            #荒地
            res.append(7)
        elif ha=='Imp':
            continue
    if res==[]:
        res.append(7)
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

#information of species
animalinfo=gpd.read_file('/home/gh/work/data/fixdata/biodiversity/shp/fix_china_animal.shp')
smoddata=gdal.Open('/home/gh/work/BIOFIX/middata/distance.tif')
info=getinfo(smoddata)
anipath='/data/gh/data/china_animal'
key1path='/data/gh/data/animalhabitat/key1'
key2path='/data/gh/data/animalhabitat/key2'

row=40
col=46

for i in range(row):
    for j in range(col):


        if not os.path.exists(f'/data/gh/data/cutCLCD/um-{i}-{j}'):
            continue
        if not os.path.exists(os.path.join(key2path,f'a{i}b{j}')):
            os.mkdir(os.path.join(key2path,f'a{i}b{j}'))

        

        LC=gdal.Open(os.path.join('/data/gh/data/cutCLCD',f'um-{i}-{j}',f'um1990.tif'))
        DEM=gdal.Open(os.path.join('/data/gh/data/cutDEM',f'dem{i}-{j}.tif'))
        uinfo=getinfo(LC)
        anis=gpd.read_file(os.path.join(anipath,f'a{i}b{j}.shp'))




        LCdata=LC.ReadAsArray(0,0)
        DEMdata=DEM.ReadAsArray(0,0)


        for t,item in anis.iterrows():
            id_no=item['id_no']
            name=item['binomial']
            habitats=gethabitat(item['habitat'])
            ele_upper=item['ele_upper']
            ele_lower=item['ele_lower']
            data=gdal_array.LoadFile(os.path.join(key1path,f'a{i}b{j}',f'{name}.tif'))

            
            if ele_upper>ele_lower:
                DEM_choice=(DEMdata>=ele_lower)&(DEMdata<=ele_upper)
                data=data*DEM_choice
            elif ele_upper<ele_lower:
                DEM_choice=(DEMdata>=ele_lower)
                data=data*DEM_choice
            elif ele_upper==ele_lower and ele_upper!=0:
                DEM_choice=(DEMdata>=ele_upper-100)&(DEMdata<=ele_upper+100)
                data=data*DEM_choice


            mask=np.isin(LCdata,habitats)
            data=data*mask

            gdal.UseExceptions()
            savepath=os.path.join(key2path,f'a{i}b{j}',f'{name}.tif')
            driver = gdal.GetDriverByName("GTiff") 
            ds=driver.Create(savepath,data.shape[1],data.shape[0],1,gdal.GDT_Byte,options=['COMPRESS=LZW'])
            band=ds.GetRasterBand(1)
            band.SetNoDataValue(0)
            band.WriteArray(data,0,0)
            ds.SetGeoTransform([uinfo['minx'],30,0,uinfo['maxy'],0,-30])
            ds.SetProjection(LC.GetProjection())
            ds=None

            print(f'\r{i}-{j}-{t}/{anis.shape[0]}')
