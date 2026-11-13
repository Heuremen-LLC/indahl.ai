# Check blocks (watch/readcheck.py). One entry per reading, appended, never edited after commit.

## 2026-11-11 PETROL desk first read (draft page body, not shipped, no ledger rows)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: PLAN.md sha256 dcc1a24d (data/plan_seal.json, sealed before analyze_petrol.py was first run) matches at every run. Not a git commit, the folder is not a repository, so the seal is a hash and a timestamp only
- II: n/a: no repeated item
- III: holds: ABOVE and BELOW are separate columns, CANNOT_TELL is its own column with its reasons counted apart, nothing is folded
- V: holds: rulers named in PLAN.md before any outcome: OPEC revision width (90th percentile of first to second print, issues up to October 2024) and EIA 2015 to 2019 spread (90th percentile of the absolute weekly minus monthly difference)
- VI: holds: four outcomes kept in both parts
- R: holds: counts and values are read from summary_petrol.json of the run, and no number in the page is typed
- Looked at before the plan (disclosed in PLAN.md): the September 2026 table of the October 2026 MOMR, statement texts and table images, per-issue row and member counts of the parser, first and last rows of the two EIA files. No revision, gap, spread or outcome had been computed
- Gates: parse (12 OPEC members in every issue from May 2020, 22 in every issue from May 2024, the three OPEC sums within 3 tb/d of the printed totals, six hand-read September 2026 values equal), join (528 rows), targets (arithmetic only), rule (synthetic), EIA format, join, January 2019 hand average, rule. All passed
- caught: the plan said every typed target would be re-read against its image on a second pass. What was done instead is the arithmetic check: May to June 2025 differs by 412 against a printed 411, August to September 2025 by 547 against 547, March to April 2026 by 207 against 206, April to May 2026 by 206 against 206. The printed totals of 188 (August 2026) and 137 (December 2025) cannot be checked because the previous month tables were not transcribed. These are one-unit rounding differences and the check tolerance was 2 tb/d. A fresh by-eye second pass is still open
- caught: the plan named the target months by statement. The table for 2026-09 is the December 2026 table of the 1 November 2026 statement, used for September 2026 because the statement text says September 2026 required production is maintained for December. This is the only target that is not a table of its own month, and it is flagged in data/targets.csv
- cannot tell: MOMR issues before May 2020 (another layout) and December 2023 (not fetchable) are not in the baseline. Non-OPEC DoC secondary-source crude figures exist in the cached issues only from May 2024, so their width is pooled and relative and rests on the issues May to October 2024
- not done: no monthly required-production table was found for April, July, October and November 2025, and for June, July and October 2026, so the eight voluntary-adjustment countries read CANNOT_TELL in those months. Not rendered in a browser. No wrapper page, no ledger rows, no site edits

## 2026-11-12 01:05 Second by-eye read of every typed target value (Bones), and the shipped PETROL readings
- I: holds: the widths come from OPEC's own first-to-second-print revisions (May 2020 to Oct 2024) and EIA's 2015-2019 weekly-minus-monthly spread, both baselines ending before the first scored month, sealed in PLAN.md before outcomes
- II: holds: rows are counted member by member and month by month (50 ABOVE, 182 BELOW, 93 CONSISTENT, 203 CANNOT_TELL), never netted into one OPEC+ gap
- III: holds: ABOVE and BELOW are kept apart, signed gaps printed per row, no product or sum is claimed
- V: holds: rulers named before the numbers: OPEC revision P90 per member (4 to 52 tb/d), pooled 7.7 percent for non-OPEC members, EIA 331 tb/d, with 0.5x and 2x sensitivity in the summary
- VI: holds: four outcomes kept, CANNOT_TELL split by reason (120 no target table transcribed, 72 exempt, 11 no delivered value)
- R: holds: all 9 source images re-read against data/targets.csv: the 38th ONOMM table (11 non-eight members) and the 2025-05, 06, 08, 09, 2025-12 to 2026-03, 2026-04, 05, 08 and Dec-2026 tables; every value matches, the Dec 2025 increments sum to the printed 137, the Apr and May 2026 increments sum to 205 against a printed 206 (rounding in the source)
- P10: holds: the headline lead (the BELOW count for the latest month) was chosen after the run and is labelled so on the page

## 2026-11-12 10:20 Faults and Guards 2.0 migration of the PETROL outcome rule (PLAN_ADDENDUM_std2.md)
packs: P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: n/a: no baseline or null is built by this change, the sealed widths and baselines are untouched and the sealed PLAN.md hash 8b2605ce still matches data/plan_seal.json
- II: n/a: no repeated item, every member and month stays its own row and no outcome changed in any row
- III: holds: ABOVE and BELOW stay separate, signed gaps stay in the rows, and every non-outcome number of summary_petrol.json compared equal before and after the migration
- V: holds: the rule is named in PLAN_ADDENDUM_std2.md before any reading under it, the band is minus w to plus w with closed edges, a zero-width interval by owner decision O1, no new tolerance invented
- VI: holds: four outcomes kept, CANNOT_TELL now carries one closed reason per row, 203 NO_INTERVAL_FORMABLE of 528 over the window, 4 of 22 in September 2026, 0 TOO_WIDE_TO_RESOLVE, both-alternatives test cannot fire on a zero-width reading
- R: holds: counts and REQ-13 lines are read from summary_petrol.json after re-running analyze_petrol.py offline, 50 ABOVE 182 BELOW 93 CONSISTENT 203 CANNOT_TELL unchanged, gates all passed
- P1: n/a: no quotation of any source in this change
- P2: n/a: no new figure, every number already names its source table on the page and in the rows file
- P3: n/a: no setting labels of any source are touched by this change
- P4: holds: no cause is named, the added text says only which closed reason a CANNOT_TELL carries
- P5: holds: the page says each gap is a published value against a published value, an interval of zero width, so no interval method applies, and the width is a yardstick of ours
- P6: holds: the page summary is the same sentence as before plus the REQ-13 count line read from the summary, no stronger than the reading
- P7: holds: no ledger row changes because no outcome or count moved, the source grep BELOW 10 in summary_petrol.json still matches, nothing shipped from here, the owner ships with ship.sh
- P8: cannot tell: page body rebuilt by build_page.py and lint_copy.py reported 0 hits, but the page was not rendered in a browser or served because nothing is deployed from this session
- P9: holds: plain sentences without semicolons in the added page text, no count of our own things in any heading, lint_copy.py 0 hits
- P10: holds: the lead number is still labelled as chosen after the run, and the addendum is dated 12 Nov 2026 and written before any reading under the new rule
