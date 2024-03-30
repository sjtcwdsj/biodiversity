##Calculate indirect losses in urban and rural areas
import numpy as np
import pandas as pd
from osgeo import gdal,gdal_array
import os
import sys




infopath='/data/gh/new_data/loss/info_init'

#CF
CF=pd.read_csv('/home/gh/work/BIOFIX/middata/pot_fix.csv')
c=CF['CF'].tolist()



# The proportion of cropland encroachment*CF  in each block is equal to the indirect encroachment of urban and rural areas respectively.

row=40
col=46

arearatio=pd.read_csv('/home/gh/work/BIOFIX/middata/area_ratio.csv')

province=gdal_array.LoadFile('/home/gh/work/BIOFIX/middata/province.tif')
pros=np.unique(province)

ratio_csvs={}
recf_csvs={}
for pro in pros:
    if pro==0:
        continue
    ratio_csvs[pro]=pd.read_csv(f'/home/gh/work/BIOFIX/middata/pro_ratio/{pro}.csv')
    recf_csvs[pro]=pd.read_csv(f'/home/gh/work/BIOFIX/middata/pro_CF/{pro}.csv')
res={'Urban-Direct-For':[0]*30,
     'Urban-Direct-Gra':[0]*30,
     'Urban-Direct-Wet':[0]*30,
     'Urban-Direct-Bar':[0]*30,
     'Rural-Direct-For':[0]*30,
     'Rural-Direct-Gra':[0]*30,
     'Rural-Direct-Wet':[0]*30,
     'Rural-Direct-Bar':[0]*30,
     'Urban-Indirect-For':[0]*30,
     'Urban-Indirect-Gra':[0]*30,
     'Urban-Indirect-Wet':[0]*30,
     'Urban-Indirect-Bar':[0]*30,
     'Rural-Indirect-For':[0]*30,
     'Rural-Indirect-Gra':[0]*30,
     'Rural-Indirect-Wet':[0]*30,
     'Rural-Indirect-Bar':[0]*30}


def getdirectfix(item,ty,year,areafix):
    return item[f'{ty}{year}']*areafix

def getindirect_urbanfix(item,ty,year,areafix):
    PRO=item['PRO']
    if PRO<=0:
        return 0
    
    CF=recf_csvs[PRO]['CF'].tolist()[year-1990]
    if CF>1:
        CF=1
    ratio=ratio_csvs[item['PRO']]['ratio'].tolist()[year-1990]
    return item[f'c{ty}{year}']*CF*ratio*areafix

def getindirect_ruralfix(item,ty,year,areafix):
    PRO=item['PRO']
    if PRO<=0:
        return 0
    CF=recf_csvs[PRO]['CF'].tolist()[year-1990]
    if CF>1:
        CF=1
    ratio=ratio_csvs[item['PRO']]['ratio'].tolist()[year-1990]
    return item[f'c{ty}{year}']*CF*(1-ratio)*areafix


def getexcel(i,j):
    if not os.path.exists(f'/data/gh/data/cutCLCD/um-{i}-{j}'):
        return

    
    data=pd.read_csv(os.path.join(infopath,f'a{i}b{j}.csv'))
    areafix=arearatio.loc[arearatio['rc']==f'a{i}b{j}','change'].tolist()[0]

    df=pd.concat([data['row'],data['col'],data['UR']], axis=1)
    for year in range(1990,2020):
        for ty in ['For','Gra','Wet','Bar']:
            df[f'{ty}{year}']=data.apply(getdirectfix,axis=1,args=(ty,year,areafix))
            df[f'u{ty}{year}']=data.apply(getindirect_urbanfix,axis=1,args=(ty,year,areafix))
            df[f'r{ty}{year}']=data.apply(getindirect_ruralfix,axis=1,args=(ty,year,areafix))


    


        print(f'\r{year}-{i}-{j}',end='',flush=True)


    df.to_csv(f'/data/gh/new_data/loss/info_loss/a{i}b{j}.csv',index=0)



if __name__=="__main__":
    
    row=40
    col=46

    le=int(sys.argv[1])
    ri=int(sys.argv[2])

    for i in range(le,ri):
        for j in range(col):
            getexcel(i,j)