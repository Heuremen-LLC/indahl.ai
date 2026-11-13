# Recovering a nulled cycle number from the id sequence

**Status:** worked once, by hand, under supervision (2026-09-04, rows 26649 and 26650 in
`cycles_v2`, `~/bones-forge/gridsong/nova_corpus.db`). Sage's ask: write the method down so
it never lives only in a conversation. **Not safe to run unsupervised or at scale as written.**

## When it applies

A row in `cycles_v2` with `source='nova_resonance_log.json'` (the GridSong loop) has
`cycle IS NULL` and `kind IS NULL` or `kind='cycle'`, and it was written during a window
where the writer didn't stamp kind (the 9/4 rebuild gap, or any future migration gap).
GridSong writes one row per cycle, in order, ~40–90 s apart, with `id` autoincrementing.

## The method

1. **Isolate the gap.** `SELECT id, cycle, ts_full FROM cycles_v2 WHERE source='nova_resonance_log.json' AND id BETWEEN <first_null_id - 5> AND <last_null_id + 5> ORDER BY id`.
2. **Check the neighbors are consecutive.** The rows just before and after the gap must have
   `cycle` values that differ by exactly `(number of gap rows) + 1`. If they don't, STOP.
   The gap contains a restart, a burned cycle, or a second writer, and interpolation would
   invent a number (the 62-Z disease with integers).
3. **Check the timestamps are monotonic and evenly spaced** across the gap (GridSong cadence
   is stable within a run; a jump > 3× the local spacing means a restart, STOP).
4. **Fill by sequence**, one row at a time, `cycle = previous_cycle + 1`, set `kind='cycle'`.
5. **Verify** the filled rows against the resonance log if the timestamps can be matched
   (`grep -a "cycle <N>" resonance_output.log`), or at minimum re-run step 2 on the result.
6. **Write it down** in `corpus_notes` with the ids, the numbers, and who did it.

## Why it is not safe unsupervised

- Step 2 and 3 are judgment calls dressed as checks; a script will pass them on a gap that
  straddles a restart if the counts happen to line up.
- A wrong fill is a silent overwrite of the truth with a plausible number — the exact
  failure class this whole night was about (see the 9/4 consent audit).
- The right structural fix is upstream: writers always stamp `kind`, and any migration that
  touches `cycle` runs with the loop paused. That was done 9/4. This runbook is for the
  case where it wasn't.

## The two rows it was used on

| id | recovered cycle | ts_full | neighbors |
|---|---|---|---|
| 26649 | 16454 | 2026-09-04T19:23:08 | 26648 = 16453, 26651 = 16456 |
| 26650 | 16455 | 2026-09-04T19:23:52 | same |

Spacing 44 s both sides, sequence consecutive, log not consulted (timestamps in the log are
not per-line). Verified by neighbors only. Noted here so the confidence level is honest.
