# QIA hourly calibration (plan committed before any job; 30 Oct 2026, his word: "we really need the calibrations updated ... focus on the chain and the calibrations")
Question: on each IBM processor, every hour, does the calibration IBM publishes for each qubit match what the qubit delivers? It replaces the
queue probe; the wait from submission to running is still recorded from the same job, as a by-product.
Design (cal.py): one Sampler job per operational processor, every usable qubit (x and measure in the target), all at once, physical layout,
optimization 0. C0: measure at rest (1,000 shots). C1: X then measure (1,000 shots). T1: X, delay 15 / 40 / 80 / 160 / 320 us, measure (500 shots each).
Record: the record in force when the job RAN, pulled by time from IBM (properties(datetime=start)); the record at submission is kept too (/q 3).
Readings per qubit (callib.py): P(1|0) from C0 and P(0|1) from C1 with exact 99.9% intervals, against IBM's prob_meas1_prep0 and prob_meas0_prep1;
T1 = B + A exp(-d/T1) with B fixed at the measured P(1|0), Pearson-weighted least squares on a log grid, 99.99% profile interval, against IBM's T1.
Outcomes from IBM's side: ABOVE (IBM's figure above our interval), BELOW, CONSISTENT, CANNOT_TELL (T1 interval at the grid edge or best under 5 us).
For readout errors ABOVE means IBM states more error than delivered; for T1 ABOVE means IBM states a longer T1 than delivered.
KNOWN-GOOD per run (seat): median over qubits of measured/stated mean readout error, and of measured/stated T1, each within [0.5, 2.0]; else every
reading of that run is CANNOT_TELL.
SYNTH (synth.py, synth_results.text): with IBM exactly right, chance calls per processor run p10 0.20, p01 0.05, T1 0.00 (40 runs x 156 qubits);
planted readout x3 found 98%, T1 x0.4 found 100%, readout x0.25 found 76%, T1 x2.5 found 100%, both on one qubit 98%, wrong direction 0;
true T1 2 us reads CANNOT_TELL; all readout x4 fails the seat. Rules fixed on synth only (Clopper-Pearson for readout; T1 cut moved from 99.9% to
99.99% because 99.9% gave three times its nominal false rate) before any job.
Known differences from IBM's own procedure (/q 9): we read all qubits at once (IBM's simultaneity is not stated); our delay grid is ours; our C1
includes the X gate error, as IBM's prob_meas0_prep1 does.
Chain: every finished run adds one entry to the off-record chain (qia_offchain), by this rule and not by hand: processor, window, job id, counts per
outcome, every ABOVE/BELOW reading with IBM's figure and date, and the sha256 of the full per-qubit file published at /qia/cal/<job>.json.
Budget: Darkwave Disco (us-east, six processors) floor 100 s; Quaker (eu-de, aachen) floor 50 s; about 4-6 s per processor run, hourly, until the floor.
What it cannot say: why a figure is off; anything about a time it did not run. A run that has not happened is not a clean bill.

## Note 1 (30 Oct, about 02:20 UTC, after the first aachen run was read and before any US run is read)
Two rules change, both because IBM publishes no uncertainty for its figures:
1. Readout: every IBM readout figure on aachen is an exact multiple of 1/4096 (312 of 312), so it is a count from about 4,096 shots, not an exact
   value. IBM's figure now gets its own exact 99.9% interval (n = 4,096 when the value is a multiple of 1/4096). ABOVE / BELOW only when IBM's interval
   and ours do not overlap; CONSISTENT when they do. A reading of 1 in 1,000 against IBM's 0 of 4,096 is no longer a call.
2. T1: IBM publishes no fit uncertainty, as for T2 in the audit (which marks T2 above 2.5 x T1, not 2). The same 25% margin: ABOVE when IBM's T1 is
   above 1.25 x the top of our interval, BELOW when below the bottom / 1.25, CONSISTENT inside our interval, CANNOT_TELL in between.
The aachen run already in the off-record chain is corrected by a new entry under these rules (append only; the first entry stays).
Synth under Note 1 (synth_results.text): IBM exactly right gives no chance calls (p10 0.00, p01 0.00, T1 0.00 per run); planted readout x3 found 88%, T1 x0.4 100%, readout x0.25 52%, T1 x2.5 100%, both 88%, wrong direction 0.

## Note 2 (30 Oct 2026, display only)
ibm_boston's 03:13 UTC job waited more than 8 hours in IBM's queue (497 jobs pending), and one job per processor is kept in flight, so boston's
row showed a 02:14 reading with no reason given. The published file now also lists, per processor, the send time of a job still waiting in IBM's
queue, and the page prints it beside the older reading. No reading, rule or interval changes.

## Note 3 (30 Oct 2026, 13:57 UTC by the file time, written before any run is re-read under it; the re-reads were appended at about 14:00 UTC)
Note 1 gave IBM's readout figure its own exact interval with n = 4,096 whenever the figure is a multiple of 1/4096. Every multiple of 1/1024 is also a
multiple of 1/4096, and on ibm_fez and ibm_marrakesh every readout figure in the record is a multiple of 1/1024 (fez 312 of 312, marrakesh 312 of 312
in the 30 Oct 12:41 UTC job; across saved runs fez 3,432 of 3,432 and marrakesh 2,808 of 3,432), so those figures are counts from about 1,024 shots.
Their intervals were drawn half as wide as they are. Found by an outside read of the live page during the 30 Oct site pass, after fez and marrakesh
readings were published.
Rule from now on: the shot count behind IBM's readout figures is read from the record of each run. n = 1,024 when every readout figure in that
record is a multiple of 1/1024, otherwise 4,096 (callib.ibm_readout_shots). Nothing else changes.
Synth under Note 3 (synth_results.text): a null world whose IBM figures are counts out of 1,024 gives n = 1,024 in 40 of 40 runs and no chance calls.
The old rule (n forced to 4,096) also gives no chance calls in a pure null world, so its extra calls on fez and marrakesh are readings near the edge
where the record and our job differ by more than the narrower interval allowed. They are corrected, not explained.
Every fez and marrakesh run already in the off-record chain is re-read from its saved raw counts and its saved record under Note 3, and a new
entry names the entry it corrects (append only). Each corrected run's file is published as /qia/cal/<job>n3.json beside the original.
