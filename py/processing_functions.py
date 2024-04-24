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


def fire_year_from_base(filename):
    """takes filepath and returns year of fire"""
    name = re.sub(r'^.*/', "", filename)  
    name = str(name)
    year = name.split('_')[1] # 1 returns the second object in the list (first object is always 0). [#] refers to index position
    return year

def match_coords(img, ref):
    result = img.assign_coords({
    "lon": ref.lon,
    "lat": ref.lat,})
    return result


def getName(filename):
    """ takes in filepath and returns the name of the file for a tif 
    """
    name = re.sub(r'^.*/', "", filename)
    name = name.replace("_pp", "")
    name = name.replace("_nbr", "")
    name = name.split(".")[-0]
    return name

def check_shp_exists(shp, name):
    if name in shp:
        res = 1
    else:
        res = 0
    return res


def clipRastersTIF(in_path, shpfile, out_path):
    pathlist = Path(in_path).rglob('*.tif')
    for path in pathlist:
        path_in_str = str(path)
        src = rx.open_rasterio(path)
        name = getName(path_in_str)
        print(name)
        src_lonlat = src.rio.reproject("epsg:4326") 
        shp = gpd.read_file(shpfile)
        shp = shp[shp.Fire_ID == name]
        clipped = src_lonlat.rio.clip(shp.geometry.values, shp.crs, drop=True, invert=False)
        out_dir = out_path + name +".tif"
        clipped.rio.to_raster(out_dir, driver="GTiff", compress="LZW")


def raster_stats(ras):
    median =  ras.median()
    mean = ras.mean()
    std = ras.std()
    median = median.to_pandas()
    mean = mean.to_pandas()
    std = std.to_pandas()
    cv = std/mean
    return (mean, median, cv)
    
def calc_rbr(ras):
    """returns a new raster consisting of rbr (2) , 
    and a dataframe consisting of median, mean and cv rbr
    """
    pre = ras[0]
    post = ras[2]
    post = post.assign_coords({
    "x": pre.x,
    "y": pre.y,})
    new_raster=(((pre - post)*1000)/ pre + 1.001)
    mean, median, cv = raster_stats(new_raster)
    df = pd.DataFrame({
    "Fire_ID": [name],
    "rbr_median": [median],
    "rbr_mean": [mean],
    "rbr_cv": [cv]
    })
    return (df, new_raster)

def std_nbr(df):
    df.index.name ="year"
    df.reset_index(inplace=True)
    df['year'] = df['year'].astype('int16')
    df['nbr'] = df['nbr'].where(df['nbr'] < 2, df['nbr']/1000)
    df.set_index('year')
    return(df)


def nc_to_xarray(img, sets):
    """converts nc files with unorganized bands from either nbr grouping (sets) 
    or pp grounping and converts to xr array
    """
    # get years
    year = int(fire_year_from_base(nbr_nc)) #coerce to integer
    if sets == "nbr":
        end = year + 11 # add 10 years 
        years = list(range(year, end))
        # deleted postNBR year (year 1)
        del years[1] 
        #filter bands
        nbr0=img.rename_vars(Band10="nbr")['nbr']
        nbr2=img.rename_vars(Band1="nbr")['nbr']
        nbr3=img.rename_vars(Band2="nbr")['nbr']
        nbr4=img.rename_vars(Band3="nbr")['nbr']
        nbr5=img.rename_vars(Band4="nbr")['nbr']
        nbr6=img.rename_vars(Band5="nbr")['nbr']
        nbr7=img.rename_vars(Band6="nbr")['nbr']
        nbr8=img.rename_vars(Band7="nbr")['nbr']
        nbr9=img.rename_vars(Band8="nbr")['nbr']
        nbr10=img.rename_vars(Band9="nbr")['nbr']

        # make sure coordinates match
        nbr2= match_coords(nbr2, nbr0)
        nbr3= match_coords(nbr3, nbr0)
        nbr4= match_coords(nbr4, nbr0)
        nbr5= match_coords(nbr5, nbr0)
        nbr6= match_coords(nbr6, nbr0)
        nbr7= match_coords(nbr7, nbr0)
        nbr8= match_coords(nbr8, nbr0)
        nbr9= match_coords(nbr9, nbr0)
        nbr10= match_coords(nbr10, nbr0)

        #concat
        da = xr.concat([nbr0, nbr2, nbr3, nbr4, nbr5, nbr6, nbr7, nbr8, nbr9, nbr10], dim=pd.Index(years, name='time'))
    if sets == "pp":
        start = year - 1
        end = year + 2 # add 10 years 
        years = list(range(start, end))
        # deleted postNBR year (year 1)
        del years[1] 
        #filter bands
        preNBR= img.rename_vars(Band1='nbr')['nbr']
        postNBR= img.rename_vars(Band2='nbr')['nbr']

        # make sure coordinates match
        postNBR= match_coords(postNBR, preNBR)
        
        #concat
        da = xr.concat([preNBR, postNBR], dim=pd.Index(years, name='time'))


    da.attrs['long_name'] = "nbr"
    return(da)

        
        

def combine_nc_to_xarray(nbr_img, pp_img, filename):
    img = nbr_img
    img2 = pp_img
    filename =str(filename)
    # get years
    year = int(fire_year_from_base(filename)) #coerce to integer
    start = year - 1
    end = year + 11 # add 10 years 
    years = list(range(start, end))
    #filter bands
    nbr0=img.rename_vars(Band10="nbr")['nbr']
    nbr2=img.rename_vars(Band1="nbr")['nbr']
    nbr3=img.rename_vars(Band2="nbr")['nbr']
    nbr4=img.rename_vars(Band3="nbr")['nbr']
    nbr5=img.rename_vars(Band4="nbr")['nbr']
    nbr6=img.rename_vars(Band5="nbr")['nbr']
    nbr7=img.rename_vars(Band6="nbr")['nbr']
    nbr8=img.rename_vars(Band7="nbr")['nbr']
    nbr9=img.rename_vars(Band8="nbr")['nbr']
    nbr10=img.rename_vars(Band9="nbr")['nbr']

    # make sure coordinates match
    nbr2= match_coords(nbr2, nbr0)
    nbr3= match_coords(nbr3, nbr0)
    nbr4= match_coords(nbr4, nbr0)
    nbr5= match_coords(nbr5, nbr0)
    nbr6= match_coords(nbr6, nbr0)
    nbr7= match_coords(nbr7, nbr0)
    nbr8= match_coords(nbr8, nbr0)
    nbr9= match_coords(nbr9, nbr0)
    nbr10= match_coords(nbr10, nbr0)

    # pre nbr
    preNBR= img2.rename_vars(Band1='nbr')['nbr']
    postNBR= img2.rename_vars(Band2='nbr')['nbr']

    # make sure coordinates match
    postNBR= match_coords(postNBR, nbr0)
    preNBR= match_coords(preNBR, nbr0)

    #concat
    da = xr.concat([preNBR, nbr0, postNBR, nbr2, nbr3, nbr4, nbr5, nbr6, nbr7, nbr8, nbr9, nbr10], dim=pd.Index(years, name='time'))

    da.attrs['long_name'] = "nbr"
    return(da)


def combine_write_to_xarray(nbr_in_path, pp_in_path, out_path):
    pathlist = Path(nbr_in_path).rglob('*.nc') # create nbr pathlist
    for path in pathlist: # loop through nbr folder
        nbr_path_in_str = str(path) # get nbr path as string
        nbr_img = xr.open_dataset(path, decode_coords="all") # open nbr as xarray
        name = getName(nbr_path_in_str)
        path2 = pp_in_path + name + "_pp.nc" 
        pp_img = xr.open_dataset(path2, decode_coords="all") # open pp as xarray
        ds = combine_nc_to_xarray(nbr_img, pp_img, nbr_path_in_str)
        out_dir = out_path + name + ".nc"
        ds.to_netcdf(out_dir)


def clipRasters(in_path, shpfile, out_path):
 pathlist = Path(in_path).rglob('*.nc')
 for path in pathlist:
  path_in_str = str(path)
  src = xr.open_dataset(path, decode_coords=True)
  name = getName(path_in_str)
  src.rio.write_crs("epsg:4326", inplace=True)
  print(name)
  src_lonlat = src.rio.reproject("epsg:4326") 
  shp = gpd.read_file(shpfile)
  if shp.isin([name]).any().any() == False:
    continue
  else:
    shp = shp[shp.Fire_ID == name]
    clipped = src_lonlat.rio.clip(shp.geometry.values, shp.crs, drop=True, invert=False)
    out_dir = out_path + name +".nc"
    vars_list = list(clipped.data_vars)  
    for var in vars_list:  
        del clipped[var].attrs['grid_mapping']
    clipped.to_netcdf(out_dir)



def set_attrs(img, filepath):
    name = getName(filepath)
    year = fire_year_from_base(filepath)
    img = img.assign_attrs(fire_name= name, fire_year = year)
    return(img)
    

