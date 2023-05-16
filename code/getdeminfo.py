from osgeo import gdal
import pandas as pd
import numpy as np
import os
import sys
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

res=[]
path='/root/work/BIO/new_code/data/zip2'
ps=os.listdir(path)
for p in ps:
    if p.endswith('.tif'):
        opath=os.path.join(path,p)
        data=gdal.Open(opath)
        info=getinfo(data)
        res.append([opath,info['minx'],info['maxx'],info['miny'],info['maxy']])

res=pd.DataFrame(res,columns=['path','minx','maxx','miny','maxy'])
res.to_csv('/root/work/BIO/new_code/data/DEMinfo.csv',index=0)
