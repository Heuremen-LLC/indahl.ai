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
