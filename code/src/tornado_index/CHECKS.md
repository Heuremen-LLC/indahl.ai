# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## Data access and terms (scouted 10 Nov 2026)
- NOAA SPC products, database and storm reports: public domain. The SPC data page sets no licence and says the data "are used by the NWS for verification purposes and may not accurately reflect all storm events".
- Iowa Environmental Mesonet: "The materials found on this website are in the public domain and may be used freely by anyone for any lawful purpose." Attribution requested, given on the page.
- US Census cartographic boundary files: public domain.
- Requests one at a time, 1.5 s apart, user agent heuremen-tornado/0.1 (+https://indahl.ai/tornado).

## 2026-11-10 10:40 TORNADO first read and ship after the outside referee: SPC 1300 UTC Day 1 tornado bands on an 80 km grid against the SPC tornado database 2007 to 2025, Kansas and Tornado Alley apart, 2026 preliminary, NWS warnings against the GPRA goals
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: PLAN.md committed 447599c at 09:27:46 -05:00 (sha256 40153979, data/plan_seal.json), first comparison 14:33:12Z, plan unchanged since. Same quantity both sides: a stated chance of one or more tornadoes within 25 miles of a point in the outlook period, against a tornado track within 25 statute miles (40.234 km) of the grid point with its start in the period. The none: point-days under 2 percent, 8,320,020 rows with 3,358 hits (0.040 percent, interval 0.038 to 0.042), counted and read. Nothing returned kept apart: 15 days with no cycle 13 outlook, 0 unreadable, 0 preliminary days missing, 0 warning years missing, 60 CIG layers outside the stated set (2026 only), 312 tornadoes in the 1200 to 1300 UTC gap
- II: holds: every band prints point-days, days, hits, share, interval and reading apart. Cannot tell is never folded. The three closed cells read: United States 3 consistent, 1 above, 4 cannot tell (3 of them under 30 days). Kansas 2 consistent, 6 cannot tell. Tornado Alley 3 consistent, 1 above, 4 cannot tell
- III: holds: the one above band keeps its side and size: United States 10 to 15 percent, 1,546 of 8,760 point-days on 502 days, 17.65 percent (day bootstrap 16.25 to 19.04, whole-year bootstrap 15.11 to 20.25, both above 15). Tornado Alley 10 to 15: 17.25 percent, 15.24 to 19.29 (day), above, and cannot tell under whole-year resampling (14.67 to 20.59), shown in the summary as display only. Kansas 10 to 15: 541 point-days, 96 days, 15.53 percent, 11.87 to 19.65, cannot tell
- V: holds: plan ruler is the band [L, next L) with the day-block bootstrap. Two more rulers are display only and decide nothing: the contour value as a point (every United States contour with 30 or more days reads above, referee R4) and whole-year resampling. Brier skill, the plan's second ruler: United States 0.0579 (0.0530 to 0.0625), Kansas 0.0605, Tornado Alley 0.0561, all above zero
- VI: holds: four outcomes kept, both alternatives in the plan. Hatched EF2 or stronger against 10 percent or more: United States 723 of 7,454, 9.70 percent (8.18 to 11.27) cannot tell. Kansas 31 of 497, 6.24 percent (3.18 to 9.87) below. Tornado Alley 164 of 2,270, 7.22 percent (5.49 to 8.98) below. Upper bound with every unrated tornado read as EF2 or stronger: 10.55, 7.04, 9.08 percent (referee R5). Warnings FY2008 to FY2025 pooled, 23,092 tornadoes, 50,758 warnings: detection 62.69 percent (61.45 to 63.94) below 72, lead 9.75 min (9.36 to 10.16) below 13, false alarms 71.20 percent (70.36 to 72.04) cannot tell against 71. Polygon-end floor (referee R6, display only): 34.73, 2.64, 78.17
- R: holds: counts read from summary_tornado.json of the run at 15:4x UTC on the raw files of the first read. Gate 2 (stated reader): 30 of 30 point-days agree with IEM outlook_by_point at one minute after the product issue time (summary gates.point_check). Gate 3 raw row: database line 70272 `2410131430-01,2024,10,13,2024-10-13,14:30:00,3,MI,...,2024-10-13,14:31:00` reads start 2024-10-13 20:30 UTC and end 20:31 UTC (CST plus 6 hours). The referee read `2011-04-27 00:12 CST` as 06:12 UTC, matching. Referee recount (tornado_index_referee/code, own shapefile reader, Albers, ray casting, distance, warning segments, seed 987654): every count, hit, share, outcome and Brier figure identical on the same grid, warnings within 0.0006 (edge convention, R9)
- P1: holds: quotes copied from fetched pages on 10 Nov 2026: spc.noaa.gov/misc/about.html (probability definition, valid period), spc.noaa.gov/publications/mkay/probver (80 km grid, 1300 and 2000 UTC outlooks, hatched caption "10% or greater chance of 1 or more F2 or stronger tornadoes"), OIG-25-026-I Box 1 page 11 (POD, lead, FAR definitions and goals 72, 13, 71) and Finding III
- P2: holds: page figures come from summary_tornado.json through build_page.py and tornado_headline.py, the feed /tornado/live.json is the same summary without the year table, ledger rows tornado.* cite this file
- P3: holds: probability, contour, hatched, POD, lead time and FAR as the sources name them. Detection, false alarms and point-day are defined on the page
- P4: holds: no cause named for any reading. The page says a reading says how often tornadoes came where a band was drawn and not why
- P5: holds: every interval labelled a 95 percent day-block bootstrap percentile interval, the whole-year interval named as such
- P6: fixed: referee R1 (grid rectangle clipped 11 points of the 48 states, now 1,230 points, rerun), R2 (nine of the fifteen days hold a 1300 UTC product under another cycle label, now listed), R2b (29 days scored from 1300 UTC with a later product, stated), R3 (the page no longer says it follows the paper's method or uses its only issuance), R4 (contour value column), R5 (unrated share and bound), R6 (polygon held to expire, floor printed, earliest-warning rule named), R10 (headline names the three thin bands apart), R11 (hatched definition cited to Kay and Brooks), R12 (CIG change dated March 2026). R7 (33 duplicate warning rows, below 0.001) and R9 (matplotlib may count a point on an edge as inside, 8 of 1,460 preliminary reports) noted here and not changed
- P7: holds: ledger rows written before the site edit, release through ledger/ship.sh only
- P8: cannot tell: checked after the ship on the live page
- P9: holds: lint_copy.py gives 2 hits, both the capital I in the report name OIG-25-026-I read as first person, cleared here. No semicolons, no digits in headings, Heuremen LLC named
- P10: holds: after-data additions are display only and listed in summary_tornado.json after_data_note. The grid rectangle change restores the plan's own rule. No band, threshold, cell, ruler or outcome definition changed. The preliminary hatched cells read cannot tell because no preliminary report carries a rating, the rule's unreadable case
- O1: holds: rider on the tick bus every 222 ticks (about daily), with --publish putting tornado_live in the site KV, served at /tornado/live.json
- O2: holds: a failed fetch names its file in sources.stale and the run falls back to the last copy. A failed gate turns every outcome into cannot tell and keeps the original
- O3: n/a: no GPU, CPU arithmetic only (numpy, matplotlib Path)
- O4: holds: the feed carries generated and updated, data/tornado_history.jsonl gets one line per run
- O5: holds: tornado_tick.py chdirs to its own folder, wrangler called by absolute path with PATH set as NEO does
- O6: n/a: no GPU job runs in this rider

## 2026-11-12 10:34 TORNADO migrated to the Faults and Guards 2.0 outcome rule (PLAN_ADDENDUM_std2.md): warning goals read as one-sided bounds, reasons beside CANNOT_TELL, REQ-13 lines, display column against the contour value never consistent
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: data, sources, grid, frame, cells, bands, warning definitions, gates and the day-level bootstrap (2,000 draws, seed 20261110) unchanged. The offline re-run (15:32 UTC) gave the same cells, years, warnings, sources and nothing-returned numbers as the 14:27 UTC summary, compared field by field with outcome, reason and display fields set aside
- II: holds: the readings that moved are counted by kind. Two yearly FAR rows (FY2022, FY2025) CONSISTENT to BELOW, 24 display readings against the contour value CONSISTENT to CANNOT_TELL. No band reading and no POD or lead reading changed word
- III: holds: ABOVE and BELOW keep their sides. The two FAR rows moved to BELOW, meaning the false alarm ratio is at or under 71 percent and the goal is met, and the page says so beside the table
- V: holds: the ruler is the plan's. The addendum 1833981 with its correction, committed before the new run, reads the goals as one-sided bounds with the goal itself counting as met, keeps the bands' edge convention [lo, hi) and names no size that matters
- VI: holds: four outcomes with a reason on every CANNOT_TELL (headline bands 1 STRADDLES_EDGE, 2 TOO_WIDE_TO_RESOLVE, 1 NO_INTERVAL_FORMABLE). Both-alternatives test not applied because the plan names no size that matters, said on the page. A goal reading never prints CONSISTENT, checked in the rule selftest
- R: holds: the REQ-13 lines are computed by K.req13 in tornado_tick.py from the run (headline 15 NOTHING_RETURNED, CANNOT_TELL 4 of 8, warnings 0 NOTHING_RETURNED, CANNOT_TELL 23 of 63). The 15 are the days with no 1300 UTC outlook, listed apart. The plan seal is untouched
- P1: holds: the quoted SPC and OIG text on the page was not touched
- P2: holds: page figures come from summary_tornado.json through build_page.py and tornado_headline.py, the feed carries reason and req13 on the cells, the headline rows and the forecasters rows
- P3: holds: goal readings keep the plan's wording of the goals. The page explains that above means a met goal for detection and lead and a missed goal for false alarms
- P4: holds: no cause named for a band or a goal that cannot be told
- P5: holds: the interval note still names the day bootstrap and that it does not cover neighbouring days
- P6: fixed: the old note said consistent if the whole interval was at or above the goal, which a one-sided threshold may not print. The note now says above, below or cannot tell for the goals, and lists the three reasons for the bands
- P7: holds: no ledger row changes outcome, two rows (tornado.ks.band10_15 and tornado.us.bss) carry surface text that now includes the reason and were re-recorded with ledger.py off and on before any page ships. Nothing shipped, ship.sh not run
- P8: cannot tell: the page was built to tornado.html and read as text, it was not rendered in a browser because nothing was deployed
- P9: holds: lint_copy.py 2 hits, both the letter I in the report number OIG-25-026-I inside quoted text, the same hits as before this change, no semicolons in the added text
- P10: n/a: no label added after the data, the retired rule is stated in the addendum dated before the run
- O1: holds: the rider on the tick bus is unchanged, tornado_tick.py --offline re-ran from the stored files with no network and --selftest passed
- O2: holds: failed reads are counted as NOTHING_RETURNED beside the headline and listed apart, a failed gate turns every outcome into CANNOT_TELL with reason NO_INTERVAL_FORMABLE and keeps outcome_before_gate
- O3: n/a: no GPU used
- O4: holds: the offline run wrote summary, live feed and a history row, the live row reads it as before
- O5: holds: paths and imports unchanged, numpy plus the desk's kit copy
- O6: n/a: no GPU job started by this change
