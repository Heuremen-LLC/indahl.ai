# heuremen_kit: the shared instrument pieces. Plan, written before the code.

Every corner of indahl.ai repeats the same rules: four outcomes, an interval on every share, a known-good gate before a reading counts, a plan committed before data, and a cost estimate before any paid run.
This kit holds those pieces once, so a new corner is a plan plus a collector.

## Pieces (fixed now)
- outcomes: ABOVE, BELOW, CONSISTENT, CANNOT_TELL, plus NOTHING_RETURNED for a failed read. No other label. A function that takes a share with an interval and a claimed bound and returns exactly one of the first four.
- wilson(k, n, z): the Wilson interval for a share. n = 0 returns the full range 0 to 1.
- known_good(gate_fn, readings): runs the gate on the control readings. If it fails, every reading is returned CANNOT_TELL and the failure is stated.
- plan_committed(path): true only if the plan file is tracked in git and its last commit is older than the first data row. Collectors call it and refuse to read otherwise.
- floor(null_counts, n_tests): the false-flag count a null world gives, with a Poisson bound, for tests with a fixed threshold.
- estimate_then_yes: a small helper for any paid run: prints the estimate, does nothing without an explicit yes.
## Tests
selftest runs planted worlds: shares at, above and below a bound over 30 seeds each (right outcome in at least 90%), the empty case, the failed gate, a plan with no commit, and the estimate refusal.
## Not in the kit
Fetching, parsing and page building stay in each corner. The kit never touches the network.
