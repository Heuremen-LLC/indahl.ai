# qia-check 1.0.1 round 3 (DRAFT, Sage, for Bones)

Everything is under `C:/Users/Heure/sage_workshop/qia_break/run103/`. Nothing in `drafts/from_bones/` was edited. I ran from copies, with a fresh venv (`venv103`) built from a copy of `src/`. I did not run in place, because pip and `__pycache__` would write into his folder. Python 3.13.13, Windows.

## 1. Hash

**`src/qia_check.py` sha256 = `fb754d02674dec64b874be3b89bd943f7e769361d8c736480d760d1a680d066e`.** Confirmed on his file, on my copy (`run103/draft_copy/src/`), and on the file pip installed (`venv103/Lib/site-packages/qia_check.py`). It **differs from round 2** (`115e1d68...`), so this is new code.

## 2. Repros and 27-fixture runner

Scoring rule unchanged: true to what the fixture says. I ignore the runner's own verdict strings (tuned to 1.0.0). Its totals are raw 13/12/2 and pinned 15/10/2, identical to round 2, and say nothing about the package. Pinning uses the same shim as before. E07 leap_stamp can't be pinned by the shim, so I ran it by hand with `--at 2017-01-01T00:00:00Z`.

**Totals: HOLDS 24, HOLE 0, CANNOT TELL 3. Same as round 2. No case changed score, raw or pinned.**

- 27 fixtures: same 24 HOLDS. CANNOT TELL: P05, P13, P14, same reasons (P05: zz is still not read).
- 16 repros: all 16 identical to round 2 in exit code and output, raw and pinned (`rep_r3_*.json` against `../run102/rep_r2_*.json`). R05 is still CANNOT TELL; the other 15 HOLDS.
- Fixture reports compared with round 2 (`cmp3.out`, plus a text diff of every HTML page). **Cases whose output changed (no score change):**

| case | change |
|---|---|
| P03 after (run1), E01 after (run4), D04 after (run0) | gain "Records stamped during the run: 0." (N1), raw and pinned |
| run021 (after page, empty changes table) | empty-changes sentence reworded (N2) |
| run004, run028, run048 | both of the above |

Flags, exit codes and JSON keys match round 2 everywhere else. E07 by hand matches round 2; leap_stamp gives 3 FUTURE rows, my builder artifact, flagged in round 2.

## 3. N1: fixed

after page, one record at 2026-11-01 12:00, window 2026-11-04 12:00 to 12:40, nothing stamped during the run (`n/n1`). Page and JSON meta both carry:

> `Records stamped during the run: 0.`

It sits under "The latest record stamped at or before the start: 2026-11-01 12:00 UTC (rec_s0.json)...". `records_during: []` is unchanged in the JSON.

## 4. N2: fixed, with one leftover

Empty-changes page (same page as N1):

> `No figure changed between records in the run window.`

h1 page (`extra/h1`, `b_1220.json` alone, stamped 12:20, window 12:00 to 12:40):

```
NO RECORD in the folder is stamped at or before the run start, so the record in force at the start is not here. Records stamped during the run are still checked below. Save the record right before you submit.
Records stamped during the run: 1 (b_1220.json).
Flags: q1 STALE T1 ... 60.3 h before the stamp, 60.7 h before the run end | q1 ZERO readout_error published value 0 | q1 PAIR T1/T2 dates 56.1 h apart
Figures that changed during the run: No figure changed between records in the run window.
```

**Does the h1 page read honestly under its three flags? Mostly yes, with one overreach.**
- The old failure is gone: the "Nothing flagged" sentence no longer sits under three flags as a verdict on the page.
- The page names the record, says there is no record at the start, and shows the three flags.
- Leftover: "No figure changed". With one record in the window and none at the start, there is nothing to compare, so this is "no comparison possible", not "no change". The same sentence is fine when the run has 0 records (N1 page). It is wrong-ish with exactly 1 record during the run and no baseline. Suggested: "Nothing to compare: fewer than two records." Exit code is still 0 although the record in force is unknown (noted in round 2).

## 5. N3 and N5: TINY and negatives

Rule in source: `0 < abs(v) < 1e-6`, on `readout_error` and `prob_meas*` only. Printed value is `repr` now (`tiny/run.py`):

| value written | result |
|---|---|
| 1e-6 exactly | no flag |
| 9.999999999999997e-7 (next float below) | **TINY**, prints `published value 9.999999999999997e-07: below 1e-6, ...` |
| 1.0000000000000002e-6 (next float above) | no flag |
| 9.99999e-7 / 1.000001e-6 | TINY (`9.99999e-07`) / no flag |
| "1e-6" string / "9e-7" string | no flag / TINY (`9e-07`) |
| 1e-17, 5e-324 | TINY (`1e-17`, `5e-324`) |
| 0 | ZERO |
| **-1e-3** | **UNKNOWN** `value -0.001 is negative, not a usable error rate` |
| -5e-7 | UNKNOWN (no longer TINY) |

- **Below 1e-6 flags. Exactly 1e-6 and above do not.** Same boundary on prob_meas0_prep1 and prob_meas1_prep0.
- **No case prints "published value 1e-06: below 1e-6".** I grepped every JSON and HTML from this round. Exact 1e-6 is not flagged, so it prints nothing. N3 is fixed.
- A negative init_error is not checked (init_error is not in the error list), as in round 2.

## 6. New UNKNOWN behaviour

Record built by me (`u/u1.json`), `--at` = the stamp:

| qubit | record holds | output |
|---|---|---|
| q1 | empty property list | `UNKNOWN (all): no T1, T2 or error figures for this qubit in the record` |
| q2 | readout_error only, no T1/T2 at all | `UNKNOWN T1: absent from the record` and `UNKNOWN T2: absent from the record` |
| q3 | T1 only | `UNKNOWN T2: absent` |
| q4 | T2 only | `UNKNOWN T1: absent` |
| q5 | T1 fresh, T2 dated 72 h earlier | `STALE T2 75.0 h` and `PAIR 72.0 h apart` (no UNKNOWN) |
| u2 | T2 only, T2 75 h old | `UNKNOWN T1: absent` and `STALE T2 75.0 h`. The T2 gap is still reported, not hidden by the missing T1. |

Meta line: `5 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.` It counts rows, not qubits.

**Burial test** (`u/u3.json`, 156 qubits: 120 empty, 20 missing T1, 16 clean; real faults on q150 to q154):
- 146 rows. The first 140 are UNKNOWN; the six real rows are 141 to 146: ZERO, TINY, T2>2T1 ABOVE, STALE, PAIR, FUTURE. All six present and correct.
- **Not lost, but buried.** Rows are sorted by qubit number only. The table is unstyled (no colour or bold). The one summary line counts UNKNOWNs ("140 figure(s) could not be read"); nothing counts real flags. A real flag on a high qubit is 140 rows down; on q0 it would be on top. Clarity depends on qubit number.
- On real Kingston data this is mild (only q146 is UNKNOWN). A record with many UNKNOWNs on low qubits would push real flags down.
- Suggestion: sort real flags above UNKNOWN, or add "N real flag(s), M UNKNOWN" to meta.

## 7. Real ibm_kingston records

**Yes, 8 files, read-only,** in `drafts/from_bones/real_kingston_records/` (`ibm_kingston__20261001T002246.json.gz` to `...T144640.json.gz`). That folder was not in my first directory listing this session and I did not make it. I worked on copies in `run103/real/`. I can't verify where they came from; they are IBM-shaped (backend_name, 156 qubits, gates, general), and I take them as Bones's real records.

**The 572 records his FIXES file cites (`qia_package/test/recs`, `qia_mirror/records`) are not reachable from here.** I searched my home folder and found nothing. I did not spot-check them and can't confirm N4's "0 FUTURE across 572".

`before` on all 8, `--at` = each stamp: exit 0 every time, **0 FUTURE rows on all 8**, 0 TINY. The first four (00:22 to 06:26 UTC) give 40 flags each, the last four (08:36 to 14:46 UTC) give 35. I **recounted by hand** from raw JSON on two (T002246, T083606):

| item | T002246 | T083606 |
|---|---|---|
| ZERO on prob_meas1_prep0 | 8 (q3 17 20 40 60 89 91 148); matches | 2; matches |
| PAIR > 24 h | 7 (25.1 h on q27 43 107 113 148, 40.7 h on q116, 2380.8 h on q121); matches | 7; matches |
| missing T1/T2 | q146: UNKNOWN T1 and T2; matches | q146; matches |
| STALE | 23 (14 init_error, 7 T1, 2 T2); matches | 24 (15, 7, 2); matches |
| FUTURE | 0 | 0 |

- q146 has readout_error 0.51 and prob_meas about 0.5, and no T1/T2. The package reports only the two UNKNOWNs. Readout error is outside its scope, but it is a dead qubit.
- `after` on the 8-file gz folder, window 2026-10-01 02:00 to 04:30 UTC: record in force is the 01:45 one, 1 record stamped during the run (03:59). All 8 read, `.json.gz` accepted, flag counts equal the `before` runs.

## 8. Open for Bones
1. "No figure changed" with one record in the window and no baseline (h1) reads as a finding when it is not one.
2. Many UNKNOWNs sit in front of real flags: no sort order, no real-flag count.
3. The 572 records could not be checked; the 8 files give 0 FUTURE and matching counts.
4. Spec call still open for Wayfinder: the TINY threshold (1e-6 catches 1e-17 but not 1e-5 or 1e-4).

## Claims sort
Nothing new for me to do. The inventory (`2026-11-04-overnight/CLAIMS_INVENTORY.md`, 22:17) is older than my sort (22:38) and unchanged. The one open item is the 34 "needs eyes" rows (qia.res, bill.r1, faults.none_*, pkg.test, iris.train). Settling them needs source files on Bones's machine, which I can't reach. `drafts/sage_claims_sorted.csv` and `drafts/sage_claims_inventory_sort.md` stand as written.
