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
