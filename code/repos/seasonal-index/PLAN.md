# SEASONAL: stated seasonal outlook chances against the observed tercile. Plan, written before any stated chance was set beside an observed category.

## Claim read
Each month the NOAA Climate Prediction Center (CPC) issues 3-month outlooks for temperature and precipitation over the United States. Each outlook states, for each place, the chance that the 3-month mean falls in the upper third (above normal), the middle third (near normal) or the lower third (below normal) of the climate record. Where no category is favoured the outlook says equal chances, 33.33 percent each.

CPC keeps an archive of its outlooks at the 0.5-month lead on a 2 by 2 degree grid over the contiguous United States (130W to 60W, 20N to 56N), with the observed category for each cell and season, in the files it uses for its own verification (cpc.ncep.noaa.gov/products/predictions/long_range/tools/briefing/verification/). It publishes a Heidke skill score for every season in temp01.heidke.txt and prec01.heidke.txt, with the definition "HSS (%) = 100 * (H - E) / (T - E) where H = Number of correct forecasts, E = Expected number of correct forecasts (1/3 of total), and T = Total number of valid forecast-observation pairs" and "HSS withEC (%) = HSS * coverage" (products/verification/summary/index.php?page=tutorial).

Questions: when CPC states a chance for a category, does that category happen about as often as stated? And does our recompute of CPC's Heidke skill score from CPC's own archive give the scores CPC states?

The unit is CPC's grid cell, not the climate division. CPC archives both the outlook and the observed category on this grid, and its own scores are computed on it. No division-level archive of past outlooks with observed categories was found.

## Data
All from the CPC verification directory, read without a key, at most once a day:
- temp01_forecast_above.bi, temp01_forecast_below.bi, prec01_forecast_above.bi, prec01_forecast_below.bi: stated chance of above and below normal in percent. Near normal is 100 minus the two.
- temp01_forecast.bi, prec01_forecast.bi: CPC's category (1 below, 2 near, 3 above, 0 equal chances).
- temp_seas_verif.bi, prec_seas_verif.bi: observed category (-1 below, 0 near, 1 above, -9999 missing).
- temp01.heidke.txt, prec01.heidke.txt: CPC's stated scores per season (first target month, Non-EC, All, Coverage).
Format, as CPC's about files state and the file sizes give: little-endian 4-byte floats, 684 values per record (36 longitudes by 19 latitudes, west to east, then south to north), one record per season. Forecast record i was issued in December 1994 plus i months and is valid for the 3 months starting January 1995 plus i months. Observed record i is the season starting January 1995 plus i months.
NOAA/NWS information is in the public domain (weather.gov/disclaimer). It is credited and not presented as NWS material.

## Frame (fixed now)
- Cells: every grid cell with an observed category (not -9999) in the season. No cell is picked by us.
- Seasons: every forecast record with a matching observed record. Forecast records without one read NOTHING_RETURNED, counted apart.
- Variables: temperature and precipitation, always read apart.
- One row is one season, one cell, one variable and one category (above, near, below), with the stated chance for that category and whether that category was observed.

## Rules (fixed now)
Reliability. Stated chances are put in bins (percent): under 25, 25 to under 31, 31 to under 36 (around equal chances), 36 to under 40, 40 to under 50, 50 to under 60, 60 and over. A row whose stated chances are missing, negative, or do not leave a near-normal chance between 0 and 100 reads CANNOT_TELL, reason unreadable.
For each variable, category and bin: the mean stated chance, the rows, and the observed frequency of the category. A cell's outcome:
- CANNOT_TELL if fewer than 30 rows or fewer than 24 distinct seasons.
- ABOVE if the interval's lower bound is over the mean stated chance (the category happened more often than stated).
- BELOW if the upper bound is under the mean stated chance.
- CONSISTENT if the mean stated chance is inside an interval no wider than 0.10.
- Otherwise CANNOT_TELL.
A further cell per variable, "leaning": every row of any category stated at 40 percent or more. The headline cell is temperature, leaning.

Interval. Rows are not independent: every cell in a season shares one weather pattern, and neighbouring seasons share two of their three months. The interval is a moving-block bootstrap over seasons: the seasons are sorted, blocks are 12 consecutive seasons, a replicate draws ceil(S/12) block starts with replacement, and every row of a drawn season enters with that multiplicity. 2,000 replicates, seed 20261110, 2.5th and 97.5th percentiles of the replicate frequencies. The page says so.

Heidke recompute (second ruler). For each season and variable, over the cells with an observed category: CPC's category from the categorical file, read only where it is exactly 0, 1, 2 or 3 (other values are counted and left out). T is the number of cells with category 1, 2 or 3. H is the number of those where the category matches the observed one. E is T/3. Non-EC score = 100 (H - E) / (T - E). Coverage = 100 T over the cells with an observed category. All score = non-EC score times coverage / 100. Cells are not weighted by area (CPC states no weighting). A cosine-of-latitude weighted score is shown beside it, described and not scored.
Against CPC's stated score for the same season: the difference ours minus CPC's, per season, and its mean over seasons with the same block bootstrap. Outcome per variable and score: CONSISTENT if the interval of the mean difference lies inside -2 to +2 points, ABOVE if its lower bound is over +2, BELOW if its upper bound is under -2, otherwise CANNOT_TELL. The share of seasons within 1 point is printed.

## Both alternatives
A. Categories happen about as often as stated, and our recompute gives CPC's scores. Cells read CONSISTENT.
B. Categories happen more or less often than stated (ABOVE or BELOW), or our recompute differs from CPC's scores.
Either result is printed the same way, with no cause named.

## Known-good gates (a failed gate turns every outcome into CANNOT_TELL)
1. Format. Each file is a whole number of 684-value records. The forecast files have at least as many records as the observed files. The observed values are only -1, 0, 1 and -9999.
2. Orientation. The cells with an observed category form one land mask that is the same in every season, and the cell at 82W 28N (Florida) is in it while the cells at 128W 22N (Pacific) and 62W 54N (Atlantic) are not.
3. Record alignment. The number of rows in each heidke file equals the number of observed records, and the first target month is January 1995.
4. Rule. Synthetic rows read ABOVE, BELOW, CONSISTENT and CANNOT_TELL correctly, the Heidke formula gives 100 for a perfect season, 0 for one with a third correct and the stated value for a planted case, planted reliable and unreliable worlds read CONSISTENT and BELOW in the bootstrap rule, and heuremen_kit's self-test passes.

## Described and not scored
Shares by bin of how often the near-normal category was observed. The area-weighted Heidke score. Seasons by start month.

## Set aside
Leads beyond 0.5 month (only in shapefile contours from 2007). Monthly outlooks. Alaska and Hawaii (not on the grid). Climate divisions. The normals period behind the observed terciles is not stated in the files and is not read here.

## Reading done before this plan was written
An outside scout read the CPC verification pages, the about files, the shapefile archive listing and the HSS tutorial, and checked file sizes, missing flags and the value sets of the categorical and observed files. We then read the land mask of the first observed record and the first forecast record, the value ranges of the stated chances and the categorical file over land cells (share of whole-number categories, share of equal chances, the near-normal range), and the first and last rows of temp01.heidke.txt. No stated chance or category was set beside an observed category.
