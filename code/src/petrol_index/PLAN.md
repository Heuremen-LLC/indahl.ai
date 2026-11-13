# PETROL: oil output (volumes only, never prices), stated against delivered. Plan, written before any outcome was computed by this desk.

Division ATLAS. Heuremen LLC. Draft, not shipped, no ledger rows.

## Part 1. OPEC+ required production against delivered crude output
### Claim read
OPEC+ ministerial statements publish a required production level per country in thousand barrels a day (tb/d). OPEC's Monthly Oil Market Report (MOMR) publishes crude production per country from secondary sources, and the DoC statements say conformity is monitored with the average of the approved secondary sources. The required level is the stated figure. The secondary-source figure is the delivered one. Gap = delivered minus required, in tb/d. Nothing here says a country is non-compliant. A reading says only where the gap sits against a width.

### Frame (fixed now)
Members: the 22 countries in the MOMR DoC secondary-sources table: Algeria, Congo, Equatorial Guinea, Gabon, IR Iran, Iraq, Kuwait, Libya, Nigeria, Saudi Arabia, UAE, Venezuela (OPEC), Azerbaijan, Bahrain, Brunei, Kazakhstan, Malaysia, Mexico, Oman, Russia, Sudan, South Sudan (non-OPEC DoC). Months: November 2024 to October 2026 (24 months). A row is one member and one month. Every row gets an outcome and none is dropped. Prices are not read.

### Delivered figure
The latest print of the month in the MOMR secondary-sources table among the issues cached by this desk (data/raw/momr). The source PDF, page and table title are kept per value (data/momr_secondary.csv). A printed ".." or a missing value is CANNOT_TELL (no delivered value).

### Stated figure (target)
Only figures read from an OPEC press statement are used, each with its URL and image. No target is interpolated, extended or computed from another month.
- Non-eight members (Congo, Equatorial Guinea, Gabon, Nigeria, Azerbaijan, Bahrain, Brunei, Malaysia, Mexico, Sudan, South Sudan): the table "Required Production Levels for 2025 and 2026" of the 38th ONOMM statement (Dec 2024), reaffirmed by the 41st ONOMM statement (June 2026). Applies January 2025 to October 2026. November and December 2024 have no 2024 table transcribed: CANNOT_TELL, no target.
- Eight voluntary-adjustment countries (Algeria, Iraq, Kuwait, Saudi Arabia, UAE, Kazakhstan, Oman, Russia): only a month that has its own monthly required production table in an eight-country (later seven-country) statement. The transcribed months are listed in data/targets.csv. Any other month is CANNOT_TELL, no target table transcribed. The UAE has no table after the May 2026 one (the later statements list seven countries), so UAE is CANNOT_TELL from June 2026.
- Exempt: Libya, IR Iran, Venezuela have no required level in the tables: CANNOT_TELL, exempt.
- The tables are images, so the figures were read by eye and typed into data/targets.csv. A second pass re-reads every typed value against its image before the run (gate 3).
Compensation plans and any additional cut a country states for itself are not read. The required level is the one in the table.

### The ruler (fixed now, from revisions only, never from gaps)
The width of the delivered figure is OPEC's own revision of the same month. For a month M, the first print is in the earliest cached issue that holds M and the second print is in the next issue. r = second print minus first print. The baseline is every month whose second print is in an issue up to October 2024, using issues from May 2020 (earlier issues use a different layout and are not parsed) to October 2024. Issue December 2023 was not reachable, so months whose first or second print needs it have no revision row. The baseline ends before the first scored month, so the ruler never sees a scored gap.
- OPEC members (Algeria, Congo, Equatorial Guinea, Gabon, Iraq, Kuwait, Nigeria, Saudi Arabia, UAE): width w = the 90th percentile (nearest rank) of |r| for that member over the baseline. A member with fewer than 24 revision rows is CANNOT_TELL, no width.
- Non-OPEC DoC members: their secondary-source crude figures appear in the cached issues only from the May 2024 issue. Width is relative and pooled: q = the 90th percentile (nearest rank) of |r| divided by the first print over all ten members and all baseline months (issues May 2024 to October 2024), and w = q times the delivered figure of the row. Fewer than 30 pooled rows gives CANNOT_TELL, no width.
This width is a yardstick of how much the delivered figure moved between OPEC's own prints. It is not a published width, and the page says so. Later prints (a third print and beyond) can move a month further, and that is described and not scored.

### Outcome rule (fixed now)
gap = delivered minus required. ABOVE if gap > w. BELOW if gap < minus w. CONSISTENT if |gap| <= w, edges included. CANNOT_TELL with a counted reason: exempt, no target, no delivered value, no width. The four outcomes are never folded. CANNOT_TELL is its own count and never joins CONSISTENT. No share of rows is read against 90 percent, the yardstick is not a stated coverage.
Described and not scored: median gap per member over the scored months, the largest gap, the gap in units of w.

### Headline candidate (named now)
For the latest month in the window with a delivered figure: its outcome counts over the 22 members, ABOVE, BELOW, CONSISTENT, CANNOT_TELL as separate numbers, and the same four counts over all 24 months. If the latest month has fewer than six scored members, the latest month with six or more is used and the page says which.

### Known-good gates
1. Parse: every cached issue from May 2020 has 12 OPEC members, and each issue from May 2024 has 22. The total of the OPEC rows is within 3 tb/d of the printed Total OPEC for the three months of one hand-picked issue (October 2026), and the 22 September 2026 values equal the hand-read table printed in the scout of this desk.
2. Join: the target table has 22 members with a target or an exempt/no-table reason for all 24 months.
3. Targets: every typed value equals the value re-read from its statement image on a second pass, and the eight-country monthly totals match the printed increment totals (206 tb/d for April and May 2026, 188 for August 2026, 137 for December 2025).
4. Rule: synthetic rows with a known answer read ABOVE, BELOW, CONSISTENT and every CANNOT_TELL reason correctly.
A failed gate turns every outcome into CANNOT_TELL.

## Part 2. EIA weekly US crude production against EIA monthly
### Claim read
EIA's Weekly Petroleum Status Report prints a weekly estimate of US field crude production, which EIA describes as model based and rounded. EIA's monthly figure (Petroleum Supply Monthly) is the delivered one. Question: where does the average of a month's weekly estimates sit against EIA's monthly figure, with a width taken from a baseline period named now.

### Data (fixed now)
Weekly: https://www.eia.gov/dnav/pet/hist_xls/WCRFPUS2w.xls, sheet Data 1, thousand barrels a day, week ending dates. Monthly: https://www.eia.gov/dnav/pet/hist_xls/MCRFPUS2m.xls, sheet Data 1, thousand barrels a day. Both are public, no key. Each file holds one vintage only (the current one), so earlier prints and later revisions of the monthly figure cannot be read from them. The page says so. The weekly series is itself re-benchmarked by EIA, and the file carries only the current series.

### Method (fixed now)
A week belongs to the month of its week-ending date. The weekly average of a month is the plain mean of those weeks, and a month needs at least four weeks. d = weekly average minus monthly figure. Baseline: January 2015 to December 2019 (60 months). Width w = the 90th percentile (nearest rank) of |d| over the baseline. EIA publishes no numeric uncertainty for either series in the files read, so none is used. Scored months: January 2020 to the latest month in the monthly file.
Outcome: ABOVE if d > w, BELOW if d < minus w, CONSISTENT if |d| <= w, edges included. CANNOT_TELL with reasons: no monthly value, fewer than four weeks, fewer than 48 baseline months. The four outcomes are never folded. The baseline months themselves are shown as a described row set and are not scored.
Described and not scored: median signed d and median |d| by calendar year of the scored months, the largest d, d in units of w, and the same counts at 0.5 and 2.0 times w (counts only, 1.0 times w is the reading that counts).

### Headline candidate (named now)
Counts of the four outcomes over the scored months, with the latest month's outcome and d named, and w in tb/d.

### Gates
1. Format: both files have sheet Data 1, header text names thousand barrels per day, dates are increasing, no gaps over 8 days in the weekly after 2015, no gap in the monthly after 2015.
2. Join: every scored month has at least four weekly rows, except any listed apart.
3. Hand check: one month (January 2019 in the baseline) averaged by hand from the printed weeks equals the script value.
4. Rule: synthetic rows read ABOVE, BELOW, CONSISTENT and each CANNOT_TELL reason correctly.

## Disclosure of what was seen before the plan
OPEC pages: the September 2026 secondary-sources table printed in the October 2026 MOMR (members and the layout), the text of the statements and the table images listed in data/targets.csv. No revision, no gap and no outcome was computed. The parser was run to check layout across issues and its output counts (rows per issue and members found) were printed, not the values. EIA: the first and last rows of each file were printed while checking the file layout (the weekly file ends at week ending 2026-10-30 with 14,003 and the monthly file at August 2026 with 13,965). No d, no baseline spread and no outcome was computed.

## Set aside
Prices of any kind, forecasts, causes of any gap, non-DoC countries, liquids other than crude, MOMR direct-communication figures (kept only as a described column if used later), any member before the window, EIA state or regional series.

## Amendment A1, 12 November 2026 (Bones, after the first run, before any later month was read)
The Part 1 window rolls. It starts November 2024 and ends one month past the newest MOMR issue's latest reference month, so each new issue adds a month on its own. Nothing else changes: the widths (OPEC first-to-second-print revisions to the October 2024 issue, the pooled 7.7 percent for non-OPEC members, EIA's 2015 to 2019 spread), the outcome rules and the CANNOT_TELL reasons stay as sealed. New required-production tables are still read by eye and checked against their printed increments before they count. Reason: a status that can go stale is rebuilt from the record by a script, or it is not published.
