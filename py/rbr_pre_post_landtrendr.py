import ee
import geemap
import numpy as np
import geopandas as gpd
import pandas as pd
import os
from ltgee import LandTrendr
from datetime import date
import ltgee

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


############### START OF LANDTRENDR AND BURN SEVERITY ANALYSIS ###############

# get Fires
fids = fires.aggregate_array('Fire_ID')
 # turn it to python list
fids = fids.getInfo()


test_fire = fires.filter(ee.Filter.eq('Fire_ID','FOR13_1987_316'))
ft = test_fire.first()
'RED7_1986_119'
# loop through list of fire ids

for j in fids:
  Name = j
  fiya= fires.filterMetadata('Fire_ID', 'equals', Name).first();
  ft = ee.Feature(fiya)
  fName = ft.get("Fire_ID")
  fire = ft


  fireBounds = ft.geometry().bounds()
  fyr = ft.get('Fire_Year')
  fyr = fyr.getInfo()
  fyr = str(fyr)
  fireYear = ee.Date(fyr)
  preFireYear = fireYear.advance(-1, 'year')
  
  
  lt_params = {
      "start_date": date(1984, 4,1),
      "end_date": date(2021, 11,1),
      "index": 'NBR',
      "ftv_list": ['TCB', 'TCG', 'TCW', 'TCA', 'NBR'],
      "mask_labels": ['cloud', 'shadow', 'snow', 'water'],
      "area_of_interest": fireBounds 
      ,"run_params": {
              "maxSegments": 6,
              "spikeThreshold": 0.9,
              "vertexCountOvershoot":  3,
              "preventOneYearRecovery":  True,
              "recoveryThreshold":  0.25,
              "pvalThreshold":  .05,
              "bestModelProportion":  0.75,
              "minObservationsNeeded": 2,
          }}

  lt = LandTrendr(debug=True, **lt_params)
  lt.run()
  
  #lt.data.getInfo()
  #lt.sr_collection.getInfo()
 
  #lt.lt_collection.getInfo()
   
 # lt.clear_pixel_count_collection
   
  ftv_nbr = lt.data.select('ftv_nbr_fit').clip(lt_params['area_of_interest'])
  ftv_tca = lt.data.select('ftv_tca_fit').clip(lt_params['area_of_interest'])
  ftv_tcb = lt.data.select('ftv_tcb_fit').clip(lt_params['area_of_interest'])
  ftv_tcw = lt.data.select('ftv_tcw_fit').clip(lt_params['area_of_interest'])
  ftv_tcg = lt.data.select('ftv_tcg_fit').clip(lt_params['area_of_interest'])
  
  
  # creat list of years to get imagery
  years = ee.List.sequence(1984, 2021)
  
  # make it a string
  yearsStr = years.map(getYearStr)
  
   ### get RBR image
  # create sequence for each fire to filter image to years we want
  start = ee.Date(fireYear.advance(-1, 'year'))
  start = getYearNumber(start)
  end = ee.Date(fireYear.advance(11, 'year'))
  end = getYearNumber(end)
  yoi = ee.List.sequence(start, end)
  yoiStr = yoi.map(getYearStr)
  yoiStr = yoiStr.getInfo()
 
  
  #nbr
  ftv_nbr2 = ftv_nbr.arrayFlatten([yearsStr])
  nbr = ftv_nbr2.select(yoiStr)
  
  #tca
  ftv_tca2 = ftv_tca.arrayFlatten([yearsStr])
  tca = ftv_tca2.select(yoiStr)
  
  #tcb
  ftv_tcb2 = ftv_tcb.arrayFlatten([yearsStr])
  tcb = ftv_tcb2.select(yoiStr)
  
  #tcw
  ftv_tcw2 = ftv_tcw.arrayFlatten([yearsStr])
  tcw = ftv_tcw2.select(yoiStr)
  
  #tcg
  ftv_tcg2 = ftv_tcg.arrayFlatten([yearsStr])
  tcg = ftv_tcg2.select(yoiStr)
  
  

  ## get nbr
  preNBR = nbr.select(getYear(yoiStr, 0)).rename('preNBR').toFloat()
  postNBR = nbr.select(getYear(yoiStr, 2)).rename('postNBR').toFloat()
  
  # scale nbr
  preNBR = preNBR.select('preNBR').divide(1000)
  postNBR = postNBR.select('postNBR').divide(1000)


  # add prefire and post fire
  indices = preNBR.addBands(postNBR)
  
  export_pp_name = Name + "_pp"

  #export pre/post
  geemap.ee_export_image_to_drive(indices, description=export_pp_name , folder="chapter3_lt_pp", region=fireBounds, scale=30, maxPixels = 1e13)


 
