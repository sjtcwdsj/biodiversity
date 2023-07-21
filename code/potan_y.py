import numpy as np
import pandas as pd
from osgeo import gdal,gdal_array
import geopandas as gpd
import os
import sys
potanpath='/root/work/BIO/new_code/res/potan'
patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
croplosspath='/root/work/BIO/fix/res/loss/loss_cropdirect'
#CR：极度濒危  EN：濒危 VU：易危  NT：近危  LC:几乎不关注
anitypes=['CR','EN','VU','NT']
maskpath='/root/work/BIO/city_rural/res/cr_sum_patch'
if __name__=="__main__":
    anitype=sys.argv[1]

# for anitype in anitypes:
    csv=pd.read_csv(os.path.join('/root/work/BIO/new_code/res/loss',f'x_{anitype}.csv'),index_col='year')
    us={}
    for year in range(1990,2020):
        us[year]=np.array([])

    for ID in patchs['ID']:
        # losstif=gdal.Open(os.path.join(croplosspath,anitype,f'{anitype}-{ID}_loss1.tif'))
        losstif=pd.read_csv(os.path.join(croplosspath,anitype,f'{ID}_td.csv'))
        citymask=gdal_array.LoadFile(os.path.join(maskpath,f'sum{ID}.tif'))
        for year in range(1990,2020):
            print(f'\r doing-{anitype}-{ID}-{year}',end='',flush=True)
            #耕地侵占
            loss=losstif[losstif['year']==year]
            #potan
            if year>=1990 and year<2000:
                uyear=1990
            elif year>=2000 and year<2010:
                uyear=2000
            else:
                uyear=2010
            # potantif=gdal_array.LoadFile(os.path.join(potanpath,str(uyear),f'pot{ID}.tif'))
            merge=citymask[loss['row'],loss['col']]
            us[year]=np.concatenate((us[year],merge),0)
            # for u in us.keys():


    res={}
    res['year']=list(range(1990,2020))
    res['thekey']=[]
    for year in range(1990,2020):
        item=us[year]
        item.sort()
        item=item[::-1]
        ukey=int(csv.loc[year,'xnum'])
        if item.shape[0]>ukey:
            key=item[int(csv.loc[year,'xnum'])]
        else:
            key=item[-1]
        res['thekey'].append(key)
    res=pd.DataFrame(res)

    
    res.to_csv(f'/root/work/BIO/fix/res/loss/potancsv/y_{anitype}.csv',index=0)

        # if ID==2:
        #     break
    # for u in us:
    #     print(len(u))