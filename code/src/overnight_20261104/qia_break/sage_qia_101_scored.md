# qia-check 1.0.1 DRAFT scored against Sage's 27 fixtures (DRAFT, Sage, for Bones)

**qia_check.py as run: sha256 `fbb9a30c2e4e7aeadeb83e8124a0a2759ae28ffbe2d91c3b3cbde66a9910ad78`**
Checked three times: the file in `drafts/from_bones/2026-11-04-qia-1.0.1/src/`, my copy, and the copy pip installed into the test venv (`venv101/Lib/site-packages/qia_check.py`). All three have the same hash, and it starts `fbb9a30c`. Version string in the package: 1.0.1. Python 3.13.13, Windows.

Nothing in `drafts/from_bones/` was edited. I copied the folder into the workshop (`qia_break/run101/draft_copy`) and installed from that copy, so pip's build files did not land in Bones' folder. (A `src/__pycache__` was already in his folder before I started; I did not make it and did not touch it.)

Everything below is under `C:\Users\Heure\sage_workshop\qia_break\run101\`:
- `venv101\` : fresh venv, `pip install ./draft_copy`
- `fx\` : copy of my runner (`run_all.py`) and `make_fixtures.py`; fixtures regenerated into `fx\data\`
- `results_raw\` and `results_pinned\` : runner results.json/results.md plus `reports\runNNN\` HTML and JSON for every call
- `fx\run_all_pinned.py`, `shim.py`, `qia-check-pinned.cmd` : the pinning mechanism
- `extra\` : my extra hand runs (X1 to X6 below)
- `detail.md`, `gen.py`, `show.py` : generators for section 4

## 1. The two runs and every tweak

Raw: `python run_all.py --venv ..\venv101 --results ..\results_raw`. Pinned: `QIA_EXE=...\qia-check-pinned.cmd python run_all_pinned.py --venv ..\venv101 --results ..\results_pinned`.

Tweaks, complete list:
1. **Raw run: none.** The runner found `Scripts\qia-check.exe` and `Lib\site-packages` in the new venv (Windows layout; its `bin/` fallback and `lib/python*/` paths were not needed). It ran unmodified, from a copy in `fx\`, so the original `qia_break\fixtures\` and its old results are untouched.
2. **Pinned run, runner copy `run_all_pinned.py`, three edits:**
   - added a global `VENV_EXE` set to the venv's exe (`global EXE, RES, VENV_EXE`, `VENV_EXE = EXE`);
   - P14's site-packages path now starts from `VENV_EXE` instead of `EXE`. This is the only path fix: with `EXE` pointing at the shim, P14 looked in the wrong folder and crashed on the first try (FileNotFoundError);
   - after the version string is read, `EXE = os.environ['QIA_EXE']` so the cases go through the shim. One dead no-op line (`EXE = os.environ.get('QIA_EXE', EXE) if False else EXE`) is left from my first edit; it does nothing.
3. **The pinning shim** (`shim.py`, called by `qia-check-pinned.cmd`): for `before` only, reads the record's own `last_update_date`, converts to UTC, appends `--at <that stamp>`. `after` calls pass through (already pinned by `--start`/`--end`). It does not touch the checker.
   - Shim limit: it cannot parse a stamp with seconds = 60, so for **E07 leap_stamp** it silently ran unpinned. I re-ran that fixture by hand with `--at 2017-01-01T00:00:00Z` (X1). Every other pinned cell shows "0.0 h before the run time".
4. **No runner verdict was trusted.** Its HOLDS/HOLE strings are tuned to 1.0.0 (E01, E02, E03, E05, E06, D02, D04 and P05 are hard-coded `HOLE` or key on 1.0.0 behavior). I scored every case by hand from the outputs. Runner totals for reference: raw 13 HOLDS / 12 HOLE / 2 CANNOT TELL; pinned 15 / 10 / 2.
5. Runner D05 compares the D02 folder, which now refuses to run, so it compares nothing (0 flags vs 0 flags). I did D05 by hand with `--backend` (X3).

Extra hand runs (under `extra\`): X1 E07 leap_stamp with `--at`; X2 P03 `before --at 2026-11-04T12:00:00Z` (stamp + 72 h); X3 D02 folder with `--backend ibm_kingston` and `--backend ibm_fez`; X4 mixed folder where nothing precedes `--start`; X5 naive-stamp repro; X6 a single during-run record with no earlier record.

## 2. Scores, all 27

Scoring rule: is the output true to the fixture. A true refusal or UNKNOWN is HOLDS. A wrong number, a false clean or a silent drop is HOLE. CANNOT TELL: this package cannot exercise the case.
"Raw" = run time is the moment of the run (2026-11-04 03:15 UTC), so every 1 Nov figure is genuinely older than 24 h; those STALE rows are true but swamp the boundary cases. For age cases the pinned run is the one that exercises the case. "Final" is my score.

| id | case | raw | pinned | **final** | runner said (raw/pinned) | why |
|---|---|---|---|---|---|---|
| P01 | init_error 84 d before stamp | true (every field STALE vs now, init_error included) | STALE init_error only | **HOLDS** | HOLDS/HOLDS | init_error is read and aged |
| P02 | prob_meas0_prep1 97 h older | true | STALE prob_meas0_prep1 only | **HOLDS** | HOLDS/HOLDS | readout family aged |
| P03 | stamped 72 h before run | STALE vs this check, true | none (run time = stamp, true); X2 `--at` stamp+72h: 10 STALE rows, T1 "73.0 h before the run time" | **HOLDS** | HOLDS/HOLDS | after mode with start = stamp+72h also STALE 73 h |
| P04 | absent/null/NaN/date-null/0 | UNKNOWN each, plus true STALE | UNKNOWN T1 (q0-q4), T2 (q5, q6); control q7 ABOVE 2.626 | **HOLDS** | HOLDS/HOLDS | no silent qubit; reasons stated |
| P05 | zz = 0 with calibrated CZ | no zz row | no flags | **CANNOT TELL** | HOLE/HOLE | declared out of scope, see section 4 |
| P06 | 24h00m00s / 23h59m59s / 24h00m01s | all STALE vs now (true) | F / F / T | **HOLDS** | HOLE/HOLDS | exact 24 h not stale, 24 h + 1 s stale, as documented |
| P07 | EDT offset, Z, +00:00, naive, "EDT" | naive: UNKNOWN | a,b,c identical; d,e,f UNKNOWN | **HOLDS** | HOLE/HOLE | refusal is honest |
| P08 | 1e-17, -0.0, "0", 1/1024, 0 | ZERO on -0.0, "0", 0 | same | **HOLE** (minor, judgment call) | HOLDS/HOLDS | 1e-17 passes silently, H3 |
| P09 | T2/T1 edges 2.0/2.5 | OK/CT/CT/ABOVE/CT/CT | same | **HOLDS** | HOLDS/HOLDS | matches expected, incl. decimal-exact 2.5 |
| P10 | PAIR 24 h boundary | F/T/F | F/T/F | **HOLDS** | HOLDS/HOLDS | strict > 24 h |
| P11 | window spanning a restamp | at start 11:00, during 12:20, T1 152.3 -> 97.4 | same | **HOLDS** | HOLDS/HOLDS | |
| P12 | stamp moved, values frozen | all STALE vs now (true) | F/F/T by stamp age; after: 1 record during, 0 changes | **HOLDS** | HOLE/HOLDS | page says "Records stamped during the run: 1." and makes no change claim |
| P13 | shot grid on rounded decimals | no shot logic in package | same | **CANNOT TELL** | CT/CT | not in this package |
| P14 | YO vs code | code side recorded, no YO shipped | same | **CANNOT TELL** | CT/CT | YO not in the package |
| E01 | malformed JSON | exit 1, clean, no report; after names bad.json | same | **HOLDS** | HOLE/HOLE | |
| E02 | empty qubits / empty qubit | exit 2 NO QUBITS CHECKED; q0 UNKNOWN (all) | same | **HOLDS** | HOLE/HOLE | |
| E03 | conflicting duplicates | UNKNOWN T1, same in either order | same | **HOLDS** | HOLE/HOLE | |
| E04 | negative T1 | UNKNOWN T1; q1 PAIR 30.0 h and STALE kept | same | **HOLDS** | HOLDS/HOLDS | |
| E05 | unit confusion s/ms/us | q0 none (0.79), q1 ABOVE 2.663, q2 ABOVE 2.663 | same | **HOLDS** | HOLE/HOLE | all three true |
| E06 | string numbers | no traceback; ZERO on "0.0" and "0"; ABOVE 2.667 | same | **HOLDS** | HOLE/HOLE | |
| E07 | leap second / DST | aware DST PAIR 24.5 h; naive stamp read as UTC | STALE 24.5 h + PAIR 24.5 h; naive stamp read as UTC | **HOLE** (narrow: naive stamp) | HOLE/HOLE | H2 |
| E08 | readout family 84 d old | true | STALE on three readout fields | **HOLDS** | HOLDS/HOLDS | |
| D01 | null/negative T1 hides PAIR | PAIR on all three | PAIR on all three | **HOLDS** | HOLDS/HOLDS | |
| D02 | two backends in one folder | exit 1, refused | same | **HOLDS** | HOLE/HOLE | true refusal; see H1 |
| D03 | mid-run record unchecked | b_1220 flags STALE T1, ZERO, PAIR | same | **HOLDS** | HOLDS/HOLDS | |
| D04 | same stamp, different files | CONFLICT line; b.json flagged | same | **HOLDS** | HOLE/HOLE | |
| D05 | after JSON has flags | runner vacuous; by hand (X3) JSON 4 flags = HTML 4 rows | n/a | **HOLDS** | HOLDS/HOLDS (vacuous) | |

Totals (mine): HOLDS 22 = P01 P02 P03 P04 P06 P07 P09 P10 P11 P12 E01 E02 E03 E04 E05 E06 E08 D01 D02 D03 D04 D05. HOLE 2 = P08, E07. CANNOT TELL 3 = P05, P13, P14.

## 2b. Holes (each is a candidate VERDICT, with repro)

**H1: records stamped during the run are neither checked nor named when no record precedes `--start`; a mixed-backend folder is not refused in that branch either.** Not tied to one of the 27 fixtures (D02 and D03 both have a record before start); found while testing item 3.
Repro: `qia-check after extra\h1 --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z --out extra\x6`, where `extra\h1\` holds only `b_1220.json` (ibm_kingston, stamp 12:20, q1 readout_error 0.0, q1 T1 measured 60 h before the stamp). Result: exit 0, JSON `flags: []`, no `records_during`. The page says only: "No record in the folder is stamped at or before the run start, so the record in force at the start is not here. Save the record right before you submit." It does not say a record stamped inside the run was found and not checked, so "no flags" can be read as a clean window. Second repro: `extra\mix\` (an ibm_fez record and an ibm_kingston record, both stamped inside the window, `--start 2026-11-01T10:00:00Z`): exit 0, no refusal for the mix, same one-line note. Cause in the source: the whole `else:` branch holding the backend refusal, the during-run checks and the changes table runs only `if under`.

**H2: a zoneless record stamp is read as UTC and printed as fact (E07 dst_naive_walls).** R06 refuses zoneless field dates, but `load()` does `S, _ = when(d['last_update_date'])` and throws away the naive flag.
Repro: `extra\naive_stamp.json` = P07 b_utc_Z with `last_update_date` "2026-11-01T12:00:00" and T1/T2 dated 2026-10-31T13:00:00Z; `qia-check before extra\naive_stamp.json --at 2026-11-01T16:00:00Z`. Page: "record stamped 2026-11-01 12:00 UTC, 4.0 h before the run time ..." and flag "measured 2026-10-31 13:00 UTC: 23.0 h before the stamp, 27.0 h before the run time". If the stamp is a New York wall clock (EDT = 16:00Z) the true stamp age is 27.0 h, not 23.0 h. No UNKNOWN row, no note. On E07 dst_naive_walls itself this shows as "record stamped 2026-11-01 01:15 UTC, 74.0 h before this check" (on fall-back night that wall time is 05:15 or 06:15 UTC). Honest behavior would be UNKNOWN for the stamp-derived ages, or a refusal, to match R06.

**H3 (minor, spec call): P08 value 1e-17 passes with no row.** The docstring ZERO line says "a value such as 1e-17 cannot come from any shot count", but no check implements it, and the ZERO row text is only "published value 0" (the 0.29 % bound is in the docstring, not on the page). Either implement a flag or reword the docstring. I score HOLE because my fixture's stated expectation is that 1e-17 is flagged; Wayfinder may rule otherwise.

**Not scored, for your eye (no fixture says what is right):** a measurement date later than the record stamp (negative age) is accepted without a word. It shows in E07 leap_stamp (readout dated 2026-11-01, stamp 2017, and X1); that is my fixture builder's artifact, but a real record with a date after its stamp would pass clean.

## 3. R05, R06, R13 on the report pages

**R05 (gates and zz): CONFIRMED.** Every page that is written carries it twice (checked on before, after, before-with-UNKNOWN, after-with-nothing-in-force and NO-QUBITS pages), and the JSON `meta` has it too:
- meta paragraph: `<p class="note">Gates and zz are not read by this package.</p>` (`results_raw/reports/run008/before_ibm_kingston_...html`, `run028/after_...html`, `extra/x4/after_...html`)
- footer: "These checks read IBM&rsquo;s published figures only and make no claim about your results. Gates and zz are not read."
Pages that are not written (exit-1 refusals: bad JSON, mixed backends) have no such note. For P05 the Flags section itself still says "Flags (0)" and "Nothing flagged."; the note and footer are the only places the scope is stated.

**R06 (naive time): CONFIRMED per row. NOT as a page-level note. NOT for the stamp.** On the page (`run011/before_...html`, P07 d_naive_utc_wall) the table rows read:
- `date 2026-10-31T14:00:00 has no zone, so its age cannot be known; not read` (twice, T1 and T2), outcome UNKNOWN
- meta: "2 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass."
No sentence on the page says zoneless times are refused as a rule; that is stated only in the docstring (UNKNOWN bullet: "a date with no zone") and in the `--at`/`--start` message ("add Z or an offset, so the time is not read in the wrong zone"). The record stamp is the exception (H2).

**R13 (mixed backends): NOT on a report page.** The refusal is stderr plus exit 1, and no report is written:
```
$ qia-check after data\D02\records --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z --qubits 0,1
stderr: the folder mixes backends (ibm_fez, ibm_kingston); give --backend NAME; refused      (exit 1)
```
What a page does say once `--backend` is named (X3, `extra/x3_ibm_kingston/after_...html`): "Not used: b_fez_1150.json (backend ibm_fez, not ibm_kingston)." and "Backend ibm_kingston. The latest record stamped at or before the start: 2026-11-01 11:00 UTC (a_kingston_1100.json)...". The docstring says "A folder that mixes backends is refused unless --backend names one." A page-level refusal note is not built, and in the nothing-before-start branch the mix is not refused at all (H1).

## 4. The ten cases in full

P05 gates detail: edge cz [0,1] has `zz = 0.0 kHz` beside gate_error 0.0042; edge cz [1,2] has `zz = 12.4 kHz`.

### P05: zz = 0.00 on an edge with calibrated CZ error

**Ruling: CANNOT TELL (honest, disclosed out of scope)**

The record has zz=0.00 on edge 0-1 (gates block, 11 entries; the checker reads only `qubits`). Output: exit 0, "Flags (0)", page says "Nothing flagged." The same page says "Gates and zz are not read by this package." in the meta and the footer. Nothing false is asserted about zz; the package cannot see this case. One caution for Bones: the heading + 'Nothing flagged.' sits under a clean-looking exit 0, and the disclaimer is in a note paragraph above and the footer below, not in the Flags section itself.

**Fixture contents** (condensed from the JSON; dates as stored; only the six figure fields shown; gates not shown):

```
FILE data/P05/record.json
backend=ibm_kingston last_update_date='2026-11-01 12:00:00+00:00' gates=11
 q0: T1=152.31 us @2026-11-01 09:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
 q1: T1=152.31 us @2026-11-01 09:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
 q2: T1=152.31 us @2026-11-01 09:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
```

**Exact output, pinned run** (`--at` = the record stamp; the constant meta lines "IBM recalibrates..." and "Gates and zz are not read by this package." are omitted here; the latter is quoted in item 3):

```
$ qia-check before data\P05\record.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 3.
  flags: (none; page says "Nothing flagged.")
```

**Exact output, raw run** (run time = the moment of the run, 2026-11-04 03:15 UTC):

```
$ qia-check before data\P05\record.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 3.
  flag: q0 STALE T1  | measured 2026-11-01 09:00 UTC: 3.0 h before the stamp, 66.3 h before this check
  flag: q0 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q1 STALE T1  | measured 2026-11-01 09:00 UTC: 3.0 h before the stamp, 66.3 h before this check
  flag: q1 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q1 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q1 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q1 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q2 STALE T1  | measured 2026-11-01 09:00 UTC: 3.0 h before the stamp, 66.3 h before this check
  flag: q2 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q2 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q2 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q2 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
```

### P07: same instant as EDT offset, Z, +00:00, naive, (and "EDT" text)

**Ruling: HOLDS (honest)**

Offset spellings agree: a (-04:00), b (Z), c (+00:00) give identical output (pinned: none; raw: the same STALE rows). Zoneless dates d and e give UNKNOWN for T1 and T2 with the reason in the row; the EDT-wall naive record is not guessed. The abbreviation 'EDT' gives UNKNOWN 'cannot be read', no traceback. No wrong number, no silent drop. The requirement 'naive == offset' cannot be met by a refusal, as Bones' notes say; the refusal is the honest behavior.

**Fixture contents** (condensed from the JSON; dates as stored; only the six figure fields shown; gates not shown):

```
FILE data/P07/a_edt_offset.json
backend=ibm_kingston last_update_date='2026-11-01T12:00:00Z' gates=7
 q0: T1=152.31 us @2026-10-31T10:00:00-04:00; T2=118.74 us @2026-10-31T10:00:00-04:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
FILE data/P07/b_utc_Z.json
backend=ibm_kingston last_update_date='2026-11-01T12:00:00Z' gates=7
 q0: T1=152.31 us @2026-10-31T14:00:00Z; T2=118.74 us @2026-10-31T14:00:00Z; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
FILE data/P07/c_plus0000.json
backend=ibm_kingston last_update_date='2026-11-01T12:00:00Z' gates=7
 q0: T1=152.31 us @2026-10-31T14:00:00+00:00; T2=118.74 us @2026-10-31T14:00:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
FILE data/P07/d_naive_utc_wall.json
backend=ibm_kingston last_update_date='2026-11-01T12:00:00Z' gates=7
 q0: T1=152.31 us @2026-10-31T14:00:00; T2=118.74 us @2026-10-31T14:00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
FILE data/P07/e_naive_edt_wall.json
backend=ibm_kingston last_update_date='2026-11-01T12:00:00Z' gates=7
 q0: T1=152.31 us @2026-10-31T10:00:00; T2=118.74 us @2026-10-31T10:00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
FILE data/P07/f_edt_abbrev.json
backend=ibm_kingston last_update_date='2026-11-01T12:00:00Z' gates=7
 q0: T1=152.31 us @2026-10-31T10:00:00 EDT; T2=118.74 us @2026-10-31T10:00:00 EDT; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
```

**Exact output, pinned run** (`--at` = the record stamp; the constant meta lines "IBM recalibrates..." and "Gates and zz are not read by this package." are omitted here; the latter is quoted in item 3):

```
$ qia-check before data\P07\a_edt_offset.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 1.
  flags: (none; page says "Nothing flagged.")
$ qia-check before data\P07\b_utc_Z.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 1.
  flags: (none; page says "Nothing flagged.")
$ qia-check before data\P07\c_plus0000.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 1.
  flags: (none; page says "Nothing flagged.")
$ qia-check before data\P07\d_naive_utc_wall.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 1.
  meta: 2 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | date 2026-10-31T14:00:00 has no zone, so its age cannot be known; not read
  flag: q0 UNKNOWN T2 UNKNOWN | date 2026-10-31T14:00:00 has no zone, so its age cannot be known; not read
$ qia-check before data\P07\e_naive_edt_wall.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 1.
  meta: 2 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | date 2026-10-31T10:00:00 has no zone, so its age cannot be known; not read
  flag: q0 UNKNOWN T2 UNKNOWN | date 2026-10-31T10:00:00 has no zone, so its age cannot be known; not read
$ qia-check before data\P07\f_edt_abbrev.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 1.
  meta: 2 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | date '2026-10-31T10:00:00 EDT' cannot be read
  flag: q0 UNKNOWN T2 UNKNOWN | date '2026-10-31T10:00:00 EDT' cannot be read
```

**Exact output, raw run** (run time = the moment of the run, 2026-11-04 03:15 UTC):

```
$ qia-check before data\P07\a_edt_offset.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 1.
  flag: q0 STALE T1  | measured 2026-10-31 14:00 UTC: 22.0 h before the stamp, 85.3 h before this check
  flag: q0 STALE T2  | measured 2026-10-31 14:00 UTC: 22.0 h before the stamp, 85.3 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
$ qia-check before data\P07\b_utc_Z.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 1.
  flag: q0 STALE T1  | measured 2026-10-31 14:00 UTC: 22.0 h before the stamp, 85.3 h before this check
  flag: q0 STALE T2  | measured 2026-10-31 14:00 UTC: 22.0 h before the stamp, 85.3 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
$ qia-check before data\P07\c_plus0000.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 1.
  flag: q0 STALE T1  | measured 2026-10-31 14:00 UTC: 22.0 h before the stamp, 85.3 h before this check
  flag: q0 STALE T2  | measured 2026-10-31 14:00 UTC: 22.0 h before the stamp, 85.3 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
$ qia-check before data\P07\d_naive_utc_wall.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 1.
  meta: 2 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | date 2026-10-31T14:00:00 has no zone, so its age cannot be known; not read
  flag: q0 UNKNOWN T2 UNKNOWN | date 2026-10-31T14:00:00 has no zone, so its age cannot be known; not read
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
$ qia-check before data\P07\e_naive_edt_wall.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 1.
  meta: 2 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | date 2026-10-31T10:00:00 has no zone, so its age cannot be known; not read
  flag: q0 UNKNOWN T2 UNKNOWN | date 2026-10-31T10:00:00 has no zone, so its age cannot be known; not read
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
$ qia-check before data\P07\f_edt_abbrev.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 1.
  meta: 2 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | date '2026-10-31T10:00:00 EDT' cannot be read
  flag: q0 UNKNOWN T2 UNKNOWN | date '2026-10-31T10:00:00 EDT' cannot be read
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
```

### E01: malformed JSON (truncated, trailing comma, list top-level, no stamp)

**Ruling: HOLDS (honest)**

All four bad single files refuse: exit 1, one-line reason on stderr, no report written, no traceback. In after mode the unreadable file is named in the page ('Not used: bad.json (...)') and the good record is still checked. Nothing silently dropped. (Caveat of wording only: 'no_stamp' and 'list_top' both say 'not a calibration record', which is true but does not say which part is missing.)

**Fixture contents** (condensed from the JSON; dates as stored; only the six figure fields shown; gates not shown):

```
FILE data/E01/truncated.json
RAW(unparseable: Expecting ',' delimiter: line 97 column 3 (char 1739)):
{
 "backend_name": "ibm_kingston",
 "backend_version": "1.27.3",
 "last_update_date": "2026-11-01 12:00:00+00:00",
 "qubits": [
  [
   {
    "date": "2026-11-01 09:00:00+00:00",
    "name": "T1",
    "unit": "us",
    "value": 152.31
   },
   {
    "date": "2026-11-01 09:07:00+00:00",
    "name": "T2",
    "unit": "us",
    "value": 118.74
   },
   {
    "date": "2026-11-01 08:00:00+00:00",
    "n
FILE data/E01/trailing_comma.json
RAW(unparseable: Illegal trailing comma before end of object: line 1 column 97 (char 96)):
{"backend_name": "ibm_kingston", "last_update_date": "2026-11-01 12:00:00+00:00", "qubits": [[]],}
FILE data/E01/list_top.json
JSON top-level is list: [{
 "backend_name": "ibm_kingston",
 "backend_version": "1.27.3",
 "last_update_date": "2026-11-01 12:00:00+00:00",
 "qubits": [
  [
   {
    "date": "2026-11-01 09:00:00+00:00",
    "name": "T1",
   
FILE data/E01/no_stamp.json
backend=ibm_kingston last_update_date=None gates=7
 q0: T1=152.31 us @2026-11-01 09:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
FILE data/E01/dir/bad.json
RAW(unparseable: Expecting property name enclosed in double quotes: line 10 column 5 (char 200)):
{
 "backend_name": "ibm_kingston",
 "backend_version": "1.27.3",
 "last_update_date": "2026-11-01 12:00:00+00:00",
 "qubits": [
  [
   {
    "date": "2026-11-01 09:00:00+00:00",
    "name": "T1",
    
FILE data/E01/dir/good.json
backend=ibm_kingston last_update_date='2026-11-01 11:00:00+00:00' gates=7
 q0: T1=152.31 us @2026-11-01 09:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
```

**Exact output, pinned run** (`--at` = the record stamp; the constant meta lines "IBM recalibrates..." and "Gates and zz are not read by this package." are omitted here; the latter is quoted in item 3):

```
$ qia-check before data\E01\truncated.json   -> exit 1
  stderr: data/E01/truncated.json is not a readable calibration record (Qiskit BackendProperties JSON): Expecting ',' delimiter: line 97 column 3 (char 1739)
$ qia-check before data\E01\trailing_comma.json   -> exit 1
  stderr: data/E01/trailing_comma.json is not a readable calibration record (Qiskit BackendProperties JSON): Illegal trailing comma before end of object: line 1 column 97 (char 96)
$ qia-check before data\E01\list_top.json   -> exit 1
  stderr: data/E01/list_top.json is not a readable calibration record (Qiskit BackendProperties JSON): not a calibration record
$ qia-check before data\E01\no_stamp.json   -> exit 1
  stderr: data/E01/no_stamp.json is not a readable calibration record (Qiskit BackendProperties JSON): not a calibration record
$ qia-check after data\E01\dir --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z   -> exit 0
  meta: Run window 2026-11-01 12:00 to 2026-11-01 12:40 UTC. Records read: 1.
  meta: Backend ibm_kingston. The latest record stamped at or before the start: 2026-11-01 11:00 UTC (good.json). If IBM recalibrated after it and before the run, the record in force is not in the folder.
  meta: Not used: bad.json (Expecting property name enclosed in double quotes: line 10 column 5 (char 200)).
  meta: Records stamped during the run: 0.
  flags: (none; page says "Nothing flagged.")
```

**Exact output, raw run** (run time = the moment of the run, 2026-11-04 03:15 UTC):

```
$ qia-check before data\E01\truncated.json   -> exit 1
  stderr: data/E01/truncated.json is not a readable calibration record (Qiskit BackendProperties JSON): Expecting ',' delimiter: line 97 column 3 (char 1739)
$ qia-check before data\E01\trailing_comma.json   -> exit 1
  stderr: data/E01/trailing_comma.json is not a readable calibration record (Qiskit BackendProperties JSON): Illegal trailing comma before end of object: line 1 column 97 (char 96)
$ qia-check before data\E01\list_top.json   -> exit 1
  stderr: data/E01/list_top.json is not a readable calibration record (Qiskit BackendProperties JSON): not a calibration record
$ qia-check before data\E01\no_stamp.json   -> exit 1
  stderr: data/E01/no_stamp.json is not a readable calibration record (Qiskit BackendProperties JSON): not a calibration record
$ qia-check after data\E01\dir --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z   -> exit 0
  meta: Run window 2026-11-01 12:00 to 2026-11-01 12:40 UTC. Records read: 1.
  meta: Backend ibm_kingston. The latest record stamped at or before the start: 2026-11-01 11:00 UTC (good.json). If IBM recalibrated after it and before the run, the record in force is not in the folder.
  meta: Not used: bad.json (Expecting property name enclosed in double quotes: line 10 column 5 (char 200)).
  meta: Records stamped during the run: 0.
  flags: (none; page says "Nothing flagged.")
```

### E02: empty qubit list; a qubit with an empty property list

**Ruling: HOLDS (honest)**

Empty qubit list: exit 2, stderr and page both say NO QUBITS CHECKED / 'Nothing here is a pass'. With --qubits 0,1 on an empty record: same, plus 'Not in this record'. Empty qubit 0 beside a healthy qubit 1: q0 gets UNKNOWN (all), 'Qubits checked: 2', and the meta says UNKNOWN is not a pass; exit stays 0, which is consistent with how UNKNOWN is handled everywhere else in this build.

**Fixture contents** (condensed from the JSON; dates as stored; only the six figure fields shown; gates not shown):

```
FILE data/E02/empty.json
backend=ibm_kingston last_update_date='2026-11-01 12:00:00+00:00' gates=7
FILE data/E02/empty_qubit.json
backend=ibm_kingston last_update_date='2026-11-01 12:00:00+00:00' gates=7
 q0: []
 q1: T1=152.31 us @2026-11-01 09:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
```

**Exact output, pinned run** (`--at` = the record stamp; the constant meta lines "IBM recalibrates..." and "Gates and zz are not read by this package." are omitted here; the latter is quoted in item 3):

```
$ qia-check before data\E02\empty.json   -> exit 2
  stderr: NO QUBITS CHECKED: this report is not a pass (exit 2)
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 0.
  meta: NO QUBITS CHECKED: the record has no qubits, or none of the ones asked for. Nothing here is a pass.
  flags: (none; page says "Nothing flagged.")
$ qia-check before data\E02\empty.json --qubits 0,1   -> exit 2
  stderr: NO QUBITS CHECKED: this report is not a pass (exit 2)
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 0.
  meta: NO QUBITS CHECKED: the record has no qubits, or none of the ones asked for. Nothing here is a pass.
  meta: Not in this record, so not checked: qubits 0, 1.
  flags: (none; page says "Nothing flagged.")
$ qia-check before data\E02\empty_qubit.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 2.
  meta: 1 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN (all) UNKNOWN | no T1, T2 or error figures for this qubit in the record
```

**Exact output, raw run** (run time = the moment of the run, 2026-11-04 03:15 UTC):

```
$ qia-check before data\E02\empty.json   -> exit 2
  stderr: NO QUBITS CHECKED: this report is not a pass (exit 2)
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 0.
  meta: NO QUBITS CHECKED: the record has no qubits, or none of the ones asked for. Nothing here is a pass.
  flags: (none; page says "Nothing flagged.")
$ qia-check before data\E02\empty.json --qubits 0,1   -> exit 2
  stderr: NO QUBITS CHECKED: this report is not a pass (exit 2)
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 0.
  meta: NO QUBITS CHECKED: the record has no qubits, or none of the ones asked for. Nothing here is a pass.
  meta: Not in this record, so not checked: qubits 0, 1.
  flags: (none; page says "Nothing flagged.")
$ qia-check before data\E02\empty_qubit.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 2.
  meta: 1 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN (all) UNKNOWN | no T1, T2 or error figures for this qubit in the record
  flag: q1 STALE T1  | measured 2026-11-01 09:00 UTC: 3.0 h before the stamp, 66.3 h before this check
  flag: q1 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q1 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q1 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q1 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
```

### E03: duplicate entries for one qubit with conflicting values

**Ruling: HOLDS (honest)**

Duplicate T1 entries that conflict: UNKNOWN T1 '2 conflicting entries in one record; none used', identical for stale-first, stale-last and the ratio conflict, so order no longer matters. T2/T1 and the dates of the conflicted field are not evaluated (honest: T1 is not trusted). Note: a PAIR check is also skipped for that qubit because the conflicted T1 date is dropped; covered by the UNKNOWN row.

**Fixture contents** (condensed from the JSON; dates as stored; only the six figure fields shown; gates not shown):

```
FILE data/E03/stale_first.json
backend=ibm_kingston last_update_date='2026-11-01 12:00:00+00:00' gates=7
 q0: T1=152.31 us @2026-10-30 12:00:00+00:00; T1=152.31 us @2026-11-01 09:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
FILE data/E03/stale_last.json
backend=ibm_kingston last_update_date='2026-11-01 12:00:00+00:00' gates=7
 q0: T1=152.31 us @2026-11-01 09:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00; T1=152.31 us @2026-10-30 12:00:00+00:00
FILE data/E03/ratio_conflict.json
backend=ibm_kingston last_update_date='2026-11-01 12:00:00+00:00' gates=7
 q0: T1=150.0 us @2026-11-01 09:00:00+00:00; T2=400.0 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00; T1=210.0 us @2026-11-01 09:00:00+00:00
```

**Exact output, pinned run** (`--at` = the record stamp; the constant meta lines "IBM recalibrates..." and "Gates and zz are not read by this package." are omitted here; the latter is quoted in item 3):

```
$ qia-check before data\E03\stale_first.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 1.
  meta: 1 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | 2 conflicting entries in one record; none used
$ qia-check before data\E03\stale_last.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 1.
  meta: 1 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | 2 conflicting entries in one record; none used
$ qia-check before data\E03\ratio_conflict.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 1.
  meta: 1 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | 2 conflicting entries in one record; none used
```

**Exact output, raw run** (run time = the moment of the run, 2026-11-04 03:15 UTC):

```
$ qia-check before data\E03\stale_first.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 1.
  meta: 1 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | 2 conflicting entries in one record; none used
  flag: q0 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
$ qia-check before data\E03\stale_last.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 1.
  meta: 1 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | 2 conflicting entries in one record; none used
  flag: q0 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
$ qia-check before data\E03\ratio_conflict.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 1.
  meta: 1 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | 2 conflicting entries in one record; none used
  flag: q0 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
```

### E05: T1 in s / ms vs T2 in us (unit confusion)

**Ruling: HOLDS (correct numbers)**

Units are normalised: q0 T1 0.0001502 s = 150.2 us vs T2 118.74 us -> ratio 0.79, no flag (right). q1 T1 150.2 us vs T2 0.0004 s = 400 us -> ratio 2.663, ABOVE (right). q2 T1 0.1502 ms = 150.2 us vs T2 400 us -> 2.663 ABOVE (right). Printed T1/T2 are in us, so the page shows the normalisation. The three ratios match the truth in the fixture.

**Fixture contents** (condensed from the JSON; dates as stored; only the six figure fields shown; gates not shown):

```
FILE data/E05/record.json
backend=ibm_kingston last_update_date='2026-11-01 12:00:00+00:00' gates=11
 q0: T1=0.0001502 s @2026-11-01 09:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
 q1: T1=150.2 us @2026-11-01 09:00:00+00:00; T2=0.0004 s @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
 q2: T1=0.1502 ms @2026-11-01 09:00:00+00:00; T2=400.0 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
```

**Exact output, pinned run** (`--at` = the record stamp; the constant meta lines "IBM recalibrates..." and "Gates and zz are not read by this package." are omitted here; the latter is quoted in item 3):

```
$ qia-check before data\E05\record.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 3.
  flag: q1 T2>2T1 T2/T1 ABOVE | ratio 2.663 (T1 150.2 us, T2 400 us)
  flag: q2 T2>2T1 T2/T1 ABOVE | ratio 2.663 (T1 150.2 us, T2 400 us)
```

**Exact output, raw run** (run time = the moment of the run, 2026-11-04 03:15 UTC):

```
$ qia-check before data\E05\record.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 3.
  flag: q0 STALE T1  | measured 2026-11-01 09:00 UTC: 3.0 h before the stamp, 66.3 h before this check
  flag: q0 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q1 STALE T1  | measured 2026-11-01 09:00 UTC: 3.0 h before the stamp, 66.3 h before this check
  flag: q1 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q1 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q1 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q1 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q1 T2>2T1 T2/T1 ABOVE | ratio 2.663 (T1 150.2 us, T2 400 us)
  flag: q2 STALE T1  | measured 2026-11-01 09:00 UTC: 3.0 h before the stamp, 66.3 h before this check
  flag: q2 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q2 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q2 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q2 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q2 T2>2T1 T2/T1 ABOVE | ratio 2.663 (T1 150.2 us, T2 400 us)
```

### E06: string-typed numbers

**Ruling: HOLDS (honest, correct)**

Numeric strings are read: '152.31'/'118.74' give no T2>2T1 (ratio 0.78, right). String zeros '0.0' (readout_error) and '0' (prob_meas0_prep1) give ZERO (right, the value is zero). T2 '400.0' with T1 150.0 gives ABOVE 2.667 (right). No traceback. Raw run also lists STALE rows against 'this check' (about 63 h after the stamp); those are true.

**Fixture contents** (condensed from the JSON; dates as stored; only the six figure fields shown; gates not shown):

```
FILE data/E06/numbers_as_strings.json
backend=ibm_kingston last_update_date='2026-11-01 12:00:00+00:00' gates=7
 q0: T1='152.31' us @2026-11-01 09:00:00+00:00; T2='118.74' us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
FILE data/E06/zero_as_string.json
backend=ibm_kingston last_update_date='2026-11-01 12:00:00+00:00' gates=7
 q0: T1=152.31 us @2026-11-01 09:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error='0.0' @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
 q1: T1=152.31 us @2026-11-01 09:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1='0' @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
FILE data/E06/err_as_string_nonzero.json
backend=ibm_kingston last_update_date='2026-11-01 12:00:00+00:00' gates=7
 q0: T1=150.0 us @2026-11-01 09:00:00+00:00; T2='400.0' us @2026-11-01 09:07:00+00:00; readout_error='0.0122' @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
```

**Exact output, pinned run** (`--at` = the record stamp; the constant meta lines "IBM recalibrates..." and "Gates and zz are not read by this package." are omitted here; the latter is quoted in item 3):

```
$ qia-check before data\E06\numbers_as_strings.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 1.
  flags: (none; page says "Nothing flagged.")
$ qia-check before data\E06\zero_as_string.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 2.
  flag: q0 ZERO readout_error  | published value 0
  flag: q1 ZERO prob_meas0_prep1  | published value 0
$ qia-check before data\E06\err_as_string_nonzero.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 0.0 h before the run time 2026-11-01 12:00 UTC. Qubits checked: 1.
  flag: q0 T2>2T1 T2/T1 ABOVE | ratio 2.667 (T1 150 us, T2 400 us)
```

**Exact output, raw run** (run time = the moment of the run, 2026-11-04 03:15 UTC):

```
$ qia-check before data\E06\numbers_as_strings.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 1.
  flag: q0 STALE T1  | measured 2026-11-01 09:00 UTC: 3.0 h before the stamp, 66.3 h before this check
  flag: q0 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
$ qia-check before data\E06\zero_as_string.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 2.
  flag: q0 STALE T1  | measured 2026-11-01 09:00 UTC: 3.0 h before the stamp, 66.3 h before this check
  flag: q0 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 ZERO readout_error  | published value 0
  flag: q1 STALE T1  | measured 2026-11-01 09:00 UTC: 3.0 h before the stamp, 66.3 h before this check
  flag: q1 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q1 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q1 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q1 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q1 ZERO prob_meas0_prep1  | published value 0
$ qia-check before data\E06\err_as_string_nonzero.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 12:00 UTC, 63.3 h before this check. Qubits checked: 1.
  flag: q0 STALE T1  | measured 2026-11-01 09:00 UTC: 3.0 h before the stamp, 66.3 h before this check
  flag: q0 STALE T2  | measured 2026-11-01 09:07 UTC: 2.9 h before the stamp, 66.1 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: 2.5 h before the stamp, 65.8 h before this check
  flag: q0 T2>2T1 T2/T1 ABOVE | ratio 2.667 (T1 150 us, T2 400 us)
```

### E07: leap second and DST fall-back timestamps

**Ruling: HOLE (narrow): honest on leap seconds and aware DST; wrong on the naive stamp**

(a) leap second: T1 date 2016-12-31T23:59:60Z is read as 00:00:00 on 1 Jan; the pinned run is clean, ages right. (b) leap in the stamp: read as 2017-01-01 00:00 UTC, right (my pinning shim could not parse ':60', so that cell ran unpinned in the 'pinned' pass; I re-ran it by hand with --at 2017-01-01T00:00:00Z, see Tweaks; result: no flags, meta '0.0 h before the run time'). (c) DST with offsets: stamp 06:15Z, T1 05:45Z a day earlier: STALE 24.5 h and PAIR 24.5 h, both right. (d) DST naive walls: T1 and T2 are refused UNKNOWN (honest) BUT the record stamp '2026-11-01T01:15:00' is also zoneless and is silently read as UTC and printed as fact: 'record stamped 2026-11-01 01:15 UTC'. On fall-back night in New York that wall time is 05:15 or 06:15 UTC (ambiguous), so the stamp and every 'h before the stamp' / 'h before this check' number derived from it carry an unflagged 4-5 h assumption. R06's refusal covers field dates, not the stamp. Repro with a number that visibly moves is in Hole H2 below. Ruling: wrong (an unmarked assumption presented as a figure).

**Fixture contents** (condensed from the JSON; dates as stored; only the six figure fields shown; gates not shown):

```
FILE data/E07/leap_t1.json
backend=ibm_kingston last_update_date='2017-01-01T06:00:00Z' gates=7
 q0: T1=152.31 us @2016-12-31T23:59:60Z; T2=118.74 us @2017-01-01T00:00:00Z; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
FILE data/E07/leap_stamp.json
backend=ibm_kingston last_update_date='2016-12-31T23:59:60Z' gates=7
 q0: T1=152.31 us @2016-12-31T12:00:00Z; T2=118.74 us @2016-12-31T12:00:00Z; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
FILE data/E07/dst_aware.json
backend=ibm_kingston last_update_date='2026-11-01T01:15:00-05:00' gates=7
 q0: T1=152.31 us @2026-10-31T01:45:00-04:00; T2=118.74 us @2026-11-01T01:15:00-05:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
FILE data/E07/dst_naive_walls.json
backend=ibm_kingston last_update_date='2026-11-01T01:15:00' gates=7
 q0: T1=152.31 us @2026-10-31T01:45:00; T2=118.74 us @2026-11-01T01:15:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
```

**Exact output, pinned run** (`--at` = the record stamp; the constant meta lines "IBM recalibrates..." and "Gates and zz are not read by this package." are omitted here; the latter is quoted in item 3):

```
$ qia-check before data\E07\leap_t1.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2017-01-01 06:00 UTC, 0.0 h before the run time 2017-01-01 06:00 UTC. Qubits checked: 1.
  flags: (none; page says "Nothing flagged.")
$ qia-check before data\E07\leap_stamp.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2017-01-01 00:00 UTC, 86259.3 h before this check. Qubits checked: 1.
  flag: q0 STALE T1  | measured 2016-12-31 12:00 UTC: 12.0 h before the stamp, 86271.3 h before this check
  flag: q0 STALE T2  | measured 2016-12-31 12:00 UTC: 12.0 h before the stamp, 86271.3 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: -86193.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: -86193.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: -86193.5 h before the stamp, 65.8 h before this check
$ qia-check before data\E07\dst_aware.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 06:15 UTC, 0.0 h before the run time 2026-11-01 06:15 UTC. Qubits checked: 1.
  flag: q0 STALE T1  | measured 2026-10-31 05:45 UTC: 24.5 h before the stamp, 24.5 h before the run time
  flag: q0 PAIR T1/T2 dates  | 24.5 h apart
$ qia-check before data\E07\dst_naive_walls.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 01:15 UTC, 0.0 h before the run time 2026-11-01 01:15 UTC. Qubits checked: 1.
  meta: 2 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | date 2026-10-31T01:45:00 has no zone, so its age cannot be known; not read
  flag: q0 UNKNOWN T2 UNKNOWN | date 2026-11-01T01:15:00 has no zone, so its age cannot be known; not read
```

**Exact output, raw run** (run time = the moment of the run, 2026-11-04 03:15 UTC):

```
$ qia-check before data\E07\leap_t1.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2017-01-01 06:00 UTC, 86253.3 h before this check. Qubits checked: 1.
  flag: q0 STALE T1  | measured 2017-01-01 00:00 UTC: 6.0 h before the stamp, 86259.3 h before this check
  flag: q0 STALE T2  | measured 2017-01-01 00:00 UTC: 6.0 h before the stamp, 86259.3 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: -86187.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: -86187.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: -86187.5 h before the stamp, 65.8 h before this check
$ qia-check before data\E07\leap_stamp.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2017-01-01 00:00 UTC, 86259.3 h before this check. Qubits checked: 1.
  flag: q0 STALE T1  | measured 2016-12-31 12:00 UTC: 12.0 h before the stamp, 86271.3 h before this check
  flag: q0 STALE T2  | measured 2016-12-31 12:00 UTC: 12.0 h before the stamp, 86271.3 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: -86193.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: -86193.5 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: -86193.5 h before the stamp, 65.8 h before this check
$ qia-check before data\E07\dst_aware.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 06:15 UTC, 69.0 h before this check. Qubits checked: 1.
  flag: q0 STALE T1  | measured 2026-10-31 05:45 UTC: 24.5 h before the stamp, 93.5 h before this check
  flag: q0 STALE T2  | measured 2026-11-01 06:15 UTC: 0.0 h before the stamp, 69.0 h before this check
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: -3.2 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: -3.2 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: -3.2 h before the stamp, 65.8 h before this check
  flag: q0 PAIR T1/T2 dates  | 24.5 h apart
$ qia-check before data\E07\dst_naive_walls.json   -> exit 0
  meta: Backend ibm_kingston, record stamped 2026-11-01 01:15 UTC, 74.0 h before this check. Qubits checked: 1.
  meta: 2 figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.
  flag: q0 UNKNOWN T1 UNKNOWN | date 2026-10-31T01:45:00 has no zone, so its age cannot be known; not read
  flag: q0 UNKNOWN T2 UNKNOWN | date 2026-11-01T01:15:00 has no zone, so its age cannot be known; not read
  flag: q0 STALE readout_error  | measured 2026-11-01 09:30 UTC: -8.2 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas0_prep1  | measured 2026-11-01 09:30 UTC: -8.2 h before the stamp, 65.8 h before this check
  flag: q0 STALE prob_meas1_prep0  | measured 2026-11-01 09:30 UTC: -8.2 h before the stamp, 65.8 h before this check
```

### D02: after mode with records from two backends in one folder

**Ruling: HOLDS (true refusal)**

Mixed folder (ibm_kingston 11:00, ibm_fez 11:50) is refused: exit 1, stderr 'the folder mixes backends (ibm_fez, ibm_kingston); give --backend NAME; refused', no report. Honest. With --backend named (my extra run) each backend is chosen correctly and the other is listed 'Not used: ... (backend ibm_fez, not ibm_kingston)'. Two limits: the refusal is stderr only, there is no report page for it (matters for item 3), and it only fires when some record is stamped at or before --start (Hole H1).

**Fixture contents** (condensed from the JSON; dates as stored; only the six figure fields shown; gates not shown):

```
FILE data/D02/records/a_kingston_1100.json
backend=ibm_kingston last_update_date='2026-11-01 11:00:00+00:00' gates=7
 q0: T1=152.31 us @2026-11-01 08:00:00+00:00; T2=118.74 us @2026-11-01 08:07:00+00:00; readout_error=0.0122 @2026-11-01 08:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 08:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 08:30:00+00:00
 q1: T1=152.31 us @2026-11-01 08:00:00+00:00; T2=118.74 us @2026-11-01 08:07:00+00:00; readout_error=0.0122 @2026-11-01 08:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 08:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 08:30:00+00:00
FILE data/D02/records/b_fez_1150.json
backend=ibm_fez last_update_date='2026-11-01 11:50:00+00:00' gates=7
 q0: T1=61.0 us @2026-10-30 20:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
 q1: T1=61.0 us @2026-10-30 20:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
```

**Exact output, pinned run** (`--at` = the record stamp; the constant meta lines "IBM recalibrates..." and "Gates and zz are not read by this package." are omitted here; the latter is quoted in item 3):

```
$ qia-check after data\D02\records --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z --qubits 0,1   -> exit 1
  stderr: the folder mixes backends (ibm_fez, ibm_kingston); give --backend NAME; refused
```

**Exact output, raw run** (run time = the moment of the run, 2026-11-04 03:15 UTC):

```
$ qia-check after data\D02\records --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z --qubits 0,1   -> exit 1
  stderr: the folder mixes backends (ibm_fez, ibm_kingston); give --backend NAME; refused
```

### D04: two files, same stamp, different contents

**Ruling: HOLDS (honest)**

a.json and b.json share the 12:00 stamp and differ. Page: 'CONFLICT: a.json and b.json share the stamp 2026-11-01 12:00 UTC and differ. Both are checked below.' Both are checked and flags are tagged by file; a.json is clean; b.json (T1 41 us measured 50 h before the stamp, T2 118.74) gets STALE T1 50.0 h, T2>2T1 ABOVE ratio 2.896 (118.74/41 = 2.896, right) and PAIR 47.1 h (right). The answer no longer depends on file name.

**Fixture contents** (condensed from the JSON; dates as stored; only the six figure fields shown; gates not shown):

```
FILE data/D04/records/a.json
backend=ibm_kingston last_update_date='2026-11-01 12:00:00+00:00' gates=7
 q0: T1=152.31 us @2026-11-01 09:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
FILE data/D04/records/b.json
backend=ibm_kingston last_update_date='2026-11-01 12:00:00+00:00' gates=7
 q0: T1=41.0 us @2026-10-30 10:00:00+00:00; T2=118.74 us @2026-11-01 09:07:00+00:00; readout_error=0.0122 @2026-11-01 09:30:00+00:00; prob_meas0_prep1=0.0151 @2026-11-01 09:30:00+00:00; prob_meas1_prep0=0.0093 @2026-11-01 09:30:00+00:00
```

**Exact output, pinned run** (`--at` = the record stamp; the constant meta lines "IBM recalibrates..." and "Gates and zz are not read by this package." are omitted here; the latter is quoted in item 3):

```
$ qia-check after data\D04\records --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z   -> exit 0
  meta: Run window 2026-11-01 12:00 to 2026-11-01 12:40 UTC. Records read: 2.
  meta: Backend ibm_kingston. The latest record stamped at or before the start: 2026-11-01 12:00 UTC (a.json, b.json). If IBM recalibrated after it and before the run, the record in force is not in the folder.
  meta: CONFLICT: a.json and b.json share the stamp 2026-11-01 12:00 UTC and differ. Both are checked below.
  meta: Records stamped during the run: 0.
  flag: b.json q0 STALE T1  | measured 2026-10-30 10:00 UTC: 50.0 h before the stamp, 50.0 h before the run start
  flag: b.json q0 T2>2T1 T2/T1 ABOVE | ratio 2.896 (T1 41 us, T2 118.7 us)
  flag: b.json q0 PAIR T1/T2 dates  | 47.1 h apart
```

**Exact output, raw run** (run time = the moment of the run, 2026-11-04 03:15 UTC):

```
$ qia-check after data\D04\records --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z   -> exit 0
  meta: Run window 2026-11-01 12:00 to 2026-11-01 12:40 UTC. Records read: 2.
  meta: Backend ibm_kingston. The latest record stamped at or before the start: 2026-11-01 12:00 UTC (a.json, b.json). If IBM recalibrated after it and before the run, the record in force is not in the folder.
  meta: CONFLICT: a.json and b.json share the stamp 2026-11-01 12:00 UTC and differ. Both are checked below.
  meta: Records stamped during the run: 0.
  flag: b.json q0 STALE T1  | measured 2026-10-30 10:00 UTC: 50.0 h before the stamp, 50.0 h before the run start
  flag: b.json q0 T2>2T1 T2/T1 ABOVE | ratio 2.896 (T1 41 us, T2 118.7 us)
  flag: b.json q0 PAIR T1/T2 dates  | 47.1 h apart
```
