#The GHS-SMOD data is tailored for the follow-up study
#Quoted from cutCLCD.py

import numpy as np
import pandas as pd
from osgeo import gdal,gdal_array,_gdalconst
import geopandas as gpd
import os


#(3940,4580)
#中国被分成了20400*20400个区块。
#每个区块包含20400/1020=20个 1020分辨率像元

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


#(3940,4580)
smoddata=gdal.Open('/home/gh/work/BIOFIX/middata/distance.tif')
info=getinfo(smoddata)


row=40
col=46



for i in range(row):
    for j in range(col):
        if not os.path.exists(f'/home/gh/work/BIOFIX/middata/cutCLCD/um-{i}-{j}'):
            continue
        leftx=info['minx']+j*102000
        upy=info['maxy']-i*102000
        lcol=100
        lrow=100
        if j*100+100>info['col']:
            lcol=info['col']-j*100
        if i*100+100>info['row']:
            lrow=info['row']-i*100

        data=np.zeros((100,100))
        u=smoddata.ReadAsArray(j*100,i*100,lcol,lrow)
        data[:lrow,:lcol]=u

        
        driver = gdal.GetDriverByName("GTiff") 
        ds=driver.Create(f'/home/gh/work/BIOFIX/middata/cutD/di-{i}-{j}.tif',100,100,1,gdal.GDT_Float32,options=['COMPRESS=LZW'])
        
        band=ds.GetRasterBand(1)
        band.SetNoDataValue(-3.40282306e+38)
        band.WriteArray(data,0,0)
        ds.SetGeoTransform([leftx,1020,0,upy,0,-1020])
        ds.SetProjection(smoddata.GetProjection())
        ds=None
