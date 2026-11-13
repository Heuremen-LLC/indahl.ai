# CENSUS: stated first prints against the later record, economic indicators. Plan, written before any first print was set beside a later value by this desk.

This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.

## Claim read
The Census Bureau publishes advance monthly estimates of new residential sales, new residential construction (starts, permits, completions) and retail and food services sales. Each is a sample estimate and is published with a sampling error. Each month is then revised: sales three times, starts and completions twice, retail by a preliminary estimate and later revisions, and all of them again in annual revisions.

Question: how often does a later value of the same month sit inside the 90 percent interval that Census states for the first print, by series, geography and revision step.

What the width means is pinned in CHECKS.md (section "What the error fields are") from the Census documents, quoted with URLs. In short:
- New residential sales and new residential construction: the API fields E_TOTAL (and E_SINGLE, E_MULTI) are the estimated relative standard error in percent, rounded to a whole number. The release calls it "Average relative standard error for the latest 6-month period". The 90 percent confidence interval multiplier is 1.645 (Census SOC methodology page).
- Advance monthly retail: E_SM is the coefficient of variation of the monthly level in percent (one decimal). Census states the 90 percent interval is "the estimated value +/-1.753 x CV x (the estimated monthly total)".
So the stated 90 percent half-width of a first print p is 1.645 x RSE/100 x p for housing and 1.753 x CV/100 x p for retail.
Census states 90 percent as the share of its intervals that would hold the value a complete enumeration gives. A later revised estimate is not that value. Reading the share of later values inside the interval against 90 percent is our reading, named as ours wherever it is printed.

## Disclosure of what was seen before the plan
The scout (census_scout/SCOUT.md, 11 Nov 2026) printed three months, 2024-12, 2025-03 and 2025-06, for first, second and current values of the US total in each series. Those months are in the frame and are not dropped. No other first-versus-later comparison had been made. The ALFRED pulls had started and were not read.

## Data
Stated side. ALFRED (St. Louis Fed, keyless) holds the series as known on each vintage date. Series: HSN1F (new one-family houses sold, thousands, SAAR) with HSN1FNE, HSN1FMW, HSN1FS, HSN1FW, HOUST (total housing starts, thousands, SAAR) with HOUSTNE, HOUSTMW, HOUSTS, HOUSTW, PERMIT (total permits), COMPUTSA (completions), RSAFS (retail and food services, millions of dollars, seasonally adjusted). One call per series and vintage date, paced, all cached. Vintages from 1 January 2016.
The first print of month M is the value of M in the earliest pulled vintage that holds M. A month already in the earliest pulled vintage has no known first print and is not a row.
Vintage dates are the dates ALFRED first recorded the values. They stand in for the Census release dates and can differ from them by a day or so. We say so on the page. No release calendar is used.
Print 2 (S1) of M is the value of M in the vintage where M+1 first appears. Print 3 (S2) is the value of M in the vintage where M+2 first appears. Current (S3) is the value in the newest vintage pulled. These are separate cells and are never merged.

Width side. ALFRED gives values and no widths. EITS (api.census.gov, key) serves the current vintage only. Our own dated copies start on 11 Nov 2026 (data/snapshots), and from then each first print can be read with its width as printed. Until a month has a copy made on its release day, its width is the one EITS serves now for that month, read from our earliest copy. That width is not as printed. Every row carries width_basis: "as printed" (a copy made within 3 days after the first print vintage date) or "as served 2026" (all history). The two bases are separate cells and are never merged. No width is estimated or filled in. A month with no served width is CANNOT_TELL with reason no width.
Width fields used (seasonally adjusted): sales ASOLD E_TOTAL for geographies US, NO, MW, SO, WE. Starts ASTARTS E_TOTAL, same geographies. Completions ACOMPLETIONS E_TOTAL, US. Permits APERMITS has no error field, so every permits row is CANNOT_TELL with reason no width and is described only. Retail category 44X72 (total) E_SM, US.
The served RSE is a whole number, so the true value lies within half a point of it. This is shown as a sensitivity and does not enter the outcome.

## Frame (fixed now)
Row = (series, geography, month). Series: SALES (US and four regions), STARTS (US and four regions), COMPLETIONS (US), PERMITS (US), RETAIL (US). Geographies are separate cells. A region is never pooled with the US total. Steps S1, S2, S3 as above (RETAIL S2 too).

## Rules (fixed now)
Interval = [p1 - h, p1 + h], h as above from the first print p1 and the served width. Values compared as published, no tolerance.
Row outcome at each step:
- CONSISTENT: the later value is inside the interval (edges included).
- ABOVE: the later value is above the interval. BELOW: below it.
- CANNOT_TELL, each reason counted apart:
  - no width: no served width for that row.
  - universe break: RETAIL only. The retail break vintage is the earliest vintage where a month at least 14 months older than the newest month in the vintage changed by more than 3 percent against the previous vintage (the Census documents the April 2025 annual revision as removing nonemployer firms). A RETAIL row whose first print comes before the break vintage and whose later value is taken at or after it is CANNOT_TELL. This hits S3 for early rows and S1/S2 where the window crosses it.
  - annual revision in window: an annual-revision vintage lies between the first print vintage and the target vintage (S1, S2 only, all series). An annual-revision vintage is a vintage where any month at least 14 months older than the newest month changed against the previous vintage. S3 is the annual-revised value by design and is not dropped for this reason.
  - missing vintage: the vintage for the step does not exist or lacks the month (for example M+1 or M+2 has not yet been published).
Rows are counted by series, geography and step, and every row a rule drops is listed in the counts. Nothing is dropped silently.

Cells. A cell is series, geography, step and width basis. Its share is CONSISTENT over CONSISTENT, ABOVE and BELOW rows. CANNOT_TELL rows are shown beside every cell and are never folded into either side. The interval is a 95 percent Wilson interval. Cell outcome against the stated 90 percent: ABOVE if the lower bound is over 0.90, BELOW if the upper bound is under 0.90, CONSISTENT if the interval holds 0.90, CANNOT_TELL with fewer than 10 scored rows. Consecutive months of one series overlap in what they measure and regions sum to the US, so rows are not independent and the interval is narrower than a fully honest one. The page says so.
Headline cells: US total of SALES, STARTS, COMPLETIONS, RETAIL at S1, S2 and S3 with width basis "as served 2026".

Described and not scored: median absolute revision as a share of the first print, and in units of the stated half-width, by cell. Sensitivity of the share to the served RSE moved down and up half a point. Permits revisions. M3 durable goods, construction spending and international trade are copied by the snapshot job and not read here.

## Both alternatives
A. Later values sit inside the stated interval about 90 percent of the time or more. The cell reads CONSISTENT or ABOVE.
B. Later values leave the stated interval more often. The cell reads BELOW. Either result prints the same way. A BELOW cell says how often a later value left the interval and names no cause.

## Known-good gates (a failed gate turns every outcome into CANNOT_TELL)
1. Format. Every ALFRED file has the header observation_date and one value column named SERIES_YYYYMMDD with the vintage date asked for.
2. Reader. Hand-read rows (CHECKS.md) from the Census release text equal the parsed rows.
3. Join. The newest ALFRED vintage value of each US series for the latest month equals the EITS current value (to rounding), for at least 90 percent of the compared US months of the last 12.
4. Rule. Synthetic rows with a known answer read ABOVE, BELOW, CONSISTENT and each CANNOT_TELL reason correctly, and heuremen_kit's self-test passes.

## Set aside
Census population estimates, projections, PES, BFS, SAIPE and SAHIE, other desks. M3, VIP and trade: copied, not read. ACS comparisons. Any cause for a revision.
