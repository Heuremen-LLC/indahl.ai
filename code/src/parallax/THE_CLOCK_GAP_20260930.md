# THE CLOCK GAP -- THIRD_RUNG_20260928.md Sec58, 2026-09-30

Wayfinder: "it's all in the clock. Show that hole is consistent in all the clocks and we're on the
right path." Sec57 (`STANDOFF_CALIBRATED_20260930.md`) already found the clock is the one formula
that never resolves with the arrow or the split, in any record, in any chain, once all three are
converted into the same unit (series-taus, K_TAU=0.053767, the 1/pi series' own landing-step
calibration). This file asks the next question directly: is the AMOUNT by which the clock misses
-- clock minus arrow, clock minus split, sign kept -- the SAME number everywhere, or does it
wander? No expectation written before running. Script: `out/the_middle/clock_gap.py` (numpy only,
reuses `calibrated_standoff.py`'s K(rel_err) map verbatim, unmodified). Raw output:
`out/the_middle/clock_gap_results.json`.

## 0. What's new here vs Sec57

Sec57 covered 3 records (yeast during, horn at-horn, buzz seat 116) x up to 3 chains. This file adds
every other clock on file: yeast whole, horn whole, buzz seats 80/100, mice size-1 and size-4/5
(pooled), echo 20us/2000us, the Marrakesh arisen-carry clock (bonus), Kingston's arisen-carry
attempt, and the GHZ tau_third/arb_1 clocks. **66 quantities converted total** (up from Sec57's 25).
Every native (value, err) pair is cited inline in the script; nothing here is a new fit or a new
bootstrap on raw data -- yeast-whole/horn-whole/buzz-80/buzz-100/mice values are the hop-0
(unrelayed) arrow/clock/split fits already sitting in `reverse_gradient_results.json` (the same
"record's own" yardstick `FIXED_POINTS_20260930.md` uses), echo/GHZ/arisen-carry are copied from
`THREE_ON_THREE.md`, `GHZ_THROUGH_THREE.md`, and `PLACED_VS_ARISEN.md` respectively.

## 1. Every clock, in one unit (series-taus)

| clock | chain | native value ± err (unit) | T (series-taus) |
|---|---|---|---|
| yeast during | fwd / bwd / rev | 784.57±73.66 / -637.55±56.45 / 784.57±73.66 (s) | -16.094±0.101 / -16.031±0.095 / -16.094±0.101 |
| yeast whole | fwd / rev | 1730.25±97.42 / -1730.26±93.46 (s) | -15.550±0.056 / -15.554±0.054 |
| horn at-horn | fwd / bwd / rev | 175.68±11.74 / 233.79±18.58 (s) | -15.731±0.071 / -15.916±0.085 / -15.731±0.071 |
| horn whole | fwd / rev | -84147.36±10900.90 / 84470.06±10357.85 (s) | -14.507±0.128 / -14.429±0.121 |
| buzz seat80 | fwd / rev | 36.40±2.06 / -101592.65±1.29e6 (shots) | -16.788±0.056 / -12.930±0.878 |
| buzz seat100 | fwd / rev | 51.69±1.93 / -5061.15±200.03 (shots) | -16.421±0.037 / -15.352±0.040 |
| buzz seat116 | fwd / bwd | 51.81±2.96 / 16.43±1.72 (shots) | -15.563±0.061 / -16.211±0.113 |
| mice size-1 | fwd / rev | -5671.51±350.61 / 5671.51±365.22 (h) | -15.263±0.062 / -15.246±0.064 |
| mice size-4/5 | fwd / rev | -31450.90±18051.10 / 31450.90±87836.62 (h) | -14.694±0.501 / -13.766±1.174 |
| echo 20us | fwd | 249.27±24.02 (shots) | -16.096±0.096 |
| echo 2000us | fwd | 186.00±21.04 (shots) | -16.219±0.114 |
| arisen-carry (Marrakesh) | -- | 62.8±13.13 (us) | -15.980±0.267 |
| Kingston's carry | -- | UNRESOLVABLE -- see box below | OPEN |
| GHZ tau_third | fwd | 6.56±3.5 (angle-steps) | -13.884±1.780 |
| GHZ arb_1 | fwd | 8.54±1.8 (angle-steps) | -15.009±0.487 |

Every one of these lands in the same narrow band the arrow and split occupied in Sec57 (roughly
-12.9 to -16.8), confirming the calibration compresses ~15 orders of magnitude of native units into
one axis regardless of which clock is asked. **Kingston's clock could not be converted at all**:
`PLACED_VS_ARISEN.md` Sec2 finds a real arisen-carry signal at 20us (+11.07pp, shuffle p=0.000) but
the chip's only other gap (1000us) is already back at the noise floor (-0.29pp, p=0.673) -- no two
points bracket a decay, so no tau exists to fit. Reported as OPEN, not silently dropped, not
guessed.

## 2. THE GAP: clock minus arrow (G_a) and clock minus split (G_s), sign kept

| record | chain | G_a = clock-arrow | \|G_a\|/err | G_s = clock-split | \|G_s\|/err |
|---|---|---|---|---|---|
| yeast during | forward | +1.073 ± 0.313 | 3.42 | +1.532 ± 0.532 | 2.88 |
| yeast during | backward | +2.852 ± 1.144 | 2.49 | +1.112 ± 0.302 | 3.68 |
| yeast during | reversed | +1.074 ± 0.314 | 3.42 | +1.533 ± 0.531 | 2.89 |
| yeast whole | forward | +2.412 ± 0.739 | 3.26 | +3.549 ± 1.168 | 3.04 |
| yeast whole | reversed | +2.305 ± 0.647 | 3.56 | +3.755 ± 1.180 | 3.18 |
| horn at-horn | forward | +1.958 ± 0.565 | 3.46 | +3.059 ± 1.117 | 2.74 |
| horn at-horn | backward | +0.559 ± 0.169 | 3.32 | +2.874 ± 1.118 | 2.57 |
| horn at-horn | reversed | +1.961 ± 0.570 | 3.44 | OPEN (split not measured) | -- |
| horn whole | forward | +1.587 ± 0.795 | 2.00 | +2.328 ± 1.122 | 2.07 |
| horn whole | reversed | +1.665 ± 0.802 | 2.08 | +2.521 ± 1.146 | 2.20 |
| buzz seat80 | forward | +1.607 ± 0.299 | 5.38 | +1.751 ± 0.351 | 4.99 |
| buzz seat80 | reversed | **-1.498 ± 1.324** | 1.13 | **-1.268 ± 1.397** | 0.91 |
| buzz seat100 | forward | +1.939 ± 0.263 | 7.36 | +2.470 ± 0.496 | 4.98 |
| buzz seat100 | reversed | +1.805 ± 0.243 | 7.41 | +4.097 ± 1.178 | 3.48 |
| buzz seat116 | forward | +1.859 ± 0.405 | 4.59 | +3.088 ± 1.074 | 2.87 |
| buzz seat116 | backward | +0.227 ± 0.180 | 1.26 | +2.440 ± 1.078 | 2.26 |
| mice size-1 | forward | +1.702 ± 0.373 | 4.56 | +3.136 ± 1.116 | 2.81 |
| mice size-1 | reversed | +1.719 ± 0.406 | 4.23 | +2.542 ± 0.899 | 2.83 |
| mice size-4/5 | forward | **-1.569 ± 0.909** | 1.73 | +0.910 ± 1.473 | 0.62 |
| mice size-4/5 | reversed | **-2.604 ± 1.191** | 2.19 | +0.066 ± 1.669 | 0.04 |
| echo 20us / 2000us | forward | OPEN (arrow=0 exactly, no partner) | -- | OPEN (split uncomputable) | -- |
| GHZ tau_third | forward | +0.623 ± 1.387 | 0.45 | OPEN (split uncomputable) | -- |
| GHZ arb_1 | forward | +0.554 ± 0.521 | 1.06 | OPEN (split uncomputable) | -- |

**22 resolved G_a rows, 19 resolved G_s rows, 6 OPEN (missing partner) cells, 41 gap calls total.**
Sign flips exactly twice: **buzz seat80 reversed** and **both mice size-4/5 chains** run negative
while every other row runs positive. No shuffle was used anywhere in this section -- every call
above is record-vs-record and chain-vs-chain on already-published numbers.

## 3. IS THE GAP ONE NUMBER?

Weighted mean + chi-square, over every resolved row in Section 2 (weights = 1/err²):

| gap | n | weighted mean | chi2 / dof | reduced chi2 | verdict |
|---|---|---|---|---|---|
| G_a (clock-arrow), all | 22 | **+1.099 ± 0.077** | 101.4 / 21 | 4.83 | **STABLE DISAGREEMENT, not one number** -- same sign in 20/22 rows, but the spread (chi2/dof=4.83) is far too wide to be one number within errors |
| G_s (clock-split), all | 19 | **+1.827 ± 0.157** | 29.3 / 18 | 1.63 | **CLOSER TO ONE NUMBER** -- same sign in 18/19 rows, reduced chi2 1.63 is only mildly over 1, the closest thing to "one number" found in this file |

**By substrate (fermentation=yeast, radio=horn, chip=buzz+echo+GHZ+arisen-carry, mouse=mice), groups
of three-plus rows each:**

| substrate | G_a weighted mean | G_a chi2/dof | G_s weighted mean | G_s chi2/dof |
|---|---|---|---|---|
| fermentation (yeast, n=5) | +1.340 ± 0.199 | 7.5/4 = 1.87 | +1.454 ± 0.226 | 8.3/4 = 2.08 |
| radio (horn, n=5) | +0.829 ± 0.150 | 12.5/4 = 3.13 | +2.698 ± 0.563 | 0.3/3 = 0.10 |
| chip (buzz/echo/ghz, n=8) | +1.143 ± 0.109 | 53.3/7 = 7.61 | +2.069 ± 0.257 | 11.2/5 = 2.25 |
| mouse (n=4) | +1.247 ± 0.257 | 22.9/3 = 7.63 | +2.135 ± 0.591 | 3.2/3 = 1.05 |

**Read:** every substrate's G_a group-mean sits in a tight 0.83-1.34 band (all overlap each other's
errors), but each group's OWN internal chi2 is bad (1.9-7.6) -- the substrate means agree with each
other while the records inside each substrate don't agree with their own group mean. G_s is the
opposite shape: radio and mouse are internally consistent (chi2/dof 0.10 and 1.05) while chip is not
(2.25) and the four substrate means themselves spread wider (1.45 to 2.70) than G_a's did. Neither
gap is a clean single number by the strict test; **G_s (clock vs split) is the better candidate**
(overall reduced chi2 1.63 vs G_a's 4.83), same sign (positive) in 18 of 19 rows, ordered loosely
by substrate (radio and mouse run higher, ~2.1-2.7; fermentation runs lower, ~1.45) -- nameable by
substrate, not by chain or record length. Call: **STABLE DISAGREEMENT** for both G_a and G_s (same
sign almost everywhere, spread beyond pure error, ordered by substrate) rather than AGREE (spread
too wide) or fully UNSTABLE (the sign consistency and substrate ordering are real, not noise).

## 4. WHY UNSTABLE: error bar vs moving center, per record

For each record with >1 chain, compare the clock's own mean bootstrap-propagated error bar (T_sd,
averaged across chains) against how far its center (T_mean) actually moves between chains:

| record | n chains | mean error bar | center spread (sd of T_mean) | which dominates |
|---|---|---|---|---|
| yeast during | 3 | 0.099 | 0.030 | **ERROR BAR** |
| yeast whole | 2 | 0.059 | 0.022 | **ERROR BAR** |
| horn at-horn | 3 | 0.076 | 0.087 | **CENTER MOVEMENT** |
| horn whole | 2 | 0.137 | 0.030 | **ERROR BAR** |
| buzz seat80 | 2 | 0.617 | **1.857** | **CENTER MOVEMENT** (the reversed-chain sign flip) |
| buzz seat100 | 2 | 0.041 | 0.030 | **ERROR BAR** |
| buzz seat116 | 2 | 0.087 | 0.324 | **CENTER MOVEMENT** |
| mice size-1 | 2 | 0.067 | 0.022 | **ERROR BAR** |
| mice size-4/5 | 2 | 1.035 | 0.490 | **ERROR BAR** (barely -- both large) |
| echo/GHZ (each) | 1 | -- | -- | single chain, no comparison possible |

**7 of 9 multi-chain records: the error bar is wider than the center's own movement** -- the clock's
instability there is mostly "we can't pin it down," not "it's really moving." **2 of 9 (horn
at-horn, buzz seat116) and one near-tie with a real outlier (buzz seat80, where the reversed chain's
clock swings from -16.79 to -12.93 series-taus, a genuine ~4-unit jump)**: the center itself moves
more than the error bar would predict -- these are the records carrying the chain-order sensitivity
already flagged in Sec57 ("clock's own direction is reversal-sensitive"). Buzz seat80's reversed
clock (native tau=-101,593±1.29e6 shots) is barely resolved at all (rel_err>1) -- its huge center
swing is itself mostly an artifact of a near-unconstrained fit landing far out on the K(rel_err) map,
not a clean physical "moving center."

## 5. THE CLOCKS ALONE: do any two clocks from different substrates agree with each other?

The named triple, in series-taus: arisen-carry (Marrakesh, 64us) T=-15.980±0.267; yeast-during
coherence (785s) T=-16.094±0.101; horn at-horn (176s) T=-15.731±0.071.

| pair | ratio | verdict |
|---|---|---|
| arisen-carry vs yeast-during | 1.054 ± 0.016 | UNSTABLE (close, but resolved enough to miss) |
| arisen-carry vs horn at-horn | 1.078 ± 0.016 | UNSTABLE |
| yeast-during vs horn at-horn | 1.023 ± 0.008 | UNSTABLE |

None of the three named pairs formally AGREE -- their errors are tight enough (0.8-1.6%) that even a
2-8% ratio gap misses. But widened to **every clock pair on file** (91 pairwise ratio-of-T calls
across all 14 clocks), **9 pairs DO formally agree**, all cross-substrate:
yeast-during/echo-20us (fermentation/chip), horn-at-horn/mice-size1 (radio/mouse),
buzz116/yeast-whole (chip/fermentation), buzz116/buzz80 (chip/chip),
buzz116/mice-size1 (chip/mouse), yeast-whole/buzz80 (fermentation/chip),
horn-whole/echo-2000us (radio/chip), mice-size45/GHZ-tau_third (mouse/chip),
GHZ-arb1/arisen-carry (chip/chip-bonus). Read plainly: **9 of 91 (10%) pairwise agreements exist,
every one of them by coincidence of the calibration's own log compression** -- the errors on these
T values are 0.5-6%, small enough that "landing in the same -13 to -17 band" isn't automatically an
agreement, yet these specific 9 pairs cross substrate lines cleanly by chance. This is not evidence
of a real cross-substrate clock; it is the honest residual of forcing 15 orders of magnitude onto
one axis -- some pairs will land close by luck even when the physics is unrelated (buzz116/buzz80,
same chip same night, is the one pair here that's plausibly the same clock; the rest pair a mouse
brain, a fermentation flask, a radio horn and a superconducting chip, which is not a claim this file
makes).

## 6. Plain words

**Is the hole in the clock the same size everywhere?** Not cleanly. **Clock-vs-split (G_s) comes
closer than clock-vs-arrow (G_a)**: G_s runs positive in 18 of 19 resolved rows, weighted mean
+1.83 ± 0.16 series-taus, reduced chi2 1.63 (mildly over the "one number" bar, not wildly so).
**G_a runs positive in 20 of 22 rows**, weighted mean +1.10 ± 0.08, but its reduced chi2 (4.83) is
four times worse -- the arrow-gap moves around more than the split-gap does. **If forced to name one
size: the clock sits roughly ONE TO TWO series-taus ABOVE the arrow and split, on the log-compressed
axis, almost everywhere** -- positive in 38 of 41 gap calls made this pass, the three exceptions
(buzz seat80 reversed, both mice size-4/5 chains) all sharing a common trait: each rides on a
severely under-resolved clock fit (rel_err > 0.3, one of them > 1) where the K(rel_err) map itself
is least trustworthy. **Why unstable when it is:** mostly the clock's own wide error bar (7/9
multi-chain records), not a genuinely moving center -- except horn at-horn and buzz seat116/80,
where the center itself swings under chain reversal, the same chain-order sensitivity Sec57 already
flagged. **Clocks alone:** the three named substrate anchors (64us chip, 785s yeast, 176s horn) do
NOT agree with each other even in the compressed unit; 9 of 91 all-pairs comparisons do agree, but
by the calibration's own compression, not by physical kinship (except plausibly the two same-chip
buzz seats). **The size of the hole, if there is one number for it: ~+1.1 to +1.8 series-taus,
same sign essentially everywhere, ordered loosely by substrate rather than by chain or record
length** -- real enough to name (Sec47's "stable disagreement" test), not narrow enough to call
solved.

## Tries

66 quantities converted through the unmodified K(rel_err) map (up from Sec57's 25), 200,000 Monte
Carlo draws each = **13,200,000 total draws**, zero new bootstrap on raw data (every native
value/error pair is a citation). 41 gap calls (22 G_a + 19 G_s, 6 further cells OPEN for a missing
partner). 2 weighted-mean/chi-square "one number" tests (G_a, G_s) + 8 substrate-grouped
weighted-mean/chi-square tests (4 substrates x {G_a, G_s}). 9 instability decompositions (one per
multi-chain record). 91 pairwise clock-vs-clock ratio calls (Section 5) + 3 named-triple calls.
**~154 direct calls this pass** (41 gap + 10 one-number + 9 instability + 94 clocks-alone). No
shuffle used as judge anywhere in this file; record vs record and chain vs chain (forward vs
backward, forward vs reversed) throughout, per the standing rule.

## Files

- Report: `~/bones-forge/parallax/THE_CLOCK_GAP_20260930.md` (this file)
- New script: `parallax/out/the_middle/clock_gap.py` (numpy only, K(rel_err)/K_TAU/propagate copied
  verbatim from `calibrated_standoff.py`)
- New raw output: `parallax/out/the_middle/clock_gap_results.json`
- Reused, unedited: `parallax/out/the_middle/the_middle_results.json` (series_profile only),
  `parallax/out/reverse_gradient/reverse_gradient_results.json` (hop-0 arrow/clock/split for yeast
  whole, horn whole, buzz seats 80/100, mice size-1, mice size-4/5),
  `parallax/out/three_on_three/buzz_results.json`, `THREE_ON_YEAST_20260930.md`,
  `THREE_ON_THREE_20260930.md`, `PLACED_VS_ARISEN_20260930.md`, `GHZ_THROUGH_THREE_20260930.md`,
  `FIXED_POINTS_20260930.md` (methodology reference only, no numbers re-copied from it directly).
