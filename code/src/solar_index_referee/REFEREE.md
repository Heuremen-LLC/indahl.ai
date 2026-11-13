# Referee report: SOLAR desk (SWPC stated space-weather chances against the delivered record)

Referee: read-only refuting pass, 10 November 2026. Nothing in `solar_index/` was edited.
Inputs read: PLAN.md (commits 07b57e8 and 92b157b, `git show 07b57e8:PLAN.md`), data/plan_seal.json, solar_tick.py (including its uncommitted edit), heuremen_kit.py, summary_solar.json, data/solar.json, data/known_good_rows.json, solar.html, build_page.py, solar_headline.py, CHECKS.md, every raw file under data/raw (RSGA tars and day files, events tars and day files, DGD, DSD, SPE.txt, GFZ Kp), and the SWPC RSGA README and Edited Events README (both fetched by curl from ftp.swpc.noaa.gov on 10 Nov 2026).

Referee code is in `code/`. `recount.py` has its own RSGA reader, events reader, DGD reader (regex and a fixed-width cross-check, 0 mismatches), DSD reader, SPE reader, Wilson interval, bin rule, Brier skill and block bootstrap (numpy, seed 27, 2000 reps, 27-day moving blocks). It imports nothing from solar_tick.py or heuremen_kit.py. Everything was run with `python3 -I`. Outputs are in `out/`.

## Verdict

**HOLD.** Do not ship the page as built. The desk's events reader silently drops every flare line whose event number is below 1000, about 10 percent of all X-ray lines. That undercounts M-class days by 68 and X-class days by 11, and it changes the fixed headline from "7 of 8 bins consistent" to "4 of 8 bins consistent, 4 above". The rule, the plan, the stated-side reader, the geomagnetic side and the proton hold all reproduce exactly. Once the reader is fixed and the page rebuilt, this becomes FIX THEN SHIP: the remaining findings are copy and display. No threshold, bin, event or plan rule needs to change.

## Findings

| # | Severity | Finding |
|---|---|---|
| 1 | **blocks ship** | Events reader drops XRA lines with event id under 1000 (leading space). M and X cells, the M-only described row and the headline are wrong. |
| 2 | **blocks ship** (same fix) | The headline "7 of 8" is wrong. Correct: 4 of 8 consistent, 4 above, 0 below, Brier skill 0.268. |
| 3 | fix before ship (code) | Join gate passed at 96.3 percent and its 67 disagreeing days were never looked at. 56 of the 67 were the bug in finding 1. |
| 4 | fix before ship (copy) | Middle-latitude reading: Fredericksburg K is a poor fit, planetary Kp fits. The page's lines and table must say so beside the BELOW readings. |
| 5 | fix before ship (copy) | Held proton cells print a Brier skill of -2.35 on the page and `outcome_before_hold` in the public feed. |
| 6 | fix before ship (copy) | Addendum 1 item 2 and the page count refusals wrongly: the amendment file is never read, so "refused: 1" should read 2. |
| 7 | fix before ship (copy) | Headline line and "other events" sentence lead with the one event that reads closest to consistent, and the sentence lists only "less often" counts. Add one overall line. |
| 8 | note | Report-day change (Addendum 1 item 1) does not select on outcomes. |
| 9 | note | Code was not sealed. Only PLAN.md was committed before the first comparison. |
| 10 | note | Wilson independence statement is adequate for most cells, too narrow for M and high latitude. Six bins flip under my block bootstrap. |
| 11 | note | Event definitions: all supported by SWPC text; sum of Minor and Major-severe is defensible. |
| 12 | note | Flare day assignment, duplicates, channel, secondary satellite: no material effect. |
| 13 | note | Proton hold is right and the omission claim is true. |
| 14 | note | Licences: clean. No sunspot number in any output. |

## 1. Recount from raw

Rows: 44,940 on both sides (2,140 issue days x 3 leads x 7 events). Status counts are identical on both sides: scored 42,766; after the proton list last changed 1,062; no K for the day 742; no RSGA on file 126; not yet settled 105; issued late 91; dates do not match the issue day 42; no events file 6.

Row-by-row diff against data/solar.json (status, p, o): **237 rows differ, all in M (204) and X (33)**, every one with the desk at o = 0 and the referee at o = 1. Zero differences in status or p anywhere. Zero differences in P, MID5, MID6, HI5, HI6. (`out/diff_vs_desk.json`)

Cells: 15 of 21 cells (proton, middle and high latitude, all three leads) reproduce exactly: n, events, mean stated, observed, Wilson lo and hi, outcome for every bin, Brier score, Brier skill. The six M and X cells differ because of finding 1.

Skill bootstraps, my own blocks and generator: for the 15 identical cells the skill interval bounds agree within 0.03 except the held proton cells (for example P day 1 desk [-4.87, -1.69], mine [-4.68, -1.65], same place); bin bootstrap bounds agree within 0.048 on all 111 bins with a bootstrap. Skill outcomes (ABOVE, BELOW, CANNOT_TELL) agree in all 21 cells on both records.

Corrected M and X cells (referee):

| Cell | Days | Event days (desk -> referee) | Brier score | Climatology | Skill, referee | Skill, desk | Bins n>=30 (referee) |
|---|---|---|---|---|---|---|---|
| M day 1 | 2,114 | 693 -> 761 | 0.16858 | 0.23039 | 0.2683 [0.203, 0.320] ABOVE | 0.2495 [0.186, 0.304] | 4 consistent, 4 above, 0 below |
| M day 2 | 2,126 | 704 -> 772 | 0.18622 | 0.23126 | 0.1948 [0.123, 0.252] ABOVE | 0.1814 | 3 consistent, 5 above |
| M day 3 | 2,125 | 703 -> 771 | 0.19571 | 0.23118 | 0.1534 [0.079, 0.212] ABOVE | 0.1458 | 4 consistent, 4 above, 0 below (desk had 1 below) |
| X day 1 | 2,114 | 76 -> 87 | 0.03887 | 0.03946 | 0.0149 [-0.115, 0.132] CANNOT_TELL | -0.0236 | 2 consistent, 3 below |
| X day 2 | 2,126 | 77 -> 88 | 0.03953 | 0.03968 | 0.0038 [-0.115, 0.111] CANNOT_TELL | -0.0343 | 2 consistent, 3 below |
| X day 3 | 2,125 | 77 -> 88 | 0.04004 | 0.03970 | -0.0087 [-0.124, 0.092] CANNOT_TELL | -0.0404 | 2 consistent, 3 below |

M day 1, every bin (referee; Wilson interval and my block bootstrap interval):

| Bin | n | Events | Mean stated | Observed | Wilson | Outcome | Block bootstrap | Outcome on bootstrap |
|---|---|---|---|---|---|---|---|---|
| 0 to 2 | 285 | 9 (desk 7) | 1.00 | 3.16 | 1.67 to 5.89 | ABOVE | 1.3 to 6.2 | ABOVE |
| 3 to 7 | 160 | 11 (10) | 5.00 | 6.88 | 3.88 to 11.89 | CONSISTENT | 3.5 to 11.1 | CONSISTENT |
| 8 to 17 | 299 | 51 (47) | 12.42 | 17.06 | 13.22 to 21.73 | ABOVE | 13.4 to 21.3 | ABOVE |
| 18 to 27 | 265 | 70 (61) | 23.15 | 26.42 | 21.47 to 32.03 | CONSISTENT | 21.2 to 32.0 | CONSISTENT |
| 28 to 42 | 406 | 159 (146) | 35.60 | 39.16 | 34.54 to 43.99 | CONSISTENT | 33.3 to 44.9 | CONSISTENT |
| 43 to 57 | 344 | 189 (164) | 51.21 | 54.94 | 49.66 to 60.12 | CONSISTENT | 48.8 to 61.4 | CONSISTENT |
| 58 to 72 | 216 | 152 (145) | 63.63 | 70.37 | 63.97 to 76.06 | ABOVE | 62.0 to 77.1 | CONSISTENT |
| 73 to 87 | 130 | 111 (105) | 76.62 | 85.38 | 78.30 to 90.44 | ABOVE | 73.3 to 93.0 | CONSISTENT |
| 88 to 100 | 9 | 9 (8) | 92.78 | 100 | 70.1 to 100 | CANNOT_TELL | | |

Overall M day 1: mean stated 32.0 percent, observed 36.0 percent (761 of 2,114). Observed is above mean stated in 8 of 9 bins. The desk's 32.8 percent base rate is 36.0.

The other 15 cells for reference (referee = desk): MID5 day 1 skill 0.0085, 1 consistent 6 below; MID6 day 1 skill 0.0986, 2 consistent 2 below; HI5 day 1 skill -0.0472, 1 consistent 5 below; HI6 day 1 skill -0.0904 BELOW, 6 below.

## 2. Is the stated side as issued before the outcome?

- Files read: 2,134 report days from 2021 on parse (2,135 report files carry the Part III and VI blocks, counting one that falls before the frame). Missing report days: 2022-06-29, 2022-12-16, 2024-06-01 (only a correction exists), 2025-11-13, 2026-04-25, and 2026-11-10 (today). That is 6 days, 126 rows, as the desk says.
- Issue time. 2,096 of 2,134 reports carry `:Issued:` exactly 2200 UTC of the report day (others minutes to hours late). 13 reports were issued after the report day ended (00:05 to 19:15 the next day: 2021-06-09, 2021-11-01, 2022-04-26, 2024-04-25, 2024-06-18, 2024-10-18, 2024-11-04, 2025-05-20, 2025-08-28, 2025-10-14, 2026-03-14, 2026-04-07, 2026-09-03). For these, day one is issued after its midnight and is not scored, which is the plan's rule (91 rows = 13 x 7). Their day two and day three are before their target day and are scored. Nothing was scored with a forecast issued after 00:00 UTC of its target day.
- Corrections: the 1 June 2024 file ("SDF Number 152 Correction") is refused. The 3 December 2024 amendment is `2024_RSGA/2024onRSGA.txt` ("Issued at 2322Z (AMD)"). It is never read, because both the desk and my reader only take names with 8 digits before RSGA. The original 3 December report (issued 2235) is read, but its Part III header says "03 Dec-05 Dec" (the amendment presumably fixes this), so it fails the date gate and is not scored. The 7 March 2026 report has the same header typo ("07 Mar-09 Mar") and is also not scored. Those two days account for the 42 "dates do not match" rows (2 x 3 x 7). Dropping both is the cautious choice. See finding 6 for the count that the page gets wrong.
- Report-day assignment (Addendum 1 item 1). The old key (`:Issued:` date) and the new key (SDF line day) differ on 26 day keys. Under the old key the 13 after-midnight reports took the next day's key, the next day's own 2200 report lost it, and 13 day-one rows were unscored. Under the new key those 13 rows are scored and nothing else changes: lead 1 gains 13 rows, leads 2 and 3 gain 26 each, 0 rows removed, 0 rows with a changed p or o. The rule uses printed text timestamps only. It cannot select on outcomes. For information, the 13 added M rows have 8 flare days (62 percent against 36 percent overall), because after-midnight reports follow busy periods. They are scored on the same rule as every other row. Note only (finding 8).
- Part III and Part VI parse, by eye against raw text on six files (`out/eyeball.txt`): 15 Mar 2021, 22 Feb 2022, 19 Jul 2023, 25 Apr 2024 (late report), 2 Oct 2025, 14 Mar 2026 (late report). Every triple equals the raw text. Across all 2,135 report files each label occurs once per block, with one casing variant ("Minor Storm") and no other label. No triple is missing or outside 0 to 100. Capped sums: exactly 1 (2021-11-01 high latitude, Minor 20/20/50 plus Major 20/25/75, day three).
- The three reader-gate rows in known_good_rows.json (15 Mar 2021, 5 Nov 2026, 9 Nov 2026) equal the parsed rows. The 15 Mar 2021 row matches my eyeball read. The two 2026 rows reference `2026/RSGA/...` files, which I did not separately open beyond the full parse.

## 3. Event definitions against SWPC's own text

RSGA README (3 Jan 2008): "Class M and class X: Probability forecast of the occurrence of one or more class-M or class-X x-ray flares for each of the next 3 days." Part VI: "the probability of at least one 3-hour K index, at the indicated level, for each of the next 3 days. Active K = 4, Minor storm K = 5, Major or Severe storm K >= 6." Part V says "AFr indices (A-indices from Fredericksburg, VA)" and "AP-indices (planetary A-indices)". Part VI names no station. The README sample's issue 02 Jan has Part III headed "03 Jan-05 Jan", so day one is issue day plus one, as the plan says.

Edited Events README: "The UTC day of the event's begin time is the UTC day of the list. The UTC day of the maximum and/or end times may or may not be the same as the begin time ... if the maximum or end time is less than the begin time, then assume the times are for the next UTC day." XRA is "X-ray event from SWPC's Primary or Secondary GOES spacecraft", class "x = peak flux in the 0.1 to 0.8 nm range", M is 1e-5 <= x < 1e-4 and X is x >= 1e-4 W m-2.

**Class M as M or greater: plausible, not proven.** In all 6,402 stated triples Class X is never above Class M, which fits "M or greater" (X flares are a subset). The README sentence "one or more class-M or class-X flares" reads either way. Empirically the two readings give almost the same result (M-only, M1.0 to M9.9, 749 days against 761: skill 0.266 against 0.268, 5 consistent and 3 above against 4 and 4), so the page's description is enough. Say plainly that it is the plan's reading and give the M-only row.

**Minor + Major-severe for K>=5: defensible.** The categories behave as mutually exclusive classes of the day's greatest K. At middle latitudes Active + Minor + Major-severe exceeds 100 in only 3 of 6,405 triples (max 105). At high latitudes it exceeds 100 in 70 of 6,405 (1.1 percent). Minor is below Major-severe in 45 of 6,402 middle triples and 3,119 of 6,402 high triples, so they are not cumulative "K at least" figures. If they were cumulative, Minor would never be below Major. The sum is therefore P(greatest K >= 5) under the exclusive reading, and only 1 sum exceeds 100. Under the literal "at least one K at the indicated level" wording the sum would be an upper bound, so the plan's described literal row (Minor alone against "at least one K equal to 5") is the right companion and should stay.

**Middle latitude = Fredericksburg: not supported by the stated numbers, and the data say so.** Day one, referee (`out/station_reading.txt`, `out/exclusive_reading.txt`):

| Reading of "K>=5, middle latitudes" | Days | Mean stated | Observed | Skill |
|---|---|---|---|---|
| Fredericksburg K >= 5 (plan) | 2,047 | 15.8 | 8.9 | +0.009 |
| SWPC estimated planetary K (DGD) >= 5- (4.67) | 2,110 | 15.7 | 16.8 | +0.149 |
| GFZ Kp >= 5- | 2,115 | 15.8 | 15.4 | +0.133 |
| College K >= 5 | 2,060 | 15.8 | 43.2 | -0.235 |

By category of the day's greatest K (stated mean against observed): Active 24.6 against Fredericksburg 22.3 and planetary 22.0; Minor 11.9 against Fredericksburg 6.5 and planetary 11.2; Major-severe 3.8 against Fredericksburg 2.4 and planetary 5.6. The middle-latitude stated numbers track the planetary distribution; Fredericksburg's local K scale sits lower at K = 5 and above. For high latitudes the reverse holds: College K (Minor 23.8 against 21.8, Active 13.5 against 18.4) fits and planetary does not (Minor 11.2, Major 5.6 against stated 23.8 and 36). Correlation of the stated K>=5 chance with the day's greatest K: Fredericksburg 0.419, GFZ Kp 0.460, SWPC planetary 0.466. So the High = College reading holds up. The Middle = Fredericksburg reading gives BELOW in 6 of 7 bins, and under planetary Kp the same stated chances are close to calibrated (the desk's own described rows show 6 consistent of 7 for Kp 5-).

How the page should present it: keep the plan's Fredericksburg cells as scored, and keep calling the reading ours. But the three places where "middle latitude storms in 6 of 7 bins" is used as a finding (headline sentence, table, cell title) need a sentence directly beside them: the report names no station for Part VI; Part V names Fredericksburg for the A index; the stated chances sit far closer to planetary Kp than to Fredericksburg K; so a BELOW here may say more about which index is meant than about the forecaster. Show the planetary row at the same size as the Fredericksburg row, not in a "described, decides nothing" footer. Also fix the sentence "The planetary Kp ... is a different index from the one the report names": the report names none for Part VI. If planetary rows are shown, SWPC's own estimated planetary K from the DGD (which forecasters actually see) is closer to what the forecaster used than the GFZ definitive Kp, and GFZ's recent days are nowcast values.

## 4. Flare day assignment, duplicates, and the join gate

- Day = UTC day of the maximum (max earlier than begin goes to the next day). Cases: 17 M or X flares have a maximum on the next UTC day than the begin; 15 XRA lines have `////` for the maximum (uses the begin). Duplicate XRA lines from two satellites (G16 12,041 lines, G18 5,202, G19 710, G17 290) do not matter for a day-level yes or no. Only the 1-8A channel exists; the sole non-1-8A token is `2.28` on 19 Apr 2023 (a C2.7 line, no effect). The desk's regex does not test the channel field, so "1-8A only" is not enforced in code, but nothing changes.
- **Finding 1 detail.** The desk's XRA pattern starts with `^\d+`. In the Warehouse events files an event number below 1000 is printed with a leading space (` 560 +     0033 ...`). 1,800 of the 18,243 XRA lines (9.9 percent) begin with a space and all are dropped. Example: 7 May 2021 ` 640 +     1843   1904      1919  G16  5   XRA  1-8A      M3.9` is missed (DSD shows 1 M flare that day). Replaying the desk's pattern on the raw files gives 709 M-or-X days against my 777 (68 missing, 0 extra) and 77 X days against 88, and it reproduces the desk's 1,754 of 1,821 join exactly.
- **Join gate.** Desk: 1,754 of 1,821 (96.3 percent), 67 disagreeing days. With the reader fixed: 1,810 of 1,821 (99.4 percent). The 11 left: 10 are a midnight-crossing flare (M2.2 at begin 2358 on 14 May 2022, max 0008; 12/13 Oct 2022; 6/7 Nov 2022; 21/22 Dec 2023; 11/12 May 2025; 7 Dec 2025) where DSD counts the begin day and the plan counts the maximum day. Assigning by begin day gives 1,820 of 1,821. The 1 left is 4 Oct 2022 (M1.6 at 1248 in the events list, DSD M = 0). Neither record is mis-read on those 11. The X-flare join is 1,821 of 1,821 with the fix (desk 1,812). The begin-day assignment would change M day 1 by 1 event day (762 against 761) and skill by 0.004, so the plan's maximum-day rule can stay; the page should say DSD counts by begin day.
- The gate passed with a 3.7 percent mismatch, because the plan's threshold is 95 percent. The gate is only as good as its threshold and nobody looked at the disagreeing days. Fix: print the disagreeing days with the gate, and require the 11-day residual rather than 67 (a hard gate near 99 percent would have failed this run).
- Secondary satellite: 53 of 777 M-or-X days have the M or X logged only by an observer that is not the month's main one (partly the GOES-16 to 18 and 18 to 19 handovers). Note only.

## 5. Proton hold

True and right. The RSGA of 23 March 2024 reads "Protons greater than 10 MeV at geosynchronous orbit reached a peak level of 955 pfu at 23/1820Z", and SPE.txt has no 2024 entry between 9 Feb and 10 May. Beyond that example: RSGA Part IIA reports a >10 MeV peak of 10 pfu or more on 106 report days since 2021, and SPE.txt lists 23 start days in the frame. 67 of the 106 have no listed start within one day (`out/proton_check.txt`), among them 2024-03-23 (955), 2024-03-24 (724), 2024-06-08 (1,028), 2024-10-28 (363), 2025-06-01 (666). SPE.txt also contains an inconsistent entry ("Nov 21/1925 ... Nov 11/0355" in 2024), which the display-only "start through maximum" variant (Addendum 1 item 4) would mis-span. Scored against this list the proton chance reads BELOW in 4 of 5 bins with skill -2.35, which is the incomplete list talking. Holding is right. Note that the 2026-01-19 and 2026-01-20 reports (36,976 and 5,680 pfu) fall after the list's last change, so they are rightly excluded as "no delivered record".

## 6. Autocorrelation and bin flips

Residual (observed minus stated) autocorrelation, day one: M lag 1 = 0.18, lag 2 = 0.07, lag 7 = 0.02; X 0.03; MID5 0.07; HI5 lag 1 = 0.14, lag 2 = 0.10, lag 27 = 0.11. A Bartlett effective sample size over 27 lags is about 1,100 for M and 1,070 for HI5, 2,190 for X and 2,770 for MID5, against about 2,050 to 2,110 days. So independence is a fair approximation for X, MID5 and MID6, and a Wilson interval is too narrow (roughly sqrt 2 times) for M and HI5. Over 121 bins with n>=30, block bootstrap width divided by Wilson width has median 1.03, range 0.66 to 1.62, wider than Wilson in 60 percent. The plan's wording ("the interval can be too narrow, the page says so beside every table") is adequate, but the effect is not uniform and should not be described as small.

Outcome flips if the bin reading used my block interval (corrected data): 6 of 108 non-proton bins with n>=30. M day 1 58 to 72 and 73 to 87 (ABOVE to CONSISTENT), M day 2 18 to 27 (ABOVE to CONSISTENT), MID5 day 3 43 to 57 (CONSISTENT to BELOW), MID6 day 3 0 to 2 (ABOVE to CONSISTENT), HI6 day 1 8 to 17 (BELOW to CONSISTENT). On the desk's own `boot_lo` and `boot_hi` before the fix 5 bins flipped (M2 3 to 7, M3 58 to 72, MID5 2 0 to 2, MID6 3 0 to 2, HI6 1 8 to 17). On M day 1 the bootstrap reading gives 6 consistent and 2 above, against 4 and 4 on Wilson. The plan names Wilson as the deciding interval, so the headline stays the Wilson count, but a headline that says "4 of 8" must be printed with "6 of 8 on the block interval" nearby, since the two readings straddle the half.

## 7. Headline

Plan: M day one, big number = bins consistent out of bins with n>=30.
- Desk says 7 of 8 (7 consistent, 1 above, 0 below), skill 0.25 [0.19, 0.30].
- Referee: 8 bins with n>=30 (right), **4 of 8 consistent**, 4 above (0 to 2, 8 to 17, 58 to 72, 73 to 87), 0 below, skill 0.268 [0.203, 0.320], reads above zero.
- The line should read, for example: "For M-class flares on the day after each forecast, the share of days with a flare fell inside the interval of the chance NOAA SWPC stated in 4 of 8 bins. In the other 4 bins a flare came more often than stated: where it stated 1 percent on average, 3.2 percent of 285 days; 12 percent, 17.1 percent of 299 days; 64 percent, 70.4 percent of 216 days; 77 percent, 85.4 percent of 130 days." The generator already builds that sentence from the numbers, so fixing the data fixes the line.
- Misleading risks even after the fix (finding 7). (a) The headline cell is the one event whose stated chances are too low (observed above stated in 8 of 9 bins), while the rest of the record reads the other way: across all 108 non-proton bins with n>=30 the referee reads 34 consistent, 16 above, 58 below. The "other events" sentence lists only "less often than stated" counts, and omits MID6 and HI6, so a reader sees "4 of 8" followed by a list of below counts and cannot tell that M reads above. Add one sentence with the overall count, or state each event's direction (above for M, below for X, middle and high latitude storms). (b) "Brier skill 0.27, reads above zero, better than base rate" compares with in-sample climatology (the days' own base rate), which flatters climatology, so the skill is conservative. Say "base rate of the same days", which the page already does. (c) Day two and day three of M read above in 5 and 4 of 8 bins. The page links to them, which is right.

## 8. Licences and terms

- NOAA SWPC products are US government works. The Warehouse README says the files are "preliminary reports as originally published" and "SWPC does not encourage the use of preliminary data for research purposes"; the page states this.
- GFZ Kp: file header "LICENSE: CC BY 4.0, except for the sunspot numbers contained in this file, which have the CC BY-NC 4.0 license". Searched summary_solar.json, data/solar.json, data/solar_live.json, solar.html, build_page.py, CHECKS.md: no sunspot number, no SN column, no "sunspot" text outside the quoted licence note. The raw GFZ file is under `data/raw/`, which `.gitignore` excludes (git tracks no raw file), so the CC BY-NC column does not reach the public repository. The page carries the attribution (Matzka et al. 2021, doi 10.1029/2020SW002641, data doi 10.5880/Kp.0001). Add that the recent Kp values are nowcast and may be replaced.
- Reads are one at a time with a named user agent.

## Detail on findings

**1. Events reader (blocks ship).** Fix `XRA` to allow leading whitespace (`^\s*\d+`), and test the channel field (`1-8A`). Rebuild: M day 1 days with the event 693 to 761, X 76 to 87, and every M and X table, the M-only described row, the headline, the live feed. Then rerun. My recount equals the DSD M-plus-X day flag on 1,810 of 1,821 days (desk 1,754). This is an implementation fault against the sealed plan, not a plan change: the plan says an XRA event counts and defines the event, so the fix needs a short Addendum 2 saying the reader was fixed after an outside recount, how it was found (a DSD cross-check, not a read of the forecast outcomes), and what moved (M and X events counts, headline from 7 of 8 to 4 of 8).

**2. Headline (blocks ship, same fix).** The "7 of 8" appears in the page's big number and line, and `summary_solar.json`'s new `headline` block (`consistent 7, share 0.875`). It becomes 4 of 8, share 0.5.

**3. Gate (fix before ship, code).** Print the disagreeing days with the gate result. The 56 days fixed by finding 1 were visible as 67 disagreements in the gate. Treat anything beyond midnight-crossing days as a failure to explain.

**4. Middle latitude presentation (fix before ship, copy).** As in section 3.

**5. Held proton cells (fix before ship, copy).** Addendum 1 item 3 says "their computed figures stay in the data, labelled as held". The page table prints the proton Brier score 0.043, skill -2.35 and interval -4.87 to -1.69 beside "held", and `summary_solar.json` and the live feed carry `outcome_before_hold`. A skill of -2.35 beside a note that the record is incomplete still reads as a finding. Show a dash for score and skill on the page, and keep the numbers in the data file only. The held bins show "0 0 0" for consistent, above and below on the page, which is right.

**6. Refusal count (fix before ship, copy).** Addendum 1 item 2 says the code "refuses both by name and counts them". The AMD file `2024onRSGA.txt` is never read (the name filter needs eight digits) and is not counted. `sources.rsga_unparsed` is 1 (the correction). The page says "Reports refused as a correction or amendment, or that did not parse: 1". It should say 2, and the refusal should be by name as the addendum says. Also mention the two reports with a header date typo that were read and not scored (3 Dec 2024, 7 Mar 2026), which the page already counts under "dates in the report that do not follow its own day".

**8, 9.** Notes as above. The plan was committed 09:19:32 -0500 (14:19:32Z), the first comparison ran at 14:25:43Z (6 minutes later), and the plan sha256 in plan_seal.json equals `git show 07b57e8:PLAN.md` (12c748f4...). The addendum is additive (7 inserted lines, 0 changed) and labelled. solar_tick.py and heuremen_kit.py were first committed in 92b157b after the first read, and solar_tick.py has an uncommitted edit now (the headline function). `plan_unchanged_since_commit: false` in the summary is just the addendum. For future desks put the code commit in the seal. For this one, commit the fixed reader with Addendum 2.

**10.** As in section 6. Print the block-interval reading with the Wilson reading in the headline line, not only in the table.

**11, 12.** As in sections 3 and 4.

**13.** As in section 5.

**14.** As in section 8.

## Files

- `/Users/heuremen/bones-forge/solar_index_referee/code/recount.py` (own readers, rulers, diff, own bootstrap)
- `/Users/heuremen/bones-forge/solar_index_referee/code/explain_flares.py`, `flare_extra.py`, `secondary_sat.py` (flare reader fault, day assignment, DSD join)
- `/Users/heuremen/bones-forge/solar_index_referee/code/stated_checks.py`, `eyeball.py`, `addendum1_effect.py` (stated side, parse by eye, report-day rule)
- `/Users/heuremen/bones-forge/solar_index_referee/code/station_reading.py`, `exclusive_reading.py` (middle and high latitude readings)
- `/Users/heuremen/bones-forge/solar_index_referee/code/proton_check.py`, `autocorr_missingK.py`
- `/Users/heuremen/bones-forge/solar_index_referee/out/` (rows.json, recount.json, diff_vs_desk.json, boot_flips.json, and a text output per script)

## Re-check, 10 November 2026 (commit 1f5097c)

Read-only. Reran `code/recount.py` against the new data/solar.json and summary_solar.json, and read solar.html, solar_headline.py output (via summary headline), build_page output and PLAN.md Addendum 2.

**Verdict: SHIP.** Nothing blocks.

1. Rows and headline (finding 1, 2). Row diff: 44,940 against 44,940, **0 differences** in status, p and o. Every cell and bin I compute equals the desk's (no cell or bin differences reported). Headline block: 8 bins, 4 consistent, 4 above, 0 below, share 0.5, skill 0.2683 [0.2086, 0.3225] ABOVE, 6 of 8 on the block interval (mine 6 of 8). All-bin counts 34 / 16 / 58 equal mine; per-event counts for M (13 above, 11 consistent over three leads) equal mine. Page big number reads "4 of 8".
2. Refusals (6). `rsga_unparsed` is 2: the 1 June 2024 correction and `2024onRSGA.txt` (amendment), both by name. The page says "refused ... : 2".
3. Held proton (5). The string `before_hold` and `held_figures` do not occur in summary_solar.json or data/solar_live.json. Proton cell skill, brier and bin figures are null there; the page shows dashes and "held". The figures sit under `held_figures` in data/solar.json only. (That file is the row feed, so if it is served publicly the held figures are still reachable there. Your call, noted as such.)
4. Middle latitude (4). Both middle-latitude tables carry the paragraph "The report names no station ... Part V names Fredericksburg ... may say more about which index is meant than about the forecast", followed by a same-size table against SWPC estimated planetary K. The described rows equal my recount: K >= 5-, 2,110 days, observed 16.78 percent, skill 0.1494; K >= 6-, 5.59 percent, skill 0.1254. The false "names" wording is gone. The headline also carries a sentence on it.
5. Headline (7, 10). The line now gives the four above bins with observed and stated figures, the block-interval count (6 of 8), the overall 34 / 16 / 58, and says M came more often than stated while X and storms mostly came less often. That addresses both findings.
6. Addendum 2 states how the reader fault was found (the Daily Solar Data cross-check and a recount, not the forecasts), what changed, and that no threshold, bin, event or rule changed. Accurate. The join line on the page reads 1,810 of 1,821.
7. Licence: no "sunspot" text in the summary, feed or page.

Still open as notes only: the code was sealed after the first read (finding 9, now committed), and finding 3's suggestion of a tighter join gate was met by printing the disagreeing days.
