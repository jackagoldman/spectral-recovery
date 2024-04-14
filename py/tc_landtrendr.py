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
fids1 = str(fids)

test_fire = fires.filter(ee.Filter.eq('Fire_ID', 'QC_533_1996'))
ft = test_fire.first()
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
  
  
  #tca
  tcaP = tca.select(getYear(yoiStr, 0)).rename('tca_pre')
  tcaY = tca.select(getYear(yoiStr, 1)).rename('tca_yof')
  tca1 = tca.select(getYear(yoiStr, 2)).rename('tca_1yr')
  tca2 = tca.select(getYear(yoiStr, 3)).rename('tca_2yr')
  tca3 = tca.select(getYear(yoiStr, 4)).rename('tca_3yr')
  tca4 = tca.select(getYear(yoiStr, 5)).rename('tca_4yr')
  tca5 = tca.select(getYear(yoiStr, 6)).rename('tca_5yr')
  tca6 = tca.select(getYear(yoiStr, 7)).rename('tca_6yr')
  tca7 = tca.select(getYear(yoiStr, 8)).rename('tca_7yr')
  tca8 = tca.select(getYear(yoiStr, 9)).rename('tca_8yr')
  tca9 = tca.select(getYear(yoiStr, 10)).rename('tca_9yr')
  tca10 = tca.select(getYear(yoiStr,11)).rename('tca_10yr')
  
  #tcg
  tcgP = tcg.select(getYear(yoiStr, 0)).rename('tcg_pre')
  tcgY = tcg.select(getYear(yoiStr, 1)).rename('tcg_yof')
  tcg1 = tcg.select(getYear(yoiStr, 2)).rename('tcg_1yr')
  tcg2 = tcg.select(getYear(yoiStr, 3)).rename('tcg_2yr')
  tcg3 = tcg.select(getYear(yoiStr, 4)).rename('tcg_3yr')
  tcg4 = tcg.select(getYear(yoiStr, 5)).rename('tcg_4yr')
  tcg5 = tcg.select(getYear(yoiStr, 6)).rename('tcg_5yr')
  tcg6 = tcg.select(getYear(yoiStr, 7)).rename('tcg_6yr')
  tcg7 = tcg.select(getYear(yoiStr, 8)).rename('tcg_7yr')
  tcg8 = tcg.select(getYear(yoiStr, 9)).rename('tcg_8yr')
  tcg9 = tcg.select(getYear(yoiStr, 10)).rename('tcg_9yr')
  tcg10 = tcg.select(getYear(yoiStr,11)).rename('tcg_10yr')
  
   #tcw
  tcwP = tcw.select(getYear(yoiStr, 0)).rename('tcw_pre')
  tcwY = tcw.select(getYear(yoiStr, 1)).rename('tcw_yof')
  tcw1 = tcw.select(getYear(yoiStr, 2)).rename('tcw_1yr')
  tcw2 = tcw.select(getYear(yoiStr, 3)).rename('tcw_2yr')
  tcw3 = tcw.select(getYear(yoiStr, 4)).rename('tcw_3yr')
  tcw4 = tcw.select(getYear(yoiStr, 5)).rename('tcw_4yr')
  tcw5 = tcw.select(getYear(yoiStr, 6)).rename('tcw_5yr')
  tcw6 = tcw.select(getYear(yoiStr, 7)).rename('tcw_6yr')
  tcw7 = tcw.select(getYear(yoiStr, 8)).rename('tcw_7yr')
  tcw8 = tcw.select(getYear(yoiStr, 9)).rename('tcw_8yr')
  tcw9 = tcw.select(getYear(yoiStr, 10)).rename('tcw_9yr')
  tcw10 = tcw.select(getYear(yoiStr,11)).rename('tcw_10yr')
  
   #tcb
  tcbP = tcb.select(getYear(yoiStr, 0)).rename('tcb_pre')
  tcbY = tcb.select(getYear(yoiStr, 1)).rename('tcb_yof')
  tcb1 = tcb.select(getYear(yoiStr, 2)).rename('tcb_1yr')
  tcb2 = tcb.select(getYear(yoiStr, 3)).rename('tcb_2yr')
  tcb3 = tcb.select(getYear(yoiStr, 4)).rename('tcb_3yr')
  tcb4 = tcb.select(getYear(yoiStr, 5)).rename('tcb_4yr')
  tcb5 = tcb.select(getYear(yoiStr, 6)).rename('tcb_5yr')
  tcb6 = tcb.select(getYear(yoiStr, 7)).rename('tcb_6yr')
  tcb7 = tcb.select(getYear(yoiStr, 8)).rename('tcb_7yr')
  tcb8 = tcb.select(getYear(yoiStr, 9)).rename('tcb_8yr')
  tcb9 = tcb.select(getYear(yoiStr, 10)).rename('tcb_9yr')
  tcb10 = tcb.select(getYear(yoiStr,11)).rename('tcb_10yr')
  
 
  
  # add bands
  #tca
  tcaBands = tcaP.addBands(tcaY)
  tcaBands = tcaBands.addBands(tca1)
  tcaBands = tcaBands.addBands(tca2)
  tcaBands = tcaBands.addBands(tca3)
  tcaBands = tcaBands.addBands(tca4)
  tcaBands = tcaBands.addBands(tca5)
  tcaBands = tcaBands.addBands(tca6)
  tcaBands = tcaBands.addBands(tca7)
  tcaBands = tcaBands.addBands(tca8)
  tcaBands = tcaBands.addBands(tca9)
  tcaBands = tcaBands.addBands(tca10)
  
  #tcb
  tcbBands = tcbP.addBands(tcbY)
  tcbBands = tcbBands.addBands(tcb1)
  tcbBands = tcbBands.addBands(tcb2)
  tcbBands = tcbBands.addBands(tcb3)
  tcbBands = tcbBands.addBands(tcb4)
  tcbBands = tcbBands.addBands(tcb5)
  tcbBands = tcbBands.addBands(tcb6)
  tcbBands = tcbBands.addBands(tcb7)
  tcbBands = tcbBands.addBands(tcb8)
  tcbBands = tcbBands.addBands(tcb9)
  tcbBands = tcbBands.addBands(tcb10)
  
  #tcw
  tcwBands = tcwP.addBands(tcwY)
  tcwBands = tcwBands.addBands(tcw1)
  tcwBands = tcwBands.addBands(tcw2)
  tcwBands = tcwBands.addBands(tcw3)
  tcwBands = tcwBands.addBands(tcw4)
  tcwBands = tcwBands.addBands(tcw5)
  tcwBands = tcwBands.addBands(tcw6)
  tcwBands = tcwBands.addBands(tcw7)
  tcwBands = tcwBands.addBands(tcw8)
  tcwBands = tcwBands.addBands(tcw9)
  tcwBands = tcwBands.addBands(tcw10)
  
  #tcg
  tcgBands = tcgP.addBands(tcgY)
  tcgBands = tcgBands.addBands(tcg1)
  tcgBands = tcgBands.addBands(tcg2)
  tcgBands = tcgBands.addBands(tcg3)
  tcgBands = tcgBands.addBands(tcg4)
  tcgBands = tcgBands.addBands(tcg5)
  tcgBands = tcgBands.addBands(tcg6)
  tcgBands = tcgBands.addBands(tcg7)
  tcgBands = tcgBands.addBands(tcg8)
  tcgBands = tcgBands.addBands(tcg9)
  tcgBands = tcgBands.addBands(tcg10)
  
 
  
  export_tca_name = Name + "_tca"
  export_tcb_name = Name + "_tcb"
  export_tcw_name = Name + "_tcw"
  export_tcg_name = Name + "_tcg"
  
  # export  burn Indices imagery
  geemap.ee_export_image_to_drive(tcaBands, description=export_tca_name , folder="chapter3_lt_tca", region=fireBounds, scale=30)
  #export tcb
  geemap.ee_export_image_to_drive(tcbBands, description=export_tcb_name , folder="chapter3_lt_tcb", region=fireBounds, scale=30)
  #tcw
  geemap.ee_export_image_to_drive(tcwBands, description=export_tcw_name , folder="chapter3_lt_tcw", region=fireBounds, scale=30)
  #tcg
  geemap.ee_export_image_to_drive(tcgBands, description=export_tcg_name , folder="chapter3_lt_tcg", region=fireBounds, scale=30)




