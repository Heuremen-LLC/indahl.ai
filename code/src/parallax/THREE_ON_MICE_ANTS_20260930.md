# THREE FORMULAS ON TWO MORE RECORDS -- mice social sync + ant colony tempo, 2026-09-30

Continues THREE_ON_YEAST_20260930.md (arrow/clock/split, forward + backward chains,
Wayfinder's corrected verdict rule: **bootstrap errors from real-order resampling are the
judge, shuffle floors are logged but never the verdict**). Records: mice body-temp
circadian sync (dryad.1v8j2) and Temnothorax ant colony tempo/synchrony (dryad.4b92t21),
both already fetched and logged in DRYAD_SWEEP_20260930.md. Instrument reused verbatim:
`parallax/out/three_on_three/core.py` (factored from `parallax/out/yeast/three/
three_formulas.py` + `backwards.py`, no formula edits). New code: `mice_ants_pipeline.py`
(per-mouse / per-colony forward+backward chains) and `aggregate_mice_ants.py` (pooling +
verdict calls). Raw output: `mice_results.json`, `ants_results.json`,
`mice_ants_pooled.json`. No expectation written first. numpy only, single process.

## 0. Groups, corrected against SOURCE.txt

SOURCE.txt's inferred sizes ("1,1,2,2,3,3,4,5,5", sum=26) do not match the 25 mice on
disk. Direct count from filenames (`SC<mouseID>.<groupID>`) gives 8 groups: sizes
**3,1,2,5,5,2,4,3** (sum=25, correct). Bucketed as instructed (size 1 / sizes 2-3 /
sizes 4-5):

| bucket | groups | n mice |
|---|---|---|
| size1 (null) | group 2 | 1 |
| size2-3 | groups 1,3,6,8 | 10 |
| size4-5 (signal) | groups 4,5,7 | 14 |

Windows per mouse: first/middle/last third of the 8192-pt trace (~2730 pts each, dt=15
min). Detrend: single running-median width ~4 periods (385 pts, period=24h) -- the
multi-width cutoff-sensitivity test from the yeast run was NOT repeated here (time
budget); one width used and named, not hidden.

Arrow k-grid: 12 values, 0.25-3.0 periods in 0.25-period steps (6-72h). Shuffle floor
n=200/cell (logged, not the verdict). Bootstrap n=300/cell (real-pair/real-cycle
resampling, IS the verdict input). Reduced from yeast's 1000 for runtime across 25
mice x 3 windows x 2 chains; named as a scope cut, not hidden.

## 1. MICE -- three cells side by side (median across mice in the bucket, IQR spread)

### ARROW -- forward z (best-k vs shuffle floor, NOT the verdict, reported as the raw number)

| window | size1 (n=1) | size2-3 (n=10) | size4-5 (n=14) |
|---|---|---|---|
| first | -4.40 | -5.56 (IQR 9.07) | +3.21 (IQR 8.91) |
| middle | +3.28 | +1.63 (IQR 13.10) | -2.99 (IQR 8.10) |
| last | +4.63 | -5.46 (IQR 3.24) | -2.52 (IQR 10.19) |

Sign flips window-to-window and bucket-to-bucket with no pattern tied to group size --
matches DRYAD_SWEEP's own recursive-gradient finding (no directional asymmetry by
group size). Arrow forward-vs-backward **sign match fraction** (raw trace @best-k vs
message-unit series @k*, different units so magnitude not compared, sign only):
size1 = 1.0/0.0/0.0 (n=1, noisy), size2-3 = 0.70/0.60/0.70, size4-5 = 0.43/0.71/0.57.
No bucket shows better forward/backward sign agreement than another -- the null and the
signal groups are equally noisy on this formula.

### CLOCK -- forward tau_h (coherence-decay fit, raw trace) vs backward tau_h (message-unit series)

| window | size1 fwd/bwd (h) | size2-3 fwd/bwd (h) | size4-5 fwd/bwd (h) |
|---|---|---|---|
| first | 606.1 / 121.9 (DIVERGENT) | 455.3(IQR207) / 39.9(IQR19) | 229.4(IQR429) / 48.8(IQR24) |
| middle | 844.0 / 76.1 (DIVERGENT) | 347.1(IQR563) / 39.0(IQR23) | 306.2(IQR376) / 50.3(IQR27) |
| last | 239.7 / 54.8 (DIVERGENT) | 349.6(IQR321) / 46.4(IQR55) | 474.7(IQR301) / 39.5(IQR18) |

Forward-vs-backward call, by bucket x window (DIVERGENT = bootstrap sd > \|tau\| on
>=1 side, reported instead of a real verdict):

| window | size1 | size2-3 (n=10 mice) | size4-5 (n=14 mice) |
|---|---|---|---|
| first | DIVERGENT (1/1) | STABLE DISAGREEMENT 7, DIVERGENT 3 | STABLE DISAGREEMENT 10, DIVERGENT 3, AGREE 1 |
| middle | DIVERGENT (1/1) | STABLE DISAGREEMENT 6, DIVERGENT 4 | STABLE DISAGREEMENT 9, DIVERGENT 5 |
| last | DIVERGENT (1/1) | STABLE DISAGREEMENT 9, DIVERGENT 1 | STABLE DISAGREEMENT 12, DIVERGENT 2 |

Where a real call is possible (not divergent), it is **STABLE DISAGREEMENT every time**:
forward tau (raw trace, ~230-925h typical, order 10-40x the 24h period) sits an order
of magnitude above backward tau (message-unit crossing series, ~35-125h, order 1.5-5x
the period) -- same directional relationship as the yeast record's forward-vs-backward
tau gap, now seen a third way. The null group (size1) is 3/3 DIVERGENT, i.e. its clock
fit never converges cleanly on either chain -- n=1 mouse, flagged as thin evidence, not
asserted as a group effect.

### SPLIT -- forward P (all buckets, all windows)

P = **0.500 to float precision** in every one of the 75 mouse-windows (spread
2e-16 to 5e-16, i.e. zero to numerical noise), reproducing exactly on the backward
chain by construction (same telescoping-sum identity flagged in the yeast report: D is
a cumulative sum of the same crossing series it is regressed against). This is the
same construction artifact as the yeast record, not a biological finding -- reported
because it is a real, exact number, not hidden because it is inconvenient. Forward
z-vs-shuffle-floor (not the verdict) ranges 1.45-3.13 across cells -- weak and not
tied to group size either.

### Null (size1) vs signal (size4-5) call, per cell -- CAVEAT n=1 for size1

| window | ARROW z call | CLOCK tau call | SPLIT P call |
|---|---|---|---|
| first | UNSTABLE (signs differ, -4.40 vs +3.21) | STABLE DISAGREEMENT (606 vs 229h) | IDENTICAL (0.500 = 0.500, float noise only) |
| middle | UNSTABLE (+3.28 vs -2.99) | STABLE DISAGREEMENT (844 vs 306h) | IDENTICAL |
| last | UNSTABLE (+4.63 vs -2.52) | STABLE DISAGREEMENT (240 vs 475h, direction flips vs the other two windows) | IDENTICAL |

No formula gives a *consistent* null-vs-signal separation across all three windows.
Arrow disagrees in sign every window (UNSTABLE, as defined). Clock disagrees in
magnitude every window (STABLE DISAGREEMENT) but the direction of the disagreement
flips at the last window -- not a stable group-size effect, a real number that doesn't
hold a consistent story. Split is identical everywhere by construction. **This is the
honest reproduction, with three formulas instead of one, of DRYAD_SWEEP's own finding:
the paper's synchrony effect (singles/pairs fail, quintets sync) does not show up as a
directional or magnitude signal in any of the three formulas here** -- consistent with
DRYAD_SWEEP's recursive-gradient result on the same data (no mouse cleared its own
shuffle floor).

## 2. ANTS -- record does NOT carry what was asked for; logged, not hidden

**Blocker, found and reported, not swept past:** the fetched public files for
dryad.4b92t21 do not contain raw per-time-bin activity traces. `Doering_et_al_2019_
Temnothorax_all_time_series_scores.txt` is **one row per colony x trial** (18 colonies
x 6 trials, 108 rows) of already-computed per-trial summary statistics (Period_wavelet,
Synchrony, Average_activity, ...) -- not a time series inside a trial. The isolated
queen/worker files (`experiment2_isolated_queens.csv`, `experiment2_isolated_workers.csv`)
are **one scalar per colony**, n=6 each (Proportion_of_time_active etc.) -- fully
cross-sectional, zero repeated measurements, no time axis of any kind.

Consequence, stated directly: **THE ARROW, THE CLOCK, and THE SPLIT cannot run on the
isolated-queen/isolated-worker files at all** -- all three formulas require >=2
time-ordered points to form a single lag, and these files provide one point per colony.
This is UNCOMPUTABLE by construction, not a fit that failed.

### In-nest: best available ordered series is Synchrony-by-trial (n=6 points/colony, trial index as the only order)

Thin and flagged as such. Six groups of three colonies (alphabetical, 18/3=6):

| group | colonies | ARROW z (median, IQR, n=3) | CLOCK tau_trials (median, IQR, n=3) | n divergent clock/3 |
|---|---|---|---|---|
| 1 | A10,A11,A18 | -2.11 (IQR 0.05) | -12.80 (IQR 5.64) | 3/3 |
| 2 | A5,A7,A8 | +0.81 (IQR 1.02) | +5.12 (IQR 1.97) | 3/3 |
| 3 | A9,D10,D13 | -1.98 (IQR 0.11) | -6.48 (IQR 3106.4) | 1/3 |
| 4 | D15,D16,D17 | -2.09 (IQR 0.54) | -16.65 (IQR 49.70) | 2/3 |
| 5 | D4,D8,D9 | -1.05 (IQR 1.10) | +7.33 (IQR 3.18) | 3/3 |
| 6 | R10,R5,R8 | -1.07 (IQR 0.50) | -7.41 (IQR 7.30) | 3/3 |

15 of 18 colonies (83%) have a DIVERGENT clock fit (bootstrap sd > \|tau\|) at n=6
points -- the formula does not have enough data to fit an exponential here, reported
as a real finding: **the clock formula needs more than 6 ordered points to be
trustworthy**, seen identically in the yeast record's own divergent before-window fit.
ARROW at n=6 is limited to k=1-2 by construction; z values (-2.5 to +1.0, shuffle-floor
based, not the verdict) show no consistent sign across groups. SPLIT could not be
computed for any of the 18 colonies: naive peak detection needs >=5 points of margin
per side and a real cycle structure that a 6-point summary-score series does not have
-- logged per-colony as `n_peaks_found=0 or 1, formula uncomputable`, not silently
skipped (18 rows in the error table, one per colony).

### Isolated queen / isolated worker controls (the null beside the in-nest signal)

| | n colonies | median Proportion_of_time_active | IQR | ARROW/CLOCK/SPLIT |
|---|---|---|---|---|
| isolated queens | 6 | 0.293 | 0.155 | UNCOMPUTABLE (cross-sectional, no time axis) |
| isolated workers | 6 | 0.923 | 0.142 | UNCOMPUTABLE (cross-sectional, no time axis) |
| in-nest (pooled Synchrony, all 18 colonies x 6 trials, from DRYAD_SWEEP) | 108 | 0.039 (mean, DRYAD_SWEEP) | -- | thin ordered series only, see above |

The null-vs-signal contrast in this record is real and measured (queens mostly
inactive, workers mostly active, colony-level synchrony low but nonzero) but it lives
entirely in **descriptive numbers**, not in any of the three formulas -- the isolated
files have no lag to test, and the in-nest file's only orderable axis (trial 1-6) is
too short for the clock or split to say anything trustworthy. Same three-way call as
the mice: **UNSTABLE/UNCOMPUTABLE, not a clean AGREE or a clean signal**, on every
cell that could be attempted, and flatly UNCOMPUTABLE on the two cells (isolated
queens, isolated workers) that could not.

## 3. ERRORS, DIVERGENT FITS, UNCOMPUTABLE CELLS -- full table, not a footnote

Full machine-readable list: `mice_ants_pooled.json` (`mice_error_rows`, 21 rows) and
`ants_results.json` (per-colony `errors` list, 18 SPLIT-uncomputable rows + 2
isolated-file UNCOMPUTABLE-all-three rows).

### Mice: 21 divergent clock fits out of 150 mouse-window clock comparisons (14%)

19 on the forward (raw-trace) side, 3 on the backward (message-unit) side (1 window --
mouse 14, size4-5, middle -- divergent on BOTH sides at once). Every one is a real
fit, not a crash: `fit_exp_decay` always returned a finite tau, but the bootstrap sd
exceeds the tau's own magnitude, meaning the exponential decay is not distinguishable
from flat noise over these window lengths -- exactly the failure mode the yeast run's
before-window message-unit clock fit showed (tau=250,766s vs bootstrap sd=517,580s).
Full list of the 21 rows is in `mice_ants_pooled.json`; three representative extremes:

| mouse | bucket | window | fwd tau (h) | fwd boot sd (h) | bwd tau (h) | bwd boot sd (h) |
|---|---|---|---|---|---|---|
| 31 | size2-3 | middle | -7901.96 | **55,403.22** (largest fwd sd, 7.0x \|tau\|) | 34.44 | 2.77 |
| 18 | size4-5 | middle | 587.97 | 160.26 | -5769.04 | **47,791.71** (largest bwd sd, 8.3x \|tau\|) |
| 14 | size4-5 | middle | 995.84 | 7754.82 | 185.18 | 265.87 (both sides divergent at once) |

No NaN and no exceptions anywhere in `mice_results.json` -- every one of the 75
mouse-windows produced a complete forward+backward record; the 21 divergences are
finite-but-untrustworthy numbers, not missing ones.

### Error-bar sizes, as a column, largest and smallest named (mice, all 75 mouse-windows)

| quantity | smallest boot sd | largest boot sd | ratio largest/smallest |
|---|---|---|---|
| arrow forward (raw trace) | 0.0112 (mouse 18, size4-5, first) | 0.142 (mouse 10, size1, last) | 12.6x |
| clock forward tau (h) | 5.10h (mouse 31, size2-3, last) | 55,403h (mouse 31, size2-3, middle -- same mouse, divergent window) | 10,864x |
| clock backward tau (h) | 0.603h (mouse 27, size4-5, last) | 47,792h (mouse 18, size4-5, middle) | 79,257x |
| split P | 0.114 (mouse 13, size2-3, first) | 0.531 (mouse 24, size2-3, last) | 4.7x |

The clock's error bars span four to five orders of magnitude between its best window
and its worst, in the SAME mouse in one case (31) -- the formula is not uniformly
reliable across windows even for one individual; arrow and split stay within an order
of magnitude across all 75.

### Ants: 15/18 in-nest colonies DIVERGENT on clock (83%), 18/18 UNCOMPUTABLE on split, 12/12 isolated colonies UNCOMPUTABLE on all three

| quantity | smallest boot sd | largest boot sd |
|---|---|---|
| arrow (Synchrony-by-trial, n=6) | 1.54e-6 (colony D8) | 6.76e-5 (colony A7) -- 44x range |
| clock tau_trials | 5.91 trials (colony A8) | 1061.0 trials (colony D13) -- 179x range |

D13's clock fit (tau=-5909 trials, boot sd=1061) is technically under my "sd>\|tau\|"
divergence cutoff (ratio 0.18) but still carries a >1000-trial-unit error bar on a
6-trial series -- reported as thin-but-finite rather than divergent, not rounded up
or down to make a cleaner story.

## 4. Mice vs ants vs yeast, per cell (sign kept, no labels)

| cell | yeast (THREE_ON_YEAST) | mice (this run) | ants (this run) |
|---|---|---|---|
| ARROW sign pattern | -,-,+ (before/during/after), flips exactly under reversal | flips every window, every bucket, no group-size pattern | flips across colonies (mostly negative, 2-3 positive), no in-nest-vs-isolated comparison possible (isolated uncomputable) |
| CLOCK tau vs period | 14-24x period (688-1223s / 48.7s) | forward 10-40x period (230-925h / 24h); backward 1.5-5x period (35-125h / 24h) -- same forward>backward ordering as yeast | no established period in trial units -- tau_trials (5-1061 trials) not convertible to a period ratio, reported in native units only |
| CLOCK fit reliability | 1 of 3 window fits DIVERGENT (before-window message-unit, sd 2.06x tau) | 21 of 150 (14%) DIVERGENT, concentrated on the forward/raw-trace side | 15 of 18 (83%) DIVERGENT -- worst of the three records, driven by n=6 |
| SPLIT P | 0.500 exactly (telescoping construction) | 0.500 exactly, all 75 windows (same construction) | UNCOMPUTABLE, all 18 colonies (no peaks in a 6-point series) |
| Null vs signal, same record | n/a (yeast has no null/signal group, one continuous record) | UNSTABLE (arrow), STABLE DISAGREEMENT w/ flipping direction (clock), IDENTICAL (split) -- no clean separation by group size | descriptive-only separation (queens 0.29 vs workers 0.92 proportion-active); none of the three formulas can even attempt the isolated arm |

Read straight: the SPLIT formula's P=0.500 is now confirmed a **construction artifact
of the D=cumsum(crossing) definition**, not a biological number, on two of three
records (yeast, mice) and inapplicable on the third (ants) for lack of any cycle
structure to build D from. The CLOCK formula's reliability degrades sharply with
series length -- clean on the ~1500-point yeast trace's synchrony window, patchy on
mice's ~2700-point thirds, mostly broken on ants' 6-point summary series. That
degradation curve is itself the honest cross-record finding, not a side note.

## Tries

Mice: 25 mice x 3 windows x 2 chains = 150 mouse-window-chain runs. Arrow: 12 k-grid
values x 200 shuffle-floor draws x 75 forward cells = 180,000 shuffle draws, +300
bootstrap draws x 75 = 22,500 bootstrap draws (forward); backward arrow: up to 3 k
variants x 300 bootstrap x 75 = ~67,500 bootstrap draws. Clock: 300 bootstrap x 150
(75 forward + 75 backward) = 45,000 bootstrap draws. Split: 300 bootstrap + 200
shuffle-floor x 75 forward cells = 22,500 + 15,000 = 37,500 draws. Mice total:
approx 180,000 + 22,500 + 67,500 + 45,000 + 37,500 = **352,500 resample/shuffle draws**,
150 formal point estimates with a call each (arrow sign-match, clock AGREE/STABLE
DISAGREEMENT/DIVERGENT, split identical-by-construction).

Ants: 18 colonies x (arrow: 2 k x 200 shuffle + 300 bootstrap; clock: 300 bootstrap) =
18 x (400 + 300 + 300) = 18,000 draws; split attempted and logged uncomputable for
all 18 (0 draws, no fit to bootstrap). Isolated queens/workers: 0 draws (UNCOMPUTABLE
by construction, no fit attempted). Ants total: **18,000 draws**, 18 arrow + 18 clock
formal point estimates (36), plus 18+2 UNCOMPUTABLE/error rows logged.

Grand total this pass: **370,500 resample/shuffle draws**, 186 formal point estimates
with a direct call, 21 (mice) + 18 (ants split) + 2 (ants isolated, all-three) = 41
explicit error/uncomputable rows kept in the same tables as the results, not dropped.

## Files

- Report: `~/bones-forge/parallax/THREE_ON_MICE_ANTS_20260930.md` (this file)
- Instrument (reused, unedited): `parallax/out/three_on_three/core.py`
- New scripts: `parallax/out/three_on_three/mice_ants_pipeline.py` (per-mouse/per-colony
  forward+backward chains), `parallax/out/three_on_three/aggregate_mice_ants.py`
  (pooling, verdict calls)
- Raw output: `parallax/out/three_on_three/mice_results.json`,
  `parallax/out/three_on_three/ants_results.json`,
  `parallax/out/three_on_three/mice_ants_pooled.json`
- Source data (already fetched, DRYAD_SWEEP_20260930.md): `parallax/out/dryad_sweep/
  mice_social_sync/`, `parallax/out/dryad_sweep/ant_tempo/`
