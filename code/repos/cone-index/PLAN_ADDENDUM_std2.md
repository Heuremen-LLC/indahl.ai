# CONE plan addendum for Faults and Guards 2.0, 12 Nov 2026

This addendum is dated 12 Nov 2026 and is written before any reading is computed under the 2.0 outcome rule. PLAN.md is not edited and its seal in data/plan_seal.json is unchanged. The data, the sources, the cone construction, the known-good checks and the tests are unchanged beyond the outcome rule. Outcomes recorded earlier stand under the rules PLAN.md named.

## Bands and edge convention
Every reading in PLAN.md is a two-sided band, so each is read with K.read(lo, hi, band=...) and no size that matters is needed. The both-alternatives test is not applied to these cells, and each recount says so.
- Whole-path cells, band [0.60, 0.70], NHC's stated about 60 to 70 percent.
- Circle cells, band [0.6167, 0.7167], two-thirds plus or minus 5 points, our reading and named as ours. It prints as 61.7 to 71.7 percent.
- Second ruler rows, band the NHC mean plus or minus the larger of 1.0 n mi and 2 percent of the NHC mean. This is an exact row-level read of a published mean against a published mean with the plan's tolerance, an interval of zero width (owner decision O1), read with K.read_exact.
Both edges are closed for every band. An interval end equal to a band edge is inside the band. A circle row is INSIDE when the distance is less than or equal to the radius, as PLAN.md states, and that is the same closed convention. PLAN.md did not write the edge convention. It was closed in the code through the old K.classify, and this addendum states it.

## Interval method and level
Unchanged. A storm-level block bootstrap, storms resampled with replacement, all of a drawn storm's rows come with it, 2,000 resamples, seed 20261110, percentile 95 percent interval. The second ruler's own bootstrap of our mean is a description and decides nothing.

## How the desk's own CANNOT_TELL causes map to the closed reasons
- A cell with fewer than 10 storms or fewer than 30 scored rows: TOO_WIDE_TO_RESOLVE (owner decision O3).
- A cell with no scored rows, so no interval can be formed: NO_INTERVAL_FORMABLE. This includes a current season with no forecast that has a full track yet.
- A known-good gate failure, which turns every outcome into CANNOT_TELL: NO_INTERVAL_FORMABLE. The earlier outcome is kept as outcome_before_gate.
- A circle row whose position does not parse: NO_INTERVAL_FORMABLE.
- A second ruler row whose NHC value is missing: NO_INTERVAL_FORMABLE.
- A second ruler row whose case counts differ by more than the larger of 2 cases and 5 percent: NO_INTERVAL_FORMABLE. The samples differ, so the planned comparison of two means over the same cases cannot be formed.
- An interval that overlaps a band edge without meeting a rule above: STRADDLES_EDGE.

## Failed reads
A forecast position with no best-track point at the verifying time, or a point that is not a tropical or subtropical cyclone, is NOTHING_RETURNED, each reason counted apart as PLAN.md says. It is a status of the read (read_status in the rows) and never an outcome. Those rows are outside the numerator and denominator of every share. The same holds for a whole-path forecast whose track ended or stopped being tropical inside five days.

## Counts beside every headline share
Beside every cell and beside the headline the recount prints the NOTHING_RETURNED count and the CANNOT_TELL share split by reason, over the rows of the cell (REQ-13, K.req13). For a whole-path cell the rows are the scored whole-path forecasts and the failed reads are the forecasts whose track ended. For a circle cell the rows are the positions that read INSIDE, OUTSIDE or CANNOT_TELL.

## Effect on recorded outcomes
No cell changes its outcome under this addendum. The Atlantic whole path, 697 of 1,315, interval 45.1 to 60.4 percent, remains CANNOT_TELL, now with reason STRADDLES_EDGE because the interval overlaps the lower edge 0.60 of the band. The 14 circle cells and the second ruler rows keep their readings.
