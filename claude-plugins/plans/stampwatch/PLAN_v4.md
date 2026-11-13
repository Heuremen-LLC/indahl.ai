# stampwatch: plan amendment v4, before rule 4 reads any test pair

Heuremen LLC, 13 November 2026. Amends PLAN.md (f570f1f), PLAN_v2.md (7c0c08d) and PLAN_v3.md (cba7756), which stay as they were.
Answers the outside referee's pass on v3 (verdict MOVES, coding cleared). The code exists (plugins/stampwatch/scripts/stampwatch.py,
sha256 04f55b137439de2d6d8294106547c4f2c6a49c325e5512873650c72742ff7638); its planted self-test passes (13 of 13). No test pair has been read, and no blind snapshot has been read for the fault.
Every number below comes from dates in the floor window, or from values inside the floor window only. Files: witness/ibm_counts_20261113.json,
witness/ibm_floors_20261113.json.

## Floors, read from the floor window only

Identical values among date moves in the floor window, per backend and field: 0 of 172,993 in total (0 on every backend and both
fields). Floor u per backend is therefore the exact 95 % upper bound of 0 of n: about 0.00021 to 0.00027 per backend, 0.00086 on phoenix
(4,280 / 4,331 moves). Leave-one-backend-out: every backend reads CANNOT_TELL against the other five, because both sides are 0; no
backend shows a habit that its own floor could absorb. Readings use the per-backend floor; the cross-backend floor is printed beside it.
Not tested: a habit present on every backend is absorbed into every floor and cannot be seen by rule 4.

## Expected outcomes written before any test pair is read

- At the real IBM floor (u about 0.00022, n about 150 date moves in a pair): k = 1 identical restamp gives p about 0.032; k = 2 gives
  p about 0.0005. With 12 readings in the negative run, the Benjamini-Hochberg threshold for the smallest p is 0.0042. So one identical
  restamp in a pair reads CANNOT_TELL or CONSISTENT, not ABOVE; two or more in one pair read ABOVE. Any ABOVE on a real pair is a reading
  about that pair ("this pair has more identical restamps than the floor predicts"), never "a lazy restamp", and it gets a second reader
  before anything says it.
- Planted single-restamp case: u = 0.001, n = 156, 31 readings in its run, expected p = 0.145; it must come out as an unflagged count
  (it does). Not tested, amended: a single restamp with an identical value is not distinguishable from chance where n x u is not small.
- Rule 4's recall rests on planted cases only. The house holds no real-data known positive for RESTAMPED_IDENTICAL: Q6 pairs are
  positives because their dates did not move, so they test FROZEN_RECORD and FROZEN_DATE, not rule 4.

## Pair classes, per field (counts of classes from dates only)

Pairs are classed per field (T1 and T2 separately). "Unchanged" means the field's date is unchanged. Outside the floor window, with a
stamp gap over 24 h: positive 6 pairs for T1 and 6 for T2; negative 6 and 6; between 0 and 0; pairs with a stamp gap of 24 h or less
(unclassed) 2,770 per field. A field whose value changed while its date did not is counted as its own observation, never classed.
Duplicate snapshots of one stamp found by the code: 0. The referee's dig reported two boston files holding one stamp; the code
compares stamps as strings after parsing, and this difference is reported, not resolved by hand.

## Kill condition, with its denominator

Negative set: 12 record-by-field readings (6 T1, 6 T2). That is under 100, so any flag kills. The expected count of raw p-values at or
under 0.05 under the floor (an upper bound on Benjamini-Hochberg flags) is 0.20 for T1 and 0.20 for T2, so the kill has roughly a one
in three chance of firing on chance alone at this n. We state that now rather than change the rule after: if it fires, stampwatch ships
"lazy restamps only" (FROZEN counts, no RESTAMPED_IDENTICAL outcome) until more negative pairs accumulate.

## CKAN

A resource over 20 MB is recorded as dropped (too_large, with its size from the resource metadata), counted, and excluded from
direction B; NOTHING_RETURNED is kept for fetches that fail. A CARRIED candidate whose changed lines differ only in datetime-shaped values
reads CANNOT_TELL (METHOD_UNSTATED). Every CARRIED is printed with a diff summary (rows added, removed, changed, columns touched).

## Small

Leave-one-pair-out stays in the code but is not described as a guard (test pairs are all outside the window). Archive.org capture URLs
go in witness/ once they resolve; the first request returned an error and is retried.
