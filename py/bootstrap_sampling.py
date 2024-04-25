def random_sample(da,
                  n, 
                  dim_slice,
                  keep_cols=True):
    """
    take a data array, turn to df and get random sample
    da = xarray data array with n dimensions
    n = number of samples
    dim_slice = slice along certain time dimension
    keep_cols = whether or not to drop crs , time and nbr col in all_samples df

    """
    # slice along dimension
    da2= da.isel(time=dim_slice)
    #to dataframe
    df = da2.to_dataframe()

    # sample location
    samples = []
    no_of_points = n
    # random sample of n points
    sample_loc = df.dropna().sample(n=int(round(no_of_points)))
    samples.append(sample_loc)
    #join back into single datafame
    all_samples = pd.concat([samples[i] for i in range(0,len(samples))])
    
    # x and y to lat and lon column
    all_samples.reset_index(inplace = True)
    all_samples = all_samples.rename(columns={'y': 'Lat', 'x': 'Long'}) 
    
    if keep_cols==False:
        #remove crs, nbr and time cols
        all_samples = all_samples.drop(columns =['crs', 'time', 'nbr'])
     # for each lat/long select pixel
    pix_samples = []
    for index, row in all_samples.iterrows():
        x = row['Long']
        y = row['Lat']
        df2 = da.to_dataframe()
        df2 = df2.dropna()
        df2 = std_nbr(df2)
        df2 = df2.loc[(df2['y'] == y) & (df2['x'] == x)]
        pix_samples.append(df2)

    #join back into single datafame
    all_samples = pd.concat([pix_samples[i] for i in range(0,len(pix_samples))])

    all_samples
  
    #remove crs
    all_samples = all_samples.drop(columns =['crs'])
    
    return(all_samples)