# Rural development outpaces urban expansion in threatening biodiversity in China

In this study, we explore what extent urban and rural built-up land expansion has contributed to habitat losses of endangered species from 1990 to 2020. Our data calculation results include two parts: 

i) Habitat ranges of different endangered species were calculated based on habitat ranges of endangered species provided by International Union for Conservation of Nature (IUCN), Landsat-derived annual China land cover dataset (CLCD) and DEM data. 

ii) Location of species habitat loss due to urban and rural expansion from 1990 to 2020 based on CLCD and habitat range calculation.

The code folder provides the source code for this process, based on the python 3.9.7, the python configuration is listed in environment.yml.

|Filename|Introduce|
|--------|--------|
|**cutCLCD.py cutDEM.py cutPOT.py cutPRO.py cutGHS.py** | Preprocessing and region segmentation of datas|
|**gethabitat1.py gethabitat2.py**|Preprocessing and region segmentation of species datas|
|**code/dohabitat3.py**|Calculate species habitat range (Limited by storage space, the detailed grid range of species habitat is automatically generated in the form of intermediate variables during code operation and automatically deleted during code operation. Relevant codes can be deleted from the code to retain their generated results. The code takes the species richness data of the partition block as the final output result.)|
|**code/tsum.py & code/tcut.py**|Divide urban and rural areas according to the CLCD dataset|
|**code/loss_cropdirect.py**|Calculates the loss of habitat pixels caused by cropland expansion|
|**code/potan_y.py & code/mergethekey.py**|The cultivated land migration amount and the threshold of cultivated land migration pixels were calculated based on the China farmland productivity potential dataset|
|**loss_direct.py & loss_indirect.py**|Location of habitat loss pixels directly or indirectly caused by urban and rural areas|
|**biostat.py**|Calculates species richness where habitat pixels are lost|

The sample folder provides some sample code and sample data.
|Filename|Introduce|
|--------|--------|
|**biodiversity**|Habitat type and range of suitable habitat elevation for endangered species based on IUCN API [http://apiv3.iucnredlist.org/api/v3/docs]|
|**sample-totif.py**|Example code for converting habitat loss pixels stored in csv file to tif format|
|**thres.csv**|In order to meet the threshold specified in hypothesis 1 (method), if the proportion of built-up area in a region is greater than this threshold, the encroachment of cultivated land on habitat in the region is defined as the impact of cultivated land migration|
|**meansum.tif**| The 900m × 900m grid data used to divide urban and rural areas, and each grid pixel value represents the proportion of built-up areas|


Annual urban or rural encroachment on species habitat (in pixels) is temporarily available at
https://drive.google.com/drive/folders/1ttj8xUfTvwarCHdzVRty5enu0K065_Eq?usp=sharing

Habitat loss data includes two parts, the main conclusion of this paper is based on the statistical analysis and drawing of these two parts:
i) "loss_indirect_fix": indirect habitat expansion caused by urban and rural built-up land expansion.
ii) "loss_direct_fix": direct habitat expansion caused by urban and rural built-up land expansion.

We classified the habitats of different endangered species (VU,NT,EN,CR [https://www.iucnredlist.org/](https://www.iucnredlist.org/)).

The data consists of a csv file named "{ID}_id/td.csv". 
We divided the whole of China into 447 regions, and the region ranges are stored in patchs/patchs.shp, where {ID} corresponds to the ID column in the patchs.shp property table.
patchs/IDinfo.csv stores the number of rows and columns of the raster after converting these regions into a 30m × 30m resolution raster, which is used to locate all identified pixels.
By storing pixel information from damaged habitats in this way, we can reduce the storage space to some extent.
The proj4 of projection coordinate system of patchs.shp is always: **+proj=lcc +lat_0=0 +lon_0=105 +lat_1=30 +lat_2=62 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +type=crs**

sample-totif.tif provides a sample code for converting csv data to tif format.

The meanings of the columns in the csv file are as follows (Each row represents a damaged habitat pixel):
| row     | col     | value   |cityinfo|year|{VU/NT/EN/CR}_num|
| -------- | -------- | -------- |-------- |-------- |-------- |
| Row of pixel | Col of pixel| Land cover type of pixel* |The proportion of built-up area in the surrounding 900m × 900m range is used to assess whether the pixel loss is attributable to the countryside |The year in which the pixel was damaged| The abundance of species at that pixel |

\* The types represented by different values are as follows:
1 Cropland,
2 Forest,
3 Shrub, 
4 Grassland,
5 Water,
6 Sonw/Ice, 
7 Barren, 
8 Impervious,
9 Wetland






## be continued
