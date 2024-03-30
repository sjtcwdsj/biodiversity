#The DEM data is tailored for the follow-up study
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
CLCDpath='/home/gh/work/data/CLCD'
patchs=gpd.read_file('/home/gh/work/data/fixdata/biodiversity/shp/patchs.shp')
tifpath='/data/gh/data/DEMlam'



minxs=[]
maxxs=[]
minys=[]
maxys=[]
datas=[]

cols=[]
rows=[]


for pa in os.listdir(tifpath):
    # print(f'\r reading-{ID}',end='',flush=True)
    p=os.path.join(tifpath,pa)
    tifdata=gdal.Open(p)
    datas.append(p)
    info=getinfo(tifdata)
    minxs.append(info['minx'])
    maxxs.append(info['maxx'])
    minys.append(info['miny'])
    maxys.append(info['maxy'])
    cols.append(info['col'])
    rows.append(info['row'])
    # print(info['col'],info['row'])
    # assert info['col']>=3400
    # assert info['row']>=3400

def search(uminx,umaxx,uminy,umaxy):
    tres=[]
    for i in range(len(datas)):
        if uminx<=maxxs[i] and umaxx>=minxs[i]:
            if uminy<=maxys[i] and umaxy>=minys[i]:
                tres.append(i)
    return tres


row=40 
col=46 


sinfo=getinfo(smoddata)
for i in range(row):
    for j in range(col):

        leftx=sinfo['minx']+j*102000
        rightx=sinfo['minx']+(j+1)*102000
        upy=sinfo['maxy']-i*102000
        downy=sinfo['maxy']-(i+1)*102000
        da=search(leftx,rightx,downy,upy)
        if len(da)==0:
            continue
        
        
        ures=np.zeros((3400,3400))
        ures=ures-999
        for d in da:

            mdata=gdal.Open(datas[d])

            xoffset=int(round((leftx-minxs[d])/30))
            yoffset=int(round((maxys[d]-upy)/30))

            tcol=int(round((maxxs[d]-minxs[d])/30))
            trow=int(round((maxys[d]-minys[d])/30))


            if tcol>=3400:
                if xoffset>0:
                    xt=0
                    xu=xoffset
                    if tcol-xoffset<3400:
                        xlen=tcol-xoffset
                    else:
                        xlen=3400
                else:
                    xt=abs(xoffset)
                    xu=0
                    xlen=3400+xoffset
            else:
                if xoffset>0:
                    xt=0
                    xu=xoffset
                    xlen=tcol-xoffset
                else:
                    xt=abs(xoffset)
                    xu=0
                    if tcol+abs(xoffset)<=3400:
                        xlen=tcol
                    else:
                        xlen=3400+xoffset
            if trow>=3400:
                if yoffset>0:
                    yt=0
                    yu=yoffset
                    if trow-yoffset<3400:
                        ylen=trow-yoffset
                    else:
                        ylen=3400
                else:
                    yt=abs(yoffset)
                    yu=0
                    ylen=3400+yoffset
            else:
                if yoffset>0:
                    yt=0
                    yu=yoffset
                    ylen=trow-yoffset
                else:
                    yt=abs(yoffset)
                    yu=0
                    if trow+abs(yoffset)<3400:
                        ylen=trow
                    else:
                        ylen=3400+yoffset


            # print(yoffset,xoffset)
            # print(xu,yu,xlen,ylen)
            # print(yt,yt+ylen,xt,xt+xlen)
            key=ures[yt:yt+ylen,xt:xt+xlen]
            him=mdata.ReadAsArray(xu,yu,xlen,ylen)
            key[key==-999]=him[key==-999]
            ures[yt:yt+ylen,xt:xt+xlen]=key

        print(f'\r{i}-{j}',end='',flush=True)



        sampledata=gdal.Open(datas[0])
        info=getinfo(sampledata)
        driver = gdal.GetDriverByName("GTiff") 


        ds=driver.Create(f'/data/gh/data/cutDEM/dem{i}-{j}.tif',ures.shape[1],ures.shape[0],1,gdal.GDT_Int16,options=['COMPRESS=LZW'])
        band=ds.GetRasterBand(1)
        band.SetNoDataValue(-999)
        band.WriteArray(ures,0,0)
        ds.SetGeoTransform([leftx,30,0,upy,0,-30])
        ds.SetProjection(sampledata.GetProjection())
        ds=None



# data=smoddata.ReadAsArray(0,0)
# print(data.shape)
