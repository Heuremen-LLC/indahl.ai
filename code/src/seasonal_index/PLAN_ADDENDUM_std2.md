# SEASONAL: plan addendum for Faults and Guards 2.0, 12 Nov 2026

This addendum is written before any new reading under the 2.0 outcome rule. PLAN.md is not edited and its seal in data/plan_seal.json is unchanged. The data, the sources, the grid, the bins, the known-good checks and the interval method are unchanged. Only the outcome rule changes, to the reading outcomes of the standard (section 6). Outcomes recorded earlier stand under the rules they named.

## Reading cells (bins and the leaning cells)
- The quantity is the observed share of rows in the cell. The figure it is read against is the mean stated chance of the rows in the cell. The plan names a width cap of 0.10 and no tolerance, so the figure is a point figure with no tolerance.
- Under 2.0 a point figure with no tolerance has no CONSISTENT. The cell reads against the bound at the mean stated chance. ABOVE if the lower end of the interval is over the bound. BELOW if the upper end is under it. Otherwise CANNOT_TELL with reason STRADDLES_EDGE. The width cap of 0.10 is retired as an outcome rule. No tolerance is named now, because one named after the data would be a rule written after the data.
- Edge convention: closed. An interval end equal to the bound is not over it and not under it.
- Size that matters: none named in PLAN.md and none is named now. The both-alternatives test is not applied to these cells, and the page says so.
- Interval: the plan's moving-block bootstrap over seasons, blocks of 12 consecutive seasons, 2,000 replicates, seed 20261110, 2.5th and 97.5th percentiles, level 95 percent. It is kept in the desk's own code, because it resamples whole seasons with a weight matrix on array sums. The kit's block_bootstrap draws from a different random stream and would not reproduce the stored intervals. The method is unchanged.

## Heidke difference cells
- The plan's two-sided band of minus 2 to plus 2 points is a tolerance, so CONSISTENT stays available. Edge convention closed. The band is read with the kit's band reading.
- Size that matters: none named. Both-alternatives test not applied.
- Interval: the same block bootstrap over seasons as above.

## How the desk's own CANNOT_TELL causes map
- A cell with fewer than 30 rows or fewer than 24 distinct seasons reads CANNOT_TELL with reason TOO_WIDE_TO_RESOLVE (minimum sample rule, owner decision O3).
- A cell with no rows, a cell whose bootstrap forms no interval, and any cell read while a known-good check has failed read CANNOT_TELL with reason NO_INTERVAL_FORMABLE. A failed known-good check means the files cannot be trusted to form a reading, so the planned quantity cannot be formed. The old bare CANNOT_TELL had no closed reason, and this is the closest one.
- Interval overlaps the bound or the band edge: STRADDLES_EDGE.

## Counts beside the headline (REQ-13)
- The headline is the temperature leaning cell. Beside it the page prints the REQ-13 line over every reading of the desk (the leaning cells, the bin cells and the Heidke difference cells).
- NOTHING_RETURNED counts the failed reads: the forecast records still waiting for an observed season, as PLAN.md names them, and any CPC file whose fetch failed in the run. They are listed apart and are outside the numerator and denominator.
- Unreadable rows (stated chances missing or impossible) are left out of the cells as before and their count stays printed.

## Expected effect, stated before the new run
The temperature leaning headline stays ABOVE. The precipitation leaning cell and seven bin cells that read CONSISTENT by the width cap read CANNOT_TELL with reason STRADDLES_EDGE. The four Heidke difference cells stay CONSISTENT. No number other than an outcome moves.
