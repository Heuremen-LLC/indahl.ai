# qia-check 1.0.1 round 12: `src/qia_check.py.7e` 5edeaa41... against `.7d` c237b0aa... (DRAFT, Sage, for Bones)

All work is in `C:/Users/Heure/sage_workshop/qia_break/run112/`. I edited nothing in `drafts/from_bones/`. I ran from copies in fresh venvs (Python 3.13.13, Windows): `venv_d` (copy of `.7d`), `venv_e` (copy of `.7e`), and `venv_full` (7e plus Bones's pyproject, TESTED.md and CITATION.cff, for the packaging claim). All were built with `pip install ./copy_x`. The installed files hash to `c237b0aa...` and `5edeaa41...`. README means `README.md.7c`, the newest README file. The root `README.md` (4,031 B, 23:26) is older and has no exit-codes or clean-page sections. The `readme` in pyproject points at `README.md`, so a build from the folder as it stands ships the old one.

## Summary

- **Hashes: nothing moved.** 7e is `5edeaa41...`. The FIXES 7e header and the corrected 7d header match their files.
- **Diff 7d to 7e: 6 hunks. Every hunk maps to a stated change, with three unstated side effects, all in hunk 4.**
  - Every skip line now reads `(ExcType: message)` and is cut at 80 characters.
  - A non-string `backend_name` is turned into text and never skipped.
  - A file that fails `sha()` is dropped from the `inputs` list.
- **Fixtures and repros: 16 of 16 repros and 27 fixtures give the same exit codes, stderr, flags and scores on 7d and 7e, raw and pinned.** The only changed case is E01 (skip-line wording). The runner's P11 string match is HOLE on both 7d and 7e. It still flips against 7b, and 7e does not change it.
- **Three of the four after-mode crashes are fixed as stated** (directory named x.json, unopenable file, 9999 stamp with an offset). The good records are still read, rc 0.
- **The fourth crash is not fixed as FIXES says.** FIXES says a numeric `backend_name` is skipped, "tested: rc 0, the good record read". Without `--backend`, rc is 1: `the folder mixes backends (5, ibm_kingston); give --backend NAME; refused`. rc is 0 only with `--backend`, and then the file is skipped as `(backend 5, not ibm_kingston)`.
- **Other tracebacks remain.**
  - Before mode with a leap-second stamp `9999-12-31T23:59:60Z`: OverflowError. The same stamp in after mode is skipped.
  - `--start`, `--end` or `--at` set to `9999-12-31T23:59:59-05:00`: OverflowError.
  - A figure whose `unit` is a list or dict: TypeError in both modes. In after mode it is not skipped.
  - A deeply nested JSON file: RecursionError in both modes. In after mode it is not skipped.
- **Conflicts by figures: fixed for byte-different, figure-identical files.** Two edges are left (section 4):
  - JSON `100` against `100.0` still counts as a conflict, with a sentence and no difference row.
  - Identical start records still print doubled flag rows.
- **Units: the label is now exact to 1e-9 relative and has no false "same value" on unknown units.** At exactly 1e-9 the answer depends on float rounding (section 5).
- **`--out`: all results match what FIXES says.** The file-symlink case is now refused. After mode allows subfolders and refuses the records folder itself.
- **README: it was not changed for 7e, and several lines no longer match** (section 7). The main ones: line 70 ("sits inside the records folder"), line 71 (skipped files), lines 69-70 (zoneless is exit 1 in before mode only), and lines 76-77 (clean page).

## 0. Hashes at the start and the end: nothing moved

Start Wed Nov 4 00:48:37 EST 2026, end 01:00:02 EST. Files: `run112/hashes/hash_start.txt` and `hash_end.txt`. `diff` of the two (hashes, sizes, mtimes): identical.

| item | sha256 | start vs end |
|---|---|---|
| `src/qia_check.py.7e` | `5edeaa41c08ea5c14ed4be7fdb7ed0304b25ca0d5b1dfc3dc708ee1398ac78ea` (26,025 B, mtime 00:48:01) | same |
| `src/qia_check.py.7d` | `c237b0aa69b9a42d0d945e36d6f253cce8f210ee18492cd48f763959a5c6717f` | same |
| `src/qia_check.py` | `44172347d9d786d81a94a73a457299a1ad582a12a0860ba0fa7ff058b9b528dc` | same |
| `README.md.7c` (latest) | `ac42ae426b851b600a6f2e9eb29ca94428a87db978bb38b98f588a2a721413ec` (mtime 23:59:37) | same |
| `README.md` | `e18fbb870d632882c77b161e476258656e1ea5e2157238bb7db688ed5194f429` | same |
| `FIXES_1.0.1_DRAFT.md` | `b0573791a6603511ab1cc4ad4c68375db43fc27552aee6079e8442540b8617f6` (9,921 B, mtime 00:48:01) | same |
| `TESTED.md` | `0b595c52a5d073bad3c053da430c60f8eca45ef32f15bbef209ee678a7fee4b2` | same |
| `tests/baseline_conflict/a.json` | `e5fae4efc6565e48cc480b7dfb32ac4cacc9adfc1f59a8e4c5ce5a64109ab6d5` | same |
| `tests/baseline_conflict/b.json` | `ad1a514df1a6281151249ff8e4bb65b0b00fd970c08851dd441fba4625b975a7` | same |
| `tests/baseline_conflict/d.json` | `afd5ac5a57960e323a81ac8e10b2053479b6d5e2defd78bf871816f48934b6a4` | same |

- The FIXES file is `FIXES_1.0.1_DRAFT.md`. It changed between round 11 (`0a44c4bf...`, 8,630 B) and this round (`b0573791...`). That is Bones's 7e edit, made before I started.
- `find ... -newer hash_start.txt` over the folder finds nothing. `TESTED.md` is unchanged from 7c and does not mention 7e. Its line "held at 24 HOLDS, 0 HOLE, 3 CANNOT TELL through every later draft" is true of 7e by content (section 2).

## 1. The hashes and the diff 7d to 7e

**Hash and headers**
- `sha256(.7e)` starts `5edeaa41c08ea5c1...`: **confirmed**. FIXES line 74 reads `## Round 7e (...) -> src/qia_check.py sha256 5edeaa41c08ea5c1...`, a prefix of the file hash: **match**.
- FIXES line 67 reads `## Round 7d (...) -> src sha256 c237b0aa... (CORRECTED 05:5xZ: this header first said cf10f034 ...)`. The file is `c237b0aa...`: **match**. `cf10f034` appears once in FIXES, inside that correction note.
- **Left over from round 11:** four older entries still end with the sentence `src sha256 c237b0aa...`. They are Round 3b (line 45), 5b (line 48), 7b (line 59) and 7c (line 65). Their own headers say `93455adc`, `c6da3f6b`, `dc7e7525` and `106abc5c`. The trailing phrase is wrong on those four. The 7e item 5 says only "the 7d header hash is corrected".

**Diff** (`run112/diff_7d_vs_7e.diff`): **6 hunks**, 7e is 288 lines and 7d is 280. Hunk numbers are the order of the `@@` headers.

| # | hunk | what it does | maps to a stated change? |
|---|---|---|---|
| 1 | `@@ -46 @@` `when()` | `astimezone` wrapped in `try`; `OverflowError` becomes `ValueError('date out of range: ...')` | **Yes**, 7e item 1 (9999 stamp with an offset). It covers the `astimezone` call only. The `+ 1 s` on the leap-second path (line 51) is not covered. |
| 2 | `@@ -171 @@` new `figs()` | JSON string of a record's figures (value, date, unit, per field per qubit), independent of file bytes | **Yes**, item 2 |
| 3 | `@@ -182 @@` before-mode `--out` | `rd0` is now `dirname(realpath(rec))`, so a symlinked record is resolved to its real folder. The old comparison, using the typed path's folder, is kept as a second `sys.exit` with the same message. | **Yes**, item 6 |
| 4 | `@@ -199 @@` after-mode block | (a) `--out` check: `od == rd or od.startswith(rd + os.sep)` becomes `od == rd`, with a new message. (b) `hs` is filled inside the `try`; `isfile` check; backend name wrapped in `str()`; `TypeError`, `OverflowError`, `EOFError` added; skip text now `(ExcType: msg[:80])`. (c) `fs` is filtered to files that were hashed. | (a) **Yes**, item 3. (b) **Yes for** `sha()` moved inside the `try`, and for `OverflowError` and `TypeError` caught (item 1). **No, flagged:** the `str()` on the backend name, the type prefix on every skip line, and the 80-character cut. (c) **Not stated**, harmless. |
| 5 | `@@ -220 @@` conflict sentence | `hs[x] != hs[y]` becomes `figs(x[2]) != figs(y[2])` | **Yes**, item 2 |
| 6 | `@@ -259 @@` `diff()` and bases | `unit_only` rewritten: T1/T2 only, both units in `UNIT_US`, both values numeric, same date text, different unit spelling, and `math.isclose(..., rel_tol=1e-9)`. `conflict_at_start` now uses `figs`. | **Yes**, items 4 and 2 |

**Hunks that do not map to a stated change:** none as a whole. The three unstated effects, all in hunk 4:
1. **Every skip line changed wording.** Example: `bad_list.json (not a calibration record)` became `bad_list.json (ValueError: not a calibration record)`. Reasons are cut at 80 characters: `zl.json (ValueError: record stamp '2026-11-01T11:30:00' has no zone, so every age measured from it wo)`. The zoneless reason now stops mid-word. It appears in the page, in the JSON `skipped` list and in the `no readable records in ...` message. FIXES says nothing about the wording.
2. **`str(r[0])` means a non-string `backend_name` is never skipped.** It becomes a backend named `5`, `None`, `True`, `['x']` and so on. A folder with a good record plus `backend_name: 5` is refused (rc 1) unless `--backend` is given (section 3).
3. **`norm()` is now dead code.** It is still defined at line 259 but no longer called.

**One interaction to know about.** Line 189 and line 190 carry the same message. Line 189 is the old check. Line 190 is the new one. Both are needed: the old one refuses `--out = B` for a link `B/link.json`, and the new one refuses `--out = C`, the real folder.

## 2. 16 repros and 27 fixtures, raw and pinned, 7d against 7e

Method as in round 11. Raw: `fx/run_all.py`. Pinned: `fx/run_all_pinned.py` with `QIA_EXE` set to the `--at`-from-stamp shim (`qia-check-pinned.cmd`, which reads `QIA_VENV`). Repros: `runrepros.py`. Compare: `cmp12.py` (`cmp12.out`). The runs are `runall.sh d` and `runall.sh e`. Outputs: `res_d_raw`, `res_d_pin`, `res_e_raw`, `res_e_pin`, `rep_{d,e}_{raw,pin}.json`, `out_fx_*.txt`.

- **Repros: 16 of 16 identical in stdout and exit code, raw and pinned.** R13 exits 1 by design on both.
- **Fixtures: runner verdicts identical on all 54 case-runs** (27 cases, raw and pinned). Totals are the same on both versions: raw **12 HOLDS / 13 HOLE / 2 CANNOT TELL**, pinned **14 / 11 / 2**.
- **Exit code and stderr: identical on all 98 runs.** No HOLDS, HOLE or CANNOT TELL change, by runner or by content. Pages: 84 JSON pages, **flags identical including order on 84 of 84**.
- **Every changed case: one, E01** (`malformed JSON (truncated, trailing comma, list top-level, no stamp)`, run028 in each batch, raw and pinned). Rc is 0 in both. The page still names `bad.json`; only the wording changes:

```
7d  Not used: bad.json (Expecting property name enclosed in double quotes: line 10 column 5 (char 200)).
7e  Not used: bad.json (JSONDecodeError: Expecting property name enclosed in double quotes: line 10 column 5 (char 200)).
```
  The JSON key `skipped` and the `meta` line change the same way. The compare script printed nothing else.
- **My own score:** I did not re-score each case by hand. The flags are identical on every page, so my round-11 score of 24 HOLDS / 0 HOLE / 3 CANNOT TELL (P05, P13, P14) carries over by content.
- **P11 string match: it still flips, the same on both.** The runner (line 203) needs `(0, 'T1', '152.3', '97.4') in ch`, but the cells read `152.3 us` and `97.4 us`. P11 is HOLE on 7d and 7e, raw and pinned. By content nothing changed. FIXES 7e item 6 says the string match is the runner's and was not changed; that matches what I see. I did not rerun 7b this round. Round 9 recorded 7b as HOLDS.

## 3. The four after-mode crashes, the 11 skipped kinds, and the zoneless stamp

Scripts: `t7a.py` (helpers), `t7b.py` (crashes), `t7c.py` (kinds, zoneless). Output: `out_t7b.txt`, `out_t7c.txt`. Each case: `good1.json` (11:00) and `good2.json` (12:20) plus the bad input, run on 7e then 7d. Run window 12:00 to 12:40.

**The four crashes**

| # | input | 7e rc and skip line | good records read? | 7d |
|---|---|---|---|---|
| 1 | a **directory** named `x.json` | **rc 0**, `x.json (ValueError: not a file)` | yes, `Records read: 2` | rc 1, `PermissionError` traceback |
| 2 | a file the OS will not open (`icacls /deny user:(R)`; Python itself raised `PermissionError` on it; permissions restored afterwards, checked) | **rc 0**, `locked.json (PermissionError: [Errno 13] Permission denied: 'C:\\\\Users\\\\Heure\\\\sage_workshop\\\\qia_break\\\\run11)` (cut at 80) | yes, 2 | rc 1, traceback |
| 3 | stamp `9999-12-31T23:59:59-05:00` | **rc 0**, `far.json (ValueError: record stamp unreadable: '9999-12-31T23:59:59-05:00')` | yes, 2 | rc 1, `OverflowError` |
| 3b | stamp `0001-01-01T00:00:00+05:00` | rc 0, `far.json (ValueError: record stamp unreadable: '0001-01-01T00:00:00+05:00')` | yes, 2 | rc 1 |
| 3c | stamp `9999-12-31T23:59:60Z` (leap second) | rc 0, `far.json (OverflowError: date value out of range)` | yes, 2 | rc 1 |
| 3d | control `9999-12-31T23:59:59Z` | rc 0, read, `Records read: 3` | yes | same |
| 4 | `backend_name: 5` beside good records | **rc 1**, `the folder mixes backends (5, ibm_kingston); give --backend NAME; refused`, no report | **no, refused** | rc 1, `TypeError: '<' not supported between instances of 'int' and 'str'` |
| 4a | same, with `--backend ibm_kingston` | rc 0, `bn.json (backend 5, not ibm_kingston)` | yes (the page says `Records read: 3`, counted before the backend filter) | rc 1, `TypeError` |
| 4b | `backend_name` `null`, `true`, `['x']`, `{'a': 1}`, `1.5` | the same as 5: rc 1 `folder mixes backends (None, ibm_kingston)` and so on; rc 0 with `--backend`, skipped as `(backend None, not ibm_kingston)` | | rc 1, `TypeError` in all |
| 4c | `backend_name: 5` **alone** | rc 0, the file is read as backend `5`, `Records read: 1` | | rc 0 |
| 4d | `backend_name: 5` alone, `--backend 5` | rc 0, read | | **rc 2**, `bn.json (backend 5, not 5)` |
| 4e | `backend_name: 5`, before mode | rc 0, report written | | same |
| 3-before | before mode, stamp `9999-12-31T23:59:59-05:00` and `0001-01-01T00:00:00+05:00` | **rc 1, clean message**: `... is not a readable calibration record (Qiskit BackendProperties JSON): record stamp unreadable: '9999-12-31T23:59:59-05:00'` | | rc 1, `OverflowError` traceback |
| 3-before-leap | before mode, stamp `9999-12-31T23:59:60Z` | **rc 1, `OverflowError: date value out of range` traceback** | | same traceback |
| all | one folder with `x.json` dir, the 9999 stamp, `backend_name: 5` and a truncated file, plus the two good records | rc 1, `folder mixes backends (5, ibm_kingston)` | refused | rc 1, `PermissionError` traceback |

**Crash 4 is the one that does not match FIXES.** Item 1 says "a numeric backend_name ... skipped and named with the reason (tested: rc 0, the good record read)". That holds only with `--backend`. A numeric backend name is refused as a second backend, not skipped.

**Further tracebacks I found** (`t9.py`, `t10.py`, `out_t9.txt`, `out_t10.txt`). None is in FIXES as fixed, and none is a regression:
- Leap-second `9999-12-31T23:59:60Z` stamp in **before** mode: `OverflowError` (row above).
- `--start 9999-12-31T23:59:59-05:00` (after) and `--at 9999-12-31T23:59:59-05:00` (before): `OverflowError` traceback, rc 1. The `utc()` helper catches only `ValueError`.
- A figure with `"unit": ["us"]` (list) or a dict: `TypeError: unhashable type`, rc 1, in **before** mode and in **after** mode beside a good record. The file is not skipped. With `--qubits 5` (not read) there is no crash, so it fails at check time, not at load. Unit `5` is fine (`unknown unit 5`, UNKNOWN row).
- A file of 200,000 `[` characters: `RecursionError`, rc 1, in before mode and in after mode beside a good record (not skipped).
- Before mode with a missing file, or a directory as the record: `FileNotFoundError` / `PermissionError` traceback, rc 1 (`sha(rec)` runs before the `try`).

**Retest of the 11 previously skipped kinds** (`t7c.py`, section B; one folder per kind, two good records plus the bad file). All rc 0, `Records read: 2`, both good records used, the bad file named in `skipped` and in the page text. **No regression in rc, in which files are read, or in which file is named.** The wording changed on all 11 (hunk 4):

| kind | 7e skip line | 7d skip line |
|---|---|---|
| truncated JSON | `bad_truncated.json (JSONDecodeError: Unterminated string starting at: line 1 column 2 (char 1))` | `... (Unterminated string starting at: line 1 column 2 (char 1))` |
| empty file | `(JSONDecodeError: Expecting value: line 1 column 1 (char 0))` | `(Expecting value: ...)` |
| top-level list | `(ValueError: not a calibration record)` | `(not a calibration record)` |
| no stamp | `(ValueError: not a calibration record)` | same, no prefix |
| `qubits` not a list | `(ValueError: not a calibration record)` | same, no prefix |
| null stamp | `(ValueError: record stamp unreadable: None)` | no prefix |
| numeric stamp | `(ValueError: record stamp unreadable: 12345)` | no prefix |
| zoneless stamp | `(ValueError: record stamp '2026-11-01T11:30:00' has no zone, so every age measured from it wo)` **cut mid-word** | `(record stamp '2026-11-01T11:30:00' has no zone, so every age measured from it would be a guess; refused)` |
| latin-1 bytes | `(UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 6: invalid continuation byte)` | no prefix |
| UTF-8 BOM | `(JSONDecodeError: Unexpected UTF-8 BOM (decode using utf-8-sig): line 1 column 1 (char 0))` | no prefix |
| bad `.json.gz` | `bad_gz.json.gz (BadGzipFile: Not a gzipped file (b'no'))` | no prefix |

New in this retest: a 5,000-digit integer value is skipped as `bigint.json (ValueError: Exceeds the limit (4300 digits) for integer string conversion: value has 5000 di)`. A file of NUL bytes and an empty file are skipped.

**Zoneless record stamp, exit code, both modes** (7e and 7d identical):

| mode | input | rc | what the page says |
|---|---|---|---|
| before | the one record has a zoneless stamp | **1**, no report | `<path> is not a readable calibration record (Qiskit BackendProperties JSON): record stamp '2026-11-01T11:30:00' has no zone, so every age measured from it would be a guess; refused` |
| after | good record + zoneless record (the zoneless one stamped 11:30, or 12:20 inside the run window) | **0** | `Records read: 1`, `Not used: zl.json (ValueError: record stamp ... has no zone ... wo)`. The header reads `0 flag row(s), 0 UNKNOWN` and the flags section reads `Nothing flagged in the fields this package reads`. |
| after, with `--backend ibm_kingston` | the same | 0 | the same |
| after | the zoneless file is the **only** record | **1**, no report | `no readable records in <folder>: zl.json (ValueError: record stamp ... wo)` |
| after | two zoneless files, nothing else | 1, no report | the same |
| before | zoneless **field** date (T1), stamp fine | 0 | `0 flag row(s), 1 UNKNOWN` |

The zoneless exit code is unchanged: 1 in before mode, 0 in after mode unless it is the only file.

## 4. Conflicts by figures (`t4.py`, `t8.py`; `out_t4.txt`, `out_t8.txt`)

Start record(s) 11:00 with T1 150 us, unless stated. Run window 12:00 to 12:40. `d.json` at 12:20 with T1 60.

**Byte-identical copies**

| case | 7e | 7d |
|---|---|---|
| a.json and b.json byte-identical, d.json T1 60 | `2026-11-01 12:20 q0 T1 150 us -> 60 us` (one row), `conflicts: []` | same |
| three byte-identical copies | one row, `conflicts: []` | same |
| byte-identical start pair, d1 12:10 T1 100, d2 12:20 T1 80 | `12:10 q0 T1 150 us -> 100 us`, `12:20 (from d1.json) q0 T1 100 us -> 80 us` | same |
| byte-identical start pair, three during-run records | `12:10 ...`, `12:20 (from d1.json) 100 -> 80`, `12:30 (from d2.json) 80 -> 70` | same |

**Same figures, different bytes: fixed in 7e, as FIXES item 2 says**

| case | 7e | 7d |
|---|---|---|
| a.json and b.json differ only in `gates` | **one row** `12:20 q0 T1 150 us -> 60 us`; no CONFLICT sentence; `conflicts: []` | two rows, `12:20 (from a.json)` and `12:20 (from b.json)`, plus `CONFLICT: a.json and b.json share the stamp 2026-11-01 11:00 UTC and differ` |
| b.json is a.json re-written with `indent=3, sort_keys` | one row, `conflicts: []` | two rows + CONFLICT sentence |
| same stamp written `Z` and `+00:00`, same figures | one row, `conflicts: []` | two rows + CONFLICT sentence |
| two start records, same figures, differ only in `gates`, with d1 and d2 during the run | `12:10 q0 T1 150 -> 100`, `12:20 (from d1.json) 100 -> 80`; no sentence | `12:10 (from a.json)`, `12:10 (from b.json)` (doubled), plus the `12:20 (from d1.json)` row and the sentence |
| two during-run files at the same stamp 12:10, same figures, differ only in `gates` | one row, `conflicts: []` | sentence `d1.json and d1b.json share the stamp 2026-11-01 12:10 UTC and differ` |

**Same stamp, one figure different: still a conflict, rows as before**

| case | 7e rows (7d identical) |
|---|---|
| `a.json` T1 150, `b.json` T1 100; d1 12:10 T1 100, d2 12:20 T1 80 | `CONFLICT a.json vs b.json q0 T1 150 us -> 100 us` / `2026-11-01 12:10 (from a.json) q0 T1 150 us -> 100 us` / `2026-11-01 12:20 (from d1.json) q0 T1 100 us -> 80 us` |
| Bones's `tests/baseline_conflict` | `CONFLICT a.json vs b.json q0 T1 150 us -> 41 us` / `2026-11-01 12:20 (from b.json) q0 T1 41 us -> 150 us`; flag `b.json T2>2T1 CANNOT_TELL`. Matches FIXES 7b. |
| `a.json` T2 100, `b.json` T2 101 | `CONFLICT a.json vs b.json q0 T2 100 us -> 101 us`; then `12:20 (from a.json) T1 150 -> 60`, `12:20 (from b.json) T1 150 -> 60`, `12:20 (from b.json) q0 T2 101 us -> 100 us` |
| T1 differs by 1e-12 | `CONFLICT a.json vs b.json q0 T1 150 us -> 150 us` (the cells look equal) |
| T1 date differs by 5 minutes only | `CONFLICT a.json vs b.json q0 T1 150 us -> 150 us` and `q0 T2 100 us -> 100 us` (T2 differs because the T2 date was also moved by the helper) |
| T1 unit differs only (150 us against 0.15 ms) | `CONFLICT a.json vs b.json q0 T1 150 us -> 0.15 ms`. **The CONFLICT row carries no unit-only label.** |
| three same-stamp records, a = b, c differs | sentence names only `b.json and c.json`; rows `12:20 (from a.json)`, `(from b.json)` (identical rows), `(from c.json)` |
| two during-run files at the same stamp 12:10, T1 100 vs 90 | `12:10 q0 T1 150 us -> 100 us`, `12:10 (from d1.json) q0 T1 100 us -> 90 us`, plus the sentence |
| differ on qubit 1 only, `--qubits 0` | sentence, no CONFLICT row (qubit not asked) |
| differ on qubit 1 only, `--qubits 1` | `CONFLICT a.json vs b.json q1 T1 80 us -> 70 us` |

**Edges where "conflict by figures" is not the whole story (7e and 7d identical unless stated)**
- **JSON `100` against `100.0`** (same value, different type): 7e still prints the CONFLICT sentence and two rows `12:20 (from a.json)` / `(from b.json)`, and there is **no CONFLICT row** because the row test compares `100 == 100.0` as equal. The sentence says they differ; nothing shows how. A string `'100'` against number `100` prints `CONFLICT a.json vs b.json q0 T1 100 us -> 100 us`.
- **Identical start records still produce doubled flag rows.** Two byte-identical copies, or two figure-identical files, whose T2/T1 is above 2.5 give `a.json T2>2T1 ABOVE` **and** `b.json T2>2T1 ABOVE`. The loop at line 243 checks every record in force. The changes table is deduplicated; the flags table is not. FIXES says "doubled rows"; if it means the changes table only, that matches.

**Two during-run records and the label** (7e, same as 7d)
- Start record stamped 11:00 T1 150, d1 12:10 T1 100, d2 12:20 T1 80: `12:10 q0 T1 150 us -> 100 us` (no label) / `12:20 (from d1.json) q0 T1 100 us -> 80 us`. The label is true on the second row.
- Three during-run records: `12:30 (from d2.json) q0 T1 80 us -> 70 us`. True.
- No record at the start, d1 and d2 only: `12:20 (from d1.json) q0 T1 100 us -> 80 us`. True.
- A first during-run record against a real conflict at the start is labelled `(from a.json)`. That is also true.

## 5. Units (`t3b.py`; `out_t3b.txt`, `out_t3b_summary.txt`)

`a.json` at 11:00, `b.json` at 12:20 (run window 12:00 to 12:40), T1 changed, T2 unchanged, same T1 date. The label is in the `record` cell. The before/after cells carry the unit text and print numbers with `.4g`, so a cell can hide a small difference. A "same value" row can read `100 us` against `0.1 ms` when the stored value is `0.1000000001`.

**Required rows** (7e; 7d in the right column where it differs)

| change | 7e row: (record, field, before, after) | 7d |
|---|---|---|
| **100 us to 0.1 ms** | `('2026-11-01 12:20 (unit only, same value)', 'T1', '100 us', '0.1 ms')` | same |
| **100 us to 100 ns** | `('2026-11-01 12:20', 'T1', '100 us', '100 ns')`, no label; the page also has `T2>2T1 ABOVE` | same |
| 100 us to 100 µs (U+00B5) | `... (unit only, same value)`, `'100 us'`, `'100 µs'` | same |
| 100 us to 100 μs (U+03BC) | `... (unit only, same value)`, `'100 us'`, `'100 μs'` | same |
| 100 us to 100, blank unit | `... (unit only, same value)`, `'100 us'`, `'100'` | same |
| 100 us to 100, unit key missing | `... (unit only, same value)`, `'100 us'`, `'100'` | same |
| **100 furlongs to 100 furlongs** | **no row** (`rows: none`); the page has two `UNKNOWN T1` flags | same |
| **100 furlongs to 100 us** | `('2026-11-01 12:20', 'T1', '100 furlongs', '100 us')`, **no label**; flag `UNKNOWN T1` | `(unit only, same value)` label |
| **100 us to 100 furlongs** | `('2026-11-01 12:20', 'T1', '100 us', '100 furlongs')`, **no label**; flag `UNKNOWN T1` | `(unit only, same value)` label |
| 100 furlongs to 0.1 ms | plain row, no label | labelled |
| 100 furlongs to 90 furlongs | plain row, no label | same |

- All 12 ordered pairs of `us`, `µs`, `μs` and blank carry `(unit only, same value)` on both 7e and 7d. Unit spellings are listed, not suppressed.
- Also correct on 7e: `100 us -> 100000 ns` (`1e+05 ns`), `100 us -> 1e-4 s` (`0.0001 s`), `0.1 ms -> 100 us` and the numeric string `'0.1'` ms are labelled. `100 us -> 100 ms`, `100 us -> 90 us`, `100 us -> 90 ns` are plain changes. `100 us -> 0.1 ms` **with the T1 date moved** is a plain change (the date differs).
- **The CONFLICT row never carries the label.** Same stamp, `100 us` against `0.1 ms`: `('CONFLICT a.json vs b.json', 'T1', '100 us', '0.1 ms')`.

**Floating-point and the 1e-9 boundary.** Rows from 7e (7d never labelled any of these except the exact `100 us -> 0.1 ms` case, so those rows are plain changes there):

| case | label on 7e? |
|---|---|
| `0.1+0.2` ms (stored `0.30000000000000004`) to `300` us | **labelled** `(unit only, same value)` (the cell reads `0.3 ms`) |
| `300` us to `0.1+0.2` ms | **labelled** |
| `0.1+0.2` us to `300` ns | **labelled** |
| `0.1+0.2` us to `0.3` us (same unit) | **plain change, no label** (`0.3 us` against `0.3 us`; the cells look identical and the unit does not differ) |
| `9 ns -> 0.009 us`, `1001 us -> 1.001 ms`, `123 us -> 0.000123 s` | all **labelled** (7d left them plain; this is the float under-labelling that round 11 raised) |
| 100 us to 0.1 ms, exact | labelled |
| 100 us to **0.10000000009** ms (+0.9e-9 relative) | labelled |
| 100 us to **0.1000000001** ms (+1.0e-9) | **labelled** |
| 100 us to **0.10000000011** ms (+1.1e-9) | **plain** |
| 100 us to **0.09999999991** ms (-0.9e-9) | labelled |
| 100 us to **0.0999999999** ms (-1.0e-9) | **plain, no label** |
| 100 us to **0.09999999989** ms (-1.1e-9) | plain |
| 100 us to blank-unit **100.00000009** (+0.9e-9), **99.99999991** (-0.9e-9) | labelled |
| 100 us to blank-unit **100.00000011** (+1.1e-9), **99.99999989** (-1.1e-9) | plain |
| 100 us to blank-unit **100.0000001** (+1.0e-9 exact), **99.9999999** (-1.0e-9 exact) | **both labelled** |
| 0.1 ms to **100.0000001** us, and to **99.9999999** us | **both labelled** |

- **At exactly 1e-9 the result depends on float rounding, not on the stated bound.** `100 us -> 0.1000000001 ms` is labelled, and `100 us -> 0.0999999999 ms` is not. The same-size step in blank-unit form (`99.9999999`) is labelled. `math.isclose` is inclusive and its result at the edge follows the last bit. Away from the edge (0.9e-9 and 1.1e-9) the label is on one side in all four directions.
- The first test run had two rows mis-specified by me (0.099999999991 and 0.099999999989 ms are 0.09e-9 and 0.11e-9 away, not 0.9e-9 and 1.1e-9). The table above uses the corrected values (`fix_m0.9e-9_...`, `fix_m1.1e-9_...` in `out_t3b_summary.txt`). The two mis-specified rows are still in the file under `bnd_-0.9e-9__...` and `bnd_-1.1e-9__...`.
- **FIXES item 4 is met:** `100 furlongs` is a plain change, the label needs both units known, and the 1e-9 bound is in the code. A value that differs by less than 1e-9 relative but is stored differently is called "same value". That is what the bound says.

## 6. `--out` (`t5.py`, `t5b.py`; `out_t5.txt`, `out_t5b.txt`)

**Before mode.** Folder A holds `rec.json`. "Refused" means exit 1 and `--out must not be the folder that holds the record (a report there could later be read as a record)`, and the folder gained nothing. **7e and 7d agree on every row except the last two.**

| `--out` | 7e result |
|---|---|
| exact folder | **refused** |
| exact folder with forward slashes | **refused** |
| trailing backslash `A\` | **refused** |
| trailing slash `A/` | **refused** |
| `A\sub\..`, sub does **not** exist | **refused** |
| `A\sub\..`, sub exists | **refused** |
| `A/sub/..` with forward slashes | **refused** |
| `../` with cwd = `A\sub` (resolves to A) | **refused** |
| `../A/` with cwd = A | **refused** |
| `../` with cwd = A (resolves to the parent) | not refused, exit 0, report in the parent |
| upper-case spelling | **refused** |
| NTFS junction to A | **refused** |
| record read through the junction, `--out` = real folder A | **refused** |
| record read through the junction, `--out` = the junction | **refused** |
| directory symlink to A | **refused** |
| directory symlink to A, plus `/sub` | not refused, exit 0, report in `A/sub/` |
| **subfolder** of A, not existing (`A/reports`) and existing (`A/sub2`) | **allowed**, exit 0, report written there |
| parent of A | allowed, exit 0 |
| **file symlink** `B/link.json` -> `C/real.json`, `--out` = **B** (where the link lives) | **refused** (7d: refused) |
| **same file symlink, `--out` = C** (the real folder is given) | **refused** (**7d: not refused**, exit 0, report written beside `real.json`) |

The last row is the one that changed. FIXES item 6 is met.

**After mode.** Records folder AF holds `a.json` and `b.json`.

| `--out` | 7e | 7d |
|---|---|---|
| exact folder | **refused**, exit 1, `--out must not be the records folder (a report there would be read as a record)` | refused, `--out must be outside the records folder` |
| trailing backslash, trailing slash | **refused**, same message | refused |
| `AF/sub/..` (resolves to AF), `AF/../AF`, upper case | **refused** | refused |
| junction to AF | **refused** | refused |
| **subfolder that does not exist (`AF/rep`)** | **allowed**, exit 0, report in `AF/rep/` | refused |
| **subfolder that exists and is empty (`AF/sub2`)** | **allowed**, exit 0 | refused |
| junction to AF, plus `/sub` | allowed, exit 0, report in `AF/sub/` | refused |
| sibling folder, parent folder | allowed, exit 0 | allowed |

- FIXES item 3 ("a subfolder is allowed, the records folder itself is refused") is met.
- **A report in a subfolder is not read as a record:** with a before-report in `AF/rep/`, `after` on AF read `Records read: 2` and skipped nothing (the glob is top-level).
- **A report at the top level is skipped, not read:** `before_ibm_kingston_....json (ValueError: not a calibration record)`, exit 0.
- **A subfolder whose name ends in `.json`:** `--out AF/rep.json` is accepted (rc 0). On the next `after` run the directory is skipped as `rep.json (ValueError: not a file)`, rc 0. No crash.
- The 7e message for after mode changed text ("must be outside the records folder" became "must not be the records folder ..."). Nothing in README quotes either.

## 7. README (`README.md.7c`) read line by line against 7e

Line numbers are those of `README.md.7c` (`cat -n`). Tests: `t9.py` (before mode), `t10.py` (after mode and wording), `t11.py` (exit codes), `out_t9.txt`, `out_t10.txt`. The README was not edited for 7d or 7e.

### Claims the code does not meet

| lines | README says | what 7e does | evidence |
|---|---|---|---|
| **70** | an `--out` folder that "...sits inside the records folder" exits 1 | **Not true of after mode any more.** Only the records folder itself is refused (hunk 4). A folder inside it is written, rc 0. | section 6: `AF/rep`, `AF/sub2`, junction + `/sub` all rc 0. Before mode never refused a subfolder either. |
| **69-70** | exit 1 when it refuses "a record stamp with no zone" | Before mode: rc 1. **After mode: rc 0**, the file is skipped, unless it is the only readable record (then rc 1). | section 3, zoneless table |
| **69** | exit 1 when it refuses "an unreadable record" | Before mode: truncated JSON is a clean refusal, rc 1. **A missing file or a directory gives a Python traceback, rc 1.** After mode: an unreadable file is skipped, rc 0, unless it is the only one. | `out_t9.txt`: `FileNotFoundError`, `PermissionError` tracebacks |
| **71** | "In after mode, a file in the folder that cannot be read as a record is skipped and named on the page." | **Met for the 11 old kinds, and now for a directory, an unopenable file and a 9999-with-offset stamp.** **Not met for:** (1) a figure whose `unit` is a list or dict, which gives a `TypeError` traceback, rc 1; (2) deeply nested JSON, `RecursionError`, rc 1; (3) a non-string `backend_name`, which is not skipped: the folder is refused (rc 1) unless `--backend` is given, and then the file is skipped as a different backend; (4) a file that is the only one: no page, rc 1, a message. Reasons are cut at 80 characters, so the zoneless reason is cut mid-word. | sections 3 and 7-notes |
| **28** | ZERO is "an error value of 0", TINY is "a nonzero error value below 1e-6" | These rows are produced for `readout_error`, `prob_meas0_prep1` and `prob_meas1_prep0` only. **`init_error` 0, and `init_error` 1e-17, give no row.** README names `init_error` as a field it reads (lines 28, 76). | `out_t9.txt`: `init_error = 0`, `1e-17`: `rows=[]` |
| **29** | UNKNOWN covers "an unknown unit" | Only for T1 and T2. **An error figure (`readout_error`, `init_error`) with unit `furlongs` gives no row.** A T1 with no unit key is read as microseconds without a row. | `out_t9.txt` |
| **29** | "UNKNOWN is never a pass." | The exit code is 0 for a page whose only content is UNKNOWN rows, in both modes. **Before mode says so on the page** (`2 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.`). **After mode does not**: its page has the header `0 flag row(s), 1 UNKNOWN (...)` and the flags table, and no "not a pass" sentence. | `out_t9.txt` (`notapass=True`); `out_t10.txt` (after, `notapass=False`) |
| **39** | two same-stamp files with "different contents" are both checked and "their differences are listed as a conflict" | The test is now by **figures**, not contents: files that differ only in `gates` or whitespace are not a conflict (7e item 2; README wording is "contents"). Where a conflict is declared, the differences are **not always listed**: JSON `100` against `100.0` prints the sentence and no CONFLICT row; a difference on a qubit not asked for is not listed. | section 4 |
| **76-77** | "A clean page means no flag fired in the fields the package reads: T1, T2, readout_error, prob_meas0_prep1, prob_meas1_prep0 and init_error, per qubit, with their dates and units." | The page prints `Nothing flagged in the fields this package reads` (and header `0 flag row(s), 0 UNKNOWN`) when **an error figure is absent entirely**, **has an unknown unit**, or (`init_error`) is 0 or 1e-17. It also prints it in **after mode when a record was skipped**, including a zoneless record stamped inside the run window, a file that could not be read, or the only start record. The only mention is the `Not used:` line. | `out_t9.txt`, `out_t10.txt` (`w4`) |
| **29 against 74-77** | UNKNOWN is never a pass; a clean page is one where no flag fired | A page with `0 flag row(s), N UNKNOWN` is clean by the line 74 definition. Line 29 says it is not a pass. The README does not say which wins. Before mode adds the "not a pass" sentence; after mode does not. | `out_t10.txt` |

### Claims I checked and found met on 7e

| lines | claim | result |
|---|---|---|
| 5 | files are opened read-only and never changed | sha256 and mtime of two records identical before and after an `after` run. The code opens with `'r'` or `'rb'`. |
| 5 | the checker sends nothing anywhere; only `--pull` contacts IBM | No network import in the file. `qiskit_ibm_runtime` is imported only inside `pull()`. **`--pull` itself I did not run** (no IBM account here). |
| 5 | Python 3.9 or later | **Not tested**; only 3.13 is installed here. |
| 13-19 | `qia-check[ibm]` extra, `qia-check` command, `import qia_check` | pyproject has `ibm = ["qiskit-ibm-runtime"]` and `qia-check = "qia_check:main"`. Installed `qia-check.exe` runs, and the runner imports the module. |
| 26-27 | `before ... --at ... --qubits`; without `--at` the check time is used; ages against stamp and run time | yes |
| 28 | flags STALE, FUTURE, T2>2T1, PAIR as described | yes (fixtures, repros) |
| 29 | UNKNOWN for absent, null, NaN, zero, negative T1 or T2; negative error value; unreadable date; zoneless date; conflicting duplicates; qubit with no figures | **all 11 kinds listed on that line are present** with the right reason. An identical duplicate gives no row. |
| 30 | the page opens with the numbers of flag rows and UNKNOWN rows | yes (first meta line, both modes) |
| 30 | a page where nothing was checked says so and exits 2 | yes: `--qubits 99` (before and after), `--backend ibm_nope`, only record after `--end`: rc 2, `NOTHING WAS CHECKED: this report is not a pass (exit 2)` |
| 30 | a record stamp with no zone is refused | yes in before mode (see line 69-70 for after mode) |
| 31 | gates and zz are not read | yes |
| 36-38 | times in UTC with Z or an offset; the latest record at or before the start, those during the run, the changes | a zoneless `--start` is refused, rc 1, with a clear message |
| 39 | a mixed-backend folder is refused without `--backend` | rc 1 |
| 39 | with no record before the start, the during-run records are still checked and the page says so | yes: `NO RECORD in the folder is stamped at or before the run start ...` |
| 48 | `TESTED.md` in the sdist and installed under `share/doc/qia-check/` | yes, built from `venv_full`: the sdist lists `TESTED.md` and `CITATION.cff`; the wheel installs both under `share/doc/qia-check/`. **The README that builds is the file called `README.md`, which is the older one** (no exit-code or clean-page text). |
| 68-69 | exit 0 for a report that checked a qubit; exit 2 when nothing was checked (no qubit asked for, or no record covers the run) | yes (`t11.py`) |
| 70 | exit 1 for a mixed-backend folder, and for `--out` equal to the record's own folder | yes. The file-symlink record with the real folder given is now refused too. |
| 71-72 | `--pull` ignored with a note when a record is given | yes: `note: --pull ibm_x ignored because RECORD.json was given` on stderr, report written, rc 0 |
| 77 | the clean page says nothing about gates, zz, other fields, or results | yes; the page line says gates and zz are not read |

I did not test the links (lines 52-58) or the terms (62-64): they are not behaviour.

## 8. For Bones

1. **7e does what FIXES says for crashes 1 to 3, for conflicts by figures, for units, for the after-mode subfolder and for the file symlink.** It changes no score: 24 / 0 / 3 by content, runner totals 12/13/2 raw and 14/11/2 pinned, flags identical on all 84 pages. The one changed case is the wording of one skip line (E01).
2. **FIXES item 1 is wrong about numeric `backend_name`.** It is refused (rc 1) without `--backend`, not skipped with rc 0. Either change the FIXES sentence or skip a record whose `backend_name` is not a string (drop the `str()` in `str(r[0])` and add a type check).
3. **The skip line lost information.** The 80-character cut ends the zoneless reason mid-word, and every skip line carries an exception type name. If that is not wanted, cut at a longer length or only prefix the type for non-ValueError exceptions.
4. **Tracebacks still reachable:**
   - the `+ 1 s` leap-second line in `when()` (before mode, 9999-12-31T23:59:60Z);
   - `utc()` for `--start`, `--end` and `--at`;
   - a `unit` that is a list or dict (`u not in UNIT_US` and the `set(...)` of entries);
   - `RecursionError` from `json.load`;
   - before mode, `sha(rec)` on a missing file or a directory.
5. **README needs the 7e edit.** Lines 70, 69-70, 71, 76-77 and 29 above. The folder's `README.md` is the stale one: the build ships it.
6. **FIXES: four old entries (3b, 5b, 7b, 7c) still end with `src sha256 c237b0aa...`.**
7. **Smaller:**
   - `figs()` treats `100` and `100.0` as different, so the conflict sentence appears with no row.
   - Identical same-stamp start records still double the flag rows.
   - The CONFLICT row never carries the unit label.
   - At exactly 1e-9 the label follows float rounding.
   - `norm()` is dead code.
   - `Records read: N` counts files before the backend filter.

## Files

`C:/Users/Heure/sage_workshop/qia_break/run112/`:
- Hashes and diff: `hashes/hash_start.txt`, `hashes/hash_end.txt`, `diff_7d_vs_7e.diff`
- Environment: `copy_d/`, `copy_e/`, `copy_full/`, `venv_d/`, `venv_e/`, `venv_full/`, `dist_full/`, `h.py`, `shim.py`, `qia-check-pinned.cmd`, `runall.sh`
- Fixtures and repros: `res_{d,e}_{raw,pin}/`, `out_fx_{d,e}_{raw,pin}.txt`, `rep_{d,e}_{raw,pin}.json`, `cmp12.py`, `cmp12.out`, `runrepros.py`, `repros/`, `fx/`
- Crashes, kinds, zoneless: `t7a.py`, `t7b.py`, `t7c.py`, `out_t7b.txt`, `out_t7c.txt`
- Conflicts: `t4.py`, `t8.py`, `out_t4.txt`, `out_t8.txt`
- Units: `t3b.py`, `sumb.py`, `out_t3b.txt`, `out_t3b_summary.txt`
- `--out`: `t5.py`, `t5b.py`, `out_t5.txt`, `out_t5b.txt`
- README claims: `t9.py`, `t10.py`, `t11.py`, `out_t9.txt`, `out_t10.txt`

