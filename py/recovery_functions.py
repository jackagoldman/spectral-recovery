import numpy as np
import rioxarray as rx
import rasterio
from rasterio.mask import mask
from pathlib import Path
import geopandas as gpd
import pprint
import re
import os
import glob
import xarray as xr
import matplotlib.pyplot as plt
import xarray
import pandas as pd
from exactextract import exact_extract





def magnitude_calc(x):
    pre= x[x['nbr_time'] == 0]
    pre = pre['nbr'].item()
    post= x[x['nbr_time'] == 1]
    post = post['nbr'].item()
    p_diff = pre - post
    rec = x[x['nbr_time'] == 11]
    rec = rec['nbr'].item()
    rec_diff = rec - post
    mag = (rec - post)* 100
    
    return pd.DataFrame({'recovery_magnitude': [mag]})

def recovery_magnitude(df):
    grp = df.groupby('id')
    magnitudes = []
    # for length in 1-1001
    ids = np.arange(1,1001,1)
    for i in ids:
        # get group
        x = grp.get_group(i)
        # calc mac
        res = magnitude_calc(x)
        # add id column
        res['id'] = i
        # append to list
        magnitudes.append(res)
        
        
    #join back into single datafame
    all_mags = pd.concat([magnitudes[i] for i in range(0,len(magnitudes))])
    
    return(all_mags)


def magnitude_calc_prep(da):
    """
    calculates the distribution for the reference portion of the fire.
    Steps:
    1. slice og dataframe by dimension time = 1 using isel. 
        This returns all the pixel locations for a given year that we then 
        use to iterate throught the og dataframe
    2. drop NA
    3. iterate through the OG dataframe
    
    """
    da2 = da.isel(time= 0)
    da2 = da.to_dataframe().reset_index()
    da2.dropna()
    
    pix_samples = []
    for index, row in da2.iterrows():
        x = row['x']
        y = row['y']
        df2 = da.to_dataframe()
        df2 = df2.dropna()
        df2 = std_nbr(df2)
        df2 = df2.loc[(df2['y'] == y) & (df2['x'] == x)]
        # add add row that goes preNBR - nbr 10
        ints = np.arange(0,12,1)
        df2['nbr_time'] = ints
        df2['nbr_time'] = df2['nbr_time'].replace({'0': 'preNBR', '1': 'nbrYOF', '2': '1', '3': '2', '4': '3', '5': '4', '6': '5', '7': '6', '8': '7', '9':'8', '10': '9', '11': '10'})
        pix_samples.append(df2)
    
    #join back into single datafame
    all_samples = pd.concat([pix_samples[i] for i in range(0,len(pix_samples))])
  
    #remove crs
    all_samples = all_samples.drop(columns =['crs'])
    
    # set ids, but need to now pixel_count so get length of da2
    pix_count = len(da2)
    ids = np.arange(1,pix_count,1)
    # add pixel id
    all_samples['id'] = np.repeat(ids, 12, axis = 0)
    
    return(all_samples)

