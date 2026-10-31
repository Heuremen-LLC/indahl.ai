# Addendum (record the job ran under) -- written 2026-10-24T19:19Z, BEFORE any result exists for this folder

Fact: props_kumar_before_*.json was saved at submit time (06:48:33 local, 24 Oct). The submit then blocked:
IBM's job list shows NO ibm_marrakesh job since then, and at 19:19Z ibm_marrakesh reports status "maintenance", 723 pending.
So the saved "before" record predates a maintenance and is NOT the record the job will run under (/q check 3).

Rule, fixed now:
1. The record the job ran under = the backend properties at the job's own start time (job.metrics timestamps), pulled with
   properties(datetime=<job start>) after the job; props_kumar_after.json is the cross-check.
2. props_kumar_before_* is kept and labelled "pre-maintenance record, not the run's record". Any stated-vs-delivered line uses rule 1 only.
3. If rule-1 record and props_after disagree on a qubit/pair used, that line is CANNOT_TELL for the record match.
4. The layout/transpile was chosen on the pre-maintenance record. If any used qubit or pair is missing or flagged in the rule-1 record,
   the run's readings on it are reported as such, not dropped.
