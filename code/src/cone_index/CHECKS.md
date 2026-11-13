# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-10 10:05 CONE desk first read: NHC official track forecasts 2010 to 2025 against HURDAT2, whole-path cone and per-lead circles, and NHC's stated average track errors recounted
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: PLAN.md committed e49ebd2 at 09:27:14 -05:00 with data/radii.json and data/stated_errors.json, before the first comparison (data/plan_seal.json). The none is the tau 0 join: 11,178 frame forecasts, median distance from the OFCL tau 0 position to the best track at the initial time 6.0 n mi (gate under 15). Set aside by reason before scoring: not a tropical cyclone at the initial time 916, East Pacific west of 140 W 755, season without radii (2012, second ruler only) 754, no best-track point at the initial time 134, no best track for the storm 29. Nothing returned is counted apart in every cell and never enters a share
- II: holds: every cell prints inside and outside apart with nothing returned beside it. Atlantic whole path 697 inside, 618 left the cone, 1,692 nothing returned. East Pacific whole path 650 inside, 456 left, 1,590 nothing returned
- III: holds: the two rulers point the same way per lead: every circle cell share is above two-thirds (68.6 to 72.6 percent) while both whole-path shares are below 60 percent at the point estimate (53.0 and 58.8). Not a contradiction: the whole path needs 19 points inside at once
- V: holds: plan ruler is the storm-level block bootstrap (2,000 resamples, seed 20261110). Whole path against NHC's stated 60 to 70 percent, circles against our 61.7 to 71.7 percent reading of two-thirds. Second ruler: NHC's yearly average track errors against our recount, 220 of 224 rows consistent
- VI: holds: four outcomes kept. Atlantic whole path CANNOT_TELL (53.0 percent, 45.1 to 60.4). East Pacific whole path CANNOT_TELL (58.8, 52.4 to 65.0). Circles: Atlantic 12 h CONSISTENT (68.7, 66.1 to 71.3), the other 13 CANNOT_TELL with upper bounds above 71.7. Second ruler: AL 111 consistent and 1 cannot tell, EP 109 consistent and 3 cannot tell
- R: holds: counts read from summary_cone.json and data/cone.json of the run at 15:0x UTC 10 Nov 2026 on HURDAT2 hurdat2-1851-2025-092326.txt and hurdat2-nepac-1949-2025-092926.txt and 625 a-deck files. Stated tables "Verification based on NHC best track database as of 5/12/26". After the data: our 60 h recount beside second-ruler rows whose case counts differ (AL 2020 72 h: NHC prints 79.9 n mi on 318 cases, our 72 h recount is 98.1 on 275, our 60 h recount is 79.8 on 319). Labelled in summary_cone.json after_data_note, display only
- P1: holds: NHC sentences copied from the fetched aboutcone.shtml, a cone graphic page, verify2.shtml and the PDF notes on 10 Nov 2026
- P2: holds: page figures come from summary_cone.json through build_page.py and cone_headline.py. Every row is in data/cone.json
- P3: holds: best track, official forecast, cone, circle and radius as NHC names them. Nothing returned defined on the page
- P4: holds: no cause named for any forecast outside the cone or for the 2020 72 h row
- P5: holds: every interval labelled a storm-level block bootstrap 95 percent interval, the circle band labelled our reading
- P6: holds: the headline gives the plan's Atlantic whole-path cell first, with its cannot tell reading
- P7: cannot tell: not shipped yet. Ledger rows, site edit and ship follow the referee
- P8: cannot tell: checked on the live page after the ship
- P9: holds: lint_copy.py, one hit, inside the NHC quote ("forecast errors"), cleared here. No semicolons outside quotes, no digits in headings
- P10: holds: the 60 h display is the one after-data addition and is labelled
- O1: cannot tell: the rider is added at the ship
- O2: holds: a failed fetch is named in sources.stale and the run uses the last copy. A failed gate turns every scored outcome into cannot tell and keeps the original
- O3: n/a: no GPU used, network reads and arithmetic on the CPU only
- O4: holds: summary carries generated, data/cone_history.jsonl gets one line per run
- O5: holds: cone_tick.py chdirs to its own folder and every path is under it. wrangler called by absolute path with PATH set
- O6: n/a: no GPU job runs in this rider

## Data access and terms (scouted 10 Nov 2026)
- NOAA/NHC files are US government works in the public domain. Credit NOAA/NHC. ATCF a-decks and b-decks at ftp.nhc.noaa.gov/atcf (https), HURDAT2 at nhc.noaa.gov/data/hurdat, the cone page and verification PDFs at nhc.noaa.gov. Keyless. The rider sends heuremen-cone/0.1 (+https://indahl.ai/cone), one request at a time, 0.8 s apart.
- Internet Archive: 123 distinct copies of aboutcone.shtml since 2007, read through the CDX index and raw-copy addresses. No copy names 2012.

## 2026-11-10 11:20 CONE ship after the outside referee: referee fixes R1 to R4, R6, R7 and R9 in the page and headline, ledger rows for the whole-path and circle cells and the second ruler, page at /cone under ATLAS, feed /cone/live.json, rider publishing on the tick bus
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is unchanged from the first read (tau 0 median 6.0 n mi on 11,178 frame forecasts). The referee recount (cone_index_referee/code, own readers, own geometry, own bootstrap, seed 777) reproduces all 66,165 circle rows and 6,017 whole-path rows with 0 differences in outcome or distance over 0.01 n mi, and all 224 second-ruler rows
- II: holds: inside and outside printed apart in every cell, nothing returned beside each with its two reasons (track ended, no longer tropical)
- III: holds: every circle share is above two-thirds (68.6 to 72.6) while both whole-path shares sit below 60 at the point estimate. The page states both without folding one into the other
- V: holds: plan ruler decides. Display rulers from the referee, after the data and deciding nothing: cone started at the 12 h circle lowers the whole-path share by 1.6 (Atlantic) and 2.8 (East Pacific) points. Partial-path scoring (60.7 Atlantic) is not printed in the headline, per referee R1
- VI: holds: cells: Atlantic, whole path CANNOT_TELL (697 of 1315, 45.1 to 60.4). East Pacific, whole path CANNOT_TELL (650 of 1106, 52.4 to 65.0). Atlantic, 12 h CONSISTENT (3169 of 4612, 66.1 to 71.2). Atlantic, 24 h CANNOT_TELL (2889 of 4092, 67.5 to 73.6). Atlantic, 36 h CANNOT_TELL (2562 of 3617, 67.0 to 74.3). Atlantic, 48 h CANNOT_TELL (2248 of 3186, 66.4 to 74.3). Atlantic, 72 h CANNOT_TELL (1697 of 2425, 65.3 to 74.3). Atlantic, 96 h CANNOT_TELL (1295 of 1839, 64.5 to 76.1). Atlantic, 120 h CANNOT_TELL (971 of 1415, 61.3 to 75.2). East Pacific, 12 h CANNOT_TELL (2930 of 4172, 67.8 to 72.5). East Pacific, 24 h CANNOT_TELL (2621 of 3672, 68.7 to 74.0). East Pacific, 36 h CANNOT_TELL (2291 of 3209, 68.3 to 74.4). East Pacific, 48 h CANNOT_TELL (2027 of 2793, 69.0 to 75.9). East Pacific, 72 h CANNOT_TELL (1521 of 2109, 67.9 to 76.1). East Pacific, 96 h CANNOT_TELL (1133 of 1564, 67.4 to 77.4). East Pacific, 120 h CANNOT_TELL (819 of 1135, 66.1 to 77.9)
- R: holds: counts from summary_cone.json of the run at 16:1x UTC 10 Nov 2026 (generated field), same HURDAT2 files and 625 a-deck files as the first read. Second ruler: AL 111 CONSISTENT and 1 CANNOT_TELL, EP 109 CONSISTENT and 3 CANNOT_TELL. AL 2020 72 h: NHC 79.9 on 318, our 72 h 98.1 on 275, our 60 h 79.8 on 319 (after data, display)
- P1: holds: NHC quotes rechecked by the referee against the saved pages. The live cone page no longer carries the older timing sentence, so the graphic page is the one quoted for the 60-70 percent
- P2: holds: page figures come from summary_cone.json through build_page.py and cone_headline.py, the feed /cone/live.json is the same summary less the season table, ledger rows cone.* cite this file
- P3: holds: center, cone, circle, best track as NHC writes them (referee R9: our own text now spells center)
- P4: holds: no cause named. The 60 h column is two pairs of numbers set side by side and says nothing about why
- P5: holds: every interval labelled a storm-level block bootstrap 95 percent interval. The circle band labelled our reading
- P6: fixed: referee R1. The lead now says the share covers the 1,315 forecasts whose storm stayed tropical for all five days, that 1,692 did not, and that NHC does not say which forecasts its 60 to 70 percent covers. R3 and R4: the lead carries no counts of our own cells or rows. R5: the page says the upper end of the Atlantic interval is 0.4 points above 60
- P7: holds: ledger rows written before the site edit, release through ledger/ship.sh only, live check after the ship
- P8: cannot tell: checked on the live page after the ship (recorded in the ship report)
- P9: holds: lint_copy.py one hit, inside the NHC quote, cleared
- P10: holds: after-data items labelled: the 60 h column and the referee's 12 h start figure
- O1: holds: rider added to watch/tick_bus.py every 60 ticks with --publish (backup tick_bus.py.bak-20261110-cone, compiled with /usr/bin/python3). headlines.py cone(), live_headlines.py cone, activity_check slug, push_public and receipts mappings, desk_pack entry
- O2: holds: a failed KV put is logged as publish FAILED and added to sources.stale
- O3: n/a: no GPU used, network reads and arithmetic on the CPU only
- O4: holds: the feed carries updated and generated, the live_headline row reads it stale after 9 h
- O5: holds: cone_tick.py chdirs to its own folder, wrangler called by absolute path with PATH set
- O6: n/a: no GPU job runs in this rider

## 2026-11-12 10:31 Faults and Guards 2.0 migration: reason codes, REQ-13 line, edge convention, addendum, K.read replaces K.classify
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, PLAN.md is not edited and its seal in data/plan_seal.json still matches, the addendum is a new file committed as cbcf1c5 before any reading under it
- II: n/a: no repeated item, forecasts of one storm stay one block in the same storm-level bootstrap with seed 20261110 and 2,000 resamples
- III: holds: INSIDE and OUTSIDE stay separate columns, every non-outcome number of summary_cone.json (scored, inside, outside, storms, share, lo, hi and all 224 second-ruler values) compared equal before and after the code change in all 16 cells, 224 verification rows and every season cell, 0 differences
- V: holds: the bands are named in PLAN_ADDENDUM_std2.md before any reading under it, 0.60 to 0.70 for the whole path, 0.6167 to 0.7167 for the circles and the larger of 1 n mi and 2 percent for the second ruler, edges closed, no new tolerance invented
- VI: holds: four outcomes kept and every CANNOT_TELL carries one closed reason, Atlantic whole path stays CANNOT_TELL with STRADDLES_EDGE at 697 of 1,315 and interval 45.1 to 60.4, the 4 second-ruler rows with differing case counts read CANNOT_TELL NO_INTERVAL_FORMABLE, no cell needs a size that matters and the addendum says so
- R: holds: counts and reasons are read from summary_cone.json after re-running cone_tick.py offline, rule self-test and kit self-test passed, 1,692 NOTHING_RETURNED beside the Atlantic whole path apart from the 1,315, the ledger rows still match the cells
- P1: n/a: no quotation of any source in this change, the lint hit on forecast errors is inside the NHC quote and was cleared before
- P2: n/a: no new figure, every number keeps its source on the page
- P3: n/a: no setting labels of any source are touched by this change
- P4: holds: no cause is named, the added text says only which closed reason a CANNOT_TELL carries and what the edges are
- P5: holds: the page note still names the storm-level bootstrap with 2,000 draws and states the closed edges and the minimum of 10 storms or 30 rows as TOO_WIDE_TO_RESOLVE
- P6: holds: the headline line is the same sentences as before plus the reason beside cannot tell and the REQ-13 line of the Atlantic whole-path rows read from the summary, no stronger than the reading
- P7: holds: no outcome moved, the one row whose surface text changed (cone.ruler2.al2020_72) was updated in the ledger with off and on under the ledger lock before the page text is released, the other cone.* snippets are prefixes of the new page text, the owner ships with ship.sh
- P8: cannot tell: cone.html rebuilt by build_page.py and lint_copy.py reported only the cleared quote hit, but the page was not rendered in a browser or served because nothing is deployed from this session
- P9: holds: plain sentences without semicolons in the added page text, no count of our own things in any heading, lint_copy.py only the cleared NHC quote hit
- P10: holds: the addendum is dated 12 Nov 2026 and written before any reading under the new rule, no rule set after the data
