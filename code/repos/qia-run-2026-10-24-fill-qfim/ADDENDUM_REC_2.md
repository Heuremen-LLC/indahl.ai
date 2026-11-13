# Correction to ADDENDUM_REC_1 -- written 2026-10-24T20:17Z, before any result of this folder is read

ADDENDUM_REC_1 says IBM's job list showed no ibm_marrakesh job. That was wrong: my listing used created_after 12:00Z, and the
jobs were created ~10:02-10:48Z (06:02-06:48 local). IBM's list (read now) shows this folder's job QUEUED/RUNNING since then,
held across the marrakesh maintenance. The rule in REC_1 stands unchanged: the record the job ran under = properties at the
job's own start time; props_before (saved at submit) is the pre-maintenance record and is not used for stated-vs-delivered lines.
