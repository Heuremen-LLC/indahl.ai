# Referee report: SEASONAL desk (CPC 3-month outlook stated chances against the observed category, 2-degree grid)

Referee: read-only refuting pass, 10 November 2026. Nothing in `seasonal_index/` was edited.
Inputs read: PLAN.md, git log, data/plan_seal.json, seasonal_tick.py (read only), summary_seasonal.json, seasonal.html, seasonal_headline.py, CHECKS.md, lint_copy.py, the 14 raw CPC files, and cpc.ncep.noaa.gov/products/verification/summary/index.php?page=tutorial (fetched raw with curl).
Referee code (shares nothing with the desk code, no import of seasonal_tick.py or heuremen_kit.py): `code/recount.py` (reader, alignment and orientation tests), `code/explore.py` (land mask, value ranges), `code/boot.py` (own binning, rule, moving-block bootstrap, block sweep, diff against desk), `code/sens.py` (seed sweep), `code/heidke.py` (own Heidke), `code/frac.py` (non-whole categories), `code/probcat.py` (probability files against category file), `code/interp.py` (pooling, eras, composition), `code/extra.py` (edge weights, circular blocks, El Nino calendar check). Outputs in `out/rows.json`, `out/diff_vs_desk.json`, `out/heidke_none.json`.

## Verdict

**FIX THEN SHIP.** Every row count, hit count, mean stated chance, observed frequency, interval and outcome reproduces (44 of 44 cells, 0 differences). The Heidke recompute reproduces CPC's published scores. Alignment and orientation are right and each wrong alternative destroys the match. Nothing blocks on a number and no outcome changes under the plan. The fixes are copy: the page tells a reader the temperature "leaning" cell is a forecaster miss, but the same file shows the above-normal category was observed in 51.6 percent of all land cells, and CPC says its thirds come from a 1981-2010 reference period. The page says the period is not stated, which is true of the files and false of CPC's own tutorial.

## Seal

Plan commit 11d602c at 09:42:56 -05:00 (14:42:56Z). First comparison 14:44:05Z, 69 seconds later. PLAN.md sha256 equals plan_seal.json (3a5e5ab6...), `git diff 11d602c HEAD -- PLAN.md` is empty. Raw files on disk are dated 09:28 and were scouted before the plan, which the plan states (mask, value ranges, share of whole categories, first and last Heidke rows). Desk code and the dated copy of the raw files came in commit 39638cb (09:48), after the first run, which is allowed. data/seasonal.json is not tracked in git (see R11).

## 1. Alignment and orientation (independent)

Forecast files hold 383 records, observed 380, Heidke files 380 rows (19950101 to 20260801), 684 values each.

Alignment test: my own Heidke on CPC's categorical file against CPC's stated non-EC score, forecast record i set against observed record i plus a shift.

| forecast shift | temp mean abs diff to CPC (points) | prec mean abs diff |
|---|---|---|
| -2 | 18.26 | 25.34 |
| -1 | 12.66 | 17.30 |
| 0 (desk) | 0.004 | 0.012 |
| +1 | 13.09 | 17.48 |
| +2 | 18.77 | 24.54 |
| observed shift -1 / +1 | 19.39 / 18.36 | 17.21 / 18.45 |

Share of seasons within 0.05 point of CPC: 99.7 percent (temp) and 98.7 percent (prec) at shift 0, under 3 percent at any other shift. Alignment is right.

Probability files against the category file: with the probability record at shift 0, the category equals the larger of above and below in 99.93 percent (temp) and 100.00 percent (prec) of non-EC cells. At shift -1 or +1 it is 83.6 / 83.8 percent (temp) and 72.2 / 72.4 percent (prec). So the above and below files are aligned to the same record as the category file, which is what the reliability rows need.

Calendar anchor (cannot be proven from the files alone, the Heidke match only fixes record to record): precipitation non-EC score peaks at first-target-month 19971201 (61.6), the DJF 1997-98 El Nino winter, and 19971101 is 41.3. That is the right calendar for "first target month, 3-month season". The desk's season labels (JFM 1995 to ASO 2026) are consistent with this and with the CPC about file ("Valid Period JFM 1995").

Orientation: land mask is identical in all 380 seasons (232 cells). Reading the record as 19 latitude rows by 36 longitude columns, row 0 is 20N, column 0 is 130W. Row 3 (26N) holds land at column 16 (98W, the Texas tip) and columns 24 and 25 (82W and 80W, south Florida). Florida (82W 28N) is land, 128W 22N and 62W 54N are not. Rows 0 to 2 and 15 to 18 are all sea. Applying a flip or a transpose to the forecast only gives a 19 to 27 point mean difference from CPC. Orientation is right. (The desk's gate 2 passes for the same reason.)

## 2. Recount, desk against referee

| | Desk | Referee |
|---|---|---|
| Seasons scored / forecasts waiting | 380 / 3 per variable | 380 / 3 (383 minus 380 records) |
| Land cells | 232 | 232 |
| Unreadable rows (missing, negative, near outside 0 to 100, NaN) | 0 | 0 (above range 3.33 to 79.6, below 3.33 to 76.4, near 17.0 to 45.6) |
| Reliability cells (2 variables x (1 leaning + 3 categories x 7 bins)) | 44 | 44 |
| Rows, seasons, hits, mean stated, observed in all 44 cells | | 0 differences |
| Intervals (own bootstrap, same design, seed 20261110) | | max difference 0.0000 |
| Outcomes in all 44 cells | | 0 differences |
| Heidke mean difference ours minus CPC, 4 score rows | +0.002, +0.001, +0.010, +0.007 | 0.0018, 0.0002, 0.0100, 0.0051 (my all-score has 380 prec seasons, R2) |

Headline: temperature leaning, 30,834 rows, 380 seasons, 18,533 hits, stated 48.24, observed 60.11, interval 54.88 to 64.22, ABOVE. Precipitation leaning 14,027 rows, 371 seasons, stated 45.29, observed 45.52, interval 42.01 to 48.49, CONSISTENT. Both reproduce.

An identical interval to four places means numpy's default_rng with the plan's seed gives the same stream, so this checks the aggregation and the rule and not the Monte Carlo. R6 covers the Monte Carlo.

## 3. Findings

**R1. Observed thirds are set against a fixed older reference period and the page says CPC does not state it. Severity: fix before ship (copy).** The page says "The observed categories come from CPC's own verification files, which do not state which period of normals sets the thirds." The files do not, but the CPC tutorial that the page cites says "The observation categories are determined by using the climatology data from 1981-2010 as the reference period." Across all 380 seasons the observed temperature category is above in 51.6 percent of land cells, near 28.6, below 19.8 (a perfect tercile world gives 33.3 each). Equal-chances rows alone (the 31 to 35 bin) saw above in 46.1 percent, near 30.4, below 23.4. By era of 120, 120 and 140 seasons, leaning rows were stated 45.5, 46.8, 49.8 percent and observed 54.1, 52.7, 65.4. The reading "above, it happened more often than stated" is true, but the headline invites the reader to think the stated chances were badly set in a year-by-year sense, when most of the gap is that the observed thirds are not centred on these years. Precipitation shows no such offset (above 35.2, near 31.4, below 33.4 percent). Fix: (a) replace the sentence on normals with "CPC's tutorial states that the observed categories use 1981-2010 as the reference period. Over all rows, the observed temperature category was above in 51.6 percent of cells, near in 28.6 and below in 19.8." with the three numbers written to summary_seasonal.json by the desk (described-not-scored, like the other shares); (b) in the headline add "(thirds set by CPC's 1981-2010 reference period)" after "observed in 60.1 percent of grid cells". This names a definition, not a cause. If CPC moved the verification to 1991-2020 normals, the tutorial page does not say so, and the page must not say it did.

**R2. All-score comparison drops six precipitation seasons that CPC lists. Severity: fix before ship (copy and count).** CPC lists 19960201, 19960601, 19960701, 19960801, 19970601 and 20030601 for precipitation as non-EC "nan", All 0.00, Coverage 0.00 (every one of the 232 cells is equal chances). Leaving them out of the non-EC difference is fair, CPC has no number there either. For the all-score the formula gives 0 (coverage 0) and CPC states 0.00, so the difference is 0 and the all-score row should read 380 seasons, not 374. Effect on the reading: none (mean difference 0.0051 against 0.0070, CONSISTENT either way). Fix: count those six seasons in the precipitation all-score row with difference 0, and add to the sentence about the six seasons: "CPC lists these seasons with an all score of 0 and no non-EC score." Alternatively, keep 374 and say on the page that CPC states 0.00 for the other six. Either way the page must say what CPC lists.

**R3. Ten cells hold non-whole categories that CPC appears to count, and the page does not say so. Severity: note.** The categorical file holds non-integer values (1.282, 1.329, 1.848, 1.991, 2.662, 2.663, 2.711, 2.816, 2.165, and others) in 9 precipitation cells over 5 seasons and 1 temperature cell in 1 season. The plan leaves them out, as stated. CPC's coverage in those seasons is higher than ours by up to 1.73 points (for example precipitation 20210101: ours 76.29, CPC 78.02, a difference of 4 cells of 232) and the one precipitation season outside 1 point (20210101, non-EC 6.78 against 5.52, a difference of 1.26) is explained by this. Rounding the values makes coverage match CPC to 0.005 in every season. The recompute is within tolerance either way. Fix: one clause on the page, "In 6 seasons, 10 cells hold a category that is not a whole number, we left them out, and CPC's stated coverage is up to 1.7 points higher in those seasons." Name the one precipitation season outside 1 point, which the page currently counts silently as 373 of 374.

**R4. Bin labels do not match the bin edges. Severity: fix before ship (copy).** Edges are under 25, 25 to under 31, 31 to under 36, 36 to under 40, 40 to under 50, 50 to under 60, 60 and over. Labels read "25 to 30", "31 to 35", "36 to 39", "40 to 49". Stated chances are continuous in this file (about 5,000 distinct values for above-normal temperature), so 3,844 temperature rows with 30 <= x < 31 sit in the "25 to 30" bin (754 above, 214 near, 2,876 below), and similarly for 35 to 36 (3,759 rows), 39 to 40 (3,175) and 49 to 50 (948). A reader who tests a row at 30.5 percent will not find it. Equal chances in the file range 31.5 to 35.5 (temperature) and 31.5 to 36.1 (precipitation), so the 31 to 35 bin does hold them all except for a few precipitation rows above 36 (they sit in the next bin, at most a handful). Fix: label the bins "25 to under 31", "31 to under 36", "36 to under 40", "40 to under 50", "50 to under 60" in the plan note on the page, in the summary bin keys and in both tables, or add one sentence "Bins include the lower edge and exclude the upper edge, in percent." This changes labels only.

**R5. The "leaning" cell is mostly one category and the page does not say so. Severity: fix before ship (copy).** Temperature leaning rows: 28,312 above-normal (17,580 observed, 62.1 percent, stated 48.7), 2,394 below-normal (900 observed, 37.6 percent, stated 43.6), 128 near-normal (53 observed, stated 42.3). So 91.8 percent of the leaning rows are the warm category, and below-normal leans were observed less often than stated (37.6 against 43.6), which runs the other way. Pooling hides this. Precipitation: 7,197 above (stated 45.2, observed 43.8) and 6,830 below (stated 45.4, observed 47.4), balanced, no near rows. Concentration is not an issue: the five seasons with the most leaning rows hold 3.4 percent of temperature rows, the top 20 hold 12.2 percent, the top 38 (10 percent of seasons) hold 21.8 percent, and with those 38 removed the cell reads observed 59.0 against stated 47.7. 66.1 percent of temperature seasons have observed above stated. So no few seasons carry it, but the late years carry the most rows (140 seasons, 56.6 percent of rows). Fix: add one described-not-scored line under the leaning table, from the summary: "Of the temperature rows, 28,312 lean above normal (observed 62.1 percent against 48.7 stated) and 2,394 lean below normal (37.6 against 43.6)." The headline sentence "a temperature category" can stay.

**R6. Block bootstrap sensitivity. Severity: note (one copy sentence is optional).** Block length sweep with my own code, 2,000 draws, sealed seed:

| block | temp leaning interval | outcome | prec leaning | outcome |
|---|---|---|---|---|
| 6 | 55.5 to 63.9 | ABOVE | 42.0 to 48.7 | CONSISTENT |
| 12 (sealed) | 54.9 to 64.2 | ABOVE | 42.0 to 48.5 | CONSISTENT |
| 24 | 54.0 to 64.7 | ABOVE | 42.0 to 48.4 | CONSISTENT |
| circular, 12 | 55.1 to 64.8 | ABOVE | | |
| 1 (seasons as independent) | 57.3 to 62.9 | ABOVE | | |

The headline does not flip at any block length. Of the other 42 cells one flips between blocks of 12 and 6 or 24: temperature, above, 25 to 30 percent goes CANNOT_TELL to ABOVE at block 6 (interval 28.8 to 45.5 against a stated 28.3). No flip at 24. Seed sweep (10 other seeds, block 12): one cell changes, precipitation, below, 40 to 49 percent. It reads CANNOT_TELL under the sealed seed (interval 40.5 to 50.7, width 0.1023, just over the 0.10 limit) and CONSISTENT under 2 of 10 other seeds (width about 0.099). That cell sits on the width rule and nothing else does. Headline and all other cells are stable across seeds. Edge effect: moving blocks with starts uniform on 0 to S-12 weight the first and last season at 0.087 expected draws against 1.04 for an interior season (blocks of 12), with the weight rising across the first 12 and last 12 seasons. Circular blocks give a slightly wider interval (55.1 to 64.8) and the same reading. Fix: none required. Optional sentence: "A circular block, or a block of 6 or 24 seasons, gives the same reading for both headline cells."

**R7. The leaning cell is the plan's headline, but temperature stated chances are interpolated grid values and not the numbers printed on CPC maps. Severity: note.** The gridded file holds about 5,000 distinct above-normal values, not the contour levels CPC prints on its outlook maps (33, 40, 50 and so on). Equal chances in the grid are 31.5 to 35.5, not exactly 33.33. Category 0 (equal chances) is 38.5 percent of temperature rows and 61.8 percent of precipitation rows, and those cells carry stated chances of 31.5 to 35.5, so the label "33.33 each" is CPC's, the file holds interpolated values near it. The page says "Where no category is favoured it states equal chances, 33.33 percent each", which is what CPC states, and then reads 31 to 35 as the equal-chances bin, which is fine. But "the chance the outlook stated" for a 44 percent row is a grid value, not a printed one. Fix: add to the data paragraph "Stated chances are the gridded values in CPC's verification files, which can differ slightly from the contours printed on the outlook maps." I could not check against map images, so I state this as a risk, not a finding of difference.

**R8. Heidke recompute checks alignment, not reliability. Severity: note.** The page calls the recompute a "second ruler". It tests that the categorical file and the observed file pair up as CPC pairs them, which my alignment table above uses as evidence. It does not test the stated chances. That is fine, but the wording "matches the score CPC states within 1 point in 380 of 380 temperature seasons" should say "from CPC's categorical file". Mean difference is 0.002 points for temperature (max 0.62 in one season, 20240501, coverage one cell short, same cause as R3) and 0.010 for precipitation (max 1.26). Also my own formula (HSS = 100(H-E)/(T-E), E = T/3 over non-EC cells, All = HSS x coverage) reproduces all 380 temperature seasons within 1 point and 373 of 374 precipitation seasons, bootstrap interval of the mean difference -0.0001 to +0.0053 (temperature non-EC) and +0.0023 to +0.0199 (precipitation non-EC). Same readings as the desk, CONSISTENT in all four rows.

**R9. CPC quote accuracy. Severity: note (verified).** The page's quote "HSS (%) = 100 * (H - E) / (T - E) where H = Number of correct forecasts, E = Expected number of correct forecasts (1/3 of total), and T = Total number of valid forecast-observation pairs" is verbatim from the tutorial. The second quote on the page, "HSS withEC (%) = HSS * coverage", is verbatim (the tutorial writes it with a space). The tutorial adds "where coverage = number of non EC forecasts/Total", the page's own gloss agrees. The tutorial also says "For monthly and seasonal forecasts, the equal chances (EC) forecast category are included in scores" which is why there are two scores, and it says the chart date for seasonal scores is the middle month. The Heidke file column is labelled "1st_Target_Month", the page follows the file. State this in a clause if the page keeps "first target month". The about files are stale: 90day_obs_about.txt states "Number of Records: 169" and "End of Record: Valid Period JFM 2009", while the file holds 380 records. The page does not repeat it. Optional: one clause that CPC's about files are older than the archive.

**R10. Copy and house rules. Severity: note (passes).** lint_copy.py 0 hits. I found no semicolons in visible text (the 7 in the file are HTML entities and CSS), no AI statements, no digits in any heading (h1 and six h2 headings, the big "60.1%" is not a heading), no cause named ("This page does not say why a category happens more or less often than stated" stands), NOAA public-domain credit present ("NOAA/NWS information is in the public domain. Our counts and readings are ours and are not NWS material."). Heading "Temperature by stated chance" etc. are fine. Every number on the page and in seasonal_headline.py traces to summary_seasonal.json (60.1, 48.2, 54.9, 64.2, 45.3, 45.5, 42.0, 48.5, 380, 373 of 374, 232, 3 and 3, all 44 table cells, all heidke cells). Fix R4 labels in the same pass. The headline says "it happened more often than stated" which is right for the cell, add the R1 clause so a cold reader does not read it as a verdict on CPC.

**R11. data/seasonal.json is not in git. Severity: note.** git ls-files shows summary_seasonal.json, data/seasonal_live.json and data/plan_seal.json but not data/seasonal.json (per-season Heidke rows). Whether it is in .gitignore by design is the desk's call. The dated raw copy is tracked, so any row can be rebuilt from it.

**Climate divisions and grid. Severity: acceptable.** The desk uses CPC's 2-degree grid, 232 land cells, because CPC archives both the outlook and the observed category on that grid, scores itself on it, and no division-level archive was found. I looked for one and agree: CPC's verification directory holds the grid files only, shapefiles cover 2007 on, with contours not observed categories. The grid is acceptable as the unit and it is a reason to read CPC's own scores (R8 shows the recompute matches). Two copy points: cells are 2 degrees square so they carry unequal areas and land fraction (coastal cells may be mostly sea, the mask is "has an observation" not "all land"), and rows weight each cell equally. The page says "did not weight cells by area" for the Heidke score only. Add "Cells are not weighted by area" to the reliability paragraph. The page does say divisions were set aside and why, good.

## 4. Summary table

| # | Severity | Item |
|---|---|---|
| R1 | fix before ship (copy) | State CPC's 1981-2010 reference period, give the all-rows observed shares (51.6 above), add to headline |
| R2 | fix before ship (copy and count) | Six all-EC precipitation seasons: CPC lists All 0.00, count them in the all-score row or say so |
| R3 | note | 10 non-whole category cells, CPC counts them, one sentence and name the season outside 1 point |
| R4 | fix before ship (copy) | Bin labels say 30, 35, 39, 49, edges are 31, 36, 40, 50 |
| R5 | fix before ship (copy) | Leaning cell is 91.8 percent above-normal rows, give above and below split |
| R6 | note | Block 6, 24, circular and seeds: headline never flips, two non-headline cells sit on a rule edge |
| R7 | note | Stated chances are grid values, not map contours |
| R8 | note | Heidke checks pairing, not reliability, wording |
| R9 | note | Quotes verified, about files stale |
| R10 | note | Lint passes, numbers traceable |
| R11 | note | seasonal.json not tracked |

No outcome, threshold, bin edge or cell changes under the plan. Do not change the plan. Items R1 to R5 are page and summary-field changes only.
