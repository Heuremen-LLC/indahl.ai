# Census desk scout (11 Nov 2026)

Scope: research only. Nothing built, no site edits. Raw pulls and helper scripts are in this folder (cget.sh reads the key at call time and never prints or stores it; pull_econ.py, pull_bfs.py, pull_pep.py, pull_saipe.py reproduce the numbers below; raw/ holds the pulls). Outcomes are not labelled anywhere in this file. Numbers are shown stated beside delivered with widths where a width exists.

## Ranked list (best desk first)

1. NEW RESIDENTIAL SALES, advance print vs revised print, 90% width published (Census EITS ressales plus ALFRED first prints). A figure stated before the delivered one exists, revised twice then annually, with sampling error published, many months, four regions. June 2025 first print 627, second 656, current 665.
2. HOUSING STARTS (and permits, completions), same design (EITS resconst plus ALFRED HOUST). June 2025 first print 1,321, second 1,358, current 1,379, with a published sampling error. Slightly lower than sales only because revisions are smaller relative to the width.
3. ADVANCE RETAIL SALES (MARTS) vs preliminary and later revised (EITS marts plus ALFRED RSAFS). Standard error of the percent change is in the API and the 90% rule is documented (1.753 x SE). Ranks third because the April 2025 annual revision changed the universe (nonemployers removed), so first prints before and after are not like-for-like. Advance vs preliminary within one universe is clean.
4. 2020 CENSUS vs POST-ENUMERATION SURVEY, 51 states and DC, stated net coverage error with a standard error, two independent official counts of the same people (dec/pes G_STATES). Best "two independent measurements with a width" in Census. One-time (no refresh), so it is a fixed 51-row desk, not a recurring one.
5. POPULATION ESTIMATE VINTAGES, July 1 estimate for the same state or county and year across Vintages 2019 to 2025, then vs the 2020 Census count. Fully retrievable history, thousands of rows, but no published width on any estimate (use the PES standard error for the census side, or the inter-vintage spread). Needs a CANNOT_TELL rule for the missing width.
6. NATIONAL POPULATION PROJECTIONS (2017 and 2023 series) vs later estimates. Stated figure well before delivered, with a stated scenario band in the 2023 series (high, low, zero immigration), but it is a scenario band and not a statistical interval, and the row count is small (one national total per year, plus age, sex, race cells).
7. BUSINESS FORMATION STATISTICS, projected formations within 4 and 8 quarters vs realized (EITS bfs). 222 months with both values (2004-07 to 2022-12), a stated projection and a realized figure, but no width, we do not know that the projection column is frozen at first publication, and the realized column stops at 2022-12 in the API.
8. SAIPE vs ACS 1-year poverty, SAHIE vs ACS uninsured, both with 90% bounds and about 800 to 3,100 counties. Not independent (SAIPE and SAHIE use ACS as an input), so overlap is expected by construction. Useful as a model-vs-direct-survey desk, weak as a stated-vs-delivered one.
9. Untested: ACS SNAP households vs USDA administrative counts, ACS veterans vs VA VetPop, ACS enrolment vs NCES. These are cross-agency definition fights. Not pulled.

Best single recommendation: one ECONOMIC INDICATOR REVISIONS desk built from items 1 to 3 with a shared reading rule, because the "stated" figure and the width are published by Census and the history can be rebuilt from ALFRED today. Item 4 is a cheap second desk that can ship from a static file.

## Access, keys, terms (all candidates)

- API base https://api.census.gov/data/. The key works (tested). Keyless use is limited to about 500 calls a day per IP according to Census documentation (from Census docs as I know them, not re-verified here). With the key there is no stated cap. All pulls above were a few dozen calls, no loops.
- Census data is a US government work. The Census API Terms of Service (checked at census.gov/data/developers/about/terms-of-service.html) say: use is allowed to build services that analyze and display the data, you may not use the Census Bureau name to imply endorsement, you may not modify content and still claim it as Census content, and the Bureau may limit or block access that exceeds or circumvents limits. Practical consequence: add the standard line "uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau" and keep our readings clearly ours.
- ALFRED (St. Louis Fed) keyless CSV endpoint works: https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=SERIES&vintage_date=YYYY-MM-DD&cosd=YYYY-MM-DD&coed=YYYY-MM-DD . One vintage date per call returns the series as known on that date (a comma list returned only the first vintage in my test). The official vintage list needs the FRED API (free key). Vintages reach back to roughly 1996 for housing starts and 2003 for retail sales in my spot checks. Cite the St. Louis Fed and Census as sources. I did not check ALFRED's terms page beyond the public CSV working; read it before scheduling pulls.
- Flat files for population estimates and projections live at www2.census.gov/programs-surveys/popest and /popproj and need no key.

## 1. New residential sales (EITS ressales; ALFRED HSN1F)

- Stated: advance estimate of new single-family houses sold, SAAR, thousands (Census and HUD, released about the 17th business day). Delivered: the same month as revised the next two months, then in annual revision, current value from the API.
- Endpoint: timeseries/eits/ressales with category_code=ASOLD (SAAR), data_type_code=TOTAL, geo_level_code=US/NO/MW/SO/WE, seasonally_adj=yes, time_slot_id=0, error_data=no for values and error_data=yes for E_TOTAL. First prints: ALFRED series HSN1F.
- Width: E_TOTAL is returned for each cell (US, four regions). Values here are whole numbers (9, 10, 11 for US) and look like percent standard errors or coefficients of variation. The MARTS page documents 90% = 1.753 x standard error. The meaning of E_ for ressales must be confirmed against the Census release notes before any desk uses it. The monthly release also prints a 90% interval on the percent change, which is in the PDF release table, not in the API.
- First-print history: retrievable from ALFRED. EITS holds only the current vintage, so snapshot EITS every release from now on to keep widths as printed.
- Side by side (US total, thousands, SAAR; width = API E_TOTAL as returned, in percent):

| Month | First print (vintage ~25th next month) | Second print | Current | E_TOTAL |
|---|---|---|---|---|
| 2024-12 | 664 | 698 | 702 | 11 |
| 2025-03 | 724 | 670 | 656 | 10 |
| 2025-06 | 627 | 656 | 665 | 9 |

- Like-for-like: ALFRED vintage dates are not the Census release dates (I used about the 25th of the next month as a stand-in, which falls after the advance print and before the second). Get exact release dates from the Census release calendar. Revised region values exist too. Annual revisions change seasonal factors for all earlier months at once.

## 2. Housing starts, permits, completions (EITS resconst; ALFRED HOUST)

- Stated: advance estimate of total privately-owned housing starts, SAAR, thousands. Delivered: revised next two months, then annually.
- Endpoint: timeseries/eits/resconst with category_code=ASTARTS (SAAR; also APERMITS, ACOMPLETIONS), data_type_code=TOTAL/SINGLE/MULTI, geo_level_code=US/NO/MW/SO/WE, seasonally_adj=yes in the get list and as a predicate (the call fails without it), time_slot_id=0. Latest month available in the API at the time of the pull was 2026-09.
- Width: E_TOTAL per cell, whole numbers (5 and 6 for US). Same unverified meaning as above. The release prints a 90% interval on the percent change from the prior month.
- Side by side (US total, thousands, SAAR):

| Month | First print | Second print | Current | E_TOTAL |
|---|---|---|---|---|
| 2024-12 | 1,499 | 1,515 | 1,494 | 6 |
| 2025-03 | 1,324 | 1,339 | 1,346 | 6 |
| 2025-06 | 1,321 | 1,358 | 1,379 | 5 |

- Like-for-like: starts are SAAR in thousands in ALFRED and the API (same units). Permits include a separate "authorized, not started" series. The single-family only series has its own widths.

## 3. Advance monthly retail trade, MARTS (EITS marts; ALFRED RSAFS)

- Stated: advance estimate for retail and food services (category 44X72, SM data type, millions of dollars, SAAR sense: the seasonally adjusted series), released about 10 business days after month end. Delivered: preliminary estimate from the Monthly Retail Trade Survey one month later, then revised again, then annual benchmark.
- Width: MARTS documentation (census.gov/retail/marts/how_surveys_are_collected.html) states the margin of sampling error is a 90 percent interval and equals 1.753 x standard error; for monthly totals the median coefficient of variation is given and the interval is value +/- 1.753 x CV x value. API: data_type_code E_SM is the CV of the level in percent, E_MPCSM is the standard error of the month-to-month percent change in points. About 40 industry categories (441, 442, 443 and so on).
- Side by side (44X72 seasonally adjusted, millions of dollars):

| Month | First print (ALFRED vintage ~20th, month+1) | Second print (vintage ~20th, month+2) | Current (API) | E_SM (CV %) | E_MPCSM (points) |
|---|---|---|---|---|---|
| 2024-12 | 729,191 | 730,300 | 691,794 | 0.8 | 0.2 |
| 2025-03 | 734,870 | 723,714 | 694,750 | 0.9 | 0.1 |
| 2025-06 | 720,106 | 722,571 | 691,883 | 0.9 | 0.1 |

- Like-for-like problem, large: the April 2025 annual revision report removed nonemployer firms from the time series (documented on the MARTS page). The gap between the first print and current for every month in the table is mostly that universe change, not sampling error. A desk must compare advance with preliminary (same universe), or compare month-over-month percent changes, and must mark the benchmark break. The widths above are as returned now, not as printed at the time.

## 4. 2020 Census vs Post-Enumeration Survey, states (dec/pes, group G_STATES)

- Stated: the 2020 Census count. Delivered or independent: the PES (dual-system estimate from an independent sample). Net coverage error is the percent difference with a standard error. The estimate covers the household population (group quarters excluded), so the census count it uses is smaller than the total in dec/pl.
- Endpoint: https://api.census.gov/data/2020/dec/pes?get=NAME,group(G_STATES)&for=state:* . Fields: G_STATES_001 census count (rounded to thousand), _002 net coverage error percent, _003 standard error percent. 51 rows plus Puerto Rico in group A_TOTPR. Also national by race, age, sex, tenure, and housing units by state (HG_STATES, HH_STATES). Saved: raw/pes_g_states.json.
- Width: standard error in percent. A 90% interval is NCE +/- 1.645 x SE (Census states PES estimates are significant at the 90% level).
- Sign convention to confirm in the Census release: negative net coverage error is an undercount (the published headline of -5.04 for Arkansas is described as an undercount).
- Side by side:

| State | Total 2020 Census count (dec/pl) | PES household census count | NCE % | SE % |
|---|---|---|---|---|
| California | 39,538,223 | 38,620,000 | +0.47 | 0.65 |
| Texas | 29,145,505 | 28,540,000 | -1.92 | 0.82 |
| Arkansas | 3,011,524 | 2,929,000 | -5.04 | 2.21 |

- The Demographic Analysis (the other official coverage measure) is national only and is not in the API, so state comparisons are PES only. Refresh: none, it is a finished 2020 product (a 2030 version follows in the 2030s).

## 5. Population estimate vintages (flat files; also api 2019/pep/population and 2021/pep/population)

- Stated: the Census Bureau's estimate of a state or county July 1 population as published in a given Vintage. Delivered: the same year's estimate in later Vintages, and the April 1, 2020 Census count.
- Files (keyless): nst-est2019-alldata.csv, nst-est2020.csv, NST-EST2022/2023/2024/2025-ALLDATA.csv under www2.census.gov/programs-surveys/popest/datasets/ (county files in the same tree). Each Vintage is its own file, so first-print values are retrievable for every vintage ever released. The API only has vintages 2019 and 2021 (and older); 2022 onward are files only. A new Vintage lands each December (state) and March to June (county).
- Width: none published for the estimates. Vintage-to-vintage revisions are the only spread available. The PES SE (item 4) gives a width for the census side.
- Side by side (July 1 values unless marked):

| State | V2019 Jul 2019 | V2020 Apr 1 2020 | V2020 Jul 2020 | 2020 Census | Jul 2020 in V2022 / V2023 / V2024 / V2025 | Jul 2022 in V2022 / V2023 / V2024 / V2025 |
|---|---|---|---|---|---|---|
| California | 39,512,223 | 39,418,894 | 39,368,078 | 39,538,223 | 39,501,653 / 39,503,200 / 39,521,958 / 39,527,808 | 39,029,342 / 39,040,616 / 39,142,414 / 39,125,347 |
| Texas | 28,995,881 | 29,286,467 | 29,360,759 | 29,145,505 | 29,232,474 / 29,234,361 / 29,239,570 / 29,237,895 | 30,029,572 / 30,029,848 / 30,113,488 / 30,118,002 |
| Arkansas | 3,017,804 | 3,029,672 | 3,030,522 | 3,011,524 | 3,014,195 / 3,014,348 / 3,014,546 / 3,014,399 | 3,045,637 / 3,046,404 / 3,047,704 / 3,047,429 |

- Like-for-like: Vintages 2019 and 2020 are built on the 2010 Census base, Vintage 2021 onward on the 2020 Census base (Vintage 2021 and later restate 2020 to the new base), so compare V2019 and V2020 only with the census count and with each other, and compare V2021 and later with each other. V2020 April 1 (a count-date estimate) lines up with the census date, July 1 does not. The estimates base for 2020 itself also moves a little between vintages (for example California 39,538,245 in V2022, 39,555,674 in V2024).

## 6. National population projections (flat files)

- Stated: 2017 National Population Projections (main series, 2016 to 2060) and 2023 National Population Projections (main, high, low and zero immigration, 2022 to 2100). Delivered: the Vintage 2025 national estimates.
- Files: popproj/datasets/2017/2017-popproj/np2017_d1.csv and datasets/2023/2023-popproj/np2023_d1_{mid,hi,low,zero}.csv (saved: raw/np2017_d1.csv, raw/np2023_d1_*.csv). The API dataset 2017/popproj/pop rejects most predicate combinations ("too many predicates"), so use the files.
- Width: the 2023 series gives scenario bounds, not a probability interval. The 2017 series has the main series in this file.
- Side by side (resident population, July 1 projection year vs Vintage 2025 estimate):

| Year | 2017 projection | 2023 projection mid (hi / low / zero) | Vintage 2025 estimate |
|---|---|---|---|
| 2020 | 332,639,102 | not available (series starts 2022) | 331,578,104 |
| 2023 | 339,665,118 | 334,906,305 (335,674,990 / 334,393,850 / 333,368,934) | 336,755,052 |
| 2025 | 344,234,377 | 338,016,259 (340,326,253 / 336,476,277 / 333,396,257) | 341,784,857 |

- Like-for-like: projection dates are July 1 resident population, matching the estimate series, but the 2017 series was built on a Vintage 2016 base and 2023 on Vintage 2022. Immigration surprises are the main driver and are what the scenarios are about. Few rows (national only; state projections are the 2005 series).

## 7. Business Formation Statistics (EITS bfs)

- Stated: BF_PBF4Q and BF_PBF8Q, projected number of business formations within 4 and 8 quarters of the application month. Delivered: BF_BF4Q and BF_BF8Q, formations that actually occurred (BF_SBF4Q is the spliced series that uses actual where it exists, else the projection).
- Endpoint: timeseries/eits/bfs?get=cell_value,data_type_code&for=us:*&time=from+2004-07&category_code=TOTAL&seasonally_adj=no&time_slot_id=0&error_data=no (the time variable cannot be in the get list for range queries). National and about a dozen industry categories only; the state BFS tables are CSV downloads on census.gov, not in this API (my guessed URL returned a 404, not located).
- Width: none published.
- Side by side (US total, not seasonally adjusted):

| Application month | Projected within 4Q | Realized within 4Q | Projected within 8Q | Realized within 8Q | Business applications (BA_BA) |
|---|---|---|---|---|---|
| 2019-03 | 22,105 | 25,277 | 28,822 | 31,030 | 327,817 |
| 2021-03 | 34,123 | 34,238 | 45,603 | 42,781 | 612,494 |
| 2022-12 | 20201 | 19815 | 26311 | n/a | 295553 | (last month with both 4Q)

- Problems: a projection column that is overwritten each release is not a first-print projection, and nothing says otherwise; we would have to snapshot from now on. The realized column is absent from 2023-01 on in the API (months 2023-03, 2024-09, 2025-06 return no BF_BF4Q), so the realized side lags more than four quarters. Whether the projection published at the time matches today's column needs a check against an archived release.

## 8. SAIPE and SAHIE vs ACS (model vs direct survey)

- SAIPE (timeseries/poverty/saipe) gives point and 90% bounds (SAEPOVRTALL_PT, _LB90, _UB90; counts SAEPOVALL_*) for states and counties, 1989 on, annual. ACS 1-year subject table S1701 gives the same concept with a 90% margin of error (S1701_C03_001E and _M), counties of 65,000 or more. SAHIE (timeseries/healthins/sahie) gives PCTUI_PT, _LB90, _UB90, by age, sex, race, income, years 2008 on.
- Side by side, 2023 poverty rate, all ages, percent (SAIPE point, SAIPE 90% bounds; ACS 1-year estimate, ACS 90% margin):

| Place | SAIPE | SAIPE 90% bounds | ACS 1-year | ACS MOE90 |
|---|---|---|---|---|
| California | 12.0 | 11.9 to 12.1 | 12.0 | 0.2 |
| Arkansas | 15.4 | 15.0 to 15.8 | 15.7 | 0.6 |
| Harris County TX | 16.0 | 15.4 to 16.6 | 16.0 | 0.6 |

- Problem: SAIPE uses the ACS 1-year estimate as a model input, so the two are not independent measurements, and the SAIPE intervals are for the model not for the delivered value. SAHIE has the same structure (ACS plus administrative records). I pulled one SAHIE row only to confirm bounds exist (California 2022, uninsured under 65, 7.5, bounds 7.4 to 7.6).

## Dead ends and not checked

- No published first-print vintages inside Census. EITS and the population API give current values only. Snapshot each release from now on (a rider on a release-day schedule), and use ALFRED for history.
- Vintage 2022 onward are not in the API as pep/population (404). Use flat files.
- 2017 popproj API predicates are broken for multi-filter queries, files work.
- Not examined: ACS vs USDA SNAP, VA VetPop, NCES; durable goods advance M3 (EITS advm3, requires for=us:*) and construction spending (ALFRED TTLCONS, EITS vip), both follow the same advance-vs-revised pattern as items 1 to 3 and would join that desk; international trade (FT-900) advance goods vs revised, same pattern; Quarterly Services Survey; Quarterly Financial Report. ALFRED spot checks returned values for DGORDER (vintage 2025-07-20 and a 2005 vintage) and TTLCONS, confirming first prints are retrievable.
- Meaning of the E_ values for ressales and resconst needs one confirming read of the Census technical notes before any width is used on a page.
