import pandas as pd
import numpy as np
import geopandas as gpd
from osgeo import gdal,gdalconst
import os
import sys
import shutil

#将土地覆盖聚合起来(900m*900m)
#用行政区的城市进行数据校准

patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
tifpath='/root/work/BIO/new_code/res/cuttif_lam'
midpath='/root/work/BIO/city_rural/mid'
savepath='/root/work/BIO/city_rural/res/cr_sum'
statpath='/root/work/BIO/city_rural/res/statpatch'

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


# us=dir(gdalconst)
# for u in us:
#     if 'GRA' in u:
#         print(u)
year=2020
minxs=[]
maxxs=[]
minys=[]
maxys=[]
datas=[]
gdal.UseExceptions()
for ID in patchs['ID']:
    # print(f'\r reading-{ID}',end='',flush=True)
    p=os.path.join(tifpath,str(ID),f'bio_{year}.tif')
    tifdata=gdal.Open(p)
    datas.append(p)
    info=getinfo(tifdata)
    minxs.append(info['minx'])
    maxxs.append(info['maxx'])
    minys.append(info['miny'])
    maxys.append(info['maxy'])

def search(uminx,umaxx,uminy,umaxy):
    tres=[]
    for i in range(len(datas)):
        if uminx<=maxxs[i] and umaxx>=minxs[i]:
            if uminy<=maxys[i] and umaxy>=minys[i]:
                tres.append(i)
    return tres


minx=np.min(minxs)
maxx=np.max(maxxs)
miny=np.min(minys)
maxy=np.max(maxys)

col=int(round((maxx-minx)/900))
row=int(round((maxy-miny)/900))

res=np.zeros((row,col))

for i in range(row):
    for j in range(col):

        leftx=minx+j*900
        rightx=minx+(j+1)*900
        upy=maxy-i*900
        downy=maxy-(i+1)*900
        da=search(leftx,rightx,downy,upy)
        if len(da)==0:
            continue

        ures=np.zeros((30,30))
        for d in da:

            mdata=gdal.Open(datas[d])

            xoffset=int(round((leftx-minxs[d])/30))
            yoffset=int(round((maxys[d]-upy)/30))

            tcol=int(round((maxxs[d]-minxs[d])/30))
            trow=int(round((maxys[d]-minys[d])/30))

            if xoffset>0:
                xt=0
                xu=xoffset
                if tcol-xoffset<30:
                    xlen=tcol-xoffset
                else:
                    xlen=30
            else:
                xt=abs(xoffset)
                xu=0
                xlen=30+xoffset
            if yoffset>0:
                yt=0
                yu=yoffset
                if trow-yoffset<30:
                    ylen=trow-yoffset
                else:
                    ylen=30
            else:
                yt=abs(yoffset)
                yu=0
                ylen=30+yoffset

            # mid=mdata.ReadAsArray(xu,yu,xlen,ylen)
            # mid2=ures[yt:yt+ylen,xt:xt+xlen]
            # print(xu,yu,xt,yt,xlen,ylen)
            # mid=mdata.ReadAsArray(0,4000)
            ures[yt:yt+ylen,xt:xt+xlen]=mdata.ReadAsArray(xu,yu,xlen,ylen)
        
        ures[ures!=8]=0
        ures[ures==8]=1
        tmean=np.mean(ures)
        res[i][j]=tmean
        print(f'\r{i}-{j}-{tmean}',end='',flush=True)


sampledata=gdal.Open(datas[0])
info=getinfo(sampledata)
driver = gdal.GetDriverByName("GTiff") 
ds=driver.Create('/root/work/BIO/city_rural/res/cr_sum/meansum.tif',res.shape[1],res.shape[0],1,gdal.GDT_Float32,options=['COMPRESS=LZW'])
band=ds.GetRasterBand(1)
band.SetNoDataValue(0)
band.WriteArray(res,0,0)
ds.SetGeoTransform([minx,900,0,maxy,0,-900])
ds.SetProjection(sampledata.GetProjection())
ds=None

        






    # res=np.zeros((info['row'],info['col']))
    # print(res.shape[0]%30,res.shape[1]%30)
    # break
    # for year in range(1990,2021):
    #     tifdata=gdal.Open(os.path.join(tifpath,str(ID),f'bio_{year}.tif'))
    #     info=getinfo(tifdata)




        # data=tifdata.ReadAsArray(0,0)
        # data[data!=8]=0
        # data[data==8]=1
        # driver=gdal.GetDriverByName('GTiff')

        # ds=driver.Create(os.path.join(midpath,f'{ID}_{year}.tif'),info['col'],info['row'],1,gdal.GDT_Float32,options=['COMPRESS=LZW'])
        # band=ds.GetRasterBand(1)
        # band.SetNoDataValue(0)
        # band.WriteArray(data,0,0)
        # ds.FlushCache()
        # ds.SetGeoTransform(tifdata.GetGeoTransform())
        # ds.SetProjection(tifdata.GetProjection())
        # ds=None



        # # print(help(gdal.WarpOptions))
        # ds2=gdal.Warp(os.path.join(savepath,f'cr{ID}.tif'),
        #     os.path.join(midpath,f'{ID}_{year}.tif'),
        #     format='GTiff',
        #     outputType=gdalconst.GDT_Float32,
        #     creationOptions=['COMPRESS=LZW'],
        #     dstNodata=-999,
        #     outputBounds=[info['minx'],info['miny'],info['maxx'],info['maxy']],
        #     xRes=900,
        #     yRes=900,
        #     resampleAlg=gdalconst.GRA_NearestNeighbour,
        #     )
        # ds2=None
        # os.remove(os.path.join(midpath,f'{ID}_{year}.tif'))
        # quit()
