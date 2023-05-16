from osgeo import gdal,osr,gdalconst
import pandas as pd
import numpy as np
import os
import sys
import geopandas as gpd

gdal.UseExceptions()
srs=osr.SpatialReference()
srs.ImportFromProj4('+proj=lcc +lat_0=0 +lon_0=105 +lat_1=30 +lat_2=62 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +type=crs')

path='/root/work/BIO/new_code/mid/demmid'
savepath='/root/work/BIO/new_code/res/cutdem_lam'
patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')


for ID in patchs['ID']:
    DEMpath=os.path.join(path,f'DEM{ID}.tif')

    ds=gdal.Warp(os.path.join(savepath,f'DEM{ID}.tif'),
                gdal.Open(DEMpath),
                format='GTiff',
                creationOptions=['COMPRESS=LZW'],
                cutlineDSName='/root/work/BIO/new_code/data/patchs.shp',
                cutlineSQL=f'SELECT * from patchs WHERE ID={ID}',
                cropToCutline=True,
                dstNodata=-999,
                dstSRS=srs,
                xRes=30,
                yRes=30,
                resampleAlg=gdalconst.GRA_NearestNeighbour
                )
    ds=None
    print(f'\r{ID}',end='',flush=True)