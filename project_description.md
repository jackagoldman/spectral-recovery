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
7) Downscale climate data using krigr? - downscale using gcm


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
QC_63_1987
QC_64_1991
QC_65_1990
QC_757_1996 = good example of overlap 
QC_783_1996 = overlap good example
QC_788_1996
QC_792_1996 = small area
QC_81_1991 = small area
QC_96_1991
COC16_1997_1038
DRY27_1996_1121
IGN9_1987_492
NIP136_1995_1299
NIP20_2005_1521
NIP51_1996_620
NIP9_1992_1122 



Bad
SAU4_1998_335
SLK60_1996_884 - very small defolaited portion
QC_103_1988 - all defoliated
QC_122_1988 - weird, good example of inaccuracies of nbac
QC_1445_1995
QC_508_1996 = good inaccuracies example
QC_547_2010 = small
QC_739_1996
QC_745_1996 = weird
QC_750_1996 = weak overlap -> could be low severity
FOR13_1987_316 = weak overlap good example -> could be low severity

Maybe - unsure
THU37_2007_1662 - weird scale
QC_1234_1995 - weird shapes
QC_319_1986 - inaccurate
QC_444_1991 - inaccurate
QC_480_1996 = small defoliated area
QC_59_1986 = were areas
QC_728_1996 - poor coverage over non defoliated area, good example
FOR13_1987_316 = weak overlap good example = could be low severity
NIP230_1998_821 = small area
NIP44_2000_29  = small area but over 2500 pixels for one half, 71000 for other.-> poor overlap defoliated
NIP56_1998_832 = under 1000 pixels.


