def check_image_info(img):
  imgInf = img.getInfo()
  print(imgInf)
  
  # Returns vegetation indices for LS8 / change to CO2_T2_L2
def ls8_Indices(lsImage):
  nbr = lsImage.normalizedDifference(['SR_B5', 'SR_B7']).toFloat()
  qa = lsImage.select(['QA_PIXEL'])
  ndsi = image.normalizedDifference({'SR_B3', 'SR_B6'}).toFloat()
  nbr = nbr.addBands(ndsi)
  return nbr.addBands([qa]).select([0,1,2], ['nbr', 'ndsi','QA_PIXEL']).copyProperties(lsImage, ['system:time_start'])

  
#// Returns vegetation indices for LS4, LS5 and LS7 . change to CO2_T2_L2
 def ls4_7_Indices(lsImage):
   nbr = lsImage.normalizedDifference(['SR_B4', 'SR_B7']).toFloat()
   ndsi = image.normalizedDifference({'SR_B2', 'SR_B5'}).toFloat()
   nbr = nbr.addBands(ndsi)
   qa = lsImage.select(['QA_PIXEL'])
   return nbr.addBands([qa]).select([0,1,2], ['nbr','ndsi', 'QA_PIXEL']).copyProperties(lsImage, ['system:time_start'])
  
 
# Mask Landsat surface reflectance images
# Creates a mask for clear pixels 
 def lsCfmask(lsImg):
  qa = lsImg.select("QA_PIXEL")
  cloudBitMask = 1 << 3
  cirrusBitMask = 1 << 4
  waterBitMask = 1 << 7
  mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0)).And(
    qa.bitwiseAnd(waterBitMask).eq(0))
  return lsImg.updateMask(mask) \
      .select("nbr") \
      .copyProperties(lsImg, ["system:time_start"])
   
   
#  check to see if there are pixels: this prints to console
def check_pixel_count(img, geom):
  res = img.reduceRegion(**{
  'reducer': ee.Reducer.count(),\
  'geometry':geom,\
  'scale': 30})
  print(res.getInfo())


# check to see if there are pixels: this returns a number object
def return_pixel_count(img, geom, time):
  res = img.reduceRegion(**{
  'reducer': ee.Reducer.count(),\
  'geometry':geom,\
  'scale': 30})
  if time == "preNBR":
    res = res.getNumber('preNBR')
  elif time == "postNBR":
    res = res.getNumber('postNBR')
  return(res.getInfo())

# check dates - converts ee date to y-m-d and prints in console
def check_dates(date):
  date = date.format('Y-M-d')
  print(date.getInfo())


# check if image contains key
def get_keys(img, geom):
  res = img.reduceRegion(**{
  'reducer': ee.Reducer.count(),\
  'geometry':geom,\
  'scale': 30})
  res = res.keys()
  return(res.getInfo())


# mask imagery
def create_mask_from_shapefile(input_shapefile, raster_path, out_path):
"""
this function crops a raster based on a feature in a shapefile which matches the id
takes three arguments:
input_shapefile
raster_path
out_path
"""
#first loop through dir
    with os.scandir(raster_path) as p: # Open the folder containing the rasters as p.
        for raster in p: # Get each raster in the folder.
          with rasterio.open(raster, 'r') as src:
            name = src.name
            name = name.replace('/Users/jgoldman/Google Drive/My Drive/winter_test_folder/', '')
            name = name.replace('.tif', "")
            
            # read in shapefile
            with fiona.open(input_shapefile) as shp:
              for feature in shp:
                  if feature['properties']['Fire_ID'] in name:
                    shape = [feature['geometry']]
                    out_image, out_transform = mask(src, shape, crop=True) # setting all pixels outside of the feature zone to zero
                    out_meta = src.meta
        
                    out_meta.update({"driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform})
            
                   # write output name
                    output_file = name + '.tif'
                
                    with rasterio.open(os.path.join(out_path, output_file), "w", **out_meta) as dest:
                        dest.write(out_image)
                    

