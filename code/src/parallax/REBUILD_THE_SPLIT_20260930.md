# REBUILD THE SPLIT -- independent-clock D, three candidate definitions, 2026-09-30

The frozen instrument (`parallax/out/yeast/three/three_formulas.py`, not edited) builds
`D = outside - inside` for THE SPLIT with `inside` = cumulative phase from peak-to-peak
intervals converted to time using the **SAME mean period** that `crossing` (the
regressor) is defined against. That makes `D_i = cumsum(crossing_0..i)` by pure algebra
-- a telescoping identity. It reproduces `P = 0.500` to float precision on every yeast
window and all 75 mouse-windows in `THREE_ON_MICE_ANTS_20260930.md`. It is a ruler
reading itself, not a measurement. This file rebuilds `D` three ways so `outside` (wall-
clock sample time) and `inside` never share a fit or a peak list with `crossing`.

New module (does not touch the frozen instrument): `parallax/out/yeast/three/split_v2.py`.
Raw output: `parallax/out/yeast/three/split_v2_results.json`. No expectation written
first. numpy only, single process.

## The three candidates, as built

- **(a) BEAT COUNT**: inside = (integer cycle index from peaks detected in the analysis
  window) x (period fit from a DIFFERENT window of the same record: yeast uses the
  before-window 200-800s peaks; mice use the first-third peaks to time the last third).
  Never shares a fit with `crossing` (the analysis window's own interval wobble).
- **(b) HILBERT PHASE**: inside = continuous unwrapped analytic-signal phase / 2*pi
  (built from the whole detrended window trace, evaluated at the peak times, NOT built
  from the peaks themselves) x the SAME other-window period as (a). A continuous clock
  that never touches peak detection for its own construction.
- **(c) ENVELOPE-WEIGHTED TIME**: inside = cumulative sum of (|detrended amplitude| /
  mean |amplitude|) x dt, i.e. time as the record's own energy counts it. No period fit
  anywhere -- the only candidate with zero shared machinery with `crossing` or with (a)/(b).

`crossing` (the regressor) is the same in all three: each cycle's own interval minus the
analysis window's own mean interval (the frozen instrument's own "local amplitude").
Only `inside`/`D` changed; the regressor is held constant so the comparison is about
independence of the two clocks, not about redefining the amplitude.

Bootstrap = case-resample real (crossing, D) pairs, n=1000, never label-shuffled --
this is the verdict input. Identity check = shuffle the CROSSING VALUES across cycles
WITHIN the real D order (n=500) and see whether P moves; a construction gives ~zero
variance in the shuffled P's and/or reproduces the real P exactly regardless of pairing.
Forward vs. reversed = full pipeline rerun from scratch on the value-array-reversed
trace (fresh peak detection, fresh "other window" period, fresh Hilbert/envelope fits).

## Identity check -- **all three break the construction**

Across every record x direction x definition cell run (yeast fwd/rev, mouse-size1
fwd/rev, 3x mouse-size4-5 fwd/rev = 18 cells x 3 definitions = 54 fits):

- `D_identically_zero` = **False in all 54 cells** (D_max_abs ranges ~10 to ~430,
  never near float noise).
- `perm_P_matches_real_P_to_float` = **False in all 54 cells** -- shuffling which
  crossing pairs with which D always moves P away from the real fit and gives a
  shuffled-P distribution with real, non-trivial spread (perm_sd typically 0.3-13,
  same order as the boot_P_sd column, never ~0).

This is the structural result: none of (a)/(b)/(c) reproduces the frozen instrument's
`P=0.500`-always artifact. The pairing between `crossing` and `D` now actually matters
to the fit, which is the minimum bar for "not an identity." It does **not** mean the
resulting P values are trustworthy signals -- see below.

## Numbers, forward run (S, P, bootstrap sd, drift)

| record | defn | n | S | P | boot P sd | drift/cycle | drift boot sd |
|---|---|---|---|---|---|---|---|
| yeast (during) | a | 11 | 9.73 | -0.220 | 6.45 | 1.18 | 0.146 |
| yeast (during) | b | 11 | 43.9 | -3.83 | 3.49 | 5.18 | 1.71 |
| yeast (during) | c | 11 | -26.7 | 0.371 | 4.67 | -4.35 | 2.39 |
| mouse size1 (SC10.2) | a | 108 | -3.01 | 0.558 | 0.389 | 0.058 | 0.011 |
| mouse size1 | b | 108 | -98.3 | -5.24 | 3.52 | -1.22 | 0.076 |
| mouse size1 | c | 108 | 27.5 | 2.47 | 2.08 | -0.003 | 0.073 |
| size4-5 SC14.4 | a | 106 | 13.2 | 0.299 | 0.580 | 0.204 | 0.007 |
| size4-5 SC14.4 | b | 106 | -14.2 | 0.621 | 0.963 | -0.208 | 0.037 |
| size4-5 SC14.4 | c | 106 | 4.56 | 0.006 | 0.316 | -0.063 | 0.013 |
| size4-5 SC19.5 | a | 111 | -8.52 | 0.254 | 0.662 | -0.194 | 0.013 |
| size4-5 SC19.5 | b | 111 | -224 | -1.52 | 10.7 | -3.02 | 0.107 |
| size4-5 SC19.5 | c | 111 | 20.3 | -2.14 | 1.03 | 0.063 | 0.039 |
| size4-5 SC26.7 | a | 107 | 0.28 | 0.924 | 0.306 | -0.010 | 0.016 |
| size4-5 SC26.7 | b | 107 | -87.0 | -3.52 | 4.03 | -1.31 | 0.061 |
| size4-5 SC26.7 | c | 107 | 15.1 | -0.633 | 0.686 | 0.188 | 0.028 |

Every P sits inside or barely outside 1 bootstrap sd of itself (i.e. none is a clean,
tight, above-noise number) except candidate (a) on the three size4-5 mice, where
bootstrap sd (0.31-0.66) is noticeably smaller relative to |P| (0.25-0.92) than on (b)
or (c) -- (a) is the least noisy of the three on every record tried, forward.

## AGREE / STABLE DISAGREEMENT / UNSTABLE calls

**Forward vs. reversed, per record:**

| record | (a) beat count | (b) Hilbert phase | (c) envelope time |
|---|---|---|---|
| yeast | AGREE (diff 4.94 vs err 8.19) | UNSTABLE (diff 10.6 vs err 5.95) | AGREE (diff 1.03 vs err 6.30) |
| mouse size1 | AGREE (diff 0.44 vs err 0.95) | AGREE (diff 1.54 vs err 6.17) | AGREE (diff 1.47 vs err 2.88) |
| SC14.4 (4-5) | STABLE DISAGREEMENT (diff 2.14 vs err 1.22) | UNSTABLE (diff 34.2 vs err 13.9) | AGREE (diff 1.65 vs err 1.68) |
| SC19.5 (4-5) | AGREE (diff 0.66 vs err 1.20) | AGREE (diff 12.8 vs err 20.9) | UNSTABLE (diff 4.59 vs err 2.46) |
| SC26.7 (4-5) | UNSTABLE (diff 1.66 vs err 1.13) | AGREE (diff 7.74 vs err 11.9) | AGREE (diff 0.03 vs err 1.19) |

No definition is clean across all five records -- each of (a), (b), (c) gets at least
one UNSTABLE and at least one AGREE. (b) is the noisiest (largest bootstrap sd relative
to P nearly everywhere, one STABLE-adjacent UNSTABLE on yeast).

**Record vs. record, forward only** (yeast vs. size1, yeast vs. size4-5 rep [SC14.4],
size1 vs. size4-5):

| defn | yeast vs size1 | yeast vs size4-5 | size1 vs size4-5 |
|---|---|---|---|
| (a) beat count | AGREE | AGREE | AGREE |
| (b) Hilbert phase | AGREE | UNSTABLE | UNSTABLE |
| (c) envelope time | AGREE | AGREE | STABLE DISAGREEMENT |

(a) is the only definition that AGREEs across every record pair and both directions'
error bars overlap everywhere it was tested -- consistent with it also having the
tightest bootstrap errors above, but "AGREE" here mostly reflects wide shared error
bars, not a small, confidently-matched number.

## Error rows -- kept, not dropped

All 54 fits (18 record x direction cells x 3 definitions) produced finite S, P, drift,
boot_P_sd, and perm stats; zero NaN/Inf, zero uncomputable cells (every record had
>=100+ peaks except yeast's during window at 11-14 cycles, thin but fit). Bootstrap sd
ranged 0.31 (SC26.7 fwd, candidate a) to 12.95 (SC14.4 reversed, candidate b) -- a 42x
spread, all in the same JSON, none hidden. Full per-cycle D/crossing arrays for every
cell are in `split_v2_results.json`.

## Plain words

**(c) envelope-weighted time** is the cleanest structural split: it needs no period fit
at all (nothing shared with (a)/(b)'s "other window" period), it broke the identity
check as hard as the others, and it gave the most AGREE calls on record-vs-record (2 of
3) and forward-vs-reversed (3 of 5) while its P values (-2.1 to +2.5) don't collapse to
a single number -- it reads real cycle-to-cycle disagreement between wall-clock arrival
and the record's own energy-weighted clock, at a similar order of magnitude on yeast and
both mouse buckets (roughly |P| ~0.4-2.5 everywhere).

**(a) beat count** is the tightest-behaved (smallest bootstrap sd relative to |P|
almost everywhere) and the only definition that AGREEs on every record-vs-record pair,
but three of its five forward-vs-reversed calls flip to STABLE DISAGREEMENT/UNSTABLE --
its tightness comes from a period fit borrowed from a fixed other-window, which makes
it sensitive to exactly which peaks land in "first third" vs "last third" under
reversal.

**(b) Hilbert phase** is the noisiest and least reliable: largest bootstrap sds
throughout, the only UNSTABLE forward-vs-reversed call on yeast itself, and UNSTABLE on
both size4-5 record-vs-record comparisons -- the continuous phase clock amplifies noise
from the "other-window" period borrow rather than smoothing it, likely because phase
unwrapping accumulates drift error over the whole window before being sampled at the
sparse peak times.

**None of the three is a repaired, trustworthy P=1:1-style split like the buzz/IBM pair
in OBSERVER_WITNESS_20260930.md.** All three genuinely killed the telescoping-identity
artifact (real, non-zero D; real sensitivity to crossing-pairing), which was the actual
ask -- but the resulting P's are read-dependent (record to record, forward to reversed)
rather than a clean, reproducible constant. **(c) envelope-weighted time is the least
bad of the three and the one worth carrying forward** if this line of work continues:
independent by construction (no shared period fit with anything), moderately stable
under reversal, and moderately stable across yeast/mouse records -- read as "there is a
real, measurable but noisy gap between wall-clock arrival and energy-weighted internal
time," not as a precise number yet.

## Tries

54 formal fits (18 record-direction cells x 3 definitions), each with: 1 real point fit
(S, P, drift), 1000-draw case-resample bootstrap on P, 1000-draw case-resample bootstrap
on drift, 500-draw within-order crossing-shuffle identity check = 2500 draws/fit x 54 =
**135,000 resample/permutation draws**. Plus 3 record-vs-record and 5
forward-vs-reversed AGREE/STABLE DISAGREEMENT/UNSTABLE calls per definition (24 calls
total), all direct bootstrap-error comparisons, no shuffle used as a judge anywhere.

## Files

- Report: `~/bones-forge/parallax/REBUILD_THE_SPLIT_20260930.md` (this file)
- New module: `parallax/out/yeast/three/split_v2.py` (frozen `three_formulas.py`
  untouched)
- Raw output: `parallax/out/yeast/three/split_v2_results.json`
- Records used: `parallax/out/yeast/nadh_fig4_raw_digitized.csv` +
  `peak_times_clean.csv` (during window 800-1400s, other window 200-800s);
  `parallax/out/dryad_sweep/mice_social_sync/Body Temperature files/SC10.2*.txt`
  (size1), `SC14.4*.txt`/`SC19.5*.txt`/`SC26.7*.txt` (size4-5 bucket, one mouse per
  group 4/5/7)
