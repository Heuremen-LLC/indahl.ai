
## 2026-11-01 20:16 Darkwave Correction Kit v1.1 known-good run on ibm_kingston: R1 CONSISTENT, R2a CONSISTENT, R2b ABOVE, kit passes
packs: Q,P
(answer each line: holds:/fixed:/caught:/n/a:/cannot tell: followed by what was checked)
- I: holds: kit and study code same job, same 117 targets, idle 545 dt, D/M scheduled equal; R2b gate kept 113 of 117 and the referee found the outcome unchanged with no gate or other gates
- II: holds: per-target spread printed; correlation 0.645 traced to 3-4 low-coherence targets (0.999 without them) and stated in README, post hoc
- III: holds: residual +0.086 near zero, share 1.012 just above 1; sign flipped correction reads -0.99 in the referee test
- V: holds: kit table read two ways and equal; R2a and R2b both required; referee recomputed all numbers with own code
- VI: holds: four outcomes from bands; R2a band [-0.007,+0.180] inside +-0.5, R2b band above 0.5
- R: holds: job ids, 20 s and 9 s, plan commit b2464e4 at 01:15:01Z before job 1 at 01:15:50Z, from git and job record
- QA: n/a: no vendor figure is compared; the comparison is our kit against the study code in one job
- QB: holds: idle arm equal length on every target, checked on scheduled circuits before submit
- QC: holds: known-good = study calibration code same job, R1 CONSISTENT; synth counts the corrections from the real apply and reproduces fire 1 failure (0.252)
- QD: holds: one chip as planned, four outcomes, scope stated as one chip and one calibration snapshot
- QE: holds: no physical mechanism named; correction counts stated as pre-transpile with the X-basis merge noted
- QF: holds: plan public before the fire; one fire as planned
- QG: holds: outside referee reproduced every number from the raw arrays; four flags acted on in README (correlation, tail, counts, scope)
- P1: n/a: no quoted text appears in any file of this folder
- P2: holds: every figure names results_kitcheck_ibm_kingston.text and the raw files here
- P3: holds: kit version 1.1 and plan PLAN_KITCHECK2 named
- P4: holds: no cause named for the turn; the low-coherence explanation of the correlation drop is labelled post hoc
- P5: holds: 95 % bootstrap over targets, 2,000 resamples, seed 41
- P6: holds: pass scoped to one chip, one snapshot, second attempt; tail named
- P7: n/a: ledger rows are added before the kit page carries these numbers, in the same release
- P8: n/a: no rendered page yet for these readings
- P9: holds: plain sentences, no AI statements, no counts of our things in headings
- P10: holds: referee-derived readings labelled defined after the data
