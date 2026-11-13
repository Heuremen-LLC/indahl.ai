# stampwatch: plan amendment v3, before rule 4's code

Heuremen LLC, 13 November 2026. Amends PLAN.md (f570f1f) and PLAN_v2.md (7c0c08d), which stay as they were. Answers the outside
referee's pass on v2 (verdict MOVES): rule 4 as written in v2 gave every single event the same p-value, so it moves to a grain with
n > 1. Everything else in v2 stands except where changed below.

## Floor window, counted before any test pair is read

Saved IBM records stamped 2026-05-04 to 2026-09-14: 6,543 records, 6 backends. Date moves of T1 / T2 in that window:
boston 13,432 / 13,482; fez 17,377 / 17,863; kingston 17,676 / 17,981; marrakesh 16,384 / 17,151; phoenix 4,280 / 4,331;
pittsburgh 16,446 / 16,590. Total 85,595 / 87,398. These are counts of date moves only; no value was compared.

## Rule 4, replaced: record-by-field reading

- Unit of reading: one backend, one consecutive snapshot pair, one field (T1 or T2). Count k identical restamps (the field's date moved
  and its value is bitwise identical) among n date moves of that field in that pair.
- Floor u: the exact 95 % upper bound of the identical-on-date-move share for that field, per backend where the backend has at least
  500 date moves of the field in the floor window (every backend above does), learned leave-one-pair-out from the floor window only.
- Test: one-sided exact binomial P(X >= k | n, u). Benjamini-Hochberg at q = 0.05 across all record-by-field readings in the run.
- Outcomes: ABOVE when flagged. CONSISTENT when the exact 95 % upper bound of k/n is at or below u + 0.05 (the size that matters, named
  now). Otherwise CANNOT_TELL (TOO_WIDE_TO_RESOLVE). A field with fewer than 500 floor-window date moves on every stratum reads
  CANNOT_TELL (NO_INTERVAL_FORMABLE).
- Single RESTAMPED_IDENTICAL events are observations, counted and printed beside their chance expectation (n x u). They are never
  outcomes. Not tested: a single restamp with an identical value is not distinguishable from chance at a nonzero floor.

Planted cases under this grain: one record where 20 of 156 qubits restamp T1 with bitwise-identical values against a realistic floor
must read ABOVE; one planted single identical restamp must come out as a count that is not flagged.

Kill condition denominator: record-by-field readings in the negative set. That n is published before reading. If n < 100, any flag
kills; otherwise more than 1 % flagged kills.

## Pair classes, defined

- Positive (Q6): stamp moved by more than 24 h and T1/T2 unchanged on at least 95 % of qubits.
- Negative: stamp moved by more than 24 h and field dates moved on at least 50 % of qubits.
- Between: stamp moved by more than 24 h and T1/T2 unchanged on more than 50 % and less than 95 % of qubits. Neither class; listed by
  count and reported as observations.

## Shot-quantized IBM fields

readout_error, prob_meas0_prep1 and prob_meas1_prep0 have no outside reference, so they are not tested under rule 4 or rule 5. Their
FROZEN_DATE and FROZEN_RECORD counts are still reported as observations. (readout_error is the mean of the two prob_meas fields; its
step is 1/(2 x shots).)

## CKAN blind feed, repeat floor and frame

- In the first collection round each CSV resource is fetched twice, at least 5 minutes apart. A resource whose two fetches differ is
  non-deterministic: excluded from direction B, listed by count, reported as CANNOT_TELL (METHOD_UNSTATED).
- Size cap 20 MB. A larger resource is recorded as NOTHING_RETURNED (too_large), counted, and excluded from direction B.
- The sample frame (the first 1000 CSV datasets by metadata_created at draw time) is saved with its sha256, so the draw can be repeated.
- Results name no dataset or publisher as at fault.
- The seed (f570f1f's hash) makes the draw a fixed rule. It is not outside-random: a self-made hash could in principle be re-rolled.

## Witness that lasts

The repository activity record for the plan pushes is saved in witness/ (f570f1f pushed 2026-11-13T17:26:00Z, 7c0c08d pushed
17:59:22Z). An archive.org capture of each plan file is requested. Each blind-feed collector appends to a manifest (file, sha256, read
time); the manifests are pushed to this repository daily, so the series is outside-witnessed as it grows.
