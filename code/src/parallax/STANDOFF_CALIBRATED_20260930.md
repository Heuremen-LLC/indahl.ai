# THE STANDOFF, CALIBRATED -- THIRD_RUNG_20260928.md Sec57, 2026-09-30

Wayfinder: "each equation will resolve the other in a three-body standoff... the one in the middle
might be for calibration, frequency calibration, just like a three-body problem." Sec50's standoff
failed because the arrow's k (seconds/shots), the clock's tau (seconds/shots) and the split's
per-cycle crossing (a dimensionless fitted slope) live in different units. This file converts all
three, on three records (yeast, horn, buzz J2 seat 116), into ONE unit using the 1/pi series
(Sec56/THE_MIDDLE_PI_20260930.md) as the calibrator, then re-runs the standoff. No expectation
written first. Script: `out/the_middle/calibrated_standoff.py` (numpy only). Raw output:
`out/the_middle/calibrated_standoff_results.json`. No new bootstrap on raw data -- every native
(value, error) pair below is copied, cited, from prior reports (`THREE_ON_YEAST_20260930.md`,
`THREE_ON_THREE_20260930.md`, `three_on_three/buzz_results.json`, `PLACED_VS_ARISEN_20260930.md`);
the only new computation is the conversion map and its Monte Carlo error propagation.

## 0. The conversion, defined precisely

The series' own relative error rel_e_K (K=0..8, from `the_middle_results.json`) falls off
doubly-exponentially: 2.43e-8, 2.04e-16, 1.81e-24, ... A continuous landing-step index K(rel_err)
is built by LOG-LINEAR interpolation between anchors: K=-1 at rel_err=1.0 (zero terms summed --
full/undefined uncertainty, a modeling choice, not a measured point) and K=k at rel_err=rel_e_k for
k=0..8 (the series' own profile), extrapolated by the nearest segment's slope outside that range.
**"One series tau"** = the K at which the series' error first falls to 1/e of its K=0 value:
solving K(rel_e_0/e) gives **K_TAU = 0.053767** (between the K=0 and K=1 anchors -- the series is so
fast that an e-fold improvement past its own first term happens within ~5% of one more "step").
Every quantity T = K(rel_err)/K_TAU is then in units of series-taus.

- (a) ARROW: rel_err = |bootstrap_err(A) / A| at the record's own best k. K(rel_err), then /K_TAU.
- (b) CLOCK: rel_err = |tau_err / tau|. Same map. ("one series tau" is the fixed reference unit
  itself, defined once above, not re-derived per record.)
- (c) SPLIT: rel_err = |P_err / P| (P = the split's fitted per-cycle crossing slope). Same map.

Every real rel_err handled here (0.057-1.09) sits between the K=-1 and K=0 anchors -- none of these
measurements is anywhere close to the series' own first-term precision (2.43e-8), consistent with
THE_MIDDLE_PI's finding that every record lands coarser than the series' K=0 term. Errors on T are
Monte Carlo (200,000 draws per quantity: value_i ~ N(value, boot_err), rel_err_i = |boot_err/value_i|,
T_i = K(rel_err_i)/K_TAU, report mean/sd of T_i) -- no new bootstrap on raw data, only propagation of
the already-published bootstrap errors through the new nonlinear map.

## 1. CONVERSION TABLE (compressed; full table incl. reversed chain in the JSON)

| record | chain | arrow T (series-taus) | clock T | split T |
|---|---|---|---|---|
| yeast | forward | -17.167 ± 0.296 | -16.094 ± 0.101 | -17.628 ± 0.527 |
| yeast | backward (10-9-8) | -18.883 ± 1.135 | -16.031 ± 0.095 | -17.143 ± 0.286 |
| yeast | reversed | -17.166 ± 0.295 | -16.094 ± 0.101 | -17.625 ± 0.522 |
| horn | forward | -17.691 ± 0.569 | -15.731 ± 0.071 | -18.792 ± 1.116 |
| horn | backward | -16.475 ± 0.145 | -15.916 ± 0.085 | -18.789 ± 1.115 |
| horn | reversed | -17.691 ± 0.564 | -15.731 ± 0.071 | (not measured -- open) |
| buzz J2 seat 116 | forward | -17.424 ± 0.407 | -15.563 ± 0.061 | -18.651 ± 1.071 |
| buzz J2 seat 116 | backward | -16.438 ± 0.140 | -16.211 ± 0.113 | -18.650 ± 1.075 |
| buzz J2 seat 116 | reversed | NOT RUN upstream (`THREE_ON_THREE.md`, time budget) -- open row |
| arisen-carry clock (bonus, Marrakesh, `PLACED_VS_ARISEN.md` Sec1b) | clock only | -- | -16.964 ± 0.237 | -- |

Sign is kept in the native-unit citation (Section "0" of each source report); the calibrated T
itself has no sign (it is a log-derived precision index) -- direction comparisons are made on the
NATIVE numbers before conversion (Section 2b below), per the task's own item 2 ("does the clock's
direction... match the arrow's sign").

## 2a. THE STANDOFF IN ONE UNIT -- 3x3 pairwise ratios, per record, per chain

Ratio-of-T (should be 1.0 if two quantities land at the same calibrated precision). AGREE if
|ratio-1| <= combined MC error; else UNSTABLE (single-pair comparisons here, so never "STABLE
DISAGREEMENT" per the corrected verdict rule -- that call needs same-direction evidence across
more than one pairing).

| record | chain | arrow/clock | arrow/split | clock/split |
|---|---|---|---|---|
| yeast | forward | 1.067 ± 0.020 UNSTABLE | **0.975 ± 0.032 AGREE** | 0.914 ± 0.026 UNSTABLE |
| yeast | backward | 1.178 ± 0.071 UNSTABLE | 1.102 ± 0.069 UNSTABLE | 0.935 ± 0.016 UNSTABLE |
| horn | forward | 1.125 ± 0.037 UNSTABLE | **0.945 ± 0.060 AGREE** | 0.840 ± 0.046 UNSTABLE |
| horn | backward | 1.035 ± 0.011 UNSTABLE | 0.880 ± 0.049 UNSTABLE | 0.850 ± 0.047 UNSTABLE |
| buzz seat116 | forward | 1.120 ± 0.027 UNSTABLE | 0.937 ± 0.054 UNSTABLE (close: diff 0.063 vs err 0.054) | 0.837 ± 0.044 UNSTABLE |
| buzz seat116 | backward | 1.014 ± 0.011 UNSTABLE | 0.884 ± 0.047 UNSTABLE | 0.872 ± 0.047 UNSTABLE |

**Read: arrow/split lands within a factor of ~1 (AGREE) in the forward chain on BOTH yeast and
horn** (buzz seat 116 misses by a hair, ratio 0.937 vs required <=0.946). **Clock is the outlier in
every cell**: clock/split and arrow/clock never AGREE, in any record, any chain. Calibration did not
make the clock converge with the other two -- it moved all three onto a shared axis (series-taus,
all -15.6 to -18.9, vs. raw units spanning 15 orders of magnitude) and on that axis the clock still
sits measurably apart.

## 2b. Direction / sign check (native units, per task item 2)

| record | arrow sign at best k (native) | clock direction (rise/decay, native) | match? |
|---|---|---|---|
| yeast forward | + (during window, per THE TABLE's k=115.28s; the overall-strongest window was AFTER, +5.9M) | decay after switch-off (tau=+688 to +785s fits) | sign pattern -,-,+ across before/during/after brackets the decay's own before/after boundary, but (per THREE_ON_YEAST) the before/after clock fits have residuals 0.58-0.59 -- too flat over the window to confirm beyond noise, unchanged from the Sec50 finding |
| yeast backward | arrow at k* flips sign after-window (+237,900 raw vs -503.5 msg-unit) | clock tau flips sign under the SAME backward chain (+688 -> -638) | the one place BOTH arrow and clock flip together -- the after-window boundary, confirmed again here |
| horn | + (0.0169) | decay during at_horn (tau=+175.7s); home_after clock itself flips sign under reversal (+4696 -> -4696, expected -- decay/rise swap under reversal by construction) | clock's OWN direction is reversal-sensitive as designed; arrow's sign there is not separately diagnostic of the clock's direction (different physical quantities, as Sec50 already found) |
| buzz seat116 | + (104.5, "last"/after-like window) | clock fit positive (51.8, "middle"/during-role); backward-chain clock flips sign is NOT seen here (16.4, still positive) | no sign flip on this record/chain -- unlike yeast, buzz's clock does not flip under the 10-9-8 backward chain |

**Read:** the arrow/clock sign match is real only at the one place already found in Sec50c (yeast's
after-window boundary, where BOTH flip under backward chaining) -- it does not generalize to horn or
buzz seat 116, where either the clock's own fit is reversal-trivial (horn's during-role
autocorrelation) or no flip happens at all (buzz backward clock stays positive).

## 2c. Split's per-cycle term vs clock's amplitude, now in the same unit

Calibrated: split T vs clock T, forward chain -- yeast: -17.628 vs -16.094 (diff 1.53, combined err
0.54, **UNSTABLE**); horn: -18.792 vs -15.731 (diff 3.06, err 1.12, **UNSTABLE**); buzz seat116:
-18.651 vs -15.563 (diff 3.09, err 1.07, **UNSTABLE**). The calibration did not connect this hole
either -- same verdict as Sec50's native-unit finding ("split's crossing... never connected to the
clock's amplitude"), now confirmed in the shared unit rather than left unconvertible.

## 3. RECORD vs RECORD, in the one unit (forward chain, canonical)

| formula | yeast vs horn | yeast vs buzz seat116 | horn vs buzz seat116 |
|---|---|---|---|
| ARROW | **AGREE** (diff 0.524, err 0.641) | **AGREE** (diff 0.257, err 0.503) | **AGREE** (diff 0.268, err 0.699) |
| CLOCK | UNSTABLE (diff 0.363, err 0.123) | UNSTABLE (diff 0.531, err 0.118) | UNSTABLE (diff 0.168, err 0.094) |
| SPLIT | AGREE (diff 1.164, err 1.234) | AGREE (diff 1.022, err 1.194) | AGREE (diff 0.141, err 1.547) |

Bonus: arisen-carry clock (Marrakesh, chip family) vs buzz seat116 clock (also chip family):
**UNSTABLE** (diff 1.401, combined err 0.245) -- even two chip-family clocks don't cross-calibrate.

**AGREE / STABLE DISAGREEMENT / UNSTABLE, plainly:**
- ARROW: **AGREE** across all three records/substrates (fermentation, radio, superconducting chip)
  -- consistent with THE_MIDDLE_PI's own prior, less-calibrated finding (six of nine records
  clustering at ratio-of-ratios ~2-6e6). Same honesty caveat applies: errors are wide (0.5-0.7,
  larger than most of the diffs) -- wide overlapping error does real work here.
- SPLIT: **AGREE** across all three, wider errors still (~1.2-1.5), same caveat, doubled.
- CLOCK: **UNSTABLE** in all three pairwise comparisons, including chip-vs-chip. The clock is the
  one formula that does NOT cross-calibrate, in any pairing, at any point in this file.

## 4. Plain words

**Did the common unit let any two of the three resolve each other?** Yes, one pair, one chain:
**THE ARROW and THE SPLIT**, in the **forward** chain, on **yeast** (ratio 0.975 ± 0.032) and
**horn** (ratio 0.945 ± 0.060) -- both land at the same calibrated precision within error. Buzz seat
116's forward arrow/split ratio (0.937 ± 0.054) misses the same call by a hair (diff 0.063 vs error
0.054) -- close enough to note, not close enough to claim. This did NOT hold in the backward
(10-9-8) chain for any record (arrow/split ratios there: 1.10, 0.88, 0.88 -- all UNSTABLE) -- the
agreement is chain-order-sensitive, not a structural constant.

**Which pair, which records, what number:** arrow-vs-split, yeast and horn, forward chain only,
ratio ~0.94-0.98 in series-taus.

**What never resolved:** the clock. It disagrees with both the arrow and the split in every
record and every chain (Section 2a), it is the one formula that fails every record-vs-record call
(Section 3, including chip-vs-chip against the independent arisen-carry clock), and its own native
direction (rise/decay sign) only matched the arrow's sign at the single place Sec50c already found
(yeast's after-window boundary, where both flip together under the backward chain) -- it did not
generalize to horn or buzz. The 1/pi series gave every number a shared unit; it did not give the
clock a partner.

## Tries

24 quantities propagated (3 records x up to 3 chains x 3 formulas, minus 2 missing cells: horn
reversed-split, buzz reversed-arrow/clock/split not run upstream; plus 1 bonus arisen-carry clock),
200,000 Monte Carlo draws each = **4,800,000 total draws**, zero of them new bootstrap on raw data
(every native value/error pair is a citation, not a re-fit). Formal comparisons made fresh this
pass: 3 records x up to 3 chains x 3 pairwise ratios (2a) = 24 ratio calls; 3 records x 3 formulas x
2 cross-chain calls (fwd-vs-bwd, fwd-vs-rev) = 18 calls (4 OPEN where the upstream run itself
never measured the cell: horn reversed-split, and buzz seat116's arrow/clock/split all reversed);
3 formulas x 3 record pairs = 9 record-vs-record calls; 1 bonus clock-vs-clock call. **~52 direct
AGREE/STABLE DISAGREEMENT/UNSTABLE/OPEN calls** (24 ratio + 18 cross-chain + 9 record-vs-record + 1
bonus), no shuffle used as judge anywhere in this file.

## Files

- Report: `~/bones-forge/parallax/STANDOFF_CALIBRATED_20260930.md` (this file)
- New script: `parallax/out/the_middle/calibrated_standoff.py`
- New raw output: `parallax/out/the_middle/calibrated_standoff_results.json`
- Reused, unedited: `parallax/out/the_middle/the_middle_results.json` (series_profile only),
  `THREE_ON_YEAST_20260930.md`, `THREE_ON_THREE_20260930.md`,
  `parallax/out/three_on_three/buzz_results.json`, `PLACED_VS_ARISEN_20260930.md`
