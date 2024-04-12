def getRecov(fire):
  fireBounds = ft.geometry().bounds()
  year = ft.get('Fire_Year')
  year = year.getInfo()
  year = str(year)
  fireYear = ee.Date(year)
  preFireYear = fireYear.advance(-1, 'year')
  preFireIndices = lsCol.filterBounds(fireBounds) \
                            .filterDate(preFireYear, fireYear) \
                            .filter(ee.Filter.dayOfYear(PreFireStartDay, PreFireEndDay)) \
                            .select('nbr') \
                            .mean() \
                            .rename('preNBR')
  postFireYear = fireYear.advance(1, 'year')
  postFireIndices = lsCol.filterBounds(fireBounds).filter(
                              ee.Filter.Or(
                                ee.Filter.And(
                                  ee.Filter.date(fireYear, fireYear.advance(1, 'year')),
                                  ee.Filter.dayOfYear(PostFireStartDayYOFdefault, PostFireEndDayYOF)),
                                ee.Filter.And(
                                  ee.Filter.date(postFireYear, fireYear.advance(2, 'year')),
                                  ee.Filter.dayOfYear(PostFireStartDayYAFdefault, PostFireEndDayYAF))
                                )) \
                            .select('nbr') \
                            .mean() \
                            .rename('postNBR')
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
  postFireYear10b = postFireYear10.advance(242, 'day')
  
  
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
  nbrRecov = postFireIndices1.addBands(postFireIndices2)
  nbrRecov1 = nbrRecov.addBands(postFireIndices3)
  nbrRecov2 = nbrRecov1.addBands(postFireIndices4)
  nbrRecov3 = nbrRecov2.addBands(postFireIndices5)
  nbrRecov4 = nbrRecov3.addBands(postFireIndices6)
  nbrRecov5 = nbrRecov4.addBands(postFireIndices7)
  nbrRecov6 = nbrRecov5.addBands(postFireIndices8)
  nbrRecov7 = nbrRecov6.addBands(postFireIndices9)
  nbrRecov8 = nbrRecov7.addBands(postFireIndices10)
  nbrRecov9 = nbrRecov8.addBands(preFireIndices)
