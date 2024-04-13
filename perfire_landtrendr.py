#landtrendr

import ee
import geemap
import numpy as np
import geopandas as gpd
import pandas as pd
import os
from ltgee import LandTrendr
from datetime import date

ee.Initialize()
# 
fires = ee.FeatureCollection("users/jandrewgoldman/on-qc-defol");
fire_names = fires.aggregate_array('Fire_ID').getInfo()
qc_fires = ee.FeatureCollection("users/jandrewgoldman/qc-fire-perims-shield-2").filter(ee.Filter.inList('Fire_ID', fire_names))
qc_names = qc_fires.aggregate_array('Fire_ID').getInfo()
on_fires = ee.FeatureCollection("users/jandrewgoldman/Ont_BurnSeverity_Trends/ON_FirePerimeters_85to2020_v0").filter(ee.Filter.inList('Fire_ID', fire_names))
on_names = on_fires.aggregate_array('Fire_ID').getInfo()

# get required columns and add them together
on_fires = on_fires.select('Fire_ID', 'Fire_Year')
qc_fires = qc_fires.select('Fire_ID', 'Fire_Year')

on_qc_fires = on_fires.merge(qc_fires)

fires = on_qc_fires


############### start of landtrendr analysis

# get Fires
fids = fires.aggregate_array('Fire_ID')
 # turn it to python list
fids = fids.getInfo()
fids1 = str(fids)

test_fire = fires.filter(ee.Filter.eq('Fire_ID', 'FOR13_1987_316'))
ft = test_fire.first()
# loop through list of fire ids

fireBounds = ft.geometry().bounds()
fyr = ft.get('Fire_Year')
fyr = fyr.getInfo()
fyr = str(fyr)
fireYear = ee.Date(fyr)
preFireYear = fireYear.advance(-1, 'year')

col =landsat_timeseries_legacy(
    roi=fireBounds,
    start_year= 1982,
    end_year=2023,
    start_date="04-01",
    end_date="11-15",
    apply_fmask=True,
    frequency="year",
    date_format=None,
)

lt = ee.Algorithms.TemporalSegmentation.LandTrendr(
       timeSeries=col.select(['NBR', 'SWIR2', 'NIR', 'Green']),
       maxSegments=10, 
       spikeThreshold=0.7, 
       vertexCountOvershoot=3,
       preventOneYearRecovery=True,
       recoveryThreshold=0.5,
       pvalThreshold=0.05,
       bestModelProportion=0.75,
       minObservationsNeeded=6)

def getYearStr(year):
  return(ee.String('yr_').cat(ee.Algorithms.String(year).slice(0,4)))

years = ee.List.sequence(1982, 2023)


yearsStr = years.map(getYearStr)

nir_fit = lt.select(['NIR_fit'])

swir2_fit = lt.select(['SWIR2_fit'])

NIRftvStack = nir_fit.arrayFlatten([yearsStr])


SWIRftvStack = swir2_fit.arrayFlatten([yearsStr]) 

# water mask
nir = water_mask(NIRftvStack)
swir = water_mask(SWIRftvStack)

#geemap.ee_export_image_to_drive(NIRftvStack, description='test_img', folder="chapter_3_landTrendr_test", region=fireBounds, scale=30)

### get RBR image
# create sequence for each fire to filter image to years we want
start = ee.Date(fireYear.advance(-1, 'year'))
start = getYearNumber(start)
end = ee.Date(fireYear.advance(11, 'year'))
end = getYearNumber(end)
yoi = ee.List.sequence(start, end)
yoiStr = yoi.map(getYearStr)
yoiStr = yoiStr.getInfo()

## filter image for the years we want
nir = nir.select(yoiStr)
swir = swir.select(yoiStr)

# def function, for each year, create new img for that year wth two bands
def mergeByYear(img1, img2, key):
  yr = getYear(yoiStr, key)
  nir2 = img1.select(yr).rename('nir')
  swir2 = img2.select(yr).rename('swir')
  merged = nir2.addBands(swir2)
  nbr= nbrPerYear(merged)
  if (key == 0):
    img = merged.addBands(nbr).select('nbr').rename('preNBR')
  elif (key == 2):
    img = merged.addBands(nbr).select('nbr').rename('postNBR')
  elif (key == 3):
    img = merged.addBands(nbr).select('nbr').rename('nbr_1yr')
  elif (key == 4):
    img = merged.addBands(nbr).select('nbr').rename('nbr_2yr')
  elif (key == 5):
    img = merged.addBands(nbr).select('nbr').rename('nbr_3yr')
  elif (key == 6):
    img = merged.addBands(nbr).select('nbr').rename('nbr_4yr')
  elif (key == 7):
    img = merged.addBands(nbr).select('nbr').rename('nbr_5yr')
  elif (key == 8):
    img = merged.addBands(nbr).select('nbr').rename('nbr_6yr')
  elif (key == 9):
    img = merged.addBands(nbr).select('nbr').rename('nbr_7yr')
  elif (key == 10):
    img = merged.addBands(nbr).select('nbr').rename('nbr_8yr')
  elif (key == 11):
    img = merged.addBands(nbr).select('nbr').rename('nbr_9yr')
  elif (key == 12):
    img = merged.addBands(nbr).select('nbr').rename('nbr_10yr')
  return(img)

test = mergeByYear(nir, swir, 0)

geemap.ee_export_image_to_drive(test, description='preNBR_test', folder="chapter_3_landTrendr_test", region=fireBounds, scale=30)


