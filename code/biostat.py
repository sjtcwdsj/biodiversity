import numpy as np
import pandas as pd
from osgeo import gdal,gdal_array
import geopandas as gpd
import os
import sys
import shutil

patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
#CR：极度濒危  EN：濒危 VU：易危  NT：近危  LC:几乎不关注
anitypes=['CR','EN','VU','NT']

direct_path='/root/work/BIO/fix/res/loss/loss_direct'
indirect_path='/root/work/BIO/fix/res/loss/loss_indirect'

habitat_path='/root/work/BIO/new_code/res/ani_byBW'
savetdpath='/root/work/BIO/fix/res/loss/loss_direct_fix'
saveidpath='/root/work/BIO/fix/res/loss/loss_indirect_fix'

def tifinfo(ID,anitype):

    directdata=pd.read_csv(os.path.join(direct_path,anitype,f'{ID}_td.csv'))
    indirectdata=pd.read_csv(os.path.join(indirect_path,anitype,f'{ID}_id.csv'))

    hpath=os.path.join(habitat_path,anitype,f'Habitat_{ID}.tif')
    htif=gdal.Open(hpath)
    hdata=htif.ReadAsArray(0,0)

    restd=None
    resid=None
    for year in range(1990,2020):

        td=directdata[directdata['year']==year]
        id=indirectdata[indirectdata['year']==year]

        

        # td=directdata[year-1990,:,:]
        # id=indirectdata[year-1990,:,:]
        # print(np.unique(td),np.unique(id))

        td[f'{anitype}_num']=hdata[td['row'],td['col']]
        id[f'{anitype}_num']=hdata[id['row'],id['col']]

        restd=td if restd is None else pd.concat((restd,td),axis=0)
        resid=id if resid is None else pd.concat((resid,id),axis=0)

    restd.to_csv(os.path.join(savetdpath,anitype,f'{ID}_td.csv'))
    resid.to_csv(os.path.join(saveidpath,anitype,f'{ID}_id.csv'))




# def stat(data):
#     ds=np.unique(data)
#     res={}
#     for d in ds:
#         choice=data[data==d]
#         num=choice.shape[0]
#         res[d]=num
#     return res


# def work(anitype):
#     tres={}
#     for year in range(1990,2020):
#         tres[year]=None
#     for ID in patchs['ID']:
#         ures=tifinfo(ID,anitype)
#         print(f'\r{anitype}-{ID}',end='',flush=True)
#         for year in range(1990,2020):
#             if tres[year] is None:
#                 tres[year]=ures[year]
#             else:
#                 tres[year]=np.concatenate((tres[year],ures[year]),axis=0)
#     quit()
#     f=open(os.path.join(savepath,f'{anitype}-stat.csv'),'w')
#     f.write('year,info,\n')
#     for year in range(1990,2020):
#         f.write(str(year)+',')
#         st=stat(tres[year])
#         for key in st.keys():
#             f.write(str(key)+':'+str(st[key])+'-')
#         f.write(',')
#         if year!=2019:
#             f.write('\n')
#     f.close()


    


if __name__=="__main__":


    for anitype in anitypes:
        opath=os.path.join(savetdpath,anitype)
        if os.path.exists(opath):
            shutil.rmtree(opath)
        os.mkdir(opath)
        upath=os.path.join(saveidpath,anitype)
        if os.path.exists(upath):
            shutil.rmtree(upath)
        os.mkdir(upath)
        for ID in patchs['ID']:
            print(f'\r{anitype}-{ID}',end='',flush=True)
            tifinfo(ID,anitype)

    # anitype=sys.argv[1]
    # res=work(anitype)
