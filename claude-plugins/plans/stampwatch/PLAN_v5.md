# stampwatch: plan amendment v5

Heuremen LLC, 13 November 2026. Amends PLAN.md and v2 to v4, which stay as they were. Answers the outside referee's pass on the code and
the IBM controls (verdict: FIX; blind feeds HOLD, keep collecting). Code sha256 51832bcd3764c0faf92e2958e99e356828a4af88ea9378fff056919b8e08db6e; planted self-test 25 of 25, end to end through
ibm-index, pairs, observe and ibm-read on synthetic records written to disk with read-time file names.

## u when the floor holds no identical value

The floor window holds 0 identical values in 172,993 date moves. u is then the 95 % upper bound of a rate never observed, about 3/n: it
measures how much history we hold, not a noise rate (phoenix's looser u comes from fewer records). The output says so beside every floor.
CONSISTENT is worded "the pair's identical share is bounded below u + 0.05", never "matches the floor".

## Rule 4: one Benjamini-Hochberg family per class

Each pair class (negative, positive, between, unclassed) is its own BH family, and the family size m is printed with every reading.
Before reading, the smallest k that could be flagged (as the family's smallest p) is printed per backend and field (witness/ibm_counts_v5):
negative family (m = 12): k = 2 on every backend; unclassed family (m = 5,540): k = 3 or 4. At the real floor, k = 1 (p about 0.038) is
unflagged in both families; k = 2 is flagged with m = 12 and not with m = 5,540 (planted cases). Re-reading under families changed no
outcome: every real pair has k = 0.

## Not tested, added

The real-data negative set contained 0 RESTAMPED_IDENTICAL events. The kill condition passed without being exercised: rule 4 is tested on
planted cases only, in both directions. The comparator does return "identical" on real IBM values (1,646,953 identical values under
unmoved dates in the test pairs), so the zero is about remeasures, not a blind comparison.

## Pairs and observations

- Pairs are consecutive records in read-time order. Same stamp and same content: a duplicate. Same stamp and different content: CARRIED
  (direction B), kept as a pair and counted. A later read with an earlier stamp: a stamp regression, counted. In the IBM folder: 0, 0, 0.
- FROZEN_DATE now matches the plan: the stamp moved, the field's date and value are unchanged, and other fields under the stamp moved.
- FROZEN_RECORD, FROZEN_QUBITS_ONLY and FROZEN_DATE are reported by stamp-gap bin (up to 1 h, 1 to 24 h, over 24 h). Nothing at 24 h or
  under is headlined: hourly stamps routinely leave most T1/T2 dates alone while gate errors update. Over 24 h in the IBM folder:
  FROZEN_RECORD 0, FROZEN_QUBITS_ONLY 2, FROZEN_DATE T1 983 and T2 941 qubit entries.
- The first run's FROZEN_RECORD of 1,768 (T1, T2 and readout only) and the corrected 0 (every field under the stamp) both stay in CHECKS.md.

## Feeds

The feed adapter loops per unit (a units path, with one '*' to flatten nested resources), sorts snapshots by read_at and refuses files
without one, refuses a spec with evidence but no evidence_content, and counts an evidence stamp that moved with unchanged evidence content
on its own (direction A on the evidence). CKAN: the repeat floor is the first pair of snapshots at least 5 minutes apart; non-deterministic
resources are excluded from direction B; too_large is dropped; the collector keeps the previous bytes of a resource that changed, and every
CARRIED carries a diff summary (rows added, removed, changed, columns touched); a datetime-only diff reads CANNOT_TELL (METHOD_UNSTATED).
Spec files, committed before any blind read: specs/hf.json, specs/ckan.json.

## Q6 reconciliation

Pending the referee's second dig for the folder her first dig read. The plan's Q6 rule will be run on that folder too and both lists
reported side by side with file counts and refusals. yo/history: 9,331 files, 0 refused.
