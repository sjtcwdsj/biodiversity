#将每个物种栖息地范围转为栅格
import numpy as np
import pandas as pd
from osgeo import gdal,gdalconst
import geopandas
import os
import sys
import shutil
import geopandas as gpd

#1 Forest 森林
#2 Savanna 草原
#3 Shrubland 灌木
#4 Grassland 草原
#5 Wetlands 湿地
#6 Rocky Areas 荒地
#8 Desert 荒地（沙漠）
#9,10,11,12,13,15 水体
#14.1 耕地
#14.5 建筑
'''
值:1 Cropland 耕地
值:2 Forest 林地
值:3 Shrub 灌木
值:4 Grassland 草地   
值:5 Water 水体 
值:6 Sonw/Ice 雪\冰     
值:7 Barren 荒地
值:8 Impervious 不透水面 
值:9 Wetland 湿地 
'''
def Code_LC(Code):
    if Code.startswith('1.'):
        return 'For'
    elif Code.startswith('2.') or Code.startswith('4.'):
        return 'Gra'
    elif Code.startswith('3.'):
        return 'Shr'
    elif Code.startswith('5.'):
        return 'Wet'
    elif Code.startswith('6.') or Code.startswith('8.'):
        return 'Bar'
    elif Code.startswith('9.') or Code.startswith('10.') or Code.startswith('11.') \
        or Code.startswith('12.') or  Code.startswith('13.') or  Code.startswith('15.'): 
        return 'Wat'
    elif Code.startswith('14.1'):
        return 'Cro'
    elif Code.startswith('14.5'):
        return 'Imp'
    else:
        return 'None'


highpath='/root/work/BIO/new_code/data/high'
chinapath='/root/work/BIO/new_code/data'
savepath='/root/work/BIO/new_code/res/ani_range'
midpath='/root/work/BIO/new_code/mid/midshp'

anitypes=['AMPHIBIAN','BIRD','MAMMALS','REPTILES']
fields=['binomial','sci_name','binomial','binomial']

DEMinfo=pd.read_csv('/root/work/BIO/new_code/data/DEMinfo.csv')
patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
ushp=patchs.dissolve().envelope
ushp=ushp.tolist()[0]
coords=ushp.exterior.coords[:-1]
xs=[c[0] for c in coords]
ys=[c[1] for c in coords]
cminx=min(xs)
cmaxy=max(ys)
cmaxx=max(xs)
cminy=min(ys)
crange=[cminx,cminy,cmaxx,cmaxy]

def getraster(shp,info,ty,field):
    name=info['name']
    ushp=shp[shp[field]==name]
    midsave=os.path.join(midpath,f'{name}.shp')
    ushp.to_file(midsave)

    ds=gdal.Rasterize(os.path.join(savepath,ty,f'{name}.tif'),
                    midsave,
                    format='GTiff',
                    creationOptions=['COMPRESS=LZW'],
                    outputType=gdalconst.GDT_Byte,
                    xRes=30,yRes=30,
                    noData=0,
                    outputBounds=crange,
                    outputSRS='epsg:32649',
                    # attribute=field,
                    burnValues=1,
                    initValues=0,
                    )
    ds=None

    us=os.listdir(midpath)
    for u in us:
        if u.startswith(name):
            os.remove(os.path.join(midpath,u))
    

if __name__=="__main__":
    for i in range(4):
        anitype=anitypes[i]
        field=fields[i]
        shp=gpd.read_file(os.path.join(chinapath,f'china_{anitype}.shp'))
        info=pd.read_csv(os.path.join(highpath,f'{anitype}_habitats.csv'))
        for i,item in info.iterrows():
            p=os.path.join(savepath,anitype)
            if not os.path.exists(p):
                os.mkdir(p)
            getraster(shp,item,anitype,field)
            quit()


