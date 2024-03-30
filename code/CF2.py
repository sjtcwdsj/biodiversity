#On the basis of CF calculation, the proportion of indirect loss caused by urban and rural expansion is calculated each year

import pandas as pd
import numpy as np
import os
import sys
from osgeo import gdal,gdal_array


infopath='/data/gh/new_data/loss/info_init_all'


row=40
col=46

PD=0
PI=0


province=gdal_array.LoadFile('/home/gh/work/BIOFIX/middata/province.tif')
pros=np.unique(province)
ks={}
for pro in pros:
    if pro==0:
        continue
    ks[pro]={'year':list(range(1990,2020)),'urbanImp':[0]*30,'ruralImp':[0]*30,'ratio':[0]*30}






for year in range(1990,2020):

    num=[]

    urbanImp=0
    ruralImp=0
    for i in range(row):
        for j in range(col):
            if not os.path.exists(f'/data/gh/data/cutCLCD/um-{i}-{j}'):
                continue
            
            data=pd.read_csv(os.path.join(infopath,f'a{i}b{j}.csv'))
            

            for p in np.unique(data['PRO']):
                if p==0:
                    continue
                choice=data[data['PRO']==p]

                urban=choice[choice['UR']==3]
                rural=choice[np.logical_or(choice['UR']==1,choice['UR']==2)]

                ks[p]['urbanImp'][year-1990]+=np.sum(urban[f'Imp{year}'])
                ks[p]['ruralImp'][year-1990]+=np.sum(rural[f'Imp{year}'])


            print(f'\r{year}-{i}-{j}',end='',flush=True)


for p in ks.keys():
    for year in range(1990,2020):
        if ks[p]['urbanImp'][year-1990]+ks[p]['ruralImp'][year-1990]!=0:
            ks[p]['ratio'][year-1990]=ks[p]['urbanImp'][year-1990]/(ks[p]['urbanImp'][year-1990]+ks[p]['ruralImp'][year-1990])


    r=pd.DataFrame(ks[p])
    r.to_csv(f'/home/gh/work/BIOFIX/middata/pro_ratio_all/{p}.csv')
            


            

            


