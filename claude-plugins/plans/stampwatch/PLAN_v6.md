# stampwatch: plan amendment v6

Heuremen LLC, 13 November 2026. Amends PLAN.md and v2 to v5, which stay as they were. Answers the outside referee's pass on v5 (verdict
FIX: HF may open after three fixes and three days of snapshots; CKAN held). Code sha256 5c0ff58fd5a92cf1160a77a7d15707e8f3adf09d7bb3d7399e12570fc8a5cc2c; planted self-test 28 of 28.

## Feed fixes

- Read times parse in the collectors' format (20261113T172813Z, as both collectors write) or ISO; anything else refuses the snapshot.
  The repeat floor is the first snapshot at least 300 s after the first one. With no such snapshot there is no floor pair, and every unit
  is excluded from direction B. Planted: a snapshot 2 minutes after the first is not taken; one 6 minutes after is.
- A unit with no repeat-floor pair (for example a resource added later) is excluded from direction B and counted (no_repeat_floor).
- CKAN bytes are stored by their own sha (store/<resource>__<sha12>.csv.gz); a CARRIED candidate is diffed a-sha against b-sha. A
  CARRIED with no stored bytes for either side reads CANNOT_TELL (NOT_RELEASED) and is never counted as CARRIED. Reordered rows read
  reorder_only, CANNOT_TELL (METHOD_UNSTATED). The unused store_key is cut.
- The feed CLI counts an unreadable snapshot as NOTHING_RETURNED and carries on.
- specs/hf.json content is the full sibling map (every file name and blob id, README, config and weights alike).

## IBM fixes

- Stamps compare as instants (norm), not strings.
- The single-restamp planted case runs in its own ibm_read at u = 0.001: k = 1, n = 156, p = 0.1445, family m = 2, outcome CONSISTENT.
  The real-floor k = 1 and k = 2 checks are labelled BH arithmetic on hand-built families, not end to end.
- The comparator check is printed per field, with the same type test as rule 4. Identical values under unmoved dates in the yo/history
  test pairs: T1 382,807; T2 380,676; readout_error 292,759; prob_meas0_prep1 297,952; prob_meas1_prep0 292,759.

## Q6 reconciliation

The referee's earlier count read heuremen.org/experiments/calibration-records/restamp_check/ (25 records; file names carry the pull date,
sometimes the time; date-only names are read at day precision). The plan's code on that folder: 25 indexed, 0 refused; 2 duplicate
snapshots (one stamp in two files); 13 pairs with every T1/T2 date unchanged (the earlier count of 14 counted a duplicate file as a
separate pair). By the plan's Q6 rule (stamp gap over 24 h): 4 positive pairs (boston 09-22 to 09-24, boston 09-24 to 09-26, phoenix
10-05 to 10-06, pittsburgh 09-16 to 09-17); the other 9 frozen pairs are under 24 h and unclassed. No pair is FROZEN_RECORD: content
under the stamp changed in every pair. The 3 remeasured pairs are the negatives (boston 09-19 to 09-21, boston 09-26 to 10-02,
marrakesh 09-21 to 10-22 18:21): 0 restamped-identical values among 925 date moves; the "2, 2 and 1 identical" of the earlier count are
values whose dates did not move. yo/history, read separately: 6 positive pairs. The two lists are reported side by side, not merged.

## Before HF opens

HF opens when at least 3 days of snapshots exist. Before reading, the n units and n snapshots are published, with the expected counts:
direction A near zero, direction B structurally zero; any label-moved, content-frozen case is an observation about the label, and no
repository is named. CKAN stays held until its real repeat-floor pair (18:03Z and the next collector slot) has been read for
non-determinism alone.

## v6.1 (after the referee's STANDS on v6, two fixes she named as needing no re-pass)

- norm() refuses a time with no offset (it is never read as this machine's local time); planted: '2026-11-13T18:00:00' is refused.
- Pairs sort on (read time, stamp), so day-precision reads are ordered by their stamps; such tiebreaks are counted. restamp_check:
  order_by_stamp_tiebreak 0, stamp_regressions 0, duplicates 2.
- Reorder-only diffs have their own counter (CARRIED_reorder_only).
- Folder overlap, before any Q6 pairs are summed: no file of restamp_check is byte-identical to a yo/history file, but 18 of its 23
  distinct records carry the same backend, stamp and content as a yo/history record. Q6 pairs by backend and both stamps: restamp_check
  4, yo/history 6, shared 1, distinct 9 (two boston pairs share the start stamp 2026-09-23T16:58:19Z and end at different records).
- Code sha256 bb46afefc7c8d31ac3e028f8e5c104dd3d6aedd70f682300bd7a73985c3951ba; planted self-test 28 of 28.
