# Referee report: CONE desk (NHC track forecast cone against where storms went)

Referee: read-only refuting pass, 10 November 2026. Nothing under `cone_index/` was edited. Inputs read: PLAN.md (commit e49ebd2, sha256 matches data/plan_seal.json), git history (later commit bcea3a7 changes cone_tick.py by the display-only 60 h block), summary_cone.json, data/cone.json, cone.html, cone_headline.py, lint_copy.py, CHECKS.md, the 625 a-deck files, the 2026 a-deck and b-deck files, both HURDAT2 files, the 123 archived cone pages plus the live page, both NHC error PDFs, the saved NHC cone graphic page and verification page.

Referee code shares nothing with cone_tick.py, heuremen_kit.py or cone_headline.py. Own a-deck reader, own HURDAT2 and b-deck readers, own radii parser, own PDF parser, own haversine (R = 3440.065), own cone membership (exact quadratic test on the hull of two circles in an azimuthal equidistant projection centred on the tested point), own storm-level bootstrap (2,000 resamples, seed 777, so intervals differ from the desk's by at most 0.4 points).

## Verdict

**FIX THEN SHIP.** Every number reproduces exactly: all 66,165 circle rows, all 6,017 whole-path rows, all cells, all 34 by-season whole-path rows, the 2026 cells, and all 224 second-ruler rows. The geometry survives two independent methods. The faults are in what the page leads with and in a few statements around the headline. All fixes are copy. No outcome, threshold or cell changes.

## 1. Recount from raw (Desk vs Referee)

| Cell | Desk inside of scored (storms) | Desk share, 95% interval | Desk reading | Referee inside of scored (storms) | Referee share, 95% interval | Referee reading | Nothing returned desk / referee |
|---|---|---|---|---|---|---|---|
| Atlantic, whole path | 697 of 1315 (93) | 53.0 (45.1 to 60.4) | CANNOT_TELL | 697 of 1315 (93) | 53.0 (45.0 to 60.3) | CANNOT_TELL | 1692 / 1692 |
| East Pacific, whole path | 650 of 1106 (102) | 58.8 (52.4 to 65.0) | CANNOT_TELL | 650 of 1106 (102) | 58.8 (52.5 to 64.6) | CANNOT_TELL | 1590 / 1590 |
| Atlantic, 12 h | 3169 of 4612 (261) | 68.7 (66.1 to 71.2) | CONSISTENT | 3169 of 4612 (261) | 68.7 (66.0 to 71.3) | CONSISTENT | 520 / 520 |
| Atlantic, 24 h | 2889 of 4092 (239) | 70.6 (67.5 to 73.6) | CANNOT_TELL | 2889 of 4092 (239) | 70.6 (67.4 to 73.6) | CANNOT_TELL | 949 / 949 |
| Atlantic, 36 h | 2562 of 3617 (217) | 70.8 (67.0 to 74.3) | CANNOT_TELL | 2562 of 3617 (217) | 70.8 (67.2 to 74.4) | CANNOT_TELL | 1268 / 1268 |
| Atlantic, 48 h | 2248 of 3186 (201) | 70.6 (66.4 to 74.3) | CANNOT_TELL | 2248 of 3186 (201) | 70.6 (66.4 to 74.3) | CANNOT_TELL | 1466 / 1466 |
| Atlantic, 72 h | 1697 of 2425 (170) | 70.0 (65.3 to 74.3) | CANNOT_TELL | 1697 of 2425 (170) | 70.0 (65.4 to 74.2) | CANNOT_TELL | 1668 / 1668 |
| Atlantic, 96 h | 1295 of 1839 (128) | 70.4 (64.5 to 76.1) | CANNOT_TELL | 1295 of 1839 (128) | 70.4 (64.6 to 76.1) | CANNOT_TELL | 1709 / 1709 |
| Atlantic, 120 h | 971 of 1415 (100) | 68.6 (61.3 to 75.2) | CANNOT_TELL | 971 of 1415 (100) | 68.6 (61.5 to 75.1) | CANNOT_TELL | 1592 / 1592 |
| East Pacific, 12 h | 2930 of 4172 (281) | 70.2 (67.8 to 72.5) | CANNOT_TELL | 2930 of 4172 (281) | 70.2 (67.8 to 72.6) | CANNOT_TELL | 484 / 484 |
| East Pacific, 24 h | 2621 of 3672 (264) | 71.4 (68.7 to 74.0) | CANNOT_TELL | 2621 of 3672 (264) | 71.4 (68.5 to 74.0) | CANNOT_TELL | 907 / 907 |
| East Pacific, 36 h | 2291 of 3209 (241) | 71.4 (68.3 to 74.4) | CANNOT_TELL | 2291 of 3209 (241) | 71.4 (68.1 to 74.4) | CANNOT_TELL | 1259 / 1259 |
| East Pacific, 48 h | 2027 of 2793 (217) | 72.6 (69.0 to 75.9) | CANNOT_TELL | 2027 of 2793 (217) | 72.6 (69.2 to 75.9) | CANNOT_TELL | 1481 / 1481 |
| East Pacific, 72 h | 1521 of 2109 (175) | 72.1 (67.9 to 76.1) | CANNOT_TELL | 1521 of 2109 (175) | 72.1 (67.7 to 76.2) | CANNOT_TELL | 1625 / 1625 |
| East Pacific, 96 h | 1133 of 1564 (142) | 72.4 (67.4 to 77.4) | CANNOT_TELL | 1133 of 1564 (142) | 72.4 (67.3 to 77.4) | CANNOT_TELL | 1654 / 1654 |
| East Pacific, 120 h | 819 of 1135 (105) | 72.2 (66.1 to 77.9) | CANNOT_TELL | 819 of 1135 (105) | 72.2 (65.8 to 77.9) | CANNOT_TELL | 1561 / 1561 |

Row-by-row diff against data/cone.json (code/diff_desk.py, out/diff_vs_desk.json):

| | Desk | Referee |
|---|---|---|
| Circle rows (all seasons incl. 2012 and 2026) | 66,165 | 66,165 |
| Rows on one side only | 0 | 0 |
| Outcome differences (INSIDE, OUTSIDE, NOTHING_RETURNED and its reason) | 0 | 0 |
| Distance differences over 0.01 n mi | 0 | 0 |
| Tropical-at-both-times flag differences | 0 | 0 |
| Whole-path rows | 6,017 | 6,017 |
| Whole-path rows on one side only / outcome differences / first-outside-hour differences | 0 / 0 / 0 | 0 / 0 / 0 |
| By-season whole-path rows (34, incl. 2012 not scored) | counts and readings | identical |
| 2026 cells (whole path 0 of 0 Atlantic, 103 of 182 East Pacific, 14 circle cells) | | identical inside, scored, nothing returned, reading |
| Second ruler (224 rows) | AL 111 CONSISTENT, 1 CANNOT_TELL. EP 109 CONSISTENT, 3 CANNOT_TELL | identical, every n, stated value, our mean (to 0.05) and reading |
| Radii, 18 seasons, both basins | data/radii.json | identical, same first copy for each season |
| Gate 3 (tau 0 median) | 6.0 n mi on 11,178 | 6.004 on 11,178 |
| Forecast files read, OFCL lines, differing duplicates, unreadable lines | 625, n/a, 0, 0 | 625, 183,932, 0, 0 |
| Forecasts shorter than five days | AL 2,236, EP 2,171 | identical |
| Forecasts without lead 12 / 24 / 36 / 48 / 72 / 96 / 120 | 23 / 216 / 516 / 991 / 2,219 / 3,432 / 4,684 | identical |

## 2. Joins, radii, rules

- Radii: re-parsed from the HTML (year from "cones in YYYY", first table, Atlantic column 1, East Pacific column 2). Same values and same earliest copy as the desk in all 18 seasons. Copies naming the same year disagree for 2020 (copy of 1 May 2020 differs from 1 April 2020) but only in the Central Pacific column, which is not scored. The 31 March 2020 copy names 2019 over the 2020 values, as the plan says. One archived copy (20190831171555) is binary and has no year, harmless. 2012 has no copy naming it, as stated.
- Joins: storm key is file name basin, number and year, the same as the HURDAT2 ID (AL012010 and so on). Tau 0 median 6.0 n mi on 11,178 forecasts, so no storm or time mispairing. Verifying time is the initial time plus the lead in hours. No HURDAT2 duplicates at a synoptic time. No a-deck line failed to parse. Zero differing duplicate OFCL positions, so "first in file" never mattered.
- Longitudes: signed degrees, East Pacific forecasts kept only for -140 < tau 0 longitude < 0. Same rows as the desk.
- Status rule: TD, TS, HU, SD, SS only, at the initial time and at the verifying time. Nothing returned is carried as its own bin in every cell and never enters the share (checked: shares are INSIDE over INSIDE plus OUTSIDE with the desk's inside counts).
- 2026: operational b-deck status read from field 11, first BEST line per synoptic time.

## 3. Whole-path geometry, independent check

- Method A (primary): exact quadratic test of "exists t in [0,1] with the point inside the interpolated disc", which is the hull of two discs.
- Method B: sampled boundary (720 points per circle) and a scipy convex hull per segment.
- Method C: the same hull idea on the sphere (great-circle interpolation of the centre, linear radius, no projection).
- All 2,603 scored paths: sign of a separate signed margin agrees with Method A in all 2,603. Methods B and C were run on all 1,722 paths within 25 n mi of the boundary plus 300 random others (2,022): both agree with the desk's outcome in 2,022 of 2,022. Projection choice does not matter.
- Edge cases: 33 paths lie within 0.5 n mi of the boundary, 260 within 4 n mi, 403 within 6 n mi (0.1 degree is about 6 n mi, the rounding of the files). Flipping every Atlantic path within 6 n mi in the favourable direction gives at most 59.3 percent (46.2 percent the other way). East Pacific 48.5 to 67.5 percent. So the Atlantic point estimate cannot reach 60 on rounding alone.

## 4. Trying to break the reading

- Bootstrap. Correct at the storm level and correctly implemented (all circle cells reproduce to within 0.4 points with a different seed). Season-level resampling (15 seasons) gives Atlantic whole path 44.7 to 61.8 and East Pacific 54.0 to 63.4, the same readings. See R5 for the knife edge.
- Selection. Of 3,007 Atlantic forecasts that carry all seven leads, 1,315 (44 percent) have a tropical best track at all 19 points. Scoring the best track that exists for the others (tropical points up to the first gap) puts the Atlantic share at 60.7 percent (56.0 to 65.3, 166 storms), and the East Pacific at 64.6 (60.4 to 68.5). So the 53.0 is a share among storms that lasted five days, and the page does not say that NHC's 60 to 70 may cover a different set. See R1.
- Radius-0 start at tau 0. Dropping the hull from the tau 0 point to the 12 h circle: Atlantic 676 of 1,315, 51.4 percent (43.9 to 58.6), East Pacific 619 of 1,106, 56.0 (49.3 to 62.0). It lowers the share by 1.6 and 2.8 points. Display only. East Pacific stays CANNOT_TELL, Atlantic would read BELOW (upper end 58.6). See R6.
- 60 h circle. The live NHC cone page lists 60 h among the circle hours, the graphic page does not, and the plan follows the graphic page. For forecasts that carry a 60 h position and seasons whose table has a 60 h radius (2020 on), adding it changes Atlantic 260 to 264 of 568 and East Pacific 155 to 155 of 282. Under one point. See R6.
- Leave one season out. Whole path Atlantic point estimate 50.4 to 55.5 percent, East Pacific 57.3 to 59.9, so no season drives the level. The Atlantic reading flips to BELOW if 2010, 2017 or 2024 is dropped (upper end 59.4, 57.9, 59.6) and sits at 60.0 without 2016. East Pacific stays CANNOT_TELL in all 15. Circle cells: the one CONSISTENT cell (Atlantic 12 h) becomes CANNOT_TELL without 2010, 2018, 2020 or 2023, and East Pacific 12 h becomes CONSISTENT without 2014. The other 12 never change.
- Same object as NHC? The graphic page says "the entire 5-day path of the center ... will remain within the cone about 60-70% of the time", which is what is tested. Older copies of the cone page add "Based on forecasts over the previous 5 years ... roughly 60-70% of the time" and "This is a different perspective that ignores most timing errors", which supports not checking timing. The live cone page no longer carries that sentence, so the plan correctly quotes the graphic page. Neither page says which forecasts are in NHC's sample (storms that last five days, or all), nor which best track. See R1.
- Second ruler, the four CANNOT_TELL rows. The rule handles all four as written: Atlantic 2020 72 h (318 against 275 cases), East Pacific 2015 72 h (188 against 199, limit 9.4), 96 h (146 against 157, limit 7.3), 120 h (115 against 126, limit 5.75). Among the 220 CONSISTENT rows the largest case-count gap is 13 and the largest mean gap is 1.48 n mi, 147 of 220 within 0.1 n mi.
- The 60 h display. My own recount gives Atlantic 2020 at 60 h 79.85 n mi on 319 cases, 72 h 98.07 on 275, 48 h 64.58 on 369, 96 h 133.06 on 192. NHC's printed row for 2020: 48 h 64.9 on 366, 72 h 79.9 on 318, 96 h 133.0 on 192. So NHC's printed 72 h cell matches our 60 h number and its 96 h matches our 96 h. The page may show the 60 h figure beside the row with no cause, as it does, because that is an observation of two pairs of numbers. It may not say that NHC mislabelled, mixed up or dropped a column. East Pacific 2015 is not explained by west-of-140 W positions (dropping those leaves 136 cases, not 188). Nothing to say there.

## Findings

**R1. The headline gives 53.0 percent without saying it is the storms that lasted five days. Severity: fix before ship (copy).** The lead says "with all five days of track", which is true, but a reader does not learn that this is 1,315 of 3,007 Atlantic forecasts that carry seven leads, or that NHC's page does not say which forecasts its 60 to 70 percent covers. The plan counts the rest as nothing returned and this is correct. Proposed fix, one sentence in the lead after the interval: "This is the 1,315 forecasts whose storm stayed a tropical or subtropical cyclone for all five days. A further 1,692 did not and are not in the share. NHC does not say which forecasts its 60 to 70 percent covers." Do not add the 60.7 percent partial-path figure to the headline cell. If the desk wants it, show it only as a row "added after the data, display only, decides nothing", as it did with the 60 h column.

**R2. "(none percent)" on the page. Severity: fix before ship (copy).** The 2026 sentence reads "Atlantic 2026: 0 of 0 forecasts with a full track stayed inside for the whole path (none percent), which reads cannot tell." Fix: when scored is 0, write "Atlantic 2026: no forecast had a full track yet, so the whole path cannot be read." Also drop the empty "0 of 0" row cell percent in the season table (already blank, fine).

**R3. Counts of the desk's own cells and rows sit in the lead. Severity: fix before ship (copy, house rule).** The lead says "the circle cells read 1 consistent and 13 cannot tell" and "in 220 of the 220 rows". Proposed replacement: "Read one lead time at a time against two-thirds (61.7 to 71.7 percent is our reading), every share is above two-thirds, from 68.6 to 72.6 percent, and all but the Atlantic 12 h cell read cannot tell. NHC's own yearly averages of forecast distance agree with our recount from the same files wherever the case counts are within 5 percent." The statement that all 14 shares are above 66.7 is true in the data and is not a post-hoc label.

**R4. "where the case counts match" is loose. Severity: fix before ship (copy).** Counts need only be within the larger of 2 and 5 percent, and 13 cases is the largest gap among the rows that read consistent. The same sentence leaves out the four rows that read cannot tell. Fix: use the wording in R3, and in the second-ruler paragraph say "220 of 224 rows read consistent, four read cannot tell because the case counts differ".

**R5. The Atlantic whole-path reading is on a knife edge, and the page does not show it. Severity: note.** Upper end 60.4 (desk), 60.3 (mine). Across 200 seeds the upper end runs from 59.9 to 61.1, so one seed in a hundred reads BELOW. In 100,000 resamples 3.3 percent reach 60 or more. Dropping 2010, 2017 or 2024 gives BELOW. The seed is sealed in the plan, so "cannot tell" is the rule's reading and correct. Optional sentence for the page: "The upper end of the interval is 0.4 points above the lower end of NHC's range." This is a restatement of printed numbers, not a new reading.

**R6. Cone definition choices change the share by under 3 points and are not shown. Severity: note.** The tau 0 piece adds 1.6 (Atlantic) and 2.8 (East Pacific) points. The 60 h circle (NHC's current cone page lists it) adds under 1 point for 2020 on. The page already says "starting from the forecast's first position" and "joined the way NHC describes". Optional fix: say in the whole-path note that the cone omits NHC's 60 h circle, as the graphic page does, and that dropping the first segment lowers the share by about 2 points (referee recount, out/sens_report.json). Not needed for the reading.

**R7. Frame counts attribute 46 forecasts by test order. Severity: note.** The page says "755 East Pacific forecast west of 140 W". Applying the East Pacific rule first, as the plan's frame lists it, gives 801. The desk applied the best-track tests first, so 46 west-of-140 W forecasts sit in "not a tropical cyclone at the initial time" (916 against my 872) and "no best-track point" (134 against 132). The total set aside (1,834) is identical. Fix: add "counted in the first reason that applies" to the sentence.

**R8. "Division: ATLAS" tag. Severity: note (question).** The page header links the ATLAS division, which the project describes as built-infrastructure maps. CONE is a forecast-versus-record desk. If a different division is intended, change it. I did not check the site map.

**R9. Mixed spelling. Severity: note.** "centre" in the lead and tables, "center" in NHC quotes (correct there). Pick one for our own text.

**R10. Radii file changed after the plan commit. Severity: note.** `git diff HEAD -- data/radii.json` shows only last_copy of 2026 (live fetch time). The scored radii are identical to the committed ones. No action beyond committing it with the run.

Copy cold read, no further hits: no semicolons outside quotes in the visible text, no AI statement, no named cause (the page says "This page does not say why"), headings carry no counts, interval and bootstrap disclosure present, 60 h column labelled after the data. Numbers on the page all match the recount.

## Files

Code (`/Users/heuremen/bones-forge/cone_index_referee/code/`):
- `refcore.py` readers (a-deck, HURDAT2, b-deck), haversine, projection, exact hull-of-two-discs test
- `radii_ref.py` radii from the archived HTML
- `recount.py` rows and whole-path rows
- `stats.py` cells, by-season, 2026, bootstrap
- `diff_desk.py`, `cmp_summary.py` diffs against cone.json and summary_cone.json
- `second_ruler.py` PDF parse and 224 rows
- `geom_check.py` methods B and C and boundary distances
- `sens.py`, `sens_report.py` no-tau-0 piece, 60 h circle, partial path, leave one season out, season bootstrap
- `loso_circles.py` leave one season out for circle cells
- `extra60.py` 60 h and East Pacific 2015 recounts

Outputs (`/Users/heuremen/bones-forge/cone_index_referee/out/`): `radii_ref.json`, `rows.json`, `paths.json`, `frame.json`, `cells_ref.json`, `cells_ref.txt`, `table_cells.md`, `diff_vs_desk.json`, `second_ruler_ref.json`, `geom_check.json`, `boundary_flip.json`, `sens_paths.json`, `sens_report.json`, `loso_circles.json`, `extra60.json`.
