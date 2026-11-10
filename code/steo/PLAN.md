# STEO: stated 95 percent price intervals against the monthly spot price. Plan, written before any stated interval was set beside a spot price.

## Claim read
Each monthly Short-Term Energy Outlook (STEO) from the U.S. Energy Information Administration (EIA) shows a chart of the West Texas Intermediate (WTI) crude oil price and one of the Henry Hub natural gas price, each with a "95% NYMEX futures price confidence interval upper bound" and "lower bound". The chart note says: "Confidence interval derived from options market information for the five trading days ending" a stated date, and "Intervals not calculated for months with sparse trading in near-the-money options contracts." The January 2012 STEO describes the bounds as "the lower and upper limits of a 95-percent confidence interval for the market's expectations of monthly average WTI prices". The October 2025 STEO says: "We have temporarily suspended our publication of confidence intervals."

The numbers behind each chart are in the STEO chart gallery workbook (chart-gallery.xlsx, before that chart-gallery.xls), on the WTI sheet and the Henry Hub sheet, in the columns headed "Confidence Interval", "Lower" and "Upper" by month, with the level in a cell that reads 0.95. EIA serves only the current workbook. Earlier workbooks are read from Internet Archive copies made at the time.

Question: how often does the monthly average spot price land inside the 95 percent interval EIA stated for that month in an earlier STEO, by how many months ahead the interval was stated?

## Data
Stated side. Every Internet Archive copy of chart-gallery.xlsx or chart-gallery.xls under eia.gov/outlooks/steo/xls/ or eia.gov/forecasts/steo/xls/ with status 200, read through the Wayback index and raw-copy addresses, paced. Copies with the same bytes are read once. The STEO issue of a copy is fixed by the date in its chart note ("five trading days ending" a date): the issue is the first STEO release after that date, from the release table on eia.gov/outlooks/steo/outlook.php. The statement time is that issue's release date.

Delivered side. EIA monthly average spot prices: WTI Cushing (series RWTC, dnav/pet/hist_xls/RWTCm.xls, dollars per barrel) and Henry Hub (series RNGWHHD, dnav/ng/hist_xls/RNGWHHDm.xls, dollars per million Btu), read at run time and kept with the date read.

All sources are public. EIA: "U.S. government publications are in the public domain". The intervals use CME Group, Bloomberg and Refinitiv inputs, credited as EIA credits them. No key is used.

## Frame (fixed now)
- Series: WTI and Henry Hub. No other series.
- Issues: every issue with at least one used copy. No issue is picked by us.
- A row is one issue, one series and one month m with a numeric Lower and Upper. A row counts as a projection only if m begins after the issue's release date. Months that had begun at release are listed and not scored.
- Lead is m minus the release month, in months (1 is the month after release).
- When copies of one issue disagree on a value, the earliest copy is used and the disagreement is counted and shown.
- A row is scored once EIA's monthly spot value for m exists. Until then it reads NOTHING_RETURNED, counted apart.

## Rules (fixed now)
Row outcome:
- CONSISTENT: Lower <= spot <= Upper.
- ABOVE: spot above Upper.
- BELOW: spot below Lower.
- CANNOT_TELL, each reason counted apart: unreadable (a value not a number, Lower above Upper, or the level cell of the sheet not 0.95), issue unknown (no note date, or no release after it, or the copy was made before the release it maps to).
Values are compared as served, no tolerance.

Cell share: CONSISTENT rows over CONSISTENT, ABOVE and BELOW. Above and below are printed apart. CANNOT_TELL and NOTHING_RETURNED are shown beside every cell.

Interval. Rows are not independent: one outcome month is scored by many issues, and prices in neighbouring months move together. The interval is a moving-block bootstrap over outcome months: the outcome months of all scored rows of the series are sorted, blocks are 12 consecutive months in that list, a replicate draws ceil(W/12) block starts with replacement, and every row of the cell whose outcome month is in a drawn block enters with that multiplicity. 2,000 replicates, seed 20261110. 95 percent interval from the 2.5th and 97.5th percentiles. The page says so.

Cell outcome against 0.95:
- CANNOT_TELL if fewer than 30 scored rows or fewer than 24 distinct outcome months.
- BELOW if the upper bound is under 0.95. ABOVE if the lower bound is over 0.95.
- CONSISTENT if 0.95 is inside an interval no wider than 0.15.
- Otherwise CANNOT_TELL.

Cells, for each series: all leads (the headline cell is WTI, all leads), leads 1 to 2, 3 to 6, 7 to 12 and 13 or more months.

## Both alternatives
A. The stated intervals hold the monthly spot price about 95 percent of the time. Cells read CONSISTENT or CANNOT_TELL with 0.95 inside.
B. They hold it less often (BELOW) or more often (ABOVE).
Either result is printed the same way, with no cause named.

## Known-good gates (a failed gate turns every outcome into CANNOT_TELL)
1. Format. Every used copy has a WTI sheet and a Henry Hub sheet with a month column and Lower and Upper columns under a "Confidence Interval" heading.
2. Reader. Three stated values read directly from the raw sheet XML (or the raw cells of an .xls) of three copies equal the parsed values, written into data/known_good_rows.json before the first comparison.
3. Issue map. For every used copy, the note date is before the release date it maps to, and that release date is on or before the copy's capture date.
4. Same quantity. Each copy's "Historical Price" column, for months before its release, agrees with EIA's current monthly spot series within 2 percent in at least 90 percent of those months, for each series. Only months before the release are read. This checks that the stated side and the delivered side are the same price series.
5. Rule. Synthetic rows read ABOVE, BELOW, CONSISTENT and each CANNOT_TELL reason correctly, planted worlds read CONSISTENT and BELOW in the bootstrap cell rule, and heuremen_kit's self-test passes.

## Described and not scored
Shares above and below the interval. The interval width as a share of the futures settle price by lead. Months where EIA stated no interval for sparse trading.

## Set aside
Issues with no archived workbook (their charts exist only in the PDF and would need reading off the drawing). The STEO's own point forecast. Brent, retail prices and every other series. The probability workbooks (Probability_WTI.xlsx, Probability_HH.xlsx). Issues from October 2025 on (no interval published).

## Reading done before this plan was written
An outside scout read the archive index, the release schedule, the copyright page, the text of sampled PDFs (chart titles, notes and a few quoted bounds in Jan 2012 and Jun 2016 text) and found no interval series in the archived _base.xlsx workbooks. We then read the Wayback index of the chart gallery workbooks, opened one copy (captured 11 January 2023) to find the interval columns and their headers and the first rows of its Henry Hub sheet (history months of 2018), and for the copies already downloaded listed the sheet names, the series names, the note date and the level cell. The spot price files were downloaded and not opened by us. The scout saw the first value of EIA's WTI history page (January 1986). No stated interval was set beside a spot price.

## Addendum 1 (10 Nov 2026, decided after the data): the level from the chart legend
The workbooks from the June 2020 issue on carry the Lower and Upper columns without the level cell (the earlier workbooks hold the settle price, the implied volatility, the days to expiry and a cell that reads 0.95, and compute the bounds from them). Under the rule above every row of those issues reads CANNOT_TELL, reason unreadable. That was seen on the first full run, after the outcomes of the other rows had been computed.

The STEO PDF of the same issue labels the same bounds "95% NYMEX futures price confidence interval upper bound" and "lower bound" on the chart page for each series. A second reading takes the level as 0.95 for a sheet with no level cell when the issue's PDF has a page whose text holds "95% NYMEX", the word confidence, and the series name (West Texas Intermediate or WTI, or Henry Hub). Every other rule, cell and threshold is unchanged.

The reading in "Rules" above stays the primary reading and the headline cell. The second reading is shown beside it on the page and in the feed, labelled as decided after the data.
