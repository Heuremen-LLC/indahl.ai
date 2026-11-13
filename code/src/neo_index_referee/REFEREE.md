# Referee report: NEO desk (JPL close-approach ranges stated earlier against the latest solution)

Referee: read-only refuting pass, 10 November 2026. Nothing in `neo_index/` was edited during this pass.
Inputs read: PLAN.md (commit 2314da1), git history, data/plan_seal.json, neo_tick.py, heuremen_kit.py, build_page.py, lint_copy.py, CHECKS.md, summary_neo.json, data/neo.json, data/known_good_rows.json, the 84 files under data/raw/wayback (83 copies plus the CDX index), data/raw/cad_current.json, data/snapshots, data/cache, neo.html, and the JPL pages ssd-api.jpl.nasa.gov/doc/cad.html, cneos.jpl.nasa.gov/ca/ and cneos.jpl.nasa.gov/ca/neo_ca_info.html (fetched 10 Nov 2026).

Referee code: `code/recount.py`, written without importing neo_tick.py or heuremen_kit.py. It has its own reader, its own designation aliasing (from the current record's fullname field, with the desk's cached JPL designation answers only as a fallback), its own Wilson interval and cell rule. Outputs are in `out/recount.json`, `out/rows.json` and `out/diff_vs_desk.json`.

## Verdict

**FIX THEN SHIP.** Every number reproduces. The rule is the sealed rule. The pairing is clean. The faults are in what the page leads with and in three statements the page makes about the ruler. All fixes are copy and display fields. No outcome, threshold or cell changes.

## 1. Recount from raw

| | Desk | Referee |
|---|---|---|
| Archived copies used / count-only or other format / other body | 58 / 24 / 1 | 58 / 24 / 1 |
| Own copies | 1 | 1 |
| Rows (object, approach, stated orbit) | 15,283 | 15,283 |
| Headline rows | 15,066 | 15,066 |
| Outcomes, all rows | CONSISTENT 623, CANNOT_TELL 277, ABOVE 12, BELOW 10, NOTHING_RETURNED 14,361 | identical |
| Statements outside the frame / copied after the approach | 27,031 / 3,503 | 27,031 / 3,503 |
| All leads | 465 of 479, 8 above, 6 below, [95.15, 98.25] BELOW | identical |
| 0 to 7 days | 193 of 193, [98.05, 100] CONSISTENT | identical |
| 8 to 30 days | 100 of 100, [96.30, 100] CANNOT_TELL | identical |
| More than 30 days | 172 of 186, [87.76, 95.46] BELOW | identical |
| August 2026 | 14 of 14, 7 cannot tell, CANNOT_TELL | identical |
| Join gate (same orbit, dist within 1e-5) | 195 of 195 | 195 of 195 |

Row-by-row diff against data/neo.json: 0 rows only on one side, 0 outcome differences, 0 headline-flag differences. The 22 outside rows (14 headline) reproduce with the same orbit IDs, moves and readings.

## 2. Is dist_min to dist_max JPL's 3-sigma range? Yes, with one correction to our reading

- Close-Approach Data API: dist_min "minimum (3-sigma) approach distance (au)", dist_max "maximum (3-sigma) approach distance (au)", orbit_id "orbit ID used for the close-approach computation". The API "provides access to current close-approach data". Defaults "date-min now, date-max +60, dist-max 0.05". The plan quotes these correctly.
- CNEOS table legend: "The minimum possible distance is based on the 3-sigma Earth target-plane error ellipse." The plan quotes it correctly.
- CNEOS uncertainties page: the minimum is "the minimum distance between the 3-sigma Earth target-plane error ellipse and the Earth's surface". The legend and the API say Earth center. Note only. The values are the same field.

**R1. The 99.7 percent reading is not the only reading the docs support. Severity: fix before ship (copy).** The range comes from a two-dimensional 3-sigma ellipse in the target plane. Under a normal error model a point inside that ellipse has probability 1 − e^(−4.5) = 98.9 percent, and every point inside it has a distance between the minimum and the maximum. So the docs support an expected share between about 98.9 percent and about 99.7 percent (the 99.7 holds when the ellipse is small next to the distance, so distance is close to linear). I re-ran every cell against 98.89 percent: the outcomes are identical (all leads BELOW, hi 98.25; more than 30 days BELOW; 0 to 7 CONSISTENT; 8 to 30 CANNOT_TELL). Fix: one sentence naming the 98.9 percent floor and saying the readings are the same against it.

**R2. The later solution is not the truth. Severity: note, already conservative.** The later solution shares most of its observations with the earlier one. If the earlier covariance were right, the later nominal would land inside the earlier range more often than the nominal share, not less. Requiring the whole later interval inside is stricter, but the plan drops edge crossings (37) to CANNOT_TELL rather than counting them. Counting every edge row as inside gives 502 of 516, [95.5, 98.4], still BELOW. The BELOW readings survive both directions.

**R3. "Under a normal distribution about 32 percent of shifts would be beyond one sigma." Severity: fix before ship (remove).** This is not what a correct range predicts. (a) By R2 the expected share of later nominals beyond one stated sigma is below 32 percent when the stated covariance is right, so the page's 14 percent beside 32 percent reads as "tighter than expected" when it is not evidence of that. (b) For lopsided ranges, one sixth of the range is not a sigma (R5). Remove the sentence. The shift column stays as a described quantity.

## 3. Are the archived copies pre-approach statements with the right orbit IDs? Yes

- Every row's copy time precedes its approach. The smallest lead among all 15,283 rows is 0.024 days (34 minutes). No row has a lead under 0.01 days, so the UTC capture time against the TDB approach time (about 69 s apart) cannot move a row across the line.
- The 9 Feb 2024 05:42:43 copy is what JPL served that day. It contains 205 objects designated in 2024, all with half-month letters A, B or C (1 January to 15 February). No later designation appears. Its 69 objects shared with the separate copy captured two minutes later (05:44:26, a different query) carry the same orbit IDs in all 69. Across 18,068 later-copy pairings of the same object, a later copy carries a lower numeric orbit ID in 2 (2018 VK, 2021 GS). Neither object is in a scored row.
- Every scored row's stated orbit ID differs from the latest orbit ID by construction, and in no scored row is the latest ID numerically lower.
- Gate 2 (reader) rows and the two rows in CHECKS.md R reproduce from raw text.

## 4. Does matching by designation within 10 days mis-pair? No

- For every scored row the referee's pairing (aliases from the current record's fullname) gives the same latest record as the desk. 918 of 922 passed rows pair from the current record. 1 pairs through the desk's cached JPL designation answer. 3 (2024 BY15, three orbit IDs) have no record because JPL answers "object not found", and they read CANNOT_TELL no record as the plan says.
- No scored row had a second current record of the same object within 10 days, so the "nearest" choice never had to choose.
- The largest approach-time offset in a scored row is 101 h (2021 WR, stated 652 days ahead, CONSISTENT). The desk's own time check puts 310 of 316 scored rows with a stated time sigma inside 3 sigma.
- Renumbered objects pair correctly (1998 SH2 to 875163, 2004 MO3 to 887324, 2007 DB61 to 887773).

## 5. The 9 February 2024 copy

**R4. The headline does not disclose the dependence where a reader sees it. Severity: blocks ship (copy).** The draft headline is "465 of 479 ... the cell reads below". The dependence is in the last section of the page.

What the copy carries (recounted):
- 170 of the 479 scored headline rows, and 161 of the 186 scored rows stated more than 30 days ahead. Every other copy is a short window (default 60 days, 10-row lists, single objects), so this copy is effectively the whole long-lead sample.
- 13 of the 14 outside headline rows. The 14th (2007 EG, stated 28 Jan 2026, 46 days ahead) is also a long-lead row.
- 8 of the 193 rows in the 0 to 7 day cell (approaches in the week after 9 Feb 2024).

Without the copy (after the data, referee only):

| Cell | Scored | Inside | 95% interval | Outcome |
|---|---|---|---|---|
| All leads | 309 | 308 | 98.2 to 99.9 | CONSISTENT |
| 0 to 7 days | 185 | 185 | 98.0 to 100 | CANNOT_TELL (lower bound 97.97) |
| 8 to 30 days | 99 | 99 | 96.3 to 100 | CANNOT_TELL |
| More than 30 days | 25 | 24 | 80.5 to 99.3 | BELOW (on one row) |

So the dependence is two-sided. The pooled BELOW turns CONSISTENT without the copy, and the 0 to 7 day CONSISTENT turns CANNOT_TELL without it. The more-than-30-day BELOW survives on the 25 remaining rows, but on one miss.

Should the headline be the 0 to 7 day result? No. It is not robust: one row outside the range makes it 192 of 193, [97.1, 99.9], CANNOT_TELL, and dropping the 9 Feb copy also makes it CANNOT_TELL. Picking the friendliest cell after the data would also break the plan's cell order. The plan fixed all leads as the first cell, and that stays the number.

Fix: keep the plan's all-leads count as the big number, and put the split and the dependence in the headline line itself: all outside rows were stated more than 30 days ahead, 13 of them in one archived copy of 9 Feb 2024 that supplies 161 of the 186 statements made that far ahead, and without that copy 308 of 309 are inside. Then the 0 to 7 day result with its fragility. The figures come from a display block computed in neo_tick.py (labelled after the data), not typed into the page.

**R5. Lopsided stated ranges. Severity: fix before ship (copy).** Three of the six BELOW headline rows have a stated nominal sitting at the near edge of a very wide, lopsided range: 2022 CE2 (nominal 0.9 percent of the way from minimum to maximum, range 2.57 million km), 1999 AO10 (0.4 percent, 53,000 km), 2017 WJ2 (14 percent, 1.97 million km). Their shift in "stated sigma" is −0.1, −0.3 and −1.0 while they read outside. That is consistent with the target-plane geometry (a minimum over an ellipse can sit close to the nominal), and the BELOW reading is right on the plan's rule. The page must say so, or the shift column looks like it contradicts the reading. Fix: one note under the outside table.

**R6. Independence. Severity: fix before ship (copy).** The Wilson interval treats rows as independent. 13 of 14 outside rows come from one copy, which is one moment of JPL's data and software. Rows from one copy can share a cause, so the interval can be too narrow. WATER says the same thing about neighbouring water years. Fix: one sentence. No cause is named.

## 6. The cell rule

Sealed in PLAN.md at 2314da1 (11:07:37Z). The first comparison was at 11:14:08Z (plan_seal.json), the plan hash matches, and the plan file is unchanged since. neo_tick.py's cell_outcome is the plan's rule in the plan's order. The gate-2 row replaced before the first full read (a Ceres query the frame excludes) is disclosed in CHECKS.md R.

Soundness:
- BELOW when the 95% upper bound is under 99.73 percent. Sound, and robust to the 98.9 percent floor (R1).
- CONSISTENT when the lower bound is 98 percent or more. This is a loose standard next to 99.73. It means "not shown to be below, and at least 98 percent". It is pre-registered and the page states it. The 0 to 7 day cell clears it by 0.05 points (R4). Fix: say on the page that one row outside would make the cell cannot tell.
- ABOVE when the lower bound is over 99.73 percent. It needs about 1,400 rows all inside. Harmless.
- Four lead cells and one subset with no multiplicity adjustment. Note only. The two BELOW cells overlap (all leads contains more than 30 days).

## 7. Copy rules (neo.html draft)

lint_copy.py gives 0 hits, and I re-read the visible text in full. No semicolons, no AI statements, no cause words, no digits in headings, Heuremen LLC named, "our reading" marks the 99.7. Faults beyond R1 and R3 to R6:
- "Copies of our own: 1" and "Rows read: 15283" sit in the sources line, not a title or lead. Fine. "15283" should print as 15,283.
- The User-Agent's contact is https://indahl.ai/neo, which goes live with this ship.
- JPL's fair-use terms forbid embedding the APIs in a website. The page serves our own derived file (/neo/live.json) and never calls JPL from the browser. Fine.

## 8. Fixes, in order

1. R4: headline line names the split and the 9 Feb 2024 dependence, from a new display block in neo_tick.py (`dependence`, labelled after the data).
2. R3: remove the 32 percent sentence.
3. R1: add the 98.9 percent floor and say the readings are the same against it (computed in neo_tick.py, not typed).
4. R5: lopsided-range note under the outside table, with the lopsided rows flagged by the code.
5. R6: independence sentence.
6. Section 6: one-row fragility sentence for a consistent cell at the floor.
7. Thousands separators in the sources line.

No outcome changes. No plan change. A re-referee is not needed for the numbers. The changed copy should be cold-read once on the live page.
