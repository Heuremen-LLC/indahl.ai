# THREE FORMULAS, THREE MORE RECORDS -- 2026-09-30

Same frozen instrument as `THREE_ON_YEAST_20260930.md` (THE ARROW A(k), THE CLOCK
C(g)=C0 exp(-g/tau), THE SPLIT D=S+P*crossing), plus the backwards chain (order
10-9-8: split -> arrow -> clock, each fed by the previous), run on three more
records: THE HORN DAY, THE ECHO SHOT ORDER (two gaps), THE BUZZ ROTATION
(positive control). Formula code is byte-identical to
`parallax/out/yeast/three/{three_formulas.py,backwards.py}`, refactored into
`parallax/out/three_on_three/core.py` so every record calls the same functions
(`core.arrow_stat`, `core.fit_exp_decay`, `core.split_fit`, etc. -- the shuffle
floor is reused across k within a window as a pure compute-cost optimization,
same statistic). Only the windowing, detrend scale, and data source differ per
record; that is documented per record below, not hidden. Scripts:
`parallax/out/three_on_three/{core,engine,load_horn,load_echo,load_buzz,
run_horn,run_echo,run_echo_reversed,run_buzz,final_table}.py`. Shuffle floor and
bootstrap = 1000 draws per test throughout, same as yeast. No expectation
written before running. numpy only.

**UNITS WARNING, read before the table:** yeast and horn are seconds-based
(real clock time). Echo and buzz are SHOT-based (no wall clock; k and tau are
in shots). A verdict cell comparing a shots-record to a seconds-record is
comparing raw numbers in DIFFERENT UNITS -- reported as computed, but "AGREE"
there means "close in raw magnitude despite the unit mismatch," not a physical
equivalence. Only same-unit pairs (yeast<->horn, echo<->buzz) are physically
comparable calls.

## Data pulled

- **Horn**: `ssh c-train-express /home/ctrai/horn/20260928_091702/power_4080.csv`
  -- pulled only `unix_time` + `db_4070_4090` (29,226 rows, ~163 KB), not the
  1.6 GB file. There is no column literally named "4080" or "4075-4085"; the
  narrowest available band around 4080 MHz, `db_4070_4090`, was used instead --
  documented substitution. Local copy: `three_on_three/horn_4080_pull.csv`.
  Timeline confirmed against `the-horn/field_notes.txt`: file starts
  09:17:11.89 EDT, ends 12:00:49.90 EDT, matching the day's log exactly.
- **Echo**: `parallax/out/echo_20260928_122733/E0_20.npz`, `E0_2000.npz` (m0,
  first-look, 1500 shots x 78 qubits, complex128). Geometry/readability gate
  (median-cloud threshold, SNR>=1.5) reused verbatim from
  `pre_measurement/pre_measurement.py` against the same 2000us calibration
  clouds -- 74/78 qubits readable total (varies 47-56 per window/gap as some
  qubits go flat in a given third). Per-qubit series thresholded to 0/1 at 0.5
  (pre_measurement's own convention).
- **Buzz**: `parallax/out/raw_repull/dat9o2tvr3kc73el5j20.npz` (job J2), seats
  80/100/116 (buzz_common.py's tile-8 fit seats), pubs p0__m1 (sign +1),
  p1__m1 (sign -1, conjugated per nu_precise.py's observed 1-cloud convention),
  4000 shots total. Per-shot unwrapped angle built directly from
  `buzz_common.iq_residual` + `np.unwrap(np.angle(.))`, since `unfold2.py`
  itself computes cross-job frequency-unfolding, not a per-shot angle series --
  documented substitution, functionally the same underlying per-shot phase.

## Raw, per record

**Horn** (home_before 09:17:11-10:40, at_horn 11:17-11:25, home_after
11:45-12:00, detrend width 289 pts = 1/5 of the at_horn window, dt=0.33s):
arrow best at_horn k=23.1s, A=+0.01687 +/- 0.00648 (boot, z=3.67 vs shuffle
floor); clock (during-role, autocorrelation coherence) tau=175.68 +/- 11.74s;
split (260 peaks, 259 cycles) S=11.59s, P=0.500 +/- 0.481 (boot). 0 failures.

**Echo 20us / 2000us** (first/middle/last third of 1500 shots, population =
74 readable qubits, pooled by median): **arrow A(k)=0.0 exactly, every k,
every window, every qubit, both gaps** -- an exact algebraic identity, not a
null result: for any 0/1-valued series, x^2=x, so a^2*b - a*b^2 = a*b - a*b = 0
identically, for the real series AND every shuffle. z=0/0, reported as 0.
Clock (middle-window, autocorrelation): 20us tau=249.27 +/- 24.02 shots;
2000us tau=186.00 +/- 21.04 shots (median across qubits, boot-over-qubits
error). Split: no peaks exist in a monotone/flat 0/1 decay series --
FAILED for every qubit/window, both gaps (148 rows in the failure table).
Reversed-trace clock check (middle window): forward and reversed tau
numerically identical to 1e-13 at both gaps -- autocorrelation is symmetric
under time-reversal by construction, same as horn's during-window clock.

**Buzz J2** (seats 80/100/116, first/middle/last third of 4000 shots,
detrend width = 8 revolutions = 120 pts using nu_precise.json's |nu|=0.06675
cyc/shot, period=14.98 shots): pooled (median across 3 seats) middle-window
arrow k=34 shots, A=-18.99 +/- 24.38 (boot-over-seats); clock tau=51.69 +/-
6.98 shots; split (per-seat peaks = phase 2*pi crossings) S=-7.65, P=0.500
+/- 1.4e-15 (boot-over-seats, n=3 seats -- thin, flagged). 0 failures.

## THE TABLE

| record | arrow: best k (native units) | arrow A +/- boot err | sign | clock tau +/- boot err (native units) | split S | split P +/- boot err |
|---|---|---|---|---|---|---|
| yeast forward | 115.28 s | -99,144,751 +/- 24,815,877 | - | 784.57 +/- 73.66 s | 2.373 s | 0.5000 +/- 0.1828 |
| yeast backward (10-9-8) | 48.81 s (k*) | +0.392 +/- 0.428 | + | -637.55 +/- 56.45 s | 2.373 s | 0.5000 +/- 0.1226 |
| horn | 23.10 s | +0.01687 +/- 0.00648 | + | 175.68 +/- 11.74 s | 11.59 s | 0.5000 +/- 0.4813 |
| echo 20us | 49 shots (tie, A=0 all k) | 0.0 +/- 0.0 (exact) | 0 (exact) | 249.27 +/- 24.02 shots | -- | FAILED (no peaks) |
| echo 2000us | 49 shots (tie, A=0 all k) | 0.0 +/- 0.0 (exact) | 0 (exact) | 186.00 +/- 21.04 shots | -- | FAILED (no peaks) |
| buzz J2 (control) | 34 shots | -18.99 +/- 24.38 | - | 51.69 +/- 6.98 shots | -7.65 | 0.5000 +/- 1.4e-15 |

### Record-vs-record calls (vs yeast-forward, the record this instrument was built on)

| record | arrow vs yeast-fwd | clock vs yeast-fwd | split P vs yeast-fwd |
|---|---|---|---|
| yeast backward | UNSTABLE (diff 99,144,751.6, err 24,815,877.2) | UNSTABLE (diff 1422.1s, err 130.1s) | AGREE (diff 0, err 0.305) |
| horn | UNSTABLE (diff 99,144,751.2, err 24,815,876.7) | UNSTABLE (diff 608.9, err 85.4; UNITS: s vs s, valid) | AGREE (diff ~0, err 0.664) |
| echo 20 | UNSTABLE (diff 99,144,751.2, err 24,815,876.7; UNITS MISMATCH: A dimensionless-0 vs count^3) | UNSTABLE (diff 535.3, err 97.7; UNITS MISMATCH: shots vs s) | UNSTABLE (missing -- split failed) |
| echo 2000 | UNSTABLE (diff 99,144,751.2, err 24,815,876.7; UNITS MISMATCH) | UNSTABLE (diff 598.6, err 94.7; UNITS MISMATCH) | UNSTABLE (missing -- split failed) |
| buzz J2 | STABLE DISAGREEMENT (diff 99,144,732.2, err 24,815,901.1; same sign pattern net-negative across before/during; UNITS MISMATCH: shots vs s) | UNSTABLE (diff 732.9, err 80.6; UNITS MISMATCH) | AGREE (diff ~0, err 0.183) |

### Record-vs-record calls (vs buzz, the positive control)

| record | arrow vs buzz | clock vs buzz | split P vs buzz |
|---|---|---|---|
| yeast forward | UNSTABLE (units mismatch, see above) | UNSTABLE (diff 732.9, err 80.6, units mismatch) | AGREE (diff ~0, err 0.183) |
| yeast backward | AGREE (diff 19.4, err 24.8 -- units mismatch, coincidental) | UNSTABLE (diff 689.2, err 63.4, units mismatch) | AGREE (diff ~0, err 0.123) |
| horn | AGREE (diff 19.0, err 24.4 -- units mismatch, coincidental) | UNSTABLE (diff 124.0, err 18.7, units mismatch) | AGREE (diff ~0, err 0.481) |
| echo 20 | AGREE (diff 19.0, err 24.4 -- units mismatch, coincidental) | UNSTABLE (diff 197.6, err 31.0 -- SAME units, shots vs shots, valid) | UNSTABLE (missing) |
| echo 2000 | AGREE (diff 19.0, err 24.4 -- units mismatch, coincidental) | UNSTABLE (diff 134.3, err 28.0 -- SAME units, shots vs shots, valid) | UNSTABLE (missing) |

**Read on "AGREE" cells above between records of different units:** every
`arrow vs buzz` AGREE is a units-mismatched coincidence (buzz's A is O(10),
yeast/horn's raw-count A is O(10^7-10^8), echo's is exactly 0 -- none of these
compare against buzz's O(10) on shared footing; the call machinery returned
AGREE only because the combined bootstrap error, ~24, happens to exceed the
~19-diff between buzz's number and 0, not because 0 and -19 "agree" in any
physical sense). Same-unit pairs, the only physically meaningful ones: echo-20
vs echo-2000 clock (both shots) = diff 63.3 shots, combined err 45.1 shots ->
**UNSTABLE**; horn vs yeast-forward clock (both seconds) = diff 608.9s,
combined err 85.4s -> **UNSTABLE**; yeast-forward vs yeast-backward split-P
(both dimensionless slope) = diff ~0, err 0.305 -> **AGREE** (expected: same
formula, same during-window data, reused by the backward chain's own spec --
not an independent check, exactly as flagged in `backwards.py`'s own note).

## Forward-chain vs backward-chain (order 10-9-8), per formula

| record | formula | forward | backward | diff | combined boot err | call |
|---|---|---|---|---|---|---|
| yeast | arrow (during, at k*) | 15,252,874.9 +/- 10,537,590.2 | 0.392 +/- 0.428 | 15,252,874.5 | 10,537,590.6 | UNSTABLE |
| yeast | clock (pointing window = after) | 688.17 +/- 66.86 s | -637.55 +/- 56.45 s | 1325.72 | 123.31 | UNSTABLE |
| horn | arrow (at_horn, at k*=3.47s) | 0.129 +/- 2.264 | -3.573 +/- 0.478 | 3.703 | 2.742 | UNSTABLE |
| horn | clock (at_horn, during-role) | 175.68 +/- 11.74 s | 233.79 +/- 18.58 s | 58.11 | 30.32 | UNSTABLE |
| buzz J2 | clock (pooled, during) | 51.69 +/- 6.98 shots | 25.04 +/- 4.63 shots | 26.65 | 11.61 | UNSTABLE |
| echo 20/2000 | all | -- | -- | -- | -- | **NOT RUN: split has no peaks (see failures), so the chain's own step 1 cannot start** |

Every forward-vs-backward call that could be run came back UNSTABLE (same
pattern already found on yeast alone). Sign patterns were not uniform across
windows in any record, so none qualified for STABLE DISAGREEMENT under the
verdict rule; they are UNSTABLE, not AGREE, full stop.

## Reversed-trace vs forward, per formula

| record | formula/window | forward | reversed | call |
|---|---|---|---|---|
| horn | arrow, home_before | +1.6433 | -1.6433 | AGREE (magnitude, diff 0) |
| horn | arrow, at_horn | +0.01687 | -0.01687 | AGREE (magnitude, diff 0) |
| horn | arrow, home_after | +9.6145 | -9.6145 | AGREE (magnitude, diff 0) |
| horn | clock, home_before | 24,164.9 s | -24,164.9 s | UNSTABLE (diff 48,329.9, err 8192.6 -- rise/decay role flips under reversal by construction) |
| horn | clock, at_horn (during-role) | 175.68 s | 175.68 s | AGREE (diff ~2.6e-13, autocorrelation is reversal-symmetric) |
| horn | clock, home_after | -4695.8 s | +4695.8 s | AGREE (diff 9391.6, err 9706.6 -- large error swallows the sign-flip) |
| echo 20 | clock, middle (pooled median) | 249.27 shots | 249.27 shots | AGREE (diff 8.5e-14, reversal-symmetric) |
| echo 2000 | clock, middle (pooled median) | 186.00 shots | 186.00 shots | AGREE (diff 2.8e-14, reversal-symmetric) |
| buzz | arrow (per-seat) | see backwards.py convention (antisymmetric by design) | -- | not separately re-derived this pass (time budget; logged below as an open item, not hidden) |

The arrow's antisymmetry under reversal (|A| unchanged, sign flipped) that
yeast showed holds exactly on horn too. The "during-role" clock method
(autocorrelation-based) is EXACTLY reversal-symmetric on every record it ran
on (horn at_horn, echo both gaps) -- `correlate(x,x)` does not see time
direction, a property of the method, not of any record's own physics.

## ERRORS AND FAILURES (every one counted, none dropped to "n/a")

| record | formula | window | what failed | raw value / count |
|---|---|---|---|---|
| echo 20 | arrow | first/middle/last, 64 (qubit,window) cells total | series has zero variance in this window (0/1 series is constant) | 64 cells, values all exactly 0 or 1 |
| echo 20 | clock | first/middle/last, 64 (qubit,window) cells total | series has zero variance in this window | same 64 cells as arrow |
| echo 20 | split | every qubit, middle window, 74 cells | 0/1 first-look series has no periodic structure (monotone/flat toward readout floor) -- no peaks exist | 74 cells (n_peaks=0 in every case) |
| echo 2000 | arrow | first/middle/last, 74 (qubit,window) cells total | series has zero variance in this window | 74 cells |
| echo 2000 | clock | first/middle/last, 74 (qubit,window) cells total | series has zero variance in this window | same 74 cells |
| echo 2000 | split | every qubit, middle window, 74 cells | no periodic structure, no peaks | 74 cells |
| echo (both gaps) | arrow | all valid cells (306 qubit-window combos) | NOT a failure, but flagged: A(k)=0 exactly for every k by algebra (x^2=x on 0/1 data) -- z=0/0 reported as 0.0, a real result not a search failure | 306 combos, A=0.0 exactly in all |
| horn | -- | -- | 0 failures | -- |
| buzz J2 | -- | -- | 0 failures | -- |
| buzz J2 | arrow reversed-check | all seats/windows | NOT RUN this pass (scope/time) | logged as an open item, not hidden -- would reuse the same reversed-A machinery already run on horn/yeast |
| echo (both gaps) | backward chain (10-9-8) | step1 (split) | cannot start: no peaks anywhere in the record to define k*/crossing/D | 100% of qubit/window cells for both gaps |
| all new records | THE SPLIT's telescoping identity | -- | S,P recomputed on any record with peaks (horn, buzz, yeast) all land at P=0.4999999... to 1e-13 -- same construction flaw yeast already flagged (D is a cumsum of the crossing it's regressed against, forcing P->0.5-ish structurally on any near-regular peak spacing), not independent confirmation of anything physical | horn P=0.499999999999984; buzz P=0.499999999999999 (3 seats, spread 1.4e-15) |

**Error-bar-size column, by formula, across records (the errors as data):**

| formula | record with LARGEST bootstrap error | value | record with SMALLEST bootstrap error (excluding echo's exact-0 case) | value |
|---|---|---|---|---|
| arrow | yeast forward (raw NADH counts, native units) | 24,815,877 | horn (at_horn, native seconds) | 0.00648 |
| clock tau | yeast forward (autocorrelation, seconds) | 73.66 s | buzz J2 (autocorrelation, shots) | 6.98 shots |
| split P | horn (259 cycles, at_horn) | 0.4813 | buzz J2 (3-seat pooled) | 1.4e-15 |

Read plainly: yeast's arrow error is ~7 orders of magnitude larger than
horn's, entirely a units/scale artifact (raw NADH fluorescence counts cubed vs
a dB-power-derived detrended signal cubed) -- not evidence either record's
underlying process is more or less noisy. Buzz's split error is startlingly
small (1.4e-15) because P=0.5 came out numerically IDENTICAL to machine
precision across all 3 seats (the telescoping identity above, not a real
physical agreement) -- the tiny error bar there is a construction artifact,
not a strong result, and is reported as such: a real, exact number that means
less than its smallness suggests.

## Tries

Real-data bootstrap and shuffle-floor draws actually run this pass (yeast's
own 687,000 draws from `THREE_ON_YEAST_20260930.md` are not re-run and not
recounted here):

- Horn: 570,000 draws (arrow k-search shuffle floors 549,000 across 3 windows
  x ~183 k's each; arrow bootstrap+reversed-floor 6,000; clock forward+reversed
  bootstrap 6,000; split 2,000; backward chain step2 (3 k-variants x 3
  windows x msg+raw boot) 18,000; step3 clock bootstrap 1,000).
- Echo: 15,814,000 draws (306 valid qubit-window combos at gap=20/2000
  combined x 49-k arrow search x 1000 = 14,994,000; +306,000 arrow bootstrap;
  +306,000 clock bootstrap; +208,000 reversed-check combos on the middle
  window across both gaps).
- Buzz: 459,000 draws (9 seat-window arrow k-searches x ~44 k's x 1000 =
  396,000; +9,000 bootstrap; +9,000 reversed floor; +18,000 clock
  forward+reversed bootstrap; +6,000 split boot+shuffle across 3 seats;
  +54,000 backward-chain step2; +3,000 step3).

**Grand total this pass: 16,843,000 resample/shuffle draws**, underneath
approximately 549 (horn) + 15,042 (echo, 158+148 qubit-window combos x 49 k's)
+ 396 (buzz, 9 combos x 44 k's) = **15,987 point estimates** for the arrow
alone, plus ~700 clock fits and ~10 split fits across all three records
combined. Every one of the 424 echo failures (arrow zero-variance, clock
zero-variance, split-no-peaks) and the 2 open items (buzz reversed-arrow not
run; echo backward chain not startable) above is counted in this total's
accounting, not folded into a silent pass/fail rate.
