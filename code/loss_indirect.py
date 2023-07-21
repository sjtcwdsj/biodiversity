from osgeo import gdal,gdal_array
import time
import geopandas as gpd
import numpy as np
import pandas as pd
import os
import sys
import shutil

#计算栖息地损失的总面积(x1年到x2年)---直接侵占
haibitat_path='/root/work/BIO/new_code/res/ani_all'
patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
tifpath='/root/work/BIO/new_code/res/cuttif_lam'
#城市mask数据
maskpath='/root/work/BIO/city_rural/res/cr_sum_patch'

potancsv=pd.read_csv('/root/work/BIO/fix/res/loss/potancsv/thres.csv',index_col='year')

#CR：极度濒危  EN：濒危 VU：易危  NT：近危  LC:几乎不关注
# anitypes=['AMPHIBIAN','BIRD','MAMMALS','REPTILES']
anitypes=['CR','EN','VU','NT']
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




def getlossall(ID,savepath):
    starttime=time.time()
    habitatopath=os.path.join(haibitat_path,f'Habitat_{ID}.tif')
    IDpath=os.path.join(tifpath,str(ID))
    habitat=gdal.Open(habitatopath)
    uinfo=getinfo(habitat)
    mask=habitat.ReadAsArray(0,0)
    # thres=np.max(mask)*0.1
    citymask=gdal_array.LoadFile(os.path.join(maskpath,f'sum{ID}.tif'))
    
    hamask=mask.copy()
    hamask[hamask>0]=1
    # cr_mask=gdal.Open(os.path.join(maskpath,f'sum{ID}.tif'))
    # cr=cr_mask.ReadAsArray(0,0)
    # cr[cr>thres]=1
    # cr[cr<=thres]=0

    respd=None

    for year in range(1990,2020):
        thekey=potancsv.loc[year,'thekey']

        year1_d=gdal_array.LoadFile(os.path.join(IDpath,f'bio_{year}.tif'))
        year2_d=gdal_array.LoadFile(os.path.join(IDpath,f'bio_{year+1}.tif'))
        # year1_d=gdal.Open(os.path.join(IDpath,f'bio_{year}.tif'))
        # year1_d=year1_d.ReadAsArray(0,0)
        # year2_d=gdal.Open(os.path.join(IDpath,f'bio_{year+1}.tif'))
        # year2_d=year2_d.ReadAsArray(0,0)

        #栖息地掩膜
        lc1=year1_d*hamask
        lc2=year2_d*hamask

        #耕地
        lc2=(lc2==1)
        oc=lc1*lc2


        #剔除没有变化的耕地
        oc[oc==1]=0
        loss1=oc   

        #城市mask
        cmask=(citymask>=thekey)
        loss1*=cmask

        cityinfo=citymask[loss1>0]
        




        endtime=time.time()
        print(f'\r{ID}-{year}-{(endtime-starttime):.2f}',end='',flush=True)

        tpd={}
        wh=np.where(loss1>0)
        tpd['row']=wh[0]
        tpd['col']=wh[1]
        tpd['value']=loss1[wh]
        tpd['cityinfo']=cityinfo
        tpd=pd.DataFrame(tpd)
        tpd['year']=[year]*tpd.shape[0]
        tpd['num']=mask[wh[0],wh[1]]

    
        if respd is None:
            respd=tpd
        else:
            respd=pd.concat([respd,tpd],axis=0)
    respd.to_csv(os.path.join(savepath,f't{ID}.csv'),index=0)

 

    
    
    
    
    
    # #loss1：被侵占的栖息地类型
    # driver = gdal.GetDriverByName("GTiff") 
    # ds=driver.Create(os.path.join(savepath,f'{anitype}-{ID}_loss1.tif'),uinfo['col'],uinfo['row'],len(uloss1),gdal.GDT_Int32,options=['COMPRESS=LZW'])
    # for b in range(len(uloss1)):
    #     band=ds.GetRasterBand(b+1)
    #     band.SetNoDataValue(0)
    #     band.WriteArray(uloss1[b],0,0)
    # transform=[uinfo['minx'],uinfo['pixelW'],0,uinfo['maxy'],0,uinfo['pixelH']]
    # ds.SetGeoTransform(transform)
    # ds.SetProjection(habitat.GetProjection())
    # ds=None





if __name__=="__main__":
    savepath='/root/work/BIO/fix/res/loss/loss_indirect_all'

    # for anitype in anitypes:
    #     if anitype=='CR' or anitype=='EN':
    #         continue
    #     opath=os.path.join(savepath,anitype)
    #     if os.path.exists(opath):
    #         shutil.rmtree(opath)
    #     os.mkdir(opath)
    for ID in patchs['ID']:
        if ID <19:
            continue
        getlossall(ID,savepath)