import numpy as np
import pandas as pd
import geopandas as gpd
import os
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

dicLC={1:'Cro',2:'For',3:'Shr',4:'Gra',5:'Wat',6:'Bar',7:'Bar',8:'Imp',9:'Wet'}

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

def getLC(habitat):
    Codes=habitat.split('-')
    Cs=[]
    for Code in Codes:
        C=Code_LC(Code)
        if C=='None':
            continue
        Cs.append(C)
    Cs=np.array(Cs)
    Cs=np.unique(Cs)
    s=''
    for i,C in enumerate(Cs):
        if i>0:
            s+='_'
        s+=C
    return s        


patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
# patchs=patchs.to_crs('epsg:4326')

anitypes=['AMPHIBIAN','BIRD','MAMMALS','REPTILES']
highpath='/root/work/BIO/new_code/data/high2'

IDres={}
for ID in patchs['ID']:
    IDres[int(ID)]=pd.DataFrame(columns=['name','type','habitat','ele_upper','ele_lower','category'])
for anitype in anitypes:
    csv=pd.read_csv(os.path.join(highpath,f'{anitype}_infos.csv'))
    for i,item in csv.iterrows():
        print(f'\r{anitype}-{i}/{csv.shape[0]}',end='',flush=True)
        name=item['name']
        habitat=getLC(item['habitat'])
        ele_upper=item['ele_upper']
        ele_lower=item['ele_lower']
        category=item['category']
        IDs=item['IDs'].split('_')
        for ID in IDs:
            if ID=='':
                continue
            if int(ID) in IDres.keys():
                IDres[int(ID)].loc[IDres[int(ID)].shape[0]]=[name,anitype,habitat,ele_upper,ele_lower,category]
for ID in patchs['ID']:
    IDres[int(ID)].to_csv(os.path.join(f"/root/work/BIO/new_code/res/bioversity/{ID}.csv"),index=0)
