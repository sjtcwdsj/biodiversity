import geopandas as gpd
import os
anitypes=['AMPHIBIAN','BIRD','MAMMALS','REPTILES']

for anitype in anitypes:
    path=f'/root/work/BIO/new_code/data/china_{anitype}.shp'
    data=gpd.read_file(path)
    data=data.to_crs('+proj=lcc +lat_0=0 +lon_0=105 +lat_1=30 +lat_2=62 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +type=crs')
    data.to_file(f'/root/work/BIO/new_code/data/china_{anitype}_lam.shp')