# NEO plan addendum for Faults and Guards 2.0, 12 Nov 2026

This addendum is dated 12 Nov 2026 and is written before any reading is computed under the 2.0 outcome rule. PLAN.md is not edited and its seal in data/plan_seal.json is unchanged. The data, the sources, the matching, the known-good checks and the tests are unchanged beyond the outcome rule. Outcomes recorded earlier stand under the rules PLAN.md named.

## Row reading
A row sets the delivered 3-sigma range of the latest solution against the stated range. Both are published values, so the reading is exact with no sampling. The delivered range [latest dist_min, latest dist_max] is the interval and the stated range [stated dist_min, stated dist_max] is the two-sided band, read with K.read and closed edges. ABOVE if the whole delivered range is above the stated maximum. BELOW if it is below the stated minimum. CONSISTENT if it lies inside the stated range with the ends included. Otherwise CANNOT_TELL with reason STRADDLES_EDGE. This is the plan's own row rule, unchanged.

## How the row CANNOT_TELL causes map to the closed reasons
- same solution (the latest orbit_id equals the stated one, so no later solution exists): NO_INTERVAL_FORMABLE.
- no record (no current record within 10 days and 0.5 au): NO_INTERVAL_FORMABLE.
- unreadable (a stated or delivered value does not parse, or min is above max): NO_INTERVAL_FORMABLE.
- wide range (the stated range is wider than 0.05 au, wider than the frame itself): TOO_WIDE_TO_RESOLVE. The stated range cannot separate the outcomes it is read against.
- edge (the delivered range crosses an edge of the stated range): STRADDLES_EDGE.
- A known-good gate failure, which turns every outcome into CANNOT_TELL: NO_INTERVAL_FORMABLE. The earlier outcome is kept as outcome_before_gate.
A row whose approach has not yet passed is NOTHING_RETURNED. It is a status of the read and carries no outcome. It is outside the numerator and denominator of every cell share.

## Cell reading
The reading is the share of scored rows that are CONSISTENT, CONSISTENT rows over rows that read CONSISTENT, ABOVE or BELOW, with a Wilson 95 percent interval. The plan names two figures for a cell. The ABOVE and BELOW bound is our 99.7 percent reading of a 3-sigma range. The CONSISTENT rule is that the lower bound is 0.98 or more. The plan names no upper limit for CONSISTENT because a share cannot pass 1, so this addendum writes the CONSISTENT band as [0.98, 1.0], a two-sided band whose upper edge is the cap of a share. The read is two steps. First K.read(lo, hi, bound=0.9973) decides ABOVE or BELOW. If it gives neither, K.read(lo, hi, band=(0.98, 1.0)) decides CONSISTENT. Otherwise CANNOT_TELL with reason STRADDLES_EDGE. With this band a cell such as 0 to 7 days, interval [0.9809, 1.0], keeps its CONSISTENT reading, and the sentence of PLAN.md that a cell needs about 190 scored rows, all inside, to read CONSISTENT is unchanged.

## Size that matters and the both-alternatives test
PLAN.md names no size that matters. The cell is a coverage against a stated figure, not a departure from a null with a named size. The both-alternatives test is therefore not applied, and each recount says so. The reading against 98.9 percent in the dependence block is displayed after the data, decides nothing, and uses the same two steps.

## Edge convention
Both edges are closed for every row, bound and band. An interval end equal to the bound 0.9973 is neither above nor below it. An interval end equal to 0.98 or 1.0 is inside the band.

## Interval method and level
Unchanged. A Wilson interval at 95 percent for every cell. Rows have no resampling, so there are no draws and no seed.

## Cell CANNOT_TELL causes
- Fewer than 10 scored rows: TOO_WIDE_TO_RESOLVE (owner decision O3).
- No scored rows (zero denominator): NO_INTERVAL_FORMABLE.
- A gate failure: NO_INTERVAL_FORMABLE.
- Any other interval that is neither above, below nor inside: STRADDLES_EDGE.

## Counts beside every headline share
Beside every cell the recount prints the NOTHING_RETURNED count and the CANNOT_TELL share split by reason, over the one row per object that the cell counts (REQ-13, K.req13). The summary also carries the same block for the headline rows of every approach.

## Effect on recorded outcomes
No cell changes its outcome under this addendum. All leads stays BELOW, 0 to 7 days stays CONSISTENT, 8 to 30 days stays CANNOT_TELL (STRADDLES_EDGE), more than 30 days stays BELOW. The 0 to 7 days CONSISTENT depends on the band [0.98, 1.0] written above.
