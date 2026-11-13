# Darkwave Correction Kit version 1.1: known-good run on ibm_kingston, second fire, 2 November 2026

Plan: PLAN_KITCHECK2.md.text, committed and public before any job. Results: results_kitcheck_ibm_kingston.text (its first line names the first
plan's file because the analysis code is unchanged from the first fire). Raw arrays, circuits, calibration records and the job record are here.
The run code is the first fire's, in code/ with local paths replaced (see ../2026-11-02-darkwave-kit-check/REDACTIONS.md).

What it read (kit version 1.1, rule: R1 CONSISTENT, R2a CONSISTENT and R2b ABOVE):
- R1, the kit against the study's own code in the same job: kit median -3.224 deg per readout, study code -3.251. Kit minus study -0.041
  [-0.231, +0.101], CONSISTENT within 0.5. Share of the 117 targets differing by more than 1 deg 0.085. Correlation over targets 0.645
  (0.958 in the first fire).
- R2a, turn left after the kit's correction: +0.086 [-0.007, +0.180] deg per readout, CONSISTENT with zero within 0.5. The uncorrected turn in
  the same job was -3.223.
- R2b, share of the turn given back: 1.012 [0.993, 1.027] over 113 targets, ABOVE 0.5.
The kit passes its hardware check on this chip, in one calibration snapshot (both fires read the same calibration record), on the second
attempt after a fix. The first fire, with version 1.0, failed it and is kept in ../2026-11-02-darkwave-kit-check.

Read after the result (defined after the data, from a recount of the raw arrays with separate code):
- The per-target correlation fell from 0.958 to 0.645 because of 3 to 4 targets with low idle coherence (below 0.35 at N = 4, for example q121, q131
  and q146), where the N = 4 phase is noise or lands on a different turn of the circle. Without them the correlation is 0.999 in both fires. The kit
  unwraps its N = 4 value near 4 times its N = 1 value and the study code near 4 times its committed 21 October value, so the two can differ there.
- The share given back is a median over targets. A tail keeps part of the turn: 12 % of targets keep more than 1 deg per readout, mostly low-coherence
  targets, and among high-coherence ones q147 keeps +9.47 of a -22.1 deg turn. The bulk sits at the shot-noise level (median absolute deviation 0.39 deg).
- The correction counts per target in the plans (4 in version 1.1, 1 in version 1.0) are counts before transpiling. In the transpiled X-basis circuits
  in this folder the transpiler merges one correction into a neighbouring rz, so they show one fewer. The total angle added per target is the same.
- The residual (corrected minus idle) is wrapped to one turn and not unwrapped near an expected value. This does not move the medians.
- The drift line in the results needs the study's 31 October table, published at
  https://github.com/Heuremen-LLC/indahl.ai/tree/main/code/readout-correction/run/data (fresh_kicks_ibm_kingston.json).

Bands: 95 % bootstrap over targets, 2,000 resamples, seed 41. QPU time: 20 s and 9 s.
