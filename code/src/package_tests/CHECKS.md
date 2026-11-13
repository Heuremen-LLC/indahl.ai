
## 2026-11-01 20:42 Give-away package tests: QIA checker agrees with mirror audit on 7 of 7 processors; IRIS reproduces published flips 1, 4, 11, 10; ATLAS and list packs match live page counts
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: each package was run on data with an answer already published by separate code (mirror audit, item_flips.py, live page counts)
- II: holds: flip counts compared item by item, per pair, not as net rates; per-processor agreement checked qubit by qubit
- III: holds: flip directions printed (right to wrong, wrong to right) and match the published direction
- V: holds: two implementations side by side in every test; stated that both are ours, so agreement checks implementations not rules
- VI: n/a: these are agreement checks with a known answer, reported as matched or not, no interval outcome claimed
- R: holds: counts read from the test outputs and TESTED.md files, dates 2 Nov 2026
- P1: n/a: no quoted text appears in the box lines or test sections
- P2: holds: each test section names its source and the published file it was compared with
- P3: holds: package names and versions as built
- P4: holds: no cause named, agreement only
- P5: n/a: no intervals in the box lines or test summaries
- P6: holds: box lines say tested against known answers, no stronger; TESTED.md lists what was not tested
- P7: holds: ledger rows pkg.test.* added before the box lines and test sections ship
- P8: holds: rendered pages checked after ship
- P9: holds: plain sentences, no AI statements, no counts of our things in headings
- P10: n/a: the tests compare with answers fixed before the tests ran

## 2026-11-10 12:30 Data-pack pages (ATLAS, OY, MODEL) print the built README with its counts filled, in place of the template with {TOKEN} slots
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: each count on the page was recounted from the pack's own CSV files in dist (rows read with csv.DictReader), the file the zip carries
- II: n/a: no comparison between two runs, these are row counts of the files in the download
- III: n/a: no signed difference, each count is a level of one file
- V: holds: two counts side by side, the README value written by build_package.py and a fresh row count of the CSV, and they agree on every value
- VI: n/a: counts of rows in a file, no interval outcome claimed
- R: holds: utilities NA rows recounted (23: AK 11, HI 8, ME 2, NY 2); OY 148, 389, 291, 61, 14, 8 and MODEL 531, 74, 1,727, 569, 144, 17 recounted from the CSVs on 10 Nov 2026
- P1: n/a: no quoted text is added, the page shows the pack's own README
- P2: holds: every count names its file in the pack (json/ and csv/ paths printed beside it)
- P3: holds: file and column names as built in dist
- P4: holds: no cause named, counts only
- P5: n/a: no intervals on these pages
- P6: holds: the page says what the files hold and no more
- P7: holds: ledger rows pack.* added with surfaces atlas_pack, oy_pack, model_pack before ship, release through ship.sh, curl after
- P8: holds: rendered pages read after build, the site gate rule 0b.11 reads zero unfilled slots on every served page
- P9: holds: the README text is the pack's own plain sentences, no AI statements, no counts of our things in headings
- P10: n/a: the counts were fixed when the pack was built on 1 Nov 2026, before this page change

## 2026-11-10 13:50 ATLAS Data Pack adds WATER and the other ATLAS desks (UPTIME, TIME, CADA, SECRECORDS, SEAT, SUPPORT, CHANGE)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: every new count on the page was recounted from the pack's own CSV files in dist with pandas 3.0.5, and set against the live desk pages, their /<desk>/live.json files and summary_water.json, 52 comparisons with 0 differences
- II: n/a: no comparison between two runs, the pack pins one snapshot per desk (water rows and summary from the same run, same mtime)
- III: n/a: no signed difference is added, the pack carries the desk's own error columns unchanged
- V: holds: build_package.py writes each README value from the JSON and asserts the water lead-6 band cells recount from water_rows.json (42 of 83, 49 of 83), verify.py recounts every file cell by cell, and a changed cell and a dropped row both read FAIL
- VI: holds: the water intervals and outcomes in TESTED.md (30 to 70 percent, 39 to 78 percent, below) are the desk's own, printed as the page prints them
- R: holds: water 48 cells, 15,222 rows, 530 reports, 144 variant rows; uptime 20 and 57; time 36; cada 7 by 4; secrecords 1,000 domains and 39 read in full; seat 3 and 42; support 489, 9,375, 55, 127 of 512; change 330, 28, 12 recounted on 10 Nov 2026
- P1: holds: the only quotes are Reclamation's own sentence and document sections, carried unchanged from the desk file
- P2: holds: SOURCES.md names every upstream source with its URL and the read or snapshot date, LICENSE and NOTICE list every file
- P3: holds: file and column names as built in dist
- P4: holds: no cause named, the README describes files and counts only
- P5: holds: the intervals printed in TESTED.md are the desk's 95% Wilson intervals on water years, labelled as such
- P6: holds: TESTED.md says the counts match this snapshot and that later page counts may differ
- P7: holds: ledger rows pack.atlas.water* and pack.atlas.desks* added with surface atlas_pack before ship, release through ship.sh, curl after
- P8: holds: the rendered data-pack page is read after ship and gate 0b.11 reads zero unfilled slots
- P9: holds: plain sentences, no semicolons, no AI statements, no counts of our things in headings, Heuremen LLC
- P10: holds: the snapshots were pinned before the TESTED comparison ran

## 2026-11-10 20:10 ATLAS Data Pack: UPTIME, SECRECORDS, SUPPORT and CHANGE results only, filtered as their own desk packs are, and LICENSE item 5 made true
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: build_package.py writes each of the four desk files as tools/desk_pack.py filt() of the pinned snapshot and asserts the written JSON equals filt() of it, verify.py then compares every CSV cell with that JSON, All checks passed
- II: n/a: no comparison between two runs, the same pinned snapshots of 10 Nov as the 13:50 build
- III: n/a: no signed difference is added
- V: holds: two reads agree, the build asserts no source field name (incidents, title, impact, url, note, record, eol, last, claim, deprecated, shutdown, was, now, date, reach, indicator_now) is left in the four files, and a read of the built JSON shows only vendor, item, kind, days_left, rows, domain, reason, product, cycle, days and the counts
- VI: n/a: no new interval, the desk intervals and outcomes are carried as the snapshot holds them
- R: holds: counts unchanged from the 13:50 build (uptime 20 vendors, secrecords 1,000 and 39, support 489, 9,375, 55, 127 of 512, change 330, 28, 12), the 57 incident rows are gone with csv/uptime_incidents.csv, and ledger row pack.atlas.uptime_inc is withdrawn with them
- P1: holds: the SECRECORDS reasons are our own sentences and quote only the header or record the domain sends, which LICENSE item 5 now says
- P2: holds: SOURCES.md still names every upstream source with its URL, and says the four desk files carry no source values
- P3: holds: file and column names as built in dist, uptime_incidents.csv removed from LICENSE, NOTICE and verify.py
- P4: holds: no cause named
- P5: n/a: no new intervals
- P6: holds: README, LICENSE, NOTICE, SOURCES and TESTED say what the four files hold and what was left out, and no more
- P7: holds: ledger edits (withdraw pack.atlas.uptime_inc, pack.atlas.uptime value 20) before the surface ship, release through ship.sh under site_lock, curl after
- P8: holds: the zip is read back after ship, its sha256 equals the live .sha256 file
- P9: holds: plain sentences, no semicolons in the text files (build gate), no AI statements, no counts of our things in headings
- P10: holds: the snapshots were pinned before the filter ran, and the filter is the desk packs' own code, not a new one
