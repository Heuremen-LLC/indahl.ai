# WATER desk, refuting referee pass

Read-only pass on ~/bones-forge/water_index/ (nothing there was edited). Fresh pulls from HDB, RISE, CDEC and the Lower Colorado feed were made on 10 Nov 2026 between about 03:05 and 03:25 UTC. Scratch scripts and pulls are in /private/tmp/claude-501/-Users-heuremen/b41d2241-cc55-49dd-8b48-5ec14786a97e/scratchpad/ref/.

## Verdict: FIX THEN SHIP

The counts hold up. The Lake Mead six-month count recounts exactly from raw. Lake Powell is off by one row because our reader missed one readable table, and its outcome doesn't change. The seal is genuine and comes before the first scored output. The live panel matches RISE and HDB right now.

What has to change is mostly framing. Reclamation itself states the 80 percent elevation figure in its Minimum and Maximum reports, so the page is wrong to call it "our reading". Beyond that, the "34 of 96 against about 5 by chance" sentence doesn't hold up, the Lake Powell headline outcome depends on which ruler is used, and several things the plan promises are missing from the page.

## Issues

### Blocks ship

**B1. The 80 percent benchmark is Reclamation's own statement, not our reading.**
Evidence: since January 2010 every Probable Minimum and Probable Maximum report that has a narrative page says this on page 1 (quoted from APR26_MIN_508.pdf and OCT26_MAX_508.pdf, the same wording back to JAN10_MIN_508.pdf):
"Probable minimum and probable maximum model runs are conducted in January, April, August, and October, or when necessary to incorporate changing conditions. The Probable Minimum inflow scenario reflects a dry hydrologic condition which statistically would be exceeded 90% of the time. The Most Probable inflow scenario reflects a median hydrologic condition which statistically would be exceeded 50% of the time. The Probable Maximum inflow scenario reflects a wet hydrologic condition which statistically would be exceeded 10% of the time. There is approximately an 80% probability that a future elevation will fall inside the range of the minimum and maximum inflow scenarios. Additionally, there are possible inflow scenarios that would result in reservoir elevations falling outside the ranges indicated in these reports."
- 182 of 205 Minimum and Maximum reports carry the sentence.
- 79 of the 86 band months carry it in both reports.
- The seven band months without it print tables only: 2006-08, 2008-04, 2008-08, 2009-04, 2009-08, 2016-10 and 2023-10.
- The plan and page copied only the RISE catalog blurb. None of the 530 catalog entries carries the sentence. Only the report PDFs do.

Wrong copy right now:
- The headline: "which is our reading of the inflow probabilities Reclamation states".
- Page paragraph 3: "Those probabilities describe inflow, not elevation. Reading the range ... as one that should hold about 80 percent ... is our reading".
- PLAN.md line 11.

Fix:
- Quote Reclamation's sentence on the page and in the headline.
- Keep "our reading" for the Most Probable-as-median test only.
- Add a dated Addendum 2 to the plan, marked as after the first comparison. It records the sentence, which band months carry it, and that no rule or threshold changed.
- Suggested headline line: "Reclamation's Minimum and Maximum reports say there is approximately an 80% probability that a future elevation will fall inside the range. At that rate about 66 of each would have." No numbers change.
- Optional extra check, marked as added after the data: restricted to the 79 months that carry the sentence, lead 6 reads Mead 37 of 76, interval 29.0 to 71.0 percent, BELOW, and Powell 45 of 75, 38.6 to 79.7 percent, BELOW.

### Fix before ship

**F1. "34 of 96 against about 5 by chance" isn't a fair comparison.**
- The 9.2 cutoff assumes 96 independent cells. In fact each lake's 24 band cells reuse the same 86 issue months. Neighbouring leads share target months, and the band and Most Probable cells at a lead share rows.
- The cluster ruler's false-flag rate per cell isn't 5 percent either (see F2).
- "If every stated figure held" is half wrong. Reclamation states the 80 percent but not the 50 percent median.
- The flagged count also depends on the ruler: 34 on the plan ruler, 28 with clusters weighted by size (Kish), 19 with two-water-year blocks.

Fix: drop the chance cutoff and the `above_chance` field. Say what the cells are instead: "Cells reading above or below: 34 of 96. Lake Mead band at 20 leads, Lake Powell band at leads 0 to 6, Lake Powell Most Probable at leads 17 to 23. Neighbouring cells share reports and target months, so these are not separate results."

**F2. The Lake Powell six-month outcome depends on the ruler. Lake Mead's doesn't.**
The plan counts distinct target water years as n_eff. Under the plan's own premise that rows in a water year move together, unequal cluster sizes shrink the effective count to (sum of m)^2 / (sum of m^2). At lead 6, water year 2022 holds 11 rows and most others hold 4, so the effective count is 16.2, not 20.
- Powell lead 6 then reads CANNOT_TELL. With two-water-year blocks it also reads CANNOT_TELL, interval 35 to 85 percent.
- The plan ruler's upper bound is 78.1 percent, and 79.7 percent on the 79 months that carry the sentence.
- Mead lead 6 reads BELOW under every ruler tried.

Fix: keep the plan's outcome but print, marked as checks added after the data, that Powell's six-month BELOW reads cannot tell when water years are weighted by row count or paired, and that Mead's holds. The feed's "second ruler" (rows counted as independent) only shows the less conservative side, so it shouldn't be the only alternative shown.

**F3. Lake Powell six months ahead is 49 of 83, not 49 of 82.**
- The Lake Powell table in AUG20_MIN_508.pdf (Probable Minimum, August 2020) wasn't found by the reader (coverage shows `powell no table: 2`). That made all 24 Powell rows from that band month CANNOT_TELL.
- The table is readable. The February 2021 row is "Feb 2021 327 338 7 680 0 680 3582.55". HDB run 3122, printed in the report, gives 3582.5495, and also matches August 2021 (3570.53) and February 2022 (3553.38).
- With it, the lead-6 Powell row is BELOW (measured 3571.46 against a band of 3582.55 to 3588.46), so the count is 49 of 83 with 26 below. 22 Powell band cells each gain one row and no outcome changes.

Fix: either fix the reader (stated side only, logged as a dated addendum) or put a line on the page naming the unread table.

**F4. The water-year ruler as written isn't conservative, and the page implies it is.**
Besides F2, rows at leads above about 6 straddle water years:
- An April study's October target sits in the next water year, so one forecast season is split across two clusters.
- Lag-1 correlation of the per-water-year inside share is about zero at lead 6 (-0.04 Mead, -0.06 Powell) but 0.59 (Mead) and 0.28 (Powell) at lead 12.

Fix: in the method note, say the ruler treats water years as independent and that neighbouring water years are correlated at long leads. Pair this with F2's sensitivity line.

**F5. No cell can ever read CONSISTENT.**
- With 18 to 21 water years per band cell, a 95% Wilson interval is about 0.33 wide at 80 percent. That can never fit inside 70 to 90 percent, which needs about 61 water years.
- The 40 to 60 percent Most Probable zone would need about 96.
- So the desk can only flag misses or say cannot tell. Yet the plan and page describe CONSISTENT as a possible outcome, and the plan promises "agreements as well as misses".

Fix: one sentence on the page saying CONSISTENT is out of reach at this sample size.

**F6. Things the plan promises that the page doesn't render.** water_live.js uses none of these feed fields:
- the 6.0 maf variant rows (plan: "The 6.0 maf run is shown apart")
- the inverted-band count (115 rows, 107 of them Powell, 96 at Powell leads 0 to 5)
- the Most Probable-outside-its-own-band count (269 rows)
- the misread rate for print-only values (Addendum 1 item 3: "The page states this rate")
- the Most Probable lead-6 cells in the headline (plan: "Headline: the band cells and the Most Probable cells at lead 6")

On the rate: 0.26 percent is measured on all HDB-backed tables. Print-only values come almost entirely from 2000 to 2011 reports (about 8,300 values). For HDB-backed 2000 to 2005 reports the rate is 1.0 percent (8 of 790 months), against 0.12 to 0.29 percent later. Many misreads are 10 ft digit swaps, such as 3588.51 for 3598.51, and the neighbour rule (30 ft and 40 ft) can't catch them.

Fix: render all five. State the rate by period, or say "0.3 percent overall, about 1 percent for 2000 to 2005 reports".

**F7. Short-lead band cells test bands that are sometimes zero wide. The page has to show this before a reader sees "BELOW".**
- At lead 0, 16 of 86 Mead bands and 10 of 85 Powell bands are zero wide (Minimum equals Maximum to 0.005 ft).
- Median width is 0.17 to 1.45 ft at leads 0 to 2.
- Reclamation's sentence covers "a future elevation", so the literal test stands. The width column is already there and labelled.

Fix: add the zero-width count next to the inverted count (F6). Name no cause.

**F8. Copy that isn't true as written.**
- "These rows are ... every projection of the latest measured month": the code shows leads 0 to 12 only (13 of the 24 per lake). Fix: "every projection made 0 to 12 months ahead", or show all 24.
- "Every row is in the full record": data/water.json isn't published or linked. Only /water/live.json is in the JSON-LD. Fix: publish and link the rows.
- "Plan, code and trend history for this page are public": WATER keeps no history file. Each run overwrites. LAUNCH has snapshots.jsonl. Fix: keep a history or drop "trend history".
- "Read about every half hour": only true once the rider is on the tick bus (CHECKS O1 says it isn't yet). The GitHub path code/water has to exist at ship.
- The live table titled "Other western reservoirs against stated capacity" has 9 rows, including Lake Mead and Lake Powell. Fix: drop those two (7 others) or retitle.

**F9. Governing-document quotes are verbatim, but four are cut mid-sentence and two labels are off.** All 11 entries match fresh copies of RecordofDecision.pdf (sha256 b2be62cf…, same as data/raw/docs) and 2027-2028OperatingGuidelines_Final.pdf (sha256 298883f1…, same). Problems:
- The 1,075 quote stops at "...Lower Division States" before "of which 2.48 maf...".
- The 1,050 and 1,025 quotes stop at "shall be apportioned".
- The 1,010 quote stops at "as appropriate" before ", to consider potential actions...".
- None of the four carries an ellipsis.
- The 3,565 entry is labelled "5.1.A.1 and 5.1.B.1", but the quoted sentence is 5.1.B.1 only. 5.1.A.1 says "at or above 3,565 feet".
- The 2.D.1.b and 2.D.1.c rows say they govern calendar year 2026. Only 2.D.1.a governed 2026, per the October 2026 study: "a Shortage Condition consistent with Section 2.D.1.a governs the operation of Lake Mead for CY 2026".
- The heading "Elevations named in the governing documents" covers one row that isn't an elevation (5.3.A.1). It also leaves out the 2019 Drought Contingency Plan and Minute 323 elevations. The October 2026 study names those as also governing CY 2026: "Section III.B of Exhibit 1 to the Lower Basin Drought Contingency Plan (DCP) Agreement and provisions in IBWC Minutes No. 323 and 330 also governs the operation of Lake Mead for CY 2026".

Fix:
- Add ellipses or quote whole sentences.
- Relabel 3,565 as 5.1.B.1 (or add the A.1 quote).
- Label 2.D.1.b and 2.D.1.c as "in force through 2026".
- Retitle to "Elevations named in the 2007 Interim Guidelines and the 2027-2028 Operating Guidelines", or add the DCP lines.

**F10. The builder's summary has one wrong figure and two loose ones. Don't carry them into the ledger or any post.**
- "The same study had Mead 15.5 ft above where it ended": 15.47 ft is the April 2026 Probable Minimum's gap (1054.32 against 1038.85). The Most Probable was 17.78 ft above (1056.63).
- "11 elevations": it's 10 elevations and one shortage provision with no elevation.
- "lowest daily reading since 1938": the page correctly says lowest since December 1999, the start of the record it reads. "Since 1938" needs the full-history source named.

### Notes

- **N1. Seal details.**
  - plan_seal.json says "Resealed 2 minutes after the first seal". It was 12 seconds (02:16:06Z to 02:16:18Z).
  - The first seal's hash (316cab8a…) isn't recorded.
  - The seal is a local JSON file, not in git and not committed, so readers can't check "fixed before the comparison" from the page. I checked it against the session record (see check 3). Commit PLAN.md with plan_seal.json at ship, as the builder asked.
- **N2. The "Reading done before this plan was written" note is incomplete.** Before the seal the builder also read:
  - the full Lake Mead daily history with its record low and largest historic one-day jumps (02:02 to 02:03Z)
  - the narrative pages of the October 2026 study (02:11Z)

  Neither set a projection against a measured month, so no rule is tainted. Add them to the disclosure in Addendum 2.
- **N3. Live-panel extras added after the first comparison aren't labelled.** These are the largest 1, 2 and 7 day rise in 60 days and the lowest-since-December-1999 line. They're readings, not tests. Label them "added after the plan".
- **N4. Datum wording.**
  - "Elevations in feet above sea level" is loose. RISE gives Lake Mead's datum as the USGS 1912 "Power House Datum" ("Add 0.55 foot to convert to ... NGVD 1929").
  - "It is a separate gauge and datum" for USGS 09379900 isn't shown. Over 2,761 days, USGS daily mean minus HDB end of day has a median of -0.36 ft. That fits a different gauge but doesn't establish a different datum.
- **N5. The Most Probable interval column has no "on N water years" label.** The band column has one.
- **N6. Headline has no interval.** For "intervals say what they are", add "counted on water years, the 95% interval is 30 to 70 percent (Mead) and 39 to 78 percent (Powell)".
- **N7. Unlabelled fields in public live.json.** `row_lo` and `row_hi`, the second ruler, carry no label. Name them or leave them out of the public feed.
- **N8. Measured-side cross-checks aren't on the page.** The plan calls them "reported but not used for scoring". The builder's own run found HDB monthly and the Lower Colorado end-of-month table differ for Lake Mead in 9 months since 1990, for example 2002-06 (1159.19 against 1160.19), 2023-12 (1068.05 against 1068.18) and 2024-07 (1061.38 against 1061.49). Scoring uses HDB as planned. Print the disagreement count and the largest gap since 2000.

## The six checks

### 1. Recount from raw

**Lead-6 band, independent read.**
- I listed band months from the raw RISE catalog: 86 months, where both a Minimum and a Maximum report exist.
- I pulled each report's Model Run ID with my own regex, fetched the run fresh from HDB, and read the printed row from the PDF with my own row reader.
- 344 lead-6 values in total:
  - 298 print equals HDB
  - 29 print only (no ID), including the 20 values from the 10 text-only reports, all of which match the rows
  - 14 HDB only (my reader missed the line). 13 equal the row and one is the AUG20_MIN gap from F3.
  - 3 disagree. Two are OCR misreads in the PDF text layer, and the page image shows the HDB value, which the desk used: JUL22_MAX Jan 2023 Mead reads 1051.87 in the text and 1051.97 on the page, and AUG23_MIN Feb 2024 Mead reads 1068.86 in the text and 1068.96 on the page. The third is a changed run: OCT11_MAX Apr 2012 Powell prints 3635.65 (image-checked) against 3629.69 in HDB, and the desk used the print, per Addendum 1.

**Measured side.** All 15,202 measured values equal a fresh HDB monthly pull (334 months per lake, Jan 1999 to Oct 2026), with 0 mismatches.

**Lead-6 results.**

| Lake | Inside | Above | Below | Water years | k_eff | Wilson 95% | Outcome | Page says |
|---|---|---|---|---|---|---|---|---|
| Lake Mead | 42 of 83 | 19 | 22 | 20 | 10 | 29.9% to 70.1% | BELOW | same |
| Lake Powell | 49 of 83 | 8 | 26 | 20 | 12 | 38.7% to 78.1% | BELOW | 49 of 82, 25 below (see F3) |

**Wider check.** Of 7,265 band-report values at leads 0 and up that could be compared, 7,214 equal a fresh HDB pull to 0.01 ft. The 51 that differ all sit in the two runs below the 60 percent line, Aug 2006 Max (one run, both tables) and Oct 2011 Max Powell. There the print stands by rule, and I checked the print on the page image.
- Nine fresh HDB requests came back empty. Those values were checked against the print instead.
- I also confirmed Addendum 1's gap claim: 9 runs at 48 percent agreement or less, none between 48 and 68 percent, then the next at 68 percent.

**Notable rows** (PDF text, page images and fresh HDB/RISE):

October 2026 study, report dated "October 15, 2026", end-of-October Powell:

| Source | Value (ft) |
|---|---|
| Most Probable, 7 maf run | 3519.23 |
| Most Probable, 6 maf run | 3519.23 |
| Probable Minimum | 3519.23 |
| Probable Maximum | 3519.50 |
| Measured (HDB monthly and RISE item 508 for 31 Oct) | 3531.90 |

April 2026 study, October 2026 target:

| Lake | Minimum | Most Probable | Maximum | Measured | Measured minus Most Probable | Outcome |
|---|---|---|---|---|---|---|
| Lake Powell | 3472.43 | 3479.67 | 3509.03 | 3531.90 | +52.23 | ABOVE |
| Lake Mead | 1054.32 | 1056.63 | 1059.45 | 1038.85 | -17.78 | BELOW, 15.47 ft under the Minimum |

**Random rows.** All match the report PDFs. Measured values match fresh HDB.

Seed 20261109, 5 rows from all scored rows:

| Report | Lake and month | Value (ft) |
|---|---|---|
| APR05 | Powell Oct 2005 | 3599.71 |
| MAY01 | Mead Aug 2002 | 1178.99 |
| FEB14 | Mead Feb 2015 | 1088.04 |
| MAY08 | Powell Nov 2008 | 3631.49 |
| NOV17 | Mead Jul 2019 | 1069.96 |

Seed 20261110, 5 band rows:

| Issue month | Lake and month | Most Probable / Min / Max (ft) | Note |
|---|---|---|---|
| APR15 | Mead Jan 2016 | 1081.78 / 1074.78 / 1083.15 | |
| SEP21 | Powell Sep 2021 | 3545.13 / 3545.23 / 3545.03 | inverted |
| AUG12 | Mead Nov 2013 | 1106.36 / 1102.53 / 1138.57 | |
| FEB21 | Powell May 2021 | 3565.88 / 3561.83 / 3576.95 | |
| AUG24 | Mead Aug 2024 | 1063.35 / 1063.14 / 1063.78 | |

Two largest-miss rows: DEC10 Mead Dec 2011 1082.67, JUL20 Powell Jul 2021 3600.67.

### 2. The 80 percent benchmark

**Reclamation's description** is quoted in B1. It states the 80 percent for elevation directly.

**Is 80 percent the right null?** As a test of what Reclamation says, yes. That is the stated claim, and the 70 to 90 percent zone covers "approximately". As a statistical expectation for a band built from two inflow scenarios with operations set by rule, it is generous in three ways:
- The scenarios share the observed start and the current month, so bands at leads 0 to 2 are often under a foot wide, and sometimes zero.
- Elevation isn't monotone in the scenario where releases respond by rule. 115 rows are inverted, mostly Powell at short leads. Example: in OCT11 the Maximum run releases 1,250 kaf in April 2012 against 605 kaf in the Minimum run, so April Powell is lower under the wet scenario.
- The band spans inflow only. It doesn't span operating choices made outside the rules.

The April 2026 study shows that last pattern: Powell ended above its Maximum while Mead ended below its Minimum. The page shouldn't name a cause. It should show width, inversions and zero-width bands (F6, F7) so readers can see what the 80 percent is being tested on.

**If the benchmark were wrong, which outcomes change?**
- Taking Reclamation's sentence literally (the fixed copy): no outcome changes. Only the attribution does.
- If the 80 percent applied only where the sentence is printed: lead 6 still reads BELOW for both lakes (Mead 37 of 76, Powell 45 of 75). Band BELOW cells go to Mead 22 and Powell 8, against 20 and 7.
- If the benchmark were rejected altogether: the 27 band BELOW cells and both headline outcomes would become plain coverage readings with no verdict. The flagged count would drop from 34 to the 7 Powell Most Probable cells, and those test our 50 percent reading, not a stated figure.

### 3. Plan seal

The seal chain checks out against the PLAN.md versions rebuilt from the builder's session transcript (agent a581d79d3a1ca8d61):

| Version | Time (UTC) | sha256 | Status |
|---|---|---|---|
| First write | 02:16:06Z | 316cab8a… | Not recorded in plan_seal.json |
| Semicolons removed | 02:16:18Z | 78ba2f9a… | Matches `sha256` |
| Plus Addendum 1 | 02:47:39Z | 1d24d13b… | Matches `addendum_1` |
| Wording edit after the comparison | 02:53:12Z | b16bf6a1… | Matches `wording_edit_1`, today's PLAN.md byte for byte, and `plan_sha256` in summary_water.json |

- The wording edit changed "by eye" to "directly from the page text" in two places. A diff confirms nothing else changed.
- The first comparison started at 02:47:51Z, 12 seconds after the Addendum 1 seal. It returned "lead-6 band Mead 42/83 Powell 49/82" by 02:48:43Z.
- No step between 02:16 and 02:47 set a projection against a measured month. Stated-side parse checks, known-good runs and measured-only reads took place in that window.
- Edits after the comparison (band width, lows, the second ruler, stale-source flags, ISO dates) didn't touch outcome rules. Caveats are in N1 and N2.

### 4. Independence

- **The water-year ruler** is a reasonable first cut at lead 6, but it isn't conservative (F2, F4). It ignores unequal cluster sizes, and at longer leads it splits forecast seasons across clusters.
- **The headline.** Mead's lead-6 BELOW is robust. Powell's isn't.
- **"34 of 96 against about 5 by chance"** isn't fair as worded (F1). Mead's 20 band cells are close to one finding seen 20 times. The cutoff assumes independence the page itself says is absent, and half of "every stated figure" isn't stated by anyone.

### 5. Live panel, checked against RISE and HDB now

| Lake | Value | Matches |
|---|---|---|
| Lake Mead | 1039.66 ft end of day on 8 Nov (RISE item 6123 equals HDB) | Feed |
| Lake Mead | 1-day +0.11, 7-day +0.73, 30-day +2.06 | RISE |
| Lake Mead | Largest rises +0.49 / +0.81 / +1.44 ft, from 23 Oct | RISE |
| Lake Mead | Hourly 1039.84 at 18:00 on 9 Nov | Fresh HDB |
| Lake Powell | 3538.84 ft on 8 Nov (RISE item 508) | Feed |
| Lake Powell | 1-day +0.28, 7-day +6.42, 30-day +19.87 | RISE |
| Lake Powell | Largest rises +1.83 / +3.24 / +9.32 ft | RISE |
| Lake Powell | Hourly 3538.84 at 23:00 on 8 Nov (HDB Powell hourly lags a day) | Fresh HDB |

- **Threshold arithmetic** checks out on all 10 elevations.
- **Other reservoirs** match the Lower Colorado JSON for 8 Nov and CDEC as of 11/08/2026:

  | Reservoir | Storage, af | Stated capacity, af |
  |---|---|---|
  | Shasta | 2,250,016 | 4,552,000 |
  | Oroville | 1,446,531 | 3,424,753 |

- **Capacity labels** match the Lower Colorado report text. "AVAILABLE CAPACITY IN A.F. *26120000 1873648 570253" with the footnote "* BOTTOM OF EXCLUSIVE FLOOD CONTROL SPACE", and "MAX. STORAGE 23314000 AF | ... 3749000 ... 1696000 ... 827472".
- **Quotes**: see F9.

### 6. Copy

| Rule | Result |
|---|---|
| Semicolons in page or rendered strings | None |
| Adjectives | None beyond factual superlatives (largest, lowest, latest) |
| Cause named | None. Quotes inside quotation marks only |
| Post-hoc labels | Band width is labelled "defined after the data" and the notable-row selection "not in the plan". The live-panel extras aren't (N3) |
| Intervals say what they are | Yes in the table and note. No interval in the headline (N6) |
| Figures say where they live | Not for the "full record" or the headline (F8) |
| Page numbers match the data | Yes: 42 of 83, 49 of 82, about 66, 530, 86, 15,202, 124. Powell's 49 of 82 matches the data, but the data misses one readable row (F3). The builder-summary figures in F10 are the ones that are wrong |

## How to reproduce

All scripts are in /private/tmp/claude-501/-Users-heuremen/b41d2241-cc55-49dd-8b48-5ec14786a97e/scratchpad/ref/scripts/:

| Script | What it does |
|---|---|
| stage1.py | Catalog and run IDs |
| stage2.py | Fresh HDB runs |
| stage3.py | Independent print read by lead |
| scan80.py | The 80 percent sentence across all 530 PDFs |
| quotes.py | Governing-document quotes against fresh PDFs |
| textrows.py, pagelines.py, cliprow.py | Row text and page-image crops |

Outputs (stage1.json, stage2_hdb.json, stage3_lead6.json, scan80.json, mine_lead6.json, fresh/, img/) are in the folder above.
