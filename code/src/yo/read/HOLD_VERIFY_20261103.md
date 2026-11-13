# YO Read: check of Sage's 3 Nov findings before the hold (3 Nov 2026, evening)
Referee: Sage, MOVES, filed 2026-11-04T00:36:09Z (19:36 EST 3 Nov), armature:/c/Users/Heure/projects/sage_referee/2026-11-04T00-36-09_yo-second-read-and-the-published-read-result.md
Scripts: yo/read/verify_20261103/ (rebuild.py, texts.py, labels.py). They import yr_data.py unchanged and only swap which list.json it opens.

## Build-time List
The items were built 2 Nov 06:25 (git 33be5c6). list.json.pre-removal-20261102 rebuilds them exactly: 688 papers, 148 TEST,
0 TEST label differences from data/test_items.jsonl. data/*.jsonl still match DATA_YO_READ.sha256 (committed in 33be5c6).
Counts below are against that List unless marked "today".

## (a) Wrong text given to YO
Test (the draft's): YO's input file under half the size of the file the List reader read (sweep_20261101/texts_read/).
- Build-time List: 103 papers (94 short, 9 empty). TEST 22 of 148 (20 short, 2 empty). TRAIN 75, VALID 6.
- Today's List: 91 papers (82 short, 9 empty). TEST 17 of 142. These are the draft's numbers. They are smaller because 17 papers left the List's "Full text" set after the build.
- 83 reader records give a bare file name: they read texts/, the same file YO read, so they are not counted.
- It touches DATES: every paper has a DATES item built from that text. 22 of 148 TEST DATES items. 5 of them got "(no sentence matched)".
  Seed 61 DATES on those 22: 15 right. On the other 126: 0.929. Seed 62 14/22, seed 63 16/22, REGEX 16/22, MAJORITY 11/22.
  7 of seed 61's 16 TEST DATES errors are on these papers. Descriptive only, not a rescore.

## (b) truth() wording fault
- DATES in TEST: not affected. Every date line in a TEST paper's F4 is the exact phrase "run dates not printed" (119 lines, 119 NO labels).
  Across all 688 one DATES line is missed (ax:2112.05821, TRAIN). Separate from truth(): the second read holds 2 TEST DATES entries (#2, #39)
  where the List reader counted a non-run date. Those are held, not settled.
- LINK in TEST: 5 labels came out YES where the List entry says no URL, DOI or repository (ax:2210.17548, ax:2304.04666, ax:2306.01639,
  ax:2401.10293, ax:2406.09316). Today's List: 6 (the 2 Nov 16:44 linkfix wording "prints no data link" is also missed).
- REQUEST from a negated line: 1, TRAIN only.

## (c) List changed 3 Nov 13:58, labels cannot be rebuilt
- The List did change (list.json mtime 3 Nov 13:58, decker edit). It had already dropped from 687 to 671 papers before 3 Nov 13:21 (pre-ramm snapshot).
- Today's list.json does not rebuild the scored labels: 6 TEST papers gone, 3 labels changed.
- The scored labels are not lost: data/test_items.jsonl is intact under its committed hash, and list.json.pre-removal-20261102 rebuilds it with 0 differences.
  This finding does not hold as stated.

## Also seen
- The KNOWN-GOOD check in yr_data.py is `assert all(i['answer'] == i['answer'] ...)`, which is always true.
- The same YO Read rows (score and "cleared ... to go to work") are also public in the IRIS lab results table, fed from yo/yo2_result.json via KV key yo (/iris/yo.json). No ledger row covers them.
