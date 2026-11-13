# QUAKE plan addendum for Faults and Guards 2.0, 12 Nov 2026

This addendum is dated 12 Nov 2026 and is written before any reading is computed under the 2.0 outcome rule. PLAN.md is not edited and its seal is unchanged. The data, the sources, the catalog counts, the known-good checks and the tests are unchanged beyond the outcome rule. Outcomes recorded earlier stand under the rules PLAN.md named.

## What is read and against what
- Range cells. The reading is the share of scored rows whose count fell inside the stated 95 percent range. The figure is the stated 95 percent. It has a tolerance named in PLAN.md, so the CONSISTENT band is [0.925, 0.975].
- Probability cells. The reading is the share of rows with at least one event. The figure is the mean stated probability of the cell. The tolerance named in PLAN.md is the largest of 0.01 and the smallest of 0.05, half the stated value and half of one minus the stated value, so the band is the stated value plus or minus that tolerance.
- Row level. A row is an exact read of a count against a published range. The count is an interval of zero width. It reads CONSISTENT inside the range with the ends included, ABOVE over the maximum and BELOW under the minimum, by K.read_exact with band (p95minimum, p95maximum) and closed edges.

## Two rules, both kept from PLAN.md
PLAN.md names two things for a cell. ABOVE and BELOW are read against the stated figure itself (ABOVE if the lower end is over it, BELOW if the upper end is under it). CONSISTENT needs the whole interval inside the tolerance band. The addendum reads them as a two-step call with K.read. First K.read(lo, hi, bound=figure) decides ABOVE or BELOW. If it gives neither, K.read(lo, hi, band=band) decides CONSISTENT. Anything else is CANNOT_TELL with reason STRADDLES_EDGE. This keeps every earlier cell reading as the plan wrote it and adds only the reason.

## Size that matters and the both-alternatives test
PLAN.md reads each cell against its own stated figure and names no size that matters. The reading is a coverage against a stated figure, not a departure from a null. The both-alternatives test therefore is not applied to these cells, and each recount says so. No cell can read TOO_WIDE_TO_RESOLVE through that test.

## Edge convention
Both edges are closed for every band and bound. An interval end equal to the stated figure is not ABOVE or BELOW. An interval end equal to a band edge is inside the band. The probability bins of PLAN.md (lower end included, upper end not, 100 percent in the top bin) are rules for which row falls in which bin and are not edge conventions of a reading.

## Interval method and level
Unchanged. The Wilson 95 percent interval and the sequence-block bootstrap (blocks of events within 100 km and 365 days, chained, 2,000 resamples, seed 20261110, percentile 95 percent). The interval used is the union of the two.

## How the desk's own CANNOT_TELL causes map to the closed reasons
- Fewer than 30 scored rows or fewer than 10 blocks: TOO_WIDE_TO_RESOLVE. The sample is below the desk's minimum, so the interval is too wide to resolve any reading.
- A cell with no rows (zero denominator) or whose bootstrap interval could not be formed: NO_INTERVAL_FORMABLE.
- A known-good gate failure, which turns every outcome into CANNOT_TELL: NO_INTERVAL_FORMABLE. The instrument failed, so no interval is formed that can be trusted. The earlier outcome is kept as outcome_before_gate.
- A row whose value did not parse, or whose version states no zone or a zone of another shape: NO_INTERVAL_FORMABLE. The planned count cannot be formed for that row.
- An interval that overlaps the figure or a band edge without meeting a rule above: STRADDLES_EDGE.

## Failed reads
A window not closed a week ago, or a catalog copy not read after a window closed, is NOTHING_RETURNED. It is a status of the read (read_status in the rows). It is never an outcome. Those rows are listed apart and are outside the numerator and the denominator of every share. Rows with an unreadable value or no zone are CANNOT_TELL with NO_INTERVAL_FORMABLE and count in the REQ-13 line.

## Counts beside every headline share
Beside the headline cell and every cell the recount prints the NOTHING_RETURNED count and the CANNOT_TELL share split by reason, over the rows of that cell (REQ-13, K.req13). Rows with an unreadable magnitude or probability cannot be placed in a cell and appear in the desk-level req13 in the summary.

## Effect on recorded outcomes
No cell changes its outcome under this addendum. The headline cell, M3 and above in every window, remains CANNOT_TELL, now with reason STRADDLES_EDGE because its interval overlaps the 0.975 band edge.
