# qia-check 1.0.1 round 7: `src/qia_check.py` 44172347... (DRAFT, Sage, for Bones)

Everything is under `C:/Users/Heure/sage_workshop/qia_break/run107/`. I edited nothing in `drafts/from_bones/`. The `2026-11-04-qia-1.0.1/` folder is untouched (all mtimes 22:12, hash unchanged after my runs). I ran from copies in a fresh venv (`venv107`, Python 3.13.13, Windows) with `pip install ./draft_copy`. `draft_copy/` holds LICENSE, README and pyproject copied from his folder, plus a copy of `src/qia_check.py`. The installed file (`venv107/Lib/site-packages/qia_check.py`) hashes to `44172347...`. I did not run in place.

**Short answer.**
- **Scores do not change.** HOLDS 24, HOLE 0, CANNOT TELL 3 (P05, P13, P14). All 84 JSON pages have the same flags as round 6, row order included. All 16 repros give the same stdout and exit code, raw and pinned.
- **D04 is fixed.** The page now compares the two same-stamp records on every field and every requested qubit.
- **Nothing-checked pages are fixed.** They say so in the header and in the flags section, in both modes, and exit 2.
- **The diff is not only your three items.** It also changes the exit code for an after page with no record, the stderr text, and the baseline for the during-run comparison (section 1).
- **DIG: not found.** The files are not on this machine (section 7).

## 1. Hash and diff

- `src/qia_check.py` sha256 = `44172347d9d786d81a94a73a457299a1ad582a12a0860ba0fa7ff058b9b528dc`. Confirmed on his file, on my copy and on the installed file.
- c6da3f6b = my round-6 copy `run106/draft_copy/src/qia_check.py`, sha256 `c6da3f6b8d87a1eba38bbf226e789bae577d29b7fbcbf40115ff08958316010f`. Confirmed.
- The diff is saved as `run107/c6da_vs_4417.diff` (CRLF stripped). It has **6 hunks**:

| # | hunk (new line numbers) | what changed | class |
|---|---|---|---|
| 1 | `145`, `write()` | pops `_empty_flags_before` from `data`. | before-mode flags text |
| 2 | `147`, `write()` | when `_empty_flags_before` is set, adds a `Flags (0)` section with that text. | before-mode flags text |
| 3 | `195`, `before` data | `_empty_flags_before = None if qs else 'Nothing was checked: no qubit to read.'` | before-mode flags text |
| 4 | `237-238`, `after` meta | `nchk = (len(in_force[:1]) + len(during)) if qs else 0`. When `nchk` is 0 the lead is `NO QUBIT WAS CHECKED: none of the asked qubits is in these records. This page is not a pass.` if any record is in force or during the run. Otherwise it is the old `NO RECORD WAS CHECKED ...`. | `--qubits 99` / no-qubits handling |
| 5 | `240-248`, `after` flags text and changes | the empty-flags text is `Nothing was checked: no qubit to read.` if records exist (otherwise `... there is no record to read.`). New loop compares adjacent same-stamp records at the start on every requested qubit and every field in `FIELDS` (T1, T2, readout_error, prob_meas1_prep0, prob_meas0_prep1, init_error). The rows are `CONFLICT a.json vs b.json`. | CONFLICT comparison |
| 6 | `256`, exit gate | `if not qs or (after and no backend) or (after and no record at start and none during)` then print `NOTHING WAS CHECKED: this report is not a pass (exit 2)` and exit 2. | no-record / no-qubit handling |

**Is the diff only the CONFLICT comparison, the before-mode flags text, and the `--qubits 99` / no-qubits handling? Almost, but not only.** Four things go beyond your list:
1. **Exit code, after mode, no record in force and none during the run (hunk 6).** Round 6 exited 0; round 7 exits 2.
   - Test: `after n2in/z0 --start ... --end ...`, run on `venv106` and `venv107`: exit 0, then exit 2.
   - It follows from "a page where nothing was checked is not a pass". FIXES says only "a record read with no qubit checked ... exits 2", so this is an unstated change.
   - No fixture or repro hits it (the 98 runs show no other exit-code change).
2. **stderr text (hunk 6).** `NO QUBITS CHECKED: this report is not a pass (exit 2)` is now `NOTHING WAS CHECKED: ...`, on every exit-2 run. In the 27 fixtures that is E02 (2 runs, raw and pinned). The runner's "observed" text for E02 changes with it.
3. **Baseline for the during-run comparison (hunk 5).** `prev` was `in_force[0]` and is now `in_force[-1]`, the alphabetically last of the same-stamp records.
   - It only matters when same-stamp records disagree and a record is stamped during the run.
   - Test `t_pair_plus_during`: a (T1 150) and b (T1 60) at 11:00, c (T1 60) at 12:20. The during-run table is empty, because c is compared to b. The a-against-b difference is listed in the CONFLICT rows.
   - It is a choice, not an error, but it is a choice.
4. **New meta line and header string (hunks 4 and 5).** The CONFLICT rows trigger the existing line `Figures on your qubits changed during the run; see the table.` The page also has a new header string, `NO QUBIT WAS CHECKED: none of the asked qubits ...`. It reads oddly when no `--qubits` was asked and the record has `"qubits": []`.

No threshold, check, sort key, JSON key or other exit code changed.

## 2. 16 repros and 27 fixtures, raw and pinned, against round 6

Same method as round 6. Raw uses the installed CLI. Pinned uses the shim that adds `--at` = the own stamp of each record. Scripts and outputs: `run107/cmp7.py`, `results_raw/`, `results_pinned/`, `rep_r7_raw.json`, `rep_r7_pin.json`. The runner commands were `fx/run_all.py` and `fx/run_all_pinned.py`, with `QIA_EXE` set to the pinned `.cmd` for the second.

**Scores: no change.** HOLDS 24, HOLE 0, CANNOT TELL 3 (P05, P13, P14).
- No runner verdict field changed on any of the 54 case results. Runner totals are raw 13/12/2 and pinned 15/10/2, as in round 6. The runner strings are tuned to 1.0.0, so those totals are not my scoring.
- My scoring is by flag content. **84 of 84 JSON pages** have flags identical to round 6, row order included. Page-level JSON keys are identical.
- Exit codes and stderr: identical on 98 runs, except E02 (below).
- 16 repros: stdout and exit code identical on 16 of 16, raw and pinned. R13 is still exit 1, by design.

**Every case whose output changed (no flag, no score):**

| case | run | what changed |
|---|---|---|
| E02 | `before data/E02/empty.json` and `... --qubits 0,1` (run029, run030), raw and pinned | stderr is now `NOTHING WAS CHECKED: ...` (was `NO QUBITS CHECKED: ...`). The flags section was `Nothing flagged in the fields this package reads (gates and zz are not read).` and is now `Nothing was checked: no qubit to read.` Exit 2 as before. |
| E02 | runner "observed" string, raw and pinned | the string embeds the stderr text, so it changed. Verdict unchanged. |
| D04 | `after data/D04/records` (run048), raw and pinned | JSON `changes` was empty and now has 1 row: `CONFLICT a.json vs b.json`, q0 T1, 152.3 against 41. Meta has one extra line: `Figures on your qubits changed during the run; see the table.` HTML has the changes table instead of `No figure changed between records in the run window.` The 3 flag rows are the same. |

That is 2 cases and 6 pages, plus 2 runner strings. The 78 other pages are identical. The html text and row sets match too, after normalising times and ages. HOLDS/HOLE/CANNOT TELL: **no change**. I score D04 HOLDS (both checked, CONFLICT reported and compared), as in round 6.

## 3. D04 and the CONFLICT comparison

`after fx/data/D04/records` (`a.json` and `b.json`, both stamped 2026-11-01 12:00 UTC, window 12:00 to 12:40). Output: `results_raw/reports/run048/`.

- **CONFLICT line (meta):** `CONFLICT: a.json and b.json share the stamp 2026-11-01 12:00 UTC and differ. Both are checked below.`
- **Changes table row:** `CONFLICT a.json vs b.json`, qubit 0, T1, before 152.3, after 41, date_before 2026-11-01 09:00:00+00:00, date_after 2026-10-30 10:00:00+00:00. JSON `conflicts` holds the one same-stamp sentence about a.json and b.json.
- The page no longer says "No figure changed".

**Does the code compare on every field, not just T1 on q0? Yes.** The new loop runs over every requested qubit and every field in `FIELDS`, and compares value and date. Tests (`run107/item3_7.py`, output in `i3_out.txt`). The records have qubits 0 and 1, same stamp:

| test | what differs | result |
|---|---|---|
| T2 only | q0 T2 120 against 77 | 1 row: `CONFLICT a.json vs b.json`, q0, T2, 120, 77. Exit 0. |
| other qubit only | q1 T1 150 against 99 | 1 row: q1, T1, 150, 99 |
| other qubit, readout | q1 readout_error 0.012 against 0.5 | 1 row: q1, readout_error |
| date only | q1 figure dates, same values | 5 rows, values equal, `date_before` and `date_after` differ |
| field absent on one side | q0 T2 missing in b | 1 row: q0 T2 120 against blank. Also 1 UNKNOWN flag. |
| three same-stamp records | T1 150 / 1 / 2 | 2 rows (a vs b, b vs c). The CONFLICT meta lists both pairs. |
| identical content | byte-identical files | no conflict, no rows |
| `--qubits 1`, q1 differs | q1 T1 | 1 row |

**Limits to know:**
- With `--qubits 0` and a difference only on q1, no row is listed (the comparison covers requested qubits only). The CONFLICT meta line is still there and the changes text reads `No figure changed between records in the run window.`
- A pair that differs only in `gates`, or only in whitespace (so the file hash differs), gives a CONFLICT meta line, no rows, and the same `No figure changed ...` text. That is true for the fields read, but a reader may take it as "the records agree". I would add "(in the fields read)".
- The rows sit under the heading `Figures that changed during the run (each record against the one before it)`. A CONFLICT row is a difference at the start, not during the run. Cosmetic.
- Same-stamp records are compared adjacent pair to adjacent pair (a to b, b to c), not a to c.

## 4. Pages with nothing checked

Script `run107/item4_7.py`, outputs in `run107/i4_out.txt` and `run107/i3/`. "Header" is the first line under the title in the HTML, and it matches JSON meta[0].

### Before mode, nothing checked (`before h/noqubits.json`, record with no qubits; exit 2)
- **Header:** `NO QUBIT WAS CHECKED: this page is not a pass.`
- **Flags section:** heading `Flags (0)`, text `Nothing was checked: no qubit to read.`
- A line further down still reads `NO QUBITS CHECKED: the record has no qubits, or none of the ones asked for. Nothing here is a pass.`
- stderr: `NOTHING WAS CHECKED: this report is not a pass (exit 2)`.
- `before h/clean.json --qubits 99` gives the same header, flags text and exit 2, plus `Not in this record, so not checked: qubits 99.`
- Control, `--qubits 0` on a clean record: header `0 flag row(s), 0 UNKNOWN (figures, qubits or entries that could not be read: absent, unusable, zoneless or conflicting).` Flags `Nothing flagged in the fields this package reads (gates and zz are not read).` Exit 0.

### After mode (`n2in/z2`: one record at 11:00 in force, one at 12:20 during the run; window 12:00 to 12:40)

| run | header | exit |
|---|---|---|
| `--qubits 99` | `NO QUBIT WAS CHECKED: none of the asked qubits is in these records. This page is not a pass.` | **2** |
| no qubits (folder whose only record has an empty qubit list) | `NO QUBIT WAS CHECKED: none of the asked qubits is in these records. This page is not a pass.` | **2** |
| valid qubit (`--qubits 0`) | `0 flag row(s), 0 UNKNOWN (figures, qubits or entries that could not be read: absent, unusable, zoneless or conflicting).` | **0** |

- In both nothing-checked after runs the flags section reads `Nothing was checked: no qubit to read.`, and stderr is `NOTHING WAS CHECKED: this report is not a pass (exit 2)`.
- Valid qubit: the flags section reads `Nothing flagged in the fields this package reads (gates and zz are not read).`
- Controls:
  - No `--qubits`: `6 flag row(s), 0 UNKNOWN (...)`, 6 rows, exit 0.
  - `--qubits 0,99`: header `0 flag row(s), ...`, meta `Not in these records, so not checked: qubits 99.`, exit 0.
  - No record at start or during (`n2in/z0`): `NO RECORD WAS CHECKED: no record of this backend is stamped at or before the start or during the run. This page is not a pass.`, flags `Nothing was checked: there is no record to read.`, **exit 2** (was 0).
  - Only a record during the run (`n2in/z1`): `3 flag row(s), ...`, exit 0.
- **Wording:**
  - The `--qubits 99` and empty-record after pages still show the changes section as `No figure changed between records in the run window.` (or `Nothing to compare: fewer than two records ...` for 1 record). Nothing was compared on those pages. The sentence is a small overreach on a "not a pass" page.
  - The empty-record page says "none of the asked qubits" when no qubit was asked.

## 5. The 8 real_kingston_records

Copied read-only to `run107/real/`. Each ran as `before <file>.json.gz --at <own stamp>`, as in round 6 (`run107/real4.py`, output `real_out.txt`). All 8 exit 0.

| file (ibm_kingston__...) | header N, M | JSON rows | N + M | UNKNOWN rows | meta "figure(s) could not be read" | HTML rows |
|---|---|---|---|---|---|---|
| 20261001T002246 | 38, 2 | 40 | 40 | 2 | 2 | 40 |
| 20261001T014526 | 38, 2 | 40 | 40 | 2 | 2 | 40 |
| 20261001T035924 | 38, 2 | 40 | 40 | 2 | 2 | 40 |
| 20261001T062638 | 38, 2 | 40 | 40 | 2 | 2 | 40 |
| 20261001T083606 | 33, 2 | 35 | 35 | 2 | 2 | 35 |
| 20261001T103611 | 33, 2 | 35 | 35 | 2 | 2 | 35 |
| 20261001T115547 | 33, 2 | 35 | 35 | 2 | 2 | 35 |
| 20261001T144640 | 33, 2 | 35 | 35 | 2 | 2 | 35 |

**Yes, they reconcile on all 8.** Header N is the non-UNKNOWN count and M the UNKNOWN count. N + M equals the JSON rows and the HTML rows, and M equals the meta count. The flag lists are identical to round 6 (order included), the other meta lines are unchanged, and the UNKNOWN rows are the last 2 rows of each page. The 2 UNKNOWN rows are qubit 146, T1 and T2, both `absent from the record`. Check mix, files 1 to 4: STALE 23, ZERO 8, PAIR 7, UNKNOWN 2. Files 5 to 8: STALE 24, PAIR 7, ZERO 2, UNKNOWN 2.

## 6. For Bones

1. **Rule on `44172347`.** Scores, flags, flag order and the 16 repros are unchanged from round 6. D04, the before-mode flags text and the nothing-checked pages all do what FIXES "Round 6b" says.
2. **Unstated changes to log in FIXES:**
   - an after page with no record at start or during now exits 2 (was 0);
   - the stderr text is now `NOTHING WAS CHECKED`;
   - the during-run baseline is the last same-stamp record, not the first.
3. **Small wording items, your call:**
   - `No figure changed between records in the run window.` appears on nothing-checked and gates-only-conflict pages. "(in the fields read)" would make it true.
   - `none of the asked qubits` appears when none were asked.
   - CONFLICT rows sit under a "during the run" heading.
4. Still open from earlier rounds: the TINY threshold (a Wayfinder call), the 572-record set (N4, not in my workshop), and README and TESTED.md (still the 22:12 text, not updated for 1.0.1).

## 7. DIG: measure_2 rows and inclusion/exclusion rules (read-only). NOT FOUND, source not on this machine

I could not quote the measure_2 rows, because **THIRD_RUNG_20260928.md is not on this machine.**
- This host is `C:\Users\Heure` (Windows). Searched with `find`:
  - all of `C:` (excluding `C:\Windows` and `node_modules`) for `*THIRD_RUNG*`, `bones-forge`, `parallax`, `Sink`, `Sink ` and `*look_floor*`: **0 hits**;
  - `/c/Users`, `/d` for `THIRD_RUNG*`, `FLOOR_CALL*`, `CLOCK81*`, `darkwave_disco`: **0 hits**.
- `~/Desktop/Sink /` does not exist. `C:\Users\Heure\Desktop` does not exist. `C:\Users\Heure\OneDrive\Desktop` exists (listing is June-era GridSong and honored_ask files) and has no `Sink`. `C:\Users\Bones` lists as empty to me.
- `~/bones-forge/` and `~/bones-forge/parallax/` do not exist. My earlier dig files cite `/Users/heuremen/bones-forge/...`, a path that does not exist here either.

So I cannot give §395, §399, §401, §442-443, the outcomes, the ruler or the dark-arm comparison for pittsburgh 1031-33, fez 1081-83 or aachen 1091-92. I have not filled them in from memory or from earlier notes.

**Inclusion/exclusion rule text dated 5-7 Oct: not found, in anything I can read.**
- **Memory folder** `C:\Users\Heure\.claude\projects\C--Users-Heure\memory\` (the only memory folder here; `C--Users-Heure-sage-workshop` and `C--WINDOWS-system32` have none). Newest file `MEMORY.md`, mtime 2026-06-11 10:12:17, then `project_crazy_hat_1177.md` 2026-06-11 10:12:09. **Nothing is newer than 11 June.** A search for `measure_2`, `corner`, `exclu*`, `inclu*` hits only `project_ratcliff_closed.md` (2026-04-28 04:31), line 16, "corner-qubit tax", which is unrelated.
- **Not searched, because not here:** `~/Desktop/Sink /`, `~/bones-forge/parallax/` and the 7 Oct session notes.

**What I do have, second-hand, and have not verified.** These are my own earlier dig reports in `C:\Users\Heure\sage_workshop\digs\`:
- `2026-11-04T04-13-03_read-only-no-edits-in-bones-forge-arxiv-one-readout-and-the-.md` (mtime 2026-11-03 23:14:11 -0500). It says the three exclusions were fixed after the 7 Oct data, that the rule that exists was written on 22 Oct, and that no earlier file, plan or commit states them.
- `2026-11-04T04-18-21_read-only-no-edits-in-bones-forge-parallax-and-any-7-oct-pla.md` (mtime 2026-11-03 23:25:08 -0500). It says the only 7 Oct text is the calls and scripts under `parallax/darkwave_disco/calls/` (`FLOOR_CALL_20261007.txt`, `FLOOR2_CALL_20261007.txt`, `CLOCK81_CALL_20261007.txt`, `CLOCK81B_CALL_20261007.txt`). They say measure_2 was to be read on ratio-to-stated-length ("measure and measure_2 within 1 % of the honest DARK arm"), with no inclusion rule.
- The earlier tool-result file `C:\Users\Heure\.claude\projects\C--Users-Heure-sage-workshop\995c36ad-63e8-4fb2-a4a8-792749ae47a7\tool-results\bt129vsx5.txt` (mtime 2026-11-03 22:34) cites the ledger as `parallax/THIRD_RUNG_20260928.md (last modified 7 Oct 14:10)`. It has no measure_2 rows.

These are my earlier reports, not primary sources. To quote the rows I need the file on this machine, or a path I can read. Until then the answer is **found: no / not readable**.

## Files
`C:/Users/Heure/sage_workshop/qia_break/run107/`: `c6da_vs_4417.diff`, `cmp7.py`, `item3_7.py`, `i3_out.txt`, `item4_7.py`, `i4_out.txt`, `real4.py`, `real_out.txt`, `results_raw/`, `results_pinned/`, `rep_r7_raw.json`, `rep_r7_pin.json`, `i3/`, `real/`, `draft_copy/`, `venv107/`.
