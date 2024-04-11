import ee 
import math
from ee_plugin import Map

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

fireID = ee.List(fires.aggregate_array('Fire_ID')).getInfo()
nFires = fireID.size()


#  PREFIRE SELECTION OF IMAGERY DATES:  This sets the range of dates to select imagery for computation of pre-fire NBR
#    Enter beginning and end days for imagery as julian days
PreFireStartDay = 140;  # May 20
PreFireEndDay   = 243;  # Aug 31


PostFireEndDayYOF   = 319;  # Nov 15
PostFireEndDayYAF   = 182;  # July 1
PostFireStartDayYOFdefault   = 258;  # Sept 15
PostFireStartDayYAFdefault   = 120;  # April 30

#  visualize fire perimeters
#Map.centerObject(fires)
#Map.addLayer(fires, {color: 'Red'}, "Fire perimeters")

#--------------------------         END OF INPUTS   -------------------------------------#
#----------------------------------------------------------------------------------------#


#----------------------------------------------------------------------------------------#
#---------------------------------     PROCESSING     -----------------------------------#

#-------------------------------  IDENTIFY JULIAN DAY WHEN FIRE ENDS  ------------------------------#

######################################/
# Import both MODIS Aqua and Terra Satellite imagery for thermal anomalies
terraFire = ee.ImageCollection('MODIS/006/MOD14A1')  # Terra Thermal Anomalies & Fire Daily Global 1km
aquaFire  = ee.ImageCollection('MODIS/006/MYD14A1')  # Aqua Thermal Anomalies & Fire Daily Global 1km

#################################################
# Filter MODIS collections for pixels that have 'nominal' or 'high' confidence of fire

#   Function to select pixels with nominal (8) or high (9) confidence of fire to create a 'fire' mask
def highConf(image):
  # Compute the bits we need to extract.
  pattern = 0
  for i in range(0, 3, 1):
    pattern += math.pow(2, i)

  # Make a single band image of the extracted QA bits, giving the band a new name.
  bits = image.select('FireMask') \
  .bitwiseAnd(pattern) \
  .rightShift(0)
  # MOD14 User Guide: Users requiring fewer False alarms (errors of commission)
  #   may wish to retain nominal- and high-confidence fire pixels:
  #   classes 8 and 9, respectively.
  return(image.updateMask(bits.gte(8).eq(1)))


#  apply fire mask function to each MODIS feature collection
terraFire=terraFire.map(highConf)
aquaFire =aquaFire.map(highConf)

#################################################
# Combine MODIS thermal image collections into one feature collection

# Function to combine MODIS collections into one by matching each day
#     Specify an equals filter for image timestamps.
filterTime = ee.Filter.equals({
    'leftField': 'system:time_start',
    'rightField': 'system:time_start'
  })

# Join Aqua and Terra collections using above filter based on timestamp
merged_feats= ee.Join.inner().apply(aquaFire, terraFire, filterTime).sort('system:time_start')

# Get daily max value of FireMask between Aqua and Terra images to determine if either platform
#    detected an active fire pixel

def func_ags(feature):
  return ee.ImageCollection([feature.get('primary'), feature.get('secondary')]) \
    .select('FireMask').max() \
    .copyProperties(feature.get('primary'), ['system:time_start'])

MODIS_highconf = merged_feats.map(func_ags)







########################################################
#  Function to evaluate the last day when a pixel burned within each fire perimeter (i.e. EOF = End Of Fire)

def addEOF(ft):
  # select fire and get fire year
  fireYear = ee.Number.parse(ft.get('Fire_Year'))
  fireBounds = ft.geometry().bounds()

  # Create dummy raster image cliped to geometry of fire perimeter
  # to be used in case a MODIS image timestep is missing
  def clip(img): return img.clip(ft)
  blank = ee.Image.constant(0).toUint8().rename('FireMask').clip(ft)
  blank = blank.updateMask(blank)

  # MODIS thermal image collection slightly filtered down to narrower range of fire season dates (Mar 15 - Nov 16)
  #    for faster processing, and to clip collection to fire perimeter and select FireMask
  collection = ee.ImageCollection(MODIS_highconf \
    .filterDate(ee.Date.fromYMD(fireYear,3,15), ee.Date.fromYMD(fireYear,11,16))) \
    .filterBounds(fireBounds) \
    .map(clip) \
    .select('FireMask')

  # simplify fire perimeter for faster processing
  ftsimp = ee.Feature(ft).geometry().simplify(20)

  # Create a list in days (in milliseconds) for the March 15 - Nov 15 period
  dayMillis = 24*60*60*1000
  listdates = ee.List.sequence(ee.Date.fromYMD(fireYear,3,15).millis(), ee.Date.fromYMD(fireYear,11,15).millis(), dayMillis)

  # function to get the total number of pixels burned within perimeter and the julian day (if no burning, pixel count is zero)

def func_mpl(day):

        # get modis image for day
        modis = ee.Image(collection.filterDate(day).first())
        modis = ee.Image(ee.Algorithms.If(modis, modis, blank)); # if MODIS time step is missing, provide dummy image

        # Calculate the number of 'active' fire pixels inside the fire perimeter on that day
        pixelcount = modis.reduceRegion(**{
          'reducer': ee.Reducer.count(),
          'geometry': ftsimp,
          'crs':'EPSG:4326',  # WGS84
          'scale': 1000,
          'bestEffort':True,
          'tileScale': 1
          }).getNumber('FireMask'); # Return the count of active fire pixels

        pixelcount = ee.Algorithms.If(pixelcount, pixelcount, ee.Number(0)) # if MODIS time step has no valid pixels, pixel count will be None; replace here with zero
        doy = ee.Date(day).format('D')                                   # get julian day
        return ee.Image(modis).set('DOY', doy, 'BurnCount', pixelcount)



EndBurnDay = ee.ImageCollection.fromImages(listdates.map(func_mpl))


  # Get the last julian day that a burned pixel occurred within fire perimeter

def func_kpi(number):
        number = ee.Algorithms.If(number, number, ee.Number(0))
        return ee.Number(number)
  BurnedOutDay = EndBurnDay.filter(ee.Filter.gt('BurnCount',0)).map(func_kpi).aggregate_max('DOY')).aggregate_max('DOY')

  BurnedOutDay = ee.Algorithms.If(BurnedOutDay,BurnedOutDay, 'NA')
  return ft.set({'EndBurnDay': BurnedOutDay}).setGeometry(None)



#/------------------       DONE WITH FIRE TERMINATION DAY PROCESS     -------------------------------------#


# ------------------IDENTIFY JULIAN DAY WHEN THE MAJORITY OF SNOW HAS MELTED --------------------------------#

# Load both MODIS Terra & Aqua Daily Snow Cover collections
terraSnow = ee.ImageCollection('MODIS/006/MOD10A1').select('NDSI_Snow_Cover')
aquaSnow  = ee.ImageCollection('MODIS/006/MYD10A1').select('NDSI_Snow_Cover')

#################################################
# Combine MODIS snow cover image collections into one feature collection

# Function to combine MODIS collections into one by matching each day
#     Specify an equals filter for image timestamps.
filterTime = ee.Filter.equals({
    'leftField': 'system:time_start',
    'rightField': 'system:time_start'
  })

# Join Aqua and Terra collections using above filter based on timestamp
merged_feats= ee.Join.inner().apply(terraSnow, aquaSnow, filterTime).sort('system:time_start')

# Get maximum value of snow cover for each day across Terra & Aqua snow cover bands.

def func_pyf(feature):
  return ee.ImageCollection([feature.get('primary'), feature.get('secondary')]).max() \
    .copyProperties(feature.get('primary'), ['system:time_start'])

yearlyCollection = merged_feats.map(func_pyf)





# function to convert all values <= 5% snow cover with their respective DOY
def returnDoy(feature):
  image = ee.Image(feature)
  # Get the Julian Day of the image from metadata (plus an extra day to get day after snow is gone)
  # getRelative converts from ee.Date object to a Julian DOY ee.Number object
  doy   = ee.Date(image.get('system:time_start')).getRelative('day','year').add(1)

  # Convert all pixel values in image at or below 5% snowcover to the images DOY
  replacement = image.expression(
      'SNOW <= 5 ? DOY : 9999', {
        'SNOW': image.select('NDSI_Snow_Cover'),
        'DOY': doy
  }).toInt()

 # Create mask for pixels with greater than 5% snowcover (pixels = 9999 after previous expression)
  withObs = replacement.neq(9999)
  return replacement.updateMask(withObs)


# function to determine the earliest julian day of snowmelt (defined as <=5% snow cover) inside of fire perimeter, between Feb 1 - July 1 in the year after fire, using these steps:
#      (a) determine the earliest julian day of snowmelt (defined as <=5% snow cover) for each pixel
#      (b) calculate the 95th and 75th percentiles of these julian days across the fire perimeter.
#      (c) if 95th percentile is < Jul 1, then use the 95th percentile value, otherwise evaluate the 75th percentile value, and
#          if 75th percentile value < Jul 1, use 75th percentile value, else assume April 30th.
def addSnowMelt(ft):
  # select fire
  fireYear = ee.Number.parse(ft.get('Fire_Year')).add(1);  # want year-after-fire
  fireBounds = ft.geometry().bounds()
  def clip(img) return img.clip(ft);}:

  # Use one of two collections, depending on the year: (1) terraSnow unmerged for 2000 - 2002, (2) aquaSnow/terraSnow merged for 2003 to present
  snowCollection = ee.ImageCollection(ee.Algorithms.If(fireYear.gte(2003), yearlyCollection, terraSnow))

  # limit imagecollection to Feb 1 - July 1 of post-fire year & to fire perimeter
  #   and get julian days with low (<=5%) snowcover (all other days with more snow cover are masked)
  collection = ee.ImageCollection(snowCollection \
    .filterDate(ee.Date.fromYMD(fireYear,2,1), ee.Date.fromYMD(fireYear,7,1))) \
    .filterBounds(fireBounds) \
    .map(clip) \
    .map(returnDoy)

  # Get earliest day for each pixel when snow cover <=5% across fire perimeter
  snowMeltDay = ee.ImageCollection(collection) \
    .reduce(ee.Reducer.min()) \
    .select(['constant_min'], ['snowMeltDOY']);  

  # calculate the 95th and 75th percentile of the DOY of snowmelt of pixels inside the fire perimeter
  #  (i.e. date when 95% or 75% of pixels' snow has melted)
  perclist = ee.List([95,75]);   # define the percentiles

  # Second, reduce the pixel values inside the fire perimeter using percentile reducer
  # with the percentiles defined as above

def func_uon(p):
          sm = snowMeltDay.reduceRegion({
          'reducer': ee.Reducer.percentile([p]),
          'geometry': ee.Feature(ft).geometry(),
          'crs':'EPSG:4326',
          'scale': 1000,
          }).getNumber('snowMeltDOY')
          return sm

  smday = perclist.map(func_uon)










  # If 95th percentile snowmelt DOY is before Jul 1, use it, otherwise use the 75th percentile snowmelt DOY
  snowMelt95 = ee.Algorithms.If(smday.getNumber(1).gt(PostFireEndDayYAF),smday.getNumber(2),smday.getNumber(1))
  # If 75th percentile snowmelt DOY is before Jul 1, use it, otherwise default to defined post-fire start day (e.g. April 30th) for year-after-fire
  snowMeltFinal = ee.Number.parse(ee.Algorithms.If(ee.Number(snowMelt95).gt(PostFireEndDayYAF),PostFireStartDayYAFdefault, snowMelt95)).int()

  return ft.set({'SnowMeltDay': snowMeltFinal}).setGeometry(None)


#/------------------       DONE WITH SNOWMELT DAY PROCESS     -------------------------------------#

#------------------------    CREATE SEVERITY IMAGERY --------------- ------------------------------#

# create list with fire IDs
fireID    = ee.List(fires.aggregate_array('Fire_ID')).getInfo()
nFires = fireID.length

#------------------- Image Processing for Fires Begins Here -------------#

# Landsat 4, 5, 7, and 8 Surface Reflectance Tier 1 collections
ls8SR = ee.ImageCollection('LANDSAT/LC08/C02/T2_L2'),
    ls7SR = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2'),
    ls5SR = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2'),
    ls4SR = ee.ImageCollection('LANDSAT/LT04/C02/T1_L2')

################/
# FUNCTIONS TO CREATE NBR
################/

# Returns vegetation indices for LS8
def ls8_Indices(lsImage):
  nbr = lsImage.normalizedDifference(['SR_B4', 'SR_B7']).toFloat()
  qa = lsImage.select(['QA_PIXEL'])
  return nbr.addBands([qa]) \
          .select([0,1], ['nbr', 'QA_PIXEL']) \
          .copyProperties(lsImage, ['system:time_start'])
  

# Returns vegetation indices for LS4, LS5 and LS7
def ls4_7_Indices(lsImage):
  nbr = lsImage.normalizedDifference(['SR_B4', 'SR_B7']).toFloat()
  qa = lsImage.select(['QA_PIXEL'])
  return nbr.addBands([qa]) \
          .select([0,1], ['nbr', 'QA_PIXEL']) \
          .copyProperties(lsImage, ['system:time_start'])
  

# Mask Landsat surface reflectance images
# Creates a mask for clear pixels
def lsCfmask(lsImg):
  quality =lsImg.select(['QA_PIXEL'])
  clear = quality.bitwiseAnd(4).eq(0) # cloud shadow \
                .And(quality.bitwiseAnd(3).eq(0) \
                .And(quality.bitwiseAnd(7).eq(0) \
                .And(quality.bitwiseAnd(5).eq(0)))); 
  return lsImg.updateMask(clear).select([0]) \
            .copyProperties(lsImg, ['system:time_start'])


# Map functions across Landsat Collections
ls8 = ls8SR.map(ls8_Indices) \
                .map(lsCfmask)
ls7 = ls7SR.map(ls4_7_Indices) \
                .map(lsCfmask)
ls5 = ls5SR.map(ls4_7_Indices) \
                .map(lsCfmask)
ls4 = ls4SR.map(ls4_7_Indices) \
                .map(lsCfmask)

# Merge Landsat Collections
lsCol = ee.ImageCollection(ls8.merge(ls7).merge(ls5).merge(ls4))

# # #test

# fireTest = fires.filter(ee.Filter.eq('Fire_ID', "RED28_2012_1849")).first()
# print(fireTest)
# fyy = ee.Date.parse('YYYY', fireTest.get('Fire_Year'))
# fbounds = fireTest.geometry().bounds()
# postFireYear = fyy.advance(10, 'year')
# postFireYear2 = postFireYear.advance(100, 'day')
# postFireYear21 = postFireYear.advance(242, 'day')
# print(postFireYear2)
# print(postFireYear21)
# index = fireTest.get("system:index")
# print(index)

# postFireIndices2 = lsCol.filterBounds(fbounds)
#                           .filterDate(postFireYear2, postFireYear21)
#                           .mean()
#                           .rename('nbrtwo')

# print(postFireIndices2)




# ------------------ Create Fire Severity Imagery for each fire -----------------#

def func_pyp(ft):
  # use 'Fire_ID' as unique identifier
  fName = ft.get("Fire_ID")
  fire = ft
  fireBounds = ft.geometry().bounds()
  Year = ee.Number.parse(fire.get('Fire_Year'))
  fireYear = ee.Date.parse('YYYY', fire.get('Fire_Year'))

  #  Get PostFire start days for year-of-fire & year-after-fire by running MODIS functions above
  # if no EOF day is determined, set default to 258 (Sept 15)
  BurnedOutDay = addEOF(ft).get('EndBurnDay')
  BurnedOutDay = ee.Number.parse(ee.Algorithms.If(BurnedOutDay='NA',PostFireStartDayYOFdefault, BurnedOutDay)).int()

  PostFireStartDayYOF = ee.Algorithms.If(Year.gte(2000),BurnedOutDay, PostFireStartDayYOFdefault)
  SnowMelted = addSnowMelt(ft).get('SnowMeltDay')

  PostFireStartDayYAF = ee.Algorithms.If(Year.gte(2000),SnowMelted, PostFireStartDayYAFdefault)

  # Create Pre-Fire NBR as mean composite
  preFireYear = fireYear.advance(-1, 'year')
  preFireIndices = lsCol.filterBounds(fireBounds) \
                          .filterDate(preFireYear, fireYear) \
                          .filter(ee.Filter.dayOfYear(PreFireStartDay, PreFireEndDay)) \
                          .mean() \
                          .rename('preNBR')

  # if any pixels within fire have no data due to clouds, go back two years to fill in no data areas
  preFireIndices2 = lsCol.filterBounds(fireBounds) \
                          .filterDate(fireYear.advance(-2, 'year'), fireYear) \
                          .filter(ee.Filter.dayOfYear(PreFireStartDay, PreFireEndDay)) \
                          .mean() \
                          .rename('preNBR')
  preFireIndices = ee.Image(preFireIndices).unmask(preFireIndices2)

  # if band is non-existent (i.e. no data), add a masked band of the same name (ie: replace it).
  preFireIndices = ee.Image().rename("preNBR").addBands(preFireIndices, None, True)

  # Create Post-Fire NBR as mean composite
  postFireYear = fireYear.advance(1, 'year')
  postFireIndices = lsCol.filterBounds(fireBounds) \
                          .filter(
                            ee.Filter.Or(
                              ee.Filter.And(
                                ee.Filter.date(fireYear, fireYear.advance(1, 'year')),
                                ee.Filter.dayOfYear(PostFireStartDayYOF, PostFireEndDayYOF)),
                              ee.Filter.And(
                                ee.Filter.date(postFireYear, fireYear.advance(2, 'year')),
                                ee.Filter.dayOfYear(PostFireStartDayYAF, PostFireEndDayYAF))
                              )) \
                          .mean() \
                          .rename('postNBR')

  # if band is non-existent (i.e. no data), add a masked band of the same name (ie: replace it).
  postFireIndices = ee.Image().rename("postNBR").addBands(postFireIndices, None, True)

  ##############################################/
  # Create Post fire band for 10 years after the fire.
  #Create post fire years of interest

  postFireYear1 = fireYear.advance(1, 'year')
  postFireYear1a = postFireYear1.advance(141, 'day')
  postFireYear1b = postFireYear1.advance(242, 'day')
  postFireYear2 = fireYear.advance(2, 'year')
  postFireYear2a = postFireYear2.advance(141, 'day')
  postFireYear2b = postFireYear2.advance(242, 'day')
  postFireYear3 = fireYear.advance(3, 'year')
  postFireYear3a = postFireYear3.advance(141, 'day')
  postFireYear3b = postFireYear3.advance(242, 'day')
  postFireYear4 = fireYear.advance(4, 'year')
  postFireYear4a = postFireYear4.advance(141, 'day')
  postFireYear4b = postFireYear4.advance(242, 'day')
  postFireYear5 = fireYear.advance(5, 'year')
  postFireYear5a = postFireYear5.advance(141, 'day')
  postFireYear5b = postFireYear5.advance(242, 'day')
  postFireYear6 = fireYear.advance(6, 'year')
  postFireYear6a = postFireYear6.advance(141, 'day')
  postFireYear6b = postFireYear6.advance(242, 'day')
  postFireYear7 = fireYear.advance(7, 'year')
  postFireYear7a = postFireYear7.advance(141, 'day')
  postFireYear7b = postFireYear7.advance(242, 'day')
  postFireYear8 = fireYear.advance(8, 'year')
  postFireYear8a = postFireYear8.advance(141, 'day')
  postFireYear8b = postFireYear8.advance(242, 'day')
  postFireYear9 = fireYear.advance(9, 'year')
  postFireYear9a = postFireYear9.advance(141, 'day')
  postFireYear9b = postFireYear9.advance(242, 'day')
  postFireYear10 = fireYear.advance(10, 'year')
  postFireYear10a = postFireYear10.advance(141, 'day')
  postFireYear10b = postFireYear10.advance(2242, 'day')


#fire years go from 1986-2020. Is there a way to loop through the code and say if there is only 3 years, leave the rest blank

postFireIndices1 = lsCol.filterBounds(fireBounds) \
                          .filterDate(postFireYear1a, postFireYear1b) \
                          .mean() \
                          .rename('nbr1')

postFireIndices2 = lsCol.filterBounds(fireBounds) \
                          .filterDate(postFireYear2a, postFireYear2b) \
                          .mean() \
                          .rename('nbr2')


postFireIndices3 = lsCol.filterBounds(fireBounds) \
                          .filterDate(postFireYear3a, postFireYear3b) \
                          .mean() \
                          .rename('nbr3')

postFireIndices4 = lsCol.filterBounds(fireBounds) \
                          .filterDate(postFireYear4a, postFireYear4b) \
                          .mean() \
                          .rename('nbr4')


postFireIndices5 = lsCol.filterBounds(fireBounds) \
                          .filterDate(postFireYear5a, postFireYear5b) \
                          .mean() \
                          .rename('nbr5')

postFireIndices6 = lsCol.filterBounds(fireBounds) \
                          .filterDate(postFireYear6a, postFireYear6b) \
                          .mean() \
                          .rename('nbr6')

postFireIndices7 = lsCol.filterBounds(fireBounds) \
                          .filterDate(postFireYear7a, postFireYear7b) \
                          .mean() \
                          .rename('nbr7')

postFireIndices8 = lsCol.filterBounds(fireBounds) \
                          .filterDate(postFireYear8a, postFireYear8b) \
                          .mean() \
                          .rename('nbr8')

postFireIndices9 = lsCol.filterBounds(fireBounds) \
                          .filterDate(postFireYear9a, postFireYear9b) \
                          .mean() \
                          .rename('nbr9')

postFireIndices10 = lsCol.filterBounds(fireBounds) \
                          .filterDate(postFireYear10a, postFireYear10b) \
                          .mean() \
                          .rename('nbr10')
#add bands
nbrRecov = postFireIndices1.addBands(postFireIndices2) \
                          .addBands(postFireIndices3) \
                          .addBands(postFireIndices4) \
                          .addBands(postFireIndices5) \
                          .addBands(postFireIndices6) \
                          .addBands(postFireIndices7) \
                          .addBands(postFireIndices8) \
                          .addBands(postFireIndices9) \
                          .addBands(postFireIndices10) \
                          .addBands(preFireIndices)



  return nbrRecov.set({
                        'fireID' : ft.get('Fire_ID'),
                        'fireYear' : ft.get('Fire_Year')
  })

indices = ee.ImageCollection(fires.map(func_pyp))


 for j in fireID:
  id   = j
  Name = id
  fireExport = ee.Image(indices.filterMetadata('fireID', 'equals', id).first())
  fireBounds = ee.Feature(fires.filterMetadata('Fire_ID', 'equals', id).first()).geometry().bounds()

  task = ee.batch.Export.image.toDrive(**{
    'image': fireExport,
    'description': Name,
    'folder':'nbr_chapter3_imagery',
    'scale': 30,
    'region': fireBounds.getInfo()['coordinates']
    })
      
    # start task
    task.start()
    
    
    #Export.image.toDrive({
    #  'image': exportImg,
     # 'description': Name + '_' + bandExport,
    #  'fileNamePrefix': Name + '_' + bandExport,
     # 'maxPixels': 1e13,
    #  'scale': 30,
     # 'crs': "EPSG:4326",
      #'folder': 'fires',
      #'region': fireBounds
  #})








