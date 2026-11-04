# Stamp log, PLAN_YO_FRESH (times read from the file record: stat mtimes and STAMPED_AT.txt)
- 22:48:30Z  PLAN_YO_FRESH.md stamped.
- ~23:00Z    overlap check first run inline in the shell (no output file kept).
- 23:01:04Z  PLAN_YO_FRESH_ADDENDUM1.md stamped. WITHDRAWN before any run: item 2 gave the overlap run as "~23:10Z" and named yf_overlap.py, which did not
             exist yet. The withdrawn .ots proof file was deleted when the corrected addendum was stamped. That deletion was a mistake: it should have been
             kept. Its existence is recorded here and in STAMPED_AT.txt.
- 23:01:17Z  yf_overlap.py written (mtime) and run: "fresh 288 vs old 671: id 0, arXiv (version stripped) 0, exact title 0, title ratio > 0.9 0".
- 23:01:21Z  addendum item 2 corrected (mtime); 23:01:23Z corrected addendum stamped (this is the one the driver checks).
- No adapter has answered a fresh item: no eval_fresh_* or out_* file exists at the time of writing.
- overlap result at stamp time had no output file; yf_overlap.out is a re-run at 23:03:54Z.
- Rule from here: a withdrawn proof file is never deleted. It is withdrawn in this log and left on disk.
- 23:10:29Z addendum 2 stamped (Sage VERDICT 23:08Z on Addendum 1: MOVES). Addendum 1's proof stays on disk; its rules stand, its test set is replaced by the primary set.
- 23:16:53Z addendum 3 stamped (Sage VERDICT 23:15Z on Addendum 2: MOVES).
- 23:17:24Z addendum 3 re-stamped; the 23:16:53Z stamp is withdrawn because the driver gate call omitted Addendum 3. Its text and proof are kept in withdrawn/.
- 23:20:57Z addendum 4 stamped: pins the 9 adapters, the base snapshot and the driver; records 76 of 88 REQUEST NO are from silence; yf_score_tests.out versions (A2 era = commit 19689c1, sha 04e29dea, kept as yf_score_tests_A2era.out; current = A3).
- 76 of 88 REQUEST NO are from silence.
- 23:23:28Z addendum 5 stamped (last addendum).
- A3 line for yf_drive.sh superseded by A4 at 23:20:57Z; A4 line for yf_drive.sh superseded by A5 at 23:23:28Z. Neither is tampering: the driver changed on purpose, and each addendum says so.
- 23:23:56Z addendum 5 re-stamped; the first A5 stamp (232328) is withdrawn because it said 11 snapshot files (there are 10). Kept in withdrawn/.
- 23:29:19Z addendum 6 stamped: one-shot plus exit-trap stamp. The A5 line for yf_drive.sh is superseded by A6 at 23:29:19Z. From now on yf_drive.sh is not executed until the run.
