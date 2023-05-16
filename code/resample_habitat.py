#把栖息地栅格重采样为较大的像元，然后合并为全中国地图
import numpy as np
import pandas as pd
from osgeo import gdal,osr,gdalconst
import geopandas as gpd
import os
import sys
import shutil
gdal.UseExceptions()
srs=osr.SpatialReference()
srs.ImportFromProj4('+proj=lcc +lat_0=0 +lon_0=105 +lat_1=30 +lat_2=62 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +type=crs')

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

path='/root/work/BIO/new_code/res/ani_range_fix'
anitypes=['AMPHIBIAN','BIRD','MAMMALS','REPTILES']
patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
size=300

for anitype in anitypes:
    if anitype!='BIRD':
        continue
    habitatpath=os.path.join(path,anitype)
    resamplepath=os.path.join(path,f'{anitype}_resample_{size}')
    if os.path.exists(resamplepath):
        shutil.rmtree(resamplepath)
    os.mkdir(resamplepath)
    
    for ID in patchs['ID']:
        opath=os.path.join(habitatpath,f'Habitat_{ID}.tif')
        habitat=gdal.Open(opath)
        info=getinfo(habitat)

        ds=gdal.Warp(os.path.join(resamplepath,f'Habitat_{ID}.tif'),
            habitat,
            format='GTiff',
            creationOptions=['COMPRESS=LZW'],
            outputBounds=[info['minx'],info['miny'],info['maxx'],info['maxy']],
            dstNodata=0,
            dstSRS=srs,
            xRes=size,
            yRes=size,
            resampleAlg=gdalconst.GRA_Average
            )
        ds=None
        print(f'\r {anitype}-{ID}',end='',flush=True)


