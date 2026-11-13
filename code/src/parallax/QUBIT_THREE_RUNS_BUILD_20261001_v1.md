# QUBIT THREE RUNS -- BUILD REPORT, 2026-10-01
Spec (the only design): `QUBIT_THREE_RUNS_APPROVED_20261001.md`. Code: `out/qubit_three_runs/`.
Nothing was submitted to hardware. `--fire` was never called. The only account contact was one read-only look (usage, backend limits, properties) via `live_probe.py`.

## READ THIS FIRST
**THE DRY RUN PROVES THE CODE PATH ONLY, NOT THE PHYSICS.** The local simulator has no raw I/Q, so every I/Q number in the dry runs is SYNTHETIC (fabricated from simulated 0/1 outcomes, plus an injected synthetic fade of tau = 300 us so the fit has something to find). Every dry-run results file and every analysis header says so. The 300 us recovered as ~250-275 us says only that the fitting code runs; it says nothing about the chip.

**The account has 0 seconds left right now** (601 of 600 used; `time_available_at` 2026-10-22). Any `--fire` today would be refused by its own guard.

## Where it broke first
1. **First break, run 1 dry run: `meas_type="kerneled"` (raw I/Q) on the local simulator.** `UFuncTypeError: ufunc 'multiply' did not contain a loop with signature matching types (complex128, <U4)` (a different symptom than the IndexError sealed_disco2 saw; same cause: there is no kerneled-measurement model locally). Substitution, declared: same circuits, bitstring measurement, each 0/1 placed in a synthetic Gaussian cloud around a fabricated per-qubit centre. Recorded in every `run*_meta.json` under `simulator_breaks`.
2. `rep_delay` is accepted and ignored locally (UserWarning). Rep-rate effects exist only on hardware.
3. **The local noise model has no fading during a WAIT.** Simulated ON-start mean bit fell 0.014 across a 1000 us wait where the maker's T1 median (292 us) alone would give about 0.9. (Aer attaches relaxation to gates, not to `delay`.) So the clock fit cannot be tested on simulated physics; the dry run injects a labelled synthetic fade instead (`--synth-tau-us`, default 300, 0 = none; value recorded in meta).
4. Not a simulator break but found in the dry run: the FakeKingston snapshot (2026-04-15) has qubit 96 at readout error 0.49, which blew up a plain mean across qubits (variance 2.4 +- 31). Pooling across qubits is now the MEDIAN. The live backend today shows qubit 96 at 0.013.
5. Memory: no break at 9 qubits (cap 2048 MB, 1 thread). The full-width/stabilizer breaks from sealed_disco2 do not apply at this width.
6. Untestable locally, so a risk on first real fire: mid-circuit measurement together with `meas_type="kerneled"` on Kingston, and the real shape of the returned complex arrays (`np.asarray(data.L1)` is assumed to be (shots, qubits) complex). The sealed_disco2 jobs assumed the same; nobody has confirmed it end to end.
7. Plumbing bug avoided: sealed_disco2 v1 transpiled with no layout, so virtual qubits 0..n landed on physical 0..n. Here every circuit is transpiled with `initial_layout = the chosen qubits`, and `check_layout` refuses any leak.

## What each run is, in plain words
Every qubit gets one of three STARTS: **OFF** (nothing put in), **BOTH-AND-NEITHER** (one half-turn gate, the in-between state), **ON** (fully put in). A **LOOK** is one reading of the qubit; the raw readout dot (I/Q) is kept every time. A **WAIT** is the pause between two looks.
- **Run 1, ONE LOOK:** start, look. 3 circuits (one per start).
- **Run 2, TWO LOOKS:** start, look, wait, look. Waits short 20 us / medium 100 us / long 1000 us. 3 starts x 3 waits = 9 circuits.
- **Run 3, THREE LOOKS:** start, look, wait, look, wait, look. Layout (wait in gap 1, wait in gap 2): (20,100), (100,1000), (1000,20), for each start = 9 circuits. Across the 9 circuits each wait sits in gap 1 exactly 3 times and in gap 2 exactly 3 times. (Same-wait pairs and the 27-circuit full grid were not built; the three-layout cycle is the smallest set that balances every wait across both gaps.)
- Waits are laid down as whole multiples of 16 clock ticks: 19.968, 99.968, 1000.000 us realized (backend limits did not force any change; realized values are in each meta file).
- Same qubits in all three runs: **random groups of three, seed 20261001** (full: 3 groups = 9 qubits: [82,139,154], [38,92,96], [25,109,135]; min: first 2 groups = 6 qubits). Candidates = qubits with measure, x, sx. Circuit order: seeded shuffle, **run 1 seed 20261011, run 2 seed 20261012, run 3 seed 20261013**. Synthetic-I/Q seed 20261021. Analysis seed 20261031, bootstrap 200.
- One job per run, all of a run's circuits as pubs of one sampler call. rep_delay fixed at 500 us (backend range 0-2 ms), recorded.
- Recorded in every results set: start and end time, backend calibration timestamp, and the maker's published T1/T2/readout error per qubit (the OUTSIDE reading) in `run*_maker_clock.json` beside the results.

## QPU-second estimates
Method as sealed_disco2: 3.0 s per job (measured from the real echo run) + sequence time (shots x [rep_delay + looks x 1.6 us readout + waits]); 1.6 us readout is an assumption. Two bases: per-job (one job per run) and worst case charging 3.0 s per circuit.

| | shots/circuit | qubits | Run 1 | Run 2 | Run 3 | **Three runs, per-job basis** | Worst case (3.0 s per circuit) |
|---|---|---|---|---|---|---|---|
| **FULL** | 1500 | 9 | 5.3 s | 14.8 s | 19.9 s | **40.0 s** | 94.0 s |
| **SMALLER** | 500 | 6 | 3.8 s | 6.9 s | 8.6 s | **19.3 s** | 73.3 s |

Qubit count does not change QPU time (qubits run in parallel); only shots and waits do. The smaller variant cuts shots and one group. All three starts and all three waits are kept in both. Fire guard (account must hold 1.25 x the worst case for that run): full 15 / 49 / 55 s (119 total); smaller 13 / 39 / 41 s (93 total).

## Exact fire commands (never run by the builder)
Each requires the sealed, posted prediction file for that run (its sha256 is printed and saved in the meta) and refuses unless the account holds the seconds. Dry-run first, always.
```
cd /Users/heuremen/bones-forge/parallax/out/qubit_three_runs
PY=~/bones-forge/venv_quantum/bin/python
$PY run1.py --fire --variant full --prediction-file <run1_sealed.json> --confirm-submit
$PY run2.py --fire --variant full --prediction-file <run2_sealed.json> --confirm-submit
$PY run3.py --fire --variant full --prediction-file <run3_sealed.json> --confirm-submit
```
(`--variant min` for the smaller purchase. Without `--confirm-submit` a fire call only builds, budget-checks and prints; with a short account it exits with BRAKE.) Results land in `data/fire_<variant>_<stamp>/`; analyze with `analyze.py run1 | run1+2 | run1+2+3 --data-dir <that dir> --predictions <file>`. The fire path's account/sampler/collection code is the one part never exercised even in dry form (it needs the account); read it before the first real fire.

## Quantities that need sealed predictions
Template: `out/qubit_three_runs/predictions_template.json` (69 quantities, no numbers filled; each takes `predicted` and `width`; MISS = |measured - predicted| / width). All values are in that run's own look units: the OFF-to-ON line, OFF = 0, ON = 1. Pooled across qubits by median.
- **Before run 1:** `r1.L1.{OFF,MID,ON}.{mean,var,skew}` (9); `r1.L1.MID-MIX.{mean,var,skew}` (3); `r1.remainder_rms`.
- **Before run 2:** `r2.tau.{OFF,MID,ON,shared}` (fading time, us); `r2.{start}.w{20,100,1000}.gap_mean` (9); `r2.remainder_rms`.
- **Before run 3:** `r3.{start}.pool.hat{1,2,3}` (9) and `r3.ALL.hat{1,2,3}` (3) (each look's own error variance, raw); `r3.tau12.shared`, `r3.tau23.shared`; `r3.remainder_rms`.
- **For the combined table:** `drift.L1.{start}.{mean,var,skew}.run{1,2,3}` (27).
Note: OFF mean and ON mean are 0 and 1 by construction (that is the ruler), so predicting them is empty.

## What the analysis prints (analyze.py)
Run 1 reads THE MESSAGE: per start, mean / variance / third moment (on the continuous projection of raw I/Q, never 0/1); the seeded 50/50 pool of OFF+ON shots; BOTH-AND-NEITHER minus the pool, with OFF-minus-pool(MID,ON) and ON-minus-pool(OFF,MID) beside it. Run 2 reads THE CLOCK: gap look1-to-look2 per start and wait (each wait against the other two), fitted fading time per start and shared, three clocks (inside fitted / outside waits / maker T1,T2) with every pair beside the third. Run 3 reads THE SUBSTRATE: V12, V23, V13; the three-cornered-hat solve (raw, negatives kept); THE REMAINDER = what each pair of looks shares, read against the other two pairs (C12, C23, C13 and rem12/rem23/rem13), plus its rms over all nine circuits; a ruler row for the gap-closure identity. Combined mode: look 1 is the one reading present in all three runs, so drift = each run against the mean of the other two, with width, plus the measured time between runs, plus the MISS table for every sealed prediction. The last line gives each run's own left-over (run 1: rms of the MID-minus-pool numbers; run 2: rms of the shared-fit residuals; run 3: rms of the rem values) with width in widths, lists which runs carry a readable one, and prints no YES or NO. **Choice to confirm with the owner:** "which runs see it" is implemented as "which runs produced a readable remainder", with the value-in-widths printed beside; I did not cut a line.
Dry-run end-to-end results (synthetic): `analyze.py run1`, `run1+2`, `run1+2+3` all exit 0 on both the full and the smaller dry data; 1 row of CAN'T READ per start-with-no-fade (OFF) appears with its reason (fading time ran to the search edge). Pooled-qubit width and the across-groups spread are both printed.

## Audit: two-way comparisons and thresholds in analyze.py
Grep for pass/fail/threshold/significant/consistent/agree/match/verdict/YES/NO/clip/max(0/comparison-against-a-constant found:
- **No threshold on any measured number. No verdict word in output. No clipping of any solve** (hat negatives print raw).
- Conditionals that exist, none a reading: `MIN_SHOTS = 30` (fewer shots on a look -> CAN'T READ with reason); fit pinned at the 1 us / 100000 us search edge or non-convergent -> CAN'T READ with reason; non-finite gap -> CAN'T READ; prediction width <= 0 -> CAN'T READ. The count of failed refits inside the bootstrap is printed on the row, not used to drop it. These are structural limits of fitting, flagged for the owner in case any counts as a cut.
- **Two-way items that remain, each spec-mandated or an input, each shown inside its three:** MID minus the OFF+ON pool (spec), always printed with the other two starts read against the pool of their other two; pairwise variances V12/V23/V13 (the hat's three inputs, all three always together); the look-1-to-look-2 gap itself (spec) is shown for each wait against the other two; the three-clock pair ratios (spec) each with the third clock beside; the axis is defined from OFF and ON look-1 centres (a ruler, not a printed comparison).
- **Found and removed while building:** (1) drift in `run1+2` mode would have been a lone pair of runs -> now prints CAN'T READ (needs all three). (2) A signed remainder: the three rem values sum to exactly zero by construction, so a signed mean would have been a hidden zero -> replaced by the rms plus the three signed values printed. (3) A duplicate per-start signed row. (4) Plain mean across qubits (one poor qubit owned it) -> median. (5) Anything that thresholded a look to 0/1: none was written; the third-moment statistic runs on the continuous projection only.
- Caveats on numbers (not on rules): an rms remainder carries a positive bias from sampling noise and is not centered on zero; the shared fit has 5 degrees of freedom, the per-start fits have 1; the hat assumes uncorrelated look errors and the looks here are causally chained, so a negative or odd solve is data, not an error.

## Files
`out/qubit_three_runs/`: `common.py` (plumbing, estimator, fire guard), `run1.py`, `run2.py`, `run3.py`, `analyze.py`, `predictions_template.json`, `live_probe.py` (read-only), `data/dryrun_full/`, `data/dryrun_min/` (synthetic results, meta, maker-clock files, analysis json).
