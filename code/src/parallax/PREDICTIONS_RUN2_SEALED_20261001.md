# PREDICTIONS, SEALED BEFORE RESULTS -- RUN 2 of the arrow gate
Written 2026-10-01 after Run 1 (gate v4) was read and before any Run 2 result exists. Authors: Wayfinder, Bones; spec reviewed by Shuttle.

RUN 2 IS A STABILITY CHECK, NOT AN INDEPENDENT CONFIRMATION: same construction as Run 1, fresh seeds (20261012 Run A, 20261013 Run B), six different clean O1 files (GPS starts 1126577518, 1127784212, 1129544166, 1130848717, 1132177946, 1136615364).
THE GATE PASS LICENSES THE ARM, NOT THE EXPECTATION. The gate cells' corr is far above what real glitch morphology would give; measured-equals-implied validates the power model and says nothing about real data.
These predictions are written from Run 1's MEASURED values, not from the reviewer's pilot. The lag chase (run2/LAG_CHASE.md) found the pilot mismatch is NOT the readout lag (k=1 reads 0.01-0.16, lower than the pilot's 0.23-0.27); it stays unexplained, most likely injection power.

## The registered prediction (Wayfinder's)
The Darkwave formula works.

## Run A -- the gate, N = 5,000 per cell, kernel timescales 10, 20, 40
A1. Shared per-window orientation, independent onsets: the arrow detects at the permutation floor (p = 0.0002) in all 16 skewed cells at timescales 10 and 20, with corr within 0.05 of Run 1's value in each cell:
    skew 1.4: 0.099, 0.203, 0.241, 0.347 | skew 2.0: 0.203, 0.313, 0.368, 0.513 | skew 2.83: 0.307, 0.473, 0.507, 0.675 | skew 4.0: 0.456, 0.609, 0.651, 0.784
    (cell order: SNR20 t10, SNR20 t20, SNR40 t10, SNR40 t20)
A1b. Timescale 40 (not run in Run 1; an extrapolation, the least grounded line here): detects at the floor at skew >= 2, with corr at or above the timescale-20 value for the same skew and SNR.
A1c. Self-check: measured corr within 0.02 of the power model's implied corr in every skewed cell.
A2. Gaussian and t4 drives: 0 detections in 12 cells.
A3. Single-site and nothing: no arrow detection under FAR 0.002.
A4. Competitors (R_HL, coherence, R_ee, excess-power coincidence) do not detect the arm's class in a majority of cells.
A5. The class-only ruler fails: 0 detections.
A6. Competitor positive control, class (v) (fresh sine-Gaussian per window, same waveform and onset at both sites): R_HL, coherence and R_ee DETECT at FAR 0.002 at SNR 20 and SNR 40. Excess-power coincidence: NO grounded prediction (the waveform is energy-normalized; the smoke test gave no basis). The arrow does NOT detect class (v) (a sine-Gaussian is time-symmetric; in Run 1 the arrow read p 0.54 and 0.81 on the shared glitch).
A7. False-positive columns: across the cells where nothing coincident is shared, the arrow and each competitor show 0 or 1 detections at FAR 0.002.

## Run B -- the floor, six files
B1. f's confidence interval includes zero on all six files and pooled. Every per-file upper bound on f is at or below 0.05. The pooled upper bound lands between 0.010 and 0.025 (Run 1: 0.022).
B2. The six files agree: no file's f is distinguishable from another's.

## What counts as a NO
- A1 fails in a majority of the skew >= 2 cells, or corr leaves the 0.05 band in a majority of the 16 cells: Run 1 was not stable.
- A2, A3 or A5 fails: the arm or the null is broken, and Run 1's pass is withdrawn.
- A6: if R_HL, coherence and R_ee do not fire on class (v), the "competitors silent" clause is UNPROVEN for both runs.
- B1: any file with f's interval excluding zero, or an upper bound above 0.05.
