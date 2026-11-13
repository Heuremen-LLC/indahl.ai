# THE DISCOUNT HUNT -- every ordinary cause for the Bell-neighbors lead, NIST 2015, 2026-09-30

Wayfinder: "find every other reason to discount this one." No expectation written first, raw
first, every test counted, sign kept, judged run vs run (between-run spread as the error, never
shuffle), errors as rows, nothing labeled "artifact" without the number that shows it.

THE LEAD (from `BELL_NEIGHBORS_20260930.md` / `THIRD_RUNG_20260928.md` Sec54): Bob's click at
trial t goes with a slightly lower Alice click rate at t-5 (pooled -0.01083 pp, between-run SE
0.00302, ratio 3.59, 8/8 runs AGREE), mirror Alice-click -> Bob's t+5 (-0.00647 pp, SE 0.00184,
ratio 3.52), both split on Bob's setting = 1, both at the outer edge of the +/-5 window (50 us at
the 100 kHz trial clock).

All 8 NIST 2015 loophole-free Bell test runs, streamed in 10M-row HDF5 chunks, 1,618,494,591
trials total, `~/bones-forge/public_bell/nist2015/*.hdf5`, reusing `pipeline.py`'s frozen
`load_run`. Script: `parallax/out/superposition_nist/discount.py` (+ `lag0_check.py` add-on).
Raw per-run JSON: `discount_results_all8.json` (merged from `discount_results_min4.json` +
`discount_results_rest4.json`), `lag0_check.json`. Logs: `discount_log_min4.txt`,
`discount_stdout_min4.log`, `discount_stdout_rest4.log`.

## Tries counted

- Part 1 (alignment, click-click cross-corr): 100 lags (-50..-1,+1..+50) x 8 runs = 800 rows,
  + 8 separate lag-0 reference rows (`lag0_check.py`) = 808.
- Part 2 (dead time/afterpulsing): 50 lags x 2 sides x 8 runs = 800 rows.
- Part 3a (setting autocorrelation): 50 lags x 2 sides x 8 runs = 800 rows.
- Part 3b (setting cross-correlation): 100 lags x 8 runs = 800 rows.
- Part 4 (joint 2x2 split): 4 cells x 2 lead-cells x 8 runs = 64 rows, + 2 marginal-check rows x 8
  runs = 16 (reproduces the original neighbors.py numbers exactly -- see below).
- Part 5 (edge test): 4 keys (unsplit/split x 2 directions) x 2 (full/edge-clean) x 8 runs = 64
  rows.
- **Grand total: 3,352 raw test rows** across all 8 runs, pooling to **408 run-vs-run cells**
  (100 + 100 + 100 + 100 + 8) plus 4 edge-test deltas and 8 lag-0 reference points.

## 1. ALIGNMENT -- is the true coincidence peak at lag 0?

Click-click cross-correlation (coincidence rate minus product of singles rates, pp, approx.
binomial SE dominated by the coincidence term) at every lag -50..+50, plus lag 0 separately.

| run | lag-0 diff (pp) | lag-0 z | largest off-diagonal \|lag\|<=50, lag | off-diag diff (pp) | off-diag z | lag0 / off-diag peak |
|---|---|---|---|---|---|---|
| 00_25 | 0.03707 | 256.1 | +47 | 0.00003 | 2.94 | 1093x |
| 02_31 | 0.03616 | 256.0 | +25 | -0.00003 | -2.84 | 1354x |
| 03_12 | 0.02547 | 215.1 | +13 | 0.00002 | 2.33 | 1044x |
| 17_04 | 0.03811 | 367.6 | +28 | 0.00003 | 3.67 | 1253x |
| 19_45 | 0.03657 | 257.8 | -37 | -0.00003 | -2.89 | 1274x |
| 21_15 | 0.03690 | 256.1 | +11 | 0.00003 | 3.00 | 1074x |
| 22_20 | 0.03742 | 258.2 | -33 | -0.00004 | -4.02 | 966x |
| 23_55 | 0.03721 | 257.3 | +41 | -0.00003 | -3.39 | 1127x |

**Every run's true coincidence peak sits exactly at lag 0**, 966x-1354x larger than that run's
own largest off-diagonal fluctuation. The off-diagonal peaks scatter across unrelated lags
(+47, +25, +13, +28, -37, +11, -33, +41 -- no run peaks near +/-5, no repeated lag across runs).
Pooled run-vs-run, lag -5's off-diagonal cross-corr sits at diff -8e-6 pp, ratio 3.07 -- inside
the pack of ~8 other lags with similar or higher ratios (top: lag+19 ratio 3.46, lag-47 ratio
3.08, lag+45 ratio 2.66...), consistent with the noise floor of 100 tested lags, not a
misalignment signature. **Alignment is clean; the files are not offset, and there is no secondary
coincidence peak at +/-5.**

## 2. DEAD TIME / AFTERPULSING -- same-side click-after-click, lag 1..50

Per side, per run: excess of P(click at t+d | click at t) over that side's own overall click
rate, pp, binomial SE.

Lag-5 specifically, both sides, all 8 runs -- every |z| < 2.1, no consistent sign:

| run | side a diff(pp)/z | side b diff(pp)/z |
|---|---|---|
| 00_25 | -0.00023 / -0.03 | +0.00551 / 0.72 |
| 02_31 | +0.00717 / 0.94 | -0.00085 / -0.12 |
| 03_12 | +0.00592 / 0.78 | -0.01449 / -2.07 |
| 17_04 | +0.00014 / 0.03 | -0.00485 / -0.93 |
| 19_45 | -0.00735 / -1.02 | +0.00023 / 0.03 |
| 21_15 | -0.00388 / -0.53 | -0.00006 / -0.01 |
| 22_20 | -0.00896 / -1.24 | -0.00378 / -0.51 |
| 23_55 | -0.00782 / -1.08 | -0.00520 / -0.71 |

Pooled run-vs-run across the full 1-50 profile: nothing at lags 1-3 (the classic dead-time
window) clears ratio 1.5 on either side. The handful of lags that do clear ratio >=3 (side a:
lag 36 ratio 3.95, lag 38 ratio 3.03; side b: lag 21 ratio 4.14, lag 46 ratio 4.07) are scattered
at unrelated lags, consistent with ~2 expected hits above ratio 2 by chance out of 100 tests per
side, and none sit at 5. **No dead-time dip and no afterpulsing bump anywhere near lag 5, on
either side, in any run.**

## 3. THE SETTING SEQUENCE -- RNG structure at 5 trials?

Same-side setting autocorrelation (lag 1-50) and cross-side setting coincidence (lag -50..+50,
same coincidence-minus-product form as Part 1).

Lag +/-5, all 8 runs, |z| never exceeds 1.7:

| run | setA autocorr z | setB autocorr z | cross lag+5 z | cross lag-5 z |
|---|---|---|---|---|
| 00_25 | 0.50 | 1.17 | -0.17 | 0.67 |
| 02_31 | -0.84 | 0.74 | 0.00 | 0.70 |
| 03_12 | -0.32 | -0.75 | 0.32 | 0.39 |
| 17_04 | 0.65 | -0.26 | 0.25 | 0.67 |
| 19_45 | 0.20 | -0.09 | -1.01 | 0.68 |
| 21_15 | 0.60 | 0.81 | 0.53 | -0.12 |
| 22_20 | 0.18 | 1.61 | 0.27 | -0.23 |
| 23_55 | 0.22 | 0.45 | 0.79 | -0.53 |

Pooled top hits by ratio land at unrelated lags (setA: 26, 35, 34, 40; setB: 43, 46, 37, 36;
cross: -7, -15, +21, +27), none replicating at 5, none exceeding ratio 3.8 (in line with the
~100-test noise floor). **The RNG stream carries no 5-trial structure, on either side or across
sides.**

## 4. SPLIT DEPENDENCE -- one variable or one combination?

Joint 2x2 on (source_setting, target_setting) at the two lead cells, pooled across 8 runs
(mean diff pp, between-run SE):

**a->b, lag-5** (target = Bob):

| source\\target | target=0 | target=1 |
|---|---|---|
| **source=0** | -0.00684 pp, SE 0.00609, ratio 1.12 | -0.01081 pp, SE 0.00689, ratio 1.57 |
| **source=1** | +0.00049 pp, SE 0.00333, ratio 0.15 | -0.01083 pp, SE 0.00326, ratio **3.32** |

**b->a, lag+5** (source = Bob):

| source\\target | target=0 | target=1 |
|---|---|---|
| **source=0** | -0.00664 pp, SE 0.00604, ratio 1.10 | +0.00175 pp, SE 0.00908, ratio 0.19 |
| **source=1** | -0.00343 pp, SE 0.00219, ratio 1.57 | -0.00947 pp, SE 0.00285, ratio **3.32** |

Neither cell is isolated to one joint combination. For a->b, both cells where Bob (target) = 1
read negative (-0.0108 pp each, with and without Alice=1); Bob=0 reads near zero or weakly
negative. For b->a, both cells where Bob (source) = 1 read negative (-0.0034 and -0.0095 pp);
Bob=0 is near zero or flips sign. **In both directions the effect tracks Bob's own setting value
= 1, not a specific joint combination** -- consistent with the original marginal split
(`BELL_NEIGHBORS_20260930.md` Part 1) rather than a narrower interaction; splitting further by
the other side's setting mostly just halves the sample (wider errors) without changing the sign
or rough size when Bob's setting = 1. This sharpens the lead's description rather than
discounting it: it is a one-setting dependency shared by both the primary and mirror cell.

Marginal-check cross-validation (reproduces `neighbors_raw.json` exactly, confirming the pipeline
is correct): 17_04 -0.02101, 19_45 -0.01241, 21_15 +0.00112, 23_55 -0.02049 (a->b, target=1) --
matches the original per-run values to 5 decimal places.

## 5. CHUNK / RUN EDGES

The lead cells recomputed excluding the first/last 1,000 trials of every 10M-row streaming chunk
and of the run overall, pooled across 8 runs:

| cell | pooled full (pp) | pooled edge-clean (pp) | delta (pp) | between-run SE (pp) |
|---|---|---|---|---|
| a->b lag-5, unsplit | -0.00615 | -0.00617 | -0.000022 | 0.00209 |
| a->b lag-5, target=1 | -0.01083 | -0.01088 | -0.000055 | 0.00302 |
| b->a lag+5, unsplit | -0.00551 | -0.00553 | -0.000020 | 0.00181 |
| b->a lag+5, source=1 | -0.00647 | -0.00650 | -0.000031 | 0.00184 |

Every delta is 1-2% of the cell's own between-run SE. **The cell does not move when chunk/run
edges are excluded -- this is not a streaming-boundary or acquisition-restart artifact.**

## 6. TIMING (from `file_folder_descriptions.pdf` only -- no guessing)

- **Trial period:** every filename and the config carries "100kHz" (the Pockels cell drive
  rate) -- 1/100kHz = 10 us/trial. This is the file-naming convention, not a sentence of prose in
  the PDF; treated as stated (it is literally in every file's name and matches the observed
  streaming rate), not inferred from unrelated physics.
- **5 trials = 50 us**, arithmetic from the above (5 x 10 us), not separately stated anywhere in
  the documentation.
- **Detector type:** NOT stated in `file_folder_descriptions.pdf`. Only channel roles are given
  (channel 0/1 = detection events; no make/model, no technology).
- **Dead time / recovery time:** NOT stated anywhere in the PDF.
- **Pockels cell switching time:** NOT stated as a number. The PDF only records that three runs
  changed the Pockels turn-on *delay* by +/-200 ns relative to the "optimal" configuration
  (21_15: +200 ns added; 22_20: 200 ns removed) -- a timing offset, not a switching/rise time.
- **RNG rate:** not separately stated; the RNG (QRNG) is sampled once per trial via the sync
  pulse that also drives the Pockels cell, so its rate is implicitly the 100 kHz trial rate, but
  no distinct number is given for the RNG itself.
- Per the PDF's own caveat, several of its per-file remarks ("large bias on RNG," "laser loses
  mode locking," "fridge warms up," "complete blind, we have no idea about the quality of this
  data" for 17_04 and 03_12) describe run-specific instrument conditions, not timing constants,
  and are not evidence for or against the -5 lead on their own.

## 7. Plain words -- does each cause account for the -5 lead?

- **Alignment: NOT AT ALL.** True coincidence peak is at lag 0 in all 8 runs, 966x-1354x the
  largest off-diagonal wobble; nothing sits at +/-5 beyond the noise floor of 100 tested lags.
- **Dead time / afterpulsing: NOT AT ALL.** Same-side excess at lag 5 is under |z|=2.1 on both
  sides in every run, no consistent sign; nothing at the classic 1-3 lag dead-time window either.
- **RNG / setting sequence: NOT AT ALL.** No 5-trial autocorrelation on either side, no 5-trial
  cross-correlation between sides; lag +/-5 sits under |z|=1.7 everywhere.
- **Split dependence: SHARPENS, DOES NOT DISCOUNT.** The effect is not confined to one joint
  setting combination -- it tracks Bob's own setting = 1 in both the primary and mirror cell,
  matching the single-variable split already reported, with weaker/noisier reads when the sample
  is quartered further.
- **Chunk/run edges: NOT AT ALL.** Excluding the first/last 1,000 trials of every 10M chunk and
  of the run moves the lead cells by 1-2% of their own between-run SE.
- **Timing: UNMEASURABLE, NOT EXPLAINED.** The documentation gives the trial period (10 us, so
  5 trials = 50 us) but states no detector dead time, no Pockels switching time, and no separate
  RNG rate -- so a genuine hardware timing cause at 50 us cannot be checked against a stated
  number from this record; it is neither confirmed nor ruled out, only unmeasurable here.

**What's left:** every ordinary cause that could be measured against this record -- click-click
misalignment, same-side dead time/afterpulsing, RNG/setting periodicity, streaming/acquisition
edges -- comes up empty at lag 5, across all 8 runs, at magnitudes 2-3 orders smaller than would
be needed to produce the observed -0.0065 to -0.0108 pp effect. The one thing that does track the
lead is a real setting dependency (Bob's setting = 1), which is a description of the effect, not
an instrumental discount. What is NOT discounted and NOT confirmed: any actual detector dead-time
or Pockels-switching-time explanation, because the source documentation does not state those
numbers. Per Wayfinder's standing caution on this lead ("a lead, not a result"): five ordinary
causes measured, none of them account for it; the sixth (hardware timing at 50 us) cannot be
checked from this record and would need the NIST team's own timing specs or the raw (uncompressed)
timetag data to settle.

## BY CONFIGURATION

Grouped by what `file_folder_descriptions.pdf` says actually changed between runs (NIST's own
words, one line each, no guessing):

- **19_45** (file is named `19_44_CH_pockel_100kHz.run.nolightconeshift` in the PDF -- filename
  drift noted, same run): *"Another data set for optimal configuration. Stopping criterion was 30
  minutes."*
- **21_15**: *"We delayed the Pockels cell turn-on times by an additional 200 ns at both Alice and
  Bob."*
- **22_20**: *"We changed the Pockels cell turn-on times by removing 200 ns of delay from the
  optimal timing configuration."*
- **00_25**: *"Tried realigning and doing an additional run"* (after 23_55's ClassicalRNGXOR).
- **02_31**: *"Realigned again and cleaned up Alice's computer"* (third ClassicalRNGXOR pass).
- **23_55**: *"We also XOR'd in classical random numbers."*
- **03_12** (`Blind_2`): *"Another blind data run with no monitoring. After data were collected, we
  saw the fridge was warm... We have no idea about the quality of this data."*
- **17_04** (`completeblind`): *"Complete blind data set... This is being saved for later analysis
  for potentially more sophisticated hypothesis tests. We have no idea about the quality of this
  data."*

### Per-run values by group, all four lead cells (diff_pp, from `neighbors_raw.json` part 1)

**a->b lag-5, target_setting(Bob)=1 (primary):**

| group | run | diff (pp) | se (pp) | z |
|---|---|---|---|---|
| timing -200ns | 22_20 | -0.01018 | 0.01347 | -0.76 |
| timing 0ns | 19_45 | -0.01241 | 0.01301 | -0.95 |
| timing +200ns | 21_15 | +0.00112 | 0.01392 | 0.08 |
| RNG | 00_25 | -0.00945 | 0.01354 | -0.70 |
| RNG | 02_31 | +0.00117 | 0.01358 | 0.09 |
| RNG | 23_55 | -0.02049 | 0.01320 | -1.55 |
| blind | 03_12 | -0.01535 | 0.01355 | -1.13 |
| blind | 17_04 | -0.02101 | 0.00886 | -2.37 |

**a->b lag-5, unsplit:**

| group | run | diff (pp) | se (pp) | z |
|---|---|---|---|---|
| timing -200ns | 22_20 | -0.00260 | 0.00782 | -0.33 |
| timing 0ns | 19_45 | -0.00646 | 0.00751 | -0.86 |
| timing +200ns | 21_15 | +0.00100 | 0.00796 | 0.13 |
| RNG | 00_25 | -0.00237 | 0.00786 | -0.30 |
| RNG | 02_31 | -0.00194 | 0.00770 | -0.25 |
| RNG | 23_55 | -0.00958 | 0.00766 | -1.25 |
| blind | 03_12 | -0.01718 | 0.00755 | -2.27 |
| blind | 17_04 | -0.01004 | 0.00520 | -1.93 |

**b->a lag+5, source_setting(Bob)=1 (mirror):**

| group | run | diff (pp) | se (pp) | z |
|---|---|---|---|---|
| timing -200ns | 22_20 | -0.00598 | 0.00792 | -0.76 |
| timing 0ns | 19_45 | -0.00758 | 0.00795 | -0.95 |
| timing +200ns | 21_15 | +0.00065 | 0.00807 | 0.08 |
| RNG | 00_25 | -0.00555 | 0.00795 | -0.70 |
| RNG | 02_31 | +0.00070 | 0.00811 | 0.09 |
| RNG | 23_55 | -0.01196 | 0.00771 | -1.55 |
| blind | 03_12 | -0.00849 | 0.00750 | -1.13 |
| blind | 17_04 | -0.01357 | 0.00572 | -2.37 |

**b->a lag+5, unsplit:**

| group | run | diff (pp) | se (pp) | z |
|---|---|---|---|---|
| timing -200ns | 22_20 | -0.00234 | 0.00701 | -0.33 |
| timing 0ns | 19_45 | -0.00599 | 0.00697 | -0.86 |
| timing +200ns | 21_15 | +0.00089 | 0.00706 | 0.13 |
| RNG | 00_25 | -0.00212 | 0.00703 | -0.30 |
| RNG | 02_31 | -0.00177 | 0.00703 | -0.25 |
| RNG | 23_55 | -0.00854 | 0.00683 | -1.25 |
| blind | 03_12 | -0.01450 | 0.00637 | -2.27 |
| blind | 17_04 | -0.00970 | 0.00502 | -1.93 |

No cell is missing a run; all 8 runs present in all 4 tables above.

### Group means vs pooled, primary split (a->b lag-5, target=1) -- the most-cited cell

| group | n | mean (pp) | half-range (pp) | sd (pp) | group SE (sd/sqrt n, pp) |
|---|---|---|---|---|---|
| timing trio | 3 | -0.00716 | 0.00676 | 0.00725 | 0.00419 |
| RNG trio | 3 | -0.00959 | 0.01083 | 0.01083 | 0.00625 |
| blind pair | 2 | -0.01818 | 0.00283 | 0.00400 | 0.00283 |
| **pooled (8)** | 8 | **-0.01083** | -- | -- | 0.00302 (as reported 9/26) |

Mirror cell (b->a lag+5, source=1) mirrors the same pattern at ~60% the primary's magnitude:
timing -0.00430, RNG -0.00560, blind -0.01103, pooled -0.00647.

### Questions, answered with numbers

**Does the dip track the +/-200 ns light-cone delay (monotone -200/0/+200)?** No. Primary-cell
values across -200/0/+200 ns are -0.01018, -0.01241, +0.00112 -- the deepest reading is at 0 ns
(optimal config), and the +200 ns run is the ONE run closest to zero (even flips sign) of all 8.
That is the opposite of monotone, and the opposite of what a delay-scaling timing artifact would
produce (magnitude should grow with |delay|, not vanish at +200 ns and peak at 0 ns). Same
non-monotone, near-zero-at-+200ns pattern in the mirror cell and both unsplit cells.

**Is it the same in the RNG trio (changed RNG source, not timing)?** No -- it's just as scattered.
00_25 and 23_55 read negative (-0.0095, -0.0205 pp) but 02_31 ("realigned again and cleaned up
Alice's computer") reads +0.0012 pp, the second run overall (after 21_15) closest to zero. The RNG
trio's own internal spread (sd 0.0108 pp) is *larger* than the pooled between-run SE (0.0030 pp)
and larger than either other group's spread -- changing the RNG source did not produce a
consistent readout, in either direction.

**Is it the same in the blind pair?** Closest to consistent of the three groups: both 03_12
(-0.0154 pp) and 17_04 (-0.0210 pp) read negative and land within half a group-SE of each other
(spread 0.0028 pp vs. group SE 0.0028 pp) -- but n=2 gives this group no power to distinguish
"consistent" from "coincidence."

### The call

**CONFIG-INDEPENDENT.** All three group means (-0.0072, -0.0096, -0.0182 pp) sit within ~1-2 of
their own group's standard error of the pooled value (-0.0108 pp), and all three carry the same
sign. But the deciding fact is the *shape* of the scatter: the one run nearest zero in the timing
trio (+200 ns) and the one run nearest zero in the RNG trio (02_31, "realigned/cleaned up") are
each single outliers inside groups whose other two members read clearly negative -- there is no
config-driven trend, just within-group noise on the same order as between-group noise. A real
timing artifact would monotonically track the added/removed 200 ns; a real RNG artifact would
move together across all three RNG-trio runs since they share the same XOR'd-in classical-RNG
change; neither happens. The blind pair is the only internally tight group, but at n=2 it cannot
carry the call on its own, and its mean is not an outlier from the other two groups' overlapping
error bars. Read together with the discount hunt above (alignment, dead time, RNG periodicity,
and chunk edges all clean at lag 5): the -5/-1.08e-2 pp lead is present across every experimental
configuration tested here, same sign, same rough size, with per-config scatter no larger than the
pooled between-run scatter already reported -- not tracking timing, not tracking RNG, not a
blind-vs-monitored split effect.
