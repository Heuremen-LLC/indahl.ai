# YO v2: readings defined after the TEST reading, after the outside referee (31 Oct 2026 ~19:30 EDT). Not in the plan.
Recomputed by posthoc_yo_v2.py from data2/test_items.jsonl and eval2_yo_v2.jsonl.
1. Job A stale flags, qubit level: precision 0.927, recall 0.496 (227 found, 18 false, 231 missed). By the gap between the record stamp and the
   older of the qubit's T1/T2 dates: 24-25 h 1 of 70 flagged; 25-30 h 63 of 157; 30-48 h 96 of 162; 48 h or more 67 of 69. YO mostly flags a
   qubit when its dates are two or more calendar days before the stamp, not by the 24 h rule.
2. Zero flags: every zero found, none false (all are prob_meas1_prep0 = 0 in these records).
3. Two code baselines written after the data: zeros only, no stale flags 0.829; zeros plus "two or more calendar days" 0.929. YO 0.957.
4. Job A split: 205 of 400 items have nothing to flag (YO 0.995 on them); on the 195 that do, YO 0.917 against flag-nothing 0.418.
5. Job C: 94 of 100 CANNOT_TELL truths answered CANNOT_TELL; 18 of the 20 errors lie within 5 % of a rule threshold (referee's count).
Reading: YO beats every planned baseline, reads zeros exactly and gives the four-outcome verdict at 0.95, but it misses most qubits stale by
one to two days, and a simple date rule comes within 0.03 of its record-audit score. The plan's baselines were too weak to show that.
