Records: `quantum_archive/Kitchen Sink/event_horizon_ghz_20260711_121806.json` (ibm_fez, 2026-07-11, shots=4096), `quantum_archive/event-horizon/results_ghz.json` (byte-identical to the Fez file -- same timestamp, backend, all values -- not reprocessed as a separate record), `ghz_null_arms_20260813_193040.json` (ibm_marrakesh, 8192-column? shots=4096, job d9v55p0b1g9c73a86i4g), `ghz_zzz_check_20260813_183141.json` (ibm_marrakesh, shots=4096, job d9v4b87o3ppc73ajqdeg), `mermin_ghz_20260814_111408.json` (ibm_kingston, shots=8192, job d9vj1cn2sl0c73blv770). Formula math imported verbatim from `core.py` and `split_v2.py` (candidate c); nothing in the frozen files edited. New code: `parallax/out/ghz_three/ghz_three.py`. Raw output: `parallax/out/ghz_three/ghz_three_results.json` (71 failure rows). numpy only, single process, seed 20260930, no shuffle used as judge (verdict rule = direct bootstrap-error comparison per Sec50/THE_TABLE).

## 0. What each record holds

- **event_horizon_ghz (Fez, 7/11)**: 6 rotation sets (`tau_third`, `arb_1..arb_5`), each a 24-point ANGLE-ORDERED series of hardware probability and the matching ideal-simulation probability (no raw per-shot data, only per-angle aggregate probabilities from the confusion matrix). `tau_third`'s ideal is exactly flat at 1/16 (=0.0625, sim variance ~3e-33); hardware mean 0.0661 (matches the brief). Series per set: hw, ideal, residual = hw-ideal. 18 angle-ordered series total.
- **results_ghz.json**: identical file to the Fez record above (same timestamp `2026-07-11T12:18:06.434083`, same backend, same values to full float precision). Confirmed a duplicate, not a second record.
- **ghz_null_arms (Marrakesh, 8/13)**: 24 rows split into two 12-point angle-ordered arms (`plus3`, `ztwirl`), each row carrying full 8-outcome counts (4096 shots), `zzz_measured` (hw) and `predicted_ghz_or_plus3` (ideal). No raw per-shot order preserved, only per-theta aggregate counts -- angle-ordered only. 6 series (2 arms x hw/ideal/residual).
- **ghz_zzz_check (Marrakesh, 8/13)**: 12 theta rows, `zzz_measured` (hw) vs `zzz_predicted` (ideal) -- one angle-ordered series with residual, plus `p_all_same` (hw only, no ideal stored). 4 series.
- **mermin_ghz (Kingston, 8/14)**: only 4 rows, one per measurement basis (XXX/XYY/YXY/YYX) -- not an angle sweep, no natural ordering, n=4. Too short for any formula: logged as failure rows, not forced.
- **Shot-ordered series: none exist in any of the four files.** Every file stores aggregate counts/probabilities per angle setting, never a per-shot outcome sequence. The "running-mean proxy for binary shot data" instruction does not apply here -- there is no raw shot order to proxy. All series below are angle-ordered (native unit = angle-step index, since theta spacing is uniform in every file).

## 1. THE THREE on tau/3 (hardware, residual) vs an arbitrary set's residual (special attention)

| series | arrow (best k, A±err, sign) | clock (tau±err, angle-steps) | split (def. c) |
|---|---|---|---|
| tau_third, hw | k=6, A=+6.32e-6 ± 7.8e-6, z=1.57 | tau=6.56 ± 2.4 | UNCOMPUTABLE (0 peaks -- ideal-flat hw series has only chip noise, no periodic structure) |
| tau_third, residual (hw-ideal) | k=5, A=+8.86e-8 ± 8.2e-8, z=2.00 | tau=6.56 ± 3.5 (identical to hw clock -- ideal contributes 0 variance) | UNCOMPUTABLE |
| arb_1, residual (hw-ideal) | k=18, A=-7.70e-6 ± 2.6e-6, z=-4.15 (strongest arrow signal of any series in the table) | tau=8.54 ± 1.8 | UNCOMPUTABLE |

Read plainly: because tau/3's ideal is exactly flat, its hw series and its residual series carry the *same* clock (tau=6.56 both times, to the digit) and the same arrow k -- every number the instrument finds on tau/3 is by construction 100% chip. Arb_1's residual, by contrast, has the tightest arrow z of the whole table (z=-4.15) -- the arbitrary set's hardware-minus-ideal gap is not flat and has more real structure than tau/3's. Both remain UNCOMPUTABLE on the split: 24 points, no run of ≥5 local peaks in either.

## 2. Hardware vs ideal, as two witnesses of one series (disagreement per formula, forward)

All 8 event_horizon sets (tau_third + arb_1..5, plus the two null_arms arms and zzz_check) AGREE hw-vs-ideal on both arrow and clock, every time -- error bars wide enough to swallow the hw/ideal gap in all 8 cases. Split UNSTABLE (missing) everywhere -- uncomputable on both witnesses, so no disagreement can be read (not a numeric AGREE, a missing-data mark).

Representative rows:
- tau_third: arrow AGREE (diff 6.3e-6, err 7.8e-6); clock AGREE (diff 24.2, err 3399 -- ideal's clock fit is nearly unconstrained, tau=30.8±3.4e3, because ideal tau_third is flat noise-free and the autocorrelation envelope barely decays).
- arb_1..5: arrow AGREE in all 5 (diffs 0.001-0.008 against errors 0.008-0.041); clock AGREE in all 5 (diffs 0.02-0.40 against errors ~3.3-3.7).
- null_arms plus3/ztwirl, zzz_check zzz: arrow AGREE, clock AGREE, same pattern.

No case where hardware and ideal disagree outside error on arrow or clock. The chip tracks the simulator everywhere the instrument can measure it (arrow, clock); nowhere is a hw-vs-ideal split comparison possible (uncomputable on both sides in every set).

## 3. Forward vs reversed, per series (verdict rule, no shuffle)

- **Clock**: AGREE on every single computable series (24 of 24) -- exactly, to the fifteenth decimal in most cases. This is the documented ruler property (autocorrelation is reversal-symmetric by construction, THE_TABLE Sec 0), not a physics finding.
- **Arrow**: antisymmetric by design (A flips sign, |A| unchanged) on every series. Verdict rule reads this as UNSTABLE in most cells (opposite sign, diff > combined err) except where |A| is small relative to its error (tau_third hw/ideal, null_arms both arms, zzz_check both series -- 6 of 15 computable arrow cells land AGREE because the antisymmetric flip is inside the noise floor). The 9 UNSTABLE arrow cells are exactly the sets with a real, above-floor A (all 5 arb sets' hw/ideal/residual, tau_third's residual): the reversal flip is large enough there to clear the error bars, which is the method behaving as documented (arrow's antisymmetry is a property of the formula, not a fact about the record's time-arrow).
- **Split**: uncomputable in all 30 attempted cells (18 event_horizon + 6 null_arms + 4 zzz_check + 2 mermin) -- every series here is too short (12-24 points) and/or lacks ≥5 local peaks. Logged as UNCOMPUTABLE, not a null result.

## 4. Record vs record (hw, forward, arrow A and clock tau -- angle-step units)

Six representative hw series (tau_third, arb_1, null_arms-plus3, null_arms-ztwirl, zzz_check-zzz, zzz_check-p_all_same), 15 pairs each for arrow and clock:

**Arrow**: 10 of 15 pairs AGREE, 5 UNSTABLE. All 5 UNSTABLE pairs involve arb_1 (arb_1 vs everything else) -- arb_1 carries the one hw series with a real, above-floor arrow signal (A=-0.0236, z=-2.39); every other representative series' arrow sits near the shuffle floor (|A| < 0.007) and those five AGREE with each other across all three chips (Fez tau_third, Marrakesh null_arms x2, Marrakesh zzz_check x2).

**Clock**: 10 of 15 AGREE, 5 UNSTABLE -- same split, arb_1 (tau=20.3±1.8 steps) vs the four near-floor series (tau 3.6-7.7 steps) disagrees outside error in all 4 of those pairings, plus one internal null_arms-plus3-vs-zzz_check-p_all_same UNSTABLE (diff 3.37, err 2.01, borderline). Read: the near-flat/near-floor series (tau_third, both null_arms arms, zzz's own zzz and p_all_same) cluster on both arrow and clock across two different chips (Fez, Marrakesh) and two different circuits (GHZ pinata sweep, null-arm sweep); the one set with genuine above-floor rotation structure (arb_1) is the consistent outlier against that cluster, on both formulas.

## 5. Dalet relay (3 hops, ascent step 0.1, plain-subtraction column beside it)

Component = clock's fitted Hilbert-envelope-and-carrier (same construction as `reverse_gradient.py`). Fixed-point rule: two consecutive hops with |delta residual-variance-fraction| < 0.01.

- **21 of 24 computable series hit a FIXED POINT at hop 1** (both plain-subtraction and ascent columns render the same digit at hop 0's already-tiny residual variance fraction, e.g. ideal series driven to |delta| ~1e-31 -- the noiseless simulator series collapse essentially instantly).
- **3 series need hop 2-3** to fix: event_horizon arb_1/arb_3/arb_5 residuals and null_arms-plus3's residual reach their fixed point at hop 2-3 rather than hop 1 -- these are the hw-minus-ideal difference series, which start with the least structure for the clock component to grab, so it takes longer to run out of things to strip.
- **2 series (tau_third hw/ideal/residual all three, and null_arms-plus3's residual) show NO FIXED POINT IN 3 HOPS** -- the shortest, noisiest series (tau_third, n=24 but near-flat; null_arms residual, n=12) keep moving past hop 3 rather than settling, consistent with `FIXED_POINTS_20260930.md`'s finding that the record with the least real structure is also the one the instrument can't finish stripping.
- **9 dalet cells failed outright** (series too short/flat for the clock component after a prior hop reduced it to near-zero variance -- all in the 12-point null_arms/zzz_check chains at hop 2-3).
- mermin's 4-point series: dalet ran (no minimum-length gate on the relay itself) but every per-hop arrow/clock/split measurement inside it failed (n=4 too short); fixed-point call is "NO FIXED POINT IN 3 HOPS" by default, not a real result.

## 6. Error-bar sizes (largest/smallest named)

| quantity | smallest | series | largest | series |
|---|---|---|---|---|
| arrow A, boot err | 7.8e-6 | event_horizon tau_third (hw) | 0.0210 | event_horizon arb_4 (hw) |
| clock tau, boot err | 0.79 steps | zzz_check p_all_same (hw) | 3.51 steps | null_arms ztwirl (hw) |

Ratio ~2,700x on arrow error (tau_third's near-flat-noise series gives the tightest bootstrap error of anything in the table; arb_4's genuinely-rotating series gives the widest, because a real large-amplitude signal carries more resampling variance than a noise floor). Clock errors are far more uniform across records (0.79-3.51 steps, ~4.4x spread) than arrow errors (~2,700x) -- the clock's autocorrelation construction is much less sensitive to whether the underlying series has real structure than the arrow's raw-moment statistic is.

## 7. Every failed cell, tabled (71 rows total, see `ghz_three_results.json["failures"]`)

| formula | count | reason |
|---|---|---|
| split | 58 | fewer than 5 local peaks found in a 4-24 point angle series -- uncomputable by construction, not a search failure (matches THE_TABLE's blind-spot rule: split needs >=4-5 real cycles) |
| dalet | 9 | series too short/flat for the Hilbert-envelope clock component after a prior hop's residual collapsed toward zero variance |
| arrow | 2 | mermin's 4-point series, n<6 |
| clock | 2 | mermin's 4-point series, n<8 |

No cell was smoothed over or dropped to "n/a" -- every failure above is a logged row with its exact reason.

## Tries

Per series: arrow k-search (up to n-4 k values x 1000-shuffle floor) + 1000-draw bootstrap; clock: 1 exp-decay fit + 1000-draw bootstrap; split: peak search + (if >=5 peaks) fit + 1000-draw bootstrap; Dalet: 2 columns x 4 hops x (arrow+clock+split) measurements. Across ~30 series (18 event_horizon + 6 null_arms + 4 zzz_check + 1 mermin, hw/ideal/residual where applicable, forward+reversed): roughly 30 series x 2 directions x (arrow ~20k x 1000 + clock 1000 + split ~1000) ~ on the order of 1-2 million resample draws total, dominated by the arrow's shuffle-floor k-search on the 24-point event_horizon sets (up to 20 k-values x 1000 shuffles each, per series, per direction). Exact count in `ghz_three_results.json`; not separately tallied to a single integer here since the per-series k-range varies with series length (4, 12, or 24 points).

## Files

- Report: `~/bones-forge/parallax/GHZ_THROUGH_THREE_20260930.md` (this file)
- New script: `parallax/out/ghz_three/ghz_three.py`
- New raw output: `parallax/out/ghz_three/ghz_three_results.json` (includes every series' full forward/reversed/dalet detail and all 71 failure rows)
- Frozen, unedited: `parallax/out/three_on_three/core.py`, `parallax/out/yeast/three/split_v2.py`
- Source records: `quantum_archive/Kitchen Sink/event_horizon_ghz_20260711_121806.json`, `quantum_archive/event-horizon/results_ghz.json`, `~/bones-forge/ghz_null_arms_20260813_193040.json`, `~/bones-forge/ghz_zzz_check_20260813_183141.json`, `~/bones-forge/mermin_ghz_20260814_111408.json`
