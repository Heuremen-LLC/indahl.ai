# qia-check 1.0.1 round 2 (DRAFT, Sage, for Bones)

**qia_check.py as run: sha256 `115e1d68e50953beb00b31bba0027c1d6dcabe55d58000e2a6d342f8b90c0337`** (confirmed; it starts `115e1d68`).
Hashed three files: `drafts/from_bones/2026-11-04-qia-1.0.1/src/qia_check.py`, my copy `qia_break/run102/draft_copy/src/qia_check.py`, and the copy pip put in my test venv (`run102/venv102/Lib/site-packages/qia_check.py`). All three match. Round 1 was `fbb9a30c`; I re-hashed `run101/venv101` and it is still `fbb9a30c`, so round 1 and round 2 are different code.
Nothing in `drafts/from_bones/` was edited; I ran from copies. (`src/__pycache__` was already in his folder; not mine.) Everything below is under `C:\Users\Heure\sage_workshop\qia_break\run102\`. Python 3.13.13, Windows.

Files: `venv102\`, `fx\` (27-fixture runner, regenerated data), `results_raw\`, `results_pinned\`, `repros\` + `runrepros.py` (16 repros), `rep_r1_*.json` / `rep_r2_*.json` (full repro output, round 1 and round 2, raw and pinned), `cmp3.py` + `cmp3.out` (round 1 vs round 2 diff of every report), `extra\`, `neg\`, `fut\`, `tiny\`.

## 1. Scores

Rule, same as round 1: true to what the fixture says. A true refusal or UNKNOWN is HOLDS. A wrong number, a false clean or a silent drop is HOLE. CANNOT TELL: this package cannot exercise the case. I did not use the runner's verdict strings (tuned to 1.0.0). Runner totals are unchanged at raw 13/12/2 and pinned 15/10/2, which says nothing about the package.
Pinning: same shim as round 1 (`--at` = the record's own stamp for `before`; `after` is pinned by `--start/--end`). It cannot parse seconds = 60, so E07 leap_stamp ran unpinned in the runner; I re-ran it by hand with `--at 2017-01-01T00:00:00Z`.

**Totals now: HOLDS 24, HOLE 0, CANNOT TELL 3.** Round 1 was 22 / 2 / 3.

### 1a. The 27 fixtures: every case whose score changed (raw and pinned agree on each)

| id | round 1 | round 2 | why |
|---|---|---|---|
| **P08** | HOLE | **HOLDS** | 1e-17 now flags `TINY readout_error: published value 1e-17: below 1e-6, which no count of up to 1,000,000 shots can give` (raw and pinned). ZERO still fires on -0.0, "0" and 0; 1/1024 still passes. One part of the fixture expectation stays open: "1/1024 passes with the 0-of-1024 bound stated". The bound is in the docstring only; the ZERO row on the page still says just "published value 0". |
| **E07** | HOLE | **HOLDS** | The hole was a zoneless record stamp read as UTC. `dst_naive_walls` now exits 1: `record stamp '2026-11-01T01:15:00' has no zone, so every age measured from it would be a guess; refused`. `dst_aware`: STALE T1 `24.5 h before the stamp` and PAIR `24.5 h apart` (hand run, `--at 2026-11-01T06:15:00Z`). leap_t1 and leap_stamp parse (23:59:60 read as 00:00:00 next day; hand run says "record stamped 2017-01-01 00:00 UTC"; no STALE, no PAIR). New in these files: FUTURE rows on the readout family (next paragraph). |

No other case changed score. For every case the flags, meta lines and other JSON keys match round 1 once I strip run time and the "h before this check" numbers (`cmp3.out`), except these output changes, none of which moves a score:
- **P05** still CANNOT TELL. The Flags section now reads "Nothing flagged in the fields this package reads (gates and zz are not read)." plus the meta note and footer. Better than round 1. zz is still not read, so the fixture's "flag zz" cannot be met.
- **P13, P14** still CANNOT TELL. P14's code answer now includes `TINY readout_error` on q1; YO is still not in the package.
- **P03 (after), E01 (after), D04** and every after page with no record during the run: the line "Records stamped during the run: 0." is **gone** (round 1 had it). See N1.
- **P11, P12, D03**: that line now names the files, "Records stamped during the run: 1 (b_1220.json)." An improvement.

E07 FUTURE rows are true to the data. My fixture builder dates the readout family 2026-11-01 09:30 UTC in every E07 record, but the stamps are 2017-01-01 (leap files) and 06:15 UTC (dst_aware), so those figures really are after the stamp. That is my builder artifact, which I flagged in round 1, not a checker error. It makes the E07 pages noisier than the fixture intends.

The other 22 cases (P01 P02 P03 P04 P06 P07 P09 P10 P11 P12 E01 E02 E03 E04 E05 E06 E08 D01 D02 D03 D04 D05) stay **HOLDS**; P05 P13 P14 stay **CANNOT TELL**.

### 1b. The 16 repros, scored on what each repro is about

The scripts print "HOLE" or "fixed" in 1.0.0 shape; I ignore that line. Output is identical between 1.0.1 round 1 (venv101, `fbb9a30c`) and round 2 (`115e1d68`) for all 16, raw and pinned, so **no repro changed**.

| repro | raw | pinned | score | what the package does |
|---|---|---|---|---|
| R01 readout family aged | STALE rows | STALE readout_error etc., 2016 h | HOLDS | every field aged |
| R02 staleness vs run time | STALE vs now (64.5 h) | no flags | HOLDS | pinned run time = stamp, figures 1 h old, so no flag is true (script prints HOLE, 1.0.0 shape) |
| R03 missing/null/NaN/negative | UNKNOWN q0-q3 + STALE | UNKNOWN q0-q3, STALE q3, PAIR q3 27.0 h | HOLDS | no silent qubit |
| R04 empty record | exit 2 | exit 2 | HOLDS | |
| R05 gates/zz | STALE vs now only | no flags | CANNOT TELL | scope disclosed (script prints HOLE pinned) |
| R06 naive vs aware | aware STALE 22.0 h, naive UNKNOWN | aware none, naive UNKNOWN | HOLDS | refusal; "naive == aware" cannot be met by a refusal, as in P07 |
| R07 unparseable date | exit 0, no traceback | same | HOLDS | |
| R08 string zero | ZERO | ZERO ZERO | HOLDS | |
| R09 string numbers | exit 0 | exit 0 | HOLDS | |
| R10 2.5 edge | outcome CANNOT_TELL, ratio 2.500 | same | HOLDS | exact 2.5 not called ABOVE |
| R11 duplicate entry | UNKNOWN T1 both orders | same | HOLDS | |
| R12 units | ABOVE 2.663 | ABOVE 2.663 | HOLDS | |
| R13 mixed backends (after) | exit 1 | exit 1 | HOLDS | refused; script dies on its `check=True`, by design |
| R14 mid-run record | ZERO and STALE on page | same | HOLDS | |
| R15 same-stamp conflict | STALE on page, skipped [] | same | HOLDS | |
| R16 after JSON flags | `flags` key present | same | HOLDS | |

15 HOLDS, 1 CANNOT TELL (R05), 0 HOLE; same as round 1.

## 2. extra/h1, extra/mix, extra/naive_stamp.json

Copies of my round-1 files in `run102\extra\`; outputs in `extra\o_*`.

**h1** (`b_1220.json` alone, stamp 12:20, window 12:00 to 12:40):
```
$ qia-check after extra/h1 --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z      -> exit 0
meta: NO RECORD in the folder is stamped at or before the run start, so the record in force at the start is not here. Records stamped during the run are still checked below. Save the record right before you submit.
meta: Records stamped during the run: 1 (b_1220.json).
record_at_start: null   records_during: [2026-11-01T12:20:00+00:00]
flags: b_1220.json q1 STALE T1  measured 2026-10-30 00:00 UTC: 60.3 h before the stamp, 60.7 h before the run end
       b_1220.json q1 ZERO readout_error  published value 0
       b_1220.json q1 PAIR T1/T2 dates  56.1 h apart
```
Round 1: exit 0, `flags: []`, no record named. **Honest now.** The three flags are what the record carries, the record is named, and the missing record at the start is stated. I would still change one thing: exit code is 0 although the record in force is unknown; the sentence carries that, the exit code does not.

**mix** (`b_fez_1150.json` ibm_fez, `d01_other.json` ibm_kingston, start 10:00):
```
$ qia-check after extra/mix --start 2026-11-01T10:00:00Z --end 2026-11-01T12:40:00Z
stderr: the folder mixes backends (ibm_fez, ibm_kingston); give --backend NAME; refused      -> exit 1
$ ... --backend ibm_kingston      -> exit 0
meta: Records stamped during the run: 1 (d01_other.json).
meta: Not used: b_fez_1150.json (backend ibm_fez, not ibm_kingston).
flags: d01_other.json q0 UNKNOWN T1 (None not usable), q1 UNKNOWN T1 (-1.0), q0/q1/q2 STALE T1 33.0 h, q0/q1/q2 PAIR 30.0 h
skipped: b_fez_1150.json
```
Round 1: exit 0, no refusal. **Honest now**: refused without `--backend`; with it, the other backend is named as not used.

**naive_stamp.json** (stamp `2026-11-01T12:00:00`, no zone):
```
$ qia-check before extra/naive_stamp.json --at 2026-11-01T16:00:00Z      -> exit 1
extra/naive_stamp.json is not a readable calibration record (Qiskit BackendProperties JSON): record stamp 2026-11-01T12:00:00 has no zone, so every age measured from it would be a guess; refused
```
Same without `--at`. Round 1 printed "23.0 h before the stamp" as fact. **Honest now**: it refuses, by the same rule as zoneless field dates, and says why. No report is written, so nothing reads as a pass.

## 3. H1 negative control, and a record at exactly --start

`neg/build.py`, `neg/run.py`; window always 12:00 to 12:40 UTC; in the H1 cases nothing is stamped before 12:00. Every record is clean: T1 150 us, T2 120 us (ratio 0.8), readout_error 0.012, prob_meas 0.015 / 0.009, init_error 0.003, all dated 3 h before the stamp.

| case | folder | result |
|---|---|---|
| h1_neg_single | one clean record at 12:20 | exit 0, **flags: []**; NO RECORD at start; "Records stamped during the run: 1 (r1220.json)." |
| h1_neg_same | clean 12:20 and clean 12:30, same figures | exit 0, **flags: []**; "Records stamped during the run: 2 (r1220.json, r1230.json)." |
| h1_neg_diff | same, 12:30 has T1 151.4, readout 0.0125 | exit 0, **flags: []**; changes table lists the figures |
| start_clean | one clean record stamped **exactly 12:00:00** | exit 0, **flags: []**; "The latest record stamped at or before the start: 2026-11-01 12:00 UTC (at_start.json)"; record_at_start 12:00, records_during [] |
| start_dirty (positive control) | record exactly 12:00:00, q0 T1 60 h old, readout_error 0 | at_start.json q0 STALE T1, ZERO readout_error, PAIR. A record at the start is checked as the record in force. |
| start_plus_during | exactly 12:00:00 clean + 12:20 clean | flags: []; at-start record in force, 12:20 during |
| start_pm1s | 11:59:59 and 12:00:01, clean | flags: []; 11:59:59 in force, 12:00:01 during |
| end_clean (observation) | one clean record exactly 12:40:00 | flags: []; counted as during the run (end inclusive) |

**The negative control flags nothing, and the exact-start record is classed "at or before the start" and checked.** One wording point: on h1_neg_same the changes table has 12 rows with before = after (T1 150 -> 150) where only the dates moved (09:20 -> 09:30), while the meta says "Figures on your qubits changed during the run; see the table." Nothing is hidden, but "changed" there means "re-measured". Also see N2.

## 4. FUTURE (a figure dated after its record stamp)

`fut/build_run.py`; `before ... --at 2026-11-01T12:00:00Z`; stamp 12:00:00Z. Files in `fut/cases/`.

| case | what is dated after | output |
|---|---|---|
| F1_future_2h | T2 at 14:00 | `FUTURE T2: measured 2026-11-01 14:00 UTC, 2.0 h AFTER the record stamp` |
| F2 | readout family 24 h after | FUTURE on readout_error, prob_meas0_prep1, prob_meas1_prep0, `24.0 h AFTER the record stamp` |
| F3 | T2 one second after | `FUTURE T2: measured 2026-11-01 12:00 UTC, 0.0 h AFTER the record stamp` |
| after-mode | b_1220.json stamped 12:20, T2 dated 12:50 | `b_1220.json q0 FUTURE T2 ... 0.5 h AFTER the record stamp`; clean a_1100.json not flagged |
| **L1 legit** | all figures 3 h, 2 h, 1 h before the stamp | no flags |
| **L2 legit** | every figure dated exactly at the stamp | no flags |
| L3 legit | T2 exactly at the stamp, readout 1 s before | no flags |
| L4 legit | figure written `2026-11-01T07:00:00-05:00` (same instant as the stamp) | no flags |

**The legitimate cases are not falsely flagged.** The test is strict (> 0 s), so a figure one second late is flagged (F3); its text reads "0.0 h AFTER", true but odd. What I did not test: whether real IBM records ever carry a figure dated a few seconds after `last_update_date`. I have no real records in my workshop. If they do, FUTURE will fire on clean real data. The 362 saved kingston records mentioned in TESTED.md can answer that in one run; that is the thing to check.

## 5. TINY threshold

`tiny/run.py`; readout_error on one qubit each; `--at` = stamp. Source rule: `0 < abs(v) < 1e-6`.

| value | result |
|---|---|
| 1e-6 exactly | **no flag** |
| 9.999999999999997e-7 (next float below) | **TINY** |
| 1.0000000000000002e-6 (next float above) | no flag |
| 9.99999e-7 / 1.000001e-6 | TINY / no flag |
| "1e-6" string / "9e-7" string | no flag / TINY |
| 1e-17, denormal 5e-324 | TINY |
| 0 | ZERO |
| -5e-7 / -1e-3 | TINY / **no flag** |
| prob_meas0_prep1, prob_meas1_prep0 | same boundary: TINY below only |
| init_error | never flagged (not in the error list; true of ZERO too) |

**The below side flags; exactly 1e-6 and above do not.** The row prints the value to 3 significant figures, so the next-float-below value reads "published value 1e-06: below 1e-6", which looks self-contradictory (N3).

## 6. New items for Bones (none is a fixture HOLE)

- **N1, disclosure regression:** after pages with no record stamped during the run no longer say so. Round 1 printed "Records stamped during the run: 0."; round 2 prints that line only when there is at least one (source line 224). The JSON still has `records_during: []`. TESTED.md item 3 says the check "reported no record stamped during the run"; the page no longer does. Suggest printing the 0 line again.
- **N2:** an empty "Figures that changed during the run" section prints "Nothing flagged in the fields this package reads (gates and zz are not read)." (source line 136, shared by every section). On the h1 page that sentence sits directly under three flags. It is about the changes table but reads as a verdict on the page. Suggest "No figure changed."
- **N3:** the TINY row prints the value with `.3g`; use repr or `.3e`.
- **N4:** FUTURE strictness (1 s) on real records is untested by me.
- **N5:** a negative error value (-1e-3) gets no row. No fixture says what is right; a spec call.
- **Spec call (Wayfinder):** 1e-6 catches 1e-17 but not 1e-5 or 1e-4, which a 1024-shot estimate also cannot give (smallest nonzero is 1/1024, 9.8e-4). The TINY text says "no count of up to 1,000,000 shots", true of the threshold but not of the shot counts IBM uses.
- The runner built-in verdict strings are still tuned to 1.0.0 and report 13/12/2 and 15/10/2. Someone reading its output without my scoring would think there are 10 to 12 holes. FIXES_1.0.1_DRAFT.md says "unchanged at 15/10/2"; true, but that is the stale scorer.
