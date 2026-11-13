
## 2026-11-01 20:13 Darkwave Correction Kit v1.0 known-good run on ibm_kingston: R1 CONSISTENT, R2 failed (0.264 given back), cause found
packs: Q,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: kit and study code ran in the same job on the same 117 targets and E pack, idle 545 dt both, kit D/M scheduled equal; R2b gate (|turn|>0.25) kept 114 of 117, count printed
- II: holds: per-target spread printed beside the median (share differing >1 deg 0.085, corr 0.958); no net over items replaces the per-target values in results json
- III: holds: residual and share are signed; residual -2.386 has the sign of the uncorrected turn -3.362, so under-correction, not overshoot
- V: holds: kit table read two ways (packed arrays and the kit get_counts path), agree exactly; R1 median of differences with bootstrap band; R2 two readings (residual, share)
- VI: holds: four outcomes from bands; R2a band [-3.282,-1.833] excludes both 0 and the margin, BELOW; R2b [0.248,0.285] below 0.5
- R: holds: job ids, usage 20 s and 9 s, times from job_kitcheck json and IBM metrics; the cause is labelled found after the result
- QA: n/a: no vendor figure is compared; the comparison is our kit against the study code in one job
- QB: holds: idle arm equal length to readout arm on every target, checked on the scheduled circuits before submit; same job
- QC: holds: known-good = study calibration code, same job, R1 CONSISTENT; synth planted five worlds; caught: synth placed the turn between readouts and hid the grouping fault, run 2 synth counts corrections on the real circuit
- QD: holds: four outcomes, one chip as planned, targets not pooled with shots
- QE: holds: no physical mechanism named; the fault named is in our code, shown by counting rz on the real circuit (2 of 8) and reproduced in synth (0.252)
- QF: holds: plan public in heuremen.org before job 1 (01:10 UTC listing), job 1 submitted 01:11:20Z, job 2 01:11:48Z
- QG: cannot tell: no outside referee has read these results yet; a referee pass runs before the kit page states them
- P1: n/a: no quoted text appears in any file of this folder
- P2: holds: every figure in README.md names results_kitcheck_ibm_kingston.text and the raw files in this folder
- P3: holds: kit version 1.0 named; plan file named
- P4: holds: the software cause is shown by direct count on the circuit, not inferred; no physical cause named
- P5: holds: bands stated as 95 % bootstrap over targets, 2,000 resamples, seed 41
- P6: holds: README says the kit failed its hardware check and gives the numbers
- P7: n/a: no number is on indahl.ai yet; ledger rows come before the kit page carries the result
- P8: n/a: no rendered page yet for these readings
- P9: holds: plain sentences, no AI statements, no counts of our things in headings
- P10: holds: the cause is labelled as found after the result
