from osgeo import gdal,osr
import geopandas as gpd
import numpy as np
import pandas as pd
import os
import sys
import math


srs=osr.SpatialReference()
srs.ImportFromEPSG(4326)
gdal.UseExceptions()

def getinfo(data):
    col=data.RasterXSize
    row=data.RasterYSize
    tr=data.GetGeoTransform()
    minx=tr[0]
    maxy=tr[3]
    pixelW=tr[1]
    pixelH=tr[5]
    maxx=minx+col*pixelW
    miny=maxy+row*pixelH
    info={}
    info['minx']=minx
    info['maxx']=maxx
    info['miny']=miny
    info['maxy']=maxy
    info['pixelW']=pixelW
    info['pixelH']=pixelH
    info['row']=row
    info['col']=col
    return info


def search(DEMinfo,cminx,cmaxx,cminy,cmaxy):
    def inser(x):
        minx=x['minx']
        maxx=x['maxx']
        miny=x['miny']
        maxy=x['maxy']
        if minx<cmaxx and maxx>cminx:
            if miny<cmaxy and maxy>cminy:
                return 1
        return 0
    sea=DEMinfo.apply(inser,axis=1)
    return DEMinfo[sea==1]

def merge(results,savepath,name):
    datas=[]
    minxs=[]
    maxxs=[]
    minys=[]
    maxys=[]
    for path in results['path']:
        data=gdal.Open(path)
        datas.append(data)
        info=getinfo(data)
        minxs.append(info['minx'])
        maxxs.append(info['maxx'])
        minys.append(info['miny'])
        maxys.append(info['maxy'])

        pixelW=info['pixelW']
        pixelH=info['pixelH']
    minx=np.min(minxs)
    maxx=np.max(maxxs)
    miny=np.min(minys)
    maxy=np.max(maxys)

    col=int(math.ceil((maxx-minx)/pixelW))
    row=int(math.ceil((miny-maxy)/pixelH))
    res=np.zeros((row,col))

    for data in datas:
        info=getinfo(data)
        
        
        xoffset=int(round((info['minx']-minx)/pixelW))
        if xoffset<0:
            xoff=0
        else:
            xoff=xoffset
        yoffset=int(round((info['maxy']-maxy)/pixelH))
        if yoffset<0:
            yoff=0
        else:
            yoff=yoffset

        rowlen=info['row']
        if yoffset<0:
            rowlen=rowlen+yoffset
        collen=info['col']
        if xoffset<0:
            collen=collen+xoffset
        # print(yoff,rowlen,xoff,collen)
        datap=data.ReadAsArray(0 if xoffset>0 else abs(xoffset),0 if yoffset>0 else abs(yoffset),collen,rowlen)
        up=res[yoff:yoff+rowlen,xoff:xoff+collen]

        res[yoff:yoff+rowlen,xoff:xoff+collen]=datap
    
    driver = gdal.GetDriverByName("GTiff") 
    ds=driver.Create(os.path.join(savepath,name),col,row,1,gdal.GDT_Float32,options=['COMPRESS=LZW'])
    band=ds.GetRasterBand(1)
    # band.SetNoDataValue(-999)
    band.WriteArray(res,0,0)
    transform=[minx,pixelW,0,maxy,0,pixelH]
    ds.SetGeoTransform(transform)
    ds.SetProjection(srs.ExportToWkt())
    ds=None




if __name__=="__main__":
    savepath='/root/work/BIO/new_code/mid/demmid'
    patchs=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
    patchs=patchs.to_crs('epsg:4326')

    DEMinfo=pd.read_csv('/root/work/BIO/new_code/data/DEMinfo.csv')

    for i,item in patchs.iterrows():
        ID=item['ID']
        geometry=item['geometry']
        
        # ushp=ushp.dissolve().envelope
        # ushp=ushp.tolist()[0]

        coords=geometry.exterior.coords[:-1]
        # coords=geometry.envelope.coords[:-1]
        xs=[c[0] for c in coords]
        ys=[c[1] for c in coords]
        cminx=min(xs)
        cmaxy=max(ys)
        cmaxx=max(xs)
        cminy=min(ys)
        dems=search(DEMinfo,cminx,cmaxx,cminy,cmaxy)

        merge(dems,savepath,f'DEM{ID}.tif')
        print(f'\r {ID}',end='',flush=True)
        
 
        # print(cminx,cmaxy,cmaxx,cminy)

        # crange=[cminx,cmaxy-32*5000,cminx+32*5000,cmaxy]
    # infos=pd.read_csv('/root/work/BIO/new_code/data/CLCDinfo.csv')
    # bios=gpd.read_file('/root/work/BIO/new_code/data/patchs.shp')
    # bios.to_crs(crs='epsg:4326')
    # IDs=bios['ID']
    
    # left=int(sys.argv[1])
    # right=int(sys.argv[2])
    # paths=np.array(infos['path'])
    # years=np.array(infos['year'])

    # for i,path in enumerate(paths):
    #     if i<left or i>=right:
    #         continue
    #     for id in IDs:
    #         IDpath=os.path.join('/root/work/BIO/new_code/res/cuttif_84',f'{id}')
    #         if not os.path.exists(IDpath):
    #             os.mkdir(IDpath)
    #         savepath=os.path.join(IDpath,f'bio_{years[i]}.tif')
    #         ds=gdal.Warp(
    #             savepath,path,
    #             creationOptions=['COMPRESS=LZW'],
    #             cutlineDSName='/root/work/BIO/new_code/data/patchs.shp',
    #             cutlineSQL=f"SELECT * from patchs WHERE ID={id}",  #选择shp之中NAME为北京的那个要素
    #             cropToCutline=True,
    #             dstNodata=0
    #         )
    #         ds=None
    #         print(f"\rcuting:{years[i]}-{id}",end='',flush=True)
