# THE GAP PER MEDIUM -- THIRD_RUNG_20260928.md Sec60, 2026-10-01

Wayfinder: "one of your measurements was from two different substrates. I don't think the darkwave
travels the same speed in every substrate. A regular wave wouldn't." A regular wave's speed belongs
to the medium (air 343 m/s, water 1480 m/s, steel 5900 m/s; light slows in glass). THE_CLOCK_GAP
(Sec58) found the clock-minus-arrow (G_a) and clock-minus-split (G_s) gaps run the SAME SIGN in 38
of 41 calls but are too wide to be ONE number overall (chi2/dof 4.83 and 1.63), loosely ordered by
substrate. This file asks the next question directly, no expectation written first: is the gap ONE
number PER SUBSTRATE, and does any property of the medium itself order it?

**n = 4 substrates (fermentation, radio, chip, mouse), ~14 records, said plainly: this is thin.**
Every substrate-level ordering test below enumerates the exact 24 orderings of 4 items (4! = 24) --
no asymptotic p-value anywhere in this section. Record-level tests (9-11 records) use a stated
10,000-draw Monte Carlo permutation, explicitly NOT exact (11! is too large), never confused with
the substrate-level exact fractions. No shuffle judges the structural claim (one-number-per-medium
is read off chi-square, not a null distribution); shuffle/permutation is used ONLY for the ordering
(Spearman) tests, per the standing rule. Script: `out/the_middle/gap_per_medium.py` (numpy only,
reuses `clock_gap_results.json` and `reverse_gradient_results.json` verbatim). Raw output:
`out/the_middle/gap_per_medium_results.json`.

## 1. Per-substrate gap: is each substrate ONE number inside itself?

Pooling every resolved (record, chain) row from `clock_gap_results.json` by substrate (fermentation
= yeast during+whole; radio = horn at-horn+whole; chip = buzz 80/100/116, echo 20/2000us [both
OPEN, no gap resolved], arisen-carry [OPEN, no gap resolved], GHZ tau_third/arb_1; mouse = size-1,
size-4/5), weighted mean (1/err^2) and within-substrate chi-square:

| substrate | n rows | G_a mean | G_a reduced chi2 | verdict | G_s mean | G_s reduced chi2 | verdict |
|---|---|---|---|---|---|---|---|
| fermentation | 5 | +1.340 +/- 0.199 | 1.88 | BORDERLINE | +1.454 +/- 0.226 | 2.09 | BORDERLINE |
| radio | 5 (G_a) / 4 (G_s) | +0.829 +/- 0.150 | 3.12 | NOT ONE NUMBER | +2.698 +/- 0.563 | **0.09** | **ONE NUMBER** |
| chip | 8 (G_a) / 6 (G_s) | +1.143 +/- 0.109 | 7.62 | NOT ONE NUMBER | +2.069 +/- 0.257 | 2.23 | BORDERLINE |
| mouse | 4 | +1.247 +/- 0.257 | 7.63 | NOT ONE NUMBER | +2.135 +/- 0.591 | **1.08** | **ONE NUMBER** |

(These reduced-chi2 numbers reproduce THE_CLOCK_GAP Sec3's substrate table exactly -- no re-fit,
same weighted-mean/chi-square machinery, same rows.) **Read: G_a is not one number in any single
substrate** (best case, fermentation, still 1.88 -- borderline at best). **G_s comes much closer:
radio and mouse are each cleanly ONE NUMBER inside themselves** (reduced chi2 0.09 and 1.08); chip
is borderline (2.23); fermentation is borderline (2.09). So the honest answer to "is the gap one
number per medium" is: **for G_s, in 2 of 4 substrates, yes -- radio and mouse each hold one number
inside themselves even though the four substrate numbers differ from each other** (1.45 to 2.70).
For G_a, no substrate clears the bar.

## 2. The medium's properties, per record (read from the source files, not guessed)

Beat period = each record's own hop-0 arrow-lag `k_native` (native units); sample interval =
`k_native / k` (time or shot-count per sample); length = `n` (samples) and `n / k` (beats); noise
floor = `resid_var_frac` at the DALET-ascent terminal hop (`reverse_gradient_results.json`, same
"record's own" fixed point `FIXED_POINTS_20260930.md` uses); amplitude = sqrt(hop-0 residual
variance), native units, dimensionful and NOT unified across substrates (flagged, not silently
converted). Temperature and coupled-unit count are given directly (task brief), not measured here.

| record | period (native) | dt (native) | n samples | n beats | noise floor (resid_var_frac @ DALET terminal) | source |
|---|---|---|---|---|---|---|
| yeast during | 66.81 s | 1.31 s | 460 | 9.02 | 5.39e-7 (hop 3) | reverse_gradient_results.json |
| yeast whole | 34.06 s | 1.31 s | 1531 | 58.88 | 2.37e-6 (hop 8) | reverse_gradient_results.json |
| horn at-horn | 25.74 s | 0.330 s | 1423 | 18.24 | 0.494 (hop 5) | reverse_gradient_results.json |
| horn whole | 25.08 s | 0.330 s | 29226 | 384.55 | 0.0334 (hop 8) | reverse_gradient_results.json |
| buzz seat80 | 75.0 shots | 1.0 shot | 4000 | 53.33 | 0.00159 (hop 6) | reverse_gradient_results.json |
| buzz seat100 | 80.0 shots | 1.0 shot | 4000 | 50.0 | 0.00084 (hop 5) | reverse_gradient_results.json |
| buzz seat116 | 80.0 shots | 1.0 shot | 4000 | 50.0 | 0.000376 (hop 3) | reverse_gradient_results.json |
| echo 20us | OPEN (A=0 exactly, no peaks) | 20 us (the look-gap) | 1500 | -- | OPEN (no DALET run) | THREE_ON_THREE.md |
| echo 2000us | OPEN | 2000 us (the look-gap) | 1500 | -- | OPEN | THREE_ON_THREE.md |
| arisen-carry (Marrakesh) | OPEN (no bracketing decay) | 20 us (look-gap) | -- (74 qubits, a population, not a time-series length) | -- | OPEN | PLACED_VS_ARISEN.md |
| GHZ tau_third | 6 angle-steps | 1 angle-step | 24 | 4.0 | OPEN ("NO FIXED POINT IN 3 HOPS") | GHZ_THROUGH_THREE.md |
| GHZ arb_1 | 18 angle-steps | 1 angle-step | 24 | 1.33 | missing (fixed point reached but resid_var_frac not tabulated there) | GHZ_THROUGH_THREE.md |
| mice size-1 | 20 h | 0.25 h | 8192 | 102.4 | 0.741 (hop 8) | reverse_gradient_results.json |
| mice size-4/5 | 0.5 h | 0.25 h | 8192 | 4096.0 | 0.929 (hop 4) | reverse_gradient_results.json |

**4 missing/OPEN period cells, 2 missing noise-floor cells, 1 missing length cell (arisen-carry, a
population not a series) -- reported as rows, not dropped, not guessed.**

Temperature (given, not measured here): fermentation ~295 K (room), radio ~295 K (room), chip
~0.04-0.07 K (IBM dilution fridge; 0.05 K midpoint used), mouse ~310 K (37 C). Coupled units: radio
= 1 (single horn/detector), chip = 1 (one seat per record; GHZ's 3-qubit entanglement not pooled
in), yeast = a population (no exact colony count on file -- **missing, not guessed**), mouse = mixes
size-1 and size-4/5 records (substrate-level count is genuinely ill-defined, left as two records,
not collapsed to one number -- **missing**).

## 3. Per-substrate medium properties (mean of that substrate's own records) and ordering

| substrate | beat period | sample interval | n samples | n beats | noise floor | temperature (K) | coupled units |
|---|---|---|---|---|---|---|---|
| fermentation | 50.4 s (n=2) | 1.31 s (n=2) | 995.5 (n=2) | 33.95 (n=2) | 1.45e-6 (n=2) | 295.15 | missing (population) |
| radio | 25.4 s (n=2) | 0.330 s (n=2) | 15324.5 (n=2) | 201.4 (n=2) | 0.264 (n=2) | 295.15 | 1 |
| chip | 51.8, MIXED UNITS: shots + angle-steps (n=5) | 0.625, MIXED UNITS: shots + angle-steps + us (n=8) | 2149.7 (n=7, excl. arisen-carry) | 31.7 (n=5) | 0.000935 (n=3, buzz only) | 0.05 | 1 |
| mouse | 10.25 h (n=2) | 0.25 h (n=2) | 8192.0 (n=2) | 2099.2 (n=2) | 0.835 (n=2) | 310.15 | missing |

**Chip's own "beat period" and "sample interval" mix three incommensurate units inside one
substrate** (shots for buzz, angle-steps for GHZ, microseconds for arisen-carry/echo) -- itself a
finding: the chip substrate does not have one native clock unit the way fermentation (seconds),
radio (seconds) and mouse (hours) each do. The chip numbers above are reported anyway (as asked),
flagged, not smoothed over.

**Exact ordering test, n=4 substrates, all 24 orderings enumerated, against each substrate's G_a
and G_s weighted mean (Section 1):**

| property | rho vs G_a | exact fraction (of 24) | rho vs G_s | exact fraction (of 24) |
|---|---|---|---|---|
| beat period | 0.00 | 24/24 = 1.000 | -0.60 | 10/24 = 0.417 |
| sample interval | +0.40 | 18/24 = 0.750 | -0.80 | 8/24 = 0.333 |
| n samples (record length) | -0.80 | 8/24 = 0.333 | **+1.00** | **2/24 = 0.083** |
| n beats | 0.00 | 24/24 = 1.000 | +0.60 | 10/24 = 0.417 |
| noise floor | -0.40 | 18/24 = 0.750 | +0.80 | 8/24 = 0.333 |
| amplitude (rms, mixed units) | +0.40 | 18/24 = 0.750 | -0.80 | 8/24 = 0.333 |
| temperature | 0.00 | 24/24 = 1.000 | +0.60 | 10/24 = 0.417 |

**No property orders G_a at all** (best case 8/24 = 0.333, three-way tie). **Record length in
samples (n) orders G_s perfectly**: fermentation (995.5) < chip (2149.7) < mouse (8192.0) < radio
(15324.5) matches G_s's own order (1.45 < 2.07 < 2.14 < 2.70) exactly, rho = +1.00. **This is the
best possible result obtainable with n=4** -- exactly 2 of the 24 orderings (the identity and its
mirror) ever reach |rho|=1, so 2/24 = 0.083 is the floor, not a small number by any conventional
bar (it is NOT below 0.05). Reported plainly: n's ordering of G_s is real and exact within this
data, but n=4 substrates cannot make it statistically tight -- the strongest honest claim here is
"consistent with," not "proven."

Record-level check (9-11 records with both a resolved gap and the property; 10,000-draw MC,
explicitly not exact): none of the five properties order G_a or G_s at the record level (observed
rho 0.08-0.45 in magnitude, MC fractions 0.18-0.83, all well above any conventional bar). The
record-length ordering that appeared cleanly at the substrate level (pooled to 4 numbers) does NOT
survive down at the individual-record level (rho = -0.23 for G_s vs n_samples, MC fraction 0.55) --
**the substrate-level agreement is a pooling effect, not something visible record by record.**

## 4. The wave-speed form: does G_s scale as a power law with a medium property?

If the gap were a travel-time difference (gap = distance / speed), |G_s| should scale as a power
law in beat period, sample interval, or length-in-beats across records. Log-log OLS slope +/- error
(record-level, using |gap|, one value per record = mean across its own chains):

| property | n | slope | slope err | r^2 |
|---|---|---|---|---|
| beat period vs G_a | 11 | -0.167 | 0.234 | 0.054 |
| beat period vs G_s | 9 | +0.198 | 0.215 | 0.108 |
| sample interval vs G_a | 11 | -0.492 | 0.501 | 0.097 |
| sample interval vs G_s | 9 | +0.030 | 0.497 | 0.001 |
| n beats vs G_a | 11 | +0.141 | 0.158 | 0.080 |
| n beats vs G_s | 9 | -0.179 | 0.191 | 0.112 |

**Every slope is consistent with zero within its own error** (all |slope| < 1 sigma from 0), and
r^2 never clears 0.11. **No wave-speed power-law form (gap ~ property^slope) is supported by this
data** -- not for beat period, not for sample interval, not for length-in-beats, against either
gap. This is a clean null, not a missing test: the travel-time-difference hypothesis, tested the
most direct way available, does not show up.

## 5. Plain words

**Is the hole in the clock one number per medium?** Partially, for G_s only: **radio and mouse are
each cleanly one number inside themselves** (reduced chi2 0.09 and 1.08); fermentation and chip are
borderline (2.09, 2.23). **G_a is not one number in any substrate** (best case 1.88, still
borderline). **What orders the media?** Of seven properties tested (beat period, sample interval,
record length, length-in-beats, noise floor, amplitude, temperature), **only record length in
samples orders G_s exactly at the substrate level** (fermentation < chip < mouse < radio, rho=+1.00)
-- but this is the best possible outcome obtainable with n=4 (2 of 24 orderings, exact fraction
0.083, not below any conventional bar), and it does **not** reproduce at the record level (rho
drops to -0.23, MC fraction 0.55) -- **a pooling artifact, not a property of individual records.**
No property orders G_a in either test. The wave-speed power-law form (gap ~ period^slope) is a
clean null: every slope tested is consistent with zero. **Read honestly: Wayfinder's frame ("a
wave's speed belongs to the medium") is the right SHAPE for what THE_CLOCK_GAP already found --
G_s really does look more like a per-medium number than a universal one, two of four substrates
land it cleanly -- but nothing on file yet says WHICH property of the medium sets that number. n=4
substrates is too thin to settle it either way; the record-length result is worth re-testing the
next time a fifth substrate's clock is added, not worth calling found.**

## Tries

8 weighted-mean/chi-square "one number per substrate" tests (4 substrates x {G_a, G_s}). 14
substrate-level ordering tests (7 properties x {G_a, G_s}), each enumerating all 24 orderings of
n=4 EXACTLY -- **336 total orderings enumerated**, zero asymptotic p-values. 10 record-level
ordering tests (5 properties x {G_a, G_s}), each a 10,000-draw Monte Carlo permutation, stated as
approximate -- **100,000 total permutation draws**, explicitly not exact. 6 log-log power-law fits
(3 properties x {G_a, G_s}). **38 total direct calls this pass.** No shuffle used to judge the
structural (one-number) claim; shuffle/permutation used only for the seven-property, ten-record
ordering tests, per the standing rule.

## Files

- Report: `~/bones-forge/parallax/GAP_PER_MEDIUM_20261001.md` (this file)
- New script: `parallax/out/the_middle/gap_per_medium.py` (numpy only)
- New raw output: `parallax/out/the_middle/gap_per_medium_results.json`
- Reused, unedited: `parallax/out/the_middle/clock_gap_results.json` (every G_a/G_s cell),
  `parallax/out/reverse_gradient/reverse_gradient_results.json` (period, dt, n, noise floor for 9
  records)
- Read by hand, cited inline, nothing recomputed: `THREE_ON_THREE_20260930.md` (echo properties),
  `GHZ_THROUGH_THREE_20260930.md` (GHZ tau_third/arb_1 properties), `PLACED_VS_ARISEN_20260930.md`
  (arisen-carry properties)
