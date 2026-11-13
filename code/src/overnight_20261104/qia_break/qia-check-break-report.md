# qia-check 1.0.0: adversarial break report (DRAFT for Bones)

Sage, 2026-11-03. Draft only. Nothing was published, pushed, tagged or filed. No fix was applied to the package.

**Bottom line.** Across 27 fixtures: **20 HOLE, 5 HOLDS, 2 CANNOT TELL.** The 20 holes come from 16 root causes, each with a reproducer of 15 lines or fewer. All three predictions on record are confirmed by the published package:

| prediction | result | fixtures |
|---|---|---|
| Q10 field coverage | **Confirmed.** Only T1 and T2 dates are ever aged. readout_error, prob_meas0_prep1 and prob_meas1_prep0 dates are loaded but never compared, and init_error is not even loaded. | P01, P02, E08 |
| Silent pass on missing fields | **Confirmed.** Absent, null, NaN, zero or negative T1/T2, a null date, an empty qubit block and an empty record all produce "Nothing flagged" with exit 0. There is no UNKNOWN outcome anywhere in the code. | P04, E02, E04, D01 |
| Staleness pinned to the stamp | **Confirmed.** Age is `last_update_date − field date`. The run time never enters the STALE check, in either mode. | P03, P12 |

---

## 1. What was installed (step 1)

- **Source:** fresh venv, `pip install qia-check` from PyPI, not the repo. Re-run in a second fresh venv with `pip install --no-cache-dir --require-hashes` pinned to the hash below.
- **Version:** **qia-check 1.0.0.** It is the only release on PyPI.
- **Wheel:** `qia_check-1.0.0-py3-none-any.whl`, sha256 `43a0cf7870c35e4f5a657a43f33aa3ca9a41690116475aac1f2d4cd9e8551304`, uploaded 2026-11-02T01:48:20. This matches both the PyPI JSON and my local download.
- **Sdist:** `qia_check-1.0.0.tar.gz`, sha256 `b9b8efa172aff90b2021222e22c30518cd3ff178e86c4ac99e3947b10a06ca43`, uploaded 2026-11-02T01:48:22.
- **Installed module:** `site-packages/qia_check.py`, 153 lines, sha256 `ef38eede8b3ae519e9c647dc85cb73d41a9e52c4f45c4bbedb58c333578df4ab`.
- **Python:** 3.13.13 on Windows. This is the only interpreter on this machine, so the claimed 3.9 floor is untested (see §8).

`pip show qia-check` (the full `-f` listing is in `qia_break/provenance.txt`):
```
Name: qia-check
Version: 1.0.0
Summary: Checks on IBM Quantum calibration records before and after a run, from Heuremen LLC. Standard library only.
Home-page: https://indahl.ai/qia
Author: Heuremen LLC
License: Heuremen LLC ... (full license text in the License field)
Location: ...\qia_break\venv_clean\Lib\site-packages
Requires:
Required-by:
Files: Scripts\qia-check.exe, share\doc\qia-check\{CITATION.cff,TESTED.md}, qia_check.py, qia_check-1.0.0.dist-info\*
```
Project URLs: Documentation https://indahl.ai/qia/package, Homepage https://indahl.ai/qia, Source https://github.com/Heuremen-LLC/indahl.ai. The console script is `qia-check = qia_check:main`. There are no dependencies; `[ibm]` adds qiskit-ibm-runtime.

## 2. Source reading (step 2)

All line numbers are for `qia_check.py` 1.0.0 as installed.

### Loading and parsing (shared by every check)
- **`qia_check.py:30`** `ERRS = ('readout_error', 'prob_meas1_prep0', 'prob_meas0_prep1'); FIELDS = ('T1', 'T2') + ERRS`
  - Only these five Nduv names are kept.
  - `init_error`, `frequency`, `readout_length` and every entry in `gates` (including any `zz`) are discarded.
- **`qia_check.py:43`** `if not isinstance(d, dict) or 'last_update_date' not in d or not isinstance(d.get('qubits'), list): raise ValueError(...)`
  - This is the only structural check.
  - An empty `qubits: []` passes it.
- **`qia_check.py:46`** `Q[i] = {x['name']: (x.get('value'), x.get('date'), x.get('unit', '')) for x in qs if x.get('name') in FIELDS}`
  - Qubits are indexed by position.
  - A repeated name inside one qubit's list silently keeps the **last** entry.
  - `unit` is stored but never read again.
  - Values are not type-checked: strings, None and NaN pass straight through.
- **`qia_check.py:47`** `return d.get('backend_name', '?'), when(d['last_update_date']), Q`. **S, the stamp, is the only time base the checks receive.**
- **`qia_check.py:34-35`** `def when(s): d = dt.datetime.fromisoformat(str(s).replace('Z', '+00:00')); return (d if d.tzinfo else d.replace(tzinfo=UTC)).astimezone(UTC)`
  - A 'Z' is turned into +00:00.
  - Offsets are honoured.
  - **A naive time is silently assumed to be UTC.**
  - Unparseable strings (a leap second `:60`, or text like `EDT`) raise ValueError.
- **`qia_check.py:91-95`** `utc()` is the CLI parser for `--start` and `--end`. It does the opposite of `when()`: `if d.tzinfo is None: sys.exit('... add Z or an offset, so the time is not read in the wrong zone')`. So the tool refuses naive run times but accepts naive record times.
- **`qia_check.py:109-110`** In before mode only `load()` sits inside `try/except (ValueError, KeyError, JSONDecodeError)`. `check_record()` (line 111) does not, so any parse or type error in a field becomes a raw traceback with no report.

### STALE
- **`qia_check.py:52-53`**
  ```
  for f in ('T1', 'T2'):
      if e.get(f) and e[f][1] and (S - when(e[f][1])).total_seconds() > 86400:
  ```
- **Fields read:** T1 and T2 dates only. The error-field dates are never compared, and init_error is never loaded.
- **Operator:** strict `>` 86400 s. Exactly 24 h 00 m 00 s is not stale; 24 h plus 1 µs is.
- **Time base:** **S − date, where S = `last_update_date`.** The run time is not used. In before mode, `now` appears only in a prose meta line (`qia_check.py:112-113`: `age = (dt.datetime.now(UTC) - S)...`, "record stamped ..., X h before this check"), never as a flag. In after mode, `--start` only selects which record to check (`qia_check.py:131`), and `check_record(S, Q, qs)` (`qia_check.py:139`) still ages against that record's own stamp.
- **Absent / null:**
  - Absent field: `e.get(f)` is None, so the check is skipped silently.
  - Null or empty date: `e[f][1]` is falsy, so the check is skipped silently.
  - A null or NaN *value* does not block STALE, because the tuple is truthy.
  - Dates later than the stamp give a negative age and never flag.

### ZERO
- **`qia_check.py:55-56`** `for f in ERRS: if e.get(f) and e[f][0] == 0: rows.append(... 'published value exactly 0')`
- **Fields read:** readout_error, prob_meas1_prep0, prob_meas0_prep1 (values only).
- **Operator:** `== 0`.
  - `-0.0 == 0` is True, so it flags.
  - `False == 0` is True, so it flags.
  - The string `"0"` compares unequal to 0, so it **passes silently**.
  - 1e-17 passes.
- **Absent / null / NaN:** absent is skipped; `None == 0` and `nan == 0` are False, so both pass silently.

### T2>2T1
- **`qia_check.py:57-59`**
  ```
  if t1 and t2 and t1[0] and t2[0] is not None and t1[0] > 0:
      r = t2[0] / t1[0]
      if r > 2.0: rows.append(... outcome='ABOVE' if r > 2.5 else 'CANNOT_TELL')
  ```
- **Fields read:** T1 and T2 values. Units are ignored.
- **Operators:** strict `> 2.0`, then strict `> 2.5`.
  - Exactly 2.0 gives no row. That is the OK case, and it shows nowhere in the report.
  - Exactly 2.5 gives CANNOT_TELL.
  - The ratio is a binary float division, so a decimal-exact 2.5 can land on 2.5000000000000004 and read ABOVE.
- **Absent / null / NaN / 0 / negative:**
  - T1 absent, null, 0 or negative: skipped silently.
  - T1 NaN: NaN is truthy, but `nan > 0` is False, so skipped silently.
  - T2 null: skipped silently.
  - T2 NaN: `r = nan` and `nan > 2.0` is False, so skipped silently.
  - A string T1 raises TypeError at `t1[0] > 0`; a string T2 raises TypeError at `/`. Either way the result is a traceback.

### PAIR
- **`qia_check.py:60-62`**, indented **inside** the line 57 block:
  ```
  if t1[1] and t2[1]:
      gap = abs((when(t1[1]) - when(t2[1])).total_seconds()) / 3600
      if gap > 24: rows.append(dict(... check='PAIR' ...))
  ```
- **Fields read:** T1 and T2 dates.
- **Operator:** strict `> 24` h on the absolute gap. Exactly 24 h does not flag.
- **Time base:** the two field dates only.
- **Absent / null:**
  - A null date on either side: skipped silently.
  - Because of the nesting, **PAIR is also skipped whenever the T1 value is null, 0, NaN or negative, or the T2 value is null**, even when both dates are present and days apart.

### After mode (`qia_check.py:117-150`)
- **Duplicate stamps (line 128):** records are deduplicated on `(backend, stamp)`. When two files share a stamp, the alphabetically first wins and the second is listed as "(same stamp as another file)".
- **Ordering and selection (lines 130-131):** records are sorted by stamp **across backends**. `under[-1]` is "the record at the start" whatever its backend.
- **Which records are checked (line 139):** only `under[-1]` goes through `check_record`. Records stamped during the run are only compared value-by-value (lines 141-147).
- **Output (line 150):** the JSON `data` holds backend, record_at_start, records_during, changes and skipped. **The flags are not in the JSON**; they appear only in the HTML.

## 3. Repo copy (step 3)

- **On this machine:** a search of `C:/Users/Heure` (by filename, directory name, and content `def check_record`) found **no local copy**, only the venv install.
- **In the repo the metadata names:** Source → `github.com/Heuremen-LLC/indahl.ai`, file `code/qia-package/src/qia_check.py` on `main`, last commit `0c41919ae3fe` (2026-11-02T00:18:09Z). I fetched it read-only into `qia_break/repo_copy/`.
- **Result: no mismatch.** The repo copy, the wheel's `qia_check.py` and the sdist's `src/qia_check.py` all hash to `ef38eede…f4ab`, and `diff` is empty for both pairs.
- **TESTED.md:** identical between sdist and wheel.
- **README:** the repo's `code/qia-package/src/README.md` differs from the PyPI README. The repo version is the full-package README (YO, t1t2-check, `python qia_check.py ...` usage); the PyPI version is the pip-only README. That is a doc difference, not a code difference.
- **Small doc nit:** the module docstring (`qia_check.py:27`) says "see LICENSE.txt", but the package ships `LICENSE`.

## 4. Fixtures and how they were run (steps 4, 5)

The plan exists: `drafts/qia-check-break-plan.md`, with 14 items. All 14 are built as P01–P14.

- **Step 5 extras:** E01–E08.
- **Holes found in the source reading, beyond the requested list:** D01–D05, clearly marked as extras.
- **Record shape:** IBM `BackendProperties.to_dict()` saved with `json.dump(..., default=str)`. That means `backend_name`, `backend_version`, `last_update_date`, `qubits` as lists of Nduv `{date, name, unit, value}` in IBM order (T1, T2, frequency, anharmonicity, readout_error, prob_meas0_prep1, prob_meas1_prep0, readout_length), and `gates` with id/sx/x/cz entries carrying `gate_error`/`gate_length`. Dates use the `str(datetime)` form `2026-11-01 12:00:00+00:00` unless a fixture is about date spelling. Units are `us`, and `ns`/`GHz` where IBM uses them.
- **How each case is run:** through the installed console script `qia-check before|after ...` via subprocess. There is no monkeypatching and no import of package internals. The runner reads the report JSON, and the report HTML for after-mode flags, since those are not in the JSON (D05).
- **Clean re-run:** `venv_clean` was built from nothing, installed with `--no-cache-dir --require-hashes`, then `run_all.py` and `build_and_run_repros.py` were run. Both regenerate their outputs from scratch, and both runs gave identical verdicts. The clean run added only D05, which was written between the two runs.

Two notes on the plan:
- **"Q10" is defined two ways.** The plan says Q10 is `init_error`; the task brief describes it as readout_error plus prob_meas* dated older than T1/T2. Both shapes are built (P01 and E08) and both are holes.
- **Field names I could not confirm.** I could not confirm from here that IBM actually publishes a qubit Nduv named `init_error`, or a `zz` gate parameter, in BackendProperties. The fixtures use the plan's names. Neither field is read by qia-check under any name.

## 5. Scores (step 6)

**HOLDS** means the package does what a careful referee requires. **HOLE** means it does not; a silent pass on missing data is always a HOLE. **CANNOT TELL** means this installed package cannot exercise the case.

| id | case | expected (careful referee) | observed (clean venv) | verdict | repro |
|---|---|---|---|---|---|
| P01 | init_error 84 d before stamp, T1/T2 fresh | flag | exit 0, no flags; init_error never loaded (:30, :46) | **HOLE** | R01 |
| P02 | prob_meas0_prep1 97 h older than readout_error | flag | exit 0, no flags | **HOLE** | R01 |
| P03 | stamp 72 h before run, T1 1 h before stamp | flag against run time | before: no flags; after with `--start` = stamp + 72 h: no flags | **HOLE** | R02 |
| P04 | T1 absent / null / NaN; also T1 date null, T1 = 0, T2 NaN, T2 absent | UNKNOWN, not pass | all 7 variant qubits have no row at all; the control qubit reads ABOVE | **HOLE** | R03 |
| P05 | zz = 0.00 on a CZ edge with gate_error 0.0042 | flag as missing | no flags; gates never read | **HOLE** | R05 |
| P06 | T1 age 24h00m00s / 23h59m59s (control 24h00m01s) | document the side | not stale / not stale / STALE. Strict `>`: exactly 24 h is **not** stale. Matches the docs' "more than 24 hours" | HOLDS | n/a |
| P07 | one instant as EDT offset, Z, +00:00, naive; also "EDT" text | identical results; naive refused | offset forms and naive-UTC-wall agree (no flags). Naive EDT wall-clock reads as UTC: **false STALE, 26.0 h** (true age 22 h). `... EDT` text: traceback `ValueError: Invalid isoformat string` | **HOLE** | R06, R07 |
| P08 | readout 1e-17, -0.0, "0", 1/1024 (control 0) | 0 and -0.0 flagged; "0" flagged or refused; shot bound stated | ZERO: 1e-17 no, -0.0 yes, **"0" no**, 1/1024 no, 0 yes. No shot bound stated anywhere | **HOLE** | R08 |
| P09 | T2/T1 = 2.0, 2.0000001, 2.5, 2.5000001, plus two decimal-exact 2.5 | OK / CT / CT / ABOVE / CT / CT | OK / CT / CT / ABOVE / **ABOVE** / CT. The plan's four hold. 0.0003085/0.0001234 = 2.5000000000000004 reads ABOVE while the detail prints "ratio 2.500" | **HOLE** (float edge) | R10 |
| P10 | T1 and T2 exactly 24 h apart; ±1 s | document the side | 24h00m00s no PAIR; 24h00m01s PAIR; 23h59m59s no PAIR. Matches "more than 24 hours apart" | HOLDS | n/a |
| P11 | run 12:00–12:40 spans a 12:20 restamp | both records surfaced | record_at_start 11:00, records_during [12:20], q0 T1 change 152.3 → 97.4 listed, 13:00 excluded | HOLDS | n/a |
| P12 | stamp moved +0 / +12 / +36 h, values and dates frozen (Q6) | age grows with the stamp, not the run | STALE = F / F / T. The same frozen dates go 1 → 13 → 37 h old because only the stamp moved. After mode shows "Records stamped during the run: 1" with an empty change table; nothing says the stamp moved with no new figures | HOLDS (as the plan expects; the root issue is P03) | n/a |
| P13 | k/1024 values written rounded (0.00293) | shot count must not flip to 4096 | qia-check 1.0.0 does no shot or grid inference at all (no "shot" in 153 lines; report silent) | CANNOT TELL | n/a |
| P14 | YO vs code on 23h59m59s and 1e-17 | page shows code as authoritative | YO is not in the PyPI package (TESTED.md: "Not yet tested inside this package: the YO reader"). Code answer recorded: 23h59m59s not STALE, 1e-17 not ZERO | CANNOT TELL | n/a |
| E01 | malformed JSON: truncated, trailing comma, list top-level, no `last_update_date` | clean refusal; bad file named in after mode | exit 1, "… is not a calibration record (Qiskit BackendProperties JSON)", no report. After mode lists `bad.json` under "Not read as records" | HOLDS | n/a |
| E02 | `qubits: []`; a qubit with an empty property list | refuse or UNKNOWN | exit 0, "Qubits checked: 0. Flags (0) Nothing flagged." With `--qubits 0,1` it notes "Not in this record", still exit 0 and clean. An empty qubit block is counted in "Qubits checked: 2" | **HOLE** | R04 |
| E03 | duplicate T1 entries, conflicting date or value | flag the conflict; result independent of order | stale-first gives no flags; stale-last gives STALE + PAIR. T1 150 then 210 with T2 400 reads clean (150 alone would be ABOVE) | **HOLE** | R11 |
| E04 | negative T1 (−150.2 us) with T2 400 | flag impossible value; PAIR still evaluated | q0: no rows. q1 (dates 30 h apart): STALE only, **PAIR suppressed** | **HOLE** | R03 |
| E05 | T1 s/ms vs T2 us | normalise or refuse | q0 (true ratio 0.79): **false ABOVE**. q1 (true 2.66): **no flag**. q2: ABOVE by accident (ratio ≈ 2,663) | **HOLE** | R12 |
| E06 | string-typed numbers | coerce, or refuse cleanly | T1/T2 strings: traceback `TypeError: '>' not supported between 'str' and 'int'`, no report. Readout `"0.0"` and p01 `"0"`: silent pass. T2 `"400.0"`: traceback `TypeError` at `/` | **HOLE** | R08, R09 |
| E07 | leap second; DST fall-back | parse or refuse cleanly; true age wins | `23:59:60` in T1 date: traceback `ValueError: second must be in 0..59`. In the stamp: misreported as "not a calibration record". DST with offsets: STALE correctly at 24.5 h (wall clock 23.5 h). That part holds. DST as naive wall clocks: **missed** (read as 23.5 h) | **HOLE** | R07, R06 |
| E08 | readout_error / prob_meas0_prep1 / prob_meas1_prep0 dated 84 d before fresh T1/T2 (the Q10 shape) | flag | exit 0, no flags | **HOLE** | R01 |
| D01 | T1 null or negative, T1/T2 dates 30 h apart | PAIR | PAIR: null no, negative no, control yes | **HOLE** | R03 |
| D02 | after-mode folder with kingston 11:00 + fez 11:50 | per-backend, or refuse | "record in force" = **ibm_fez 11:50**, checked against kingston `--qubits` | **HOLE** | R13 |
| D03 | record stamped mid-run has readout 0 and a 60 h stale T1 | flagged | no ZERO and no STALE. It shows only as an unlabelled value change 0.0122 → 0 | **HOLE** | R14 |
| D04 | two files, same stamp, different contents | conflict reported | a.json wins by filename; b.json (50 h stale T1 of 41 us) is listed as "(same stamp as another file)" and never checked | **HOLE** | R15 |
| D05 | after-mode JSON vs HTML | same flags in both | HTML has 4 flag rows; the JSON has no `flags` key | **HOLE** | R16 |

**Totals: 5 HOLDS, 20 HOLE, 2 CANNOT TELL.**

Per-fixture command lines, exit codes and stderr are in `fixtures/results/results.json`; the short table is `results.md`.

**On the 0-of-1024 bound (P08).** A published 0 read from 1024 shots still allows a true error up to 1 − 0.05^(1/1024) = **0.292 %** at 95 % one-sided confidence. 1/1024 = 0.0977 % is the smallest nonzero value on that grid. Values such as 1e-17 cannot come from any 1024, 4096 or 8192-shot count. The package says none of this. It flags "exactly 0" as documented, so I report 1e-17 as a spec gap and did not score it; the HOLE on P08 rests on the string `"0"` passing silently.

## 6. Holes: minimal reproducers and proposed fixes

Every `fixtures/repros/R*.py` is standalone, 15 lines or fewer including its header, and drives the installed `qia-check` that sits next to the python running it. Its last output line is `HOLE`. All 16 printed HOLE in the clean venv.

The shared header for before-mode repros (included at the top of each file):
```python
import json, subprocess, glob, tempfile, os, sys
d = tempfile.mkdtemp(); X = os.path.join(os.path.dirname(sys.executable), 'qia-check')
N = lambda n, v, t, u='': {'name': n, 'value': v, 'date': t, 'unit': u}
R = lambda qs, s='2026-11-01T12:00:00Z', b='ibm_kingston': {'backend_name': b, 'last_update_date': s, 'qubits': qs}
def before(rec):
    p = os.path.join(d, 'r%d.json' % len(os.listdir(d))); json.dump(rec, open(p, 'w')); o = p + '_out'
    r = subprocess.run([X, 'before', p, '--out', o], capture_output=True, text=True)
    return r.returncode, (r.stderr.strip().splitlines() or [''])[-1][:110], (json.load(open(glob.glob(o + '/*.json')[0]))['flags'] if r.returncode == 0 else None)
```
After-mode repros (R13–R16) swap `before()` for an `after(recs, start, end)` that writes a folder and runs `qia-check after` (see the files). Bodies follow.

**R01: readout-family dates are never aged (P01, P02, E08: the Q10 shape).** 13 lines.
```python
F = '2026-11-01T09:00:00Z'; OLD = '2026-08-09T12:00:00Z'   # 84 d before the stamp
q = [N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us'), N('readout_error', 0.012, OLD),
     N('prob_meas0_prep1', 0.015, OLD), N('prob_meas1_prep0', 0.009, OLD), N('init_error', 0.003, OLD)]
rc, err, fl = before(R([q])); print('flags:', fl)          # flags: []
```
*Fix.* Age every dated figure the record uses, not just T1 and T2. Run STALE over `T1, T2, readout_error, prob_meas0_prep1, prob_meas1_prep0`, and over `init_error` and any other qubit Nduv the site's claims rely on (keep a list in one place, and make line 30 load it). Add a FAMILY check: within one qubit, flag when readout_error, prob_meas0_prep1 and prob_meas1_prep0 dates differ by more than the threshold, since those three are meant to be one readout calibration (Q11). The report should name the oldest figure and its age, so a clean T1/T2 cannot vouch for a stale readout.

**R02: staleness ignores the run time (P03; P12 is the same root).** 11 lines.
```python
T = '2026-11-01T11:00:00Z'   # 1 h before the stamp; the stamp is days old when you run this
rc, err, fl = before(R([[N('T1', 150.0, T, 'us'), N('T2', 120.0, T, 'us')]]))
print('flags:', fl)          # flags: []
```
*Fix.* Give STALE a reference time separate from the stamp. In after mode use `--start`, and also check against `--end`. In before mode use `--run-at` if given, else the check time `now`. Report two ages: "age at stamp" (today's number) and "age at run". Flag STALE-AT-RUN when the run-time age passes 24 h, even if the stamp age does not. Move the meta line at :112 from prose into a flag when the record itself is more than 24 h older than the run.

**R03: silent pass on missing, null, NaN or negative values, and PAIR hidden behind the value guard (P04, E04, D01).** 14 lines.
```python
F = '2026-11-01T09:00:00Z'
qs = [[N('T2', 120.0, F, 'us')], [N('T1', None, F, 'us'), N('T2', 120.0, F, 'us')],
      [N('T1', float('nan'), F, 'us'), N('T2', 120.0, F, 'us')],
      [N('T1', -150.0, '2026-10-31T06:00:00Z', 'us'), N('T2', 400.0, F, 'us')]]   # q3 T1/T2 dates 27 h apart
rc, err, fl = before(R(qs)); print('flags:', fl)   # only q3 STALE; nothing on q0-q2; no PAIR on q3
```
*Fix.* Introduce an explicit UNKNOWN outcome. For each check and each qubit, if a required field is absent, its value is None, non-finite (`math.isfinite`), non-numeric, or out of physical range (T1 or T2 ≤ 0, error outside [0, 1]), or its date is missing, emit a row `check=<X>, outcome=UNKNOWN, detail=<why>` rather than skipping. Pull PAIR out of the line-57 value guard so it depends only on the two dates. Make the summary count UNKNOWN separately ("N flags, M unknown") and exit nonzero, or print a banner, whenever any UNKNOWN exists. The page should then say "not checked" rather than "Nothing flagged".

**R04: an empty record passes (E02).** 10 lines.
```python
rc, err, fl = before(R([])); print('exit', rc, 'flags:', fl)   # exit 0 flags: []
```
*Fix.* Refuse a record with zero qubits ("record has no qubits; nothing was checked", exit nonzero). Count a qubit as "checked" only if it has at least one of the five fields; list qubits with none as UNKNOWN. With `--qubits`, if any requested qubit is missing, make that a flag rather than only a meta line.

**R05: gates and zz are never read (P05).** 12 lines.
```python
F = '2026-11-01T09:00:00Z'; rec = R([[N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us')]] * 2)
rec['gates'] = [{'gate': 'cz', 'qubits': [0, 1], 'name': 'cz0_1', 'parameters': [N('gate_error', 0.0042, F), N('zz', 0.0, F, 'kHz')]}]
rc, err, fl = before(rec); print('flags:', fl)   # flags: []
```
*Fix.* Either bring edges into scope or say plainly that they are out of scope. In scope means: load `gates`; for every 2-qubit gate with a calibrated `gate_error`, check that the companion parameters the site cites (zz, if IBM publishes it under that name; I could not confirm the name) are present, nonzero and dated. Treat 0.00 alongside a live gate_error as "missing, published as 0", with ZERO and STALE on edge parameters too. Out of scope means: state in the README and report footer that two-qubit and edge figures are not checked, so no page cites qia-check for Q7.

**R06: a naive time is silently read as UTC (P07, E07 DST naive).** 12 lines.
```python
a = before(R([[N('T1', 150.0, '2026-10-31T10:00:00-04:00', 'us'), N('T2', 120.0, '2026-10-31T10:00:00-04:00', 'us')]]))[2]
b = before(R([[N('T1', 150.0, '2026-10-31T10:00:00', 'us'), N('T2', 120.0, '2026-10-31T10:00:00', 'us')]]))[2]
print(a, b)   # [] vs [STALE T1 26.0 h, STALE T2 26.0 h]: same instant, different answer
```
*Fix.* Apply the CLI's own rule (:94) to record times too. In `when()`, if the parsed time has no tzinfo, do not assume UTC. Either refuse it with a clear message, or accept it only under an explicit `--assume-utc` flag, and mark every affected row "time zone assumed". Report the count of naive timestamps in meta either way.

**R07: an unparseable date gives a traceback (P07 "EDT", E07 leap second).** 11 lines.
```python
for t, s in (('2016-12-31T23:59:60Z', '2017-01-01T06:00:00Z'), ('2026-10-31T10:00:00 EDT', '2026-11-01T12:00:00Z')):
    rc, err, fl = before(R([[N('T1', 150.0, t, 'us'), N('T2', 120.0, s, 'us')]], s=s)); print(rc, err)
# 1 ValueError: second must be in 0..59 / 1 ValueError: Invalid isoformat string: '... EDT'
```
*Fix.* Parse every field date once, in `load()`, inside its error handling. A field date that does not parse becomes UNKNOWN for that field with the raw string shown; it must not abort the whole run. For `:60`, either clamp to `:59.999999` with a note or refuse cleanly. When the stamp is what fails to parse, report "last_update_date could not be read: '<raw>'" rather than "not a calibration record".

**R08: a string zero passes ZERO (P08, E06).** 11 lines.
```python
F = '2026-11-01T09:00:00Z'; q = [N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us'), N('readout_error', '0', F), N('prob_meas0_prep1', '0.0', F)]
rc, err, fl = before(R([q])); print('flags:', fl)   # flags: []
```
*Fix.* Validate types in `load()`. A value that is not an int or float (bool excluded) gets one of two treatments. Either coerce it with `float()` and add a "value was a string" note to every row for that field, or mark it UNKNOWN; never compare it raw. ZERO should then use `v == 0.0` on the coerced float. Separately, flag values below the shot-grid resolution (for example 0 < v < 1/8192) as "not a possible shot-count estimate".

**R09: string numbers crash (E06).** 11 lines.
```python
F = '2026-11-01T09:00:00Z'; rc, err, fl = before(R([[N('T1', '150.0', F, 'us'), N('T2', '120.0', F, 'us')]]))
print(rc, err)   # 1 TypeError: '>' not supported between instances of 'str' and 'int'
```
*Fix.* Same `load()` validation as R08. As a backstop, wrap `check_record` per qubit, so one bad qubit becomes UNKNOWN with the exception text and the rest of the record is still checked and reported.

**R10: float edge at 2.5 (P09).** 11 lines.
```python
F = '2026-11-01T09:00:00Z'; rc, err, fl = before(R([[N('T1', 0.0001234, F, 's'), N('T2', 0.0003085, F, 's')]]))
print('flags:', fl)   # outcome ABOVE while detail prints 'ratio 2.500'
```
*Fix.* Compare the ratio against the band edges with a tolerance that matches the published precision. For example, `r > 2.5 * (1 + 1e-9)` for ABOVE (and the same at 2.0), or compute in `decimal.Decimal(str(v))` so decimal-exact ratios stay exact. Print enough digits that the detail cannot contradict the outcome (`ratio 2.5000000000000004`, or `≈2.5 (at edge)`).

**R11: duplicate entry, last one wins (E03).** 13 lines.
```python
F = '2026-11-01T09:00:00Z'; OLD = '2026-10-30T12:00:00Z'   # 48 h before the stamp
a = before(R([[N('T1', 150.0, OLD, 'us'), N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us')]]))[2]
b = before(R([[N('T1', 150.0, F, 'us'), N('T1', 150.0, OLD, 'us'), N('T2', 120.0, F, 'us')]]))[2]
print(a, b)   # [] vs [STALE, PAIR]: same data, order swapped, opposite answer
```
*Fix.* In `load()`, collect every Nduv per (qubit, name). If a name appears more than once with differing value, date or unit, emit a DUPLICATE flag listing all of them and mark the field UNKNOWN for the other checks. If the copies are identical, keep one and add a note. The answer must not depend on list order.

**R12: units are ignored (E05).** 11 lines.
```python
F = '2026-11-01T09:00:00Z'; rc, err, fl = before(R([[N('T1', 150.2, F, 'us'), N('T2', 0.0004, F, 's')]]))   # T2 = 400 us = 2.66 x T1
print('flags:', fl)   # flags: [] (the reverse mix gives a false ABOVE at ratio ~790,000)
```
*Fix.* Normalise T1 and T2 to seconds before the ratio, using the stored unit (`s`, `ms`, `us`/`µs`, `ns`). An unknown or empty unit becomes UNKNOWN. Show the normalised values in the detail. Optionally add a sanity range on T1 and T2 (for example 1 µs to 10 ms) that flags values that look like a unit slip even when the units agree.

**R13: after mode mixes backends (D02).** 14 lines.
```python
F = '2026-11-01T09:00:00Z'; q = [[N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us')]]
j, h = after({'k.json': R(q, '2026-11-01T11:00:00Z'), 'f.json': R(q, '2026-11-01T11:50:00Z', 'ibm_fez')},
             '2026-11-01T12:00:00Z', '2026-11-01T12:40:00Z')
print('record in force:', j['backend'], j['record_at_start'])   # ibm_fez 11:50, checked as if it were the run's
```
*Fix.* Group records by `backend_name` before sorting. Require `--backend`, or refuse when the folder holds more than one backend ("records from ibm_fez, ibm_kingston: pass --backend"). Print the chosen backend at the top of the report.

**R14: a mid-run record is listed but not checked (D03).** 15 lines.
```python
F = '2026-11-01T09:00:00Z'; ok = [[N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us'), N('readout_error', 0.012, F)]]
bad = [[N('T1', 150.0, '2026-10-29T12:00:00Z', 'us'), N('T2', 120.0, F, 'us'), N('readout_error', 0.0, F)]]
j, h = after({'a.json': R(ok, '2026-11-01T11:00:00Z'), 'b.json': R(bad, '2026-11-01T12:20:00Z')},
             '2026-11-01T12:00:00Z', '2026-11-01T12:40:00Z')
print('ZERO' in h, 'STALE' in h)   # False False
```
*Fix.* Run `check_record` on every record in `during` as well as `under[-1]`, with its own section per record. Part of the run executed under each of those records, so their ZERO, STALE and T2>2T1 flags apply to it.

**R15: same-stamp conflict is resolved by filename (D04).** 15 lines.
```python
F = '2026-11-01T09:00:00Z'; good = [[N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us')]]
bad = [[N('T1', 41.0, '2026-10-30T10:00:00Z', 'us'), N('T2', 120.0, F, 'us')]]
j, h = after({'a.json': R(good, '2026-11-01T11:00:00Z'), 'b.json': R(bad, '2026-11-01T11:00:00Z')},
             '2026-11-01T12:00:00Z', '2026-11-01T12:40:00Z')
print(j['skipped'], 'STALE' in h)   # ['b.json (same stamp as another file)'] False
```
*Fix.* When two files share `(backend, stamp)`, compare their loaded figures. If they are identical, keep one and note the duplicate. If they differ, raise a CONFLICT flag naming both files and every differing field, and check both. Never resolve the conflict by sort order.

**R16: the after-mode JSON has no flags (D05).** 12 lines.
```python
OLD = '2026-10-30T10:00:00Z'; q = [[N('T1', 150.0, OLD, 'us'), N('T2', 120.0, OLD, 'us')]]
j, h = after({'a.json': R(q, '2026-11-01T11:00:00Z')}, '2026-11-01T12:00:00Z', '2026-11-01T12:40:00Z')
print('STALE in html:', 'STALE' in h, '| flags key in json:', 'flags' in j)   # True | False
```
*Fix.* Add `flags=check_record(S, Q, qs)` (and the per-record flags from R14) to the after-mode `data` dict at :150, so the machine-readable report matches the HTML. Add a test asserting that the HTML rows equal the JSON rows for both modes.

## 7. Ranking (step 7)

Holes are ordered by how likely an outside user is to hit them first, weighted by how badly each would mislead a published claim ("qia-check found nothing", cited as a clean bill).

| rank | hole (repro) | likely to hit first | how badly it misleads | why |
|---|---|---|---|---|
| 1 | Readout-family dates never aged (R01; P01, P02, E08) | **very high**: every real IBM record dates its readout figures separately from T1/T2 | **high** | A clean report reads as "the record's figures are current" while the readout error a paper cites for mitigation can be weeks old. This is the Q10 shape exactly. |
| 2 | Staleness pinned to the stamp, run time ignored (R02; P03, P12) | **very high**: save once, run later; or check an archived record | **high** | "No STALE" is read as "fresh for my run". The record can be days old at run time and the tool never says so except in a prose meta line. |
| 3 | Silent pass on missing / null / NaN / 0 / negative, PAIR hidden (R03; P04, E04, D01) | **high**: degraded or unusual qubits in a record are exactly the ones whose fields look odd | **high** | "Nothing flagged" on a qubit with no usable T1 is the worst possible output for a referee. There is no UNKNOWN to read. |
| 4 | After-mode JSON has no flags (R16; D05) | **medium-high**: anyone scripting or archiving the JSON | **high** | Machine-readable output says zero flags while the HTML shows them. A pipeline that counts `flags` gets a clean result every time. |
| 5 | Empty record / empty qubit passes (R04; E02) | medium: a bad save, a filtered dump, or a wrong `--qubits` | high | Exit 0 with "Nothing flagged" when nothing was checked. |
| 6 | Mid-run record unchecked (R14; D03) | medium: any run that straddles a recalibration | medium-high | The run's own second record can carry a ZERO or stale T1 that appears only as an unlabelled value change. |
| 7 | Mixed backends in after mode (R13; D02) | medium: people keep one "records/" folder | high when hit | The wrong backend's record is named as "the record in force". |
| 8 | Gates / zz not read (R05; P05) | depends on what the site claims | high *if* any page cites qia-check for Q7 | Not a bug in what the package claims to do, but a coverage gap against the plan. |
| 9 | Units ignored (R12; E05) | low-medium: IBM `to_dict` uses `us`, but users convert, and other tools write seconds | high when hit | Produces both false ABOVE and missed ABOVE. |
| 10 | Duplicate entries, last wins (R11; E03) | low: merged or hand-built records | high when hit | The same data gives opposite answers depending on order. |
| 11 | String zero passes ZERO (R08; P08, E06) | low: `default=str` stringifies datetimes, not floats; CSV or hand-edits do | medium | A silent miss on the one exact-zero check. |
| 12 | Naive time silently UTC (R06; P07, E07) | low: IBM writes offsets | medium | A false STALE or missed STALE, up to the local UTC offset. |
| 13 | Same-stamp conflict by filename (R15; D04) | low | medium | It is surfaced as "skipped", but the conflicting figures are never checked. |
| 14 | Float edge at 2.5 (R10; P09) | low: needs a decimal-exact 2.5 | low-medium | CANNOT_TELL reported as ABOVE, with a detail that prints 2.500. |
| 15 | String numbers crash (R09; E06) | low | low | Loud traceback, no report. Nothing is misleading, it is just unusable. |
| 16 | Unparseable date crash (R07; P07, E07) | very low: IBM does not emit `:60` or zone names | low | Loud traceback. The leap-stamp case is mislabelled "not a calibration record". |

## 8. What I could not test, and what is not scored HOLDS

- **P13 (grid / shot count) and P14 (YO vs code):** CANNOT TELL. That logic is not in the PyPI package. They need the full package from indahl.ai/qia/package (YO, `yo/yo_audit.py`), which I did not install because the brief was the PyPI package. The code-side answers for P14 are recorded above, ready for when YO can be run.
- **Python 3.9 / 3.10:** only 3.13.13 is installed here. `fromisoformat` is much stricter before 3.11: some fractional-second and other date spellings that 3.13 accepts would raise on 3.9 or 3.10 and become tracebacks via R07. The package claims `requires-python >=3.9`, so this is worth a run on 3.9 before any claim of support.
- **Non-dict Nduv entries** (for example a bare string inside a qubit list): from the source, `x.get` at :46 would raise AttributeError, which `main` does not catch (:110). I did not build a fixture for this.
- **Field names:** I did not verify that IBM BackendProperties publishes `init_error` or `zz` under those names. The P01 and P05 verdicts hold regardless, because qia-check reads neither field under any name.
- **What `TESTED.md` actually establishes:** its own text says the mirror comparison "shows the two implementations agree. It does not test the rules themselves." Every hole above is in the rules, so that testing could not have caught them.

## 9. VERDICTs for Bones

- VERDICT 1 (R01, Q10): HOLE. Readout-family and init_error dates are never aged. A clean report is not evidence that readout figures are current.
- VERDICT 2 (R02, staleness base): HOLE. STALE is measured against the record's own stamp, never against the run.
- VERDICT 3 (R03 + R04, silent pass): HOLE. Missing, null, NaN, zero or negative fields and empty records give "Nothing flagged" with exit 0. There is no UNKNOWN.
- VERDICT 4 (R16): HOLE. After-mode JSON carries no flags.
- VERDICT 5 (R14, R13, R15): HOLE. After mode does not check mid-run records, mixes backends, and resolves same-stamp conflicts by filename.
- VERDICT 6 (R05): HOLE, or out-of-scope. Gates and zz are not read; either scope them in or say so on every page that cites the tool.
- VERDICT 7 (R12, R11, R08, R06): HOLE. Units, duplicates, string zeros and naive times all give wrong-but-quiet answers.
- VERDICT 8 (R10, R09, R07): HOLE, low. Float edge at 2.5; tracebacks on string numbers and unparseable dates.
- HOLDS: P06 and P10 (24 h boundaries are strict `>`, consistent with the docs), P11 (restamp surfaced), P12 (age follows the stamp, as the plan expected), E01 (malformed JSON refused cleanly).
- CANNOT TELL: P13, P14 (not in the PyPI package), and Python 3.9/3.10 behaviour.

## Files

- **This report:** `C:/Users/Heure/sage_workshop/drafts/qia-check-break-report.md`
- **Fixtures generator:** `C:/Users/Heure/sage_workshop/qia_break/fixtures/make_fixtures.py`. It writes `fixtures/data/` (52 JSON files across P01–P14, E01–E08, D01–D04).
- **Runner:** `C:/Users/Heure/sage_workshop/qia_break/fixtures/run_all.py`. Usage: `python run_all.py --venv ../venv_clean`. It writes `fixtures/results/results.json`, `results.md` and `reports/run*/`.
- **Reproducers:** `C:/Users/Heure/sage_workshop/qia_break/fixtures/repros/R01…R16_*.py`, plus `build_and_run_repros.py`, which writes and runs them all.
- **Provenance:** `C:/Users/Heure/sage_workshop/qia_break/provenance.txt` (hashes, `pip show -f`, interpreter) and `qia_break/pinned.txt` (the hash-pinned requirement).
- **Downloaded artifacts:** `qia_break/dl/` (wheel and sdist), `qia_break/sdist/` (unpacked), `qia_break/repo_copy/` (read-only fetch of the GitHub source and README).
- **Venvs:** `qia_break/venv` (first run) and `qia_break/venv_clean` (the clean re-run these results come from).
