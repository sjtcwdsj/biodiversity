from osgeo import gdal,osr,gdalconst
import pandas as pd
import numpy as np
import os
import sys
import geopandas as gpd
import shutil
gdal.UseExceptions()
srs=osr.SpatialReference()
srs.ImportFromProj4('+proj=lcc +lat_0=0 +lon_0=105 +lat_1=30 +lat_2=62 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +type=crs')

path='/root/work/BIO/new_code/res/cuttif_84'
savepath='/root/work/BIO/new_code/res/cuttif_lam'
patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
Dpath='/root/work/BIO/new_code/res/cutdem_lam'   
    


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
if __name__=="__main__":
    left=int(sys.argv[1])
    right=int(sys.argv[2])
    for ID in patchs['ID']:
        if ID<left or ID>=right:
            continue
        upath=os.path.join(savepath,str(ID))
        if os.path.exists(upath):
            shutil.rmtree(upath)
        os.mkdir(upath)

        DEM=gdal.Open(os.path.join(Dpath,f'DEM{ID}.tif'))
        info=getinfo(DEM)

        for year in range(1990,2021):
            DEMpath=os.path.join(path,str(ID),f'bio_{year}.tif')
            ds=gdal.Warp(os.path.join(upath,f'bio_{year}.tif'),
                        gdal.Open(DEMpath),
                        format='GTiff',
                        creationOptions=['COMPRESS=LZW'],
                        # cutlineDSName='/root/work/BIO/new_code/data/patchs.shp',
                        # cutlineSQL=f'SELECT * from patchs WHERE ID={ID}',
                        # cropToCutline=True,
                        outputBounds=[info['minx'],info['miny'],info['maxx'],info['maxy']],
                        dstNodata=0,
                        dstSRS=srs,
                        xRes=30,
                        yRes=30,
                        resampleAlg=gdalconst.GRA_NearestNeighbour
                        )
            ds=None
            print(f'\r{ID}-{year}',end='',flush=True)
