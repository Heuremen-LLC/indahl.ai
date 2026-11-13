# YO -- research plan (written 23 Oct 2026, ~09:00 EDT, before the history pull and before any YO v1 result was read). Wayfinder and Bones.
Working question: can a small open-weight model (Qwen3-1.7B, Apache-2.0) be trained to read a vendor's stated device calibration the way an
auditor does -- flag figures that are stale or zero under a fresh stamp, and give a FOUR-outcome verdict (ABOVE / BELOW / CONSISTENT /
CANNOT_TELL) on stated-versus-measured, instead of the two-outcome verdict models default to?
YO v1 (PLAN_YO_V1.md, sha ea078dc09c03cfe0) is the PILOT: 72 records, reported as a pilot, never pooled into the main result.

## Data (main experiment)
- IBM properties history for every backend the open instance lists (fez, kingston, marrakesh), pulled with backend.properties(datetime=t)
  at 2-hour steps over the last 180 days; distinct (backend, stamp) kept; zero QPU seconds. Saved gzipped under yo/history/.
- Split by stamp: TEST = last 30 days (stamps on/after 2026-09-23 00:00 UTC); TRAIN = older; VALID = last 10 % of TRAIN by stamp.
## Jobs
- A. RECORD AUDIT: as PLAN_YO_V1 Job A (8 seeded qubits, stale = T1/T2 dated > 24 h before the stamp; zero = error value exactly 0).
- C. FOUR-OUTCOME VERDICT: input = a reference value r, an estimate and its 95 % interval [lo, hi], and an equivalence margin d.
  Truth (stated in the prompt): ABOVE if lo > r; BELOW if hi < r; CONSISTENT if r-d <= lo and hi <= r+d; otherwise CANNOT_TELL.
  Items: every ledger row with numeric lo/hi whose claim says delivered/stated or ratio (r = 1) or difference (r = 0), d = 0.05 for ratios
  and 0.01 for differences; plus draws from the TRAIN records' own T1/T2 values (r = stated, interval from a seeded relative width 2-40 %).
  Ledger items are TEST only (they are our published readings); record-derived items follow the record split.
- B. FAULT FAMILY: as PLAN_YO_V1 Job B, reported as an appendix (house-specific labels).
## Nulls (scored BEFORE training on the same TEST items)
- A: flag nothing; base Qwen3-1.7B.  C: always CONSISTENT; base Qwen3-1.7B; and the binary rule (ABOVE/BELOW else CONSISTENT) that never says CANNOT_TELL.
- Reported for every null and YO: score, and for C the share of CANNOT_TELL truths answered CANNOT_TELL (the "forced verdict" rate).
## Rule
YO beats a null on a job only if the paired bootstrap 95 % interval (2000 resamples of TEST items) of the score difference sits above 0.
Every job and every null reported, whatever they say. No mechanism or framework vocabulary in the paper.
