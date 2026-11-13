# FLU: stated flu admission intervals against the reported count. Plan, written before any stated interval was set beside a reported count.

## Claim read
The CDC FluSight Forecast Hub (github.com/cdcepi/FluSight-forecast-hub) collects forecasts of weekly laboratory-confirmed influenza hospital admissions for the United States, the 50 states, Washington DC and Puerto Rico. Each week the hub publishes the FluSight-ensemble, "a median of quantile outputs" of the eligible submissions (model-metadata/FluSight-ensemble.yml). The ensemble is stated as 23 quantiles (0.01, 0.025, 0.05, 0.10 to 0.90 in steps of 0.05, 0.95, 0.975, 0.99) for each location, week and horizon. CDC's forecast page shows "prediction intervals, which indicate the bounds of uncertainty", and says these ensemble forecasts "have been among the most accurate for previous influenza forecasting efforts" (cdc.gov/flu-forecasting/data-vis/current-week.html, read 10 Nov 2026).

A quantile at level 0.025 and one at 0.975 state a central 95 percent prediction interval by construction. The quantiles at 0.25 and 0.75 state a central 50 percent interval. That is what the files say, and it is the claim tested here.

Question: how often does the reported weekly count fall inside the ensemble's stated 50 percent and 95 percent intervals, by horizon, season and location, and how does the ensemble's weighted interval score compare with the hub's own baseline model on the same rows?

## Data
All from the hub repository, MIT licence (the repository), the ensemble metadata names CC-BY-4.0. The target data come from CDC NHSN, a US government source. Read with git (sparse checkout of model-output/FluSight-ensemble, model-output/FluSight-baseline, target-data, hub-config, auxiliary-data/locations.csv, the two metadata files, README and LICENSE). The hub commit read is recorded on every run.

Stated side. model-output/FluSight-ensemble/<reference_date>-FluSight-ensemble.csv, target "wk inc flu hosp", output_type "quantile". Every file in the folder is used, from 2023-10-14 on.

Baseline (second ruler only). model-output/FluSight-baseline/<reference_date>-FluSight-baseline.csv, same target and quantiles.

Delivered side. target-data/time-series.csv, target "wk inc flu hosp". Each row carries as_of (the data release), target_end_date, location and observation. Two delivered values per stated row:
- Final: the observation in the latest as_of that holds the location and week at run time. This is the primary reading.
- First reported: the observation in the earliest as_of that holds the location and week, used only when that as_of is no more than 14 days after target_end_date. Otherwise the first-reported side of that row reads CANNOT_TELL, reason no early release. The hub notes that before 5 July 2025 as_of is the reference date of the release and after it the release date. The 14 day limit covers both.
Rows repeated inside one as_of with the same value are read once. Repeated rows with different values make that value unreadable.

## Frame (fixed now)
- Horizons 0, 1, 2 and 3 (week ending on the reference date and the three after). Horizon -1 (the week before the reference date) is listed and not scored, because its week can be reported before the forecast is due.
- Every location in an ensemble file. No location is picked by us.
- One row is one reference date, one location and one horizon. A row is scored on a delivered side once that side has a value. Until then that side reads NOTHING_RETURNED, counted apart from every outcome.
- Seasons by reference date: 2023-24 (to 2024-07-31), 2024-25 (to 2025-07-31), 2025-26 (to 2026-07-31), 2026-27 (after).

## Rules (fixed now)
Row outcome, for each stated interval (50 and 95) and each delivered side:
- CONSISTENT: lower quantile <= reported count <= upper quantile.
- ABOVE: the reported count is above the upper quantile.
- BELOW: the reported count is below the lower quantile.
- CANNOT_TELL, each reason counted apart: unreadable (a needed quantile missing or not a number, quantiles out of order, or the reported value unreadable), no early release (first-reported side only).
- NOTHING_RETURNED: no reported value yet.
Values are compared as served. No tolerance is added. Counts are whole numbers and the quantiles may be equal, so an interval of zero width that equals the count is inside. The share of rows whose stated 50 percent interval has zero width is printed beside every cell.

Cell share: CONSISTENT rows over rows that read CONSISTENT, ABOVE or BELOW. CANNOT_TELL and NOTHING_RETURNED are shown beside every cell and never folded into either side. The shares above and below the interval are printed apart.

Interval for a cell. Rows are not independent: every location in one week shares one season, forecasts at different horizons share target weeks, and neighbouring weeks move together. The interval is a moving-block bootstrap over target weeks. The target weeks of all scored rows are sorted, blocks are 4 consecutive weeks in that list, a replicate draws ceil(W/4) block starts with replacement from the W-3 possible starts, and every row of the cell whose target week falls in a drawn block enters with that multiplicity. 2,000 replicates, seed 20261110, the same draws for every cell. The 95 percent interval is the 2.5th and 97.5th percentile of the replicate shares. A replicate with no scored row in the cell is skipped. The page says the interval is a block bootstrap and why.

Cell outcome against the stated level p (0.50 or 0.95):
- CANNOT_TELL if the cell has fewer than 30 scored rows or fewer than 8 distinct target weeks.
- BELOW if the interval's upper bound is under p (the interval held the reported count less often than stated).
- ABOVE if the interval's lower bound is over p (more often than stated).
- CONSISTENT if p is inside the interval and the interval is no wider than 0.10.
- Otherwise CANNOT_TELL.

Cells, each for both intervals and both delivered sides:
- All horizons and locations (the headline cell is this one, 95 percent interval, final side). Then horizons 0, 1, 2 and 3.
- Each season, all horizons.
- Each location, all horizons (final side on the page, both sides in the data).

Second ruler: weighted interval score (WIS). For each row with all 23 ensemble quantiles and all 23 baseline quantiles and a reported value: WIS = (0.5 |y - median| + sum over the 11 central intervals of (alpha/2) times the interval score) / 11.5, where the interval score of [l, u] at level 1 - alpha is (u - l) + (2/alpha)(l - y) if y < l, + (2/alpha)(y - u) if y > u. Cell value: sum of ensemble WIS over sum of baseline WIS on the same rows. Interval: the same block bootstrap. Outcome: BELOW if the upper bound is under 1 (ensemble scores lower than the baseline), ABOVE if the lower bound is over 1, CONSISTENT if 1 is inside and the interval is no wider than 0.20, otherwise CANNOT_TELL, with the same minimum rows and weeks. No number is stated by the hub for this ratio. Comparing it with 1 is our ruler and is named as ours. Cells: all horizons, each horizon, each season, final side primary, first-reported side shown.

## Both alternatives
A. The stated intervals hold the reported count about as often as stated. Cells read CONSISTENT, or CANNOT_TELL with the stated level inside.
B. They hold it less often (BELOW) or more often (ABOVE) than stated.
Either result is printed the same way. A cell that reads BELOW or ABOVE says how often the reported count left the interval. It names no cause.

## Known-good gates (a failed gate turns every outcome into CANNOT_TELL)
1. Format. Every used ensemble file has the columns reference_date, location, horizon, target, target_end_date, output_type, output_type_id, value, and its "wk inc flu hosp" quantile levels include 0.025, 0.25, 0.5, 0.75 and 0.975. time-series.csv has as_of, target, target_end_date, location, observation.
2. Reader. Three stated values read directly from the raw text of three ensemble files equal the parsed values. Rows chosen from the stated side only and written into data/known_good_rows.json before the first comparison.
3. Join. target-data/target-hospital-admissions.csv (the hub's latest snapshot) agrees with the final side of time-series.csv on at least 99 percent of the location-weeks both hold.
4. Rule. Synthetic rows read ABOVE, BELOW, CONSISTENT and each CANNOT_TELL reason correctly. WIS matches a value worked out on paper for a planted row. A planted world with calibrated quantiles reads CONSISTENT in the bootstrap cell rule, and a planted world with intervals half as wide reads BELOW. heuremen_kit's self-test passes.

## Described and not scored
Shares above and below each interval. The median of (reported minus stated median) over the stated 95 percent interval width, by horizon. How often the first-reported and final values differ, and by how much.

## Set aside
Rate-change category forecasts, peak week and peak size, ED visit proportions, sample trajectories, individual team models, horizon -1, seasons before 2023-24 (another hub layout).

## Reading done before this plan was written
The hub README and target-data README, hub-config/tasks.json (first rows), the two metadata files, the LICENSE header, file names in both model folders (90 each, 2023-10-14 to 2026-11-07), the header and first data row of four ensemble files (values 4, 14, 7 and 92 for location 01 at the 0.01 quantile), counts of rows by horizon and target in those four files, and the time-series.csv header and first rows. From time-series.csv: the list of as_of values (102), the latest target week each holds and their row counts, and a check that repeated rows in as_of 2026-05-27 carry equal values. The CDC current-week forecast page. No stated interval was set beside a reported count, and no reported count for a forecast week was looked up.

## Terms recorded
Hub repository: MIT licence. FluSight-ensemble metadata: CC-BY-4.0, credited on the page. NHSN data: CDC, US government. Read through GitHub with git, no key.
