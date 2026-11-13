# Referee report: QUAKE desk (USGS aftershock forecasts stated earlier against the aftershocks that followed)

Referee: read-only refuting pass, 10 November 2026. Nothing in `quake_index/` was edited. Everything written is under `quake_index_referee/`.
Inputs read: PLAN.md, git history (ae75b55, 6b3769), data/plan_seal.json, summary_quake.json, data/quake_rows.json.gz, quake.html (visible text inside main), quake_headline.py, build_page.py, lint_copy.py, quake_tick.py (read to know the claims, never imported or reused), the raw event list, all 253 detail files, all forecast files, all 253 catalog copies. Network: 8 ComCat count queries (user agent heuremen-quake-referee/0.1, 1.2 s apart). The product files under /product/oaf/ were not fetched (outside the allowed network).

Referee code: `code/recount.py` (own reader, haversine zone test with R = 6371 km, bisect counter on [t0, t1), Wilson at z = 1.96, own block bootstrap with Python's random, own union-find blocks, own cell rules written from PLAN.md). `code/diff.py`, `seeds.py`, `analysis.py`, `analysis2.py`, `sens.py`, `geo.py`, `geo2.py`, `later.py`, `spot.py` are the side checks. Outputs in `out/`: recount.json, rows.json, diff_vs_desk.json, analysis1.json, spot_checks.json.

## Verdict

**FIX THEN SHIP.** Every desk number reproduces from raw: all 346,576 rows, every count, every outcome, every cell share, the gates and the sealed plan. One cell outcome (M3, 1 month) flips with the bootstrap draw. The faults are in what the page leads with. The headline's last sentence ("Across every magnitude ... less often than stated where the stated chance was 10 percent or more") is true of the pooled bins and of M3, and is not true of M4 and above or of the one-year window. The "network" split is not the US against elsewhere split. All fixes are copy and display columns. No outcome rule, threshold or cell changes.

## 1. Recount from raw

| | Desk | Referee |
|---|---|---|
| Events / versions | 253 / 14,464 | 253 / 14,464 |
| Versions deleted / forecast not read | 17 / 2 | 17 / 2 |
| Versions parsed | 14,445 | 14,445 |
| Zones: circle / not stated | 14,304 / 141 (788 rows) | 14,304 / 141 (788 rows) |
| Blocks (100 km, 365 days, chained) | 91 | 91 (83 in the M3 headline cell) |
| Rows total / in frame | 346,576 / 238,204 | 346,576 / 238,204 |
| Out of frame (issued after window opened) | 108,372 rows, 4,514 versions, median 6.2 min, 105 over a day | identical (4,514 versions, one late window each, 105 over a day) |
| Not closed / catalog not read | 45,742 / 18 | 45,742 / 18 (run time set to the desk's 15:08:56Z; with run = catalog read time, all 45,760 read "not closed") |
| Scored rows / bins | 191,656 / 159,706 | 191,656 / 159,706 |
| Outcomes, all rows | CONSISTENT 189,908, ABOVE 1,301, BELOW 447, CANNOT_TELL 788, NOTHING_RETURNED 45,760 | identical |
| Row by row (key seq, issued, window, mag, kind) | | 0 rows on one side only, 0 outcome differences, 0 count differences, 0 frame differences |
| Headline M3, every window | 30,761 of 31,950, 749 above, 440 below, Wilson [96.07, 96.48], bootstrap [94.66, 97.78], CANNOT_TELL | identical counts, Wilson [96.07, 96.48], bootstrap [94.62, 97.73], CANNOT_TELL |
| M3 by window: 1 day | 9,627 / 9,736, ABOVE | identical, ABOVE |
| 1 week | 9,382 / 9,626, ABOVE | identical, ABOVE |
| 1 month | 8,805 / 9,179, CANNOT_TELL | identical counts. Bootstrap upper 97.47, **CONSISTENT** on my draw (see R4) |
| 1 year | 2,947 / 3,409, BELOW | identical, BELOW (bootstrap [79.2, 94.0]) |
| M4 / M5 / M6 / M7 | 31,386 / 31,830, 31,841 / 31,950, 31,945 / 31,950, 31,949 / 31,950, all ABOVE | identical, all ABOVE |
| Every magnitude, every window | 157,958 / 159,706, ABOVE | identical, ABOVE |
| Probability bins, all ten | counts and means as printed | identical occurred, scored, stated mean. Outcomes identical: 0 to 1 CONSISTENT, 1 to 5 CANNOT_TELL, 5 to 10 CONSISTENT, every bin from 10 percent up BELOW |
| 20 to 40 percent | 938 of 4,888 against 28.5 percent | 938 of 4,888 against 28.52 percent |
| Above-mainshock rows | 56 of 31,950 against 0.37 percent, CONSISTENT | identical, CONSISTENT |
| Counter gate | 604 of 655 | 604 of 655 (own counter, own zone test) |
| Brier / rounding check | 0.0264 / 159,593 of 159,706 | 0.02640 / 159,593 of 159,706 |
| First scored version per sequence, M3 | 668 of 719 | 668 of 719 |
| Network split, M3 | 20,575 of 21,315 / 10,186 of 10,635 | identical |

Bootstrap seed spread: my percentile bounds differ from the desk's by at most 0.15 points on the large cells (headline 94.62 against 94.66 lower, 97.73 against 97.78 upper) and by up to 0.7 points on thin cells (80 to 90 percent bin upper 75.1 against 75.8). Across six seeds the headline bounds ran 94.56 to 94.76 and 97.68 to 97.79, so the headline reading does not depend on the seed. The one cell that does is R4.

Spot checks against live ComCat count queries (zone circle, [t0, t1 minus 1 ms], minmagnitude, depth range where stated): 8 queries, 7 exact and 1 off by one.

| Row | Stated | Mine | ComCat |
|---|---|---|---|
| us7000quwy, 1 week, M3, p 0.9908 (high-probability miss) | range 1 to 18 | 0 | 0 |
| us6000t7zp, 1 day, M3, p 0.9971 (high-probability miss) | range 2 to 26 | 0 | 0 |
| pr2020007007 (Indios), 1 year, M3 (large ABOVE) | 263 to 485 | 1,087 | 1,087 |
| pr2020007007, 1 year, M3 (large ABOVE) | 271 to 523 | 1,094 | 1,095 |
| us7000quwy, 1 year, M3 (BELOW) | 12 to 88 | 4 | 4 |
| us6000tkt2, 1 week, M5 | 0 to 10 | 4 | 4 |
| us7000te4b, 1 month, M3 | 1 to 13 | 4 | 4 |
| ci38457511 (Ridgecrest), 1 year, M3, depth-filtered data zone | 56 to 105 | 90 | 90 |

The one-event difference sits on a 500 km zone edge and is the size expected from ComCat's ellipsoidal distance against the plan's sphere. Moving every radius by plus 0.3 percent changes 149 row counts and 15 of 159,706 outcomes. Minus 0.3 percent changes 81 counts and none.

## 2. Findings

**R1. Headline last sentence overstates (fix before ship).** The page and headline say "Across every magnitude, at least one earthquake happened less often than stated where the stated chance was 10 percent or more." The pooled bins do read BELOW (5,558 of 17,882, 31.1 percent against 41.9 stated). Split, from the same rows (my rule, seed 1):

- By magnitude. M3 alone: every bin from 10 percent up reads BELOW (3,780 of 12,491, 30.3 against 44.5 stated). M4 and above: every bin from 10 percent up reads CANNOT_TELL, and pooled 1,778 of 5,391, 33.0 against 35.6 stated, CANNOT_TELL. M4 alone reads BELOW only at 60 to 80. M5 reads BELOW at 1 to 5 and 5 to 10, ABOVE at 40 to 60 (63.4 against 48.9, 14 blocks).
- By window, 10 percent and up pooled. 1 day 23.8 against 36.1 BELOW. 1 week 21.0 against 36.8 BELOW. 1 month 23.7 against 39.6 BELOW. **1 year 51.6 against 50.7, CANNOT_TELL.** One-year bins from 10 to 90 percent are all CANNOT_TELL, and its low bins sit above the stated values (0 to 1 percent: 1.3 against 0.2, 5 to 10: 12.5 against 7.2).
- So the pooled statement is carried by M3 and by windows from one day to one month. The one-year window leans the other way, which the pooled bins hide.
- Fix: the headline names where it holds ("for M3, and for windows of a day to a month") and says M4 and above and the one-year window read cannot tell. Add a labelled display table of the 10-percent-and-up reading by magnitude and by window (out/recount.json holds it). Drop "Across every magnitude" (it reads as each magnitude). quake_headline.py builds the sentence only from pooled bins, so the builder needs the split input.

**R2. The "network" split is not a US against elsewhere split (fix before ship).** The page splits M3 by USGS national network against regional network. Events outside the US are all located by net us (20 events by my title match: Kamchatka, Indonesia, Panama, Venezuela, Colombia, Vanuatu, Myanmar, Cuba, Afghanistan, offshore Canada, Micronesia), so the national-network row mixes US and non-US events and the reader cannot see where the non-US ones fall. The plan's "described" item is exactly the net split, so the desk followed the plan. A labelled display row with no cause would settle it:

| M3 and 10-percent-and-up | Rows | Blocks | Reading |
|---|---|---|---|
| Cover, US and territories | 29,929, 97.0 percent inside | 69 | ABOVE (1 day, 1 week, 1 month ABOVE, 1 year BELOW 87.2) |
| Cover, elsewhere (19 sequences with rows) | 2,021, 85.3 percent inside, [42.9, 96.2] | 14 | CANNOT_TELL |
| At least one, 10 percent and up, US and territories | 15,815, 29.2 against 39.5 | 66 | BELOW (M3 alone BELOW, M4 and above CANNOT_TELL) |
| At least one, 10 percent and up, elsewhere | 2,067, 45.4 against 60.0, [20.4, 73.8] | 11 | CANNOT_TELL |

Non-US events do not drive the BELOW readings (they hold under US-only). They do dominate the "farthest outside" table: 7 of its first 15 rows are non-US BELOW rows. By the user's rule the page names no cause, so only the split needs adding. Titles were matched by country name, so the list is my own approximation and is in code/geo.py.

**R3. "Sequences" column is not the independence unit (fix before ship).** Every table's last column prints 211 (events). The bootstrap resamples 83 blocks (91 over all events), and the rule text says "Fewer than 10 separate sequences is cannot tell" where the plan's rule is 10 blocks. The headline says "resamples whole sequences". Fix: print blocks (the summary has `blocks`), say blocks or "groups of nearby sequences" in the rule line. Block counts by probability bin, low to high: 83, 83, 81, 77, 74, 58, 46, 37, 32, 21. The 99 to 100 bin and the M4-and-above bins from 80 percent up (11 to 16 blocks) are thin, and the page should show the number so a reader can see it.

**R4. M3 one-month reading flips with the draw (note).** The one-month cell upper bound sits on the 97.5 percent line: across 41 seeds the bound ran 97.38 to 97.59, 19 draws CONSISTENT and 22 CANNOT_TELL. With 20,000 resamples the bound is 97.52 (CANNOT_TELL). The sealed seed (20261110) gives CANNOT_TELL in the desk's draw and CONSISTENT in mine. The sealed reading stands as the plan's reading and the page prints cannot tell. Nothing to change in the number. Do not lean on this cell in copy. No other cell flips: headline 20 of 20 seeds CANNOT_TELL (lower 94.5 to 94.8 against 95, upper 97.6 to 97.8 against 97.5), M4, 1 day, 1 week ABOVE and 1 year BELOW 20 of 20.

**R5. Reading "above" for M5 to M7 is mostly range 0 to 0 rows (fix before ship, display only).** Rows whose range is exactly 0 to 0: M3 12,819 of 31,950 (40.1 percent, 98.2 percent inside), M4 22,884 of 31,830 (71.9), M5 29,352 of 31,950 (91.9), M6 31,499 (98.6), M7 31,836 (99.6). Without those rows: M3 18,171 of 19,131 inside, 95.0 percent, [91.8, 97.1] CANNOT_TELL. M4 8,721 of 8,946, 97.5 percent, ABOVE. M5 2,573 of 2,598, 99.0, ABOVE. M6 451 of 451 (16 blocks). M7 113 of 114 (8 blocks, CANNOT_TELL). All magnitudes together 30,045 of 31,256, 96.1 percent, CANNOT_TELL. The page prints the 0-to-0 count only for the first cell. The summary already holds `range_zero_zero` for every cell, so adding that column to the cover table costs nothing. The M3 headline is not inflated by it much (the nonzero-range share is 95.0), but the "every magnitude, every window" ABOVE (98.9) is.

**R6. The frame exclusion moves the level, not the direction (note).** 108,372 rows were out of frame (versions that entered ComCat after their window opened, median 6.2 minutes, 105 over a day). 14,382 of them are M3 rows that would otherwise score. Scoring them anyway, M3 inside is 44,154 of 46,332 (95.3 percent) against 96.3 in frame, and the out-of-frame rows alone read 93.1 percent. The 10-percent-and-up share becomes 30.6 against 46.3 stated. Direction and sign are unchanged. The plan fixed this rule and the page counts the rows, so no fix. Intervals for the combined set were not recomputed.

**R7. "Public" is measured by updateTime, not by index time (note).** ComCat's `indexTime` is later than `updateTime` by a median of 4.1 s, p99 6,166 s, and for a few versions by months. 985 of 159,706 scored bin rows (0.6 percent, 221 of them M3, 540 more than a day) come from versions indexed after their window opened. Without them the M3 share is 30,585 of 31,729, 96.4 percent. The plan names updateTime and the rule is applied with the right field. Suggest the page says "stamped before the window opened" in place of "public before".

**R8. Plan seal holds (note, no fix).** PLAN.md has one commit (ae75b55, 09:25:17 -05:00), its SHA-256 equals plan_seal.json (296dae27...) and `git diff ae75b55 -- PLAN.md` is empty. The first comparison is 14:58:35Z (09:58:35 -05:00), 33 minutes after the seal. The first catalog file was written at 09:59:51 and there is no earlier catalog file (the scout folder at 09:16 holds the event list and Ridgecrest detail and forecast files only, the stated side). Forecast files were fetched 09:23 to 09:59, the plan allows the stated side before the seal. Commit 6b3769 (10:09:31, after the first comparison) is display only: the late-version summary (`LATE`), the cover-by-magnitude list fixed to M3 to M7 (which drops the M8 cell, 76 rows, 2 blocks, CANNOT_TELL, and matches the plan text "each magnitude 3 to 7"), the farthest-miss list cut to one row per sequence, and a print format. cover_cell, rel_cell, row_cover, frame, zone and counter lines are untouched. first_run.log shows the same headline as the final run, so no outcome moved. The M8 cell and the dropped miss rows are not labelled on the page. They are small and the commit comments label them.

**R9. Zone and count checks (note).** The stated zone is the counting zone. Zone circles: 148,340 of the scored bin rows use a 10 km radius, the rest 7 to 1,077 km. Median centre offset from the mainshock 1.1 km, max 162.5 km. Every zone sits inside its catalog query circle (0 zones reach beyond it). forecast.json against forecast_data.json where both exist could not be sampled: forecast_data.json is on disk only for the 44 versions whose forecast.json states no region, and the product files are outside the allowed network. The one available pair (Ridgecrest, data-file zone then forecast.json zone 1,464 hours apart) agree to 0.0002 degrees and 60 km. The 27 data files' mainshock ID lists are subsets of the event ID lists. Depth is applied only to the 44 data-file zones. No catalog event lacks a depth. The 2 unreadable forecasts are both us6000qw60 (Kamchatka), two versions listed at 37 and 38 KB and not on disk. They cannot be checked here and touch one event with many other versions.

**R10. Boundaries, magnitude, mainshock, later larger events (note).** Time: no scored row has a catalog event exactly at t0 or t1 in ms, and counting (t0, t1] changes no outcome. Magnitude: no catalog magnitude is within 1e-6 of a threshold without being equal. 139 events carry unrounded magnitudes (for example 3.2004540). The one-decimal rounding changes 113 of 159,706 row readings, as the page says. Mainshock: all 253 catalogs hold an event sharing an ID with the mainshock's list. No excluded event falls at or after the first scored window start, so the exclusion cannot change any count. Two near-duplicate events (1.9 s and 25 s after their mainshocks) fall before the first window. Foreshocks are not in the catalog (it starts 1 s before the mainshock). A later event as large as the mainshock inside a scored window and zone touches 56 M3 rows, all one-year, 4 sequences (9 inside, 47 above, 0 below, counted as ordinary). Without them the headline is 96.42 percent and the one-year share 87.6 percent, still BELOW. Twenty-seven sequences have such a later event somewhere in the catalog circle, 22 of those later events have their own forecasts. Not a fault, and the page does not mention that windows run past a later large event.

**R11. Bootstrap and blocks (note).** Block resampling of whole sequences is the right unit for nested overlapping windows and repeated versions, since each block's rows enter as sums. The reading is not driven by one block, with one exception. Top blocks hold 17.1 percent (us6000u4q4), 11.9 and 8.6 percent of M3 rows, the top five 47 percent. Dropping any of the top five leaves the headline CANNOT_TELL except us7000thwt, whose removal gives 95.94 percent [94.29, 97.37], CONSISTENT. Dropping all five gives 96.0 percent [93.3, 97.9], CANNOT_TELL. The 10-percent-and-up BELOW reading survives dropping each of the top three blocks (share 30.0 to 33.9 against 41 to 43 stated), and 43 of the 61 blocks with at least 30 such rows have observed below stated. 83 blocks supports the headline and the bins up to 90 percent. It is thin for the cells with 8 to 16 blocks (M6 and M7 nonzero range, the M4-and-above high bins, the elsewhere split).

**R12. Page copy (note, plus R1 to R3, R5).** Every number in the cover and probability tables, the counts block and the headline matches summary_quake.json, checked as formatted strings (0 misses across the 10 cover rows and 10 bin rows). Visible main text: 0 semicolons, no AI wording, no cause wording ("This page does not say why."), no digits in any heading, four outcomes with intervals. The page title, hero and block heads have no counts. "Division: ATLAS" in the crumb: confirm QUAKE belongs under ATLAS. The farthest-outside table links each event, the M3-only choice should be said in its caption (it is). The "Described, not scored" paragraph names the net split without saying it is not US against elsewhere (R2).

**R13. Gates (note).** The counter gate reproduces exactly (604 of 655) with my own counter and zone test, so the zone, time and mainshock handling is confirmed from the issued-time side as well.

## 3. Fixes list

1. Headline (blocks nothing, fix before ship). Replace the last sentence of quake_headline.py. Say where the 10-percent-and-up shortfall holds (M3, and windows of one day to one month) and that M4 and above and the one-year window read cannot tell. Drop "Across every magnitude". Add a labelled display table: stated-chance bins read for M3, M4 and above, and each window (R1).
2. Add a US and territories against elsewhere row to Described, not scored, for the M3 cover cell and the 10-percent-and-up cell, no cause named, and say the national/regional network split does not separate them (R2).
3. Print blocks instead of events in the last column and fix the rule line to "10 separate groups of nearby sequences" (R3). Show block count on the bin and cover rows.
4. Add the range 0 to 0 count as a column to the cover table for every cell, and the share without those rows as a described row for M3 to M7 (R5).
5. Change "public before the window opened" to "stamped before" and add one line that 985 scored rows came from versions indexed after their window opened (R7). Optional.
6. Add one line that scoring the out-of-frame versions would give 95.3 percent for M3 (R6). Optional.
7. Do not describe the one-month M3 reading beyond "cannot tell" (R4). Confirm "Division: ATLAS" (R12).
8. Ship through the usual pipeline after 1 to 4. No outcome, threshold, cell or seed changes are needed.
