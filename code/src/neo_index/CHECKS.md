# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-10 06:40 NEO desk first read: JPL close-approach distance ranges stated from an earlier orbit solution against the latest solution, by lead, from archived copies since 2024
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: PLAN.md committed 2314da1 at 06:07:37 -05:00 (sha256 1a571404, data/plan_seal.json), first comparison 11:14:08Z, plan file unchanged since. Same quantity both sides (dist, dist_min, dist_max in au from the same API, version 1.5 on all 58 used copies and the current record). The none is the same-solution row: 195 rows whose latest orbit_id equals the stated one, 195 agree to 1 part in 100,000. Drops by reason, all leads cell: same solution 161, edge 37, wide range 21, no record 1 (2024 BY15, JPL answers object not found), not yet 5,915. Statements outside the frame 27,031 and copied after the approach 3,503 are counted and not scored. None of the drop rules reads the outcome
- II: holds: every cell prints inside, farther and closer apart, never a net (all leads 465 inside, 8 farther, 6 closer of 479). Repeat floor: the same-solution rows show zero moves, so a move is a change of solution and not read noise. No chance figure is compared with the count of outside rows
- III: holds: outside rows keep their side and are dated: 8 above and 6 below, all in the cell stated more than 30 days ahead. The two shorter cells have none (193 of 193 and 100 of 100). Shift printed signed in stated sigma and in km
- V: holds: plan ruler is the latest solution's whole 3-sigma interval against the stated range, 95% Wilson, object counted once. Two other rulers computed after the data and not used for the outcome: latest nominal as a point (500 of 516 inside, 95.0 to 98.1 percent) and every row counted (623 of 645, 94.9 to 97.7 percent). All three read below for all leads and for more than 30 days. They differ on 8 to 30 days: object-once and the point ruler read cannot tell (100 of 100, 105 of 105), every-row reads below (155 of 161), where six later statements of approaches whose first statement was made earlier fall in that lead and read outside. The plan ruler decides
- VI: holds: four outcomes kept, both alternatives stated in the plan. Cells: all leads BELOW (95.2 to 98.2 percent against 99.7), 0 to 7 days CONSISTENT (193 of 193, lower bound 98.05), 8 to 30 days CANNOT_TELL (100 of 100, lower bound 96.3), more than 30 days BELOW (172 of 186, 87.8 to 95.5 percent). August 2026 subset CANNOT_TELL (14 of 14 scored, 7 cannot tell). The 99.7 percent is named as our reading. Size that matters: 11 of the 14 outside rows moved under 2,000 km on stated ranges 58 to 961 km wide, the other three moved 2,859, 24,116 and 338,072 km
- R: holds: counts read from summary_neo.json and data/neo.json of this run. Two rows read against raw text: 2007 DB61 stated in cad_20240209054243 (orbit 17, 0.0229416956781118, range 0.0229407728638919 to 0.022942618500816) and latest in cad_current.json under its number 887773 (orbit 32, 0.0229532982735211). 2017 WJ2 stated orbit 5, 0.0399993405263048, range 0.0381962016296112 to 0.0513871035773619, latest orbit 12, 0.0377394695502412. Reader gate rows are in data/known_good_rows.json, one replaced before the first full read because its copy was a Ceres query that the frame excludes. An earlier run stopped on a gate (reader) and printed every outcome as cannot tell, as designed
- P1: holds: the two API definitions and the CNEOS sentence ("Earth close-approach statistics for a given NEO can change (often by large amounts) as new data become available and the orbit is updated.") copied from the fetched pages ssd-api.jpl.nasa.gov/doc/cad.html and cneos.jpl.nasa.gov/ca/neo_ca_info.html on 10 Nov 2026
- P2: holds: page names the API and its version, links each outside row to its archived copy, and its figures live in summary_neo.json (cells, outside_range, august_rows) and data/neo.json (every row)
- P3: holds: nominal, minimum, maximum and 3-sigma as JPL prints them. "Farther" and "closer" are our words for above and below the stated range and the note defines them
- P4: holds: page says a later distance outside the range is a later distance outside the range and does not say why it moved. No ephemeris, force model, astrometry or weighting cause is named in the page, plan or summary
- P5: holds: every interval is labelled a 95% Wilson interval, the stated and latest ranges are labelled 3-sigma, the shift is labelled as nominal move over one sixth of the stated range
- P6: caught: the first draft said most rows come from the 9 February 2024 copy. That is true of rows read (14,667 of 15,283) and not of scored rows (170 of 479). The page now gives both the scored share and that the copy holds 13 of the 14 outside rows. Without that copy the scored rows are 308 of 309 inside (98.2 to 99.9 percent), stated in this file as an after-data check
- P7: n/a: not shipped by this agent. No ledger line, no site build edit, no tick bus edit. Bones places the page and ships through ship.sh
- P8: holds: neo.html parsed with every tag closed, 42 table rows, visible text read in full. It uses /style.css from the site, so the look is checked only when the site build places it
- P9: holds: lint_copy.py on neo.html gives 0 hits (no semicolons, no AI statements, no judgement words, no cause wording, no digits in headings). Heuremen LLC named, "our reading" and "this desk" for first person
- P10: holds: three additions after the data are labelled here and are display only: the move in km (addition 1), the count of scored and outside rows by copy day, and the two extra rulers in V. No rule, threshold, lead cell or outcome definition changed after the plan
- O1: cannot tell: the rider is not on the tick bus. Bones places it. No timer installed by this agent
- O2: holds: a failed fetch names its source in sources.stale and the run falls back to the last copy. A 400 from JPL is not retried. A failed gate turns every scored outcome into cannot tell and keeps the original
- O3: n/a: no GPU used, network reads and arithmetic on the CPU
- O4: holds: summary carries generated time, first and last stated copy times, own_first_copy, and data/neo_history.jsonl gets one line per run
- O5: holds: neo_tick.py chdirs to its own folder and every path is under it. Standard library only
- O6: n/a: no GPU job runs in this rider

## Data access and terms (scouted 10 Nov 2026)
- JPL SSD/CNEOS APIs (cad.api, sbdb.api, sentry.api, horizons.api), keyless. Fair use policy at https://ssd-api.jpl.nasa.gov/doc/index.php: requests limited to those reasonably necessary, cache and reuse, one request at a time, back off on errors, an application-specific User-Agent with product name, version and contact information, no embedding of the APIs in a website, check the version field. The rider sends heuremen-neo/0.1 (+https://indahl.ai/neo), one request at a time, 1.5 s apart. The contact in the User-Agent is the page address, which does not exist until the page ships.
- Earlier solutions: not served by JPL. cad.api is current only. sbdb.api returns one orbit and alt-orbits is empty for asteroids. Horizons prints one solution per asteroid. Sentry removed list has designation and removal time only.
- Internet Archive: 83 copies of cad.api responses since January 2024, 58 with usable Earth data, read through the CDX index and raw-copy addresses.
- Sentry: summary (2,242 objects) and removed list (3,597) stored once a day in data/snapshots, not scored.
- MPC: circulars carry dated elements and no close-approach range. Not used. Its terms page was not located at the addresses tried.
- Own copies: data/snapshots/cad_*.json.gz, at most one per 6 hours, tracked in git because they cannot be fetched again.

## 2026-11-10 08:55 NEO ship after the outside referee: referee fixes R1 and R3 to R6 in the page and the headline, ledger rows for the four lead cells and the dependence figures, page at /neo under ATLAS, feed /neo/live.json, rider publishing on the tick bus
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is unchanged from the first read (195 same-solution rows, 195 agree to 1 part in 100,000). The referee recount (neo_index_referee/code/recount.py, own reader, own aliasing, own Wilson) reproduces every row outcome and headline flag of data/neo.json, 0 differences in 15,283 rows. Drops by reason are the first read's
- II: holds: every cell still prints inside, farther and closer apart. The new dependence block prints each cell again without the copy of 9 February 2024 (all leads 308 of 309, 0 to 7 days 185 of 185, 8 to 30 days 99 of 99, more than 30 days 24 of 25) beside the plan reading, never in place of it
- III: holds: outside rows keep their side and are dated (8 farther, 6 closer, all stated more than 30 days ahead). Lopsided stated ranges are flagged by the code (2022 CE2 at 0.009 of its range, 1999 AO10 at 0.0044, 2017 WJ2 at 0.1367) and the page says why a small shift in stated sigma can still leave such a range
- V: holds: the plan ruler decides. Two more rulers are printed as display only: each cell against 98.9 percent (1 - exp(-4.5), the share of a two-dimensional normal inside its 3-sigma ellipse, from the CNEOS wording "based on the 3-sigma Earth target-plane error ellipse"), which gives the same outcome in all four cells, and the outcome a consistent cell at its floor would take with one row outside (0 to 7 days: cannot tell)
- VI: holds: four outcomes kept. Cells unchanged: all leads BELOW (465 of 479, 95.2 to 98.2 percent), 0 to 7 days CONSISTENT (193 of 193, lower bound 98.05), 8 to 30 days CANNOT_TELL (100 of 100), more than 30 days BELOW (172 of 186). Without the copy of 9 February 2024 all leads reads consistent and 0 to 7 days reads cannot tell, and the headline says the first of these
- R: holds: counts read from summary_neo.json of the offline run at 13:5x UTC on the same raw files as the first read (generated field). The dependence block, nominal_position and lopsided were added after the data at the referee and are labelled in summary_neo.json after_data_note
- P1: holds: API definitions and the CNEOS legend sentence rechecked on the fetched pages ssd-api.jpl.nasa.gov/doc/cad.html, cneos.jpl.nasa.gov/ca/ and cneos.jpl.nasa.gov/ca/neo_ca_info.html on 10 Nov 2026. The uncertainties page measures the minimum to Earth's surface where the table legend and the API say center. Noted here, not printed
- P2: holds: page figures come from summary_neo.json through build_page.py and neo_headline.py, the feed /neo/live.json is the same summary, every outside row links its archived copy, the ledger rows neo.* cite summary_neo.json
- P3: holds: nominal, minimum, maximum and 3-sigma as JPL prints them. Farther and closer defined on the page
- P4: holds: no cause named for any move. The lopsided note describes the stated range, not why the object moved. The independence sentence says rows from one copy share one moment of JPL's data and names no cause
- P5: holds: every interval labelled a 95% Wilson interval, the 98.9 percent labelled as the share inside a 3-sigma ellipse under a normal distribution
- P6: fixed: referee R4. The draft headline led with the pooled cell and kept the dependence at the bottom. The headline line now says all outside rows were stated more than 30 days ahead, 13 come from one archived copy of 9 February 2024 holding 161 of the 186 statements made that far ahead, without it 308 of 309 are inside, and the 0 to 7 day result with its one-row fragility. Referee R3: the 32 percent sentence is removed
- P7: holds: ledger rows written before the site edit, release through ledger/ship.sh only, live check after the ship
- P8: cannot tell: checked after the ship on the live page (recorded in the ship report)
- P9: holds: lint_copy.py 0 hits on neo.html, no semicolons, no digits in headings, Heuremen LLC named, our reading marked
- P10: holds: after-data additions are display only and labelled in summary_neo.json and in this entry. No rule, threshold, lead cell or outcome changed
- O1: holds: the rider was already on the tick bus every 60 ticks. It now runs with --publish and puts neo_live in the site KV. The worker serves it at /neo/live.json. TAPE and the activity tags list neo
- O2: holds: a failed KV put is logged as publish FAILED and added to sources.stale in the summary
- O3: n/a: no GPU used, network reads and arithmetic on the CPU only
- O4: holds: the feed carries updated and generated, the live_headline row reads it as stale after 9 h
- O5: holds: neo_tick.py chdirs to its own folder, wrangler is called by absolute path with PATH set as the WATER rider does
- O6: n/a: no GPU job runs in this rider

## 2026-11-11 06:54 NEO ship after second outside referee (11 Nov): once-per-object by latest designation, lead-split headline, three display additions, run lock
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is unchanged. Same-solution rows still agree on distance (gate join passed on the run). Second referee recount (neo_index_referee/recount.py, own reader) reproduced every row outcome, reason, copy and lead of data/neo.json, 0 differences in 15,299 rows, and 19 of 19 live JPL spot-checks matched to 1e-9 au
- II: holds: every cell still prints inside, farther and closer apart. Cell readings are unchanged: 0 to 7 days CONSISTENT (193 of 193, lower bound 98.05), 8 to 30 days CANNOT_TELL (100 of 100), more than 30 days BELOW (172 of 186). The dependence block still prints each cell without the copy of 9 February 2024 beside the plan reading
- III: holds: outside rows keep their side and date (8 farther, 6 closer, all stated more than 30 days ahead). Added after the data: 11 of the 14 stated ranges were under 1,000 km wide, computed in neo_tick.py (more.outside_under_1000km_wide)
- V: holds: the plan ruler decides. Added after the data and display only: the later nominal distance read alone against the stated range, counting rows that cross an edge, 500 of 516 inside, which reads the same as the plan ruler
- VI: fixed: post-seal bookkeeping fix, by the plan's own words "an object is counted once". neo_tick.py cell() and once_all() keyed the count on the stated designation, so 2014 FP47 and 671076 (one object under two names) were two rows in all leads. They are now keyed on the latest record designation (latest_des). Before: all leads 479 scored, 465 inside, 8 farther, 6 closer, 95.15 to 98.25, BELOW. After: all leads 478 scored, 464 inside, 8 farther, 6 closer, 95.1 to 98.2, BELOW (all leads BELOW (464 of 478, 95.1 to 98.2 percent)). The other three lead cells are unchanged because the two rows sit in different lead cells. No threshold, rule or outcome moved
- R: holds: every count on the page is read from summary_neo.json of the offline run on 11 Nov 2026 (generated field) over the same raw files. Cannot tell counts moved since the first ship because new own copies and new rows came in (all leads 227, 0 to 7 days 52, more than 30 days 166). Added after the data and marked on the page: the over-365-day split (the copy of 9 February 2024 gives 169 of the 478 scored rows and 13 of the 14 outside, and all 91 scored statements made more than 365 days ahead are from it, 80 inside, from other copies more than 30 days ahead 25 scored and 24 inside)
- P1: holds: quotes unchanged from the 10 Nov entry
- P2: holds: page figures come from summary_neo.json through build_page.py and neo_headline.py, the feed /neo/live.json is the same summary, the ledger rows neo.* cite this file
- P3: holds: nominal, minimum, maximum and 3-sigma as JPL prints them. Farther and closer defined on the page
- P4: holds: no cause named for any move. The new sentences describe the stated ranges and the copies, not why the object moved
- P5: holds: every interval labelled a 95% Wilson interval, the 98.9 percent labelled as the share inside a 3-sigma ellipse under a normal distribution
- P6: fixed: referee 2 item 6. The lead now opens with the lead-time split, the 0 to 7 day result first (193 of 193, consistent, one row outside would make it cannot tell), then the all-leads reading below, then that it rests mostly on the one copy of 9 February 2024 with the without-that-copy figure (308 of 309, consistent). The filler sentence about a later distance outside the range is deleted
- P7: holds: ledger rows written before the site edit, release through ledger/ship.sh inside ledger/site_lock.py only, live check after the ship
- P8: cannot tell: checked after the ship on the live page (recorded in the ship report)
- P9: holds: lint_copy.py 0 hits on neo.html, no semicolons, no counts of our own things in headings, Heuremen LLC named, our reading marked. The counts in the lead are JPL approaches, not our pages
- P10: holds: after-data additions are display only, each says it was added after the data on the page, and the after_data_note in summary_neo.json names them. No rule, threshold, lead cell or outcome changed
- O1: holds: the rider is already on the tick bus every 60 ticks with --publish. A run lock was added in neo_tick.py (fcntl non-blocking flock on neo_index/.neo_tick.lock, exit 0 quietly when held) because a run can take about 4 minutes. tick_bus.py is unchanged
- O2: holds: a failed KV put is logged as publish FAILED and added to sources.stale in the summary
- O3: n/a: no GPU used, network reads and arithmetic on the CPU only
- O4: holds: the feed carries updated and generated, the live_headline row reads it as stale after 9 h
- O5: holds: neo_tick.py chdirs to its own folder, the lock path is absolute from its own folder, wrangler is called by absolute path with PATH set
- O6: n/a: no GPU job runs in this rider

## 2026-11-11 11:16 NEO desk refresh record: the rows as shipped, recomputed from the run of 2026-11-11T14:23:11Z and the page built from it (durable source for the neo.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_neo.json of the run at 2026-11-11T14:23:11Z, the same run neo.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: farther and closer are separate columns in the cell lines, cannot tell is never folded into a share
- V: holds: one ruler, the stated 3-sigma range against the later range, read against 99.7 percent on a 95 percent Wilson interval as the plan states
- VI: holds: outcomes as the plan states them, counts of cannot tell sit beside each cell
- R: holds: counts from the summary of 2026-11-11T14:23:11Z, no number typed by hand, after-data additions keep their after-the-data label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell or the display count and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record neo.cell.all: value 0.9707, lo 0.9514, hi 0.9825, unit 464 of 478, outcome BELOW, as printed: all leads 478 464 8 6 97.1 95.1 to 98.2 below 228
row-record neo.cell.lead0_7: value 1.0, lo 0.9805, hi 1.0, unit 193 of 193, outcome CONSISTENT, as printed: 0 to 7 days 193 193 0 0 100.0 98.0 to 100.0 consistent 53
row-record neo.cell.lead8_30: value 1.0, lo 0.963, hi 1.0, unit 100 of 100, outcome CANNOT_TELL, as printed: 8 to 30 days 100 100 0 0 100.0 96.3 to 100.0 cannot tell 9
row-record neo.cell.lead30: value 0.9247, lo 0.8776, hi 0.9546, unit 172 of 186, outcome BELOW, as printed: more than 30 days 186 172 8 6 92.5 87.8 to 95.5 below 166
row-record neo.august2026: value 1.0, lo 0.7847, hi 1.0, unit 14 of 14, outcome CANNOT_TELL, as printed: 14 rows are scored, 14 inside, 0 farther and 0 closer, and 7 cannot tell.
row-record neo.dep.copy20240209: value 169, lo None, hi None, unit of 478 scored, 13 of 14 outside, outcome COUNT, as printed: It was made on 9 February 2024 and it gives 169 of the 478 scored rows and 13 of the 14 rows outside the range.
row-record neo.dep.without: value 0.9968, lo 0.9819, hi 0.9994, unit 308 of 309, outcome CONSISTENT, as printed: Without that copy 308 of 309 scored rows are inside and the first row reads consistent, and the 0 to 7 day cell holds 185 of 185 and reads cannot tell.
row-record neo.more.narrow: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: 11 of the 14 stated ranges were under 1,000 km wide.
row-record neo.more.nominal: value 500, lo None, hi None, unit of 516, outcome COUNT, as printed: 500 of 516 are inside, which reads the same.
row-record neo.more.other30: value 24, lo None, hi None, unit of 25, outcome COUNT, as printed: From other copies more than 30 days ahead: 25 scored, 24 inside.
row-record neo.more.over365: value 80, lo None, hi None, unit of 91, outcome COUNT, as printed: All 91 scored statements made more than 365 days ahead are from the 9 February 2024 copy, and 80 are inside.
row-record neo.outside.small: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: In 11 of these 14 rows the nominal distance moved by less than 2,000 km.

## 2026-11-11 11:34 NEO desk refresh record: the rows as shipped, recomputed from the run of 2026-11-11T16:29:29Z and the page built from it (durable source for the neo.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_neo.json of the run at 2026-11-11T16:29:29Z, the same run neo.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: farther and closer are separate columns in the cell lines, cannot tell is never folded into a share
- V: holds: one ruler, the stated 3-sigma range against the later range, read against 99.7 percent on a 95 percent Wilson interval as the plan states
- VI: holds: outcomes as the plan states them, counts of cannot tell sit beside each cell
- R: holds: counts from the summary of 2026-11-11T16:29:29Z, no number typed by hand, after-data additions keep their after-the-data label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell or the display count and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record neo.cell.all: value 0.9708, lo 0.9515, hi 0.9825, unit 465 of 479, outcome BELOW, as printed: all leads 479 465 8 6 97.1 95.2 to 98.2 below 228
row-record neo.cell.lead0_7: value 1.0, lo 0.9806, hi 1.0, unit 194 of 194, outcome CONSISTENT, as printed: 0 to 7 days 194 194 0 0 100.0 98.1 to 100.0 consistent 53
row-record neo.cell.lead8_30: value 1.0, lo 0.963, hi 1.0, unit 100 of 100, outcome CANNOT_TELL, as printed: 8 to 30 days 100 100 0 0 100.0 96.3 to 100.0 cannot tell 9
row-record neo.cell.lead30: value 0.9247, lo 0.8776, hi 0.9546, unit 172 of 186, outcome BELOW, as printed: more than 30 days 186 172 8 6 92.5 87.8 to 95.5 below 166
row-record neo.august2026: value 1.0, lo 0.7847, hi 1.0, unit 14 of 14, outcome CANNOT_TELL, as printed: 14 rows are scored, 14 inside, 0 farther and 0 closer, and 7 cannot tell.
row-record neo.dep.copy20240209: value 169, lo None, hi None, unit of 479 scored, 13 of 14 outside, outcome COUNT, as printed: It was made on 9 February 2024 and it gives 169 of the 479 scored rows and 13 of the 14 rows outside the range.
row-record neo.dep.without: value 0.9968, lo 0.982, hi 0.9994, unit 309 of 310, outcome CONSISTENT, as printed: Without that copy 309 of 310 scored rows are inside and the first row reads consistent, and the 0 to 7 day cell holds 186 of 186 and reads cannot tell.
row-record neo.more.narrow: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: 11 of the 14 stated ranges were under 1,000 km wide.
row-record neo.more.nominal: value 501, lo None, hi None, unit of 517, outcome COUNT, as printed: 501 of 517 are inside, which reads the same.
row-record neo.more.other30: value 24, lo None, hi None, unit of 25, outcome COUNT, as printed: From other copies more than 30 days ahead: 25 scored, 24 inside.
row-record neo.more.over365: value 80, lo None, hi None, unit of 91, outcome COUNT, as printed: All 91 scored statements made more than 365 days ahead are from the 9 February 2024 copy, and 80 are inside.
row-record neo.outside.small: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: In 11 of these 14 rows the nominal distance moved by less than 2,000 km.

## 2026-11-11 20:19 NEO desk refresh record: the rows as shipped, recomputed from the run of 2026-11-12T01:17:33Z and the page built from it (durable source for the neo.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_neo.json of the run at 2026-11-12T01:17:33Z, the same run neo.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: farther and closer are separate columns in the cell lines, cannot tell is never folded into a share
- V: holds: one ruler, the stated 3-sigma range against the later range, read against 99.7 percent on a 95 percent Wilson interval as the plan states
- VI: holds: outcomes as the plan states them, counts of cannot tell sit beside each cell
- R: holds: counts from the summary of 2026-11-12T01:17:33Z, no number typed by hand, after-data additions keep their after-the-data label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell or the display count and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record neo.cell.all: value 0.9709, lo 0.9517, hi 0.9826, unit 467 of 481, outcome BELOW, as printed: all leads 481 467 8 6 97.1 95.2 to 98.3 below 226
row-record neo.cell.lead0_7: value 1.0, lo 0.9808, hi 1.0, unit 196 of 196, outcome CONSISTENT, as printed: 0 to 7 days 196 196 0 0 100.0 98.1 to 100.0 consistent 51
row-record neo.cell.lead8_30: value 1.0, lo 0.963, hi 1.0, unit 100 of 100, outcome CANNOT_TELL, as printed: 8 to 30 days 100 100 0 0 100.0 96.3 to 100.0 cannot tell 9
row-record neo.cell.lead30: value 0.9247, lo 0.8776, hi 0.9546, unit 172 of 186, outcome BELOW, as printed: more than 30 days 186 172 8 6 92.5 87.8 to 95.5 below 166
row-record neo.august2026: value 1.0, lo 0.7847, hi 1.0, unit 14 of 14, outcome CANNOT_TELL, as printed: 14 rows are scored, 14 inside, 0 farther and 0 closer, and 7 cannot tell.
row-record neo.dep.copy20240209: value 169, lo None, hi None, unit of 481 scored, 13 of 14 outside, outcome COUNT, as printed: It was made on 9 February 2024 and it gives 169 of the 481 scored rows and 13 of the 14 rows outside the range.
row-record neo.dep.without: value 0.9968, lo 0.9821, hi 0.9994, unit 311 of 312, outcome CONSISTENT, as printed: Without that copy 311 of 312 scored rows are inside and the first row reads consistent, and the 0 to 7 day cell holds 188 of 188 and reads cannot tell.
row-record neo.more.narrow: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: 11 of the 14 stated ranges were under 1,000 km wide.
row-record neo.more.nominal: value 503, lo None, hi None, unit of 519, outcome COUNT, as printed: 503 of 519 are inside, which reads the same.
row-record neo.more.other30: value 24, lo None, hi None, unit of 25, outcome COUNT, as printed: From other copies more than 30 days ahead: 25 scored, 24 inside.
row-record neo.more.over365: value 80, lo None, hi None, unit of 91, outcome COUNT, as printed: All 91 scored statements made more than 365 days ahead are from the 9 February 2024 copy, and 80 are inside.
row-record neo.outside.small: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: In 11 of these 14 rows the nominal distance moved by less than 2,000 km.

## 2026-11-12 01:52 NEO desk refresh record: the rows as shipped, recomputed from the run of 2026-11-12T05:43:09Z and the page built from it (durable source for the neo.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_neo.json of the run at 2026-11-12T05:43:09Z, the same run neo.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: farther and closer are separate columns in the cell lines, cannot tell is never folded into a share
- V: holds: one ruler, the stated 3-sigma range against the later range, read against 99.7 percent on a 95 percent Wilson interval as the plan states
- VI: holds: outcomes as the plan states them, counts of cannot tell sit beside each cell
- R: holds: counts from the summary of 2026-11-12T05:43:09Z, no number typed by hand, after-data additions keep their after-the-data label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell or the display count and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record neo.cell.all: value 0.9709, lo 0.9517, hi 0.9826, unit 467 of 481, outcome BELOW, as printed: all leads 481 467 8 6 97.1 95.2 to 98.3 below 227
row-record neo.cell.lead0_7: value 1.0, lo 0.9808, hi 1.0, unit 196 of 196, outcome CONSISTENT, as printed: 0 to 7 days 196 196 0 0 100.0 98.1 to 100.0 consistent 52
row-record neo.cell.lead8_30: value 1.0, lo 0.963, hi 1.0, unit 100 of 100, outcome CANNOT_TELL, as printed: 8 to 30 days 100 100 0 0 100.0 96.3 to 100.0 cannot tell 9
row-record neo.cell.lead30: value 0.9247, lo 0.8776, hi 0.9546, unit 172 of 186, outcome BELOW, as printed: more than 30 days 186 172 8 6 92.5 87.8 to 95.5 below 166
row-record neo.august2026: value 1.0, lo 0.7847, hi 1.0, unit 14 of 14, outcome CANNOT_TELL, as printed: 14 rows are scored, 14 inside, 0 farther and 0 closer, and 7 cannot tell.
row-record neo.dep.copy20240209: value 169, lo None, hi None, unit of 481 scored, 13 of 14 outside, outcome COUNT, as printed: It was made on 9 February 2024 and it gives 169 of the 481 scored rows and 13 of the 14 rows outside the range.
row-record neo.dep.without: value 0.9968, lo 0.9821, hi 0.9994, unit 311 of 312, outcome CONSISTENT, as printed: Without that copy 311 of 312 scored rows are inside and the first row reads consistent, and the 0 to 7 day cell holds 188 of 188 and reads cannot tell.
row-record neo.more.narrow: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: 11 of the 14 stated ranges were under 1,000 km wide.
row-record neo.more.nominal: value 503, lo None, hi None, unit of 519, outcome COUNT, as printed: 503 of 519 are inside, which reads the same.
row-record neo.more.other30: value 24, lo None, hi None, unit of 25, outcome COUNT, as printed: From other copies more than 30 days ahead: 25 scored, 24 inside.
row-record neo.more.over365: value 80, lo None, hi None, unit of 91, outcome COUNT, as printed: All 91 scored statements made more than 365 days ahead are from the 9 February 2024 copy, and 80 are inside.
row-record neo.outside.small: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: In 11 of these 14 rows the nominal distance moved by less than 2,000 km.

## 2026-11-12 05:36 NEO desk refresh record: the rows as shipped, recomputed from the run of 2026-11-12T10:24:43Z and the page built from it (durable source for the neo.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_neo.json of the run at 2026-11-12T10:24:43Z, the same run neo.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: farther and closer are separate columns in the cell lines, cannot tell is never folded into a share
- V: holds: one ruler, the stated 3-sigma range against the later range, read against 99.7 percent on a 95 percent Wilson interval as the plan states
- VI: holds: outcomes as the plan states them, counts of cannot tell sit beside each cell
- R: holds: counts from the summary of 2026-11-12T10:24:43Z, no number typed by hand, after-data additions keep their after-the-data label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell or the display count and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record neo.cell.all: value 0.971, lo 0.9518, hi 0.9826, unit 468 of 482, outcome BELOW, as printed: all leads 482 468 8 6 97.1 95.2 to 98.3 below 227
row-record neo.cell.lead0_7: value 1.0, lo 0.9809, hi 1.0, unit 197 of 197, outcome CONSISTENT, as printed: 0 to 7 days 197 197 0 0 100.0 98.1 to 100.0 consistent 52
row-record neo.cell.lead8_30: value 1.0, lo 0.963, hi 1.0, unit 100 of 100, outcome CANNOT_TELL, as printed: 8 to 30 days 100 100 0 0 100.0 96.3 to 100.0 cannot tell 9
row-record neo.cell.lead30: value 0.9247, lo 0.8776, hi 0.9546, unit 172 of 186, outcome BELOW, as printed: more than 30 days 186 172 8 6 92.5 87.8 to 95.5 below 166
row-record neo.august2026: value 1.0, lo 0.7847, hi 1.0, unit 14 of 14, outcome CANNOT_TELL, as printed: 14 rows are scored, 14 inside, 0 farther and 0 closer, and 7 cannot tell.
row-record neo.dep.copy20240209: value 169, lo None, hi None, unit of 482 scored, 13 of 14 outside, outcome COUNT, as printed: It was made on 9 February 2024 and it gives 169 of the 482 scored rows and 13 of the 14 rows outside the range.
row-record neo.dep.without: value 0.9968, lo 0.9821, hi 0.9994, unit 312 of 313, outcome CONSISTENT, as printed: Without that copy 312 of 313 scored rows are inside and the first row reads consistent, and the 0 to 7 day cell holds 189 of 189 and reads consistent.
row-record neo.more.narrow: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: 11 of the 14 stated ranges were under 1,000 km wide.
row-record neo.more.nominal: value 504, lo None, hi None, unit of 520, outcome COUNT, as printed: 504 of 520 are inside, which reads the same.
row-record neo.more.other30: value 24, lo None, hi None, unit of 25, outcome COUNT, as printed: From other copies more than 30 days ahead: 25 scored, 24 inside.
row-record neo.more.over365: value 80, lo None, hi None, unit of 91, outcome COUNT, as printed: All 91 scored statements made more than 365 days ahead are from the 9 February 2024 copy, and 80 are inside.
row-record neo.outside.small: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: In 11 of these 14 rows the nominal distance moved by less than 2,000 km.

## 2026-11-12 10:25 NEO desk refresh record: the rows as shipped, recomputed from the run of 2026-11-12T15:24:46Z and the page built from it (durable source for the neo.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_neo.json of the run at 2026-11-12T15:24:46Z, the same run neo.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: farther and closer are separate columns in the cell lines, cannot tell is never folded into a share
- V: holds: one ruler, the stated 3-sigma range against the later range, read against 99.7 percent on a 95 percent Wilson interval as the plan states
- VI: holds: outcomes as the plan states them, counts of cannot tell sit beside each cell
- R: holds: counts from the summary of 2026-11-12T15:24:46Z, no number typed by hand, after-data additions keep their after-the-data label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell or the display count and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record neo.cell.all: value 0.971, lo 0.9518, hi 0.9826, unit 468 of 482, outcome BELOW, as printed: all leads 482 468 8 6 97.1 95.2 to 98.3 below 228
row-record neo.cell.lead0_7: value 1.0, lo 0.9809, hi 1.0, unit 197 of 197, outcome CONSISTENT, as printed: 0 to 7 days 197 197 0 0 100.0 98.1 to 100.0 consistent 53
row-record neo.cell.lead8_30: value 1.0, lo 0.963, hi 1.0, unit 100 of 100, outcome CANNOT_TELL, as printed: 8 to 30 days 100 100 0 0 100.0 96.3 to 100.0 cannot tell (STRADDLES_EDGE) 9
row-record neo.cell.lead30: value 0.9247, lo 0.8776, hi 0.9546, unit 172 of 186, outcome BELOW, as printed: more than 30 days 186 172 8 6 92.5 87.8 to 95.5 below 166
row-record neo.august2026: value 1.0, lo 0.7847, hi 1.0, unit 14 of 14, outcome CANNOT_TELL, as printed: 14 rows are scored, 14 inside, 0 farther and 0 closer, and 7 cannot tell.
row-record neo.dep.copy20240209: value 169, lo None, hi None, unit of 482 scored, 13 of 14 outside, outcome COUNT, as printed: It was made on 9 February 2024 and it gives 169 of the 482 scored rows and 13 of the 14 rows outside the range.
row-record neo.dep.without: value 0.9968, lo 0.9821, hi 0.9994, unit 312 of 313, outcome CONSISTENT, as printed: Without that copy 312 of 313 scored rows are inside and the first row reads consistent, and the 0 to 7 day cell holds 189 of 189 and reads consistent.
row-record neo.more.narrow: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: 11 of the 14 stated ranges were under 1,000 km wide.
row-record neo.more.nominal: value 504, lo None, hi None, unit of 520, outcome COUNT, as printed: 504 of 520 are inside, which reads the same.
row-record neo.more.other30: value 24, lo None, hi None, unit of 25, outcome COUNT, as printed: From other copies more than 30 days ahead: 25 scored, 24 inside.
row-record neo.more.over365: value 80, lo None, hi None, unit of 91, outcome COUNT, as printed: All 91 scored statements made more than 365 days ahead are from the 9 February 2024 copy, and 80 are inside.
row-record neo.outside.small: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: In 11 of these 14 rows the nominal distance moved by less than 2,000 km.

## 2026-11-12 10:26 Faults and Guards 2.0 migration: reason codes, REQ-13 line, edge convention, band for the CONSISTENT cell, addendum
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, PLAN.md is not edited and its seal in data/plan_seal.json still matches, the addendum is a new file committed as d32a397 before any reading under it
- II: n/a: no repeated item, one row per object per cell as before and the Wilson intervals are unchanged
- III: holds: farther and closer stay separate columns, every non-outcome number of summary_neo.json (scored, inside, above, below, share, lo, hi, cannot_tell and the by-why counts) compared equal in all 5 cells before and after the code change, 0 differences
- V: holds: the rule is named in PLAN_ADDENDUM_std2.md before any reading under it, ABOVE and BELOW against 0.9973 and CONSISTENT in the band 0.98 to 1.0 with closed edges, the band is the plan's own 0.98 floor with the cap of a share as its upper edge and no new tolerance
- VI: holds: four outcomes kept and every CANNOT_TELL carries one closed reason, 0 to 7 days stays CONSISTENT with interval 0.9809 to 1.0, all leads stays BELOW, 8 to 30 days stays CANNOT_TELL STRADDLES_EDGE, the both-alternatives test is not applied because the plan names no size that matters and the addendum says so
- R: holds: counts and reasons are read from summary_neo.json after re-running neo_tick.py offline, rule self-test and kit self-test passed, all leads 468 of 482, 0 to 7 days 197 of 197, row reasons 169 NO_INTERVAL_FORMABLE and 38 STRADDLES_EDGE and 21 TOO_WIDE_TO_RESOLVE in all leads, 5,930 NOTHING_RETURNED approaches not yet passed apart
- P1: n/a: no quotation of any source in this change
- P2: n/a: no new figure, every number keeps its source on the page
- P3: n/a: no setting labels of any source are touched by this change
- P4: holds: no cause is named, the added text says only which closed reason a CANNOT_TELL carries and what the edges are
- P5: holds: the Wilson 95 percent interval is still named beside each cell and the page note states the closed edges and the minimum of 10 scored rows as TOO_WIDE_TO_RESOLVE
- P6: holds: the headline line is the same sentences as before plus the reason beside cannot tell and the REQ-13 lines of the 0 to 7 day and all-leads cells read from the summary, no stronger than the reading
- P7: holds: no outcome moved so no ledger outcome changed, refresh_page.py run under the ledger lock refreshed 3 neo.* rows before any release and then 0, the owner ships with ship.sh
- P8: cannot tell: neo.html rebuilt by build_page.py and lint_copy.py reported 0 hits, but the page was not rendered in a browser or served because nothing is deployed from this session
- P9: holds: plain sentences without semicolons in the added page text, no count of our own things in any heading, lint_copy.py 0 hits
- P10: holds: the addendum is dated 12 Nov 2026 and written before any reading under the new rule, no rule set after the data

## 2026-11-12 21:19 NEO desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T01:15:54Z and the page built from it (durable source for the neo.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_neo.json of the run at 2026-11-13T01:15:54Z, the same run neo.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: farther and closer are separate columns in the cell lines, cannot tell is never folded into a share
- V: holds: one ruler, the stated 3-sigma range against the later range, read against 99.7 percent on a 95 percent Wilson interval as the plan states
- VI: holds: outcomes as the plan states them, counts of cannot tell sit beside each cell
- R: holds: counts from the summary of 2026-11-13T01:15:54Z, no number typed by hand, after-data additions keep their after-the-data label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell or the display count and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record neo.cell.all: value 0.971, lo 0.9518, hi 0.9826, unit 468 of 482, outcome BELOW, as printed: all leads 482 468 8 6 97.1 95.2 to 98.3 below 228
row-record neo.cell.lead0_7: value 1.0, lo 0.9809, hi 1.0, unit 197 of 197, outcome CONSISTENT, as printed: 0 to 7 days 197 197 0 0 100.0 98.1 to 100.0 consistent 53
row-record neo.cell.lead8_30: value 1.0, lo 0.963, hi 1.0, unit 100 of 100, outcome CANNOT_TELL, as printed: 8 to 30 days 100 100 0 0 100.0 96.3 to 100.0 cannot tell (STRADDLES_EDGE) 9
row-record neo.cell.lead30: value 0.9247, lo 0.8776, hi 0.9546, unit 172 of 186, outcome BELOW, as printed: more than 30 days 186 172 8 6 92.5 87.8 to 95.5 below 166
row-record neo.august2026: value 1.0, lo 0.7847, hi 1.0, unit 14 of 14, outcome CANNOT_TELL, as printed: 14 rows are scored, 14 inside, 0 farther and 0 closer, and 7 cannot tell.
row-record neo.dep.copy20240209: value 169, lo None, hi None, unit of 482 scored, 13 of 14 outside, outcome COUNT, as printed: It was made on 9 February 2024 and it gives 169 of the 482 scored rows and 13 of the 14 rows outside the range.
row-record neo.dep.without: value 0.9968, lo 0.9821, hi 0.9994, unit 312 of 313, outcome CONSISTENT, as printed: Without that copy 312 of 313 scored rows are inside and the first row reads consistent, and the 0 to 7 day cell holds 189 of 189 and reads consistent.
row-record neo.more.narrow: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: 11 of the 14 stated ranges were under 1,000 km wide.
row-record neo.more.nominal: value 506, lo None, hi None, unit of 522, outcome COUNT, as printed: 506 of 522 are inside, which reads the same.
row-record neo.more.other30: value 24, lo None, hi None, unit of 25, outcome COUNT, as printed: From other copies more than 30 days ahead: 25 scored, 24 inside.
row-record neo.more.over365: value 80, lo None, hi None, unit of 91, outcome COUNT, as printed: All 91 scored statements made more than 365 days ahead are from the 9 February 2024 copy, and 80 are inside.
row-record neo.outside.small: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: In 11 of these 14 rows the nominal distance moved by less than 2,000 km.

## 2026-11-13 00:38 NEO desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T03:25:41Z and the page built from it (durable source for the neo.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_neo.json of the run at 2026-11-13T03:25:41Z, the same run neo.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: farther and closer are separate columns in the cell lines, cannot tell is never folded into a share
- V: holds: one ruler, the stated 3-sigma range against the later range, read against 99.7 percent on a 95 percent Wilson interval as the plan states
- VI: holds: outcomes as the plan states them, counts of cannot tell sit beside each cell
- R: holds: counts from the summary of 2026-11-13T03:25:41Z, no number typed by hand, after-data additions keep their after-the-data label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell or the display count and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record neo.cell.all: value 0.971, lo 0.9519, hi 0.9827, unit 469 of 483, outcome BELOW, as printed: all leads 483 469 8 6 97.1 95.2 to 98.3 below 229
row-record neo.cell.lead0_7: value 1.0, lo 0.981, hi 1.0, unit 198 of 198, outcome CONSISTENT, as printed: 0 to 7 days 198 198 0 0 100.0 98.1 to 100.0 consistent 53
row-record neo.cell.lead8_30: value 1.0, lo 0.963, hi 1.0, unit 100 of 100, outcome CANNOT_TELL, as printed: 8 to 30 days 100 100 0 0 100.0 96.3 to 100.0 cannot tell (STRADDLES_EDGE) 9
row-record neo.cell.lead30: value 0.9247, lo 0.8776, hi 0.9546, unit 172 of 186, outcome BELOW, as printed: more than 30 days 186 172 8 6 92.5 87.8 to 95.5 below 167
row-record neo.august2026: value 1.0, lo 0.7847, hi 1.0, unit 14 of 14, outcome CANNOT_TELL, as printed: 14 rows are scored, 14 inside, 0 farther and 0 closer, and 7 cannot tell.
row-record neo.dep.copy20240209: value 169, lo None, hi None, unit of 483 scored, 13 of 14 outside, outcome COUNT, as printed: It was made on 9 February 2024 and it gives 169 of the 483 scored rows and 13 of the 14 rows outside the range.
row-record neo.dep.without: value 0.9968, lo 0.9822, hi 0.9994, unit 313 of 314, outcome CONSISTENT, as printed: Without that copy 313 of 314 scored rows are inside and the first row reads consistent, and the 0 to 7 day cell holds 190 of 190 and reads consistent.
row-record neo.more.narrow: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: 11 of the 14 stated ranges were under 1,000 km wide.
row-record neo.more.nominal: value 507, lo None, hi None, unit of 523, outcome COUNT, as printed: 507 of 523 are inside, which reads the same.
row-record neo.more.other30: value 24, lo None, hi None, unit of 25, outcome COUNT, as printed: From other copies more than 30 days ahead: 25 scored, 24 inside.
row-record neo.more.over365: value 80, lo None, hi None, unit of 91, outcome COUNT, as printed: All 91 scored statements made more than 365 days ahead are from the 9 February 2024 copy, and 80 are inside.
row-record neo.outside.small: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: In 11 of these 14 rows the nominal distance moved by less than 2,000 km.

## 2026-11-13 03:52 NEO desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T07:43:44Z and the page built from it (durable source for the neo.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_neo.json of the run at 2026-11-13T07:43:44Z, the same run neo.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: farther and closer are separate columns in the cell lines, cannot tell is never folded into a share
- V: holds: one ruler, the stated 3-sigma range against the later range, read against 99.7 percent on a 95 percent Wilson interval as the plan states
- VI: holds: outcomes as the plan states them, counts of cannot tell sit beside each cell
- R: holds: counts from the summary of 2026-11-13T07:43:44Z, no number typed by hand, after-data additions keep their after-the-data label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell or the display count and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record neo.cell.all: value 0.9711, lo 0.952, hi 0.9827, unit 470 of 484, outcome BELOW, as printed: all leads 484 470 8 6 97.1 95.2 to 98.3 below 229
row-record neo.cell.lead0_7: value 1.0, lo 0.9811, hi 1.0, unit 199 of 199, outcome CONSISTENT, as printed: 0 to 7 days 199 199 0 0 100.0 98.1 to 100.0 consistent 53
row-record neo.cell.lead8_30: value 1.0, lo 0.963, hi 1.0, unit 100 of 100, outcome CANNOT_TELL, as printed: 8 to 30 days 100 100 0 0 100.0 96.3 to 100.0 cannot tell (STRADDLES_EDGE) 9
row-record neo.cell.lead30: value 0.9247, lo 0.8776, hi 0.9546, unit 172 of 186, outcome BELOW, as printed: more than 30 days 186 172 8 6 92.5 87.8 to 95.5 below 167
row-record neo.august2026: value 1.0, lo 0.7847, hi 1.0, unit 14 of 14, outcome CANNOT_TELL, as printed: 14 rows are scored, 14 inside, 0 farther and 0 closer, and 7 cannot tell.
row-record neo.dep.copy20240209: value 169, lo None, hi None, unit of 484 scored, 13 of 14 outside, outcome COUNT, as printed: It was made on 9 February 2024 and it gives 169 of the 484 scored rows and 13 of the 14 rows outside the range.
row-record neo.dep.without: value 0.9968, lo 0.9822, hi 0.9994, unit 314 of 315, outcome CONSISTENT, as printed: Without that copy 314 of 315 scored rows are inside and the first row reads consistent, and the 0 to 7 day cell holds 191 of 191 and reads consistent.
row-record neo.more.narrow: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: 11 of the 14 stated ranges were under 1,000 km wide.
row-record neo.more.nominal: value 508, lo None, hi None, unit of 524, outcome COUNT, as printed: 508 of 524 are inside, which reads the same.
row-record neo.more.other30: value 24, lo None, hi None, unit of 25, outcome COUNT, as printed: From other copies more than 30 days ahead: 25 scored, 24 inside.
row-record neo.more.over365: value 80, lo None, hi None, unit of 91, outcome COUNT, as printed: All 91 scored statements made more than 365 days ahead are from the 9 February 2024 copy, and 80 are inside.
row-record neo.outside.small: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: In 11 of these 14 rows the nominal distance moved by less than 2,000 km.

## 2026-11-13 08:11 NEO desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T11:59:38Z and the page built from it (durable source for the neo.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_neo.json of the run at 2026-11-13T11:59:38Z, the same run neo.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: farther and closer are separate columns in the cell lines, cannot tell is never folded into a share
- V: holds: one ruler, the stated 3-sigma range against the later range, read against 99.7 percent on a 95 percent Wilson interval as the plan states
- VI: holds: outcomes as the plan states them, counts of cannot tell sit beside each cell
- R: holds: counts from the summary of 2026-11-13T11:59:38Z, no number typed by hand, after-data additions keep their after-the-data label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell or the display count and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record neo.cell.all: value 0.9711, lo 0.9521, hi 0.9827, unit 471 of 485, outcome BELOW, as printed: all leads 485 471 8 6 97.1 95.2 to 98.3 below 230
row-record neo.cell.lead0_7: value 1.0, lo 0.9812, hi 1.0, unit 200 of 200, outcome CONSISTENT, as printed: 0 to 7 days 200 200 0 0 100.0 98.1 to 100.0 consistent 54
row-record neo.cell.lead8_30: value 1.0, lo 0.963, hi 1.0, unit 100 of 100, outcome CANNOT_TELL, as printed: 8 to 30 days 100 100 0 0 100.0 96.3 to 100.0 cannot tell (STRADDLES_EDGE) 9
row-record neo.cell.lead30: value 0.9247, lo 0.8776, hi 0.9546, unit 172 of 186, outcome BELOW, as printed: more than 30 days 186 172 8 6 92.5 87.8 to 95.5 below 167
row-record neo.august2026: value 1.0, lo 0.7847, hi 1.0, unit 14 of 14, outcome CANNOT_TELL, as printed: 14 rows are scored, 14 inside, 0 farther and 0 closer, and 7 cannot tell.
row-record neo.dep.copy20240209: value 169, lo None, hi None, unit of 485 scored, 13 of 14 outside, outcome COUNT, as printed: It was made on 9 February 2024 and it gives 169 of the 485 scored rows and 13 of the 14 rows outside the range.
row-record neo.dep.without: value 0.9968, lo 0.9823, hi 0.9994, unit 315 of 316, outcome CONSISTENT, as printed: Without that copy 315 of 316 scored rows are inside and the first row reads consistent, and the 0 to 7 day cell holds 192 of 192 and reads consistent.
row-record neo.more.narrow: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: 11 of the 14 stated ranges were under 1,000 km wide.
row-record neo.more.nominal: value 509, lo None, hi None, unit of 525, outcome COUNT, as printed: 509 of 525 are inside, which reads the same.
row-record neo.more.other30: value 24, lo None, hi None, unit of 25, outcome COUNT, as printed: From other copies more than 30 days ahead: 25 scored, 24 inside.
row-record neo.more.over365: value 80, lo None, hi None, unit of 91, outcome COUNT, as printed: All 91 scored statements made more than 365 days ahead are from the 9 February 2024 copy, and 80 are inside.
row-record neo.outside.small: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: In 11 of these 14 rows the nominal distance moved by less than 2,000 km.

## 2026-11-13 11:27 NEO desk refresh record: the rows as shipped, recomputed from the run of 2026-11-13T16:19:23Z and the page built from it (durable source for the neo.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_neo.json of the run at 2026-11-13T16:19:23Z, the same run neo.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: farther and closer are separate columns in the cell lines, cannot tell is never folded into a share
- V: holds: one ruler, the stated 3-sigma range against the later range, read against 99.7 percent on a 95 percent Wilson interval as the plan states
- VI: holds: outcomes as the plan states them, counts of cannot tell sit beside each cell
- R: holds: counts from the summary of 2026-11-13T16:19:23Z, no number typed by hand, after-data additions keep their after-the-data label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell or the display count and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record neo.cell.all: value 0.9713, lo 0.9523, hi 0.9828, unit 473 of 487, outcome BELOW, as printed: all leads 487 473 8 6 97.1 95.2 to 98.3 below 230
row-record neo.cell.lead0_7: value 1.0, lo 0.9813, hi 1.0, unit 202 of 202, outcome CONSISTENT, as printed: 0 to 7 days 202 202 0 0 100.0 98.1 to 100.0 consistent 54
row-record neo.cell.lead8_30: value 1.0, lo 0.963, hi 1.0, unit 100 of 100, outcome CANNOT_TELL, as printed: 8 to 30 days 100 100 0 0 100.0 96.3 to 100.0 cannot tell (STRADDLES_EDGE) 9
row-record neo.cell.lead30: value 0.9247, lo 0.8776, hi 0.9546, unit 172 of 186, outcome BELOW, as printed: more than 30 days 186 172 8 6 92.5 87.8 to 95.5 below 167
row-record neo.august2026: value 1.0, lo 0.7847, hi 1.0, unit 14 of 14, outcome CANNOT_TELL, as printed: 14 rows are scored, 14 inside, 0 farther and 0 closer, and 7 cannot tell.
row-record neo.dep.copy20240209: value 169, lo None, hi None, unit of 487 scored, 13 of 14 outside, outcome COUNT, as printed: It was made on 9 February 2024 and it gives 169 of the 487 scored rows and 13 of the 14 rows outside the range.
row-record neo.dep.without: value 0.9969, lo 0.9824, hi 0.9994, unit 317 of 318, outcome CONSISTENT, as printed: Without that copy 317 of 318 scored rows are inside and the first row reads consistent, and the 0 to 7 day cell holds 194 of 194 and reads consistent.
row-record neo.more.narrow: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: 11 of the 14 stated ranges were under 1,000 km wide.
row-record neo.more.nominal: value 511, lo None, hi None, unit of 527, outcome COUNT, as printed: 511 of 527 are inside, which reads the same.
row-record neo.more.other30: value 24, lo None, hi None, unit of 25, outcome COUNT, as printed: From other copies more than 30 days ahead: 25 scored, 24 inside.
row-record neo.more.over365: value 80, lo None, hi None, unit of 91, outcome COUNT, as printed: All 91 scored statements made more than 365 days ahead are from the 9 February 2024 copy, and 80 are inside.
row-record neo.outside.small: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: In 11 of these 14 rows the nominal distance moved by less than 2,000 km.

## 2026-11-13 20:27 NEO desk refresh record: the rows as shipped, recomputed from the run of 2026-11-14T01:17:56Z and the page built from it (durable source for the neo.* ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every line below is read from summary_neo.json of the run at 2026-11-14T01:17:56Z, the same run neo.html prints, and the printed text is found in the rendered page (make_rows.py asserts it)
- II: n/a: no comparison between two runs, numbers copied as printed
- III: holds: farther and closer are separate columns in the cell lines, cannot tell is never folded into a share
- V: holds: one ruler, the stated 3-sigma range against the later range, read against 99.7 percent on a 95 percent Wilson interval as the plan states
- VI: holds: outcomes as the plan states them, counts of cannot tell sit beside each cell
- R: holds: counts from the summary of 2026-11-14T01:17:56Z, no number typed by hand, after-data additions keep their after-the-data label in the claim
- P1: n/a: no quoted text in this record
- P2: holds: each line names the cell or the display count and the page names the run date
- P3: holds: labels as the page prints them
- P4: holds: no cause named
- P5: holds: every share has its 95 percent Wilson interval in the line
- P6: holds: the lines say what the page says and nothing stronger
- P7: holds: ledger rows updated before the page ships, release through ledger/ship.sh
- P8: holds: rows compared with the rendered page text by check_ledger.py at the gate
- P9: holds: plain lines, no semicolons
- P10: n/a: no rule set after the data in this record
row-record neo.cell.all: value 0.9713, lo 0.9524, hi 0.9828, unit 474 of 488, outcome BELOW, as printed: all leads 488 474 8 6 97.1 95.2 to 98.3 below 229
row-record neo.cell.lead0_7: value 1.0, lo 0.9814, hi 1.0, unit 203 of 203, outcome CONSISTENT, as printed: 0 to 7 days 203 203 0 0 100.0 98.1 to 100.0 consistent 53
row-record neo.cell.lead8_30: value 1.0, lo 0.963, hi 1.0, unit 100 of 100, outcome CANNOT_TELL, as printed: 8 to 30 days 100 100 0 0 100.0 96.3 to 100.0 cannot tell (STRADDLES_EDGE) 9
row-record neo.cell.lead30: value 0.9247, lo 0.8776, hi 0.9546, unit 172 of 186, outcome BELOW, as printed: more than 30 days 186 172 8 6 92.5 87.8 to 95.5 below 167
row-record neo.august2026: value 1.0, lo 0.7847, hi 1.0, unit 14 of 14, outcome CANNOT_TELL, as printed: 14 rows are scored, 14 inside, 0 farther and 0 closer, and 7 cannot tell.
row-record neo.dep.copy20240209: value 169, lo None, hi None, unit of 488 scored, 13 of 14 outside, outcome COUNT, as printed: It was made on 9 February 2024 and it gives 169 of the 488 scored rows and 13 of the 14 rows outside the range.
row-record neo.dep.without: value 0.9969, lo 0.9825, hi 0.9994, unit 318 of 319, outcome CONSISTENT, as printed: Without that copy 318 of 319 scored rows are inside and the first row reads consistent, and the 0 to 7 day cell holds 195 of 195 and reads consistent.
row-record neo.more.narrow: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: 11 of the 14 stated ranges were under 1,000 km wide.
row-record neo.more.nominal: value 512, lo None, hi None, unit of 528, outcome COUNT, as printed: 512 of 528 are inside, which reads the same.
row-record neo.more.other30: value 24, lo None, hi None, unit of 25, outcome COUNT, as printed: From other copies more than 30 days ahead: 25 scored, 24 inside.
row-record neo.more.over365: value 80, lo None, hi None, unit of 91, outcome COUNT, as printed: All 91 scored statements made more than 365 days ahead are from the 9 February 2024 copy, and 80 are inside.
row-record neo.outside.small: value 11, lo None, hi None, unit of 14, outcome COUNT, as printed: In 11 of these 14 rows the nominal distance moved by less than 2,000 km.
