#找到每个物种栖息地范围对应的patch
import numpy as np
import pandas as pd
import geopandas as gpd
import os

highpath='/root/work/BIO/new_code/data/high'
chinapath='/root/work/BIO/new_code/data'
savepath='/root/work/BIO/new_code/res/ani_range'
midpath='/root/work/BIO/new_code/mid/midshp'

anitypes=['AMPHIBIAN','BIRD','MAMMALS','REPTILES']
fields=['binomial','sci_name','binomial','binomial']

DEMinfo=pd.read_csv('/root/work/BIO/new_code/data/DEMinfo.csv')
patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
patchs=patchs.to_crs('epsg:4326')

for i in range(4):
    anitype=anitypes[i]
    field=fields[i]
    shp=gpd.read_file(os.path.join(chinapath,f'china_{anitype}.shp'))
    shp=shp.to_crs('epsg:4326')
    info=pd.read_csv(os.path.join(highpath,f'{anitype}_habitats.csv'))
    for name in info['name']:
        print(f'\r{anitype}-{name}',end='',flush=True)
        choice=shp[shp[field]==name]
        choice=choice.dissolve()
        res=gpd.sjoin(patchs,choice)
        resID=list(res['ID'])
        IDs=''
        for ID in resID:
            IDs+='_'
            IDs+=str(ID)
        info.loc[info['name']==name,'IDs']=IDs
    info.to_csv(os.path.join('/root/work/BIO/new_code/data/high2',f'{anitype}_infos.csv'),index=0)



