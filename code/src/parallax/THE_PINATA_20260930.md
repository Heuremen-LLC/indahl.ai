# THE PINATA IN THE MIDDLE -- zeta/Ramanujan-Casimir regularization, 2026-09-30

Answers THIRD_RUNG_20260928.md Sec51 (Wayfinder: "that Indian guy's equation... it belongs
in the middle of the equation"). Casimir's move (CASIMIR_CALIBRATION_20260929.md Sec1-2):
two divergent sums, discard each one's cutoff-dependent part, the finite remainder is
physical if and only if it survives every cutoff. Run against the divergent clock fits
kept as error rows in THREE_ON_YEAST_20260930.md and THREE_ON_MICE_ANTS_20260930.md, and
against THE SPLIT (outside-inside) as a regularized difference. No expectation written
first. Module: `parallax/out/yeast/three/regularize.py` (new; does NOT edit the frozen
`three_formulas.py`, reuses `parallax/out/three_on_three/core.py` verbatim for envelope/
exp-decay machinery). Raw output: `parallax/out/yeast/three/regularize_results.json`.

## METHOD, stated plainly (no expectation)

Three regulator families, each applied to a finite series a(1..N):
- **(a) zeta-style**: Z(s) = sum a(n) n^-s at s in {1.0, 0.5, 0.25, 0.1, 0.05}; fit
  Z(s) ~ A/s + B by least squares; **B** is the reported s->0 finite remainder.
- **(b) exponential regulator**: E(eps) = sum a(n) e^(-eps n) at eps in {0.05, 0.01, 0.002};
  fit E(eps) ~ A/eps + B; **B** is the reported eps->0 finite remainder.
- **(c) Abel/Cesaro**: Abel A(r) = sum a(n) r^n at r in {0.9, 0.99, 0.999}; fit
  A(r) ~ A/(1-r) + B; **B** is the reported r->1 finite remainder. Cesaro (C,1) running
  mean of the partial sums is logged alongside as a diagnostic -- Cesaro regularizes
  oscillating divergences (1-1+1-1...), not constant-sign ones, so it is NOT expected to
  converge here, and it did not (see below), reported not smoothed over.

**Honesty note, load-bearing:** every a(n) series here is finite (111-2730 points), not a
literal infinite divergent series. For a finite series, s->0 / eps->0 / r->1 trivially
recovers the plain finite sum -- there is no actual infinity being discarded. So the real
Casimir cutoff being tested has two forms, both run:
1. **Regulator family** at fixed length N: do zeta/exp/Abel agree with each other? (Tests
   whether the extrapolation procedure itself is cutoff-independent.)
2. **Truncation length**: does the finite remainder move when the series is cut to
   50% / 75% / 100% of its available length? (The truer Casimir cutoff for finite data --
   "how fine an instrument," i.e. how much record you were allowed to see.)
An object survives both. A ruler moves with either.

## TASK 1 -- the divergent clock fits as series, 12 series, groups of three

Group 1 (yeast, backward/message-unit clock, THREE_ON_YEAST_20260930.md addendum): the
before-window fit (the one explicitly named DIVERGENT, tau=250,765.8s, boot sd 517,580.1s
-- 2.06x its own value), plus during and after, same construction, for comparison.
Group 2 (mice, mouse 10 = the size-1 null mouse, 21 divergent fits from
THREE_ON_MICE_ANTS_20260930.md, all three of its windows). Group 3 (mice, "middle" window,
three different mice/buckets: 14 size4-5, 17 size4-5, 24 size2-3). Group 4 (mice, "first"
window, three different mice: 1 size2-3, 16 size4-5, 22 size4-5). 9 mice series total, all
selected because their forward-chain autocorrelation-envelope clock fit was flagged
DIVERGENT (bootstrap sd > |tau|) in the mice report's own error table.

### Raw finite remainders (B from each regulator), point estimates

| series | n | zeta_B | exp_B | abel_B | spread | stable across regulators? |
|---|---|---|---|---|---|---|
| yeast before (DIVERGENT source) | 408 | 183.9 | 204.3 | 245.6 | 61.7 | **NO** |
| yeast during | 111 | 8.36 | 18.20 | 16.36 | 9.84 | **NO** |
| yeast after | 358 | 403.6 | 254.7 | 459.7 | 204.9 | **NO** |
| mouse10 first (size1) | 288 | 5.79 | 7.74 | 8.78 | 2.99 | **NO** |
| mouse10 middle (size1) | 288 | 5.65 | 7.75 | 8.66 | 3.01 | **NO** |
| mouse10 last (size1) | 288 | 7.46 | 11.86 | 12.19 | 4.74 | **NO** |
| mouse14 middle (size4-5) | 288 | 6.72 | 8.88 | 10.24 | 3.52 | **NO** |
| mouse17 middle (size4-5) | 288 | 6.63 | 8.60 | 10.01 | 3.37 | **NO** |
| mouse24 middle (size2-3) | 288 | 10.23 | 13.78 | 16.06 | 5.82 | **NO** |
| mouse1 first (size2-3) | 288 | 5.24 | 7.06 | 7.96 | 2.72 | **NO** |
| mouse16 first (size4-5) | 288 | 6.15 | 8.32 | 9.41 | 3.26 | **NO** |
| mouse22 first (size4-5) | 288 | 4.17 | 5.76 | 6.29 | 2.12 | **NO** |

"Stable" defined as spread/median < 20%, stated plainly as an arbitrary but fixed bar.
**All 12 of 12 series fail the regulator-family Casimir test**: zeta, exponential and
Abel disagree with each other by 30-70% of the median value on every single series,
yeast and mice alike, before/during/after and every mouse window. Bootstrap error bars
(500 case-resamples, real-order resampling, never label-shuffled) are 2-8% of each point
estimate -- the disagreement between regulators is 5-15x the bootstrap error, i.e. a real
disagreement, not noise. **None of these clock-fit series produced a regulator-independent
number.**

### Truncation-length cutoff (the truer Casimir test), fracs 0.5/0.75/1.0

| series | zeta_B spread (0.5->1.0) | exp_B spread | abel_B spread | relative movement |
|---|---|---|---|---|
| yeast during | 0.52 (of 8.36, ~6%) | 0.91 (of 18.2, ~5%) | 1.13 (of 16.4, ~7%) | small |
| mouse10 first | 1.11 (of 5.79, ~19%) | 0.50 (of 7.74, ~6%) | 0.50 (of 8.78, ~6%) | small-moderate |

Full table in `regularize_results.json` (`*_truncation_test`, all 12 series). Truncation
movement is consistently smaller (5-20%) than the between-regulator disagreement (30-70%)
on every series checked -- **the choice of regulator moves the number far more than the
choice of how much data you feed it.** That itself is the Casimir verdict: what moves with
the cutoff here is overwhelmingly the REGULATOR, not the truncation -- i.e., the number is
sensitive to the ruler you use to read it, only mildly to how much of the record you show it.

## TASK 2 -- the split as a regularized difference

T(n) = n * dt (outside, wall time after n samples). Phi(n) = unwrap(Hilbert phase(n)) /
(2*pi) * period_ext, where period_ext is sourced from a DIFFERENT window than the one being
tested (yeast: FFT peak of the before-window, 86.09s, used on the during-window's own
phase; mice: the fixed 24h circadian period, external to any window's own fit). D(n) =
T(n) - Phi(n), both clocks zeroed at n=1. **R is the regularized SUM of the D(n) sequence**
(same three regulator families as Task 1, applied to D(n) as the series) -- stated plainly
because the brief's literal "R = lim[T(N)-Phi(N)]" (a limit of a single sequence, not a
sum) is ambiguous for a bounded/drifting finite sequence; regularized-sum-of-the-gap is
the operationalization actually computed here, disclosed rather than silently assumed.

No REBUILD_THE_SPLIT.md file exists on disk (checked) -- this construction is new.

| record | window | fwd zeta_B | fwd exp_B | fwd abel_B | rev zeta_B | rev exp_B | rev abel_B | sign flip (any method)? |
|---|---|---|---|---|---|---|---|---|
| yeast | during (800-1400s) | -2,891 | +2,458 | +102.5 | -304.4 | +3,023 | +2,362 | NO (all 3 methods keep sign fwd vs rev) |
| mouse14 (size4-5) | middle | +25,812 | +27,331 | +39,396 | +25,576 | +25,899 | +37,915 | NO |
| mouse27 (size4-5) | middle | +17,513 | +19,489 | +27,498 | +20,200 | +18,063 | +27,335 | NO |
| mouse10 (size1, null) | middle | +34,661 | +25,692 | +41,885 | +34,365 | +32,501 | +48,709 | NO |

Bootstrap sd (300 case-resamples, real-order): yeast during ~105-158 (4-6% of the point
estimate); mice ~240-790 (1-3% of the point estimate). **No sign flip under time-reversal
on any record, any method** -- R keeps its sign both directions, unlike THREE_ON_YEAST's
own after-window clock tau, which DID flip under both backward chaining and reversal.

**Casimir verdict on R:** the three regulators disagree with each other by 15-90% of their
own median on every one of the four records (yeast during: zeta and exp don't even agree
in relative size to abel by a factor of ~28; mice: 15-55% spread) -- **R is a ruler
reading, not a stable object, on every record and window tried.** The yeast record (the
one continuous trace with a real switch-on/off) shows the worst regulator disagreement of
all (zeta_B negative, exp_B and abel_B positive, on the SAME series) -- the sign itself is
not even regulator-stable there, the strongest possible failure of the Casimir test.

## TASK 3 -- the pinata check: ratios to the arrow's k and the clock's tau

15 ratio checks run (yeast after-window backward-clock remainders vs. arrow k=81.22s /
forward tau=688.2s / period=48.7s; yeast SPLIT-R vs. period and arrow k during). Three
ratios landed within 2x the propagated bootstrap error of a named constant, reported with
their errors, per the brief, and stopped there -- not chased further:
- **exp_B (yeast after-window backward clock, 254.7) / arrow k (81.22s) = 3.136**, vs pi
  (3.1416): diff -0.0054, propagated error ~0.224 (2-sigma band). Within error of pi, but
  1 of 15 checks landing this close to one of 4 named constants at a 2-sigma bar is not a
  surprising coincidence rate (~5% per check per constant; multiple-comparison honest read:
  do not treat as a discovery).
- **abel_B (yeast SPLIT-R during, 102.5) / period (48.7s) = 2.11**, and **/ arrow k during
  (115.28s) = 0.889**: both technically "within 2-sigma" of several named constants at once
  (-1/12, 1/2, pi, e) only because this cell's bootstrap error (158) is itself larger than
  the remainder (102.5) -- the "match" is an artifact of a wide error bar swallowing every
  candidate, not a precise landing. Flagged as such, not sold as a hit.
No ratio landed close to a named constant with a TIGHT error bar. Full table in
`regularize_results.json` (`task3_pinata_check`).

## PLAIN WORDS

**Did any finite remainder survive every regulator, every window and both time
directions? No.** Zeta, exponential and Abel/Cesaro regularization disagree with each
other by 30-90% of their own value on every one of the 12 divergent-clock series and all
4 split-difference records tried -- the regulator family itself is the dominant source of
movement, more so than truncation length (5-20% movement) and far more than the
bootstrap error (2-8%). By Casimir's own rule (what survives every cutoff is the object,
what moves with the cutoff is the ruler), **none of these regularized remainders qualify
as objects** -- they are readings of whichever ruler (zeta / exp / Abel) was used. The one
thing that DID hold steady: sign under time-reversal for THE SPLIT's R on every record
(unlike the raw clock tau, which flipped) -- a real, if modest, finding, reported as such.
Cesaro's own running mean never converged on any series (logged, not smoothed): consistent
with theory, since Cesaro regularizes oscillating divergences and none of these series
oscillate in sign.

## Tries

Task 1: 12 series x (3 regulator methods x [5 zeta-s + 3 exp-eps + 3 Abel-r evaluations]
+ 500-draw case-resample bootstrap + 3-fraction truncation retest) = 12 x (11 point evals
+ 500 boot draws x 3 sub-methods each recomputing all 3 regs + 3 truncation refits) =
6,000 bootstrap draws total (500 x 12), plus 12 x 3 = 36 truncation-refit point estimates,
plus 12 x 11 = 132 raw regulator-value evaluations. Task 2: 4 records x 2 directions x
(11 regulator-value evaluations + 300-draw bootstrap + 3-fraction truncation on forward
only) = 2,400 bootstrap draws (300 x 4 x 2), 88 raw regulator-value evaluations, 12
truncation-refit point estimates. Task 3: 15 ratio checks x 4 named-constant comparisons
= 60 constant-proximity tests. **Grand total: 8,400 bootstrap/case-resample draws, 220
raw regulator-value point evaluations, 48 truncation-refit point estimates, 60
named-constant proximity tests, 12 + 4 = 16 series/records carried through both Casimir
tests (regulator-family and truncation-length).**

## Files

- Report: `~/bones-forge/parallax/THE_PINATA_20260930.md` (this file)
- Module (new): `parallax/out/yeast/three/regularize.py` -- does not edit
  `three_formulas.py` or `backwards.py`; imports `parallax/out/three_on_three/core.py`
  verbatim for envelope/fit reuse.
- Raw output: `parallax/out/yeast/three/regularize_results.json`
- Sources read, unedited: `THIRD_RUNG_20260928.md` Sec51/50/50c,
  `CASIMIR_CALIBRATION_20260929.md` Sec1-2, `THREE_ON_YEAST_20260930.md`,
  `THREE_ON_MICE_ANTS_20260930.md`, `out/yeast/three/three_formulas.py` (frozen, read-only),
  `out/yeast/three/backwards.py`, `out/three_on_three/{core.py,mice_ants_pipeline.py}`,
  `mice_ants_pooled.json` (error-row mouse/window selection).
