import inspect
import xarray as xr
import geopandas as gpd
import pandas as pd
import numpy as np
import dask


## get functions ##
= inspect.getsource(processing_functions.py)
= inspect.getsource(../pixel_to_df.py)
= inspect.getsource(recovery_functions.py)



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

## output paths
# reference csv's
reference_path= 
boostrap_path=
# set empty lists
pix_counts= []


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
    if pix_count_d < pix_count_nd:
            pix_count = pix_count_d
        # calc recovery magnitude for all pixels
            d_df = magnitude_calc_prep(d_df)
            rec_df = recovery_magnitude(d_df)
            ds = d_df # dataset for boostrap
    elif pix_count_d > pix_count_nd:
            pix_count = pix_count_nd
            nd_df = magnitude_calc_prep(nd_df)
            rec_df = recovery_magnitude(nd_df)
            ds = nd_df

            
    # return pix_count
    # add fire_name to a column
    pix_count_5 = pix_count / 5
    pix_count['fire_name'] = name
    pix_counts.append(pix_count)
    
    # add fire name to rec_df
    rec_df['fire_name'] = name
    
    # write out dataframe independently?
    # file out path
    out_path = reference_path + name + "rec_mag" + ".csv"
    rec_df.to_csv(out_path)

    ### PART II: BOOTSRAP SAMPLING ###

    # loop to sample 5 times 
    rmags = []
    for i in range(1,5):
        #$ get random sample $#
        df = random_sample(ds, pix_count_5 , 1, False) # number of samples = to return from part I step 3b

        #$ get recovery magnitude $#
        rm_df = recovery_magnitude(df)
        rmags.append(rm_df)
    
    # join rms
    all_rms = pd.concat([rmags[i] for i in range(0,len(rmags))])
    # save rmags as csv
    all_rms['fire_nane'] = name
    rms_out_path=boostrap_path + 'rec_mag' + '.csv' 
    all_rms.to_csv(rms_out_path)
        
     
    

    

# join pixel counts df
all_pixels = pd.concat([pix_counts[i] for i in range(0,len(pix_counts))])

