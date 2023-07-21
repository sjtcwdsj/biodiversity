import geopandas as gpd
from osgeo import gdal,gdalconst
import os
sumdata=gdal.Open('/root/work/BIO/city_rural/res/cr_sum/meansum.tif')
patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
savepath='/root/work/BIO/city_rural/res/cr_sum_patch'

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
for ID in patchs['ID']:
    sampledata=gdal.Open(os.path.join('/root/work/BIO/new_code/res/cuttif_lam',str(ID),'bio_1990.tif'))
    info=getinfo(sampledata)
    ds=gdal.Warp(os.path.join(savepath,f'sum{ID}.tif'),
            sumdata,
            format='GTiff',
            creationOptions=['COMPRESS=LZW'],
            # cutlineDSName='/root/work/BIO/new_code/data/patchs.shp',
            # cutlineSQL=f'SELECT * from patchs WHERE ID={ID}',
            # cropToCutline=True,
            outputBounds=[info['minx'],info['miny'],info['maxx'],info['maxy']],
            dstNodata=0,
            xRes=30,
            yRes=30,
            resampleAlg=gdalconst.GRA_NearestNeighbour
            )
    ds=None
    print(f'\r{ID}',end='',flush=True)