# CONE: the National Hurricane Center's stated track forecast cone against where storms went. Plan, written before any forecast position was set beside a best-track position.

## Claim read
The National Hurricane Center (NHC) publishes a track forecast cone with each forecast. Two NHC pages state how often the storm centre should stay inside it.

The cone definition page (https://www.nhc.noaa.gov/aboutcone.shtml, fetched 10 Nov 2026) says: "The cone represents the probable track of the center of a tropical cyclone, and is formed by enclosing the area swept out by a set of circles (not shown) along the forecast track (at 12, 24, 36, 48, 60, 72, 96, 120 hours). The size of each circle is set so that two-thirds of historical official forecast errors over a 5-year sample fall within the circle." It gives a table of circle radii in nautical miles for the year, for the Atlantic basin and for the Eastern and Central North Pacific basins, "based on error statistics from" the previous five years.

The cone graphic page served with each forecast (for example https://www.nhc.noaa.gov/refresh/graphics_at2+shtml/023630.shtml?cone, fetched 10 Nov 2026) says: "Historical data indicate that the entire 5-day path of the center of the tropical cyclone will remain within the cone about 60-70% of the time. To form the cone, a set of imaginary circles are placed along the forecast track at the 12, 24, 36, 48, 72, 96, and 120 h positions, where the size of each circle is set so that it encloses 67% of the previous five years official forecast errors. The cone is then formed by smoothly connecting the area swept out by the set of circles."

NHC's verification procedures page (https://www.nhc.noaa.gov/verification/verify2.shtml) says: "Track forecast error is defined as the great-circle distance between a cyclone's forecast position and the best track position at the forecast verification time." And: "Current practice is to include a forecast in the verification only if the system was a tropical or subtropical cyclone at both the forecast and the verifying time; all other stages of development (e.g., extratropical, tropical wave, remnant low) are excluded."

Questions:
1. Whole path (headline). For each forecast, did the best-track centre stay inside that forecast's cone for the whole five days? NHC states about 60 to 70 percent.
2. Circles. At each of 12, 24, 36, 48, 72, 96 and 120 hours, how often was the best-track position inside the circle of that year's radius around the forecast position? NHC states two-thirds.
3. Second ruler. NHC's yearly tables of average official track errors, against our own recount from the same public files.

## Data
Stated side.
- Official forecasts: the ATCF a-deck files, OFCL records only (https://ftp.nhc.noaa.gov/atcf/archive/YYYY/aalNNYYYY.dat.gz and aepNNYYYY.dat.gz, and for the current season https://ftp.nhc.noaa.gov/atcf/aid_public/). Storm numbers 01 to 89 (invests 90 to 99 are not storms). One forecast is one storm and one initial time (the a-deck date-time group, 00, 06, 12 or 18 UTC). Positions are read at tau 0, 12, 24, 36, 48, 72, 96 and 120 hours. The a-deck repeats a position on several lines (one per wind radius). When two OFCL records for the same storm, initial time and tau give different positions, the first in the file is used and the count of such cases is printed.
- Cone radii: the table on the NHC cone page for each year. Past years are read from Internet Archive copies of https://www.nhc.noaa.gov/aboutcone.shtml, current year from the live page. A year uses the table that names that year ("cones in YYYY"). When copies naming the same year disagree, the earliest copy that names it is used and the disagreement is listed (one case at plan time: a copy of 31 March 2020 still says 2019 over the 2020 values). A year with no copy naming it is not scored and is listed. At plan time that is 2012: the three archived copies made in 2012 (May to August) still name 2011. The radii and the copy each came from are written to data/radii.json before any comparison.
- NHC's stated average track errors: https://www.nhc.noaa.gov/verification/pdfs/1989-present_OFCL_ATL_annual_trk_errors.pdf and 1989-present_OFCL_EPAC_annual_trk_errors.pdf (error in n mi and number of cases, by year and lead).

Delivered side.
- Complete seasons: HURDAT2, NHC's post-season best track (https://www.nhc.noaa.gov/data/hurdat/, Atlantic hurdat2-1851-2025-092326.txt and Northeast and North Central Pacific hurdat2-nepac-1949-2025-092926.txt, the newest files at plan time). A newer HURDAT2 file replaces these when NHC posts one, and the run records which file it read.
- The current season (2026 at plan time): the operational ATCF b-decks (https://ftp.nhc.noaa.gov/atcf/btk/), which are not yet post-season best tracks. 2026 is shown in its own cell and is not in the headline cells. A season moves into the headline cells on the first run after a HURDAT2 file holding it is posted.
- Only synoptic best-track records (00, 06, 12, 18 UTC) are used. Landfall and other special records at other times are not.

All sources are public domain (NOAA) and need no key. One request at a time, paced, with a user agent that names this desk. Every file read is kept in data/raw.

## Frame (fixed now)
- Basins: Atlantic (aal files, storm IDs AL) and East Pacific (aep files, storm IDs EP), counted apart and never pooled. In the East Pacific a forecast counts only if its tau 0 position is east of 140 W (NHC's area of responsibility). Central Pacific storms and forecasts west of 140 W are set aside.
- Seasons: 2010 to 2025 in the headline cells (post-season best track), less any season without a radii table (2012 at plan time). 2026 in its own cell.
- A forecast enters the frame only if its storm has a best track and the best track at the initial time is a tropical or subtropical cyclone (status TD, TS, HU, SD or SS). Forecasts outside this rule are counted by reason and not scored: no best track for this storm (for example a potential tropical cyclone that never formed), no best-track point at the initial time, not a tropical or subtropical cyclone at the initial time.
- Positions are compared at the precision NHC serves (tenths of a degree). No tolerance is added. Distance is great-circle distance on a sphere of radius 3440.065 n mi.

## Rules (fixed now)
Circle row. One row is one forecast and one lead (12, 24, 36, 48, 72, 96 or 120 h) where the forecast states a position.
- INSIDE: the great-circle distance from the forecast position to the best-track position at the verifying time is less than or equal to that year's circle radius for the basin and lead.
- OUTSIDE: the distance is greater.
- NOTHING_RETURNED, each reason counted apart and never folded into either side: no best-track point at the verifying time (the track had ended), or the best-track point is not a tropical or subtropical cyclone at the verifying time (extratropical, remnant low, wave, disturbance). NHC's own verification leaves both out.
- CANNOT_TELL: a position does not parse.
- A lead the forecast does not carry is not a row. The count of forecasts without each lead is printed.

Whole-path row. One row is one forecast that carries all seven leads.
- The forecast's cone is the union of the convex hulls of each pair of consecutive circles along the forecast track: the tau 0 position as a circle of radius 0, then the circles at 12, 24, 36, 48, 72, 96 and 120 h with that year's radii. This follows the graphic page's "set of imaginary circles ... at the 12, 24, 36, 48, 72, 96, and 120 h positions" and "the area swept out by the set of circles". The tau 0 point is our reading of where the cone starts. The hull of two circles is computed in an azimuthal equidistant projection centred on the best-track point being tested.
- INSIDE: every synoptic best-track point from 12 h to 120 h after the initial time (19 points, 6 hours apart) lies in the cone. Timing is not checked, as the graphic page's "entire 5-day path" wording is about the path. The path between synoptic points is not interpolated.
- OUTSIDE: at least one of those points lies outside the cone.
- NOTHING_RETURNED: at least one of those 19 times has no best-track point or a point that is not a tropical or subtropical cyclone. Counted apart, never folded.
- Forecasts that do not carry all seven leads are counted apart as "forecast shorter than five days" and are not rows.

Cells. A cell is all rows of one basin and one lead (circle cells, 14 of them), or all whole-path rows of one basin (whole-path cells, 2), over the seasons 2010 to 2025. The share is INSIDE over INSIDE plus OUTSIDE. NOTHING_RETURNED and CANNOT_TELL rows are printed beside every cell and never enter the share.

Intervals. Forecasts of one storm are correlated: consecutive forecasts share most of their track and their errors. The interval is a storm-level block bootstrap: storms in the cell are resampled with replacement, all of each drawn storm's rows come with it, and the share is recomputed. 2,000 resamples, seed 20261110, the 2.5th and 97.5th percentiles. The page says so. A cell with fewer than 10 storms or fewer than 30 scored rows reads CANNOT_TELL.

Cell outcomes.
- Whole-path cells, against NHC's stated "about 60-70%": CONSISTENT if the whole interval lies inside 60 to 70 percent. ABOVE if the lower bound is above 70 percent. BELOW if the upper bound is below 60 percent. Otherwise CANNOT_TELL.
- Circle cells, against NHC's stated two-thirds: reading "two-thirds" as 61.7 to 71.7 percent (two-thirds plus or minus 5 points) is our reading and is named as ours wherever it is printed. CONSISTENT if the whole interval lies inside that band. ABOVE if the lower bound is above 71.7 percent. BELOW if the upper bound is below 61.7 percent. Otherwise CANNOT_TELL.
- Each season is also read on its own with the same rules (by basin, lead and whole path), shown as a table and not in the headline. The 2026 cell uses the same rules on the operational b-decks.

Headline (fixed now): the Atlantic whole-path cell, 2010 to 2025. The headline line also gives the East Pacific whole-path cell, how the 14 circle cells read, and how the second ruler reads.

Second ruler: NHC's stated average track errors.
- One row is one basin, one season (2010 to the last season the PDF table holds) and one lead (12, 24, 36, 48, 72, 96, 120 h).
- Our recount: the mean great-circle distance in n mi over forecast positions in the frame whose best-track point at the verifying time is a tropical or subtropical cyclone (forecast and verifying time both, as NHC's procedure says), and the number of such positions. These are the circle rows that read INSIDE or OUTSIDE. A season without a radii table is still recounted here, since this ruler needs no radii.
- CONSISTENT if our mean is within the larger of 1.0 n mi and 2 percent of NHC's stated mean. ABOVE if ours is higher by more than that. BELOW if lower by more than that. CANNOT_TELL if our case count differs from NHC's by more than the larger of 2 cases and 5 percent (the samples differ), or if the stated value is missing. The tolerance band is the interval printed with each row. Our storm-bootstrap 95 percent interval of the mean is printed beside it as a description.
- NHC's tables say they are homogeneous with the best-track CLIPER5 and Decay-SHIFOR5 baselines, so small case-count differences are expected. The case-count rule decides which rows are compared at all.

Described and not scored: the median distance by lead, the share of circle rows within 4 n mi of the circle edge (the size of position rounding), the count of duplicate OFCL records with different positions, and the forecasts the frame set aside by reason.

## Both alternatives
A. The cone holds the best-track path about as often as NHC states. The whole-path cells read CONSISTENT, the circle cells read CONSISTENT, or CANNOT_TELL near the band.
B. It holds the path more often (ABOVE) or less often (BELOW) than stated.
Either result is printed the same way. An ABOVE or BELOW cell says how often the path left the cone. It names no cause.

## Known-good gates (a failed gate turns every outcome into CANNOT_TELL and keeps the original)
1. Format. Every a-deck line used has at least 11 comma-separated fields, tech OFCL, latitude ending N or S and longitude ending E or W in tenths. HURDAT2 header and data lines parse with the documented layout (status in field 4). Radii tables parse with seven leads for both basins in every scored year.
2. Reader. Three OFCL positions and three best-track positions, read directly from raw text by a separate regular expression, equal the parsed values. The rows are written to CHECKS.md.
3. Join. At tau 0, the OFCL position against the best-track position at the initial time: the median distance over all frame forecasts is under 15 n mi (NHC's tables state 0 h errors near 10 n mi). A join that pairs the wrong storm or time fails this.
4. Rule. Synthetic rows with a known answer read INSIDE, OUTSIDE, each NOTHING_RETURNED reason and CANNOT_TELL correctly, a synthetic path inside and outside a synthetic cone reads correctly, the bootstrap on a synthetic one-storm-per-row sample gives an interval close to Wilson's, and heuremen_kit's self-test passes.

## Set aside
- The cone's day 1 to 3 and day 4 to 5 split (solid and stippled) as separate claims.
- Wind-field size, watches and warnings, intensity forecasts.
- Central Pacific (CPHC) forecasts and storms, and forecasts west of 140 W.
- Special advisories as a separate set (a-deck records carry no flag, so the first record per initial time and lead is used).
- Forecasts issued while the system was not a tropical or subtropical cyclone in the best track (potential tropical cyclones and post-tropical stages).
- Seasons before 2010.

## Reading done before this plan was written
- The NHC cone page (live) and its 123 Internet Archive copies, parsed for the radii tables and the year each names. These are stated values only. Tables naming 2010, 2011 and 2013 to 2026 were found. data/radii.json is committed with this plan.
- One NHC cone graphic page and the verification procedures and official error trends pages.
- Both NHC annual track error PDFs in full (stated values, 1989 to 2025, "Verification based on NHC best track database as of 5/12/26"), parsed to data/stated_errors.json, committed with this plan.
- The a-deck archive listings and the HURDAT2 directory listing. The a-deck files for 2010 to 2025 and the two HURDAT2 files were downloaded to data/raw and not parsed.
No forecast position was set beside a best-track position.

## Terms recorded
- NOAA/NHC data are works of the US government and in the public domain. NHC asks for credit to NOAA/NHC as the source. Pages say so.
- Internet Archive: copies read through the public Wayback index and raw-copy addresses, paced.
