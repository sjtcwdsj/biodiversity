# CLCD data was cropped for subsequent research

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
#GHS-SMOD data
smoddata=gdal.Open('/home/gh/work/BIOFIX/middata/GHSsmod.tif')
info=getinfo(smoddata)

pro=smoddata.GetProjection()
CLCDpath='/home/gh/work/data/CLCD'
patchs=gpd.read_file('/home/gh/work/data/fixdata/biodiversity/shp/patchs.shp')
tifpath='/home/gh/work/data/fixdata/biodiversity/cuttif_lam'

# The whole China can be divided into 3940*4580 blocks with a resolution of 1020m, and each block contains 34 × 34 30m grids
# If divided into 197 by 229 blocks, each block contains 34*20=680 by 680 grids, which is 680*30=20400 meters
# That is, each block is a 680*680 raster map with a resolution of 30m and a 20*20 map with a resolution of 1020m.

# Suppose we need a 3400*3400 raster with a resolution of 30m and an indicator with a resolution of 100*100 with a resolution of 1020m
# Then, each block will be 102000m long.
# In other words, within China, China needs to be divided into 3940*1020/102000=39.4 × 4580*1020/102000=45.8 blocks
# Need to ensure that the number of blocks is an integer.
# Therefore, the scope of China is divided into 40 by 46 blocks, each block contains a 30m grid of 3400*3400.
#(i.e. 1020 grid of 4000*4600)
# There are 2040 and 680 30m resolution grids and 60 and 20 1020m resolution grids, respectively.
# For example, for a block numbered 39/45, you only need to find the first 2040 or 680 grids for data analysis.

#整个中国范围使用1020m分辨率区块可以分成3940*4580个图块，每个图块包含34乘34个30m栅格
#如果分成197乘229个区块，则每个图块包含34*20=680乘680个栅格，也就是680*30=20400米
#也就是，每个图块是30m分辨率的680*680栅格图和1020m分辨率20*20的指示图。

#假设，我们需要30m分辨率的3400*3400的栅格图和1020m分辨率100*100的指示图
#那么，每个图块会长达102000m。
#也就是说，在中国范围内，需要将中国区分为3940*1020/102000=39.4乘4580*1020/102000=45.8个图块
#需要保证图块数为整数。
#因此，将中国范围分为40乘46个图块，每个图块包含3400*3400的30m栅格，
#(也就是 4000*4600的1020栅格)
#分别和原先多出了2040和680个30m分辨率栅格和60和20个1020m分辨率的栅格。
#也就是说，对于编号为39/45的图块，只需要寻找其前2040或680的栅格进行数据分析即可。

for year in range(1990,2021):
    if year<2020:
        continue

    data=gdal.Open(f'/data/gh/data/CLCDlam/CLCD{year}.tif')
    uinfo=getinfo(data)

    
    row=40 
    col=46 
    for i in range(row):
        for j in range(col):
            leftx=info['minx']+j*102000
            upy=info['maxy']-i*102000

            xoffset=int(round((leftx-uinfo['minx'])/30))
            yoffset=int(round((uinfo['maxy']-upy)/30))

            

            if yoffset+3400<=uinfo['row']:
                ures=data.ReadAsArray(xoffset,yoffset,3400,3400)
            else:
                ures=np.zeros((3400,3400))
                leny=uinfo['row']-yoffset
                u=data.ReadAsArray(xoffset,yoffset,3400,leny)
                ures[0:leny,:]=u
            
            if np.sum(ures)==0:
                continue
            
            print(f'\r{i}-{j}-{year}',end='',flush=True)



            driver = gdal.GetDriverByName("GTiff") 

            if not os.path.exists(f'/data/gh/data/cutCLCD/um-{i}-{j}'):
                os.mkdir(f'/data/gh/data/cutCLCD/um-{i}-{j}')

            #Save as 40 x 46 = 1840  blocks
            ds=driver.Create(f'/data/gh/data/cutCLCD/um-{i}-{j}/um{year}.tif',ures.shape[1],ures.shape[0],1,gdal.GDT_Int16,options=['COMPRESS=LZW'])
            band=ds.GetRasterBand(1)
            band.SetNoDataValue(0)
            band.WriteArray(ures,0,0)
            ds.SetGeoTransform([leftx,30,0,upy,0,-30])
            ds.SetProjection(pro)
            ds=None

    
