# THREE FORMULAS ON ONE RECORD -- yeast NADH trace, 2026-09-30

Answers THIRD_RUNG_20260928.md Sec50 ("one of three; each needs a data point from the other...
never yet run all three on ONE record"). Record: `parallax/out/yeast/nadh_fig4_raw_digitized.csv`,
1531 points, dt = 1.31 s (median), Weber/Prokazov/Zuschratter/Hauser 2012 PLoS ONE Fig 4a, 0.1%-density
NADH fluorescence, quiet -> synchronized oscillation (~800-1400 s, period 48.7 s inside) -> quiet.
Scripts: `parallax/out/yeast/three/three_formulas.py` (numpy only, no scipy on this box). Raw output:
`parallax/out/yeast/three/results.json`. No expectation written first. Shuffle floor = 1000 per test
throughout. Three windows, no binary split: before (200-800 s), during/synchrony (800-1400 s),
after (1400-2000 s), plus whole record.

## Detrend choice (THE ARROW's cutoff test)

Baseline removed with a wide running median before computing A(k). Three widths tried, in points,
scaled to the 48.7 s period (dt=1.31 s, ~37.2 pts/period): narrow ~4 periods (149 pts), primary ~8
periods (297 pts, used for the main run), wide ~16 periods (595 pts). Repeated the "during" window's
best-k search on all three:

| width | best k (s) | A | z |
|---|---|---|---|
| narrow (~4P) | 115.28 | -98,762,381 | -4.18 |
| primary (~8P) | 115.28 | -99,144,751 | -3.98 |
| wide (~16P) | 79.91 | +84,432,566 | +3.73 |

Narrow and primary agree (same k, same sign). Wide flips both the best-k location and the sign --
the detrend width matters. Primary (~8 periods) kept as the reported choice; the sign flip at wide
width is logged as a real cutoff sensitivity, not papered over.

## 1. THE ARROW -- A(k) = <x_t^2 x_(t+k)> - <x_t x_(t+k)^2>

k from 1 sample to 3 periods (146.1 s, 112 k-values), 1000 shuffles per k per window (448,000 shuffle
draws for the 4 windows; +4,000 for the reversed-trace check; +224,000 for the 2-width cutoff test on
"during" = 676,000 shuffle draws total, 676 k/window/width cells tested).

| window | n pts | best k (s) | A | z (vs floor) | reversed A | reversed z |
|---|---|---|---|---|---|---|
| before (200-800s) | 460 | 66.81 | -27,342,460 | -5.25 | +27,342,460 | +5.14 |
| during (800-1400s) | 460 | 115.28 | -99,144,751 | -3.98 | +99,144,751 | +3.90 |
| after (1400-2000s) | 459 | 81.22 | +5,907,466 | +5.80 | -5,907,466 | -5.39 |
| whole record | 1530 | 34.06 | +19,752,360 | +3.07 | -19,752,360 | -3.02 |

Arrow flips sign under time-reversal almost exactly (|A_rev| = |A|, sign flipped) in all four windows --
the statistic behaves as designed. Best |A| beyond floor: **after window, k=81.22 s** (z=5.80,
largest of the four). Sign pattern: negative before and during, positive after and on the whole record.

## 2. THE CLOCK -- C(g) = C0 exp(-g/tau)

Envelope via FFT analytic signal (no scipy Hilbert; same math). Tau fit by linear regression on
log(envelope), bootstrap n=1000 resamples per fit.

| | tau (s) | bootstrap tau mean +/- sd (s) | tau / period (48.7s) | log-fit residual |
|---|---|---|---|---|
| (a) coherence decay, autocorr envelope, during window, lags 1.3-145.4s | 784.6 | 795.3 +/- 73.7 | 16.1 | 0.043 |
| (b) decay after switch-off, t=1400-1999s | 688.2 | 690.9 +/- 66.9 | 14.1 | 0.582 |
| (c) rise before switch-on, t=200-799s (g=time-to-onset) | 1179.1 | 1223.9 +/- 275.2 | 24.2 | 0.590 |

All three tau are 14-24x the period and 1-2 orders of magnitude larger than the arrow's k's (67-115s).
(a)'s fit is tight (log-residual 0.04, tight bootstrap sd); (b) and (c) have much larger residuals
(0.58-0.59) and (c) has the widest bootstrap spread (sd 275s, larger than the window itself, 600s) --
read as a nearly-flat rise/decay over these window lengths, not a clean exponential; the reported tau
is a lower bound on "large" more than a tight number, especially for (c).

## 3. THE SPLIT -- D = outside - inside = S + P * crossing

Outside = peak wall-clock times inside the synchrony window (12 peaks, 11 cycles). Inside = cumulative
phase from the first peak using the window's mean period (48.65 s). Crossing = each cycle's own
interval minus the mean period (local wobble). Linear fit, 1000 label-shuffles of `crossing` for the
floor on P.

- S (shared offset) = 2.37 s
- P (per-cycle slope) = 0.500 (z = 2.76 vs shuffle floor, mean -0.0045 +/- 0.183)
- residual sd = 0.58 s, n=11 cycles

**Caveat, measured not asserted:** by construction D_i = cumsum(crossing_0..i) (telescoping identity,
since inside-time uses the SAME mean period that crossing is defined against) -- the last D is forced
to exactly 0. This is a real, reported number but it is testing whether cumulative wall-vs-beat drift
tracks the current cycle's own wobble (an autocorrelation-of-a-random-walk question), not an
independent "shared + per-cycle" decomposition free of that identity. n=11 is thin. Flagged, not
oversold.

## 4. THE STANDOFF

| question | arrow | clock | split | agree beyond errors? |
|---|---|---|---|---|
| best k vs tau or period | k: 67-115s (before/during/after) | tau: 688-1179s | -- | NO -- taus are 6-15x every arrow k; no k matches any tau or the 48.7s period itself (k's are ~1.4-2.4 periods) |
| clock direction vs arrow sign | sign: -,-,+ (before,during,after) | rise before (weak, tau>>window), decay after (weak, tau>>window) | -- | PARTIAL -- the arrow's sign flips at the same before/after boundary the clock treats as the transition, but (b)/(c)'s huge residuals (0.58-0.59) mean the clock's own "direction" is barely distinguishable from flat over these window lengths -- can't confirm the match beyond noise |
| split's per-cycle part vs clock's amplitude | -- | envelope amplitude (during, NADH counts) | P=0.500, z=2.76 on interval-wobble ("crossing"), not on the clock's NADH-envelope amplitude | NOT FILLED -- split's "crossing" (period wobble) and the clock's envelope (NADH amplitude) are different quantities on the same window; no number computed connecting them this pass |

**Read:** none of the three holes got a clean fill from the other two on this record. The arrow's
k's (67-115s, ~1.4-2.4 periods) sit an order of magnitude below every clock tau (688-1179s, 14-24
periods) -- the "hole" k needing tau, and tau needing a direction from A, do not converge on a shared
number here. The clock's own before/after fits are weak (residuals ~0.58) over windows too short to
pin an exponential, so "direction agrees with arrow's sign" is a coincidence-in-timing at best, not a
number-level match. The split's P=0.500 (z=2.76, the one nominally-significant number of the three) is
built on 11 cycles and a definitional identity (D is a cumulative sum of the same crossing it's
regressed against) and was never connected to the clock's own amplitude measure -- that hole (needs the
crossing size = C) stayed open. Net: the three formulas ran clean and each produced a number, but on
this one record they did not fill each other's holes -- they disagree in scale (arrow) or are too weak
to read (clock, before/after) or rest on a construction that needs a bigger n and an actual C-based
crossing size (split) before the standoff can be called either way.

## Tries

676 arrow k/window/width cells x 1000 shuffles = 676,000 shuffle draws, plus 4 reversed-trace checks
x 1000 shuffles = 4,000. Clock: 3 tau fits x 1000 bootstrap resamples = 3,000, plus the 3 direct fits.
Split: 1 regression + 1000 label-shuffles for the P floor. Total formal test count: 676 arrow cells +
4 reversed + 3 clock fits + 1 split fit = 684 point estimates; 683,000 + 3,000 + 1,000 = 687,000
resample/shuffle draws underneath them.

---

# BACKWARDS

Wayfinder: "run the standoff backwards and see what boogies." Two runs on the same record
(`parallax/out/yeast/nadh_fig4_raw_digitized.csv`, same three windows: before 200-800s, during/
synchrony 800-1400s, after 1400-2000s). Script: `parallax/out/yeast/three/backwards.py`. Raw
output: `parallax/out/yeast/three/backwards_results.json`. No expectation written first.

**Verdict rule, corrected mid-task by Wayfinder via the coordinator:** shuffles destroy time order
and then test for time order -- they can only refind themselves. Shuffle floors are still computed
and counted below (the task's own 1000-draw floor requirement), but they are NOT the verdict. The
verdict is a direct number-vs-number call using bootstrap errors from resampling the REAL data
(case-resampling real pairs/cycles, never label-shuffled): **AGREE** if the difference is inside
the combined bootstrap errors, **STABLE DISAGREEMENT** if outside but same sign/direction in all
windows tested, **UNSTABLE** otherwise. Chained-hole checks are ratios only, no p-values.

## RUN A: order 10 -> 9 -> 8 (split -> message unit -> arrow -> clock)

### Step 1 -- THE SPLIT FIRST, and the message unit

During-window cycle-by-cycle record (12 peaks, 11 cycles), same as the forward run. Crossing
sizes (each cycle's interval minus the window's mean period, 48.65 s -- this is what the forward
script itself already calls "local amplitude"), s: -0.63, +2.00, -1.09, +2.80, -3.85, +5.06, -4.02,
+0.17, +0.77, -0.30, -0.90 (11 values, full list in JSON). Re-running the split's own regression on
this same data reproduces **S = 2.37 s, P = 0.500** exactly (bootstrap sd on P, case-resampling the
11 real (crossing, D) pairs: 0.123) -- identical to the forward-run numbers by construction, since
this step's spec is "report the split's S and P again."

**Message unit** = one cycle weighted by |crossing| (its own amplitude). Characteristic lag:
**k\* = 48.81 s, spread (weighted sd) = 2.63 s.** k\*/period(48.7s) = **1.0023** -- the amplitude-
weighted mean cycle length lands almost exactly on the forward run's period, essentially by
construction (weighting cycles by their own wobble doesn't move the mean length far from the raw
mean period when the wobble is roughly symmetric).

### Step 2 -- THE ARROW at k\*, k\*/2, 2k\*, on the message-unit series

Built by interpolating each window's own per-cycle crossing series onto the original dt=1.31s grid,
then running the same A(k) formula on that series (not the raw trace) at k=24.4s, 48.81s, 97.62s.

| window | k=k*/2 | k=k* | k=2k* |
|---|---|---|---|
| before | A=-10.82, boot-SNR=-3.25 | A=+21.92, boot-SNR=1.76 | A=+9.29, boot-SNR=1.77 |
| during | A=-0.02, boot-SNR=-0.17 | A=+0.39, boot-SNR=0.92 | A=-0.49, boot-SNR=-4.46 |
| after | A=-237.7, boot-SNR=-1.43 | A=-503.5, boot-SNR=-2.27 | A=+2531.0, boot-SNR=5.96 |

(boot-SNR = A / bootstrap sd from case-resampling the real (x_t,x_t+k) pairs, 1000 draws; shuffle
floors also computed, 1000 draws each of 9 cells = 9,000 shuffle draws, logged in JSON, not the
verdict.) At k=k\* specifically, **after** has the largest bootstrap SNR (2.27) among the three
windows -- picked as the pointing window for Step 3. Note in passing: 2k\* in the after window reads
far stronger (SNR 5.96) than k\* itself -- the message-unit arrow is not simply strongest at the
split's own handed-back lag.

**Forward-chain vs. backward-chain, arrow at k\*:** the forward-chain number here is A computed on
the RAW detrended trace at the same k=k\* (not the raw trace's own best-k); the backward-chain
number is A on the message-unit series. These are NOT comparable in absolute value -- the raw trace
is in photon-count^3 units, the message-unit series is in seconds^3 (crossing is a time wobble) --
so a literal magnitude/fraction call is not physically meaningful and is reported as raw numbers
only, not scored:

| window | forward (raw@k*) | backward (msg-unit@k*) | sign match? |
|---|---|---|---|
| before | +18,929,948 (boot sd 5,653,083) | +21.92 (boot sd 12.49) | yes (+/+) |
| during | +15,252,875 (boot sd 10,656,018) | +0.39 (boot sd 0.43) | yes (+/+) |
| after | +237,900 (boot sd 1,714,909) | -503.5 (boot sd 221.9) | **no (+/-)** |

Sign agrees in before/during, flips in after -- the one window Step 2 picked as "pointing."

### Step 3 -- THE CLOCK inside the arrow's window (after)

Fit on the message-unit (crossing) series' envelope in the after window (same exponential-decay
method as the forward clock's (b)): **tau_backward = -637.6 s** (bootstrap mean -638.0, sd 58.3) --
**negative**, meaning the wobble-amplitude series is *growing*, not decaying, across the after
window. Forward run's raw-signal tau in the same window: **tau_forward = +688.2 s** (bootstrap sd
66.9). Sign is opposite. Call: **UNSTABLE** (difference 1325.7 s vs combined bootstrap error 125.2
s -- far outside, and only one window tested so "stable direction across windows" doesn't apply).

**The three holes, run backward:**
- k\* vs tau: k\*=48.81s, tau_backward=-637.6s (sign flipped from tau_forward=+688.2s) -- ratio
  k\*/tau_forward = 0.071, **not within a factor of 2**.
- arrow sign vs clock direction: arrow at k\* in the after window is negative (-503.5); the
  backward clock there is growing (negative tau, i.e. rising), the forward clock there is decaying
  (positive tau). The arrow's sign does NOT cleanly match either -- it disagrees with the forward
  clock's decay and only nominally "matches" the backward clock's rise by both being negative,
  which is a units/sign-convention coincidence, not a physical match.
- split's P vs clock's amplitude (now called "amplitude" for both, still different physical units --
  crossing is a time wobble in seconds, envelope is photon counts): correlation of |crossing| in
  the after window against the local raw envelope at the same cycle times, r = **-0.022** (bootstrap
  mean +0.011, sd 0.258) -- **no connection, r is deep inside its own bootstrap noise.**

## RUN B: time-reversed trace, all three formulas, same windows

| formula | window | forward | reversed | call |
|---|---|---|---|---|
| arrow (best-k) | before | -27,342,460 | +27,342,460 | AGREE (magnitude, antisymmetric by design) |
| arrow (best-k) | during | -99,144,751 | +99,144,751 | AGREE (magnitude) |
| arrow (best-k) | after | +5,907,466 | -5,907,466 | AGREE (magnitude) |
| arrow (best-k) | whole | +19,752,360 | -19,752,360 | AGREE (magnitude) |
| clock tau | during (coherence) | 784.6 s | 784.6 s | AGREE (diff 2e-13 s) |
| clock tau | after (decay) | +688.2 s | **-690.6 s** | UNSTABLE (sign flips; diff 1378.8 s vs combined error 134.8 s) |
| clock tau | before (rise) | 1179.1 s | 1183.4 s | AGREE (diff 4.3 s vs combined error 538.8 s) |
| split P | during | 0.500 | 0.500 | AGREE (diff ~1.6e-14, no sign flip) |

Arrow flips sign exactly under reversal in all four windows, as designed (antisymmetric statistic --
confirms the forward run's own note, magnitudes match to float precision). The clock's after-window
tau also flips sign under reversal (a decay becomes a rise when you play it backward) -- the one
clock fit that behaves like the arrow. The during-window coherence tau and before-window rise tau do
NOT flip and barely move (both AGREE, both computed as functions of lag/time-to-onset that don't
distinguish direction the way a straight decay-vs-time does). The split's P doesn't flip and doesn't
move at all under mirroring the during-window peak times -- it's insensitive to time-reversal here.

## What boogied and what didn't

**Boogied (a real, above-noise disagreement or flip, backed by direct numbers not shuffle floors):**
- The after-window clock flips sign under both backward chaining (message-unit tau goes negative,
  -637.6s vs forward's +688.2s) and time-reversal (-690.6s vs +688.2s) -- the only formula/window
  that responds to BOTH backward operations the same way, and the only one where forward-vs-backward
  is a clean UNSTABLE call, not a units mismatch.
- The arrow's sign in the after window flips between raw-trace-at-k\* (+237,900) and message-unit-
  at-k\* (-503.5) -- disagreeing where before/during agree in sign.
- k\* (48.81s, essentially the period) sits nowhere near any tau (688-1223s forward, or the negative
  637.6s backward) -- ratio 0.071-0.076, not within a factor of 2, same conclusion as the forward
  run's standoff, now confirmed from the other direction.

**Didn't boogie (agreed, or too noisy to call):**
- The arrow's antisymmetry under reversal (all four windows, to float precision) -- expected, and
  confirmed cleanly by direct magnitude comparison, no shuffle needed.
- The during- and before-window clock taus barely move under reversal (both AGREE, small diffs well
  inside combined bootstrap error).
- The split's S, P reproduce exactly when the same during-window data is re-run (by construction),
  and P doesn't move under mirroring the peak times (AGREE, no sign flip) -- the split is the most
  reversal-insensitive of the three formulas.
- Split-crossing vs. clock-envelope correlation (r=-0.022, bootstrap sd 0.258) -- no connection,
  consistent with the forward run's "not filled" verdict on this same hole.

## Tries

Run A: 3 windows x 3 k-variants x (1000 bootstrap + 1000 shuffle floor) = 18,000 draws for Step 2;
1 clock fit x 1000 bootstrap for Step 3; 1 split re-fit x (1000 bootstrap + 1000 shuffle floor) for
Step 1; 1 correlation x 1000 bootstrap for the split-vs-clock hole. Run B: 3 clock refits x 1000
bootstrap = 3,000; 1 split refit x (1000 bootstrap + 1000 shuffle floor) = 2,000; arrow reversed
numbers reused from the forward run's own 4,000 reversed-trace shuffle draws (not recomputed).
Total new draws this pass: 18,000 + 1,000 + 2,000 + 1,000 + 3,000 + 2,000 = **27,000**, on top of
the forward run's 687,000. Formal point estimates (bootstrap means/verdicts, not counting each
underlying draw): 9 arrow cells (Step 2) + 1 clock fit (Step 3) + 1 split refit (Step 1) + 1
correlation + 3 clock refits (Run B) + 1 split refit (Run B) + 4 arrow reuses (Run B) = **20** new
formal comparisons, each with a bootstrap error bar and a direct AGREE/STABLE DISAGREEMENT/UNSTABLE
call (not a p-value).

---

## ERRORS, DIVERGENT FITS, AND BOOTSTRAP ERROR SIZES (addendum)

Wayfinder: "DO NOT THROW AWAY ERRORS." Every fit attempt run for this backwards pass is reported
below, including the ones not used for the headline numbers above, with its exact value and its
bootstrap error sitting in the same table as the results -- not a footnote. Full numbers in
`backwards_results.json` (`run_A_10_9_8.step3_clock_all_windows` now carries all three window fits,
not just the pointing window; every `*_boot_sd`/`*_bootstrap_sd` field is a logged error size).

### Every clock fit attempted on the message-unit series (Step 3 candidates, all 3 windows)

The script only used the "after" window's fit for the headline Step 3 number (it was the pointing
window). The other two were computed too and are reported here in full, one of them divergent:

| window | tau (point est., s) | bootstrap mean (s) | bootstrap sd (s) | n fit pts | log-resid | status |
|---|---|---|---|---|---|---|
| before | **250,765.8** | 20,034.7 | **517,580.1** | 408 | 0.245 | **DIVERGENT** -- bootstrap sd (517,580) is 2.06x \|tau\| itself; the fit is not usable, reported as a failure, not a number |
| during | 40.39 | 40.35 | 0.696 | 111 | 0.185 | clean -- tightest fit of the three, not used because "during" wasn't the pointing window |
| after | -637.55 | -641.5 | 56.4 | 358 | 0.316 | used (pointing window); sign-flipped vs. forward's raw-trace tau (+688.2s), reported above |

The before-window message-unit clock fit is a genuine failure, not a small number: fitting an
exponential to that window's wobble-amplitude envelope produces a tau five orders of magnitude
larger than the window itself (600s) with a bootstrap spread larger than the point estimate --
functionally "no decay/rise detectable," logged here rather than dropped.

### No exceptions / no NaN or Inf in the saved JSON

Every field in `backwards_results.json` was walked and checked for NaN/Inf after the run: **zero**
found. Bootstrap loops did not silently drop failed resamples for the clock fits used above (all
`bootstrap_n_ok = 1000/1000` including the divergent "before" fit -- it converged to a bad number
every time, not intermittently). The one place resamples get silently dropped by construction is
the split-crossing-vs-clock-envelope correlation bootstrap (skips a resample only if either
resampled vector has zero variance): **0 of 1000 dropped** in the after-window run used above.
Step 2's 9 arrow/message-unit cells all computed (none skipped for insufficient points; smallest
series was 358 interpolated points, well above the k used).

### Bootstrap error sizes, all reported numbers, as data

| formula/quantity | count | smallest boot-sd | largest boot-sd | note |
|---|---|---|---|---|
| arrow, message-unit series (Step 2, 9 cells) | 9 | 0.110 (during, 2k\*) | 424.5 (after, 2k\*) | in crossing-seconds^3 units |
| arrow, raw trace at k\* (forward-chain comparison, 3 cells) | 3 | 1,714,909 (after) | ~10.5-10.7M (during) | in photon-count^3 units -- not comparable to the row above |
| clock, message-unit series (Step 3, 3 windows) | 3 | 0.696 (during) | **517,580 (before, DIVERGENT)** | seconds |
| clock, raw trace (forward + reversed, 6 fits) | 6 | 66.9 (after, forward) | 275.2 (before, forward) | seconds |
| split P (forward / backward-chain / reversed) | 3 | 0.1226 | 0.1236 | dimensionless slope |
| split-crossing vs. clock-envelope correlation r | 1 | -- | 0.258 | the only estimate computed |

**Named largest, overall, with the units caveat stated plainly:** the divergent before-window clock
fit's bootstrap sd (517,580 s) is the largest error bar that corresponds to a value meant to be read
on its own physical scale (seconds) -- and it exceeds the point estimate it's attached to, which is
exactly why that row is flagged DIVERGENT rather than reported as a number with error bars around it.
The arrow's raw-trace bootstrap sd (~10.5-10.7M, during window) is nominally larger in raw magnitude
but is in photon-count^3 units, not seconds, and was already noted above as not comparable across
the forward/backward chain's two different unit systems. **Named smallest:** 0.110, the arrow's
message-unit statistic at 2k\* in the during window -- the tightest-behaved single number produced
in this whole backwards pass.
