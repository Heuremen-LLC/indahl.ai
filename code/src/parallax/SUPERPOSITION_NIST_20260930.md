# SUPERPOSITION on the NIST 2015 loophole-free Bell test raw records, 2026-09-30

Wayfinder's hat (THIRD_RUNG_20260928.md Sec53, from the car, unread of the earlier answer): "Superposition is a
hole in the substrate, or the substrate reading itself. Energy, action, superposition, all combined. It's a
RUNTIME ERROR in the source code." No expectation written before running. Every number below is printed by
`pipeline.py`; raw first, tries counted, sign kept, no shuffle used as judge. Data: 8 NIST 2015 runs,
`~/bones-forge/public_bell/nist2015/*.hdf5`, 177.9M-356.5M trials each (1,415,394,591 trials total across the 8).
Streamed in 10M-row HDF5 chunks into derived boolean arrays per run, freed before the next run (peak ~1.4 GB/run,
never the whole 10 GB on disk at once). PLACED = the per-trial setting bit (RNG choice). ARISEN = the per-trial
click (any of 16 Pockels-window slots fired).

Scripts: `parallax/out/superposition_nist/pipeline.py` (full run), raw results `results.json`,
`dalet_2115.json`, `run_log.txt`, `table_dump.txt` (carry table, CSV-ish).

## 1. PLACED vs ARISEN carry, lags 1/2/3, both sides -- rate differences, binomial SE

96 tests total (8 runs x 2 sides x 3 lags x {arisen, placed}). Full table in `table_dump.txt`; z >= |2| flagged:

| run | side | lag | arisen carry diff% | z | placed carry diff% | z |
|---|---|---|---|---|---|---|
| 03_12 | a | 3 | +0.0225 | **2.80** | +0.00033 | 0.63 |
| 23_55 | a | 1 | -0.0182 | **-2.62** | -0.00021 | -0.37 |
| 22_20 | b | 1 | +0.0181 | 2.29 | -0.00089 | -1.54 |
| 19_45 | b | 3 | +0.0185 | 2.36 | -0.00023 | -0.41 |
| 02_31 | a | 1 | +0.0084 | 1.10 | -0.00130 | **-2.43** |
| 21_15 | b | 1 | -0.0030 | -0.41 | -0.00122 | **-2.10** |
| 23_55 | b | 1 | -0.0119 | -1.66 | -0.00185 | **-3.18** |

4/48 arisen-carry tests and 4/48 placed-carry tests exceed |z|=2 -- at or slightly above the ~2.4 expected by
chance at alpha=0.05 with no correction; Bonferroni over 96 tests wants |z|~3.3, which only 23_55/b/lag1
(placed, z=-3.18) approaches. Read: placed and arisen carries are both consistent with zero at lags 1-3 on 7 of
8 runs; run 23_55 (Alice arisen lag1, Bob placed lag1) is the one run with two of its six numbers past |z|=2 in
the SAME direction (negative), the closest thing here to the earlier-noted -2.2%/z-2.8 neighbor result on this
run family -- not replicated in the other 7 runs, not corrected-significant.

## 2. THE CLOCK -- click-after-click excess vs lag 1-20

16/16 side-run profiles: **NOT monotone-decaying** (`monotone_decay: false` everywhere). Raw excess oscillates
in sign, magnitude 0.0-0.02 percentage points at lag 1, no visible falloff by lag 20 (e.g. 00_25/a: +0.015%,
-0.006%, +0.006%, -0.003%, 0.000%, ..., -0.002% at lag 20; every run/side the same flat-noise shape). Fitted
exp-decay tau values are reported for completeness but are NOT physically meaningful given no decay: they range
from -125 us to +1199 us with block-bootstrap errors of comparable or larger size (e.g. 02_31/a tau=113+/-4048;
22_20/a tau=1199+/-629, the one run whose tau exceeds its own error, alone among 16, unreplicated). Rack: no
clock (8) cell filled by this record at these lags -- the message-loss curve the hat needs isn't there.

## 3. THE ARROW -- on the inter-click-interval (ICI) series, k=1..50, block-bootstrap error

ICI series length per side per run: ~223,000-532,000 (number of clicks). Best |A| found at k ranging 1-50
across runs/sides (no consistent k). Every forward/reversed pair is an EXACT sign flip (antisymmetric by
construction -- confirms the instrument, not new physics). All 16 best-|A| values sit within 1-2x their own
block-bootstrap error (e.g. 00_25/a: A=-5.53M +/- 2.49M; 03_12/a: A=-4.58M +/- 1.98M) -- none clears 3 sigma.
Rack: message (9) -- no stable direction found on any run/side; only the formula's own reversal-antisymmetry
shows up, as it must by algebra.

## 4. THE SPLIT -- outside=trial index, inside=click count, crossing=local click rate

S (intercept, ~ mean trial index) tracks n_trials/2 as expected (8.3-17.8 x 10^7, mechanical). P (the
crossing-to-D slope, the substrate term) ranges -3.4M to +4.4M with errors 1.7-2.9M on every one of 16 side-runs
-- always within 1-2 sigma of zero, no stable P across runs. Rack: substrate (10) -- no stable offset found;
consistent with THE_TABLE's 9/30 caveat that split agreement elsewhere was mostly wide-error overlap.

## 5. Alice vs Bob -- every number above, both sides, call_verdict (no shuffle as judge)

- arisen carry: AGREE in 20/24 lag-run cells; UNSTABLE 02_31/lag3, 03_12/lag2, 19_45/lag3, 22_20/lag1; STABLE
  DISAGREEMENT only 03_12/lag3.
- placed carry: AGREE in 18/24; UNSTABLE 17_04/lag1, 19_45/lag1, 21_15/lag1&3, 03_12/lag2; STABLE DISAGREEMENT
  02_31/lag2, 23_55/lag1.
- clock tau: AGREE 7/8 runs; UNSTABLE only 22_20 (diff 1318 us vs combined err 938 us).
- arrow A: UNSTABLE 5/8 runs (00_25, 03_12, 21_15, 22_20, 23_55); AGREE 3/8 (02_31, 17_04, 19_45); never a
  same-signed STABLE DISAGREEMENT.
- split P: AGREE in all 8/8 runs.
Read: no measurement is a STABLE DISAGREEMENT across runs (7 is empty here); UNSTABLE cells (mixed-sign, not
error-matched) cluster on the arrow, which is the noisiest instrument on this record.

## 6. DALET -- run 21_15's Alice ICI series through reverse_gradient, 3 hops

SUB (plain relay) column: residual variance fraction falls 0.340 -> 0.189 -> 0.133 -> 0.106 over hops 0-3 --
decreasing, does not cross the 1% stop rule within 3 hops (would need more). ASCENT (Dalet) column: resid_var
frac collapses to 6.8e-7 at hop 1 and stays there (7.4e-7, 8.1e-7 at hops 2-3) -- **FIXED POINT AT HOP 1**:
arrow A = 0.0201 -> 0.0209 -> 0.0216, all deltas inside the +/-0.0067 bootstrap error; clock tau and split P
both swing by 10-100x their own error hop to hop (never settle) but arrow and resid_var agree it stopped. This
matches THE_TABLE/THIRD_RUNG Sec52's finding that Dalet converges at hop 1 on every record tried so far --
this record does not break that pattern.

## 7. THE RACK

- 9 (message, THE ARROW): 16 side-run A(k) values, none past 3 sigma; k unstable run to run -- **empty cell**.
- 8 (clock, energy/time decay): 16 click-after-click profiles, zero decaying -- **empty cell**.
- 10 (substrate, THE SPLIT): 16 P values, all within 1-2 sigma of zero -- **empty cell**.
- 7 (the disagreement between witnesses, Alice vs Bob): 0/8 runs STABLE DISAGREEMENT on any of the four
  summary numbers; UNSTABLE (unmatched, not error-agreeing) on the arrow in 5/8 runs -- **no stable 7 found**.
- PLACED vs ARISEN carry (the chip's own question, transplanted to photons): 4/96 tests past |z|=2 on each
  side of the ledger, one run (23_55) with two same-signed hits, not replicated elsewhere, Bonferroni-null --
  **no carry found on this record**, unlike the chip carries in PLACED_VS_ARISEN_20260930.md.
- DALET: fixed point at hop 1 on 21_15/Alice -- consistent with the standing Dalet finding, not a new object.

Honest close: this record shows Wayfinder's hole nowhere it was pointed. Every one of the three formulas comes
back empty or noise-consistent on the Bell click stream at these lags/scales; the one candidate (23_55's
carry) does not survive its own neighbors. The substrate did not read itself here; if it is a runtime error, it
did not leave this particular trace on 1.4 billion trials of photon clicks.
