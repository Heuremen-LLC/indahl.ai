# T1 and T2 measured together: a check of IBM's published pairs. Plan, written before any run.

## Question
For a given qubit, IBM publishes T1 and T2 in one calibration record, sometimes measured on different dates. Physics bounds T2 at 2 x T1.
When T1 and T2 are measured back to back in one job on the same qubit, is T2 / T1 above 2, and does it match IBM's published values?
Flagged by the audit at indahl.ai/qia: boston q85, kingston q121, fez q148 (published ratios 5.7, 3.29, 2.64 on 28 and 29 Oct 2026).

## Method (fixed now)
One job per processor. For each qubit in the list plus one control qubit:
- T1: prepare |1>, wait d, measure. 16 delays from 0 to 3 x the published T1 (geometric spacing after the first point).
- T2: Hahn echo: H, wait d/2, X, wait d/2, H, measure. 16 delays from 0 to 3 x the published T2, capped at 2 x published T1 x 3.
- 1000 shots per circuit. Circuits run on the physical qubit (initial_layout). Delays in microseconds.
- Fit P1(d) = A exp(-d/T1) + B for T1 and P0(d) = A exp(-d/T2) + B for T2, with 200 binomial bootstrap resamples for 95% intervals on T1, T2 and T2 / T1.
- The published record is read at job time and stored with the results.

## Outcome per qubit (fixed now)
ABOVE: the lower end of the 95% interval of measured T2 / T1 is above 2.
CONSISTENT: the upper end is at or below 2.
CANNOT_TELL: the interval contains 2, or either fit has a failed or unbounded interval.
NOTHING_RETURNED: the job or a circuit returned no data.
Also reported for each qubit: measured T1 and T2 against the published ones, as a ratio with interval. No cause is named.

## Known-good
The control qubit is the qubit whose published T2 / T1 is closest to 1.0 among qubits with published T1 between 100 and 300 microseconds, picked from the same record. If the control reads ABOVE, or both its fits fail, every other qubit in the job is CANNOT_TELL and the job is reported as failing its known-good.
Before any hardware: the fitter runs on planted worlds without a device (script flag --selftest): T1 = T2 = 100 us, T1 = 100 and T2 = 200 us, T1 = 100 and T2 = 50 us, and a world with fit-unfriendly data (all points at B). Each must come out with the right outcome. The circuits are also run noiseless on a local simulator and must give P1 = 1 for the T1 circuits and P0 = 1 for the echo circuits at every delay.

## Cost
The script prints the estimated QPU seconds before submitting (circuits x shots x (mean delay + repetition delay)) and does not submit without --yes. Whoever runs it uses their own IBM account and their own seconds.

## Not claimed
Whether IBM's published numbers were wrong at the time they were published. A later measurement does not date a past one. Only whether a joint measurement now gives a ratio above 2.

## Addendum 1 (29 Oct, first self-test run)
The first self-test expected CONSISTENT for a planted world at T2 = 2 x T1. The rule gives CANNOT_TELL there, because the interval around a ratio of 2 contains 2. The expectation was wrong, the rule is unchanged. A planted world exactly at the bound must read CANNOT_TELL. A planted T2 = 1.5 x T1 must read CONSISTENT.
Added: --flagged reads the current flagged list from indahl.ai/qia/audit.json so a runner does not type qubit numbers. The fitter, thresholds and outcomes are unchanged.

## Addendum 2 (29 Oct, second self-test run)
One planted world (T1 = 100, T2 = 50) came back with T2 = 57.8 against 50 and failed the self-test's fixed 15% tolerance. A direct test of the fitter on the same world gave a mean of 51.8 and a spread of 3.6 at 1000 shots, and 50.04 with a spread of 0.34 at 100000 shots, so the fit is unbiased and the failing draw sat about 2 spreads out. A fixed percentage tolerance does not match the real spread. The self-test now requires the planted T1 and T2 to lie inside the fit's own 95% intervals, plus the outcome. No change to the method, fits, thresholds or outcomes.

## Addendum 3 (29 Oct, third self-test run)
With the interval criterion, the same T1 = 100, T2 = 50 draw still fell just outside its own 95% interval. An interval built around an estimate misses the truth in about 1 draw in 20, so one seed cannot test it. The self-test now runs each planted world over 30 seeds and requires: the right outcome in at least 90% of seeds, and the planted T1 and T2 inside their 95% intervals in at least 85% of seeds (expected about 95%). The world that must read ABOVE and the flat-data world run the same 30 seeds with the same 90% requirement. No change to the method, fits, thresholds or outcomes.

## Note 1 (29 Oct, after the jobs were submitted, before any result was read)
Order inside a job: for each qubit the T1 circuits run, then the T2 circuits. A T1 that fluctuates over minutes could differ between the two halves. The job lasts seconds, but this plan did not interleave them and a rerun should. IBM does not state whether its published T2 is echo or Ramsey. The bound T2 <= 2 x T1 holds for both, so the outcome rule is valid. A comparison of our echo T2 with IBM's published T2 is not like for like and is reported as CANNOT_TELL. Six readings are taken (three flagged, three controls), so one false ABOVE in a world with ratio exactly 2 is possible at about 2.5% per reading.

## Note 2 (29 Oct, 21:40 EDT, before any result was read)
Queue depth read from the processors' status at 21:40: ibm_boston 397 pending jobs, ibm_kingston 86, ibm_fez 3. The boston job (submitted 20:36) was still queued, and the chain would not submit the other two until it finished. The kingston and fez jobs are now submitted in parallel with the boston job. Method, circuits, fits, thresholds and outcomes are unchanged. Only the order of submission changed. Each job still carries its own control qubit and the known-good gate applies per job.

## Note 3 (29 Oct, 21:55 EDT, after the fez and kingston results were read)
Fez q148: the script printed CONSISTENT, but the T2 fit returned 0.117 microseconds, which is exactly the fit's lower bound (0.05 x the second delay), and the measured T1 was 0.82 microseconds against 5.86 published, with the delay grid (set from the published values) far longer than the decay. The plan's rule is that a failed or unbounded fit reads CANNOT_TELL. A fit sitting on its own bound is unbounded on that side, so the reading of fez q148 under the plan is CANNOT_TELL. The script's printed CONSISTENT is kept in results.json as printed and the reading under the plan's clause is published beside it. run_check.py is updated for any rerun to flag a fit on either bound and to read CANNOT_TELL, with a planted self-test for it. No threshold changed.
Also noted: the published results are for a joint measurement now. A later measurement does not date a past record, and IBM does not state whether its T2 is echo or Ramsey, so measured against published T2 is reported as a difference and not scored.
