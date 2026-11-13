# Referee report: TORNADO desk (SPC Day 1 tornado probabilities and NWS GPRA warning goals against the SPC tornado database)

Referee: read-only refuting pass, 10 November 2026. Nothing in `tornado_index/` was edited. Inputs read: PLAN.md (commit 447599c), git log, data/plan_seal.json, tornado_tick.py, shpread.py, build_page.py, lint_copy.py, tornado_headline.py, summary_tornado.json, tornado.html, the raw outlook zips, database CSV, prelim CSVs, warning geojsons and state boundaries. Primary sources fetched 10 Nov 2026 with user agent heuremen-tornado-referee/0.1: spc.noaa.gov/misc/about.html, spc.noaa.gov/publications/mkay/probver, OIG-25-026-I (text via pymupdf), NWS SCN 26-11 (search result only).

Referee code (own shapefile/dbf reader, own spherical Albers, own ray-casting even-odd, own segment distance, own warning segment logic, own bootstrap with seed 987654): `code/rshp.py rgeo.py rgrid.py rasterize.py recount.py rwarn.py analysis.py` (+ endbug.py, edgetest.py diagnostics). Outputs: `out/recount.json`, `out/diff_vs_desk.json`, `out/analysis.json`.

Seal check: plan commit 447599c at 2026-11-10T09:27:46-05:00 (14:27Z), first_comparison 14:33:12Z, later than the commit by 6 minutes. PLAN.md is unchanged since (git status shows only build_page.py modified). Sealed.

## Verdict

**FIX THEN SHIP.** Every desk number reproduces exactly (counts, events, frequencies, outcomes, BSS) once I use the desk's own grid, and the warning measures agree to 0.0006. The faults are: the grid silently drops 11 points of the 48 states (R1), the page mis-describes what the archive holds for 9 of the 15 "nothing returned" days (R2), the page says it follows the SPC paper's method and used its issuance more closely than the paper supports (R3), the band reading is the generous one and the page does not show the stated level read plainly (R4), and the hatched reading hides a large unrated share in recent years (R5). None changes the headline direction.

## 1. Recount from raw (desk grid, 1219 points, to match)

| | Desk | Referee |
|---|---|---|
| Closed days with an outlook / grid points | 6,925 / 1,219 | 6,925 / 1,219 (full 48-state grid: 1,230) |
| US rows, events | 8,441,575 rows | 8,441,575 rows, identical |
| US band rows, days, events (under 2 / 2-5 / 5-10 / 10-15 / 15-30 / 30-45 / 45-60) | 8,244,730 / 138,743 / 46,036 / 8,754 / 2,914 / 389 / 9 rows; events 3,323 / 3,029 / 3,310 / 1,545 / 776 / 187 / 3 | identical, days identical |
| US 10 to 15 band | 17.649 percent [16.27, 19.05] ABOVE | 17.649 [16.34, 19.10] ABOVE |
| US outcomes of 8 bands | 3 consistent, 1 above, 4 cannot tell | identical |
| Kansas 10 to 15 | 541 rows, 96 days, 84 events, 15.53 [11.87, 19.65] CANNOT_TELL | identical point values, [11.87, 19.47] |
| Tornado Alley 10 to 15 | 2,810 rows, 485 events, 17.26 [15.25, 19.29] ABOVE | identical, [15.23, 19.35] |
| Hatched US / Kansas / Alley | 723/7,454 = 9.70; 31/497 = 6.24 BELOW; 164/2,270 = 7.23 BELOW | identical counts; same outcomes |
| BSS US / Kansas / Alley | 0.0581 [0.0532, 0.0628]; 0.0605; 0.0564 | 0.0581 [0.0532, 0.0630]; 0.0605; 0.0564 |
| Per-year US table (19 years) | in summary | rows, events, outcomes identical |
| No 13Z outlook (CYCLE 13) days | 15 listed | same 15 |
| Database rows read / no end time | 25,265 / 1,103 | 25,265 / 1,103 |
| Tornadoes in 12Z-13Z gap / no outlook day | 296 closed (312 with prelim) / 62 | 296 / 62 |
| Pooled FY2008-FY2025 tornadoes, warnings | 23,092, 50,758 | 23,092, 50,758 |
| Pooled POD / lead / FAR | 62.69 / 9.75 / 71.20 | 62.69 [61.41, 63.96] / 9.75 [9.35, 10.15] / 71.21 [70.37, 72.10] |
| Verified warnings pooled | 14,617 | 14,615 |
| FY2008 POD / lead / FAR | 70.82 / 13.25 / 74.72 | 70.77 / 13.24 / 74.76 |
| FY2013 | 55.15 / 8.48 / 73.83 | 55.15 / 8.48 / 73.83 |
| FY2025 | 66.42 / 10.09 / 67.04 | 66.42 / 10.09 / 67.04 |
| Other FYs (all 18) | | max POD difference 0.0006, max verified difference 2, no outcome differs |

Point values match exactly or nearly. Intervals agree to about 0.001 (different seed). The 0 of 24 band outcomes differ in the three closed cells. The three warning readings (POD below, lead below, FAR cannot tell) are the same in every fiscal year. The residual warning differences (verified counts, FY2026 POD 61.69 against 61.36) come from the point-on-edge convention: 8 of 1,460 preliminary reports sit exactly on a warning polygon edge or vertex (coordinates rounded to 0.01 degree in both files). See R9.

Cross-check against an outside number: OIG Appendix B says NWS has not met the POD or lead goal since FY 2011 and met the FAR goal in 9 of the 12 years since. The desk's point FAR is at or under 71 in 8 of FY2012-FY2023 (FY2021 is 71.35). Close agreement, so the method is not off the official one by a large amount.

## 2. Is within 25 miles of a point the right reading, and is the grid faithful?

SPC about page: "The probabilities that you see on the graphics represent the probability of one or more events occurring within 25 miles of a point during the outlook period." The desk's distance rule is the literal reading. Kay and Brooks do something slightly different: "Probabilities are produced by first binning storm reports onto a grid covering the U.S. (80 km nominal grid spacing). The area of each grid box is roughly equivalent to the area of a circle 25 statute miles in radius." So SPC's own work bins reports into 80 km boxes (area 6,400 km2 against 5,083 km2 for a 25-mile circle), and the desk measures track distance to the grid point. The two readings differ in detail, not in kind. I re-ran with three shifted grids (offsets 40/40, 20/60, -30/25 km): US 10 to 15 stays ABOVE in all (17.7 to 17.9 percent), Kansas 10 to 15 stays CANNOT_TELL, Alley 10 to 15 flips between ABOVE and CANNOT_TELL, US outcome counts flip between 3 and 4 consistent. The plan does not fix the grid phase, and the desk's phase (multiples of 80 km from the projection origin) is one choice among many.

**R1. The grid bounding box clips 11 points inside the 48 states. Severity: fix before ship (rerun).** In tornado_tick.py the grid range is built from corner projections (ymin from latitude 24 at lon -125 and -66.5, ymax from latitude 50 at lon -96). Albers curves, so the southern tip of Texas (5 points), south Florida (3) and the north Washington coast (3) fall outside. The plan says points are kept where they fall inside the 48 states and DC. Full grid: 1,230 points (Alley 251, Kansas 31). Effect on the headline is negligible (US 10 to 15: 8,760 rows, 1,546 events, 17.648 percent [16.36, 19.12], same outcome counts), but every count on the page changes. Fix: build the grid from a rectangle that covers the states with margin (for example x -3200 to 3200 km, y -800 to 3600 km), rerun, rebuild. Also note DC has no 80 km point, so "48 states and DC" should read "48 states" or the DC claim goes.

## 3. Canonical outlook, re-issues, the gap hour, time zones

IEM CYCLE 13 holds 7,239 days in 2007-2025 plus 2026, one PRODISS per day (no multiple corrected products inside CYCLE 13). The other cycles are 1, 6, 16, 20 and -1.

**R2. Nine of the 15 "no outlook" days do have a 1300 UTC outlook in the archive, under CYCLE -1. Severity: fix before ship (copy).** 20070720, 20080610, 20120122, 20200308, 20200414, 20200415, 20200502, 20200523, 20200526 carry products with ISSUE 1300 (PRODISS 12:25 to 12:59, some with several corrections) labelled CYCLE -1. 20120122 includes 2, 5, 10, 15 percent contours and a hatched area. The plan fixed CYCLE 13, so leaving them out is plan-faithful, but the page sentence "Days in the frame with no 1300 UTC Day 1 outlook in the archive: 15" is false for 9 of them. Only 6 days (20100921, 20110423, 20120818, 20121009, 20131110, 20251016) have no 1300 product of any cycle. Using the latest ISSUE-1300 product on every day (6,934 days): US 10 to 15 17.72 percent [16.37, 19.10], ABOVE, outcome counts unchanged. Fix: say "no outlook with IEM cycle 13 in the archive: 15 days, nine of which hold a 1300 UTC product the archive labels cycle -1".

**R2b. Note. 30 scored days use a product issued after 1300 UTC.** On 30 days the CYCLE 13 product has ISSUE 1315 to 1630 (PRODISS up to 15:58), but the window is scored from 13Z. SPC about: "valid from the start of issuance". Tornadoes before issuance count as events against a forecast that did not yet exist. The effect on every headline value is below 0.001. Say so, or score those days from ISSUE.

Gap hour: tornadoes starting 12Z to 13Z (296 closed-year tornadoes plus 16 preliminary) are in no outlook window because the 1300 outlook is valid 13Z to 12Z. The page discloses this. A tornado that starts before 13Z and continues past it is also not counted. Note only.

Time zone: raw row `1104270012-01,2011,04,27,2011-04-27,00:12:00,3,MS,...` converts 00:12 CST to 06:12 UTC, which matches the desk. All database rows have tz 3 (0 others). Both date/time and edat/etime use the same conversion. No fault.

## 4. Band assignment and the hatched reading

**R4. The band reading [L, next L) is more generous than SPC's stated level and the page does not show the level read plainly. Severity: fix before ship (copy).** SPC labels each region with the contour value. Reading each US band against its own label, with the same interval: 2 percent contour 2.18 [2.07, 2.30] ABOVE, 5 percent 7.19 [6.80, 7.59] ABOVE, 10 percent 17.65 [16.34, 19.10] ABOVE, 15 percent 26.63 [23.38, 30.36] ABOVE. The three CONSISTENT readings on the page (2 to 5, 5 to 10, under 2) come from the band width, not from the stated level. The plan fixed the band reading and the page states it, so this is a copy issue, but a reader sees "consistent" beside 2 percent drawn and 2.18 observed with no indication that the label itself is read as too low. Fix: add one sentence and a column "Stated level" next to Observed, and state the label reading result for the bands with 30 or more days.

**R5. Hatched reading hides unrated tornadoes that are 14 to 20 percent of recent years. Severity: fix before ship (copy).** The page gives "1,546" unrated tornadoes. By year (rated none until 2016): 2016 31, 2017 66, 2019 185, 2020 106, 2021 207, 2022 155, 2023 268, 2024 256, 2025 234, which is 15 to 19 percent of each of 2021 to 2025. They are counted as not EF2 or stronger. If every unrated tornado near a hatched point were EF2 or stronger, the frequency would be at most US 10.54 (from 9.70), Kansas 7.04 (6.24), Alley 9.07 (7.23). The US reading CANNOT_TELL already sits there. The Alley BELOW reading is fragile: its upper point value 9.07 with the same interval width reaches past 10 (not recomputed with a bootstrap). Fix: state the unrated share by year and the bound, and mark the Alley and Kansas hatched BELOW as dependent on how unrated tornadoes are read. Kansas BELOW also flips to CANNOT_TELL under one of my shifted grids.

## 5. The warning method against the GPRA definition

OIG Box 1 quoted correctly in PLAN and page (checked against the PDF text, p. 11: "A warned tornado segment is one that occurs within the bounds of a warning area during the valid time of the alert", "Lead time is computed for every 1-minute segment of the tornado track", "A warning followed by a tornado is considered verified", goals 72, 13 and 71). Segment logic, issue <= t < expire, fiscal year boundaries (a warning issued before the year still covers early tornadoes, a tornado after the year end can verify a late warning), and the earliest-warning rule all reproduce. My global verification (any tornado at any time) gives 14,615 against the desk's 14,617, so the six-hour extension past the year end loses nothing. Box 1 does not say which warning supplies the lead when several cover a segment. The desk's earliest-issued rule is a choice, named nowhere on the page.

**R6. The warning polygon is the issuance polygon held to its expire time. Severity: fix before ship (copy).** The IEM rows carry utc_polygon_end, which is earlier than utc_expire in about 82 percent of the FY2018 rows (1,335 of 1,638), because the polygon is replaced or trimmed by later statements. The file read holds only the issuance polygon (status NEW). The page says "as issued" but not that it is held past its replacement. Holding the first polygon for the whole life favours the warnings if the updates trimmed it, and can disfavour them if the polygon later moved ahead of the storm. If the issuance polygon counts only until its polygon_end (a floor, since the replacement polygons are not in the file), pooled POD is 34.7 percent, lead 2.6 minutes, FAR 78.2 percent. So the true value lies between that floor and the desk's 62.7, 9.75 and 71.2. POD and lead BELOW hold at both ends. FAR CANNOT_TELL could become ABOVE at the other end. Fix: state this under the warning table and say the FAR reading is the more open of the three.

**R7. Duplicate warning rows. Severity: note.** 33 pairs share the same product, event, issue and polygon and differ only in polygon_end or expire (for example BMX event 12, 2010). Each pair is counted as two warnings in FAR and verification. 33 of 50,758, effect below 0.001.

**R8. The FY2027 row exists in the data. Severity: note.** summary has FY2027 (124 warnings, 63 tornadoes, preliminary). Check that the page row list carries the preliminary label on it and that FY2026 is also labelled. The page's own "Fiscal years from FY2026 on use the preliminary reports" covers it.

**R9. Point-on-edge convention. Severity: note.** The desk uses matplotlib contains_points, which can count a point exactly on an edge as inside. Mine counts it outside. 8 of 1,460 FY2026 preliminary reports sit exactly on an edge of an active warning (0.01 degree rounding), enough to explain the 0.003 FY2026 POD gap. State the convention in the plan notes.

## 6. Does the day-block bootstrap understate?

Yes, modestly. My intervals for 10 to 15 (US) by resampling: day [16.31, 19.09], 7-day moving block [16.32, 19.07], 14-day [16.24, 19.14], 30-day [16.09, 19.28], whole years [15.30, 20.31]. Kansas 10 to 15: day [11.72, 19.47], year [11.71, 19.67]. Alley 10 to 15: day [15.35, 19.39], 30-day [15.24, 19.40], year [14.70, 20.35]. The US 10 to 15 ABOVE holds under every one (the lowest bound is 15.30 against 15.00 for the whole year bootstrap) but with 0.3 points of margin. Alley 10 to 15 ABOVE holds at 14.70 only through the day and block versions, so under whole-year resampling it reads CANNOT_TELL. US 5 to 10 and 15 to 30 outcomes do not change. BSS US: day [0.0532, 0.0628], 30-day [0.0507, 0.0651], year [0.0508, 0.0651], still above zero. The page says the day bootstrap does not cover neighbouring days, which is honest. Fix: add "A resample by whole years widens the US 10 to 15 interval to 15.3 to 20.3 percent and the reading stays above" and change nothing else.

BSS against a smoothed climatology (120 km Gaussian, month weights 0.25, 0.5, 0.25, leave one year out): 0.0570 [0.0520, 0.0623] against the desk's 0.0581. Above zero either way. The per-point-month climatology is slightly easier to beat than a smoothed one.

## 7. Page copy

Headline (tornado_headline.py output): "17.6%" and "a tornado came within 25 miles of a point 17.6 percent of the time, with a 95% interval of 16.3 to 19.1 percent, and the band reads above. Of the eight stated bands, 3 consistent, 1 above and 4 cannot tell. In Kansas the same band held 15.5 percent, from 11.9 to 19.7 percent, over 96 days, and reads cannot tell." Every figure matches my recount (17.649, 16.27, 19.05, 15.527, 11.87, 19.65, 96 days, outcome counts).

**R10. Headline counts two empty bands as cannot tell. Severity: fix before ship (copy).** Of the four cannot tell, the 60 and over band has 0 rows and the 45 to 60 band has 9 rows on 1 day. "Of the eight stated bands" reads as eight scored. Fix: "Of the eight stated bands, 3 consistent, 1 above, 2 cannot tell, and 2 too thin to score (one day or none)". Keep the plan's order and its counts in the data.

**R3. The page says the issuance is "the Center's own verification paper used" and that "It follows that paper's method". Severity: fix before ship (copy).** Kay and Brooks (1999 experimental outlooks) used both: "Data was available for 273 1300 UTC outlooks and 266 2000 UTC outlooks". The paper bins reports to an 80 km grid and gridded 1200 UTC categorical outlooks for 1990 to 1994. It does not describe even-odd contour gridding of the outlooks, tracks as line segments, or distance to a point. The 80 km spacing and "outlook valid period" are theirs. Fix: "It uses the 80 km grid spacing and the valid period of the Center's verification paper (Kay and Brooks), which scored the 1300 and 2000 UTC outlooks." Herman, Nielsen and Schumacher (2018) was not fetched by me, so the "without interpolation" attribution in PLAN is unchecked.

**R11. The hatched definition is attributed to the product page by position. Severity: fix before ship (copy).** The sentence "A hatched area marks a 10 percent or greater chance of a tornado rated EF2 or stronger" follows the about-page quote, but the about page does not say it. It says significant means "A tornado that produces EF2 or greater damage". The hatched definition is in the Kay and Brooks figure caption ("Hatched cyan area represents 10% or greater chance of 1 or more F2 or stronger tornadoes", 1999). Fix: cite that paper for it or split the sentence.

**R12. The CIG sentence. Severity: note.** The page says the conditional intensity groups replaced the SIGN area "on or about 2 March 2026 under NWS notice SCN 26-11". SCN 26-11 exists (issued 29 Jan 2026). An NWS news item gives 3 March for the Day 1 start, the outlook data show the first CIG tornado day as 5 March 2026 and the last SIGN day as 19 Feb 2026. Use "in March 2026" or the 3 March date and add that the SCN text was not read in full by this pass.

Cause and overstatement scan: no cause is named (the lint finds no "because", "due to"). "A reading says how often tornadoes came where a band was drawn. It does not say why." is fine. The only claim that goes beyond the data is R3.

Public-copy rules on the main text: no semicolons (0 hits), no digits in any h1 to h3 heading (0 hits), no AI statement, "Heuremen LLC" appears in header, sources line and title. desk lint_copy reports 2 hits that are false positives: the capital I in "OIG-25-026-I" matched the first-person rule. Plain sentences hold. The title and meta description contain no digits.

## 8. Findings summary

| # | Severity | Item | Fix |
|---|---|---|---|
| R1 | fix before ship (rerun) | Grid box drops 11 points (TX tip, FL, WA); DC has no point | Widen the grid rectangle, rerun, rebuild |
| R2 | fix before ship (copy) | 9 of 15 nothing returned days have a 1300 product under CYCLE -1 | Reword the nothing returned sentence, list the nine |
| R2b | note | 30 days scored with a product issued 13:15 to 15:58 | Say so |
| R3 | fix before ship (copy) | "paper's issuance", "follows that paper's method" overstated | Reword as above |
| R4 | fix before ship (copy) | Band reading generous, stated level not shown, label reading ABOVE in every band with data | Add stated level column and one sentence |
| R5 | fix before ship (copy) | Unrated 15 to 19 percent of 2021 to 2025, hatched BELOW fragile in Alley | Show by year and the bound |
| R6 | fix before ship (copy) | Issuance polygon held to expire; floor and desk values differ greatly | State the bracket, FAR is the open reading |
| R7 | note | 33 duplicate warning rows | None needed |
| R8 | note | FY2027 preliminary row in the data | Confirm the page label |
| R9 | note | On-edge points count outside here, may count inside in the desk | Note the convention |
| R10 | fix before ship (copy) | Headline counts two empty bands as cannot tell | Say two are too thin |
| R11 | fix before ship (copy) | Hatched definition not on the about page | Cite Kay and Brooks |
| R12 | note | CIG date and SCN wording | Use March 2026 |
| bootstrap | note | Year resampling widens US 10 to 15 to 15.3 to 20.3, still above | One sentence |

Nothing blocks ship. Numbers reproduce. R1 needs a rerun, the rest are copy.
