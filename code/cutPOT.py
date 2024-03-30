#The Productive potential of cropland data is tailored for the follow-up study
#Quoted from cutCLCD.py

import numpy as np
import pandas as pd
from osgeo import gdal,gdal_array,_gdalconst
import geopandas as gpd
import os

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
smoddata=gdal.Open('/home/gh/work/BIOFIX/middata/GHSsmod.tif')
info=getinfo(smoddata)

pro=smoddata.GetProjection()
CLCDpath='/home/gh/work/data/CLCD'
patchs=gpd.read_file('/home/gh/work/data/fixdata/biodiversity/shp/patchs.shp')
tifpath='/data/gh/data/POTlam'



for year in [1990,2000,2010]:

    data=gdal.Open(f'/data/gh/data/POTlam/pot{year}.tif')
    uinfo=getinfo(data)

    
    row=40 
    col=46 
    for i in range(row):
        for j in range(col):

            if not os.path.exists(f'/data/gh/data/cutCLCD/um-{i}-{j}'):
                continue
            leftx=info['minx']+j*102000
            upy=info['maxy']-i*102000

            xoffset=int(round((leftx-uinfo['minx'])/1020))
            yoffset=int(round((uinfo['maxy']-upy)/1020))

            
            u=data.ReadAsArray(xoffset,yoffset,100,100)
            # if yoffset+3400<=uinfo['row']:
            #     ures=data.ReadAsArray(xoffset,yoffset,3400,3400)
            # else:
            #     ures=np.zeros((3400,3400))
            #     leny=uinfo['row']-yoffset
            #     u=data.ReadAsArray(xoffset,yoffset,3400,leny)
            #     ures[0:leny,:]=u
            
            u[u<0]=-999
            
            print(f'\r{i}-{j}-{year}',end='',flush=True)



            driver = gdal.GetDriverByName("GTiff") 

            ds=driver.Create(f'/data/gh/data/cutPOT/um{year}/a{i}b{j}.tif',u.shape[1],u.shape[0],1,gdal.GDT_Int16,options=['COMPRESS=LZW'])
            band=ds.GetRasterBand(1)
            band.SetNoDataValue(-999)
            band.WriteArray(u,0,0)
            ds.SetGeoTransform([leftx,1020,0,upy,0,-1020])
            ds.SetProjection(pro)
            ds=None
