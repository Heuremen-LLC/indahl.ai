# THE PINATA, REDONE -- Ramanujan's CONVERGENT 1/pi series in the middle, 2026-09-30

Corrects THE_PINATA_20260930.md (which ran the -1/12 zeta/exponential/Abel regulators, the WRONG
Ramanujan sum for this job -- THIRD_RUNG_20260928.md Sec56b, Wayfinder ~23:00Z: "we switched that
equation halfway through today; the morning runs had the other Ramanujan one in the middle -- go
back and take a look"). Same 12 divergent clock series and 4 split differences as the morning run,
same windows, same records, built by calling `parallax/out/yeast/three/regularize.py`'s own
(unedited) series-construction functions directly. New module:
`parallax/out/the_middle/pinata_redo.py`. Raw output: `parallax/out/the_middle/pinata_redo_results.json`.

## WHAT IS DEFINED, stated first

1/pi's series is CONVERGENT. A convergent series cannot assign a finite value to a divergent sum --
that is what "regularization" (the -1/12 move) does, and a convergent series does not do it. So
this run does not regularize anything. It does the only honest thing left: test whether each
record's OWN partial-sum sequence (task 1) or its own D(N) sequence (task 3, the split) is itself
convergent, divergent, or oscillating (Cauchy-style tail check, 300-draw block bootstrap, never
shuffled); only convergent ones get an extrapolated limit (Aitken delta-squared, and Richardson
using the record's own measured tail ratio of successive terms); divergent/oscillating ones stop
at "no limit: not defined with this middle," with the tail growth rate as their number. No
expectation written first.

## TASK 1 -- the 12 divergent clock series, partial-sum convergence + extrapolation

| series | n | Cauchy call | growth rate/idx (if undefined) | Aitken limit ± boot SE | terms to land | landing index (series always K=0, 1 term) |
|---|---|---|---|---|---|---|
| yeast before (morning's DIVERGENT source) | 408 | **DIVERGENT** | 5.37/idx | -- | -- | -- |
| yeast during | 111 | CONVERGENT | -- | 37.67 ± 12.88 | 37 | 37.0 |
| yeast after | 358 | CONVERGENT | -- | 4760.0 ± 1411.3 | 195 | 195.0 |
| mouse10 first (size1) | 288 | CONVERGENT | -- | 47.89 ± 6.54 | 203 | 203.0 |
| mouse10 middle (size1) | 288 | CONVERGENT | -- | 49.00 ± 5.39 | 224 | 224.0 |
| mouse10 last (size1) | 288 | CONVERGENT | -- | 55.72 ± 9.30 | 207 | 207.0 |
| mouse14 middle (size4-5) | 288 | CONVERGENT | -- | 58.30 ± 3.67 | 222 | 222.0 |
| mouse17 middle (size4-5) | 288 | CONVERGENT | -- | 60.19 ± 4.85 | 229 | 229.0 |
| mouse24 middle (size2-3) | 288 | **DIVERGENT** | 0.385/idx | -- | -- | -- |
| mouse1 first (size2-3) | 288 | CONVERGENT | -- | 41.64 ± 4.40 | 204 | 204.0 |
| mouse16 first (size4-5) | 288 | CONVERGENT | -- | 53.10 ± 4.14 | 232 | 232.0 |
| mouse22 first (size4-5) | 288 | CONVERGENT | -- | 32.53 ± 3.84 | 222 | 222.0 |

**10 of 12 rows are defined (their own partial sums pass the Cauchy block test); 2 are not**
(yeast before -- the morning's own named DIVERGENT source -- and mouse24 middle both fail: their
tail block-to-block drift is bigger than its own bootstrap error and holds one sign, i.e. a real,
resolvable linear growth, reported as growth rate per index rather than a limit).

**The yardstick collapses to one number:** every "convergent" row's target relative error (its own
Aitken bootstrap SE divided by its own limit, ranging 0.10-0.64) is so many orders of magnitude
above the pi series' own first-term floor (2.4e-8) that the series always lands at K=0 (1 term) --
identical to THE_MIDDLE_PI's own finding. "Landing index" is therefore just the record's own terms-
to-land number (37-232), unchanged by dividing by 1.

**Caveat that changes the plain-words read of "10/12 defined," disclosed not hidden:** the Cauchy
block test only asks whether the LAST block-to-block move is inside the record's own (large)
bootstrap noise -- it does not require the series' own TERMS to actually shrink. The record's own
measured tail ratio `r_hat` (successive-increment ratio, the number Richardson needs to be strictly
between 0 and 1) sits at **0.999-1.026 for 11 of the 12 series computed** -- essentially 1.0, i.e.
flat, not decaying. Richardson's geometric-tail formula therefore returns **no number at all
(`r_hat >= 1`) for 9 of the 10 "convergent" rows**; the one row where `r_hat` slips just under 1
(mouse16, 0.999) produces a Richardson estimate of 244.3, **4.6x Aitken's 53.1 and outside their
combined error** -- a real disagreement, not an agreement, and a numerical warning sign (1/(1-r_hat)
~1000x amplifies noise when r_hat this close to 1). Read plainly: these 10 rows are "convergent"
only in the weak sense that the record's own noise is too coarse to see further drift in the data
available -- not in the sense of the pi series' own fast, geometric convergence. Aitken's own
numbers should be read with that caveat attached, not as a clean fast landing.

## TASK 2 -- THE SPLIT's remainder, redone: 4 split differences, forward + reversed

D(n) = T(n) - Phi(n), same construction as the morning (yeast during-window, period from the
independent before-window FFT; mice, period fixed at the external 24h). R = the extrapolated limit
of D(N) as N grows (Aitken and Richardson applied directly to the D(N) sequence, since D(N) is
itself the object here, not a series to be summed).

| record | dir | Cauchy call | Aitken R ± boot SE | Richardson R ± boot SE (r_hat) | terms to land (Aitken) | stable across 2 methods? |
|---|---|---|---|---|---|---|
| yeast during (800-1400s) | fwd | CONVERGENT | -306.06 ± 99.53 | -255.95 ± 120.12 (r=0.505) | 237 | **YES** (diff 50.1, comb err 219.7) |
| yeast during | rev | CONVERGENT | -228.60 ± 117.11 | -259.44 ± 123.66 (r=0.543) | 292 | **YES** (diff 30.8, comb err 240.8) |
| mouse14 middle (size4-5) | fwd | CONVERGENT | -2469.21 ± 149.56 | -2751.34 ± 165.64 (r=0.387) | 2353 | **YES** (diff 282.1, comb err 315.2) |
| mouse14 middle | rev | CONVERGENT | -2505.52 ± 166.94 | -2773.59 ± 173.41 (r=0.384) | 2324 | **YES** (diff 268.1, comb err 340.3) |
| mouse27 middle (size4-5) | fwd | CONVERGENT | -1680.95 ± 201.55 | -1909.66 ± 227.08 (r=0.265) | 2138 | **YES** (diff 228.7, comb err 428.6) |
| mouse27 middle | rev | CONVERGENT | -1847.36 ± 195.64 | -2197.78 ± 188.28 (r=0.030) | 2126 | **YES** (diff 350.4, comb err 383.9) |
| mouse10 middle (size1, null) | fwd | CONVERGENT | -3053.69 ± 263.57 | -3328.95 ± 271.37 (r=0.491) | 2273 | **YES** (diff 275.3, comb err 534.9) |
| mouse10 middle (size1, null) | rev | **DIVERGENT** | -- | -- | -- | -- (reversal is not defined with this middle) |

**Unlike Task 1, `r_hat` here is genuinely below 1 (0.03-0.54) on every computable cell** -- these
D(N) sequences really do have a shrinking tail, so Richardson's geometric-tail formula is a
legitimate second method here, not a near-singular one. **Sign under reversal: R stays negative on
every one of the 3 records where both directions are defined (yeast, mouse14, mouse27) -- no flip,
matching the morning's own finding for the old regulator-based R.** Mouse10 (the size-1 null mouse)
is the one record where reversal cannot even be tested: its reversed D(N) sequence fails the Cauchy
test outright (DIVERGENT) -- the same null mouse that THIRD_RUNG's other reports keep finding as
"the record the instrument can't finish stripping." **Casimir test with two methods instead of
three regulators: STABLE on all 7 computable cells** (Aitken and Richardson agree within their
combined bootstrap error every time) -- a real improvement over the morning's three-regulator test,
where zeta/exp/Abel disagreed by 30-90% on every single cell and even flipped sign on the yeast.
Two methods, applied to a genuinely convergent sequence, actually agree here.

## TASK 3 -- THE MORNING'S ONE HIT, RECOMPUTED

Morning: `exp_B (yeast after-window backward-clock remainder, 254.7) / arrow k (81.22s) = 3.136`,
reported as within 2 sigma of pi (diff -0.0054, propagated error ~0.224).

Redone: the yeast after-window backward-clock series **is convergent** under the Cauchy test (see
Task 1 table), so a limit exists to put in exp_B's place -- but Richardson returns no number
(r_hat=1.011, not <1), so only Aitken's limit is available:

**New limit = 4760.037 ± 1411.267 (Aitken, robust bootstrap). New ratio = limit / arrow k (81.22s)
= 58.606714280617204 ± 17.375856762396598.**

Not rounded, per the brief. **58.6 is nowhere near pi (3.14159...)** -- the morning's 3.136 was a
number produced by the -1/12-style regulator's own extrapolation-to-a-singular-point machinery
(fitting B in `E(eps) ~ A/eps + B` as eps->0), not a property of the record; putting a legitimate
convergent limit in the same slot moves the ratio by a factor of ~19, off the pi target by more
than 3 combined errors. The one hit does not survive its own correction.

## PLAIN WORDS

**Defined vs undefined:** of the 12 divergent clock series, 10 are defined under a convergent
middle (their own partial sums pass a Cauchy block test) and 2 are not (yeast before, mouse24
middle -- genuine linear growth, reported as growth rate, not a limit). Of the 4 split differences
x 2 directions = 8 cells, 7 are defined and 1 is not (mouse10 reversed). **But "defined" here is a
weaker claim than the pi series' own convergence**: the record's own measured term ratio sits at
essentially 1.0 (not shrinking) on 11 of the 12 Task-1 series, so Richardson (which needs a real
geometric tail) produces almost nothing there, and the "convergent" call reflects noise too coarse
to resolve further drift, not fast landing. The split's D(N) sequences are the one place a real
geometric tail (r_hat 0.03-0.54) shows up, and there Aitken and Richardson genuinely agree.

**Where the defined ones land:** Task 1's Aitken limits run 32.5 to 60.2 for the 9 "clean" clock
series and 4760.0 for the yeast after-window outlier (an order of magnitude above the rest --
flagged, not smoothed). Task 2's split R runs -228.6 to -306.1 (yeast) and -1681 to -3329 (mice),
always negative.

**Does the split's remainder still refuse to flip?** Yes, on every record where reversal could be
tested (yeast, mouse14, mouse27): R keeps its negative sign both directions, matching the morning's
finding under the old regulators. The one record it could NOT be tested on is new information: the
null mouse's reversed sequence is itself undefined under this middle.

**What happened to the pi ratio:** it is gone. exp_B/arrow-k was 3.136 (within 2 sigma of pi) under
the -1/12-style regulator; under a convergent middle's own honest extrapolation of the same series,
the ratio is 58.6 ± 17.4 -- off pi by more than 3 combined errors. The morning's one hit was a
property of the wrong regulator, not of the record.

## Tries

Series profile: 11 terms (k=0..10) computed once, exact Decimal arithmetic, no bootstrap (a
deterministic sum has no error bar). Task 1: 12 series x 300-draw Cauchy block bootstrap = 3,600
draws; 10 convergent series x 2 extrapolation methods attempted (Aitken always evaluated,
Richardson evaluated but returns a number in only 2 of 10) x 300-draw extrapolation bootstrap =
3,000 draws. Task 2: 4 records x 2 directions = 8 sequences x 300-draw Cauchy block bootstrap =
2,400 draws; 7 defined sequences x 2 methods x 300-draw extrapolation bootstrap = 2,100 draws.
**Grand total: 11,100 bootstrap draws** (6,000 Cauchy-classification + 5,100 extrapolation), 20
sequences classified for convergence (12 + 8), 34 Aitken/Richardson point-estimate attempts on the
17 convergent sequences, 7 forward-vs-reversed sign-flip checks, 7 Aitken-vs-Richardson stability
checks, 1 ratio recomputation. No shuffle used as judge anywhere.

## Files

- Report: `~/bones-forge/parallax/THE_PINATA_REDO_20260930.md` (this file)
- New script: `parallax/out/the_middle/pinata_redo.py` -- imports
  `parallax/out/yeast/three/regularize.py` verbatim (unedited) for series construction; all new
  convergence-classification and Aitken/Richardson math lives in this file only.
- New raw output: `parallax/out/the_middle/pinata_redo_results.json`
- Reused, unedited: `parallax/out/yeast/three/regularize.py`, `parallax/out/three_on_three/core.py`
- Sources read: `THIRD_RUNG_20260928.md` Sec51/56/56b, `THE_PINATA_20260930.md`,
  `THE_MIDDLE_PI_20260930.md`, `parallax/out/yeast/three/regularize_results.json`,
  `parallax/out/the_middle/the_middle.py` / `the_middle_results.json`
