# Rural development outpaces urban expansion in threatening biodiversity in China

In this study, we explore what extent urban and rural built-up land expansion has contributed to habitat losses of endangered species from 1990 to 2020. Our data calculation results include two parts: 

i) Habitat ranges of different endangered species were calculated based on habitat ranges of endangered species provided by International Union for Conservation of Nature (IUCN), Landsat-derived annual China land cover dataset (CLCD) and DEM data. 

ii) Location of species habitat loss due to urban and rural expansion from 1990 to 2020 based on CLCD and habitat range calculation.

The code folder provides the source code for this process, the exampledata provides the example result of this process, based on the python 3.9.7, the python configuration is listed in environment.yml.


|Filename|Introduce|
|--------|--------|
|**cutCLCD.py cutDEM.py cutPOT.py cutPRO.py cutGHS.py** | Preprocessing and region segmentation of datas|
|**gethabitat1.py gethabitat2.py**|Preprocessing and region segmentation of species datas|
|**habitat_directloss.py habitat_indirectloss.py CF1.py CF2.py**|Calculate the direct and indirect impacts of urban and rural areas on species habitat, and see a23b32.csv in the exampledata|
|**a23b32.csv**|Example result data identifying habitat loss results at block 32, row 23, all data results are available at [https://drive.google.com/drive/folders/1ttj8xUfTvwarCHdzVRty5enu0K065_Eq?usp=sharing](https://drive.google.com/drive/folders/1kOtNCfISqMBzimFmu1LglG2bgcvAYRgt?usp=drive_link)|
|**animalloss.xlsx**|Species statistics, which identify the habitat loss for each species, are calculated by modifying habitat_directloss.py|
|**tifmap.py**|Generate the final tif file based on the csv file|

csv file data result description:
|column name|Introduce|
|--------|--------|
|**row col**|The number of rows and columns of the 1020m×1020m grid cell|
|**UR**|Is the pixel an urban area or a rural area, 1 for rural, 2 and 3 for urban|
|**{Habitat type}{year}**|Direct loss of habitat within the grid cell, the UR value determines whether these losses are due to urban or rural areas|
|**r{Habitat type}{year}**|Indirect loss of habitat caused by rural in the grid cell|
|**u{Habitat type}{year}**|Indirect loss of habitat caused by urban in the grid cell|

The **result_tif** folder holds the final result map, named in the format {A}{B}_{C}.tif, which indicates the different types of habitat (B, For = forest, Gra = grassland, Wet = wetlands, Bar = others), directly or indirectly (C) caused by urban or rural (A, u = urban, r = rural) annual loss (ha), for the period 1990 to 2020. To obtain the annual tif results of habitat loss, you can modify the contents of tifmap.py.

## be continued
