from osgeo import gdal
import geopandas as gpd
import numpy as np
import pandas as pd
import os
import sys


if __name__=="__main__":

    infos=pd.read_csv('/root/work/BIO/new_code/data/CLCDinfo.csv')
    bios=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
    bios.to_crs(crs='epsg:4326')
    IDs=bios['ID']
    
    left=int(sys.argv[1])
    right=int(sys.argv[2])
    paths=np.array(infos['path'])
    years=np.array(infos['year'])

    for i,path in enumerate(paths):
        if i<left or i>=right:
            continue
        for id in IDs:
            IDpath=os.path.join('/root/work/BIO/new_code/res/cuttif_84',f'{id}')
            if not os.path.exists(IDpath):
                os.mkdir(IDpath)
            savepath=os.path.join(IDpath,f'bio_{years[i]}.tif')
            ds=gdal.Warp(
                savepath,path,
                creationOptions=['COMPRESS=LZW'],
                cutlineDSName='/root/work/BIO/new_code/data/patchs.shp',
                cutlineSQL=f"SELECT * from patchs WHERE ID={id}",  #选择shp之中NAME为北京的那个要素
                cropToCutline=True,
                dstNodata=0
            )
            ds=None
            print(f"\rcuting:{years[i]}-{id}",end='',flush=True)

    # geometrys=bios['geometry']
    # for geometry in geometrys:
    #     coords=geometry.exterior.coords[:-1]
    #     xs=[coord[0] for coord in coords]
    #     ys=[coord[1] for coord in coords]
    #     minx=np.min(xs)
    #     maxx=np.max(xs)
    #     miny=np.min(ys)
    #     maxy=np.max(ys)
    #     sear=search(minx,maxx,miny,maxy,infos)
    #     print(minx,maxx,miny,maxy)
    #     print(sear)
    #     break


        





