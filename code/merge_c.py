
from osgeo import gdal,osr
import geopandas as gpd
import numpy as np
import pandas as pd
import os
import sys
import math


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

def merge(results,savepath,srs,func=lambda x:x):
    datas=[]
    minxs=[]
    maxxs=[]
    minys=[]
    maxys=[]
    for path in results:
        data=gdal.Open(path)
        datas.append(data)
        info=getinfo(data)
        minxs.append(info['minx'])
        maxxs.append(info['maxx'])
        minys.append(info['miny'])
        maxys.append(info['maxy'])

        pixelW=info['pixelW']
        pixelH=info['pixelH']
    minx=np.min(minxs)
    maxx=np.max(maxxs)
    miny=np.min(minys)
    maxy=np.max(maxys)

    col=int(math.ceil((maxx-minx)/pixelW))
    row=int(math.ceil((miny-maxy)/pixelH))
    res=np.zeros((row,col))

    for data in datas:
        info=getinfo(data)
        
        
        xoffset=int(round((info['minx']-minx)/pixelW))
        if xoffset<0:
            xoff=0
        else:
            xoff=xoffset
        yoffset=int(round((info['maxy']-maxy)/pixelH))
        if yoffset<0:
            yoff=0
        else:
            yoff=yoffset

        rowlen=info['row']
        if yoffset<0:
            rowlen=rowlen+yoffset
        collen=info['col']
        if xoffset<0:
            collen=collen+xoffset
        # print(yoff,rowlen,xoff,collen)
        datap=data.ReadAsArray(0 if xoffset>0 else abs(xoffset),0 if yoffset>0 else abs(yoffset),collen,rowlen)
        mid=res[yoff:yoff+rowlen,xoff:xoff+collen]
        mid[mid==0]=datap[mid==0]
        res[yoff:yoff+rowlen,xoff:xoff+collen]=mid

        res=func(res,{'yoff':yoff,'xoff':xoff,'rowlen':rowlen,'collen':collen,'p':datap})

    driver = gdal.GetDriverByName("GTiff") 
    ds=driver.Create(savepath,col,row,1,gdal.GDT_Float32,options=['COMPRESS=LZW'])
    band=ds.GetRasterBand(1)
    band.SetNoDataValue(0)
    band.WriteArray(res,0,0)
    transform=[minx,pixelW,0,maxy,0,pixelH]
    ds.SetGeoTransform(transform)
    ds.SetProjection(srs.ExportToWkt())
    ds=None


if __name__=="__main__":

    def fixline(data,info):
        data[info['yoff']-1,info['xoff']:info['xoff']+info['collen']]=data[info['yoff'],info['xoff']:info['xoff']+info['collen']]
        data[info['yoff']:info['yoff']+info['rowlen'],info['xoff']-1]=data[info['yoff']:info['yoff']+info['rowlen'],info['xoff']]
        data[info['yoff']+info['rowlen']-1,info['xoff']:info['xoff']+info['collen']]=data[info['yoff']+info['rowlen']-2,info['xoff']:info['xoff']+info['collen']]
        data[info['yoff']:info['yoff']+info['rowlen'],info['xoff']+info['collen']-1]=data[info['yoff']:info['yoff']+info['rowlen'],info['xoff']+info['collen']-2]
        
        return data

    gdal.UseExceptions()
    srs=osr.SpatialReference()
    srs.ImportFromProj4('+proj=lcc +lat_0=0 +lon_0=105 +lat_1=30 +lat_2=62 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +type=crs')



    savepath='/root/work/BIO/new_code/res/ani_range_fix/china'
    path='/root/work/BIO/new_code/res/ani_range_fix'
    anitypes=['AMPHIBIAN','BIRD','MAMMALS','REPTILES']
    size=300
    for anitype in anitypes:
        if anitype!='BIRD':
            continue
    # anitype='REPTILES'
        opath=os.path.join(path,f'{anitype}_resample_{size}')
        paths=os.listdir(opath)
        up=[]
        for p in paths:
            if p.endswith('.tif'):
                up.append(os.path.join(opath,p))
        merge(up,os.path.join(savepath,f'{anitype}_habitat.tif'),srs,func=fixline)