# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-10 10:00 STEO desk first read: EIA STEO 95 percent NYMEX intervals for WTI and Henry Hub, from archived chart gallery workbooks, against EIA monthly spot prices
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: PLAN.md committed db326888 at 09:36:54 -05:00 (data/plan_seal.json), first comparison after it. Same quantity both sides: gate 4, each workbook's history column against EIA's current monthly spot series, 3,660 of 3,660 WTI months and 3,620 of 3,660 Henry Hub months within 2 percent. Copies: 85 held, 79 used, 5 with no interval table, 1 does not open. 78 issues, Nov 2011 to Aug 2025
- II: holds: inside, above and below printed apart (WTI all leads primary: 392 inside, 38 above, 60 below of 490)
- V: holds: plan ruler moving-block bootstrap over outcome months, block 12, 2,000 draws
- VI: holds: primary WTI all leads BELOW (80.0 percent, 67.6 to 91.5), Henry Hub all leads CONSISTENT (93.9 percent, 89.3 to 97.7). Addendum 1 (after the data): WTI 87.2 percent (78.2 to 94.3) BELOW, Henry Hub 88.0 percent (78.8 to 96.5) CANNOT_TELL
- P6: caught: first full run failed gate 3 (issue map). The release table parser read only zero-padded dates (mm/dd/yyyy), so releases written m/d/yyyy were missing and copies mapped to a later issue. Every outcome was cannot tell by the gate. The parser now reads both forms (fetch_archive.py). No outcome had been read
- P6: caught: from the June 2020 issue the workbook has no level cell, so those rows read cannot tell under the plan. Addendum 1 in PLAN.md (dated, after the data) reads the level from the report's chart label. Shown beside the plan's reading, the headline keeps the plan's cell
- P9: holds: lint_copy.py 0 hits after two headings lost their digits
- O2: holds: failed fetches name their source in sources.stale and the run uses the last copies
- O5: holds: steo_tick.py chdirs to its folder, runs with venv/bin/python (xlrd, pypdf, numpy)

## Data access and terms (scouted 10 Nov 2026)
- EIA: "U.S. government publications are in the public domain". Attribution "Source: U.S. Energy Information Administration". Interval inputs credited by EIA to CME Group, Bloomberg and Refinitiv.
- Chart gallery workbook: EIA serves only the current one. Internet Archive copies under eia.gov/outlooks/steo/xls/ and eia.gov/forecasts/steo/xls/, 85 distinct. Tracked in data/raw/wayback since they are what was stated.
- STEO PDFs 2010 on in data/raw/archives (refetchable, not tracked), read only for Addendum 1's level label.
- EIA suspended the intervals from the October 2025 issue.

## 2026-11-10 10:20 STEO ship after the outside referee (HOLD, then SHIP on re-check after fixes)
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: referee recount reproduces all 2,261 rows and 20 cells with 0 differences after the fix. Drops by reason: copies with no interval table 5, does not open 1, rows unreadable under the plan (no level cell) 761, months begun at release 0
- II: holds: inside, above and below printed apart. WTI plan: 392 inside, 0 above, 60 below of 452
- III: holds: WTI rows outside all fall below the interval in the plan reading, printed with their side. 45 of the 60 fall in outcome months Nov 2014 to Feb 2016, described and not scored
- V: holds: plan reading and Addendum 1 reading side by side, block lengths 6 and 24 shown after the data
- VI: holds: WTI plan all leads CANNOT_TELL (86.7, 73.1 to 97.4), Henry Hub plan CONSISTENT (93.9, 89.3 to 97.7). Addendum 1: WTI CONSISTENT (91.0, 82.8 to 96.8), Henry Hub CANNOT_TELL (88.0, 78.8 to 96.5)
- R: holds: counts from summary_steo.json of this run. Release dates from EIA's table, issue by chart note date. Addendum 1 commit 363717d labelled
- P1: holds: chart note, Jan 2012 sentence, the 95% NYMEX label and the Oct 2025 suspension sentence verified in the PDFs by the referee
- P2: holds: every figure in summary_steo.json and data/steo.json, page names the workbook copies and spot series
- P3: holds: Lower and Upper as EIA labels them, lead defined on the page
- P4: holds: no cause named
- P5: holds: every interval labelled a block bootstrap 95 percent interval over outcome months
- P6: caught: referee R1 (blocks ship): the .xls copies' #N/A error cells were read as 42 and 38 zero-width WTI rows scored above. Fixed in the reader, gate no_zero_width added, an .xls known-good cell added. The WTI plan headline moved from BELOW (80.0) to CANNOT_TELL (86.7). Re-check SHIP
- P7: holds: ledger rows steo.* before the site edit, release by ship.sh only
- P8: holds: steo.html parsed and read in full
- P9: holds: lint_copy.py 0 hits
- P10: holds: Addendum 1 and the referee displays labelled after the data
- O1: holds: rider on the tick bus every 264 ticks with --publish (KV steo_live), spot files once a day, archive copies once a week
- O2: holds: failed fetches named in sources.stale
- O3: n/a: no GPU used, arithmetic on the CPU
- O4: holds: data/steo_history.jsonl one line per run
- O5: holds: absolute paths, venv/bin/python
- O6: n/a: no GPU job runs in this rider

## 2026-11-12 10:26 STEO: Faults and Guards 2.0 outcome rule by PLAN_ADDENDUM_std2.md (12 Nov 2026), 0.95 as a point figure with no tolerance, CONSISTENT removed from cells, reasons and REQ-13 printed
packs: P,O
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: the none is the earlier outcome rule on the same rows. steo_tick.py --offline was re-run on the local archive copies and spot files with no network, and every number other than outcome, reason and req13 matched the run before the edit (full summary compared field by field, 0 differences)
- II: holds: flips counted before any net. Plan reading 4 CONSISTENT cells (HH all leads, 1 to 2, 3 to 6 and 7 to 12 months) and Addendum 1 reading 3 (WTI all leads, HH 1 to 2 and 3 to 6 months) became CANNOT_TELL (STRADDLES_EDGE). The other 13 cells were already CANNOT_TELL and stay STRADDLES_EDGE, none read ABOVE or BELOW
- III: holds: above and below stay as separate shares in every cell, WTI all leads (plan reading) stays CANNOT_TELL with 392 of 452 and interval 0.7311 to 0.9736, no cell changed sign
- V: holds: the ruler is the level 0.95 EIA states, a point figure with no tolerance, named in PLAN_ADDENDUM_std2.md committed as 64d7333 before the new rule was run. The width cap 0.15 is removed from the outcome rule and the Addendum 1 reading stays labelled decided after the data
- VI: holds: four outcomes in the record. CONSISTENT is not available for a cell (standard 6.4). No size that matters is named so the both-alternatives test is not applied, said in the addendum. Minimum sample of 30 rows or 24 months is TOO_WIDE_TO_RESOLVE by owner decision O3
- R: holds: counts read from summary_steo.json written by steo_tick.py. Headline req13 reads 0 NOTHING_RETURNED, CANNOT_TELL 438 of 890 (438 NO_INTERVAL_FORMABLE) for the plan reading and 6 NOTHING_RETURNED, CANNOT_TELL 9 of 884 for the Addendum 1 reading. Bootstrap is the desk's own (blocks of 12, 2,000 replicates, seed 20261110). Rule dated 12 Nov 2026
- P1: holds: the quoted rule is the standard 6.4 rule for a point figure and the reason names are the kit constants STRADDLES_EDGE, TOO_WIDE_TO_RESOLVE and NO_INTERVAL_FORMABLE verbatim
- P2: holds: the page names the plan addendum of 12 November 2026 beside the reading rule and the headline line carries the counts of NOTHING_RETURNED and CANNOT_TELL by reason
- P3: holds: the plan reading table and the Addendum 1 reading table keep their labels and each Outcome cell prints the reason beside every cannot tell
- P4: holds: no cause is named for why a cell cannot tell beyond the rule, the interval holds 0.95 or the cell is under the minimum sample
- P5: holds: every interval on the page is the block bootstrap 95 percent interval the plan names, unchanged
- P6: holds: the headline sentence still says cannot tell with its reason for WTI and Henry Hub, no summary stronger than the reading
- P7: holds: the four flipped rows steo.cell.hh.all, steo.cell.hh.lead1_2, steo.add1.hh.lead1_2 and steo.add1.wti.all are changed through ledger.py before the page text with a complete CHECKS.md entry. Release is left to ledger/ship.sh by the owner, nothing deployed
- P8: cannot tell: steo.html rebuilt by build_page.py and 5 STRADDLES_EDGE strings found in it, but the rendered page was not opened in a browser because no build_site or deploy was run
- P9: holds: plain sentences, no semicolons, no count of our own things in the title, heading or lead
- P10: holds: the new outcome rule is labelled as an addendum of 12 Nov 2026 written before the read under it, and the Addendum 1 reading stays labelled as decided after the data
- O1: holds: no new job, the change is inside the existing steo_tick.py rider. steo_tick.py --selftest passes and the kit selftest passes
- O2: holds: failed fetches still go to stale, and a row with no spot price yet stays NOTHING_RETURNED listed apart, outside numerator and denominator
- O3: n/a: no GPU used, no network used in the test (--offline)
- O4: holds: the feed stamp is the run that wrote it and the offline run rewrote summary_steo.json and data/steo_live.json with a new stamp and published nothing
- O5: holds: absolute paths used, run with venv/bin/python, backups steo_tick.py.bak-20261112-std2, steo_headline.py.bak-20261112-std2 and build_page.py.bak-20261112-std2 beside the files
- O6: n/a: no GPU job, no training
