# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-10 10:30 QUAKE desk first read: USGS aftershock forecasts (every archived oaf version) against ComCat counts in the zone each version states, range cells against the stated 95 percent and probability bins, Wilson and sequence-block bootstrap
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: PLAN.md committed ae75b55 at 09:25:17 -05:00 (sha256 296dae27, data/plan_seal.json), first comparison 14:58:35Z, plan file unchanged since. Same quantity both sides: the number of ComCat earthquakes at or above the bin magnitude in the stated zone and window. The none is the counter gate: USGS's own observation counts before each forecast against our count for the same zone and span, 604 of 655 Sequence Specific versions agree within the larger of 2 and 20 percent. Drops by reason: 108,372 rows issued after the window opened (4,514 of 14,445 parsed versions, median 6.2 minutes late), 45,742 rows window not closed, 18 rows catalog not read, 788 rows zone not stated, 17 versions deleted, 2 versions whose forecast file does not parse. None of the drop rules reads a count
- II: holds: every range cell prints inside, above the range and below the range apart (M3 every window: 30,761 inside, 749 above, 440 below of 31,950). Probability cells print rows that saw at least one beside the mean stated chance. Repeat floor: the counter gate. No chance figure is compared with a count of misses
- III: holds: misses keep their side and are dated. The row farthest outside its range per event is listed with version date, window, stated chance, range and count
- V: holds: plan ruler is the union of the 95% Wilson interval and the 2,000-resample sequence-block bootstrap (seed 20261110, blocks of mainshocks within 100 km and 365 days, 91 blocks, 83 with scored M3 rows). Second ruler, Wilson alone, is printed. It would read the M3 every-window cell ABOVE (96.07 to 96.48) where the union reads CANNOT_TELL (94.66 to 97.78). The plan ruler decides. Magnitudes rounded to one decimal keep the same range reading in 159,593 of 159,706 rows
- VI: holds: four outcomes kept, both alternatives stated in the plan. Range cells: M3 every window CANNOT_TELL (30,761 of 31,950, 94.7 to 97.8 percent), M3 one day ABOVE (9,627 of 9,736, 98.0 to 99.4), one week ABOVE (9,382 of 9,626, 96.0 to 98.4), one month CANNOT_TELL (8,805 of 9,179, 94.0 to 97.6), one year BELOW (2,947 of 3,409, 79.2 to 94.2). M4 ABOVE (31,386 of 31,830), M5 ABOVE (31,841 of 31,950), M6 ABOVE (31,945 of 31,950), M7 ABOVE (31,949 of 31,950). Probability bins: 0 to 1 percent CONSISTENT (289 of 118,077 against 0.11), 1 to 5 CANNOT_TELL (576 of 17,366 against 2.42), 5 to 10 CONSISTENT (431 of 6,381 against 7.14), 10 to 20 BELOW (593 of 5,635 against 14.36), 20 to 40 BELOW (938 of 4,888 against 28.52), 40 to 60 BELOW (904 of 2,684 against 49.34), 60 to 80 BELOW (789 of 1,854 against 69.52), 80 to 90 BELOW (467 of 746 against 84.93), 90 to 99 BELOW (636 of 816 against 95.19), 99 to 100 BELOW (1,231 of 1,259 against 99.90). As large as the mainshock CONSISTENT (56 of 31,950 against 0.37)
- R: holds: counts read from summary_quake.json and data/quake_rows.json.gz of this run. One count read against ComCat directly: Ridgecrest version 2019-09-14, week window 2019-09-14 04:00 to 09-21 04:00, 60 km circle, M3 and above: the count service gives 0, the desk 0 (stated chance 99.41 percent, range 2 to 11). Reader gate rows in data/known_good_rows.json (three forecast files, raw text equals parsed)
- P1: holds: the USGS sentences in PLAN.md and the page were copied from earthquake.usgs.gov/data/oaf/overview.php, background.php and schedule.php fetched 10 Nov 2026
- P2: holds: page names the product (oaf), the service, every archived version, and its figures live in summary_quake.json, with every row in data/quake_rows.json.gz
- P3: holds: "95% confidence range", "probability" and the window labels as the USGS prints them. "Above the range" and "below the range" are our words, defined in the note
- P4: holds: the page says a count outside the range is a count outside the range and does not say why. The split by network is shown and not scored, with no reason given
- P5: holds: every interval is labelled Wilson or sequence, both 95%
- P6: n/a: first read
- P7: cannot tell: ledger rows, site build and tick-bus rider come with the ship entry below
- P8: holds: quake.html parsed with every tag closed, visible text read in full
- P9: holds: lint_copy.py on quake.html gives 0 hits. One USGS quotation that held the words "due to" was replaced with a plain description of what it says
- P10: holds: additions after the data, display only: the publication-lag figures (late_versions), the row farthest outside its range per event (biggest_misses), and the restriction of the by-magnitude table to the plan's magnitudes 3 to 7 (76 rows also state M8 and stay in the every-magnitude cell). No rule, threshold, cell or outcome definition changed after the plan
- O1: cannot tell: the rider is added at ship
- O2: holds: a failed fetch names its source in sources.stale and the run falls back to the last copy. A failed gate turns every scored outcome into cannot tell and keeps the original
- O3: n/a: no GPU used
- O4: holds: summary carries generated time, plan seal, and data/quake_history.jsonl gets one line per run
- O5: holds: quake_tick.py chdirs to its own folder and every path is under it. Standard library only
- O6: n/a: no GPU job

## Data access and terms (scouted 10 Nov 2026)
- USGS ComCat event service (earthquake.usgs.gov/fdsnws/event/1), keyless. USGS-authored data are in the public domain. User agent heuremen-quake/0.1 (+https://indahl.ai/quake).
- Every archived oaf version: includesuperseded=true on the event query. forecast.json per version at earthquake.usgs.gov/product/oaf/<code>/us/<updateTime>/forecast.json, inline bytes for some 2019 to 2023 versions. Bulk read with at most four connections, 0.25 s between requests per connection. The rider reads new versions one at a time.
- Zone: forecast.json model.parameters regionType circle, regionCenterLat, regionCenterLon, regionRadius (km) from 2022 on. Earlier versions: forecast_data.json parameters.aftershock_search_region with min_depth and max_depth where the version carries that file.
- Catalog: one query per mainshock, from the mainshock time, radius out to the far edge of every stated zone, 0.05 below the lowest stated magnitude, eventtype earthquake, kept gzipped in data/raw/catalog with its fetch time.

## 2026-11-10 11:00 QUAKE ship after the outside referee: referee fixes R1 to R3, R5 and R7 in the page and the headline, ledger rows for the range cells, the probability bins and the display split, page at /quake under ATLAS, feed /quake/live.json, rider publishing on the tick bus
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is unchanged from the first read (counter gate 604 of 655). The referee recount (quake_index_referee/code/recount.py, own reader, zone test, counter, Wilson and bootstrap) reproduces every row of data/quake_rows.json.gz, 0 count, outcome or frame differences in 346,576 rows. Drops by reason are the first read's
- II: holds: inside, above and below printed apart in every range cell. Every magnitude and window together: 157,958 of 159,706 inside, ABOVE
- III: holds: one row per event farthest outside its range, dated, with side
- V: holds: plan ruler unchanged. Referee bootstrap bounds differ from ours by at most 0.15 points on large cells. The one-month M3 cell (8,805 of 9,179) sits on the 97.5 line and flips with the draw (19 of 41 referee seeds CONSISTENT). The sealed seed reads CANNOT_TELL and the page says only cannot tell
- VI: holds: outcomes as in the first read. Display split added at the referee (R1), decides nothing, stated 10 percent or more: every magnitude every window BELOW (5,558 of 17,882 against 41.9), M3 BELOW (3,780 of 12,491 against 44.5), M4 and above CANNOT_TELL (1,778 of 5,391 against 35.6), one day BELOW (336 of 1,410), one week BELOW (863 of 4,106), one month BELOW (1,719 of 7,247), one year CANNOT_TELL (2,640 of 5,119 against 50.7). First version of each forecast, M3: 668 of 719 inside, described
- R: holds: referee spot checks, 8 ComCat count queries, 7 exact and 1 off by one on a 500 km zone edge
- P1: holds: USGS wording unchanged
- P2: holds: page figures from summary_quake.json of the run of 10 Nov
- P3: fixed: "public before the window opened" now reads "stamped in the catalog before the window opened" (referee R7), and the page counts the 985 scored rows from versions indexed after their window opened
- P4: fixed: the national/regional network split is said not to separate US events from events elsewhere, and a split by place (us_place.py, a text rule on the ComCat place and title) is shown, with no reason given for any difference (referee R2)
- P5: fixed: the last column now prints groups of sequences (bootstrap blocks), and the rule line says groups of nearby sequences (referee R3). The range 0 to 0 count is a column for every range cell, and M3 without those rows is described (referee R5)
- P6: fixed: the headline no longer says "Across every magnitude". It gives the pooled 10 percent and up reading and the split by magnitude and window (referee R1)
- P7: holds: ledger rows quake.cover.*, quake.prob.*, quake.prob10.*, quake.first.m3 added before the site edit, surface desk_quake
- P8: holds: quake.html rebuilt, tags closed, visible text read in full
- P9: holds: lint_copy.py 0 hits
- P10: holds: additions after the data at the referee, display only, labelled in summary_quake.json after_data_note and on the page: the split at 10 percent and up, the split by place, cells without 0 to 0 ranges, rows indexed after the window opened
- O1: holds: rider on the tick bus every 60 ticks with --publish (KV quake_live)
- O2: holds: as in the first read
- O3: n/a: no GPU used, network reads and arithmetic on the CPU
- O4: holds: data/quake_history.jsonl one line per run
- O5: holds: own folder, standard library only
- O6: n/a: no GPU job runs in this rider

## 2026-11-11 11:16 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-11T14:23:11Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-11T14:23:11Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-11T14:23:11Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9458, hi 0.9776, unit 30,622 of 31,820, outcome CANNOT_TELL, as printed: M3 and above, every window 31,820 30,622 756 442 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell 82 12,699
row-record quake.cover.m4: value 0.9857, lo 0.979, hi 0.9941, unit 31,248 of 31,700, outcome ABOVE, as printed: M4 and above 31,700 31,248 446 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,729
row-record quake.cover.m5: value 0.9965, lo 0.9936, hi 0.9987, unit 31,710 of 31,820, outcome ABOVE, as printed: M5 and above 31,820 31,710 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,212
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,815 of 31,820, outcome ABOVE, as printed: M6 and above 31,820 31,815 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,369
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,819 of 31,820, outcome ABOVE, as printed: M7 and above 31,820 31,819 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,706
row-record quake.cover.m3.day: value 0.9888, lo 0.9805, hi 0.9938, unit 9,595 of 9,704, outcome ABOVE, as printed: M3 and above, 1 day 9,704 9,595 51 58 98.9 98.7 to 99.1 98.0 to 99.4 above 82 7,029
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.9839, unit 9,346 of 9,591, outcome ABOVE, as printed: M3 and above, 1 week 9,591 9,346 136 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,700
row-record quake.cover.m3.month: value 0.9585, lo 0.9391, hi 0.9755, unit 8,764 of 9,143, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,143 8,764 230 149 95.9 95.4 to 96.2 93.9 to 97.5 cannot tell 77 1,766
row-record quake.cover.m3.year: value 0.8625, lo 0.7892, hi 0.9408, unit 2,917 of 3,382, outcome BELOW, as printed: M3 and above, 1 year 3,382 2,917 339 126 86.2 85.0 to 87.4 78.9 to 94.1 below 42 204
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,290 of 159,056, outcome ABOVE, as printed: every magnitude, every window 159,056 157,290 1,317 449 98.9 98.8 to 98.9 98.5 to 99.3 above 82 127,775
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 302 of 117,393, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,393 302 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0334, lo 0.0165, hi 0.0488, unit 579 of 17,360, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,360 579 2.4 3.3 3.1 to 3.6 1.7 to 4.9 cannot tell 82
row-record quake.prob.5_10: value 0.0678, lo 0.0459, hi 0.0913, unit 432 of 6,373, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,373 432 7.1 6.8 6.2 to 7.4 4.6 to 9.1 consistent 80
row-record quake.prob.10_20: value 0.1053, lo 0.0743, hi 0.1363, unit 595 of 5,648, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,648 595 14.4 10.5 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1923, lo 0.1499, hi 0.2358, unit 943 of 4,904, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,904 943 28.5 19.2 18.1 to 20.4 15.0 to 23.6 below 74
row-record quake.prob.40_60: value 0.3373, lo 0.2638, hi 0.4098, unit 907 of 2,689, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,689 907 49.3 33.7 32.0 to 35.5 26.4 to 41.0 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3042, hi 0.5614, unit 796 of 1,861, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,861 796 69.5 42.8 40.5 to 45.0 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.6248, lo 0.4904, hi 0.7564, unit 468 of 749, outcome BELOW, as printed: 80 to 90 percent, not including 90 749 468 84.9 62.5 59.0 to 65.9 49.0 to 75.6 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,232 of 1,260, outcome BELOW, as printed: 99 to 100 percent 1,260 1,232 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.0019, lo 0.0, hi 0.0044, unit 62 of 31,820, outcome CONSISTENT, as printed: 62 of 31,820 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.311, lo 0.2427, hi 0.3861, unit 5,577 of 17,930, outcome BELOW, as printed: every magnitude, every window 17,930 5,577 41.9 31.1 30.4 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3029, lo 0.2303, hi 0.3833, unit 3,793 of 12,523, outcome BELOW, as printed: M3 and above 12,523 3,793 44.6 30.3 29.5 to 31.1 23.0 to 38.3 below 77
row-record quake.prob10.m4up: value 0.3299, lo 0.2445, hi 0.419, unit 1,784 of 5,407, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,407 1,784 35.6 33.0 31.8 to 34.3 24.4 to 41.9 cannot tell 52
row-record quake.prob10.day: value 0.2381, lo 0.139, hi 0.3388, unit 336 of 1,411, outcome BELOW, as printed: every magnitude, 1 day 1,411 336 36.1 23.8 21.7 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.21, lo 0.1301, hi 0.3094, unit 863 of 4,109, outcome BELOW, as printed: every magnitude, 1 week 4,109 863 36.8 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2371, lo 0.164, hi 0.3265, unit 1,721 of 7,259, outcome BELOW, as printed: every magnitude, 1 month 7,259 1,721 39.6 23.7 22.7 to 24.7 16.4 to 32.6 below 73
row-record quake.prob10.year: value 0.5158, lo 0.4214, hi 0.6044, unit 2,657 of 5,151, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,151 2,657 50.7 51.6 50.2 to 52.9 42.1 to 60.4 cannot tell 41
row-record quake.first.m3: value 0.9287, lo 0.8814, hi 0.9563, unit 664 of 715, outcome CANNOT_TELL, as printed: 664 of 715 inside, 92.9 percent, with a sequence interval of 88.1 to 95.6 percent.

## 2026-11-11 11:34 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-11T16:29:29Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-11T16:29:29Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-11T16:29:29Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9458, hi 0.9776, unit 30,630 of 31,828, outcome CANNOT_TELL, as printed: M3 and above, every window 31,828 30,630 756 442 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell 82 12,703
row-record quake.cover.m4: value 0.9857, lo 0.979, hi 0.9941, unit 31,256 of 31,708, outcome ABOVE, as printed: M4 and above 31,708 31,256 446 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,736
row-record quake.cover.m5: value 0.9965, lo 0.9936, hi 0.9987, unit 31,718 of 31,828, outcome ABOVE, as printed: M5 and above 31,828 31,718 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,220
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,823 of 31,828, outcome ABOVE, as printed: M6 and above 31,828 31,823 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,377
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,827 of 31,828, outcome ABOVE, as printed: M7 and above 31,828 31,827 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,714
row-record quake.cover.m3.day: value 0.9888, lo 0.9805, hi 0.9938, unit 9,597 of 9,706, outcome ABOVE, as printed: M3 and above, 1 day 9,706 9,597 51 58 98.9 98.7 to 99.1 98.0 to 99.4 above 82 7,031
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,350 of 9,595, outcome ABOVE, as printed: M3 and above, 1 week 9,595 9,350 136 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,702
row-record quake.cover.m3.month: value 0.9586, lo 0.9391, hi 0.9755, unit 8,765 of 9,144, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,144 8,765 230 149 95.9 95.4 to 96.2 93.9 to 97.5 cannot tell 77 1,766
row-record quake.cover.m3.year: value 0.8625, lo 0.7893, hi 0.9408, unit 2,918 of 3,383, outcome BELOW, as printed: M3 and above, 1 year 3,383 2,918 339 126 86.2 85.0 to 87.4 78.9 to 94.1 below 42 204
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,330 of 159,096, outcome ABOVE, as printed: every magnitude, every window 159,096 157,330 1,317 449 98.9 98.8 to 98.9 98.5 to 99.3 above 82 127,810
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 302 of 117,428, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,428 302 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0333, lo 0.0165, hi 0.0487, unit 579 of 17,363, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,363 579 2.4 3.3 3.1 to 3.6 1.7 to 4.9 cannot tell 82
row-record quake.prob.5_10: value 0.0678, lo 0.0459, hi 0.0913, unit 432 of 6,374, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,374 432 7.1 6.8 6.2 to 7.4 4.6 to 9.1 consistent 80
row-record quake.prob.10_20: value 0.1053, lo 0.0743, hi 0.1363, unit 595 of 5,648, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,648 595 14.4 10.5 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1923, lo 0.1499, hi 0.2358, unit 943 of 4,905, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,905 943 28.5 19.2 18.1 to 20.3 15.0 to 23.6 below 74
row-record quake.prob.40_60: value 0.3373, lo 0.2638, hi 0.4098, unit 907 of 2,689, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,689 907 49.3 33.7 32.0 to 35.5 26.4 to 41.0 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3042, hi 0.5614, unit 796 of 1,861, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,861 796 69.5 42.8 40.5 to 45.0 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.6248, lo 0.4904, hi 0.7564, unit 468 of 749, outcome BELOW, as printed: 80 to 90 percent, not including 90 749 468 84.9 62.5 59.0 to 65.9 49.0 to 75.6 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,232 of 1,260, outcome BELOW, as printed: 99 to 100 percent 1,260 1,232 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.0019, lo 0.0, hi 0.0044, unit 62 of 31,828, outcome CONSISTENT, as printed: 62 of 31,828 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.311, lo 0.2427, hi 0.3861, unit 5,577 of 17,931, outcome BELOW, as printed: every magnitude, every window 17,931 5,577 41.9 31.1 30.4 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3029, lo 0.2303, hi 0.3833, unit 3,793 of 12,524, outcome BELOW, as printed: M3 and above 12,524 3,793 44.6 30.3 29.5 to 31.1 23.0 to 38.3 below 77
row-record quake.prob10.m4up: value 0.3299, lo 0.2445, hi 0.419, unit 1,784 of 5,407, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,407 1,784 35.6 33.0 31.8 to 34.3 24.4 to 41.9 cannot tell 52
row-record quake.prob10.day: value 0.2381, lo 0.139, hi 0.3388, unit 336 of 1,411, outcome BELOW, as printed: every magnitude, 1 day 1,411 336 36.1 23.8 21.7 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.21, lo 0.1301, hi 0.3094, unit 863 of 4,109, outcome BELOW, as printed: every magnitude, 1 week 4,109 863 36.8 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2371, lo 0.164, hi 0.3265, unit 1,721 of 7,259, outcome BELOW, as printed: every magnitude, 1 month 7,259 1,721 39.6 23.7 22.7 to 24.7 16.4 to 32.6 below 73
row-record quake.prob10.year: value 0.5157, lo 0.4214, hi 0.6039, unit 2,657 of 5,152, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,152 2,657 50.7 51.6 50.2 to 52.9 42.1 to 60.4 cannot tell 41
row-record quake.first.m3: value 0.9287, lo 0.8814, hi 0.9563, unit 664 of 715, outcome CANNOT_TELL, as printed: 664 of 715 inside, 92.9 percent, with a sequence interval of 88.1 to 95.6 percent.

## 2026-11-11 13:45 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-11T18:42:18Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-11T18:42:18Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-11T18:42:18Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9458, hi 0.9776, unit 30,633 of 31,831, outcome CANNOT_TELL, as printed: M3 and above, every window 31,831 30,633 756 442 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell 82 12,704
row-record quake.cover.m4: value 0.9857, lo 0.979, hi 0.9941, unit 31,259 of 31,711, outcome ABOVE, as printed: M4 and above 31,711 31,259 446 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,738
row-record quake.cover.m5: value 0.9965, lo 0.9936, hi 0.9987, unit 31,721 of 31,831, outcome ABOVE, as printed: M5 and above 31,831 31,721 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,222
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,826 of 31,831, outcome ABOVE, as printed: M6 and above 31,831 31,826 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,380
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,830 of 31,831, outcome ABOVE, as printed: M7 and above 31,831 31,830 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,717
row-record quake.cover.m3.day: value 0.9888, lo 0.9805, hi 0.9938, unit 9,598 of 9,707, outcome ABOVE, as printed: M3 and above, 1 day 9,707 9,598 51 58 98.9 98.7 to 99.1 98.0 to 99.4 above 82 7,032
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,350 of 9,595, outcome ABOVE, as printed: M3 and above, 1 week 9,595 9,350 136 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,702
row-record quake.cover.m3.month: value 0.9586, lo 0.9391, hi 0.9755, unit 8,766 of 9,145, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,145 8,766 230 149 95.9 95.4 to 96.2 93.9 to 97.5 cannot tell 77 1,766
row-record quake.cover.m3.year: value 0.8626, lo 0.7894, hi 0.9409, unit 2,919 of 3,384, outcome BELOW, as printed: M3 and above, 1 year 3,384 2,919 339 126 86.3 85.1 to 87.4 78.9 to 94.1 below 42 204
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,345 of 159,111, outcome ABOVE, as printed: every magnitude, every window 159,111 157,345 1,317 449 98.9 98.8 to 98.9 98.5 to 99.3 above 82 127,821
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 302 of 117,439, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,439 302 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0333, lo 0.0165, hi 0.0487, unit 579 of 17,364, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,364 579 2.4 3.3 3.1 to 3.6 1.7 to 4.9 cannot tell 82
row-record quake.prob.5_10: value 0.0678, lo 0.0459, hi 0.0913, unit 432 of 6,375, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,375 432 7.1 6.8 6.2 to 7.4 4.6 to 9.1 consistent 80
row-record quake.prob.10_20: value 0.1053, lo 0.0743, hi 0.1363, unit 595 of 5,648, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,648 595 14.4 10.5 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1922, lo 0.1499, hi 0.2357, unit 943 of 4,906, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,906 943 28.5 19.2 18.1 to 20.3 15.0 to 23.6 below 74
row-record quake.prob.40_60: value 0.3373, lo 0.2638, hi 0.4098, unit 907 of 2,689, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,689 907 49.3 33.7 32.0 to 35.5 26.4 to 41.0 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3042, hi 0.5614, unit 796 of 1,861, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,861 796 69.5 42.8 40.5 to 45.0 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.6253, lo 0.4914, hi 0.7568, unit 469 of 750, outcome BELOW, as printed: 80 to 90 percent, not including 90 750 469 84.9 62.5 59.0 to 65.9 49.1 to 75.7 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,232 of 1,260, outcome BELOW, as printed: 99 to 100 percent 1,260 1,232 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.0019, lo 0.0, hi 0.0044, unit 62 of 31,831, outcome CONSISTENT, as printed: 62 of 31,831 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.311, lo 0.2427, hi 0.3861, unit 5,578 of 17,933, outcome BELOW, as printed: every magnitude, every window 17,933 5,578 41.9 31.1 30.4 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3029, lo 0.2303, hi 0.3833, unit 3,794 of 12,525, outcome BELOW, as printed: M3 and above 12,525 3,794 44.6 30.3 29.5 to 31.1 23.0 to 38.3 below 77
row-record quake.prob10.m4up: value 0.3299, lo 0.2445, hi 0.419, unit 1,784 of 5,408, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,408 1,784 35.6 33.0 31.8 to 34.2 24.4 to 41.9 cannot tell 52
row-record quake.prob10.day: value 0.2381, lo 0.139, hi 0.3388, unit 336 of 1,411, outcome BELOW, as printed: every magnitude, 1 day 1,411 336 36.1 23.8 21.7 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.21, lo 0.1301, hi 0.3094, unit 863 of 4,109, outcome BELOW, as printed: every magnitude, 1 week 4,109 863 36.8 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2371, lo 0.164, hi 0.3265, unit 1,721 of 7,259, outcome BELOW, as printed: every magnitude, 1 month 7,259 1,721 39.6 23.7 22.7 to 24.7 16.4 to 32.6 below 73
row-record quake.prob10.year: value 0.5157, lo 0.4214, hi 0.6039, unit 2,658 of 5,154, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,154 2,658 50.7 51.6 50.2 to 52.9 42.1 to 60.4 cannot tell 41
row-record quake.first.m3: value 0.9287, lo 0.8814, hi 0.9563, unit 664 of 715, outcome CANNOT_TELL, as printed: 664 of 715 inside, 92.9 percent, with a sequence interval of 88.1 to 95.6 percent.

## 2026-11-11 16:15 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-11T20:53:40Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-11T20:53:40Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-11T20:53:40Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9459, hi 0.9776, unit 30,640 of 31,838, outcome CANNOT_TELL, as printed: M3 and above, every window 31,838 30,640 756 442 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell 82 12,705
row-record quake.cover.m4: value 0.9857, lo 0.979, hi 0.9941, unit 31,266 of 31,718, outcome ABOVE, as printed: M4 and above 31,718 31,266 446 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,741
row-record quake.cover.m5: value 0.9965, lo 0.9936, hi 0.9987, unit 31,728 of 31,838, outcome ABOVE, as printed: M5 and above 31,838 31,728 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,229
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,833 of 31,838, outcome ABOVE, as printed: M6 and above 31,838 31,833 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,387
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,837 of 31,838, outcome ABOVE, as printed: M7 and above 31,838 31,837 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,724
row-record quake.cover.m3.day: value 0.9888, lo 0.9805, hi 0.9938, unit 9,599 of 9,708, outcome ABOVE, as printed: M3 and above, 1 day 9,708 9,599 51 58 98.9 98.7 to 99.1 98.0 to 99.4 above 82 7,033
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,352 of 9,597, outcome ABOVE, as printed: M3 and above, 1 week 9,597 9,352 136 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,702
row-record quake.cover.m3.month: value 0.9586, lo 0.9391, hi 0.9756, unit 8,768 of 9,147, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,147 8,768 230 149 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell 77 1,766
row-record quake.cover.m3.year: value 0.8627, lo 0.7895, hi 0.9409, unit 2,921 of 3,386, outcome BELOW, as printed: M3 and above, 1 year 3,386 2,921 339 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 204
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,380 of 159,146, outcome ABOVE, as printed: every magnitude, every window 159,146 157,380 1,317 449 98.9 98.8 to 98.9 98.5 to 99.3 above 82 127,846
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 302 of 117,460, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,460 302 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0333, lo 0.0165, hi 0.0487, unit 579 of 17,370, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,370 579 2.4 3.3 3.1 to 3.6 1.7 to 4.9 cannot tell 82
row-record quake.prob.5_10: value 0.0679, lo 0.046, hi 0.0915, unit 433 of 6,376, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,376 433 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1053, lo 0.0742, hi 0.1362, unit 595 of 5,652, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,652 595 14.4 10.5 9.8 to 11.3 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1924, lo 0.1505, hi 0.2359, unit 944 of 4,907, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,907 944 28.5 19.2 18.2 to 20.4 15.0 to 23.6 below 74
row-record quake.prob.40_60: value 0.3372, lo 0.2637, hi 0.4098, unit 907 of 2,690, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,690 907 49.3 33.7 32.0 to 35.5 26.4 to 41.0 below 58
row-record quake.prob.60_80: value 0.4275, lo 0.304, hi 0.5609, unit 796 of 1,862, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,862 796 69.5 42.8 40.5 to 45.0 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.6253, lo 0.4914, hi 0.7568, unit 469 of 750, outcome BELOW, as printed: 80 to 90 percent, not including 90 750 469 84.9 62.5 59.0 to 65.9 49.1 to 75.7 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,232 of 1,260, outcome BELOW, as printed: 99 to 100 percent 1,260 1,232 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.0019, lo 0.0, hi 0.0044, unit 62 of 31,838, outcome CONSISTENT, as printed: 62 of 31,838 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.311, lo 0.2426, hi 0.3861, unit 5,579 of 17,940, outcome BELOW, as printed: every magnitude, every window 17,940 5,579 41.9 31.1 30.4 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3029, lo 0.2304, hi 0.3833, unit 3,795 of 12,530, outcome BELOW, as printed: M3 and above 12,530 3,795 44.6 30.3 29.5 to 31.1 23.0 to 38.3 below 77
row-record quake.prob10.m4up: value 0.3298, lo 0.2443, hi 0.419, unit 1,784 of 5,410, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,410 1,784 35.6 33.0 31.7 to 34.2 24.4 to 41.9 cannot tell 52
row-record quake.prob10.day: value 0.2381, lo 0.139, hi 0.3388, unit 336 of 1,411, outcome BELOW, as printed: every magnitude, 1 day 1,411 336 36.1 23.8 21.7 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2099, lo 0.13, hi 0.3092, unit 863 of 4,111, outcome BELOW, as printed: every magnitude, 1 week 4,111 863 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.237, lo 0.1639, hi 0.3264, unit 1,721 of 7,263, outcome BELOW, as printed: every magnitude, 1 month 7,263 1,721 39.6 23.7 22.7 to 24.7 16.4 to 32.6 below 73
row-record quake.prob10.year: value 0.5158, lo 0.4214, hi 0.6039, unit 2,659 of 5,155, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,155 2,659 50.7 51.6 50.2 to 52.9 42.1 to 60.4 cannot tell 41
row-record quake.first.m3: value 0.9287, lo 0.8814, hi 0.9563, unit 664 of 715, outcome CANNOT_TELL, as printed: 664 of 715 inside, 92.9 percent, with a sequence interval of 88.1 to 95.6 percent.

## 2026-11-11 19:07 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-11T23:02:40Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-11T23:02:40Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-11T23:02:40Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9459, hi 0.9776, unit 30,650 of 31,848, outcome CANNOT_TELL, as printed: M3 and above, every window 31,848 30,650 756 442 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell 82 12,710
row-record quake.cover.m4: value 0.9858, lo 0.979, hi 0.9941, unit 31,276 of 31,728, outcome ABOVE, as printed: M4 and above 31,728 31,276 446 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,749
row-record quake.cover.m5: value 0.9965, lo 0.9936, hi 0.9987, unit 31,738 of 31,848, outcome ABOVE, as printed: M5 and above 31,848 31,738 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,239
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,843 of 31,848, outcome ABOVE, as printed: M6 and above 31,848 31,843 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,397
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,847 of 31,848, outcome ABOVE, as printed: M7 and above 31,848 31,847 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,734
row-record quake.cover.m3.day: value 0.9888, lo 0.9805, hi 0.9938, unit 9,603 of 9,712, outcome ABOVE, as printed: M3 and above, 1 day 9,712 9,603 51 58 98.9 98.7 to 99.1 98.0 to 99.4 above 82 7,036
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,354 of 9,599, outcome ABOVE, as printed: M3 and above, 1 week 9,599 9,354 136 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,703
row-record quake.cover.m3.month: value 0.9586, lo 0.9391, hi 0.9756, unit 8,772 of 9,151, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,151 8,772 230 149 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell 77 1,767
row-record quake.cover.m3.year: value 0.8627, lo 0.7895, hi 0.9409, unit 2,921 of 3,386, outcome BELOW, as printed: M3 and above, 1 year 3,386 2,921 339 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 204
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,430 of 159,196, outcome ABOVE, as printed: every magnitude, every window 159,196 157,430 1,317 449 98.9 98.8 to 98.9 98.5 to 99.3 above 82 127,889
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 302 of 117,503, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,503 302 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0333, lo 0.0165, hi 0.0487, unit 579 of 17,375, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,375 579 2.4 3.3 3.1 to 3.6 1.7 to 4.9 cannot tell 82
row-record quake.prob.5_10: value 0.0679, lo 0.046, hi 0.0915, unit 433 of 6,376, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,376 433 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1053, lo 0.0742, hi 0.1362, unit 595 of 5,652, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,652 595 14.4 10.5 9.8 to 11.3 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1923, lo 0.1505, hi 0.2359, unit 944 of 4,909, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,909 944 28.5 19.2 18.1 to 20.4 15.0 to 23.6 below 74
row-record quake.prob.40_60: value 0.3372, lo 0.2637, hi 0.4098, unit 907 of 2,690, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,690 907 49.3 33.7 32.0 to 35.5 26.4 to 41.0 below 58
row-record quake.prob.60_80: value 0.4275, lo 0.304, hi 0.5609, unit 796 of 1,862, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,862 796 69.5 42.8 40.5 to 45.0 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.6253, lo 0.4914, hi 0.7568, unit 469 of 750, outcome BELOW, as printed: 80 to 90 percent, not including 90 750 469 84.9 62.5 59.0 to 65.9 49.1 to 75.7 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,232 of 1,260, outcome BELOW, as printed: 99 to 100 percent 1,260 1,232 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.0019, lo 0.0, hi 0.0044, unit 62 of 31,848, outcome CONSISTENT, as printed: 62 of 31,848 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3109, lo 0.2425, hi 0.386, unit 5,579 of 17,942, outcome BELOW, as printed: every magnitude, every window 17,942 5,579 41.9 31.1 30.4 to 31.8 24.2 to 38.6 below 77
row-record quake.prob10.m3: value 0.3028, lo 0.2303, hi 0.3832, unit 3,795 of 12,532, outcome BELOW, as printed: M3 and above 12,532 3,795 44.6 30.3 29.5 to 31.1 23.0 to 38.3 below 77
row-record quake.prob10.m4up: value 0.3298, lo 0.2443, hi 0.419, unit 1,784 of 5,410, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,410 1,784 35.6 33.0 31.7 to 34.2 24.4 to 41.9 cannot tell 52
row-record quake.prob10.day: value 0.2381, lo 0.139, hi 0.3388, unit 336 of 1,411, outcome BELOW, as printed: every magnitude, 1 day 1,411 336 36.1 23.8 21.7 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2099, lo 0.13, hi 0.3092, unit 863 of 4,111, outcome BELOW, as printed: every magnitude, 1 week 4,111 863 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2369, lo 0.1638, hi 0.3263, unit 1,721 of 7,265, outcome BELOW, as printed: every magnitude, 1 month 7,265 1,721 39.6 23.7 22.7 to 24.7 16.4 to 32.6 below 73
row-record quake.prob10.year: value 0.5158, lo 0.4214, hi 0.6039, unit 2,659 of 5,155, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,155 2,659 50.7 51.6 50.2 to 52.9 42.1 to 60.4 cannot tell 41
row-record quake.first.m3: value 0.9287, lo 0.8814, hi 0.9563, unit 664 of 715, outcome CANNOT_TELL, as printed: 664 of 715 inside, 92.9 percent, with a sequence interval of 88.1 to 95.6 percent.

## 2026-11-11 20:19 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-12T01:17:33Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-12T01:17:33Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-12T01:17:33Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9459, hi 0.9776, unit 30,655 of 31,853, outcome CANNOT_TELL, as printed: M3 and above, every window 31,853 30,655 756 442 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell 82 12,713
row-record quake.cover.m4: value 0.9858, lo 0.979, hi 0.9941, unit 31,281 of 31,733, outcome ABOVE, as printed: M4 and above 31,733 31,281 446 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,753
row-record quake.cover.m5: value 0.9965, lo 0.9936, hi 0.9987, unit 31,743 of 31,853, outcome ABOVE, as printed: M5 and above 31,853 31,743 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,244
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,848 of 31,853, outcome ABOVE, as printed: M6 and above 31,853 31,848 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,402
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,852 of 31,853, outcome ABOVE, as printed: M7 and above 31,853 31,852 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,739
row-record quake.cover.m3.day: value 0.9888, lo 0.9805, hi 0.9938, unit 9,606 of 9,715, outcome ABOVE, as printed: M3 and above, 1 day 9,715 9,606 51 58 98.9 98.7 to 99.1 98.0 to 99.4 above 82 7,038
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,354 of 9,599, outcome ABOVE, as printed: M3 and above, 1 week 9,599 9,354 136 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,703
row-record quake.cover.m3.month: value 0.9586, lo 0.9391, hi 0.9756, unit 8,773 of 9,152, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,152 8,773 230 149 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell 77 1,767
row-record quake.cover.m3.year: value 0.8627, lo 0.7897, hi 0.9409, unit 2,922 of 3,387, outcome BELOW, as printed: M3 and above, 1 year 3,387 2,922 339 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 205
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,455 of 159,221, outcome ABOVE, as printed: every magnitude, every window 159,221 157,455 1,317 449 98.9 98.8 to 98.9 98.5 to 99.3 above 82 127,911
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 302 of 117,523, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,523 302 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0333, lo 0.0165, hi 0.0487, unit 579 of 17,378, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,378 579 2.4 3.3 3.1 to 3.6 1.7 to 4.9 cannot tell 82
row-record quake.prob.5_10: value 0.0679, lo 0.046, hi 0.0915, unit 433 of 6,376, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,376 433 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1053, lo 0.0741, hi 0.1362, unit 595 of 5,653, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,653 595 14.4 10.5 9.8 to 11.3 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1923, lo 0.1504, hi 0.2359, unit 944 of 4,910, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,910 944 28.5 19.2 18.1 to 20.3 15.0 to 23.6 below 74
row-record quake.prob.40_60: value 0.3372, lo 0.2637, hi 0.4098, unit 907 of 2,690, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,690 907 49.3 33.7 32.0 to 35.5 26.4 to 41.0 below 58
row-record quake.prob.60_80: value 0.4275, lo 0.304, hi 0.5609, unit 796 of 1,862, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,862 796 69.5 42.8 40.5 to 45.0 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.6253, lo 0.4914, hi 0.7568, unit 469 of 750, outcome BELOW, as printed: 80 to 90 percent, not including 90 750 469 84.9 62.5 59.0 to 65.9 49.1 to 75.7 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,232 of 1,260, outcome BELOW, as printed: 99 to 100 percent 1,260 1,232 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.0019, lo 0.0, hi 0.0044, unit 62 of 31,853, outcome CONSISTENT, as printed: 62 of 31,853 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3109, lo 0.2425, hi 0.386, unit 5,579 of 17,944, outcome BELOW, as printed: every magnitude, every window 17,944 5,579 41.9 31.1 30.4 to 31.8 24.2 to 38.6 below 77
row-record quake.prob10.m3: value 0.3028, lo 0.2303, hi 0.3831, unit 3,795 of 12,534, outcome BELOW, as printed: M3 and above 12,534 3,795 44.5 30.3 29.5 to 31.1 23.0 to 38.3 below 77
row-record quake.prob10.m4up: value 0.3298, lo 0.2443, hi 0.419, unit 1,784 of 5,410, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,410 1,784 35.6 33.0 31.7 to 34.2 24.4 to 41.9 cannot tell 52
row-record quake.prob10.day: value 0.238, lo 0.1389, hi 0.3388, unit 336 of 1,412, outcome BELOW, as printed: every magnitude, 1 day 1,412 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2099, lo 0.13, hi 0.3092, unit 863 of 4,111, outcome BELOW, as printed: every magnitude, 1 week 4,111 863 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2369, lo 0.1638, hi 0.3263, unit 1,721 of 7,266, outcome BELOW, as printed: every magnitude, 1 month 7,266 1,721 39.6 23.7 22.7 to 24.7 16.4 to 32.6 below 73
row-record quake.prob10.year: value 0.5158, lo 0.4214, hi 0.6039, unit 2,659 of 5,155, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,155 2,659 50.7 51.6 50.2 to 52.9 42.1 to 60.4 cannot tell 41
row-record quake.first.m3: value 0.9287, lo 0.8814, hi 0.9563, unit 664 of 715, outcome CANNOT_TELL, as printed: 664 of 715 inside, 92.9 percent, with a sequence interval of 88.1 to 95.6 percent.

## 2026-11-12 01:52 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-12T05:43:09Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-12T05:43:09Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-12T05:43:09Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9459, hi 0.9775, unit 30,662 of 31,861, outcome CANNOT_TELL, as printed: M3 and above, every window 31,861 30,662 757 442 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell 82 12,718
row-record quake.cover.m4: value 0.9857, lo 0.9789, hi 0.9939, unit 31,287 of 31,741, outcome ABOVE, as printed: M4 and above 31,741 31,287 448 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,758
row-record quake.cover.m5: value 0.9965, lo 0.9936, hi 0.9987, unit 31,751 of 31,861, outcome ABOVE, as printed: M5 and above 31,861 31,751 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,252
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,856 of 31,861, outcome ABOVE, as printed: M6 and above 31,861 31,856 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,410
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,860 of 31,861, outcome ABOVE, as printed: M7 and above 31,861 31,860 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,747
row-record quake.cover.m3.day: value 0.9887, lo 0.9803, hi 0.9937, unit 9,607 of 9,717, outcome ABOVE, as printed: M3 and above, 1 day 9,717 9,607 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,040
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,355 of 9,600, outcome ABOVE, as printed: M3 and above, 1 week 9,600 9,355 136 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,704
row-record quake.cover.m3.month: value 0.9586, lo 0.9392, hi 0.9756, unit 8,778 of 9,157, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,157 8,778 230 149 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell 77 1,769
row-record quake.cover.m3.year: value 0.8627, lo 0.7897, hi 0.9409, unit 2,922 of 3,387, outcome BELOW, as printed: M3 and above, 1 year 3,387 2,922 339 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 205
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,492 of 159,261, outcome ABOVE, as printed: every magnitude, every window 159,261 157,492 1,320 449 98.9 98.8 to 98.9 98.5 to 99.3 above 82 127,945
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 303 of 117,555, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,555 303 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0336, lo 0.0169, hi 0.0487, unit 584 of 17,381, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,381 584 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell 82
row-record quake.prob.5_10: value 0.0681, lo 0.0463, hi 0.0916, unit 434 of 6,377, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,377 434 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1052, lo 0.0741, hi 0.1362, unit 595 of 5,654, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,654 595 14.4 10.5 9.8 to 11.3 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1928, lo 0.151, hi 0.2364, unit 947 of 4,911, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,911 947 28.5 19.3 18.2 to 20.4 15.1 to 23.6 below 74
row-record quake.prob.40_60: value 0.337, lo 0.2637, hi 0.4095, unit 907 of 2,691, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,691 907 49.3 33.7 31.9 to 35.5 26.4 to 40.9 below 58
row-record quake.prob.60_80: value 0.4273, lo 0.3037, hi 0.5606, unit 796 of 1,863, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,863 796 69.5 42.7 40.5 to 45.0 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.6253, lo 0.4914, hi 0.7568, unit 469 of 750, outcome BELOW, as printed: 80 to 90 percent, not including 90 750 469 84.9 62.5 59.0 to 65.9 49.1 to 75.7 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,232 of 1,260, outcome BELOW, as printed: 99 to 100 percent 1,260 1,232 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.0019, lo 0.0, hi 0.0044, unit 62 of 31,861, outcome CONSISTENT, as printed: 62 of 31,861 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.311, lo 0.2425, hi 0.3861, unit 5,582 of 17,948, outcome BELOW, as printed: every magnitude, every window 17,948 5,582 41.9 31.1 30.4 to 31.8 24.2 to 38.6 below 77
row-record quake.prob10.m3: value 0.3029, lo 0.2302, hi 0.3833, unit 3,798 of 12,537, outcome BELOW, as printed: M3 and above 12,537 3,798 44.5 30.3 29.5 to 31.1 23.0 to 38.3 below 77
row-record quake.prob10.m4up: value 0.3297, lo 0.2443, hi 0.4189, unit 1,784 of 5,411, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,411 1,784 35.6 33.0 31.7 to 34.2 24.4 to 41.9 cannot tell 52
row-record quake.prob10.day: value 0.238, lo 0.1389, hi 0.3388, unit 336 of 1,412, outcome BELOW, as printed: every magnitude, 1 day 1,412 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2099, lo 0.13, hi 0.3092, unit 863 of 4,111, outcome BELOW, as printed: every magnitude, 1 week 4,111 863 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2371, lo 0.1643, hi 0.3265, unit 1,724 of 7,270, outcome BELOW, as printed: every magnitude, 1 month 7,270 1,724 39.6 23.7 22.8 to 24.7 16.4 to 32.6 below 73
row-record quake.prob10.year: value 0.5158, lo 0.4214, hi 0.6039, unit 2,659 of 5,155, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,155 2,659 50.7 51.6 50.2 to 52.9 42.1 to 60.4 cannot tell 41
row-record quake.first.m3: value 0.9287, lo 0.8814, hi 0.9563, unit 664 of 715, outcome CANNOT_TELL, as printed: 664 of 715 inside, 92.9 percent, with a sequence interval of 88.1 to 95.6 percent.

## 2026-11-12 05:17 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-12T07:53:55Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-12T07:53:55Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-12T07:53:55Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9459, hi 0.9775, unit 30,664 of 31,863, outcome CANNOT_TELL, as printed: M3 and above, every window 31,863 30,664 757 442 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell 82 12,719
row-record quake.cover.m4: value 0.9857, lo 0.9789, hi 0.9939, unit 31,289 of 31,743, outcome ABOVE, as printed: M4 and above 31,743 31,289 448 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,760
row-record quake.cover.m5: value 0.9965, lo 0.9936, hi 0.9987, unit 31,753 of 31,863, outcome ABOVE, as printed: M5 and above 31,863 31,753 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,254
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,858 of 31,863, outcome ABOVE, as printed: M6 and above 31,863 31,858 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,412
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,862 of 31,863, outcome ABOVE, as printed: M7 and above 31,863 31,862 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,749
row-record quake.cover.m3.day: value 0.9887, lo 0.9803, hi 0.9937, unit 9,608 of 9,718, outcome ABOVE, as printed: M3 and above, 1 day 9,718 9,608 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,041
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,356 of 9,601, outcome ABOVE, as printed: M3 and above, 1 week 9,601 9,356 136 109 97.5 97.1 to 97.8 96.0 to 98.4 above 82 3,704
row-record quake.cover.m3.month: value 0.9586, lo 0.9392, hi 0.9756, unit 8,778 of 9,157, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,157 8,778 230 149 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell 77 1,769
row-record quake.cover.m3.year: value 0.8627, lo 0.7897, hi 0.9409, unit 2,922 of 3,387, outcome BELOW, as printed: M3 and above, 1 year 3,387 2,922 339 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 205
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,502 of 159,271, outcome ABOVE, as printed: every magnitude, every window 159,271 157,502 1,320 449 98.9 98.8 to 98.9 98.5 to 99.3 above 82 127,954
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 303 of 117,564, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,564 303 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0336, lo 0.0169, hi 0.0487, unit 584 of 17,381, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,381 584 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell 82
row-record quake.prob.5_10: value 0.068, lo 0.0463, hi 0.0916, unit 434 of 6,378, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,378 434 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1052, lo 0.0741, hi 0.1362, unit 595 of 5,654, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,654 595 14.4 10.5 9.8 to 11.3 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1928, lo 0.151, hi 0.2364, unit 947 of 4,911, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,911 947 28.5 19.3 18.2 to 20.4 15.1 to 23.6 below 74
row-record quake.prob.40_60: value 0.337, lo 0.2637, hi 0.4095, unit 907 of 2,691, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,691 907 49.3 33.7 31.9 to 35.5 26.4 to 40.9 below 58
row-record quake.prob.60_80: value 0.4273, lo 0.3037, hi 0.5606, unit 796 of 1,863, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,863 796 69.5 42.7 40.5 to 45.0 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.6253, lo 0.4914, hi 0.7568, unit 469 of 750, outcome BELOW, as printed: 80 to 90 percent, not including 90 750 469 84.9 62.5 59.0 to 65.9 49.1 to 75.7 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,232 of 1,260, outcome BELOW, as printed: 99 to 100 percent 1,260 1,232 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.0019, lo 0.0, hi 0.0044, unit 62 of 31,863, outcome CONSISTENT, as printed: 62 of 31,863 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.311, lo 0.2425, hi 0.3861, unit 5,582 of 17,948, outcome BELOW, as printed: every magnitude, every window 17,948 5,582 41.9 31.1 30.4 to 31.8 24.2 to 38.6 below 77
row-record quake.prob10.m3: value 0.3029, lo 0.2302, hi 0.3833, unit 3,798 of 12,537, outcome BELOW, as printed: M3 and above 12,537 3,798 44.5 30.3 29.5 to 31.1 23.0 to 38.3 below 77
row-record quake.prob10.m4up: value 0.3297, lo 0.2443, hi 0.4189, unit 1,784 of 5,411, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,411 1,784 35.6 33.0 31.7 to 34.2 24.4 to 41.9 cannot tell 52
row-record quake.prob10.day: value 0.238, lo 0.1389, hi 0.3388, unit 336 of 1,412, outcome BELOW, as printed: every magnitude, 1 day 1,412 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2099, lo 0.13, hi 0.3092, unit 863 of 4,111, outcome BELOW, as printed: every magnitude, 1 week 4,111 863 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2371, lo 0.1643, hi 0.3265, unit 1,724 of 7,270, outcome BELOW, as printed: every magnitude, 1 month 7,270 1,724 39.6 23.7 22.8 to 24.7 16.4 to 32.6 below 73
row-record quake.prob10.year: value 0.5158, lo 0.4214, hi 0.6039, unit 2,659 of 5,155, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,155 2,659 50.7 51.6 50.2 to 52.9 42.1 to 60.4 cannot tell 41
row-record quake.first.m3: value 0.9287, lo 0.8814, hi 0.9563, unit 664 of 715, outcome CANNOT_TELL, as printed: 664 of 715 inside, 92.9 percent, with a sequence interval of 88.1 to 95.6 percent.

## 2026-11-12 05:36 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-12T10:24:43Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-12T10:24:43Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-12T10:24:43Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9459, hi 0.9776, unit 30,673 of 31,872, outcome CANNOT_TELL, as printed: M3 and above, every window 31,872 30,673 757 442 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell 82 12,725
row-record quake.cover.m4: value 0.9857, lo 0.9789, hi 0.9939, unit 31,298 of 31,752, outcome ABOVE, as printed: M4 and above 31,752 31,298 448 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,766
row-record quake.cover.m5: value 0.9965, lo 0.9936, hi 0.9987, unit 31,762 of 31,872, outcome ABOVE, as printed: M5 and above 31,872 31,762 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,262
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,867 of 31,872, outcome ABOVE, as printed: M6 and above 31,872 31,867 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,421
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,871 of 31,872, outcome ABOVE, as printed: M7 and above 31,872 31,871 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,758
row-record quake.cover.m3.day: value 0.9887, lo 0.9803, hi 0.9937, unit 9,611 of 9,721, outcome ABOVE, as printed: M3 and above, 1 day 9,721 9,611 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,044
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,359 of 9,604, outcome ABOVE, as printed: M3 and above, 1 week 9,604 9,359 136 109 97.5 97.1 to 97.8 96.0 to 98.4 above 82 3,707
row-record quake.cover.m3.month: value 0.9586, lo 0.9392, hi 0.9756, unit 8,780 of 9,159, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,159 8,780 230 149 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell 77 1,769
row-record quake.cover.m3.year: value 0.8628, lo 0.7897, hi 0.9409, unit 2,923 of 3,388, outcome BELOW, as printed: M3 and above, 1 year 3,388 2,923 339 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 205
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,547 of 159,316, outcome ABOVE, as printed: every magnitude, every window 159,316 157,547 1,320 449 98.9 98.8 to 98.9 98.5 to 99.3 above 82 127,992
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 303 of 117,600, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,600 303 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0336, lo 0.017, hi 0.0487, unit 585 of 17,386, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,386 585 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell 82
row-record quake.prob.5_10: value 0.068, lo 0.0463, hi 0.0916, unit 434 of 6,378, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,378 434 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1052, lo 0.0741, hi 0.1362, unit 595 of 5,654, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,654 595 14.4 10.5 9.8 to 11.3 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1929, lo 0.1511, hi 0.2363, unit 948 of 4,914, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,914 948 28.5 19.3 18.2 to 20.4 15.1 to 23.6 below 74
row-record quake.prob.40_60: value 0.337, lo 0.2637, hi 0.4095, unit 907 of 2,691, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,691 907 49.3 33.7 31.9 to 35.5 26.4 to 40.9 below 58
row-record quake.prob.60_80: value 0.4276, lo 0.3048, hi 0.5606, unit 797 of 1,864, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,864 797 69.5 42.8 40.5 to 45.0 30.5 to 56.1 below 46
row-record quake.prob.80_90: value 0.6253, lo 0.4914, hi 0.7568, unit 469 of 750, outcome BELOW, as printed: 80 to 90 percent, not including 90 750 469 84.9 62.5 59.0 to 65.9 49.1 to 75.7 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,232 of 1,260, outcome BELOW, as printed: 99 to 100 percent 1,260 1,232 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0045, unit 63 of 31,872, outcome CONSISTENT, as printed: 63 of 31,872 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3111, lo 0.2426, hi 0.3861, unit 5,584 of 17,952, outcome BELOW, as printed: every magnitude, every window 17,952 5,584 41.9 31.1 30.4 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.303, lo 0.2303, hi 0.3831, unit 3,799 of 12,540, outcome BELOW, as printed: M3 and above 12,540 3,799 44.5 30.3 29.5 to 31.1 23.0 to 38.3 below 77
row-record quake.prob10.m4up: value 0.3298, lo 0.2444, hi 0.4189, unit 1,785 of 5,412, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,412 1,785 35.6 33.0 31.7 to 34.2 24.4 to 41.9 cannot tell 52
row-record quake.prob10.day: value 0.238, lo 0.1389, hi 0.3388, unit 336 of 1,412, outcome BELOW, as printed: every magnitude, 1 day 1,412 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2099, lo 0.13, hi 0.3092, unit 863 of 4,111, outcome BELOW, as printed: every magnitude, 1 week 4,111 863 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2371, lo 0.1642, hi 0.3264, unit 1,724 of 7,272, outcome BELOW, as printed: every magnitude, 1 month 7,272 1,724 39.6 23.7 22.7 to 24.7 16.4 to 32.6 below 73
row-record quake.prob10.year: value 0.516, lo 0.4217, hi 0.604, unit 2,661 of 5,157, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,157 2,661 50.7 51.6 50.2 to 53.0 42.2 to 60.4 cannot tell 41
row-record quake.first.m3: value 0.9287, lo 0.8814, hi 0.9563, unit 664 of 715, outcome CANNOT_TELL, as printed: 664 of 715 inside, 92.9 percent, with a sequence interval of 88.1 to 95.6 percent.

## 2026-11-12 07:54 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-12T12:30:40Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-12T12:30:40Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-12T12:30:40Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9459, hi 0.9776, unit 30,683 of 31,883, outcome CANNOT_TELL, as printed: M3 and above, every window 31,883 30,683 758 442 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell 82 12,729
row-record quake.cover.m4: value 0.9857, lo 0.9789, hi 0.9939, unit 31,309 of 31,763, outcome ABOVE, as printed: M4 and above 31,763 31,309 448 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,775
row-record quake.cover.m5: value 0.9965, lo 0.9936, hi 0.9987, unit 31,773 of 31,883, outcome ABOVE, as printed: M5 and above 31,883 31,773 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,273
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,878 of 31,883, outcome ABOVE, as printed: M6 and above 31,883 31,878 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,432
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,882 of 31,883, outcome ABOVE, as printed: M7 and above 31,883 31,882 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,769
row-record quake.cover.m3.day: value 0.9887, lo 0.9803, hi 0.9937, unit 9,611 of 9,721, outcome ABOVE, as printed: M3 and above, 1 day 9,721 9,611 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,044
row-record quake.cover.m3.week: value 0.9745, lo 0.9599, hi 0.984, unit 9,366 of 9,611, outcome ABOVE, as printed: M3 and above, 1 week 9,611 9,366 136 109 97.5 97.1 to 97.8 96.0 to 98.4 above 82 3,709
row-record quake.cover.m3.month: value 0.9586, lo 0.9392, hi 0.9756, unit 8,783 of 9,162, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,162 8,783 230 149 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell 77 1,770
row-record quake.cover.m3.year: value 0.8625, lo 0.7893, hi 0.9409, unit 2,923 of 3,389, outcome BELOW, as printed: M3 and above, 1 year 3,389 2,923 340 126 86.2 85.0 to 87.4 78.9 to 94.1 below 42 206
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,601 of 159,371, outcome ABOVE, as printed: every magnitude, every window 159,371 157,601 1,321 449 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,038
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 303 of 117,640, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,640 303 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0337, lo 0.017, hi 0.0488, unit 586 of 17,394, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,394 586 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell 82
row-record quake.prob.5_10: value 0.0682, lo 0.0464, hi 0.0916, unit 435 of 6,381, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,381 435 7.1 6.8 6.2 to 7.5 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1054, lo 0.0741, hi 0.1362, unit 596 of 5,656, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,656 596 14.4 10.5 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1929, lo 0.1511, hi 0.2363, unit 948 of 4,914, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,914 948 28.5 19.3 18.2 to 20.4 15.1 to 23.6 below 74
row-record quake.prob.40_60: value 0.3373, lo 0.2637, hi 0.4098, unit 908 of 2,692, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,692 908 49.3 33.7 32.0 to 35.5 26.4 to 41.0 below 58
row-record quake.prob.60_80: value 0.4279, lo 0.3048, hi 0.5611, unit 798 of 1,865, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,865 798 69.5 42.8 40.6 to 45.1 30.5 to 56.1 below 46
row-record quake.prob.80_90: value 0.6253, lo 0.4914, hi 0.7568, unit 469 of 750, outcome BELOW, as printed: 80 to 90 percent, not including 90 750 469 84.9 62.5 59.0 to 65.9 49.1 to 75.7 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,232 of 1,260, outcome BELOW, as printed: 99 to 100 percent 1,260 1,232 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0045, unit 63 of 31,883, outcome CONSISTENT, as printed: 63 of 31,883 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3111, lo 0.2426, hi 0.3862, unit 5,587 of 17,956, outcome BELOW, as printed: every magnitude, every window 17,956 5,587 41.9 31.1 30.4 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.303, lo 0.2304, hi 0.3832, unit 3,801 of 12,543, outcome BELOW, as printed: M3 and above 12,543 3,801 44.5 30.3 29.5 to 31.1 23.0 to 38.3 below 77
row-record quake.prob10.m4up: value 0.3299, lo 0.2448, hi 0.4189, unit 1,786 of 5,413, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,413 1,786 35.6 33.0 31.8 to 34.3 24.5 to 41.9 cannot tell 52
row-record quake.prob10.day: value 0.238, lo 0.1389, hi 0.3388, unit 336 of 1,412, outcome BELOW, as printed: every magnitude, 1 day 1,412 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2103, lo 0.1303, hi 0.3092, unit 865 of 4,114, outcome BELOW, as printed: every magnitude, 1 week 4,114 865 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2372, lo 0.1643, hi 0.3265, unit 1,725 of 7,273, outcome BELOW, as printed: every magnitude, 1 month 7,273 1,725 39.6 23.7 22.8 to 24.7 16.4 to 32.6 below 73
row-record quake.prob10.year: value 0.516, lo 0.4217, hi 0.604, unit 2,661 of 5,157, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,157 2,661 50.7 51.6 50.2 to 53.0 42.2 to 60.4 cannot tell 41
row-record quake.first.m3: value 0.9287, lo 0.8814, hi 0.9563, unit 664 of 715, outcome CANNOT_TELL, as printed: 664 of 715 inside, 92.9 percent, with a sequence interval of 88.1 to 95.6 percent.

## 2026-11-12 10:21 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-12T15:20:24Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-12T15:20:24Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-12T15:20:24Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9459, hi 0.9776, unit 30,694 of 31,894, outcome CANNOT_TELL, as printed: M3 and above, every window 31,894 30,694 758 442 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,735
row-record quake.cover.m4: value 0.9857, lo 0.9789, hi 0.9939, unit 31,319 of 31,774, outcome ABOVE, as printed: M4 and above 31,774 31,319 449 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,783
row-record quake.cover.m5: value 0.9966, lo 0.9936, hi 0.9987, unit 31,784 of 31,894, outcome ABOVE, as printed: M5 and above 31,894 31,784 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,283
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,889 of 31,894, outcome ABOVE, as printed: M6 and above 31,894 31,889 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,443
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,893 of 31,894, outcome ABOVE, as printed: M7 and above 31,894 31,893 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,780
row-record quake.cover.m3.day: value 0.9887, lo 0.9803, hi 0.9937, unit 9,615 of 9,725, outcome ABOVE, as printed: M3 and above, 1 day 9,725 9,615 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,048
row-record quake.cover.m3.week: value 0.9745, lo 0.9599, hi 0.984, unit 9,368 of 9,613, outcome ABOVE, as printed: M3 and above, 1 week 9,613 9,368 136 109 97.5 97.1 to 97.8 96.0 to 98.4 above 82 3,710
row-record quake.cover.m3.month: value 0.9586, lo 0.9392, hi 0.9756, unit 8,785 of 9,164, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,164 8,785 230 149 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,770
row-record quake.cover.m3.year: value 0.8626, lo 0.7895, hi 0.9409, unit 2,926 of 3,392, outcome BELOW, as printed: M3 and above, 1 year 3,392 2,926 340 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 207
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,655 of 159,426, outcome ABOVE, as printed: every magnitude, every window 159,426 157,655 1,322 449 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,084
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 303 of 117,680, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,680 303 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0337, lo 0.017, hi 0.0488, unit 586 of 17,402, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,402 586 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.0683, lo 0.0465, hi 0.0917, unit 436 of 6,382, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,382 436 7.1 6.8 6.2 to 7.5 4.7 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1053, lo 0.0741, hi 0.1362, unit 596 of 5,658, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,658 596 14.4 10.5 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1928, lo 0.151, hi 0.2363, unit 948 of 4,916, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,916 948 28.5 19.3 18.2 to 20.4 15.1 to 23.6 below 74
row-record quake.prob.40_60: value 0.3375, lo 0.2644, hi 0.4104, unit 909 of 2,693, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,693 909 49.3 33.8 32.0 to 35.6 26.4 to 41.0 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3043, hi 0.5611, unit 798 of 1,866, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,866 798 69.5 42.8 40.5 to 45.0 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.6253, lo 0.4914, hi 0.7568, unit 469 of 750, outcome BELOW, as printed: 80 to 90 percent, not including 90 750 469 84.9 62.5 59.0 to 65.9 49.1 to 75.7 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,232 of 1,260, outcome BELOW, as printed: 99 to 100 percent 1,260 1,232 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0045, unit 63 of 31,894, outcome CONSISTENT, as printed: 63 of 31,894 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3111, lo 0.2427, hi 0.3862, unit 5,588 of 17,962, outcome BELOW, as printed: every magnitude, every window 17,962 5,588 41.8 31.1 30.4 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.303, lo 0.2303, hi 0.3833, unit 3,802 of 12,548, outcome BELOW, as printed: M3 and above 12,548 3,802 44.5 30.3 29.5 to 31.1 23.0 to 38.3 below 77
row-record quake.prob10.m4up: value 0.3299, lo 0.2448, hi 0.4189, unit 1,786 of 5,414, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,414 1,786 35.6 33.0 31.8 to 34.2 24.5 to 41.9 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.238, lo 0.1389, hi 0.3388, unit 336 of 1,412, outcome BELOW, as printed: every magnitude, 1 day 1,412 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2102, lo 0.1303, hi 0.3092, unit 865 of 4,115, outcome BELOW, as printed: every magnitude, 1 week 4,115 865 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2373, lo 0.1644, hi 0.3267, unit 1,726 of 7,275, outcome BELOW, as printed: every magnitude, 1 month 7,275 1,726 39.6 23.7 22.8 to 24.7 16.4 to 32.7 below 73
row-record quake.prob10.year: value 0.5157, lo 0.4215, hi 0.6036, unit 2,661 of 5,160, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,160 2,661 50.7 51.6 50.2 to 52.9 42.1 to 60.4 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9287, lo 0.8814, hi 0.9563, unit 664 of 715, outcome CANNOT_TELL, as printed: 664 of 715 inside, 92.9 percent, with a sequence interval of 88.1 to 95.6 percent.

## 2026-11-12 10:22 Faults and Guards 2.0 migration: reason codes, REQ-13 line, edge convention, addendum
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, PLAN.md is not edited and its seal in data/plan_seal.json still matches, the addendum is a new file committed as 3ad3ea7 before any reading under it
- II: n/a: no repeated item, every cell keeps its own interval and the Wilson and sequence-group bootstrap intervals are unchanged
- III: holds: ABOVE and BELOW stay separate columns, every non-outcome number of summary_quake.json (value, lo, hi, scored, inside, share, intervals) compared equal in every cell before and after the code change, 0 differences
- V: holds: the rule is named in PLAN_ADDENDUM_std2.md before any reading under it, ABOVE and BELOW against the stated figure, CONSISTENT in the tolerance band with closed edges, no new tolerance invented
- VI: holds: four outcomes kept, every CANNOT_TELL carries one closed reason, the headline cell M3 and above reads CANNOT_TELL STRADDLES_EDGE and no cell changed its outcome, the both-alternatives test is not applied because the plan names no size that matters and the addendum says so
- R: holds: counts and reasons are read from summary_quake.json after re-running quake_tick.py --offline, the rule self-test passed and the kit self-test passed, headline M3 and above 30,694 of 31,894 unchanged, 788 rows NO_INTERVAL_FORMABLE for no zone stated, failed reads 45,904 NOTHING_RETURNED apart
- P1: n/a: no quotation of any source in this change
- P2: n/a: no new figure, every number keeps its source on the page
- P3: n/a: no setting labels of any source are touched by this change
- P4: holds: no cause is named, the added text says only which closed reason a CANNOT_TELL carries and what the edges are
- P5: holds: the page note says the interval is the union of the Wilson and the sequence-group interval and states the closed edges and the minimum of 30 rows and 10 groups as TOO_WIDE_TO_RESOLVE
- P6: holds: the headline line is the same sentence as before plus the reason beside cannot tell and the REQ-13 line read from the summary, no stronger than the reading
- P7: holds: no outcome moved so no ledger outcome changed, refresh_page.py run under the ledger lock refreshed the 24 quake.* rows surface text before any release, the owner ships with ship.sh
- P8: cannot tell: quake.html rebuilt by build_page.py and lint_copy.py reported 0 hits, but the page was not rendered in a browser or served because nothing is deployed from this session
- P9: holds: plain sentences without semicolons in the added page text, no count of our own things in any heading, lint_copy.py 0 hits
- P10: holds: the addendum is dated 12 Nov 2026 and written before any reading under the new rule, no rule set after the data

## 2026-11-12 11:46 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-12T16:41:40Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-12T16:41:40Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-12T16:41:40Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9459, hi 0.9776, unit 30,707 of 31,907, outcome CANNOT_TELL, as printed: M3 and above, every window 31,907 30,707 758 442 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,742
row-record quake.cover.m4: value 0.9857, lo 0.9789, hi 0.9938, unit 31,331 of 31,787, outcome ABOVE, as printed: M4 and above 31,787 31,331 450 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,791
row-record quake.cover.m5: value 0.9966, lo 0.9936, hi 0.9987, unit 31,797 of 31,907, outcome ABOVE, as printed: M5 and above 31,907 31,797 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,295
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,902 of 31,907, outcome ABOVE, as printed: M6 and above 31,907 31,902 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,456
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,906 of 31,907, outcome ABOVE, as printed: M7 and above 31,907 31,906 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,793
row-record quake.cover.m3.day: value 0.9887, lo 0.9803, hi 0.9937, unit 9,619 of 9,729, outcome ABOVE, as printed: M3 and above, 1 day 9,729 9,619 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,052
row-record quake.cover.m3.week: value 0.9745, lo 0.9599, hi 0.984, unit 9,371 of 9,616, outcome ABOVE, as printed: M3 and above, 1 week 9,616 9,371 136 109 97.5 97.1 to 97.8 96.0 to 98.4 above 82 3,712
row-record quake.cover.m3.month: value 0.9587, lo 0.9392, hi 0.9756, unit 8,788 of 9,167, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,167 8,788 230 149 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,771
row-record quake.cover.m3.year: value 0.8627, lo 0.7897, hi 0.941, unit 2,929 of 3,395, outcome BELOW, as printed: M3 and above, 1 year 3,395 2,929 340 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 207
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,719 of 159,491, outcome ABOVE, as printed: every magnitude, every window 159,491 157,719 1,323 449 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,137
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 303 of 117,731, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,731 303 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0337, lo 0.0171, hi 0.0488, unit 587 of 17,408, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,408 587 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.0683, lo 0.0465, hi 0.0917, unit 436 of 6,383, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,383 436 7.1 6.8 6.2 to 7.5 4.7 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1055, lo 0.0741, hi 0.1363, unit 597 of 5,659, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,659 597 14.4 10.5 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1929, lo 0.151, hi 0.2366, unit 949 of 4,920, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,920 949 28.5 19.3 18.2 to 20.4 15.1 to 23.7 below 74
row-record quake.prob.40_60: value 0.3378, lo 0.2644, hi 0.4109, unit 910 of 2,694, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,694 910 49.3 33.8 32.0 to 35.6 26.4 to 41.1 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3043, hi 0.5611, unit 798 of 1,866, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,866 798 69.5 42.8 40.5 to 45.0 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.6245, lo 0.4903, hi 0.7559, unit 469 of 751, outcome BELOW, as printed: 80 to 90 percent, not including 90 751 469 84.9 62.5 58.9 to 65.8 49.0 to 75.6 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,232 of 1,260, outcome BELOW, as printed: 99 to 100 percent 1,260 1,232 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0045, unit 63 of 31,907, outcome CONSISTENT, as printed: 63 of 31,907 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3111, lo 0.2427, hi 0.3863, unit 5,591 of 17,969, outcome BELOW, as printed: every magnitude, every window 17,969 5,591 41.8 31.1 30.4 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3031, lo 0.2304, hi 0.3833, unit 3,805 of 12,554, outcome BELOW, as printed: M3 and above 12,554 3,805 44.5 30.3 29.5 to 31.1 23.0 to 38.3 below 77
row-record quake.prob10.m4up: value 0.3298, lo 0.2447, hi 0.4189, unit 1,786 of 5,415, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,415 1,786 35.6 33.0 31.7 to 34.2 24.5 to 41.9 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.238, lo 0.1389, hi 0.3388, unit 336 of 1,412, outcome BELOW, as printed: every magnitude, 1 day 1,412 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2102, lo 0.1303, hi 0.3091, unit 865 of 4,116, outcome BELOW, as printed: every magnitude, 1 week 4,116 865 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2373, lo 0.1645, hi 0.3265, unit 1,727 of 7,278, outcome BELOW, as printed: every magnitude, 1 month 7,278 1,727 39.6 23.7 22.8 to 24.7 16.4 to 32.6 below 73
row-record quake.prob10.year: value 0.5158, lo 0.4215, hi 0.6036, unit 2,663 of 5,163, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,163 2,663 50.7 51.6 50.2 to 52.9 42.1 to 60.4 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9287, lo 0.8814, hi 0.9563, unit 664 of 715, outcome CANNOT_TELL, as printed: 664 of 715 inside, 92.9 percent, with a sequence interval of 88.1 to 95.6 percent.

## 2026-11-12 17:09 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-12T21:00:57Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-12T21:00:57Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-12T21:00:57Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9623, lo 0.9459, hi 0.9775, unit 30,721 of 31,923, outcome CANNOT_TELL, as printed: M3 and above, every window 31,923 30,721 759 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,746
row-record quake.cover.m4: value 0.9857, lo 0.9789, hi 0.9938, unit 31,347 of 31,803, outcome ABOVE, as printed: M4 and above 31,803 31,347 450 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,802
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,813 of 31,923, outcome ABOVE, as printed: M5 and above 31,923 31,813 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,308
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,918 of 31,923, outcome ABOVE, as printed: M6 and above 31,923 31,918 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,470
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,922 of 31,923, outcome ABOVE, as printed: M7 and above 31,923 31,922 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,809
row-record quake.cover.m3.day: value 0.9887, lo 0.9804, hi 0.9937, unit 9,621 of 9,731, outcome ABOVE, as printed: M3 and above, 1 day 9,731 9,621 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,052
row-record quake.cover.m3.week: value 0.9744, lo 0.9598, hi 0.9839, unit 9,377 of 9,623, outcome ABOVE, as printed: M3 and above, 1 week 9,623 9,377 137 109 97.4 97.1 to 97.7 96.0 to 98.4 above 82 3,715
row-record quake.cover.m3.month: value 0.9586, lo 0.9392, hi 0.9756, unit 8,791 of 9,171, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,171 8,791 230 150 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,772
row-record quake.cover.m3.year: value 0.8629, lo 0.7898, hi 0.9411, unit 2,932 of 3,398, outcome BELOW, as printed: M3 and above, 1 year 3,398 2,932 340 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 207
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,797 of 159,571, outcome ABOVE, as printed: every magnitude, every window 159,571 157,797 1,324 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,195
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 304 of 117,786, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,786 304 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0337, lo 0.0171, hi 0.0488, unit 587 of 17,417, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,417 587 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.0683, lo 0.0465, hi 0.0917, unit 436 of 6,388, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,388 436 7.1 6.8 6.2 to 7.5 4.7 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1055, lo 0.0741, hi 0.1363, unit 597 of 5,660, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,660 597 14.4 10.5 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.193, lo 0.1512, hi 0.2366, unit 950 of 4,922, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,922 950 28.5 19.3 18.2 to 20.4 15.1 to 23.7 below 74
row-record quake.prob.40_60: value 0.3379, lo 0.2646, hi 0.4109, unit 911 of 2,696, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,696 911 49.3 33.8 32.0 to 35.6 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.428, lo 0.3045, hi 0.5613, unit 799 of 1,867, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,867 799 69.5 42.8 40.6 to 45.1 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,236 of 1,264, outcome BELOW, as printed: 99 to 100 percent 1,264 1,236 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0045, unit 63 of 31,923, outcome CONSISTENT, as printed: 63 of 31,923 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3114, lo 0.2429, hi 0.3864, unit 5,599 of 17,980, outcome BELOW, as printed: every magnitude, every window 17,980 5,599 41.9 31.1 30.5 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3033, lo 0.2306, hi 0.3836, unit 3,809 of 12,559, outcome BELOW, as printed: M3 and above 12,559 3,809 44.6 30.3 29.5 to 31.1 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3302, lo 0.2447, hi 0.4194, unit 1,790 of 5,421, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,421 1,790 35.6 33.0 31.8 to 34.3 24.5 to 41.9 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.238, lo 0.1389, hi 0.3388, unit 336 of 1,412, outcome BELOW, as printed: every magnitude, 1 day 1,412 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2103, lo 0.1303, hi 0.3091, unit 866 of 4,117, outcome BELOW, as printed: every magnitude, 1 week 4,117 866 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2376, lo 0.1647, hi 0.3268, unit 1,730 of 7,282, outcome BELOW, as printed: every magnitude, 1 month 7,282 1,730 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.516, lo 0.4217, hi 0.6037, unit 2,667 of 5,169, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,169 2,667 50.7 51.6 50.2 to 53.0 42.2 to 60.4 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9287, lo 0.8814, hi 0.9563, unit 664 of 715, outcome CANNOT_TELL, as printed: 664 of 715 inside, 92.9 percent, with a sequence interval of 88.1 to 95.6 percent.

## 2026-11-12 21:19 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T01:15:54Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-13T01:15:54Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-13T01:15:54Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.946, hi 0.9776, unit 30,732 of 31,933, outcome CANNOT_TELL, as printed: M3 and above, every window 31,933 30,732 758 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,749
row-record quake.cover.m4: value 0.9857, lo 0.9789, hi 0.9938, unit 31,357 of 31,813, outcome ABOVE, as printed: M4 and above 31,813 31,357 450 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,810
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,823 of 31,933, outcome ABOVE, as printed: M5 and above 31,933 31,823 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,318
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,928 of 31,933, outcome ABOVE, as printed: M6 and above 31,933 31,928 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,480
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,932 of 31,933, outcome ABOVE, as printed: M7 and above 31,933 31,932 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,819
row-record quake.cover.m3.day: value 0.9887, lo 0.9804, hi 0.9937, unit 9,624 of 9,734, outcome ABOVE, as printed: M3 and above, 1 day 9,734 9,624 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,054
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.9841, unit 9,381 of 9,626, outcome ABOVE, as printed: M3 and above, 1 week 9,626 9,381 136 109 97.5 97.1 to 97.8 96.0 to 98.4 above 82 3,716
row-record quake.cover.m3.month: value 0.9586, lo 0.9392, hi 0.9756, unit 8,795 of 9,175, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,175 8,795 230 150 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,772
row-record quake.cover.m3.year: value 0.8629, lo 0.7898, hi 0.9411, unit 2,932 of 3,398, outcome BELOW, as printed: M3 and above, 1 year 3,398 2,932 340 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 207
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,848 of 159,621, outcome ABOVE, as printed: every magnitude, every window 159,621 157,848 1,323 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,236
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 304 of 117,825, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,825 304 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0336, lo 0.0169, hi 0.0487, unit 586 of 17,421, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,421 586 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.0679, lo 0.0459, hi 0.0914, unit 434 of 6,391, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,391 434 7.1 6.8 6.2 to 7.4 4.6 to 9.1 consistent 80
row-record quake.prob.10_20: value 0.1054, lo 0.0741, hi 0.1363, unit 597 of 5,663, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,663 597 14.4 10.5 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.193, lo 0.1512, hi 0.2366, unit 950 of 4,922, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,922 950 28.5 19.3 18.2 to 20.4 15.1 to 23.7 below 74
row-record quake.prob.40_60: value 0.3379, lo 0.2646, hi 0.4109, unit 911 of 2,696, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,696 911 49.3 33.8 32.0 to 35.6 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3043, hi 0.5611, unit 799 of 1,868, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,868 799 69.5 42.8 40.6 to 45.0 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,236 of 1,264, outcome BELOW, as printed: 99 to 100 percent 1,264 1,236 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 31,933, outcome CONSISTENT, as printed: 63 of 31,933 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3113, lo 0.2429, hi 0.3864, unit 5,599 of 17,984, outcome BELOW, as printed: every magnitude, every window 17,984 5,599 41.9 31.1 30.5 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3032, lo 0.2305, hi 0.3835, unit 3,809 of 12,562, outcome BELOW, as printed: M3 and above 12,562 3,809 44.6 30.3 29.5 to 31.1 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3301, lo 0.2447, hi 0.4194, unit 1,790 of 5,422, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,422 1,790 35.6 33.0 31.8 to 34.3 24.5 to 41.9 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2378, lo 0.1388, hi 0.3388, unit 336 of 1,413, outcome BELOW, as printed: every magnitude, 1 day 1,413 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2102, lo 0.1302, hi 0.3091, unit 866 of 4,119, outcome BELOW, as printed: every magnitude, 1 week 4,119 866 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2375, lo 0.1647, hi 0.3268, unit 1,730 of 7,283, outcome BELOW, as printed: every magnitude, 1 month 7,283 1,730 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.516, lo 0.4217, hi 0.6037, unit 2,667 of 5,169, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,169 2,667 50.7 51.6 50.2 to 53.0 42.2 to 60.4 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9289, lo 0.8816, hi 0.9565, unit 666 of 717, outcome CANNOT_TELL, as printed: 666 of 717 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.

## 2026-11-13 00:38 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T03:25:42Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-13T03:25:42Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-13T03:25:42Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9459, hi 0.9776, unit 30,736 of 31,938, outcome CANNOT_TELL, as printed: M3 and above, every window 31,938 30,736 759 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,752
row-record quake.cover.m4: value 0.9856, lo 0.9789, hi 0.9938, unit 31,361 of 31,818, outcome ABOVE, as printed: M4 and above 31,818 31,361 451 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,814
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,828 of 31,938, outcome ABOVE, as printed: M5 and above 31,938 31,828 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,323
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,933 of 31,938, outcome ABOVE, as printed: M6 and above 31,938 31,933 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,485
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,937 of 31,938, outcome ABOVE, as printed: M7 and above 31,938 31,937 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,824
row-record quake.cover.m3.day: value 0.9887, lo 0.9804, hi 0.9937, unit 9,625 of 9,735, outcome ABOVE, as printed: M3 and above, 1 day 9,735 9,625 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,055
row-record quake.cover.m3.week: value 0.9746, lo 0.9598, hi 0.9841, unit 9,382 of 9,627, outcome ABOVE, as printed: M3 and above, 1 week 9,627 9,382 136 109 97.5 97.1 to 97.8 96.0 to 98.4 above 82 3,717
row-record quake.cover.m3.month: value 0.9586, lo 0.9392, hi 0.9756, unit 8,797 of 9,177, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,177 8,797 230 150 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,773
row-record quake.cover.m3.year: value 0.8626, lo 0.7894, hi 0.9409, unit 2,932 of 3,399, outcome BELOW, as printed: M3 and above, 1 year 3,399 2,932 341 126 86.3 85.1 to 87.4 78.9 to 94.1 below 42 207
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,871 of 159,646, outcome ABOVE, as printed: every magnitude, every window 159,646 157,871 1,325 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,258
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 304 of 117,846, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,846 304 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0336, lo 0.0169, hi 0.0487, unit 586 of 17,422, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,422 586 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.068, lo 0.0459, hi 0.092, unit 435 of 6,393, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,393 435 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1054, lo 0.0741, hi 0.1363, unit 597 of 5,663, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,663 597 14.4 10.5 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.193, lo 0.1512, hi 0.2366, unit 950 of 4,922, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,922 950 28.5 19.3 18.2 to 20.4 15.1 to 23.7 below 74
row-record quake.prob.40_60: value 0.3382, lo 0.2649, hi 0.4112, unit 912 of 2,697, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,697 912 49.3 33.8 32.0 to 35.6 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3043, hi 0.5611, unit 799 of 1,868, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,868 799 69.5 42.8 40.6 to 45.0 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,236 of 1,264, outcome BELOW, as printed: 99 to 100 percent 1,264 1,236 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 31,938, outcome CONSISTENT, as printed: 63 of 31,938 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3114, lo 0.2429, hi 0.3864, unit 5,600 of 17,985, outcome BELOW, as printed: every magnitude, every window 17,985 5,600 41.9 31.1 30.5 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3033, lo 0.2306, hi 0.3835, unit 3,810 of 12,563, outcome BELOW, as printed: M3 and above 12,563 3,810 44.6 30.3 29.5 to 31.1 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3301, lo 0.2447, hi 0.4194, unit 1,790 of 5,422, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,422 1,790 35.6 33.0 31.8 to 34.3 24.5 to 41.9 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2378, lo 0.1388, hi 0.3388, unit 336 of 1,413, outcome BELOW, as printed: every magnitude, 1 day 1,413 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2102, lo 0.1302, hi 0.3091, unit 866 of 4,119, outcome BELOW, as printed: every magnitude, 1 week 4,119 866 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2375, lo 0.1647, hi 0.3268, unit 1,730 of 7,283, outcome BELOW, as printed: every magnitude, 1 month 7,283 1,730 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.5161, lo 0.4219, hi 0.6038, unit 2,668 of 5,170, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,170 2,668 50.7 51.6 50.2 to 53.0 42.2 to 60.4 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9289, lo 0.8816, hi 0.9565, unit 666 of 717, outcome CANNOT_TELL, as printed: 666 of 717 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.

## 2026-11-13 03:52 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T07:43:44Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-13T07:43:44Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-13T07:43:44Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.9459, hi 0.9776, unit 30,747 of 31,949, outcome CANNOT_TELL, as printed: M3 and above, every window 31,949 30,747 759 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,757
row-record quake.cover.m4: value 0.9856, lo 0.979, hi 0.9938, unit 31,372 of 31,829, outcome ABOVE, as printed: M4 and above 31,829 31,372 451 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,822
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,839 of 31,949, outcome ABOVE, as printed: M5 and above 31,949 31,839 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,333
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,944 of 31,949, outcome ABOVE, as printed: M6 and above 31,949 31,944 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,496
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,948 of 31,949, outcome ABOVE, as printed: M7 and above 31,949 31,948 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,835
row-record quake.cover.m3.day: value 0.9887, lo 0.9804, hi 0.9937, unit 9,627 of 9,737, outcome ABOVE, as printed: M3 and above, 1 day 9,737 9,627 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,057
row-record quake.cover.m3.week: value 0.9746, lo 0.9598, hi 0.9841, unit 9,384 of 9,629, outcome ABOVE, as printed: M3 and above, 1 week 9,629 9,384 136 109 97.5 97.1 to 97.8 96.0 to 98.4 above 82 3,718
row-record quake.cover.m3.month: value 0.9586, lo 0.9392, hi 0.9756, unit 8,799 of 9,179, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,179 8,799 230 150 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,774
row-record quake.cover.m3.year: value 0.8628, lo 0.7896, hi 0.941, unit 2,937 of 3,404, outcome BELOW, as printed: M3 and above, 1 year 3,404 2,937 341 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 208
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,926 of 159,701, outcome ABOVE, as printed: every magnitude, every window 159,701 157,926 1,325 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,303
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 304 of 117,888, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,888 304 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0336, lo 0.0169, hi 0.0487, unit 586 of 17,427, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,427 586 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.068, lo 0.0459, hi 0.0919, unit 435 of 6,397, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,397 435 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1054, lo 0.0741, hi 0.1363, unit 597 of 5,664, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,664 597 14.4 10.5 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1932, lo 0.1512, hi 0.2366, unit 951 of 4,923, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,923 951 28.5 19.3 18.2 to 20.4 15.1 to 23.7 below 74
row-record quake.prob.40_60: value 0.338, lo 0.2649, hi 0.4108, unit 912 of 2,698, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,698 912 49.3 33.8 32.0 to 35.6 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.4275, lo 0.3043, hi 0.5608, unit 799 of 1,869, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,869 799 69.5 42.8 40.5 to 45.0 30.4 to 56.1 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7766, lo 0.6691, hi 0.8626, unit 636 of 819, outcome BELOW, as printed: 90 to 99 percent, not including 99 819 636 95.2 77.7 74.7 to 80.4 66.9 to 86.3 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,236 of 1,264, outcome BELOW, as printed: 99 to 100 percent 1,264 1,236 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 31,949, outcome CONSISTENT, as printed: 63 of 31,949 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3114, lo 0.2429, hi 0.3863, unit 5,601 of 17,989, outcome BELOW, as printed: every magnitude, every window 17,989 5,601 41.9 31.1 30.5 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3033, lo 0.2306, hi 0.3835, unit 3,811 of 12,566, outcome BELOW, as printed: M3 and above 12,566 3,811 44.6 30.3 29.5 to 31.1 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3301, lo 0.2446, hi 0.4194, unit 1,790 of 5,423, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,423 1,790 35.6 33.0 31.8 to 34.3 24.5 to 41.9 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2378, lo 0.1388, hi 0.3388, unit 336 of 1,413, outcome BELOW, as printed: every magnitude, 1 day 1,413 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2102, lo 0.1302, hi 0.3091, unit 866 of 4,119, outcome BELOW, as printed: every magnitude, 1 week 4,119 866 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2375, lo 0.1647, hi 0.3268, unit 1,730 of 7,283, outcome BELOW, as printed: every magnitude, 1 month 7,283 1,730 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.5158, lo 0.4217, hi 0.6035, unit 2,669 of 5,174, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,174 2,669 50.7 51.6 50.2 to 52.9 42.2 to 60.4 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9289, lo 0.8816, hi 0.9565, unit 666 of 717, outcome CANNOT_TELL, as printed: 666 of 717 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.

## 2026-11-13 08:11 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T11:59:38Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-13T11:59:38Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-13T11:59:38Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.946, hi 0.9776, unit 30,760 of 31,963, outcome CANNOT_TELL, as printed: M3 and above, every window 31,963 30,760 760 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,766
row-record quake.cover.m4: value 0.9856, lo 0.979, hi 0.9938, unit 31,385 of 31,843, outcome ABOVE, as printed: M4 and above 31,843 31,385 452 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,834
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,853 of 31,963, outcome ABOVE, as printed: M5 and above 31,963 31,853 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,345
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,958 of 31,963, outcome ABOVE, as printed: M6 and above 31,963 31,958 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,510
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,962 of 31,963, outcome ABOVE, as printed: M7 and above 31,963 31,962 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,849
row-record quake.cover.m3.day: value 0.9887, lo 0.9804, hi 0.9937, unit 9,634 of 9,744, outcome ABOVE, as printed: M3 and above, 1 day 9,744 9,634 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,064
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,388 of 9,634, outcome ABOVE, as printed: M3 and above, 1 week 9,634 9,388 137 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,720
row-record quake.cover.m3.month: value 0.9586, lo 0.9392, hi 0.9756, unit 8,799 of 9,179, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,179 8,799 230 150 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,774
row-record quake.cover.m3.year: value 0.8629, lo 0.7898, hi 0.9411, unit 2,939 of 3,406, outcome BELOW, as printed: M3 and above, 1 year 3,406 2,939 341 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 208
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 157,994 of 159,771, outcome ABOVE, as printed: every magnitude, every window 159,771 157,994 1,327 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,364
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 304 of 117,944, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 117,944 304 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0337, lo 0.0169, hi 0.0487, unit 587 of 17,434, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,434 587 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.068, lo 0.0459, hi 0.0919, unit 435 of 6,397, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,397 435 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1055, lo 0.0741, hi 0.1363, unit 598 of 5,667, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,667 598 14.4 10.5 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1931, lo 0.1512, hi 0.2365, unit 951 of 4,924, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,924 951 28.5 19.3 18.2 to 20.4 15.1 to 23.6 below 74
row-record quake.prob.40_60: value 0.338, lo 0.2649, hi 0.4108, unit 912 of 2,698, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,698 912 49.3 33.8 32.0 to 35.6 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.427, lo 0.3043, hi 0.5603, unit 799 of 1,871, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,871 799 69.5 42.7 40.5 to 45.0 30.4 to 56.0 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7756, lo 0.6691, hi 0.8613, unit 636 of 820, outcome BELOW, as printed: 90 to 99 percent, not including 99 820 636 95.2 77.6 74.6 to 80.3 66.9 to 86.1 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,236 of 1,264, outcome BELOW, as printed: 99 to 100 percent 1,264 1,236 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 31,963, outcome CONSISTENT, as printed: 63 of 31,963 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3113, lo 0.2428, hi 0.3863, unit 5,602 of 17,996, outcome BELOW, as printed: every magnitude, every window 17,996 5,602 41.9 31.1 30.5 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3033, lo 0.2305, hi 0.3836, unit 3,812 of 12,570, outcome BELOW, as printed: M3 and above 12,570 3,812 44.6 30.3 29.5 to 31.1 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3299, lo 0.2445, hi 0.4192, unit 1,790 of 5,426, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,426 1,790 35.6 33.0 31.8 to 34.2 24.4 to 41.9 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2378, lo 0.1388, hi 0.3388, unit 336 of 1,413, outcome BELOW, as printed: every magnitude, 1 day 1,413 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2104, lo 0.1305, hi 0.3088, unit 867 of 4,121, outcome BELOW, as printed: every magnitude, 1 week 4,121 867 36.7 21.0 19.8 to 22.3 13.1 to 30.9 below 73
row-record quake.prob10.month: value 0.2375, lo 0.1647, hi 0.3268, unit 1,730 of 7,283, outcome BELOW, as printed: every magnitude, 1 month 7,283 1,730 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.5154, lo 0.4212, hi 0.603, unit 2,669 of 5,179, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,179 2,669 50.7 51.5 50.2 to 52.9 42.1 to 60.3 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.929, lo 0.882, hi 0.9565, unit 667 of 718, outcome CANNOT_TELL, as printed: 667 of 718 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.

## 2026-11-13 09:16 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T14:14:05Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-13T14:14:05Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-13T14:14:05Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.946, hi 0.9776, unit 30,775 of 31,978, outcome CANNOT_TELL, as printed: M3 and above, every window 31,978 30,775 760 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,771
row-record quake.cover.m4: value 0.9855, lo 0.9789, hi 0.9937, unit 31,397 of 31,858, outcome ABOVE, as printed: M4 and above 31,858 31,397 455 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,847
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,868 of 31,978, outcome ABOVE, as printed: M5 and above 31,978 31,868 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,360
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,973 of 31,978, outcome ABOVE, as printed: M6 and above 31,978 31,973 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,525
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,977 of 31,978, outcome ABOVE, as printed: M7 and above 31,978 31,977 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,864
row-record quake.cover.m3.day: value 0.9887, lo 0.9804, hi 0.9937, unit 9,639 of 9,749, outcome ABOVE, as printed: M3 and above, 1 day 9,749 9,639 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,068
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,390 of 9,636, outcome ABOVE, as printed: M3 and above, 1 week 9,636 9,390 137 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,720
row-record quake.cover.m3.month: value 0.9586, lo 0.9393, hi 0.9756, unit 8,804 of 9,184, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,184 8,804 230 150 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,775
row-record quake.cover.m3.year: value 0.863, lo 0.79, hi 0.9411, unit 2,942 of 3,409, outcome BELOW, as printed: M3 and above, 1 year 3,409 2,942 341 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 208
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 158,066 of 159,846, outcome ABOVE, as printed: every magnitude, every window 159,846 158,066 1,330 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,427
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 305 of 118,001, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 118,001 305 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0338, lo 0.0171, hi 0.0488, unit 589 of 17,444, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,444 589 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.0681, lo 0.0462, hi 0.092, unit 436 of 6,400, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,400 436 7.1 6.8 6.2 to 7.5 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1056, lo 0.0745, hi 0.1363, unit 599 of 5,670, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,670 599 14.4 10.6 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1931, lo 0.1512, hi 0.2365, unit 951 of 4,924, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,924 951 28.5 19.3 18.2 to 20.4 15.1 to 23.6 below 74
row-record quake.prob.40_60: value 0.3381, lo 0.2649, hi 0.411, unit 913 of 2,700, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,700 913 49.3 33.8 32.0 to 35.6 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.427, lo 0.3043, hi 0.5603, unit 799 of 1,871, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,871 799 69.5 42.7 40.5 to 45.0 30.4 to 56.0 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7756, lo 0.6691, hi 0.8613, unit 636 of 820, outcome BELOW, as printed: 90 to 99 percent, not including 99 820 636 95.2 77.6 74.6 to 80.3 66.9 to 86.1 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,236 of 1,264, outcome BELOW, as printed: 99 to 100 percent 1,264 1,236 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 31,978, outcome CONSISTENT, as printed: 63 of 31,978 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3113, lo 0.243, hi 0.3862, unit 5,604 of 18,001, outcome BELOW, as printed: every magnitude, every window 18,001 5,604 41.9 31.1 30.5 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3033, lo 0.2307, hi 0.3835, unit 3,814 of 12,575, outcome BELOW, as printed: M3 and above 12,575 3,814 44.5 30.3 29.5 to 31.1 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3299, lo 0.2445, hi 0.4192, unit 1,790 of 5,426, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,426 1,790 35.6 33.0 31.8 to 34.2 24.4 to 41.9 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2376, lo 0.1388, hi 0.3385, unit 336 of 1,414, outcome BELOW, as printed: every magnitude, 1 day 1,414 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2104, lo 0.1305, hi 0.3088, unit 867 of 4,121, outcome BELOW, as printed: every magnitude, 1 week 4,121 867 36.7 21.0 19.8 to 22.3 13.1 to 30.9 below 73
row-record quake.prob10.month: value 0.2377, lo 0.165, hi 0.327, unit 1,732 of 7,285, outcome BELOW, as printed: every magnitude, 1 month 7,285 1,732 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.5152, lo 0.4212, hi 0.6025, unit 2,669 of 5,181, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,181 2,669 50.7 51.5 50.1 to 52.9 42.1 to 60.2 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9291, lo 0.8824, hi 0.9566, unit 668 of 719, outcome CANNOT_TELL, as printed: 668 of 719 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.

## 2026-11-13 11:27 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T16:19:23Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-13T16:19:23Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-13T16:19:23Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.946, hi 0.9776, unit 30,783 of 31,986, outcome CANNOT_TELL, as printed: M3 and above, every window 31,986 30,783 760 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,773
row-record quake.cover.m4: value 0.9855, lo 0.9789, hi 0.9937, unit 31,405 of 31,866, outcome ABOVE, as printed: M4 and above 31,866 31,405 455 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,854
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,876 of 31,986, outcome ABOVE, as printed: M5 and above 31,986 31,876 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,368
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,981 of 31,986, outcome ABOVE, as printed: M6 and above 31,986 31,981 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,533
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,985 of 31,986, outcome ABOVE, as printed: M7 and above 31,986 31,985 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,872
row-record quake.cover.m3.day: value 0.9887, lo 0.9804, hi 0.9937, unit 9,641 of 9,751, outcome ABOVE, as printed: M3 and above, 1 day 9,751 9,641 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,069
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,390 of 9,636, outcome ABOVE, as printed: M3 and above, 1 week 9,636 9,390 137 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,720
row-record quake.cover.m3.month: value 0.9586, lo 0.9393, hi 0.9756, unit 8,809 of 9,189, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,189 8,809 230 150 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,776
row-record quake.cover.m3.year: value 0.863, lo 0.7901, hi 0.9411, unit 2,943 of 3,410, outcome BELOW, as printed: M3 and above, 1 year 3,410 2,943 341 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 208
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 158,106 of 159,886, outcome ABOVE, as printed: every magnitude, every window 159,886 158,106 1,330 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,460
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 305 of 118,031, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 118,031 305 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0338, lo 0.0171, hi 0.0488, unit 589 of 17,450, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,450 589 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.0681, lo 0.0462, hi 0.092, unit 436 of 6,401, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,401 436 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1056, lo 0.0745, hi 0.1363, unit 599 of 5,672, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,672 599 14.4 10.6 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1931, lo 0.1512, hi 0.2365, unit 951 of 4,925, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,925 951 28.5 19.3 18.2 to 20.4 15.1 to 23.6 below 74
row-record quake.prob.40_60: value 0.3381, lo 0.2649, hi 0.411, unit 913 of 2,700, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,700 913 49.3 33.8 32.0 to 35.6 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.427, lo 0.3043, hi 0.5603, unit 799 of 1,871, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,871 799 69.5 42.7 40.5 to 45.0 30.4 to 56.0 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7756, lo 0.6691, hi 0.8613, unit 636 of 820, outcome BELOW, as printed: 90 to 99 percent, not including 99 820 636 95.2 77.6 74.6 to 80.3 66.9 to 86.1 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,236 of 1,264, outcome BELOW, as printed: 99 to 100 percent 1,264 1,236 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 31,986, outcome CONSISTENT, as printed: 63 of 31,986 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3113, lo 0.243, hi 0.3862, unit 5,604 of 18,004, outcome BELOW, as printed: every magnitude, every window 18,004 5,604 41.9 31.1 30.4 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3032, lo 0.2307, hi 0.3835, unit 3,814 of 12,578, outcome BELOW, as printed: M3 and above 12,578 3,814 44.5 30.3 29.5 to 31.1 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3299, lo 0.2445, hi 0.4192, unit 1,790 of 5,426, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,426 1,790 35.6 33.0 31.8 to 34.2 24.4 to 41.9 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2376, lo 0.1388, hi 0.3385, unit 336 of 1,414, outcome BELOW, as printed: every magnitude, 1 day 1,414 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2104, lo 0.1305, hi 0.3088, unit 867 of 4,121, outcome BELOW, as printed: every magnitude, 1 week 4,121 867 36.7 21.0 19.8 to 22.3 13.1 to 30.9 below 73
row-record quake.prob10.month: value 0.2377, lo 0.165, hi 0.3268, unit 1,732 of 7,287, outcome BELOW, as printed: every magnitude, 1 month 7,287 1,732 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.5151, lo 0.4212, hi 0.602, unit 2,669 of 5,182, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,182 2,669 50.7 51.5 50.1 to 52.9 42.1 to 60.2 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9291, lo 0.8824, hi 0.9566, unit 668 of 719, outcome CANNOT_TELL, as printed: 668 of 719 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.

## 2026-11-13 14:08 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T18:29:43Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-13T18:29:43Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-13T18:29:43Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.946, hi 0.9776, unit 30,788 of 31,991, outcome CANNOT_TELL, as printed: M3 and above, every window 31,991 30,788 760 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,776
row-record quake.cover.m4: value 0.9855, lo 0.9789, hi 0.9937, unit 31,410 of 31,871, outcome ABOVE, as printed: M4 and above 31,871 31,410 455 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,857
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,881 of 31,991, outcome ABOVE, as printed: M5 and above 31,991 31,881 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,372
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,986 of 31,991, outcome ABOVE, as printed: M6 and above 31,991 31,986 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,538
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,990 of 31,991, outcome ABOVE, as printed: M7 and above 31,991 31,990 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,877
row-record quake.cover.m3.day: value 0.9887, lo 0.9804, hi 0.9937, unit 9,643 of 9,753, outcome ABOVE, as printed: M3 and above, 1 day 9,753 9,643 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,071
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,391 of 9,637, outcome ABOVE, as printed: M3 and above, 1 week 9,637 9,391 137 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,721
row-record quake.cover.m3.month: value 0.9586, lo 0.9393, hi 0.9756, unit 8,809 of 9,189, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,189 8,809 230 150 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,776
row-record quake.cover.m3.year: value 0.8631, lo 0.7902, hi 0.9412, unit 2,945 of 3,412, outcome BELOW, as printed: M3 and above, 1 year 3,412 2,945 341 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 208
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 158,131 of 159,911, outcome ABOVE, as printed: every magnitude, every window 159,911 158,131 1,330 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,480
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 305 of 118,050, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 118,050 305 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0337, lo 0.0171, hi 0.0488, unit 589 of 17,452, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,452 589 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.0681, lo 0.0462, hi 0.092, unit 436 of 6,402, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,402 436 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1056, lo 0.0745, hi 0.1363, unit 599 of 5,672, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,672 599 14.4 10.6 9.8 to 11.4 7.4 to 13.6 below 77
row-record quake.prob.20_40: value 0.1931, lo 0.1512, hi 0.2365, unit 951 of 4,926, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,926 951 28.5 19.3 18.2 to 20.4 15.1 to 23.6 below 74
row-record quake.prob.40_60: value 0.3384, lo 0.2649, hi 0.4112, unit 914 of 2,701, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,701 914 49.3 33.8 32.1 to 35.6 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.4274, lo 0.3044, hi 0.5605, unit 800 of 1,872, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,872 800 69.5 42.7 40.5 to 45.0 30.4 to 56.0 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7756, lo 0.6691, hi 0.8613, unit 636 of 820, outcome BELOW, as printed: 90 to 99 percent, not including 99 820 636 95.2 77.6 74.6 to 80.3 66.9 to 86.1 below 32
row-record quake.prob.99_100: value 0.9778, lo 0.9589, hi 0.9912, unit 1,236 of 1,264, outcome BELOW, as printed: 99 to 100 percent 1,264 1,236 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 31,991, outcome CONSISTENT, as printed: 63 of 31,991 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3113, lo 0.2431, hi 0.3863, unit 5,606 of 18,007, outcome BELOW, as printed: every magnitude, every window 18,007 5,606 41.9 31.1 30.5 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3033, lo 0.2308, hi 0.3837, unit 3,816 of 12,580, outcome BELOW, as printed: M3 and above 12,580 3,816 44.5 30.3 29.5 to 31.1 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3298, lo 0.2443, hi 0.4192, unit 1,790 of 5,427, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,427 1,790 35.6 33.0 31.7 to 34.2 24.4 to 41.9 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2376, lo 0.1388, hi 0.3385, unit 336 of 1,414, outcome BELOW, as printed: every magnitude, 1 day 1,414 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2104, lo 0.1305, hi 0.3088, unit 867 of 4,121, outcome BELOW, as printed: every magnitude, 1 week 4,121 867 36.7 21.0 19.8 to 22.3 13.1 to 30.9 below 73
row-record quake.prob10.month: value 0.2377, lo 0.165, hi 0.3268, unit 1,732 of 7,287, outcome BELOW, as printed: every magnitude, 1 month 7,287 1,732 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.5151, lo 0.4216, hi 0.602, unit 2,671 of 5,185, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,185 2,671 50.7 51.5 50.1 to 52.9 42.2 to 60.2 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9291, lo 0.8824, hi 0.9566, unit 668 of 719, outcome CANNOT_TELL, as printed: 668 of 719 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.

## 2026-11-13 15:58 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T20:51:55Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-13T20:51:55Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-13T20:51:55Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.946, hi 0.9776, unit 30,796 of 32,000, outcome CANNOT_TELL, as printed: M3 and above, every window 32,000 30,796 761 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,779
row-record quake.cover.m4: value 0.9855, lo 0.9788, hi 0.9937, unit 31,418 of 31,880, outcome ABOVE, as printed: M4 and above 31,880 31,418 456 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,862
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,890 of 32,000, outcome ABOVE, as printed: M5 and above 32,000 31,890 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,379
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 31,995 of 32,000, outcome ABOVE, as printed: M6 and above 32,000 31,995 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,547
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 31,999 of 32,000, outcome ABOVE, as printed: M7 and above 32,000 31,999 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,886
row-record quake.cover.m3.day: value 0.9887, lo 0.9804, hi 0.9937, unit 9,647 of 9,757, outcome ABOVE, as printed: M3 and above, 1 day 9,757 9,647 52 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,074
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,391 of 9,637, outcome ABOVE, as printed: M3 and above, 1 week 9,637 9,391 137 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,721
row-record quake.cover.m3.month: value 0.9586, lo 0.9393, hi 0.9756, unit 8,809 of 9,189, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,189 8,809 230 150 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,776
row-record quake.cover.m3.year: value 0.863, lo 0.7901, hi 0.9412, unit 2,949 of 3,417, outcome BELOW, as printed: M3 and above, 1 year 3,417 2,949 342 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 208
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 158,174 of 159,956, outcome ABOVE, as printed: every magnitude, every window 159,956 158,174 1,332 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,513
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 305 of 118,080, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 118,080 305 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0337, lo 0.0171, hi 0.0488, unit 589 of 17,456, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,456 589 2.4 3.4 3.1 to 3.6 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.0681, lo 0.0462, hi 0.0919, unit 436 of 6,404, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,404 436 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1059, lo 0.0748, hi 0.1367, unit 601 of 5,675, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,675 601 14.4 10.6 9.8 to 11.4 7.5 to 13.7 below 77
row-record quake.prob.20_40: value 0.1934, lo 0.1514, hi 0.2367, unit 953 of 4,928, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,928 953 28.5 19.3 18.3 to 20.5 15.1 to 23.7 below 74
row-record quake.prob.40_60: value 0.3384, lo 0.2649, hi 0.4112, unit 914 of 2,701, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,701 914 49.3 33.8 32.1 to 35.6 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3054, hi 0.5607, unit 802 of 1,875, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,875 802 69.5 42.8 40.6 to 45.0 30.5 to 56.1 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7756, lo 0.6691, hi 0.8613, unit 636 of 820, outcome BELOW, as printed: 90 to 99 percent, not including 99 820 636 95.2 77.6 74.6 to 80.3 66.9 to 86.1 below 32
row-record quake.prob.99_100: value 0.9779, lo 0.959, hi 0.9912, unit 1,237 of 1,265, outcome BELOW, as printed: 99 to 100 percent 1,265 1,237 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 32,000, outcome CONSISTENT, as printed: 63 of 32,000 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3116, lo 0.2431, hi 0.3866, unit 5,613 of 18,016, outcome BELOW, as printed: every magnitude, every window 18,016 5,613 41.9 31.2 30.5 to 31.8 24.3 to 38.7 below 77
row-record quake.prob10.m3: value 0.3035, lo 0.2309, hi 0.3839, unit 3,820 of 12,585, outcome BELOW, as printed: M3 and above 12,585 3,820 44.5 30.3 29.6 to 31.2 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3301, lo 0.2447, hi 0.4197, unit 1,793 of 5,431, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,431 1,793 35.6 33.0 31.8 to 34.3 24.5 to 42.0 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2376, lo 0.1388, hi 0.3385, unit 336 of 1,414, outcome BELOW, as printed: every magnitude, 1 day 1,414 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2104, lo 0.1305, hi 0.3088, unit 867 of 4,121, outcome BELOW, as printed: every magnitude, 1 week 4,121 867 36.7 21.0 19.8 to 22.3 13.1 to 30.9 below 73
row-record quake.prob10.month: value 0.2377, lo 0.165, hi 0.3268, unit 1,732 of 7,287, outcome BELOW, as printed: every magnitude, 1 month 7,287 1,732 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.5156, lo 0.4215, hi 0.6031, unit 2,678 of 5,194, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,194 2,678 50.7 51.6 50.2 to 52.9 42.1 to 60.3 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9292, lo 0.8824, hi 0.9566, unit 669 of 720, outcome CANNOT_TELL, as printed: 669 of 720 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.

## 2026-11-13 18:12 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T22:57:04Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-13T22:57:04Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-13T22:57:04Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9623, lo 0.946, hi 0.9776, unit 30,800 of 32,005, outcome CANNOT_TELL, as printed: M3 and above, every window 32,005 30,800 762 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,780
row-record quake.cover.m4: value 0.9855, lo 0.9787, hi 0.9936, unit 31,422 of 31,885, outcome ABOVE, as printed: M4 and above 31,885 31,422 457 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,865
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,895 of 32,005, outcome ABOVE, as printed: M5 and above 32,005 31,895 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,384
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 32,000 of 32,005, outcome ABOVE, as printed: M6 and above 32,005 32,000 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,552
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 32,004 of 32,005, outcome ABOVE, as printed: M7 and above 32,005 32,004 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,891
row-record quake.cover.m3.day: value 0.9886, lo 0.9802, hi 0.9936, unit 9,649 of 9,760, outcome ABOVE, as printed: M3 and above, 1 day 9,760 9,649 53 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,075
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,391 of 9,637, outcome ABOVE, as printed: M3 and above, 1 week 9,637 9,391 137 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,721
row-record quake.cover.m3.month: value 0.9587, lo 0.9393, hi 0.9756, unit 8,810 of 9,190, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,190 8,810 230 150 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,776
row-record quake.cover.m3.year: value 0.8631, lo 0.7901, hi 0.9412, unit 2,950 of 3,418, outcome BELOW, as printed: M3 and above, 1 year 3,418 2,950 342 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 208
row-record quake.cover.all: value 0.9888, lo 0.9848, hi 0.9934, unit 158,197 of 159,981, outcome ABOVE, as printed: every magnitude, every window 159,981 158,197 1,334 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,532
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 306 of 118,098, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 118,098 306 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0338, lo 0.0171, hi 0.0489, unit 590 of 17,460, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,460 590 2.4 3.4 3.1 to 3.7 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.0681, lo 0.0462, hi 0.0919, unit 436 of 6,405, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,405 436 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1059, lo 0.0748, hi 0.1367, unit 601 of 5,676, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,676 601 14.4 10.6 9.8 to 11.4 7.5 to 13.7 below 77
row-record quake.prob.20_40: value 0.1933, lo 0.1514, hi 0.2366, unit 953 of 4,929, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,929 953 28.5 19.3 18.3 to 20.5 15.1 to 23.7 below 74
row-record quake.prob.40_60: value 0.3384, lo 0.2649, hi 0.4112, unit 914 of 2,701, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,701 914 49.3 33.8 32.1 to 35.6 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3054, hi 0.5607, unit 802 of 1,875, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,875 802 69.5 42.8 40.6 to 45.0 30.5 to 56.1 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7756, lo 0.6691, hi 0.8613, unit 636 of 820, outcome BELOW, as printed: 90 to 99 percent, not including 99 820 636 95.2 77.6 74.6 to 80.3 66.9 to 86.1 below 32
row-record quake.prob.99_100: value 0.9779, lo 0.959, hi 0.9912, unit 1,237 of 1,265, outcome BELOW, as printed: 99 to 100 percent 1,265 1,237 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 32,005, outcome CONSISTENT, as printed: 63 of 32,005 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3115, lo 0.2431, hi 0.3866, unit 5,613 of 18,018, outcome BELOW, as printed: every magnitude, every window 18,018 5,613 41.9 31.1 30.5 to 31.8 24.3 to 38.7 below 77
row-record quake.prob10.m3: value 0.3035, lo 0.2309, hi 0.3837, unit 3,820 of 12,587, outcome BELOW, as printed: M3 and above 12,587 3,820 44.5 30.3 29.5 to 31.2 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3301, lo 0.2447, hi 0.4197, unit 1,793 of 5,431, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,431 1,793 35.6 33.0 31.8 to 34.3 24.5 to 42.0 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2376, lo 0.1388, hi 0.3385, unit 336 of 1,414, outcome BELOW, as printed: every magnitude, 1 day 1,414 336 36.1 23.8 21.6 to 26.1 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2104, lo 0.1305, hi 0.3088, unit 867 of 4,121, outcome BELOW, as printed: every magnitude, 1 week 4,121 867 36.7 21.0 19.8 to 22.3 13.1 to 30.9 below 73
row-record quake.prob10.month: value 0.2377, lo 0.165, hi 0.3268, unit 1,732 of 7,288, outcome BELOW, as printed: every magnitude, 1 month 7,288 1,732 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.5155, lo 0.4215, hi 0.6031, unit 2,678 of 5,195, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,195 2,678 50.7 51.5 50.2 to 52.9 42.1 to 60.3 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9292, lo 0.8824, hi 0.9566, unit 669 of 720, outcome CANNOT_TELL, as printed: 669 of 720 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.

## 2026-11-13 20:27 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-14T01:17:56Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-14T01:17:56Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-14T01:17:56Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.946, hi 0.9776, unit 30,810 of 32,015, outcome CANNOT_TELL, as printed: M3 and above, every window 32,015 30,810 762 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,785
row-record quake.cover.m4: value 0.9855, lo 0.9788, hi 0.9936, unit 31,432 of 31,895, outcome ABOVE, as printed: M4 and above 31,895 31,432 457 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,874
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,905 of 32,015, outcome ABOVE, as printed: M5 and above 32,015 31,905 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,394
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 32,010 of 32,015, outcome ABOVE, as printed: M6 and above 32,015 32,010 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,562
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 32,014 of 32,015, outcome ABOVE, as printed: M7 and above 32,015 32,014 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,901
row-record quake.cover.m3.day: value 0.9886, lo 0.9802, hi 0.9936, unit 9,651 of 9,762, outcome ABOVE, as printed: M3 and above, 1 day 9,762 9,651 53 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,076
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,394 of 9,640, outcome ABOVE, as printed: M3 and above, 1 week 9,640 9,394 137 109 97.5 97.1 to 97.7 96.0 to 98.4 above 82 3,723
row-record quake.cover.m3.month: value 0.9587, lo 0.9394, hi 0.9756, unit 8,813 of 9,193, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,193 8,813 230 150 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,777
row-record quake.cover.m3.year: value 0.8632, lo 0.7902, hi 0.9413, unit 2,952 of 3,420, outcome BELOW, as printed: M3 and above, 1 year 3,420 2,952 342 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 209
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 158,247 of 160,031, outcome ABOVE, as printed: every magnitude, every window 160,031 158,247 1,334 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,576
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 306 of 118,137, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 118,137 306 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0338, lo 0.0171, hi 0.0489, unit 590 of 17,466, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,466 590 2.4 3.4 3.1 to 3.7 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.0681, lo 0.0462, hi 0.0919, unit 436 of 6,406, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,406 436 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1058, lo 0.0748, hi 0.1366, unit 601 of 5,679, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,679 601 14.4 10.6 9.8 to 11.4 7.5 to 13.7 below 77
row-record quake.prob.20_40: value 0.1933, lo 0.1514, hi 0.2366, unit 953 of 4,929, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,929 953 28.5 19.3 18.3 to 20.5 15.1 to 23.7 below 74
row-record quake.prob.40_60: value 0.3383, lo 0.2647, hi 0.4111, unit 914 of 2,702, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,702 914 49.3 33.8 32.1 to 35.6 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3054, hi 0.5607, unit 802 of 1,875, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,875 802 69.5 42.8 40.6 to 45.0 30.5 to 56.1 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7756, lo 0.6691, hi 0.8613, unit 636 of 820, outcome BELOW, as printed: 90 to 99 percent, not including 99 820 636 95.2 77.6 74.6 to 80.3 66.9 to 86.1 below 32
row-record quake.prob.99_100: value 0.9779, lo 0.959, hi 0.9912, unit 1,237 of 1,265, outcome BELOW, as printed: 99 to 100 percent 1,265 1,237 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 32,015, outcome CONSISTENT, as printed: 63 of 32,015 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3115, lo 0.2431, hi 0.3866, unit 5,613 of 18,022, outcome BELOW, as printed: every magnitude, every window 18,022 5,613 41.9 31.1 30.5 to 31.8 24.3 to 38.7 below 77
row-record quake.prob10.m3: value 0.3034, lo 0.2308, hi 0.3837, unit 3,820 of 12,590, outcome BELOW, as printed: M3 and above 12,590 3,820 44.5 30.3 29.5 to 31.1 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3301, lo 0.2446, hi 0.4197, unit 1,793 of 5,432, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,432 1,793 35.6 33.0 31.8 to 34.3 24.5 to 42.0 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2375, lo 0.1387, hi 0.3385, unit 336 of 1,415, outcome BELOW, as printed: every magnitude, 1 day 1,415 336 36.1 23.8 21.6 to 26.0 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2103, lo 0.1302, hi 0.3088, unit 867 of 4,123, outcome BELOW, as printed: every magnitude, 1 week 4,123 867 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2376, lo 0.1649, hi 0.3268, unit 1,732 of 7,289, outcome BELOW, as printed: every magnitude, 1 month 7,289 1,732 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.5155, lo 0.4215, hi 0.6031, unit 2,678 of 5,195, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,195 2,678 50.7 51.5 50.2 to 52.9 42.1 to 60.3 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9292, lo 0.8824, hi 0.9566, unit 669 of 720, outcome CANNOT_TELL, as printed: 669 of 720 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.

## 2026-11-13 22:34 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-14T03:19:09Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-14T03:19:09Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-14T03:19:09Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.946, hi 0.9776, unit 30,815 of 32,020, outcome CANNOT_TELL, as printed: M3 and above, every window 32,020 30,815 762 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,789
row-record quake.cover.m4: value 0.9855, lo 0.9788, hi 0.9936, unit 31,437 of 31,900, outcome ABOVE, as printed: M4 and above 31,900 31,437 457 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,878
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,910 of 32,020, outcome ABOVE, as printed: M5 and above 32,020 31,910 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,399
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 32,015 of 32,020, outcome ABOVE, as printed: M6 and above 32,020 32,015 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,567
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 32,019 of 32,020, outcome ABOVE, as printed: M7 and above 32,020 32,019 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,906
row-record quake.cover.m3.day: value 0.9886, lo 0.9802, hi 0.9936, unit 9,652 of 9,763, outcome ABOVE, as printed: M3 and above, 1 day 9,763 9,652 53 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,077
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,396 of 9,642, outcome ABOVE, as printed: M3 and above, 1 week 9,642 9,396 137 109 97.5 97.1 to 97.8 96.0 to 98.4 above 82 3,725
row-record quake.cover.m3.month: value 0.9587, lo 0.9394, hi 0.9757, unit 8,814 of 9,194, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,194 8,814 230 150 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,778
row-record quake.cover.m3.year: value 0.8632, lo 0.7903, hi 0.9413, unit 2,953 of 3,421, outcome BELOW, as printed: M3 and above, 1 year 3,421 2,953 342 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 209
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 158,272 of 160,056, outcome ABOVE, as printed: every magnitude, every window 160,056 158,272 1,334 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,599
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 306 of 118,160, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 118,160 306 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0338, lo 0.0171, hi 0.0489, unit 590 of 17,466, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,466 590 2.4 3.4 3.1 to 3.7 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.0681, lo 0.0462, hi 0.0919, unit 436 of 6,407, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,407 436 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1058, lo 0.0748, hi 0.1366, unit 601 of 5,679, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,679 601 14.4 10.6 9.8 to 11.4 7.5 to 13.7 below 77
row-record quake.prob.20_40: value 0.1933, lo 0.1514, hi 0.2366, unit 953 of 4,929, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,929 953 28.5 19.3 18.3 to 20.5 15.1 to 23.7 below 74
row-record quake.prob.40_60: value 0.3385, lo 0.2648, hi 0.4115, unit 915 of 2,703, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,703 915 49.3 33.9 32.1 to 35.7 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3054, hi 0.5607, unit 802 of 1,875, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,875 802 69.5 42.8 40.6 to 45.0 30.5 to 56.1 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7756, lo 0.6691, hi 0.8613, unit 636 of 820, outcome BELOW, as printed: 90 to 99 percent, not including 99 820 636 95.2 77.6 74.6 to 80.3 66.9 to 86.1 below 32
row-record quake.prob.99_100: value 0.9779, lo 0.959, hi 0.9912, unit 1,237 of 1,265, outcome BELOW, as printed: 99 to 100 percent 1,265 1,237 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 32,020, outcome CONSISTENT, as printed: 63 of 32,020 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3115, lo 0.2431, hi 0.3866, unit 5,614 of 18,023, outcome BELOW, as printed: every magnitude, every window 18,023 5,614 41.9 31.1 30.5 to 31.8 24.3 to 38.7 below 77
row-record quake.prob10.m3: value 0.3035, lo 0.231, hi 0.3838, unit 3,821 of 12,591, outcome BELOW, as printed: M3 and above 12,591 3,821 44.5 30.3 29.5 to 31.2 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3301, lo 0.2446, hi 0.4197, unit 1,793 of 5,432, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,432 1,793 35.6 33.0 31.8 to 34.3 24.5 to 42.0 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2375, lo 0.1387, hi 0.3385, unit 336 of 1,415, outcome BELOW, as printed: every magnitude, 1 day 1,415 336 36.1 23.8 21.6 to 26.0 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2103, lo 0.1302, hi 0.3088, unit 867 of 4,123, outcome BELOW, as printed: every magnitude, 1 week 4,123 867 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2376, lo 0.1649, hi 0.3268, unit 1,732 of 7,289, outcome BELOW, as printed: every magnitude, 1 month 7,289 1,732 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.5156, lo 0.4215, hi 0.6031, unit 2,679 of 5,196, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,196 2,679 50.7 51.6 50.2 to 52.9 42.1 to 60.3 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9292, lo 0.8824, hi 0.9566, unit 669 of 720, outcome CANNOT_TELL, as printed: 669 of 720 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.

## 2026-11-14 00:28 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-14T05:20:39Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-14T05:20:39Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-14T05:20:39Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.946, hi 0.9776, unit 30,818 of 32,023, outcome CANNOT_TELL, as printed: M3 and above, every window 32,023 30,818 762 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,790
row-record quake.cover.m4: value 0.9855, lo 0.9788, hi 0.9936, unit 31,440 of 31,903, outcome ABOVE, as printed: M4 and above 31,903 31,440 457 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,881
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,913 of 32,023, outcome ABOVE, as printed: M5 and above 32,023 31,913 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,402
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 32,018 of 32,023, outcome ABOVE, as printed: M6 and above 32,023 32,018 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,570
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 32,022 of 32,023, outcome ABOVE, as printed: M7 and above 32,023 32,022 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,909
row-record quake.cover.m3.day: value 0.9886, lo 0.9802, hi 0.9936, unit 9,653 of 9,764, outcome ABOVE, as printed: M3 and above, 1 day 9,764 9,653 53 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,078
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,397 of 9,643, outcome ABOVE, as printed: M3 and above, 1 week 9,643 9,397 137 109 97.5 97.1 to 97.8 96.0 to 98.4 above 82 3,725
row-record quake.cover.m3.month: value 0.9587, lo 0.9394, hi 0.9757, unit 8,814 of 9,194, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,194 8,814 230 150 95.9 95.4 to 96.2 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,778
row-record quake.cover.m3.year: value 0.8632, lo 0.7904, hi 0.9413, unit 2,954 of 3,422, outcome BELOW, as printed: M3 and above, 1 year 3,422 2,954 342 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 209
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 158,287 of 160,071, outcome ABOVE, as printed: every magnitude, every window 160,071 158,287 1,334 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,612
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 306 of 118,171, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 118,171 306 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0338, lo 0.0171, hi 0.0489, unit 590 of 17,468, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,468 590 2.4 3.4 3.1 to 3.7 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.068, lo 0.0462, hi 0.0918, unit 436 of 6,408, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,408 436 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1058, lo 0.0748, hi 0.1366, unit 601 of 5,680, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,680 601 14.4 10.6 9.8 to 11.4 7.5 to 13.7 below 77
row-record quake.prob.20_40: value 0.1933, lo 0.1514, hi 0.2366, unit 953 of 4,929, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,929 953 28.5 19.3 18.3 to 20.5 15.1 to 23.7 below 74
row-record quake.prob.40_60: value 0.3385, lo 0.2648, hi 0.4115, unit 915 of 2,703, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,703 915 49.3 33.9 32.1 to 35.7 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3054, hi 0.5607, unit 802 of 1,875, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,875 802 69.5 42.8 40.6 to 45.0 30.5 to 56.1 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7756, lo 0.6691, hi 0.8613, unit 636 of 820, outcome BELOW, as printed: 90 to 99 percent, not including 99 820 636 95.2 77.6 74.6 to 80.3 66.9 to 86.1 below 32
row-record quake.prob.99_100: value 0.9779, lo 0.959, hi 0.9912, unit 1,237 of 1,265, outcome BELOW, as printed: 99 to 100 percent 1,265 1,237 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 32,023, outcome CONSISTENT, as printed: 63 of 32,023 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3115, lo 0.2431, hi 0.3865, unit 5,614 of 18,024, outcome BELOW, as printed: every magnitude, every window 18,024 5,614 41.9 31.1 30.5 to 31.8 24.3 to 38.6 below 77
row-record quake.prob10.m3: value 0.3034, lo 0.231, hi 0.3837, unit 3,821 of 12,592, outcome BELOW, as printed: M3 and above 12,592 3,821 44.5 30.3 29.5 to 31.1 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3301, lo 0.2446, hi 0.4197, unit 1,793 of 5,432, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,432 1,793 35.6 33.0 31.8 to 34.3 24.5 to 42.0 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2375, lo 0.1387, hi 0.3385, unit 336 of 1,415, outcome BELOW, as printed: every magnitude, 1 day 1,415 336 36.1 23.8 21.6 to 26.0 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2102, lo 0.1302, hi 0.3088, unit 867 of 4,124, outcome BELOW, as printed: every magnitude, 1 week 4,124 867 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2376, lo 0.1649, hi 0.3268, unit 1,732 of 7,289, outcome BELOW, as printed: every magnitude, 1 month 7,289 1,732 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.5156, lo 0.4215, hi 0.6031, unit 2,679 of 5,196, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,196 2,679 50.7 51.6 50.2 to 52.9 42.1 to 60.3 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9293, lo 0.8824, hi 0.9567, unit 670 of 721, outcome CANNOT_TELL, as printed: 670 of 721 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.

## 2026-11-14 03:57 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-14T07:40:48Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-14T07:40:48Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-14T07:40:48Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.946, hi 0.9776, unit 30,821 of 32,026, outcome CANNOT_TELL, as printed: M3 and above, every window 32,026 30,821 762 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,791
row-record quake.cover.m4: value 0.9855, lo 0.9788, hi 0.9936, unit 31,443 of 31,906, outcome ABOVE, as printed: M4 and above 31,906 31,443 457 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,882
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,916 of 32,026, outcome ABOVE, as printed: M5 and above 32,026 31,916 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,405
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 32,021 of 32,026, outcome ABOVE, as printed: M6 and above 32,026 32,021 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,573
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 32,025 of 32,026, outcome ABOVE, as printed: M7 and above 32,026 32,025 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,912
row-record quake.cover.m3.day: value 0.9886, lo 0.9802, hi 0.9936, unit 9,654 of 9,765, outcome ABOVE, as printed: M3 and above, 1 day 9,765 9,654 53 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,079
row-record quake.cover.m3.week: value 0.9745, lo 0.9598, hi 0.984, unit 9,397 of 9,643, outcome ABOVE, as printed: M3 and above, 1 week 9,643 9,397 137 109 97.5 97.1 to 97.8 96.0 to 98.4 above 82 3,725
row-record quake.cover.m3.month: value 0.9587, lo 0.9394, hi 0.9757, unit 8,815 of 9,195, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,195 8,815 230 150 95.9 95.4 to 96.3 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,778
row-record quake.cover.m3.year: value 0.8633, lo 0.7905, hi 0.9413, unit 2,955 of 3,423, outcome BELOW, as printed: M3 and above, 1 year 3,423 2,955 342 126 86.3 85.1 to 87.4 79.0 to 94.1 below 42 209
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 158,302 of 160,086, outcome ABOVE, as printed: every magnitude, every window 160,086 158,302 1,334 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,623
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 306 of 118,182, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 118,182 306 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0338, lo 0.0171, hi 0.049, unit 591 of 17,470, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,470 591 2.4 3.4 3.1 to 3.7 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.068, lo 0.0462, hi 0.0918, unit 436 of 6,408, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,408 436 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1058, lo 0.0748, hi 0.1366, unit 601 of 5,680, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,680 601 14.4 10.6 9.8 to 11.4 7.5 to 13.7 below 77
row-record quake.prob.20_40: value 0.1935, lo 0.1515, hi 0.2368, unit 954 of 4,931, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,931 954 28.5 19.4 18.3 to 20.5 15.2 to 23.7 below 74
row-record quake.prob.40_60: value 0.3385, lo 0.2648, hi 0.4115, unit 915 of 2,703, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,703 915 49.3 33.9 32.1 to 35.7 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3054, hi 0.5607, unit 802 of 1,875, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,875 802 69.5 42.8 40.6 to 45.0 30.5 to 56.1 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7756, lo 0.6691, hi 0.8613, unit 636 of 820, outcome BELOW, as printed: 90 to 99 percent, not including 99 820 636 95.2 77.6 74.6 to 80.3 66.9 to 86.1 below 32
row-record quake.prob.99_100: value 0.9779, lo 0.959, hi 0.9912, unit 1,237 of 1,265, outcome BELOW, as printed: 99 to 100 percent 1,265 1,237 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 32,026, outcome CONSISTENT, as printed: 63 of 32,026 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3115, lo 0.2431, hi 0.3866, unit 5,615 of 18,026, outcome BELOW, as printed: every magnitude, every window 18,026 5,615 41.8 31.1 30.5 to 31.8 24.3 to 38.7 below 77
row-record quake.prob10.m3: value 0.3035, lo 0.231, hi 0.3837, unit 3,822 of 12,594, outcome BELOW, as printed: M3 and above 12,594 3,822 44.5 30.3 29.5 to 31.2 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.3301, lo 0.2446, hi 0.4197, unit 1,793 of 5,432, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,432 1,793 35.6 33.0 31.8 to 34.3 24.5 to 42.0 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2375, lo 0.1387, hi 0.3385, unit 336 of 1,415, outcome BELOW, as printed: every magnitude, 1 day 1,415 336 36.1 23.8 21.6 to 26.0 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2102, lo 0.1302, hi 0.3088, unit 867 of 4,124, outcome BELOW, as printed: every magnitude, 1 week 4,124 867 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2376, lo 0.1649, hi 0.3268, unit 1,732 of 7,290, outcome BELOW, as printed: every magnitude, 1 month 7,290 1,732 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.5157, lo 0.4215, hi 0.6034, unit 2,680 of 5,197, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,197 2,680 50.7 51.6 50.2 to 52.9 42.1 to 60.3 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9293, lo 0.8824, hi 0.9567, unit 670 of 721, outcome CANNOT_TELL, as printed: 670 of 721 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.

## 2026-11-14 05:01 QUAKE desk refresh record: the rows as shipped, recomputed from the run of 2026-11-14T09:57:17Z and the page built from it (durable source for the quake.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_quake.json of the run at 2026-11-14T09:57:17Z, the same run quake.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: above and below the range are separate columns in the cover lines, cannot tell is a reading and never folded into a share
- V: holds: one ruler for the ranges, the stated 95 percent, and the stated chance for the bins, each read on the wider of the Wilson and sequence-group intervals as the plan states
- VI: holds: outcomes as the plan states them, the reading column holds the four outcomes as the plan states them
- R: holds: counts from the summary of 2026-11-14T09:57:17Z, no number typed by hand, display splits keep their label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its Wilson and sequence intervals on the page line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record quake.cover.m3: value 0.9624, lo 0.946, hi 0.9776, unit 30,829 of 32,034, outcome CANNOT_TELL, as printed: M3 and above, every window 32,034 30,829 762 443 96.2 96.0 to 96.4 94.6 to 97.8 cannot tell (STRADDLES_EDGE) 82 12,794
row-record quake.cover.m4: value 0.9855, lo 0.9788, hi 0.9936, unit 31,451 of 31,914, outcome ABOVE, as printed: M4 and above 31,914 31,451 457 6 98.6 98.4 to 98.7 97.9 to 99.4 above 81 22,888
row-record quake.cover.m5: value 0.9966, lo 0.9937, hi 0.9987, unit 31,924 of 32,034, outcome ABOVE, as printed: M5 and above 32,034 31,924 109 1 99.7 99.6 to 99.7 99.4 to 99.9 above 82 29,412
row-record quake.cover.m6: value 0.9998, lo 0.9996, hi 1.0, unit 32,029 of 32,034, outcome ABOVE, as printed: M6 and above 32,034 32,029 5 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,581
row-record quake.cover.m7: value 1.0, lo 0.9998, hi 1.0, unit 32,033 of 32,034, outcome ABOVE, as printed: M7 and above 32,034 32,033 1 0 100.0 100.0 to 100.0 100.0 to 100.0 above 82 31,920
row-record quake.cover.m3.day: value 0.9886, lo 0.9802, hi 0.9936, unit 9,655 of 9,766, outcome ABOVE, as printed: M3 and above, 1 day 9,766 9,655 53 58 98.9 98.6 to 99.1 98.0 to 99.4 above 82 7,080
row-record quake.cover.m3.week: value 0.9745, lo 0.9599, hi 0.984, unit 9,399 of 9,645, outcome ABOVE, as printed: M3 and above, 1 week 9,645 9,399 137 109 97.5 97.1 to 97.8 96.0 to 98.4 above 82 3,725
row-record quake.cover.m3.month: value 0.9587, lo 0.9394, hi 0.9757, unit 8,818 of 9,198, outcome CANNOT_TELL, as printed: M3 and above, 1 month 9,198 8,818 230 150 95.9 95.4 to 96.3 93.9 to 97.6 cannot tell (STRADDLES_EDGE) 77 1,780
row-record quake.cover.m3.year: value 0.8634, lo 0.7906, hi 0.9414, unit 2,957 of 3,425, outcome BELOW, as printed: M3 and above, 1 year 3,425 2,957 342 126 86.3 85.1 to 87.5 79.1 to 94.1 below 42 209
row-record quake.cover.all: value 0.9889, lo 0.9849, hi 0.9934, unit 158,342 of 160,126, outcome ABOVE, as printed: every magnitude, every window 160,126 158,342 1,334 450 98.9 98.8 to 98.9 98.5 to 99.3 above 82 128,655
row-record quake.prob.0_1: value 0.0026, lo 0.0007, hi 0.0043, unit 306 of 118,212, outcome CONSISTENT, as printed: 0 to 1 percent, not including 1 118,212 306 0.1 0.3 0.2 to 0.3 0.1 to 0.4 consistent 82
row-record quake.prob.1_5: value 0.0338, lo 0.0171, hi 0.049, unit 591 of 17,472, outcome CANNOT_TELL, as printed: 1 to 5 percent, not including 5 17,472 591 2.4 3.4 3.1 to 3.7 1.7 to 4.9 cannot tell (STRADDLES_EDGE) 82
row-record quake.prob.5_10: value 0.068, lo 0.0461, hi 0.0918, unit 436 of 6,411, outcome CONSISTENT, as printed: 5 to 10 percent, not including 10 6,411 436 7.1 6.8 6.2 to 7.4 4.6 to 9.2 consistent 80
row-record quake.prob.10_20: value 0.1058, lo 0.0747, hi 0.1366, unit 601 of 5,682, outcome BELOW, as printed: 10 to 20 percent, not including 20 5,682 601 14.4 10.6 9.8 to 11.4 7.5 to 13.7 below 77
row-record quake.prob.20_40: value 0.1935, lo 0.1515, hi 0.2368, unit 954 of 4,931, outcome BELOW, as printed: 20 to 40 percent, not including 40 4,931 954 28.5 19.4 18.3 to 20.5 15.2 to 23.7 below 74
row-record quake.prob.40_60: value 0.3383, lo 0.2645, hi 0.4114, unit 915 of 2,705, outcome BELOW, as printed: 40 to 60 percent, not including 60 2,705 915 49.3 33.8 32.1 to 35.6 26.5 to 41.1 below 58
row-record quake.prob.60_80: value 0.4277, lo 0.3054, hi 0.5607, unit 802 of 1,875, outcome BELOW, as printed: 60 to 80 percent, not including 80 1,875 802 69.5 42.8 40.6 to 45.0 30.5 to 56.1 below 46
row-record quake.prob.80_90: value 0.625, lo 0.4908, hi 0.756, unit 470 of 752, outcome BELOW, as printed: 80 to 90 percent, not including 90 752 470 84.9 62.5 59.0 to 65.9 49.1 to 75.6 below 37
row-record quake.prob.90_99: value 0.7747, lo 0.6691, hi 0.8604, unit 636 of 821, outcome BELOW, as printed: 90 to 99 percent, not including 99 821 636 95.2 77.5 74.5 to 80.2 66.9 to 86.0 below 32
row-record quake.prob.99_100: value 0.9779, lo 0.959, hi 0.9912, unit 1,237 of 1,265, outcome BELOW, as printed: 99 to 100 percent 1,265 1,237 99.9 97.8 96.8 to 98.5 95.9 to 99.1 below 21
row-record quake.prob.mainshock: value 0.002, lo 0.0, hi 0.0044, unit 63 of 32,034, outcome CONSISTENT, as printed: 63 of 32,034 windows saw one against a mean stated chance of 0.4 percent, and the reading is consistent.
row-record quake.prob10.all: value 0.3114, lo 0.2431, hi 0.3866, unit 5,615 of 18,031, outcome BELOW, as printed: every magnitude, every window 18,031 5,615 41.8 31.1 30.5 to 31.8 24.3 to 38.7 below 77
row-record quake.prob10.m3: value 0.3034, lo 0.2309, hi 0.3836, unit 3,822 of 12,597, outcome BELOW, as printed: M3 and above 12,597 3,822 44.5 30.3 29.5 to 31.1 23.1 to 38.4 below 77
row-record quake.prob10.m4up: value 0.33, lo 0.2446, hi 0.4195, unit 1,793 of 5,434, outcome CANNOT_TELL, as printed: M4 and above, M5 and above, M6 and above and M7 and above 5,434 1,793 35.6 33.0 31.8 to 34.3 24.5 to 41.9 cannot tell (STRADDLES_EDGE) 52
row-record quake.prob10.day: value 0.2375, lo 0.1387, hi 0.3385, unit 336 of 1,415, outcome BELOW, as printed: every magnitude, 1 day 1,415 336 36.1 23.8 21.6 to 26.0 13.9 to 33.9 below 54
row-record quake.prob10.week: value 0.2102, lo 0.1302, hi 0.3088, unit 867 of 4,125, outcome BELOW, as printed: every magnitude, 1 week 4,125 867 36.7 21.0 19.8 to 22.3 13.0 to 30.9 below 73
row-record quake.prob10.month: value 0.2376, lo 0.1649, hi 0.3267, unit 1,732 of 7,291, outcome BELOW, as printed: every magnitude, 1 month 7,291 1,732 39.6 23.8 22.8 to 24.8 16.5 to 32.7 below 73
row-record quake.prob10.year: value 0.5154, lo 0.4215, hi 0.6034, unit 2,680 of 5,200, outcome CANNOT_TELL, as printed: every magnitude, 1 year 5,200 2,680 50.7 51.5 50.2 to 52.9 42.1 to 60.3 cannot tell (STRADDLES_EDGE) 41
row-record quake.first.m3: value 0.9293, lo 0.8824, hi 0.9567, unit 670 of 721, outcome CANNOT_TELL, as printed: 670 of 721 inside, 92.9 percent, with a sequence interval of 88.2 to 95.7 percent.
