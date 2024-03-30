
#Calculate direct losses in urban and rural areas
#The calculation result of each block is saved as a csv file, 
#in which each row represents all the information of one pixel in the block 
#(location, habitat area occupied by urban and rural expansion, 
#habitat area occupied by cultivated land expansion, etc.).

import numpy as np
from osgeo import gdal,gdal_array,gdalconst
import pandas as pd
import os


#CLCD
CLCDpath='/data/gh/data/cutCLCD'
#Urban-Rural
GHSpath='/data/gh/data/cutGHS'
#habitat
Habpath='/data/gh/data/animalhabitat/key3'

#directloss
savepath='/data/gh/data/loss/directloss'


def statpixel(data):
    #林地，草地，湿地，灌木，荒地
    return np.sum(data==2),np.sum(data==4),np.sum(np.logical_or(data==5,data==9)),np.sum(data==3),np.sum(data==7)

def statnum(left,right,uk,rk,datas):
    res={}
    #区分城乡
    leftu=left*uk
    leftr=left*rk
    rightu=right*uk
    rightr=right*rk

    #找到前一年是栖息地，后一年是建成区的全部像元
    lossu=leftu[rightu==8]
    lossr=leftr[rightr==8]

    u=statpixel(lossu)
    r=statpixel(lossr)

    res['U-For']=u[0]
    res['U-Gra']=u[1]
    res['U-Wet']=u[2]
    res['U-Shr']=u[3]
    res['U-Bar']=u[4]
    res['U-Habitat']=np.sum(leftu!=0)



    res['R-For']=r[0]
    res['R-Gra']=r[1]
    res['R-Wet']=r[2]
    res['R-Shr']=r[3]
    res['R-Bar']=r[4]
    res['R-Habitat']=np.sum(leftr!=0)
    #更新往后的每个年份，已经被侵占过的栖息地不会被二次计算进去。
    for da in datas:
        da[right==8]=0

    return res,datas



def getexcel(i,j):

        if not os.path.exists(f'/data/gh/data/cutCLCD/um-{i}-{j}'):
            return

        ures={'row':[],'col':[],'All-Habitat':[],
              'distance':[],'UR':[],
              'POT1990':[],'POT2000':[],'POT2010':[],'PRO':[]}
        for year in range(1990,2020):
            ures[f'For{year}']=[]
            ures[f'Gra{year}']=[]
            ures[f'Wet{year}']=[]
            ures[f'Bar{year}']=[]
            ures[f'Imp{year}']=[]
            ures[f'cFor{year}']=[]
            ures[f'cGra{year}']=[]
            ures[f'cWet{year}']=[]
            ures[f'cBar{year}']=[]
            ures[f'cAll{year}']=[]
        

        #urban and rural
        GHS=gdal_array.LoadFile(os.path.join(GHSpath,f'ur-{i}-{j}.tif'))
        #habitat
        #If only the habitat of a single species is used in this step, the damage to different species can be counted
        #See exampledata for the calculation result
        hab=gdal_array.LoadFile(os.path.join(Habpath,f'habitat_a{i}b{j}.tif'))
        mask=hab>0
        #distance to urban (Not used in the study)
        distance=gdal_array.LoadFile(f'/data/gh/data/cutD/di-{i}-{j}.tif')

        if os.path.exists(f'/data/gh/data/CLCDfix_mask/imp_a{i}b{j}.tif'):
            impchange=gdal_array.LoadFile(f'/data/gh/data/CLCDfix_mask/imp_a{i}b{j}.tif')
        else:
            impchange=np.zeros((3400,3400))
        if os.path.exists(f'/data/gh/data/CLCDfix_mask/cro_a{i}b{j}.tif'):
            crochange=gdal_array.LoadFile(f'/data/gh/data/CLCDfix_mask/cro_a{i}b{j}.tif')
        else:
            crochange=np.zeros((3400,3400))
        
        POT1990=gdal_array.LoadFile(f'/data/gh/data/cutPOT/um1990/a{i}b{j}.tif')
        POT2000=gdal_array.LoadFile(f'/data/gh/data/cutPOT/um2000/a{i}b{j}.tif')
        POT2010=gdal_array.LoadFile(f'/data/gh/data/cutPOT/um2010/a{i}b{j}.tif')
        prodata=gdal_array.LoadFile(f'/data/gh/data/cutPRO/a{i}b{j}.tif')


        CLCDs=[]
        for year in range(1990,2021):
            #读取土地覆盖数据
            CLCD=gdal_array.LoadFile(os.path.join(CLCDpath,f'um-{i}-{j}',f'um{year}.tif'))
            #用栖息地,change掩膜
            CLCD[impchange==1]=0
            CLCD[crochange==1]=0
            CLCDs.append(CLCD)
            
            

        for x in range(100):
            for y in range(100):
                print(f'\r {i}-{j}  {x}-{y}',end='',flush=True)
                ures['row'].append(i*100+x)
                ures['col'].append(j*100+y)
                ures['All-Habitat'].append(np.sum(CLCDs[0]!=0))
                ures['distance'].append(distance[x][y])
                ures['UR'].append(GHS[x][y])
                                           
                ures['POT1990'].append(POT1990[x][y])
                ures['POT2000'].append(POT2000[x][y])
                ures['POT2010'].append(POT2010[x][y])
                ures['PRO'].append(prodata[x][y])

                for year in range(1990,2020):
                    left=CLCDs[year-1990]
                    right=CLCDs[year-1990+1]

                    leftmin=left[x*34:(x+1)*34,y*34:(y+1)*34]
                    rightmin=right[x*34:(x+1)*34,y*34:(y+1)*34]

                    #others to urban and rural 
                    loss=leftmin[rightmin==8]
                    ures[f'Imp{year}'].append(np.sum(loss==1))
                    #others to cropland
                    loss=leftmin[rightmin==1]
                    ures[f'cAll{year}'].append(np.sum(np.logical_and(loss!=8,loss!=1)))

                    leftmin=leftmin*mask[x*34:(x+1)*34,y*34:(y+1)*34]
                    rightmin=rightmin*mask[x*34:(x+1)*34,y*34:(y+1)*34]
                    loss=leftmin[rightmin==8]
                    #Different types of habitat directly invaded by urban and rural built-up area expansion
                    ures[f'For{year}'].append(np.sum(loss==2))
                    ures[f'Gra{year}'].append(np.sum(loss==4))
                    ures[f'Wet{year}'].append(np.sum(np.logical_or(loss==5,loss==9)))
                    ures[f'Bar{year}'].append(np.sum(np.logical_or(loss==3,loss==7)))
                    
                    #cropland directly encroaches on different types of habitats
                    loss=leftmin[rightmin==1]
                    ures[f'cFor{year}'].append(np.sum(loss==2))
                    ures[f'cGra{year}'].append(np.sum(loss==4))
                    ures[f'cWet{year}'].append(np.sum(np.logical_or(loss==5,loss==9)))
                    ures[f'cBar{year}'].append(np.sum(np.logical_or(loss==3,loss==7)))

        upd=pd.DataFrame(ures)
        
        upd.to_csv(f'/data/gh/new_data/loss/info_init/a{i}b{j}.csv',index=0)




import sys
if __name__=="__main__":

    row=40
    col=46

    le=int(sys.argv[1])
    ri=int(sys.argv[2])

    for i in range(le,ri):
        for j in range(col):
            getexcel(i,j)
