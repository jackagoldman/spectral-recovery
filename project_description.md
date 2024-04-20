# Project Description

**Characterizing the impacts of spruce budworm and wildfire interactions with spectral-temporal patterns of post-fire forest recovery using Landsat time series**.

## Background

## Questions

1)  How do forest recovery rates vary over time in defoliated vs non-defoliated areas?
2)  What is the relationship between recovery, defoliation, climate, and burn severity?
3)  Does the magnitude and duration of nbr spectral-temporal trajectories vary in defolaited vs. non-defoliated areas?
4)  Does burn severity vary between defoliated and non-defolaited areas?
5) 

## Steps

1)  identified fires that contained both defolaited and non-defoliated areas - DONE
2)  Split fires into two sections: defolaited - non-defoliated -- DONE
3)  Used the Landtrendr algorithm in gee to extract spectral-temporal trajectories for pixels in fire perimeter based on NBR -- DONE
4)  Extracted fitted NBR values for each fire, as ell as Tesselated cap brightness, wetness, greeness, and angle -- DONE
5)  Using NBR we calculated the magnitude and duration of change for each fire. We calculated the % recovery as the distance between nbr10 and yof dividied by the distance between prefire and yof, multiplied by 100. original methods by Bright et al 2019
6)  We calculated rbr_w_offset as the difference between ((pre - post) - offset)/pre -> offset values were extract in GEE using the original code and just extracting the offset values ith codes for each fire
7) Downscale climate data using krigr


## fire notes
Good fires
Red 7
SLK11_2007_1658	
TER7_1986_83 - double check 
THU130_1991_1263
THU36_1996_1313 - small area
QC_1017_1995
THU74_1996_1129
QC_101_1990
QC_107_1988
QC_1191_1995
QC_1218_1995
QC_1248_1995
QC_1432_1995 = small area
QC_1442_1995
QC_1824_2010
QC_33_1986
QC_377_1997
QC_533_1996


Bad
SAU4_1998_335
SLK60_1996_884 - very small defolaited portion
QC_103_1988 - all defoliated
QC_122_1988 - weird, good example of inaccuracies of nbac
QC_1445_1995
QC_508_1996 = good inaccuracies example

Maybe - unsure
THU37_2007_1662 - weird scale
QC_1234_1995 - weird shapes
QC_319_1986 - inaccurate
QC_444_1991 - inaccurate
QC_480_1996 = small defoliated area

