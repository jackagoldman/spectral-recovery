import inspect
import xarray as xr
import geopandas as gpd
import pandas as pd
import numpy as np
import dask


## get functions ##
= inspect.getsource(processing_functions.py)
= inspect.getsource(../pixel_to_df.py)



"""
The following script preforms bootstrap sampling of pixels within a fire.
Sampling is based on which portion of fire (defoliated/non-defolaited)
has the least amount of pixels.

Steps: 
Part I.
1. read in defoliated and non-defoliated fire from folders
2. calculate the amount of pixels
3. whichever has the least amount of pixel:
    a. return path
    b. return pixels amount
4. Calculate recovery magnitude for fire with least amount of pixels
5. get distribution
6. Save pixel df and distribution.
    
Part II.
1. read in raster based on path returned in step 1.
2. divded number of pixels in by 5
3. add number of pixels to sample argument
4. run five times, get distribution.


"""


# DEFAULTS

## file path ##
defol_path = 
non_defol_path = 

## set file path ##
d_pathlist = Path(defol_path).rglob('*.nc')
nd_pathlist = Path(non_defol_path).rglob('*.nc')



### PART I: FIND PORTION OF FIRE WITH LEAST AMOUNT OF PIXELS ###
for path in d_pathlist:
    # get first img
    path_in_str = str(path)
    fire_name = getName(path_in_str)
    defol = rx.open_rasterio(path, masked=True) # get img
    
    # get matching nd img
    non_defol_path = non_defol_path + fire_name + ".nc"
    non_defol = rx.open_rasterio(non_defol_path, masked=True) # get nondefol img
    
    #count pixels 
    # defol
    d_df = defol.to_dataframe()
    d_df = d_df.dropna()
    pix_count_d = d_df.count()
    # non defol
    nd_df = non_defol.to_dataframe()
    nd_df = nd_df.dropna()
    pix_count_nd = nd_df.count()
    
    # check to see which has more pixels
    if pix_count_d > pix_count_nd:
        pix_count = pix_count_d
        # calc recovery magnitude for all pixels
        
        
        

    






####### PART II: BOOTSRAP SAMPLING #######


####### loop through directory and read in data, preform ops ######

for path in d_pathlist:
    path_in_str = str(path) # get path name as string
    ds = rx.open_rasterio(path, masked=True) # get img
    name = getName(path_in_str)# get name
    
    #### loop to sample 5 times ####
    for i in range(1,5):
        #$ get random sample $#
        df = random_sample(ds, 1000, 1, False) # number of samples = to return from part I step 3b

        #$ get recovery magnitude $#
