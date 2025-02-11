import numpy as np
import os
from osgeo import gdal,gdal_array,gdalconst
import sys
import pandas as pd


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
arearatio=pd.read_csv('/home/gh/work/BIOFIX/middata/area_ratio.csv')
province=gdal_array.LoadFile('/home/gh/work/BIOFIX/middata/province.tif')
pros=np.unique(province)
ratio_csvs={}
recf_csvs={}
for pro in pros:
    if pro==0:
        continue
    ratio_csvs[pro]=pd.read_csv(f'/home/gh/work/BIOFIX/middata/pro_ratio/{pro}.csv')
    recf_csvs[pro]=pd.read_csv(f'/home/gh/work/BIOFIX/middata/pro_CF/{pro}.csv')
def getmap(key,ur,savepath,ty,path='/data/gh/new_data/loss/info_init'):

    res=np.zeros((4000,4600))   

    def update(item,key,ur,areafix,ty='direct'):
        p=item['PRO']
        if p==0:
            return

        if ur=='u' and item['UR']!=3:
            return
        if ur=='r' and item['UR'] not in [1,2]:
            return

        r=0
        for year in range(1990,2020):
            CF=recf_csvs[p]['CF'].tolist()
            CF=CF[year-1990]
            if CF>1:
                CF=1
            ratio=ratio_csvs[p]['ratio'].tolist()
            ratio=ratio[year-1990]
            if ty=='direct':
                r+=item[f'{key}{year}']*areafix
            else:
                if ur=='u':
                    r+=item[f'c{key}{year}']*CF*ratio*areafix
                else:
                    r+=item[f'c{key}{year}']*CF*(1-ratio)*areafix

        #年均
        r=r/30
        res[int(item['row'])][int(item['col'])]=r
        

    csvs=os.listdir(path)
    for i,p in enumerate(csvs):
        csv=pd.read_csv(os.path.join(path,p))
        areafix=arearatio.loc[arearatio['rc']==p.split('.')[0],'change'].tolist()[0]
        csv.apply(update,axis=1,args=(key,ur,areafix,ty))
        print(f'\r {i}/{len(csvs)}',end='',flush=True)
    
    smoddata=gdal.Open('/home/gh/work/BIOFIX/middata/GHSsmod.tif')
    info=getinfo(smoddata)
    driver = gdal.GetDriverByName("GTiff") 
    ds=driver.Create(savepath,res.shape[1],res.shape[0],1,gdal.GDT_Float32,options=['COMPRESS=LZW'])
    band=ds.GetRasterBand(1)
    band.SetNoDataValue(0)
    band.WriteArray(res,0,0)
    ds.SetGeoTransform([info['minx'],1020,0,info['maxy'],0,-1020])
    ds.SetProjection(smoddata.GetProjection())
    ds=None
    

if __name__=="__main__":
    # key=sys.argv[1]
    # ur=sys.argv[2]
    # savepath=os.path.join('/home/gh/work/BIO_response/result/map',sys.argv[3])
    # getmap(key,ur,savepath)

    getmap('For','r','/home/gh/work/BIO_response/result/map/rFor_direct.tif','direct')
    getmap('For','r','/home/gh/work/BIO_response/result/map/rFor_indirect.tif','indirect')
    getmap('For','u','/home/gh/work/BIO_response/result/map/uFor_direct.tif','direct')
    getmap('For','u','/home/gh/work/BIO_response/result/map/uFor_indirect.tif','indirect')

    getmap('Gra','r','/home/gh/work/BIO_response/result/map/rGra_direct.tif','direct')
    getmap('Gra','r','/home/gh/work/BIO_response/result/map/rGra_indirect.tif','indirect')
    getmap('Gra','u','/home/gh/work/BIO_response/result/map/uGra_direct.tif','direct')
    getmap('Gra','u','/home/gh/work/BIO_response/result/map/uGra_indirect.tif','indirect')

    getmap('Wet','r','/home/gh/work/BIO_response/result/map/rWet_direct.tif','direct')
    getmap('Wet','r','/home/gh/work/BIO_response/result/map/rWet_indirect.tif','indirect')
    getmap('Wet','u','/home/gh/work/BIO_response/result/map/uWet_direct.tif','direct')
    getmap('Wet','u','/home/gh/work/BIO_response/result/map/uWet_indirect.tif','indirect')

    getmap('Bar','r','/home/gh/work/BIO_response/result/map/rBar_direct.tif','direct')
    getmap('Bar','r','/home/gh/work/BIO_response/result/map/rBar_indirect.tif','indirect')
    getmap('Bar','u','/home/gh/work/BIO_response/result/map/uBar_direct.tif','direct')
    getmap('Bar','u','/home/gh/work/BIO_response/result/map/uBar_indirect.tif','indirect')
