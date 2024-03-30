# CF= Total potential of occupied arable land (PD)/ Total potential of newly added arable land (PI)
# A value per year that represents what percentage of farmland expansion per year we want to identify as farmland migration.
# On the original basis, it is assumed that all farmland migrations are broken down by province

import pandas as pd
import numpy as np
import os
import sys
from osgeo import gdal,gdal_array







province=gdal_array.LoadFile('/home/gh/work/BIOFIX/middata/province.tif')
pros=np.unique(province)
ks={}
for pro in pros:
    if pro==0:
        continue
    ks[pro]={'year':list(range(1990,2020)),'PD':[0]*30,'PI':[0]*30,'Imp':[0]*30,'cEat':[0]*30,'CF':[0]*30}



infopath='/data/gh/new_data/loss/info_init_all'


row=40
col=46


PD=0
PI=0

for i in range(row):
    for j in range(col):
        if not os.path.exists(f'/data/gh/data/cutCLCD/um-{i}-{j}'):
            continue

        data=pd.read_csv(os.path.join(infopath,f'a{i}b{j}.csv'))
        data=data[data['POT1990']!=-999]
        data=data[data['POT2000']!=-999]
        data=data[data['POT2010']!=-999]
        data=data[data['distance']>=0]
        for year in range(1990,2020):

            if year<2000:
                uy='POT1990'
            elif year<2010:
                uy='POT2000'
            else:
                uy='POT2010'
            

            for p in np.unique(data['PRO']):
                if p==0:
                    continue
                choice=data[data['PRO']==p]

                ks[p]['PD'][year-1990]+=np.sum(choice[f'Imp{year}']*choice[uy])
                ks[p]['Imp'][year-1990]+=np.sum(choice[f'Imp{year}'])

                ks[p]['PI'][year-1990]+=np.sum(choice[f'cAll{year}']*choice[uy])
                ks[p]['cEat'][year-1990]+=np.sum(choice[f'cAll{year}'])
            print(f'\r {i}-{j}-{year}',end='',flush=True)

for p in ks.keys():
    for year in range(1990,2020):
        if ks[p]['PI'][year-1990]!=0:
            ks[p]['CF'][year-1990]=ks[p]['PD'][year-1990]/ks[p]['PI'][year-1990]

    r=pd.DataFrame(ks[p])
    r.to_csv(f'/home/gh/work/BIOFIX/middata/pro_CF_all/{p}.csv',index=0)