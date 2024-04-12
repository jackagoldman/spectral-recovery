# raster processing

crop_rasters <- function(dir, shapefile, out_dir, file_extension){
  
  #get a list of all files with ndvi in the name in your directory
  files<-list.files(path=dir, pattern='*.tif', full.names = TRUE)
  
  if (file_extension == "defol"){
    # get file name and filter it from shapefile
    for (file in files){
      name <- file
      raster <- terra::rast(file)
      name <- basename(name)
      name <- gsub(".tif", "", name)
      
      # get shp that matches name
      shp <- shapefile |> dplyr::filter(Fire_ID == name)
      
      #crop
      cropped_raster <- terra::crop(raster, shp, mask=TRUE)
      
      # get output path
      savename<-paste0(out_dir, name, "_defol", ".tif")
      
      # write raster
      terra::writeRaster(cropped_raster, filename = savename)
    }}else if (file_extension == "non_defol"){
      for (file in files){
        name <- file
        raster <- terra::rast(file)
        name <- basename(name)
        name <- gsub(".tif", "", name)
        
        # get shp that matches name
        shp <- shapefile |> dplyr::filter(Fire_ID == name)
        
        #crop
        cropped_raster <- terra::crop(raster, shp, mask=TRUE, overwrite = TRUE)
        
        # get output path
        savename<-paste0(out_dir, name, "_non_defol", ".tif")
        
        # write raster
        terra::writeRaster(cropped_raster, filename = savename)
        
      }}
      
}


get_values <- function(dir, file_extension){
  
  #get a list of all files with ndvi in the name in your directory
  files<-list.files(path=dir, pattern='*.tif', full.names = TRUE)
  
  dflist <- list()
  
  if (file_extension == "defol"){
    for (file in files){
      name <- file
      raster <- terra::rast(file)
      # get raster name
      name <- terra::sources(raster)
      name <- basename(name)
      name <- name |> stringr::str_replace("_defol.tif", "")
      
      # get values
      df <- terra::values(raster, dataframe = TRUE)
      df <- na.omit(df) # remove na's
      df <- dplyr::summarise_all(df, mean)# summarise all columns
      df$fire_id <- name # get name and add to column
      
      # add defol column
      df$defoliated <- 1
      
      dflist[[file]] <- df
    
    }
  }else if (file_extension == "non_defol"){
    for (file in files){
      name <- file
      raster <- terra::rast(file)
      # get raster name
      name <- terra::sources(raster)
      name <- basename(name)
      name <- name |> stringr::str_replace("_non_defol.tif", "")
      
      # get values
      df <- terra::values(raster, dataframe = TRUE)
      df <- na.omit(df) # remove na's
      df <- dplyr::summarise_all(df, mean)# summarise all columns
      df$fire_id <- name # get name and add to column
      
      # add defol column
      df$defoliated <- 0
      
      dflist[[file]] <- df
    }}
  
  data <- do.call(rbind, dflist)
  
  rownames(data) <- NULL
  
  data$nbr7 <- sprintf("%.5f", data$nbr7)
  
  return(data)
  
}


#take in shapefile or dataset with area column. shape index?
area_weighted_raster_values <- function(img, shapefile){
  
  
  
}
