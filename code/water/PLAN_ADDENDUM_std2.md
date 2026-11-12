# WATER plan addendum for Faults and Guards 2.0, 12 Nov 2026

This addendum is dated 12 Nov 2026 and is written before any reading is computed under the 2.0 outcome rule. PLAN.md and its two addenda are not edited and the plan hash stays as sealed. The data, the sources, the leads, the band, the cell definitions, the known-good checks and the tests are unchanged beyond the outcome rule. Outcomes recorded earlier stand under the rules they named.

## Row reading
A row sets the measured end-of-month elevation against the band between the Probable Minimum and Probable Maximum projections. Both are published values, so the reading is exact with no sampling, an interval of zero width (owner decision O1). The band is the lower projection minus 0.005 ft to the higher projection plus 0.005 ft, the plan's own tolerance. It is read with K.read_exact and closed edges. A measured value above the band is ABOVE, below it is BELOW, inside it is CONSISTENT. This is the plan's row rule unchanged. A row with no band that month, or one edge missing or unreadable, is CANNOT_TELL with reason NO_INTERVAL_FORMABLE, since the planned interval of projections cannot be formed. A row with no measured value for its month yet is NOTHING_RETURNED, a status of the read that carries no outcome and sits outside every count.

## Cell reading
- Band cell, against the 80 percent Reclamation states for the range of the minimum and maximum inflow scenarios. ABOVE if the lower bound of the Wilson 95 percent interval on water years is above 0.80, BELOW if the upper bound is below 0.80, CONSISTENT if the whole interval lies in the band [0.70, 0.90].
- Most Probable cell, against 0.50, our reading of a median. The same rule with the band [0.40, 0.60].
The plan names two figures for each cell, the claim for ABOVE and BELOW and a band for CONSISTENT. The addendum reads them as two K.read steps. First K.read(lo, hi, bound=claim) decides ABOVE or BELOW. If it gives neither, K.read(lo, hi, band=band) decides CONSISTENT. Anything else is CANNOT_TELL with reason STRADDLES_EDGE. No cell reading changes under this.

## Size that matters and the both-alternatives test
PLAN.md names no size that matters. Each cell is a coverage against a stated figure, not a departure from a null with a named size. The both-alternatives test is therefore not applied, and each recount says so.

## Edge convention
Both edges are closed for every band and bound, as the plan's strict comparisons imply. An interval end equal to 0.80, 0.50 or a band edge is neither above nor below the claim and is inside the band.

## Interval method and level
Unchanged. A Wilson 95 percent interval on water-year clusters, n_eff the number of distinct water years in the cell, k_eff the rounded effective count. The after-data rulers of Addendum 2 (rows as independent, water years weighted by row count, neighbouring water years paired, each with and without rounding) are displayed and decide nothing, and each now carries its own reason with the same mapping. There is no resampling, so no draws and no seed.

## How the desk's own CANNOT_TELL causes map to the closed reasons
- A cell with fewer than 10 water years, the plan's n_eff rule: TOO_WIDE_TO_RESOLVE (owner decision O3).
- A cell with no water years, so no interval can be formed: NO_INTERVAL_FORMABLE.
- A row with no band or an unreadable band edge: NO_INTERVAL_FORMABLE.
- A known-good gate failure, which turns every outcome into CANNOT_TELL: NO_INTERVAL_FORMABLE. The earlier outcome is kept as outcome_before_gate.
- The USGS provisional against approved test: fewer than 30 revised days is TOO_WIDE_TO_RESOLVE (the plan's minimum). With 30 or more it stays CANNOT_TELL with NO_INTERVAL_FORMABLE, since the plan says USGS states no expected revision size and so no figure is read against.
- An interval that overlaps the claim or a band edge without meeting a rule above: STRADDLES_EDGE.

## Counts beside every headline share
Beside each headline cell the recount prints the NOTHING_RETURNED count and the CANNOT_TELL share split by reason (REQ-13, K.req13). For a band cell the readings are the rows of that reservoir and lead, with the rows that have no measured value yet listed apart. For a Most Probable cell a row has a sign and no outcome of its own, so the readings are the rows with a sign, above or below, and the failed reads are the rows with a Most Probable value and no measured value yet. The line for that cell therefore counts no CANNOT_TELL rows. The reading of the cell itself is printed with its reason beside it.

## Effect on recorded outcomes
No cell changes its outcome under this addendum. Lead 6 Lake Mead and Lake Powell band cells stay BELOW. The Most Probable cells at lead 6 stay CANNOT_TELL, now with reason STRADDLES_EDGE. Of the 48 band cells per the plan's table 27 are BELOW and 21 CANNOT_TELL with STRADDLES_EDGE, and of the 48 Most Probable cells 7 are BELOW and 41 CANNOT_TELL with STRADDLES_EDGE.
