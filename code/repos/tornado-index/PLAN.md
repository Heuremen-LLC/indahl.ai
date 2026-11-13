# TORNADO: stated tornado probabilities and warning goals against the tornadoes that happened. Plan, written before any stated figure was set beside a tornado.

## Claims read
Stated figure one. The NOAA Storm Prediction Center (SPC) Day 1 Convective Outlook draws tornado probability contours at 2, 5, 10, 15, 30, 45 and 60 percent and a hatched area. The SPC page on its products (https://www.spc.noaa.gov/misc/about.html) says: "The probabilities that you see on the graphics represent the probability of one or more events occurring" "within 25 miles of a point during the outlook period." It defines a significant severe storm as including "A tornado that produces EF2 or greater damage." The hatched area is the area SPC gives a 10 percent or greater chance of a significant tornado within 25 miles of a point. The same page says: "Each Day 1 Convective Outlook is valid from the start of issuance" "(except for the 0600 UTC issuance which begins at 1200 UTC that day)" "through 1200 UTC the following day".

The SPC's own verification paper (Kay and Brooks, "Verification of Probabilistic Severe Storm Forecasts at the SPC", https://spc.noaa.gov/publications/mkay/probver) bins storm reports onto a grid covering the United States with "80 km nominal grid spacing", defines the probabilities as "probabilities of 1 or more events occurring within 25 miles of a point", matches reports to each outlook over the outlook's valid period, uses the 1300 UTC outlook, and reads the result as a reliability diagram ("the probability of an event occurring given that it was forecast"). Herman, Nielsen and Schumacher (2018, Weather and Forecasting 33, 161) grid the outlooks "on an 80-km-spaced grid without interpolation" and add the Brier skill score against climatology. This plan follows that method.

Stated figure two. The National Weather Service (NWS) reports three tornado warning measures each fiscal year under the Government Performance and Results Act (GPRA). The Department of Commerce Office of Inspector General report OIG-25-026-I (2025), Box 1, "GPRA Metrics Definitions Since October 1, 2007", states them:
- Probability of detection: "A warned tornado segment is one that occurs within the bounds of a warning area during the valid time of the alert. The Percentage of the Event Warned (PEW) is the proportion of warned segments for a given tornado event. The official POD metric is the mean PEW for all tornadoes occurring nationwide in a given year. The current GPRA goal is greater than or equal to 72%."
- Lead time: "Lead time is computed for every 1-minute segment of the tornado track. The lead time of each warned segment is the difference between the warning's time of issuance and the timing of the segment. Each unwarned tornado segment is assigned a zero. The lead time reported for each tornado is the average over all its tornado segments. The official lead-time metric is the yearly national average of this measure. The current GPRA goal is greater than or equal to 13 minutes."
- False alarm ratio: "A warning followed by a tornado is considered verified. The FAR is the proportion of unverified warnings, or false alarms, over all warnings issued in a year. The current GPRA goal is less than or equal to 71%."
The same report (Finding III) says the public definition of lead time differs from the one computed. The computed one (segment average) is the primary reading here. The initial lead time (first segment) is shown beside it and decides nothing.
The goals are the goals the report calls current. Each fiscal year is read against them. The goal printed for each earlier year in each budget was not read for this plan, and the page says so.

## Questions
1. Where SPC drew a tornado probability band, how often did a tornado pass within 25 miles of a point in it?
2. Do NWS tornado warnings meet the stated GPRA goals when they are counted against the SPC tornado database?

## Data (all public, keyless)
Stated side, outlooks. The archive of SPC Day 1 Convective Outlooks kept by the Iowa Environmental Mesonet (IEM) at Iowa State University, as shapefiles by year (https://mesonet.agron.iastate.edu/cgi-bin/request/gis/outlooks.py, d=1, type=C, geom=geom_layers). Each polygon carries ISSUE, EXPIRE, product issue time, THRESHOLD, CATEGORY and CYCLE. The SPC archive (https://www.spc.noaa.gov/products/outlook/archive/) holds the same products. A known-good check reads stated values against IEM's outlook-by-point service, which is a separate code path.
Stated side, warnings. IEM's archive of NWS storm-based tornado warnings (https://mesonet.agron.iastate.edu/api/1/vtec/sbw_interval.geojson, ph=TO, issuance polygons only), with issue and expire times.
Delivered side, closed years. The SPC tornado database file 1950-2025_actual_tornadoes.csv (https://www.spc.noaa.gov/wcm/data/, last update 24 April 2026), one row per tornado track ("Single tracks. No state segments"), with start date and time, end date and time, start and end latitude and longitude, and rating. The time zone field 3 is Central Standard Time, read as UTC minus 6 hours.
Delivered side, recent window. SPC preliminary storm reports, one file per convective day (https://www.spc.noaa.gov/climo/reports/YYMMDD_rpts_filtered_torn.csv), times in UTC, the day running 1200 UTC to 1159 UTC. These are preliminary. Every reading that uses them is labelled preliminary and is never pooled with a closed-year reading.
Boundaries. US Census cartographic boundary file of states, 2024, 1:20,000,000 (cb_2024_us_state_20m).
Terms. NOAA data are public domain. IEM: "The materials found on this website are in the public domain and may be used freely by anyone for any lawful purpose." IEM asks for attribution, which the page gives. Census boundary files are public domain. Requests are made one at a time with pauses, with a user agent that names this desk.

## Frame (fixed now)
- Issuance scored: the 1300 UTC Day 1 Convective Outlook (IEM CYCLE 13, the canonical outlook of that cycle). Valid from 1300 UTC on its date to 1200 UTC the next day. No other issuance is scored.
- Closed years: outlooks dated 1 January 2007 to 31 December 2025, delivered side the database file. 2007 is the first full year after SPC moved to the current tornado levels, read from the stated side only before this plan.
- Recent window: outlooks dated 1 January 2026 onward, up to the last convective day that ended at least 36 hours before the run. Delivered side the preliminary reports. Labelled preliminary.
- Grid: points 80 km apart on an Albers equal-area projection of a sphere of radius 6371.0088 km (standard parallels 29.5 and 45.5 degrees north, origin 23 degrees north, 96 degrees west), kept where the point falls inside one of the 48 contiguous states or the District of Columbia.
- Stated value at a point: the highest tornado threshold among 0.02, 0.05, 0.10, 0.15, 0.30, 0.45, 0.60 whose polygon holds the point (rings read by even-odd parity, so a hole is outside). No contour means "under 2 percent". No interpolation between contours.
- Stated band: a point inside the L contour and outside the next higher one has a stated chance from L up to the next level. Bands: under 2 percent [0, 0.02), [0.02, 0.05), [0.05, 0.10), [0.10, 0.15), [0.15, 0.30), [0.30, 0.45), [0.45, 0.60), [0.60, 1]. A threshold outside this set is counted and its layer is not used.
- Hatched: a point inside a TORNADO polygon with threshold SIGN. Stated band [0.10, 1] for an EF2 or stronger tornado (database rating 2 or more).
- Event at a point: a tornado whose start time falls in the valid period passes within 25 statute miles (40.234 km) of the point. A track is the straight segment from the start point to the end point, or the start point alone when the end point is missing or zero. Distance is measured on the projection. A preliminary report is a point.
- One count per point and day. A point-day is one row.

## Rules (fixed now)
Band reading. For each cell and band: rows, days with at least one row, events, and the observed frequency (events over rows). Interval: 95 percent percentile interval from a day-level block bootstrap, 2,000 resamples of the days in the cell with replacement, every row of a drawn day kept together, fixed seed 20261110. Grid points on one day share the same storms and neighbouring days share weather systems. The day block keeps the first together. The page says the second is not covered.
- ABOVE: the whole interval is above the top of the band (tornadoes came more often than stated).
- BELOW: the whole interval is below the bottom of the band.
- CONSISTENT: the whole interval is inside the band.
- CANNOT_TELL: otherwise, or fewer than 30 days with a row in the band.
Hatched reading: the same rule against [0.10, 1] with EF2 or stronger events.

Brier, the second ruler. Stated value per row is the contour level (0 under 2 percent). Reference: climatology, the observed frequency at the same grid point in the same calendar month over the closed years with the scored year left out (all closed years for the recent window). Brier skill score = 1 minus (Brier of the outlook over Brier of climatology), over all rows of the cell, with the same day-block bootstrap interval. SPC states no Brier figure. Reading: ABOVE (better than climatology) if the whole interval is above 0, BELOW if the whole interval is below 0, CANNOT_TELL otherwise. CONSISTENT is not used for this ruler.

Cells, defined now:
- United States, closed years (48 states and DC).
- Kansas, closed years: grid points inside Kansas.
- Tornado Alley, closed years: grid points inside Texas, Oklahoma, Kansas, Nebraska, South Dakota or Iowa. There is no official boundary. This one is ours and fixed now.
- The same three cells for the recent window, labelled preliminary.
- Each closed year for the United States, shown as a table and not in the headline.

Headline (fixed now): the United States closed-years table, how many of the eight bands read each outcome, the 10 to 15 percent band's observed frequency with its interval, and the Kansas cell beside it.

Warnings. Fiscal years run 1 October to 30 September.
- Closed fiscal years: FY2008 to FY2025, delivered side the database file.
- Recent window: FY2026 to date, the database file for October to December 2025 and the preliminary reports from 1 January 2026, labelled preliminary.
- Segments. A tornado runs from its start time to its end time. It is cut into 1-minute segments, one at each whole minute from the start up to the end. A tornado with no end time, or an end before the start, is one segment at the start. The position of a segment is linear in time along the straight track. A preliminary report is one segment.
- Warned segment: inside the issuance polygon of any tornado warning with issue time at or before the segment time and expire time after it. Segment lead time: segment time minus the issue time of the earliest such warning, in minutes. Unwarned: zero.
- PEW per tornado, POD = mean PEW over the tornadoes of the fiscal year. Lead per tornado = mean over its segments, yearly lead = mean over tornadoes. Initial lead = lead of the first segment, shown only.
- A warning is verified if any segment of any tornado lies inside its polygon between its issue and expire times. FAR = unverified warnings over all warnings issued in the fiscal year.
- All tornadoes and warnings in the files are used, any state or territory, no WFO match.
- Interval: day-level block bootstrap as above, the day being the convective day 1200 UTC to 1200 UTC, tornadoes by start time and warnings by issue time.
- POD against at least 0.72 and lead against at least 13 minutes: CONSISTENT if the whole interval is at or above the goal, BELOW if the whole interval is under it, CANNOT_TELL otherwise. FAR against at most 0.71: CONSISTENT if the whole interval is at or under it, ABOVE if the whole interval is over it, CANNOT_TELL otherwise. Read for each fiscal year and for all closed fiscal years pooled.

## Nothing returned, counted apart and never folded
- A day in the frame with no 1300 UTC Day 1 outlook in the archive: NOTHING_RETURNED, the day is out of every cell, listed.
- A day whose tornado layer cannot be read: NOTHING_RETURNED, listed.
- A recent-window day whose preliminary file cannot be fetched: NOTHING_RETURNED, listed.
- A tornado without a start position or start time: counted, not placed.
- A fiscal year whose warning file cannot be fetched: NOTHING_RETURNED for that year.
- A threshold outside the stated set: counted.

## Both alternatives
A. The observed frequency in each band sits inside the band, warnings meet the goals. Cells read CONSISTENT or CANNOT_TELL.
B. Tornadoes came more or less often than the band stated, warnings miss a goal. Cells read ABOVE or BELOW.
Either result is printed the same way. No cause is named for any reading.

## Known-good gates (a failed gate turns every outcome into CANNOT_TELL and keeps the original)
1. Format. The outlook files carry ISSUE, EXPIRE, THRESHOLD, CATEGORY, CYCLE. The database header holds slat, slon, elat, elon, date, time, tz, edat, etime, mag. Every time zone field is 3, or the other rows are counted and dropped. Warning features carry utc_issue, utc_expire and a polygon.
2. Stated reader. For 30 point-days drawn with a fixed seed from the stated side (closed years, outlooks with a tornado contour), the band from our reader equals the tornado threshold IEM's outlook-by-point service returns for that point at one minute after the outlook's product issue time. At least 29 of 30 must agree (one allowed for a corrected outlook issued in the same minute).
3. Distance and time. Planted tracks at 39.9 km and 40.6 km from a point read event and no event. A tornado starting 1259 UTC is out of the day and one at 1300 UTC is in. The CST to UTC conversion of one database row read in raw text is written into CHECKS.md.
4. Warnings. Planted cases: a tornado inside a warning issued 10 minutes earlier for its whole life (PEW 1, lead 10 plus the mean minute offset), a tornado outside every warning (PEW 0, lead 0), a warning with no tornado (false alarm), a tornado that leaves the polygon halfway (PEW one half).
5. Rule. Synthetic band and goal readings come out ABOVE, BELOW, CONSISTENT and CANNOT_TELL as planted. heuremen_kit's self-test passes.

## Set aside
- The other Day 1 issuances (0600, 1630, 2000 and 0100 UTC), the Day 2 and Day 3 outlooks, and the hail, wind and categorical outlooks.
- Tornado watches.
- Outlooks before 2007.
- Alaska, Hawaii and Puerto Rico in the outlook grid (SPC outlooks cover the contiguous states). They stay in the warning reading.
- The per-year GPRA goal printed in each budget.
- Any cause of any reading.

## Reading done before this plan was written
- The tornado threshold sets of sampled 1300 UTC outlooks from 2003 to 2024, read from the stated side to fix the frame start. The field names of one outlook year file (2024).
- The header row and the end-time fill counts by year of the database file, to see that end times exist. No tornado was placed beside any outlook or warning.
- The field names of one warning record (2024).
- The SPC product page, the Kay and Brooks paper page, the Herman and others abstract, the OIG report's Box 1, Finding III and Appendix B text, the IEM disclaimer, the SPC data page.
No stated figure was set beside a tornado.
