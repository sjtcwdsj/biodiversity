
from osgeo import gdal,osr,gdalconst
import pandas as pd
import numpy as np
import os
import sys
import geopandas as gpd

gdal.UseExceptions()
srs=osr.SpatialReference()
srs.ImportFromProj4('+proj=lcc +lat_0=0 +lon_0=105 +lat_1=30 +lat_2=62 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +type=crs')

#Convert the habitat loss pixels of area ID 10 in 2000 to tif file format
ID=10
year=2000

patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
IDinfo=pd.read_csv('/mnt/d5/GH/work/BIO/fix/code/IDinfo.csv')
csv=pd.read_csv(f'/mnt/d5/GH/work/BIO/fix/res/loss/loss_indirect_fix/VU/{ID}_id.csv')
csv=csv[csv['year']==year]

row=int(IDinfo.loc[IDinfo['ID']==ID,'row'])
col=int(IDinfo.loc[IDinfo['ID']==ID,'col'])

geometry=patchs.loc[patchs['ID']==ID,'geometry'].tolist()[0]
xys=geometry.exterior.coords[:-1]
xs=[item[0] for item in xys]
ys=[item[1] for item in xys]
minx=min(xs)
maxy=max(ys)
maxx=max(xs)
miny=min(ys)


res=np.zeros((row,col))
for i,item in csv.iterrows():
    r=int(item['row'])
    c=int(item['col'])
    res[r,c]=item['value']


driver = gdal.GetDriverByName("GTiff") 
ds=driver.Create(f'/mnt/d5/GH/work/TP/mid/sample.tif',col,row,1,gdal.GDT_Int32,options=['COMPRESS=LZW'])
band=ds.GetRasterBand(1)
band.SetNoDataValue(0)
band.WriteArray(res,0,0)
ds.SetGeoTransform([minx,30,0,maxy,0,-30])
ds.SetProjection(srs.ExportToWkt())
ds=None
