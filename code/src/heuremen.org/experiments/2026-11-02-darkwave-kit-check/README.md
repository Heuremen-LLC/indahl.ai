# Darkwave Correction Kit: known-good run on ibm_kingston, 2 November 2026

Plan: PLAN_KITCHECK.md.text, committed and public before any job. Results: results_kitcheck_ibm_kingston.text. Raw arrays, circuits,
calibration records and the job record are in this folder.

What it read (kit version 1.0):
- R1, the kit against the study's own code in the same job: the two read the same turn. Kit median -3.458 deg per readout, study code -3.501.
  Kit minus study +0.025 [-0.063, +0.143] deg per readout, CONSISTENT within 0.5. Correlation 0.958 over 117 targets.
- R2, the kit's correction on hardware: it gave back 0.264 [0.248, 0.285] of the turn, BELOW the 0.5 the plan required. The residual turn
  was -2.386 [-3.282, -1.833] deg per readout, against -3.362 uncorrected. The kit failed its hardware check.

Why (found after the result, from the kit's code): `apply` treated barriers as part of a readout group, so the four readouts of each
circuit, separated by barriers, were read as one group and got one correction instead of four. One of four is 0.25, and 0.264 was read.
The simulator self-test placed its planted turn between the readouts, which split the groups and hid the fault. Version 1.1 starts a new
group whenever a qubit is read again, and its self-test now checks the kit's own circuit shape. Version 1.1 is retested on hardware under
the same plan and rule in ../2026-11-02-darkwave-kit-check-2.

Bands: 95 % bootstrap over targets, 2,000 resamples, seed 41.

Note added after a recount of the raw arrays with separate code: the correction count "one per target" is before transpiling. In the transpiled X-basis circuits in this folder the transpiler merges it into a neighbouring rz. The CHECKS.md entry's "2 of 8" refers to a small test circuit (2 targets, 4 readouts), not to the job circuits.
