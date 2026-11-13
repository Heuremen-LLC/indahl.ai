# CENSUS VINTAGES: July 1 population estimates as stated in earlier Vintages, set beside later Vintages and the 2020 Census count. Plan, written before any outcome was computed by this desk.

This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.

## Claim read
Each December the Census Bureau publishes a Vintage of population estimates. A Vintage restates the July 1 estimate of every state for every year it covers, so an earlier Vintage is a stated figure and a later Vintage is a delivered one. The Census Bureau publishes no width with any estimate. The only published width on the population of 2020 is the standard error of the Post-Enumeration Survey (PES) net coverage error for each state, which the CENSUS COVERAGE desk already holds (census_coverage/summary_coverage.json, dataset 2020/dec/pes, group G_STATES).

Question: for each state, where does a later value of the same population sit against the figure an earlier Vintage stated, and where a width exists, against that figure with its width.

Nothing on this desk says an estimate is wrong. A Vintage is allowed to restate its past. A reading says only where the later value sits.

## Disclosure of what was seen before the plan
The scout (census_scout/SCOUT.md, 11 Nov 2026) printed California, Texas and Arkansas: V2019 July 2019, V2020 April 1 and July 1 2020, the 2020 Census count, July 2020 and July 2022 in V2022 to V2025, and ESTIMATESBASE2020 in V2022, V2024 and V2025. Those three states are in the frame and are not dropped. While preparing this plan the raw files were copied and their column headers and the first rows of the two API pulls were printed (Alabama in 2019/pep/population, five states in 2021/pep/population, Alabama census count). No difference between Vintages, no outcome and no count had been computed. What was looked at is logged in CHECKS.md.

## Frame (fixed now)
Areas: the 50 states and the District of Columbia (51 areas, names as in summary_coverage.json). Puerto Rico, regions and the nation are not in the frame. Date: July 1 estimates, plus the April 1 2020 estimate of V2020 where stated below.

Vintages and what they hold (state level).
- V2019: July 1 2010 to 2019, built on the 2010 Census base. File nst-est2019-alldata.csv, cross-checked against api 2019/pep/population (DATE_CODE 3 to 12 is July 2010 to 2019).
- V2020: July 1 2010 to 2020 and an April 1 2020 estimate, 2010 Census base. File nst-est2020.csv.
- V2021: July 1 2020 and 2021, 2020 Census base. api 2021/pep/population (fields POP_2020, POP_2021). The flat file was not found at the paths tried, so this Vintage has no flat-file cross-check and no estimates base field.
- V2022 to V2025: July 1 2020 to the last year of each Vintage, 2020 Census base, and ESTIMATESBASE2020. Files NST-EST2022 to NST-EST2025-ALLDATA.csv.
- 2020 Census count: api 2020/dec/pl P1_001N, the resident population of 1 April 2020 (data/raw/census2020_pl_state.json).

A row is one area, one stated figure and one later value. The classes are separate cells and are never pooled, and every row of every class gets an outcome and none is dropped.
- Class A, SAME BASE: stated is the July 1 estimate of year Y in Vintage Va, later is the July 1 estimate of the same year Y in a later Vintage Vb, where Va and Vb sit on the same census base (V2019 and V2020 on 2010. V2021 to V2025 on 2020). Every pair Va earlier than Vb that both hold year Y. One cell per pair Va to Vb.
- Class B, ACROSS BASE: stated is the July 1 2020 estimate of V2020 (2010 base), later is the July 1 2020 estimate in V2021, V2022, V2023, V2024 and V2025 (2020 base). One cell per later Vintage. 51 rows each.
- Class C, APRIL 1 2020 ESTIMATE AGAINST THE COUNT: stated is the April 1 2020 estimate in V2020, later is the 2020 Census count. One cell, 51 rows.
- Class D, THE COUNT AGAINST LATER BASES: stated is the 2020 Census count, later is ESTIMATESBASE2020 in V2022, V2023, V2024 and V2025. One cell per Vintage. 51 rows each.
Set aside: July 1 estimates against the census count (the dates differ), counties, metro areas, age, sex and race detail, Puerto Rico, V2021 and earlier Vintages than V2019, projections, and any cause for a restatement.

## Width source (fixed now, nothing is derived from outcomes)
A cell gets a width only where Census publishes one. That is the PES standard error of the 2020 net coverage error, which applies to the level of the 2020 population. The PES standard error is a published figure in percent, SE_a for area a. For classes B, C and D the half-width of the interval is
h = 1.645 x SE_a / 100 x anchor
where the anchor is the stated figure (class B and C, the stated estimate. Class D, the census count). The multiplier 1.645 is the two sided 90 percent normal multiplier and is the same as the CENSUS COVERAGE desk uses (Census states its PES comparisons at the 90 percent level, PES20-G-02RV). The interval is [anchor - h, anchor + h], edges included, values as published, no tolerance. This is a yardstick for how precisely the 2020 population level is known. It is not a published width of any estimate, and the page says so. The PES covers the household population and the anchor here is a resident figure, so the yardstick is applied as a relative width and that is named as our step.
Class A has no width. The PES standard error is about the level of a census, and two Vintages on one base share that level error, so it does not bound a restatement between them. No spread across Vintages is used as a width, because the spread is the thing being read and would make every row read inside by construction. So every class A row is CANNOT_TELL with reason no width. This is written now and is the expected result for class A. The class A rows are described and not scored (below).
A missing width never gets filled in. A PES standard error that is missing, zero or below is CANNOT_TELL with reason no PES width.

## Rules (fixed now)
Outcome per row, from the stated anchor, later value and half-width:
- CONSISTENT: the later value is inside the interval, edges included.
- ABOVE: the later value is over the upper end. BELOW: the later value is under the lower end.
- CANNOT_TELL, each reason counted apart: no width (class A), no PES width, no stated value or no later value (a blank or absent figure).
Cells (class, Vintage pair or later Vintage) show the four counts and nothing else is scored. No share of rows is read against 90 percent, because the interval is a yardstick and not a stated coverage of the later value. No chance floor is claimed, because a yardstick has no null world. CANNOT_TELL is shown beside every cell as its own count and is never folded into CONSISTENT or into a share.

Described and not scored: for each cell the median absolute change of the later value against the stated value as a percent of the stated value, the median signed change, and the median of the absolute change in units of the area's yardstick half-width. For class A the half-width is computed the same way from the area's PES standard error and the stated value and is named a yardstick unit and not a width. The largest single restatement of each cell is named. Sensitivity of classes B, C and D to the multiplier is shown at 1.0 and 2.0 times the standard error (the counts only), and the 1.645 reading is the one that counts.

## Both alternatives
A. Later values sit inside the yardstick interval of the stated figure. The cell reads mostly CONSISTENT. A CONSISTENT row says the later value is within what the survey of the 2020 count could separate. It does not say the estimate is right.
B. Later values leave the interval. The cell reads ABOVE or BELOW rows, printed apart and never netted. A reading names no cause.

## Known-good gates (a failed gate turns every outcome into CANNOT_TELL)
1. Format and frame. Each file has the expected population columns, 51 areas by name in every Vintage, and every needed field is present for every area.
2. Reader and join. The V2019 July values from the API (DATE_CODE 3 to 12) equal the flat file for all 51 areas and 10 years. The 51 census counts add to 331,449,281, the resident population of the 50 states and the District of Columbia published for 2020. Hand-read values for California, Texas and Arkansas from the scout table (V2019 July 2019, V2020 April 1 and July 1 2020, census count, V2022 to V2025 July 2020) equal the parsed values.
3. Width. The 51 PES standard errors are read from census_coverage/summary_coverage.json, are all positive, and equal the standard errors served by the API (dataset 2020/dec/pes G_STATES) for all 51 areas.
4. Rule. Synthetic rows with a known answer read ABOVE, BELOW, CONSISTENT and each CANNOT_TELL reason correctly, and the heuremen_kit self-test passes.

## Set aside
Every other CENSUS desk, any estimate of future Vintages, Vintage 2026 and later (it lands in December and the desk is not a recurring one), anything about why a Vintage restated.
