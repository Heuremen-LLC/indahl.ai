# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-09 21:54 Lake Mead rise answer for Wayfinder: largest 1, 2 and 7 day rise in the last 60 days, two Reclamation seats and a USGS water balance
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: windows fixed before reading (60 days back from 9 Nov, 1, 2 and 7 days), both rulers (end-of-day pairs and any hourly pair inside the span) run on the same series, no gate drops any reading (1,435 hourly readings in the window, 0 gaps)
- II: holds: largest rises read item by item, not netted: +0.49 / +0.53 ft in 1 day, +0.81 / +0.83 in 2 days, +1.44 / +1.50 in 7 days (daily / hourly). repeat floor is the hour-to-hour step, -0.12 to +0.14 ft, p1 -0.07, p99 +0.06
- III: holds: every rise is positive and dated (23-25 Oct), net change since the 22 Oct low +2.50 ft daily, +2.80 ft hourly. no sign folded
- V: holds: ruler feet of elevation, two seats side by side (HDB lchdb hourly and daily, RISE item 6123 daily, both Reclamation, same database family so one seat), third seat independent: USGS gauged inflow 43,042 af on 24 Oct against storage change plus release 44,520 af
- VI: holds: claim of 20 ft in 1 to 2 days at Lake Mead reads BELOW (largest 2 day rise 0.83 ft, about 19 ft short, width 0.14 ft). alternatives tested: Lake Powell 22.2 ft since 15 Sep (size matches, speed does not: 3.5 ft in 2 days), Navajo 13.7 ft in 2 days and 24.9 in 7, datum step (RISE says +0.55 ft to NGVD 1929, no step in record), bad reading (none in window), video titles (4 and 7 Nov)
- R: holds: every number read from data/raw files (hdb_lc_1930_HR, hdb_lc_1930_DY, rise_item6123/6124/6122, usgs_mead_inflow_dv, usgs_09379900 iv and dv, hdb_uc_1928, usbr_lc_accumweb), video dates from the page metadata (uploadDate), news text from the fetched pages
- P1: holds: news quoted only from fetched page text (azfamily 6 Nov, KUTV headline), video titles copied from the page title tag
- P2: holds: each figure in the answer names its seat (HDB, RISE, LC daily JSON, USGS site number) and the file in data/raw
- P3: holds: datum labels as the sources give them (Reclamation operational datum, USGS 62614 NGVD 1929, 62615 NAVD 1988)
- P4: holds: the answer names what the record shows and lists other places the 20 ft figure appears, it does not say why he heard it
- P5: holds: no statistical interval used, the hourly step range is labelled as the hour-to-hour range in the window
- P6: holds: summary says the record shows about half a foot a day at most, it does not say he is wrong
- P7: n/a: internal answer relayed by Bones, not a public surface, no ledger line
- P8: n/a: no page rendered for this answer, the desk page is a separate entry below
- P9: holds: plain sentences, no counts of our things in headings, Wayfinder named as Wayfinder
- P10: holds: the water balance and the other-reservoir scan were added after the first read and are labelled as checks, not as the plan

## 2026-11-09 21:54 WATER desk: 24-Month Study band coverage and Most Probable median test by lead, Lake Mead and Lake Powell, plus the live panel
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: rules sealed in PLAN.md (sha256 in data/plan_seal.json, 02:16Z) and Addendum 1 before the first comparison. same quantity both sides (HDB end-of-period elevation), median Most Probable error at lead 0 is -0.11 ft Mead and -0.25 ft Powell so no datum offset. gate drops counted by reason: no band issued 5,457 Mead and 5,436 Powell rows, band edge unreadable 13 Mead and 32 Powell, none depends on the outcome
- II: holds: every cell prints inside, above and below counts separately (Mead lead 6: 42 inside, 19 above, 22 below of 83), never a net. floor 34 flagged cells against 4.8 expected and 9.2 for chance. no repeat floor exists for a single published record and the page says the cells share months
- III: holds: misses keep their side: Mead splits both ways at short leads (lead 1: 30 above, 30 below), Powell misses lean low (lead 6: 8 above, 25 below). Most Probable error printed signed with its middle 80 percent
- V: holds: plan ruler is a 95% Wilson interval on water-year clusters, the second ruler (rows counted as independent) rides beside it in the feed. They disagree on 53 of 96 cells, and in every one the plan ruler reads CANNOT_TELL where the rows ruler would give a verdict in the direction of the counts: Powell Most Probable leads 0 to 16 BELOW, Powell band leads 7 to 19 BELOW, Mead band leads 16 to 18 and 21 BELOW, Mead Most Probable leads 5 to 11 ABOVE, lead 0 BELOW, and 11 leads CONSISTENT. The plan ruler decides
- VI: holds: band cells test 80 percent and the 70 to 90 band, Most Probable cells test 50 percent and the 40 to 60 band, CANNOT_TELL where the interval reaches the claim (Mead leads 16 to 18 and 21, Powell 7 to 23 band), n_eff under 10 forced CANNOT_TELL. the 80 percent is named as our reading of inflow probabilities, not a stated elevation claim
- R: holds: counts read from data/water.json and summary_water.json, report list from RISE record 6331 cache (530 reports), plan times from data/plan_seal.json. median band width is labelled defined after the data. the notable-row selection is labelled as not in the plan
- P1: holds: all 11 governing-document quotes found verbatim in the extracted text of RecordofDecision.pdf and 2027-2028OperatingGuidelines_Final.pdf (whitespace and page headers normalised). scenario descriptions copied from the RISE catalog entries
- P2: holds: page names each source with a link, live table names HDB sdi and server, thresholds name document and section, cells name the plan. the headline figure lives in /water/live.json (headline_lead6)
- P3: holds: scenario names as Reclamation prints them (Most Probable, Probable Minimum, Probable Maximum). capacity column says what each figure is (bottom of exclusive flood control space for Mead, available capacity, maximum storage, capacity)
- P4: holds: page says a gap is a gap and does not say why. no drought, operations or forecast cause is named anywhere in the page or feed
- P5: holds: every interval labelled 95% Wilson on water years. errors labelled middle 80 percent of errors. capacity shares labelled a reading, not a test
- P6: caught: headline first said about two thirds more would have been inside. arithmetic gives 66 of 83 and 66 of 82 at 80 percent, so the line now says about 66 of each, named as our reading
- P7: n/a: not shipped by this agent. Bones places the page, adds the ledger line and ships through ship.sh
- P8: holds: live.js rendered against data/water_live.json through a DOM shim, every section filled. served routes /water/live.js and /water/live.json do not exist yet and are listed for Bones
- P9: fixed: "read by eye" replaced with "read directly from the page text" in PLAN.md (recorded in plan_seal.json as a wording edit, no rule changed). no AI statements, no semicolons in copy, no counts of our things in headings, "we" pronouns
- P10: holds: median band width column says defined after the data. the rows-to-read note says its selection is not in the plan. Addendum 1 states the 60 percent line was set from the stated-side distribution before any comparison
- O1: cannot tell: the rider is not on the tick bus or in nodes_repo/drift/targets.json yet. Bones places it (no timer installed by this agent)
- O2: fixed: a failed fetch now names the source in stale_sources in the feed and the page prints it. a failed publish prints publish FAILED
- O3: n/a: no GPU used. the tick is network reads and PDF text extraction on the CPU
- O4: holds: feed carries updated time plus each source's own data date (daily_date, hourly_time, CDEC as_of, measured_last)
- O5: holds: water_tick.py chdirs to its own folder, all data paths are under it, publish uses /opt/homebrew/bin/npx with PATH set as the launch rider does
- O6: n/a: no GPU job runs in this rider, CPU and network only

## 2026-11-09 22:50 WATER desk after the referee pass: 80 percent attributed to Reclamation, Lake Powell lead 6 at 49 of 83, after-data rulers, flagged cell list, copy and quote fixes
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: caught: the reader missed two Lake Powell tables whose scanned heading reads "Powell" or "Lake Powe ll", so the August 2020 band month lost all 24 Lake Powell rows. Fixed on the stated side only (Addendum 2 item 2), lead 6 Lake Powell now 49 of 83 with 26 below. Gate drops now 13 Mead and 10 Powell band edges unreadable
- II: holds: every cell still prints inside, above and below apart. The flagged list names the 34 cells by lake, test and lead instead of netting them against a chance figure
- III: holds: misses keep their side (Lake Powell lead 6: 8 above, 26 below). Signed Most Probable error unchanged in form. The April 2026 Lake Mead row reads 17.78 ft below the Most Probable and 15.47 ft below the Probable Minimum, each named
- V: fixed: three after-data rulers printed beside the plan ruler with the plan's rounding and without it. Lake Mead lead 6 reads below on all (upper bounds 61.1 to 78.7 percent). Lake Powell lead 6 upper bounds run 78.1 (plan), 80.8 (row-count weighted), 78.7 or 81.8 (paired water years), so it reads cannot tell under at least one alternative and the page says it depends on the ruler
- VI: fixed: the band test now tests Reclamation's own stated 80 percent (182 of 205 Minimum and Maximum reports, 79 of 86 band months in both). The Most Probable test keeps 50 percent as our reading. The page says no cell can read consistent with about 20 water years (needs about 61 for the band, 96 for the median)
- R: holds: every new count read from summary_water.json and data/scan80.json produced by this run. Addendum 2 dated after the comparison. plan_seal.json records the first-write hash 316cab8a and the 12 second reseal gap
- P1: holds: Reclamation's 80 percent sentence copied from the OCT26_MAX and APR26_MIN page text. All 11 governing-document quotes verbatim against the extracted documents, the three cut quotes end in "...", the rest are whole sentences, 3,565 ft now quotes 5.1.A.1 in full
- P2: fixed: the page says its figures live in /water/live.json. "Every row is in the full record" dropped until a rows file is published
- P3: fixed: 2.D.1.b and 2.D.1.c say in force through 2026, not the tier that governed 2026, and 2.D.1.a says governed calendar year 2026, quoted from the October 2026 study. The list is retitled to the two documents it draws on and the DCP and Minutes 323 and 330 are named as also governing 2026
- P4: holds: no cause named. Width, inverted and zero-width counts are shown without a reason
- P5: fixed: the headline now carries its 95% intervals counted on water years, and the Most Probable interval column says on how many water years
- P6: fixed: the chance comparison is gone and the headline says Lake Powell's reading depends on the ruler
- P7: n/a: not shipped by this agent. Bones places the page, adds the ledger lines and ships through ship.sh
- P8: holds: live.js rendered against the new data/water_live.json through the DOM shim, every section filled, including the 6.0 maf table, flagged list, ruler checks, sentence-month check and cross-checks
- P9: fixed: "trend history" and "Read about every half hour" dropped until true, the storage table retitled "Reservoir storage against stated capacity", the latest-month rows described as made 0 to 12 months ahead
- P10: fixed: the largest rises and lowest readings say added after the plan, the rulers, correlations and sentence-month cells say added after the data, the datum notes quote RISE
- O1: cannot tell: still not on the tick bus or in the watch. Bones places it. A one-line history file (data/water_history.jsonl) now grows on each run
- O2: holds: failed fetches still name themselves in stale_sources, the last run had none
- O3: n/a: no GPU used, the rider is CPU text extraction and network reads only
- O4: holds: the feed carries the run time and each source's own data date
- O5: holds: unchanged, all paths under the rider's own folder, npx called by absolute path
- O6: n/a: no GPU job runs in this rider, CPU and network only

## 2026-11-09 23:07 WATER ship: ledger rows for the six-month band and Most Probable cells and the threshold distances, page at /water under ATLAS, rider on the tick bus
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every ledger number is copied from the feed as published at 2026-11-10 03:59Z, kept as data/shipped_20261110_water_live.json (sha256 041304c90ec2ecbf), the same file put in KV water_live. Nothing is recomputed for the ledger. Gate drops are those of the entry above (13 Lake Mead and 10 Lake Powell band edges unreadable)
- II: holds: the lead-6 band rows keep inside, above and below apart (Lake Mead 42 inside, 19 above, 22 below of 83, Lake Powell 49, 8 and 26 of 83), never a net
- III: holds: misses keep their side in every ledger claim, and the Most Probable rows keep above and below apart (Lake Mead 180 above and 135 below of 315, Lake Powell 110 above and 204 below of 314, no ties)
- V: holds: the ledger interval is the plan ruler, 95% Wilson on water years (Lake Mead 29.9 to 70.1 percent on 20, Lake Powell 38.7 to 78.1 percent on 20). The after-data rulers stay beside it on the page, and the headline says Lake Powell's reading depends on the ruler (row-count weighted 38.1 to 80.8 percent, cannot tell)
- VI: holds: band outcomes BELOW for both lakes (upper bound under the 80 percent Reclamation states), Most Probable outcomes CANNOT_TELL for both (Lake Mead 39.1 to 73.5 percent, Lake Powell 20.7 to 54.2 percent, against 50 percent, our reading). At 80 percent, 66.4 of 83 would be inside, printed as about 66 of each
- R: holds: counts, intervals, outcomes and distances read from the frozen feed. Live levels are HDB end of day 8 Nov 2026, Lake Mead 1039.66 ft and Lake Powell 3538.84 ft. The distances move every day, so their ledger rows name that day and carry no page snippet, and the page shows the newest reading from the feed
- P1: holds: the headline quotes Reclamation's sentence as the entry above copied it from APR26_MIN and OCT26_MAX page 1. The headline built by watch/headlines.py from the feed equals the referee-checked text of the draft page character for character
- P2: holds: every ledger row names the frozen feed (or this file) and the exact text it greps. The page says its figures live in /water/live.json
- P3: holds: scenario names as Reclamation prints them, sections as the two documents number them (2.D.1.a to 2.D.1.c, 5.1, 5.1.A.1, 5.1.C.1, 5.3, 5.3.A.4, 5.3.A.5)
- P4: holds: no cause is named on the page, in the headline or in any ledger claim
- P5: holds: every interval in the ledger and the headline is the 95% Wilson interval counted on water years and says so
- P6: holds: the headline is the referee-checked line. It says Lake Powell's band reading depends on the ruler and that both Most Probable cells cannot tell
- P7: cannot tell: ledger rows go in before the page or the headline carries the numbers, and the release goes only through ledger/ship.sh. The live check after ship is the next entry
- P8: holds: the page is built by indahl-ai/build_site.py (nav, division line, desk list and reference code HLC-41A6B015 from page()). The panel script is served from public/water/live.js, byte for byte water_index/water_live.js (ledger/copies.json water-live-js). The rendered live page is checked in the next entry
- P9: holds: plain sentences, no semicolons, no counts of our things in headings, no AI statements, we pronouns. The site gate reads the built page with no breach
- P10: holds: the after-data rulers, the sentence-month cells and the live-panel extras keep their labels from the referee pass. The frozen feed is named as the ledger copy, not a new reading
- O1: holds: rider on the tick bus every 5 ticks (about every half hour) as /opt/homebrew/bin/python3 -P water_tick.py --publish, since the bus's own Python 3.9 has no pymupdf and no -P. WATER added to nodes_repo/drift/targets.json (page water, feed water/live.json, limit 1.6 h, three times 5 ticks at 6.5 minutes), pushed once the page is live. The STACK running table and the headline rider read the feed
- O2: holds: a failed fetch still names its source in stale_sources, and a failed publish prints publish FAILED in watch/novatime_jobs.log
- O3: n/a: no GPU used, the rider is network reads and PDF text extraction on the CPU
- O4: fixed: the feed's updated stamp is now written as YYYY-MM-DD HH:MM in UTC so the drift seat can read its age. The earlier form, with the year after the month, did not parse there and would have read unreachable
- O5: holds: absolute paths throughout, homebrew python by path, npx by path with PATH set. A run under a launchd-like environment (env -i with HOME and the system PATH) took 40 s and published
- O6: n/a: no GPU job, CPU and network only

## 2026-11-09 23:15 WATER live check after both releases (ship.sh 9980c1cd and 8b389463)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: https://indahl.ai/water/live.json (stamp 2026-11-10 04:02, written by the tick bus at tick 26940) equals summary_water.json on all 48 lead rows (96 cells), the flagged list, coverage, sentence-month cells, misread rates and cross-checks, and equals the frozen ledger copy on every cell
- II: holds: the rendered panel keeps inside, above and below apart (lead 6 Lake Mead 42 of 83 with 19 above and 22 below, Lake Powell 49 of 83 with 8 above and 26 below)
- III: holds: signs as the feed prints them, Most Probable median error at lead 6 +0.70 ft Lake Mead and -3.77 ft Lake Powell, middle 80 percent -5.80 to +8.97 and -14.64 to +11.49 ft
- V: holds: the live panel prints the plan ruler with the after-data rulers beside it, as the feed carries them
- VI: holds: outcomes on the live page match the feed and the ledger, band below for both lakes at lead 6 and Most Probable cannot tell for both
- R: holds: the live page is byte for byte the built indahl-ai/water.html and the public repository copy, reference code HLC-41A6B015, and /water/live.js equals its canonical (copies.py live, drift 0)
- P1: holds: the headline quote on the live page is the built text character for character
- P2: holds: the page links /water/live.json and code/water, which serves PLAN.md, water_tick.py, water_24ms.py, heuremen_kit.py and a README written for this desk (the shared README line says every plan was committed before its data, which this plan was not)
- P3: holds: menu entry WATER under ATLAS after PLANNED PLANTS, division list line "Reservoir forecasts against measured levels" with the STACK reading beside it
- P4: holds: no cause is named on the live page or in the headline
- P5: holds: every interval on the live page says 95% and on how many water years
- P6: holds: the headline on the live page is the referee-checked text
- P7: holds: ledger rows went in before the page carried the numbers, both releases went through ledger/ship.sh with every gate passing (ledger drift 0, copies drift 0, site gate 0 breaches, source gate 0 fail), and live was read after each
- P8: holds: in a browser the live page filled every panel section from the live feed with no console error or warning. A browser that still held the first release in its 5 minute page cache got the headline from headline.js
- P9: holds: the site gate read the shipped build with no breach
- P10: holds: the after-data and after-plan labels on the live page are as in the referee pass
- O1: holds: the bus ran the rider at tick 26940 and published, drift targets are on Heuremen-LLC/nodes (a1713660), the STACK running table and division list carry WATER, the LIVE tag list carries water, and the TAPE feed list carries water from its next run
- O2: holds: stale_sources is empty on the live feed and the rider's log line says published
- O3: n/a: no GPU used, CPU and network only
- O4: holds: the live stamp 2026-11-10 04:02 is in the form the drift seat and the LIVE tag reader parse (YYYY-MM-DD HH:MM)
- O5: holds: the bus calls the rider by absolute homebrew path with -P, and the manual run in a launchd-like environment took 40 s
- O6: n/a: no GPU job, CPU and network only

## 2026-11-12 10:41 Faults and Guards 2.0 migration: reason codes, REQ-13 line, edge convention, addendum, live panel and headline
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, PLAN.md and its two addenda are not edited and the plan hash still matches, the addendum is a new file committed as bf873cc before any reading under it
- II: n/a: no repeated item, water-year clusters and the rounded effective count stay as the plan states
- III: holds: ABOVE and BELOW stay separate in every cell, every non-outcome number of summary_water.json (48 band cells, 48 Most Probable cells, the three after-data rulers, the sentence cells, coverage, live panel) compared equal before and after the code change, only rows_by_outcome lost its NOTHING_RETURNED key, which moved to failed_reads
- V: holds: the claims 0.80 and 0.50 and the bands 0.70 to 0.90 and 0.40 to 0.60 are the plan's, named in PLAN_ADDENDUM_std2.md before any reading under it, closed edges, the row tolerance 0.005 ft is the plan's own, no new tolerance invented
- VI: holds: four outcomes kept and every CANNOT_TELL carries one closed reason, lead 6 Lake Mead 42 of 83 and Lake Powell 49 of 83 stay BELOW, the two Most Probable cells at lead 6 stay CANNOT_TELL STRADDLES_EDGE, 27 band cells BELOW and 21 STRADDLES_EDGE, 7 Most Probable cells BELOW and 41 STRADDLES_EDGE, no cell needs a size that matters and the addendum says so
- R: holds: counts and reasons are read from summary_water.json after re-running water_tick.py offline, gate passed, 15,222 rows, 232 of 315 lead-6 rows per reservoir have no band and read CANNOT_TELL NO_INTERVAL_FORMABLE, 6 rows per reservoir at lead 6 are NOTHING_RETURNED apart
- P1: n/a: no quotation of any source in this change
- P2: n/a: no new figure, every number keeps its source on the page
- P3: n/a: no setting labels of any source are touched by this change
- P4: holds: no cause is named, the added text says only which closed reason a CANNOT_TELL carries and what the edges are
- P5: holds: the page note and the live panel note still name the Wilson 95 percent interval on water years and now state the closed edges and the minimum of 10 water years as TOO_WIDE_TO_RESOLVE
- P6: holds: the headline line is the same sentences as before plus the reason beside cannot tell and the REQ-13 lines of the two band cells read from the feed, no stronger than the reading, and the live panel prints the reason beside every cannot tell
- P7: holds: no outcome moved so no ledger outcome changed, the ledger snippets for the headline (both cannot tell) are prefixes of the new text, copies.py publish water-live-js was run after editing the canonical and check reports drift 0, the owner ships with ship.sh
- P8: holds: public/water/live.js passes a node syntax check and ran against data/water_live.json under a stub DOM, the reason shows beside cannot tell in the band and Most Probable tables, the rule note and the REQ-13 note print, but it was not rendered in a browser or served because nothing is deployed from this session
- P9: holds: plain sentences without semicolons in the added text of the page note, the live panel notes and the headline, no count of our own things in any heading
- P10: holds: the addendum is dated 12 Nov 2026 and written before any reading under the new rule, no rule set after the data
