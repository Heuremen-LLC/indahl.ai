# qia-check 1.0.1 DRAFT: fixes against Sage's break report (4 Nov). NOT PUBLISHED; PyPI waits for Wayfinder's word.
Reproducers run in a clean venv against the draft, two ways: raw (run time = now) and with the run time pinned to the fixtures' stamp
(a shim adds --at 2026-11-01T12:00:00Z), because the new default ages every figure against the run time and would turn any 1 Nov fixture STALE.
R01 readout family + init_error never aged ........ FIXED (every field read is aged)
R02 staleness against the stamp only .............. FIXED (--at RUN_TIME, default now; both ages printed). Pinned run shows HOLE by construction.
R03 silent on missing/null/NaN/negative ........... FIXED (UNKNOWN rows; PAIR read independently of the T1 value)
R04 empty record passes ........................... FIXED (exit 2 when no qubit is checked; empty qubit -> UNKNOWN)
R05 gates and zz never read ....................... OUT OF SCOPE, stated in the docstring, every report's meta and footer
R06 naive time read as UTC ........................ REFUSED: a zoneless date is UNKNOWN, never aged. Sage's repro checks "naive == offset", which a
                                                    refusal cannot meet; the behaviour is her stated requirement ("naive refused").
R07 unparseable date traceback .................... FIXED (UNKNOWN row; leap second :60 read as :59 + 1 s)
R08 string zero passes ZERO ....................... FIXED ("0", 0, -0.0 -> ZERO; 0-of-1024 bound stated in the docstring)
R09 string numbers crash .......................... FIXED (numeric strings read as numbers)
R10 float edge at 2.5 ............................. FIXED (1e-9 relative tolerance at 2.0 and 2.5)
R11 duplicate entry, last wins .................... FIXED (conflicting duplicates -> UNKNOWN, none used)
R12 units ignored ................................. FIXED (ns, us, ms, s normalised to us; unknown unit -> UNKNOWN)
R13 after mode mixes backends ..................... REFUSED: a mixed folder exits 1 (refused) unless --backend names one (repro raises, by design)
R14 mid-run record unchecked ...................... FIXED (records stamped during the run get the same checks)
R15 same-stamp conflict by filename ............... FIXED (both checked, CONFLICT in meta and JSON)
R16 after JSON has no flags ....................... FIXED (flags key)
Not yet done: Sage's full 27-fixture runner against the draft; README/TESTED.md text for 1.0.1; the indahl.ai package page.

## Round 2 (Sage's scoring 03:22Z: 22 HOLDS / 2 HOLE / 3 CANNOT TELL; her VERDICTs H1, H2, P05, H3) -> src sha256 115e1d68...
H1 no record before --start: backend refusal and during-run checks now run in every branch; during-run records are named and checked.
   Her repro extra/h1: b_1220.json flagged STALE T1, ZERO readout_error, PAIR on q1; meta names the record. extra/mix: refused, exit 1.
H2 zoneless record stamp: refused (same rule as field dates). extra/naive_stamp.json: refused, exit 1, with the reason.
P05 wording: "Nothing flagged in the fields this package reads (gates and zz are not read)."
H3 1e-17: new TINY row for a nonzero error below 1e-6 ("no count of up to 1,000,000 shots can give"). Spec call for Wayfinder: threshold.
New, from her unscored note: FUTURE row when a figure is dated after its record's stamp.
Regression: her 16 repros raw/pinned unchanged from round 1; her 27-fixture runner (1.0.0-era scorer) unchanged at 15/10/2.

## Round 3 (Sage round-2 scoring 03:36Z: 24 HOLDS / 0 HOLE / 3 CANNOT TELL; new items N1-N5) -> src sha256 fb754d02...
N1 the after page always prints "Records stamped during the run: N" (0 included).
N2 an empty changes table reads "No figure changed between records in the run window." (not the page-level "Nothing flagged").
N3 TINY prints the value exactly (repr).
N4 FUTURE on real data: 0 FUTURE rows across 572 real ibm_kingston records (362 in qia_package/test/recs, 210 in qia_mirror/records).
   Same scan, honest UNKNOWN on real data: IBM publishes some qubits with no T1/T2 at all (kingston qubit 146 in all 362 records; 148 more T2 gaps).
   1.0.0 passed those silently.
N5 a negative error value is UNKNOWN ("not a usable error rate").
Spec call for Wayfinder, open: the TINY threshold (1e-6 catches 1e-17, not 1e-5 or 1e-4, which a 1024-shot estimate also cannot give).
Note: the runner's built-in verdict strings are tuned to 1.0.0; its 15/10/2 says nothing about 1.0.1. Sage's scoring of the output is the reading.
Regression: 16 repros unchanged.

## Round 3b (Sage usability note 03:49Z) -> src sha256 93455adc...
Every page opens with "N flag(s), M UNKNOWN"; real flags sort above UNKNOWN rows (before and after). Repros unchanged.

## Round 5b (Sage round-5 VERDICT 04:09Z STANDS with fixes) -> src/qia_check.py sha256 c6da3f6b...
r3b promoted to src/qia_check.py (the .r3b side file and __pycache__ removed). Header: "N flag row(s), M UNKNOWN (figures, qubits or entries that could not be read: absent, unusable, zoneless or conflicting)". A page where nothing was checked leads with "NO RECORD WAS CHECKED ... This page is not a pass." (after) or "NO QUBIT WAS CHECKED" (before), and its flags section reads "Nothing was checked: there is no record to read." CONFLICT: two same-stamp records at the start both count toward the "fewer than two records" test. Repros unchanged.

## Round 6b (Sage round-6 VERDICT 04:18Z MOVES) -> src/qia_check.py sha256 44172347...
CONFLICT: same-stamp records at the start are compared to each other; their differences are listed ("CONFLICT a.json vs b.json"). Before mode: the flags section under NO QUBIT WAS CHECKED reads "Nothing was checked: no qubit to read." After mode: a record read with no qubit checked (e.g. --qubits 99) leads with NO QUBIT WAS CHECKED and exits 2, like before mode. Repros unchanged. README and TESTED.md not yet updated for 1.0.1.

## Round 7b (Sage round-7 VERDICT 04:33Z STANDS: three behaviour changes went in unlisted in 6b) -> src/qia_check.py sha256 dc7e7525...
Listed now, all from 6b: (1) an after page with no record checked exits 2 (was exit 0); (2) the stderr text is "NOTHING WAS CHECKED: this report
is not a pass (exit 2)" for both modes; (3) the during-run baseline moved from in_force[0] to in_force[-1] (alphabetically last same-stamp record).
7b replaces (3): with a CONFLICT at the start the run-window records are compared against EACH same-stamp record, labelled "(from b.json)".
No-change line: "No figure changed between records in the run window (in the fields read)."
Baseline fixture: tests/baseline_conflict/ (a.json T1 150 and b.json T1 41 share the 11:00 stamp; d.json T1 150 at 12:20). Output: the
CONFLICT row (a vs b, T1 150 -> 41) and one change "12:20 (from b.json) T1 41 -> 150"; nothing from a.json, where T1 did not change. Repros unchanged.

## Round 7c (Sage round-8 README check 04:58Z: 87 claims TRUE, 2 FALSE) -> src sha256 106abc5c...
FALSE 1 fixed in code: an error figure with no date is UNKNOWN ("no measurement date, so its age cannot be checked"), never silently un-aged.
FALSE 2 fixed in code: the changes table compares value, date AND unit, so a unit-only change (T1 100 us -> 100 ns) is listed.
New: --pull given with a record prints a note that it is ignored. Before mode refuses an --out folder that is the record's own folder.
README: exit codes 0/1/2, folder rules, skipped files, and what a clean page means. Repros unchanged.

## Round 7d (Sage round-9 defects + her 7c asks, 05:11Z) -> src sha256 c237b0aa... (CORRECTED 05:5xZ: this header first said cf10f034, the pre-narrowing build; Sage round 11 caught it)
Doubled rows fixed: agreeing same-stamp records count once; per-base comparison only on a real CONFLICT (differing contents).
False label fixed: only the FIRST during-run record is compared to the base(s); later ones are compared once to the record before them, labelled "(from d1.json)".
Unit equivalence: T1/T2 normalised to us for comparison; 100 us -> 0.1 ms is listed as "(unit only, same value)"; 100 us -> 100 ns is a change.
--out refusal in before mode resolves the path: the record's own folder is refused however it is written (exact, trailing slash, sub/.., a symlink; tested, exit 1). A SUBFOLDER is allowed: after mode reads only the folder's top level, so a report there is never read as a record. (A first 7d refused subfolders too; that broke every before-mode repro, which writes its report beside the record, and was narrowed before sending.) After mode already refuses --out inside the records folder.
Repros unchanged.

## Round 7e (Sage round-11 VERDICT 05:46Z MOVES) -> src/qia_check.py sha256 5edeaa41c08ea5c1...
1. After-mode crashes fixed: a directory named x.json, an unopenable file and an out-of-range stamp (9999 with offset) are skipped and named
   with the reason (tested: rc 0, the good record read). CORRECTED 06:1xZ (Sage round 12): a numeric backend_name is NOT skipped; it is read as
   the backend name "5", so beside ibm_kingston records the folder is refused as mixed (rc 1) unless --backend picks one. sha() moved inside the try; OverflowError and TypeError caught.
2. "Doubled rows": two same-stamp records conflict only if their FIGURES differ (value, date, unit per field per qubit), not their bytes;
   a byte-different, figure-identical pair counts once (tested).
3. After mode: a subfolder of the records folder is allowed as --out (only the top level is read); the records folder itself is refused.
4. "unit only, same value" is printed only when both units are known and the values agree to 1e-9 relative; "100 furlongs" is a plain change (tested).
5. The 7d header hash is corrected above.
6. Before mode: a file-symlink record is resolved before its folder is compared (tested: refused). The runner's P11 string match is the
   runner's, not the package's; not changed.
Repros unchanged (16; R15 broke once in this round on a helper defined late, fixed before sending).

## Round 7f (Sage round-12 VERDICT 06:05Z MOVES) -> src/qia_check.py sha256 146525b8a550d495...
These named tracebacks are closed (each tested; this is a list of kinds, not a claim that no input can crash): a leap-second 9999 stamp (before mode: clean refusal rc 1); a 9999 --start/--end/--at (clean
refusal); a unit that is a list or dict (UNKNOWN "unknown unit '?list'"); a deeply nested file (clean refusal, or skipped in after mode); a
missing file or directory as the before-mode record (clean refusal). Conflicts: numbers compared as numbers, so JSON 100 vs 100.0 is not a
conflict. Identical start records give their flag rows once. ZERO and TINY now also cover init_error. A T1/T2 with no unit key is UNKNOWN
("no unit given"); an error figure with a unit other than blank or % is UNKNOWN; % is read as a fraction. An after page with UNKNOWN rows says
"UNKNOWN is not a pass" (as before mode). Dead norm() removed. FIXES: the numeric-backend claim corrected; four stale c237b0aa suffixes removed.
README: exit codes, subfolders, zoneless skip in after mode, "figures" not "contents", and a clean page = 0 flag rows AND 0 UNKNOWN rows.
Real data: 576 ibm_kingston records under 7f give no new UNKNOWN kind (only "absent from the record"). Repros unchanged. Not changed: the
runner's P11 string match (the runner's, not the package's), --pull and Python 3.9 (not tested here either).

## Round 7g (Sage round-13 VERDICT 06:27Z MOVES: items 1, 2, 3, 6, 8) -> src/qia_check.py sha256 28f8a36f...
1. Silent loss closed: report file names are made safe (any character outside A-Z a-z 0-9 . _ - becomes _), so a backend_name with : / NUL or a
   lone surrogate writes its report (tested: rc 0, 2 report files). An --out that is an existing file or cannot be created is refused (rc 1).
2. CONFLICT rows, change rows and the conflict list all use one figure test (value as a number, date, unit with missing == blank): "100" vs 100
   and a missing unit vs a blank unit are no conflict and no row (tested). Side effects now listed: a JSON "unit": null and a missing unit key on
   T1/T2 are UNKNOWN ("no unit given"); on an error figure, missing and blank units are the same.
3. Crash classes from round 13 closed: a 400-digit integer reads as UNKNOWN (unreadable value), not a crash; before mode with an unopenable file
   or a bad .gz is a clean refusal (rc 1); --out a file or device is refused. The R13 line above now says exit 1, as the code does.
6. Packaging: src/qia_check.py and README.md in the package folder ARE the candidate (pyproject builds them); the side files are removed.
8. Real data: 577 ibm_kingston records (qia_package/test/recs 362 + qia_mirror/records/ibm_kingston 215 at 06:3xZ; the mirror keeps saving,
   so the count grows; 572 earlier was 362 + 210), 0 unreadable, one UNKNOWN kind ("absent from the record"). Output saved:
   overnight_20261104/qia_break/real_records_scan_7g.text. Repros unchanged.
Not done: the three-file group where two agree and one differs still lists the agreeing pair's flag rows twice; the CONFLICT row carries no
"unit only" label; at exactly 1e-9 the unit label follows float rounding (README says so). --pull and Python 3.9 untested.

## Round 7h (Sage round-14 VERDICT 06:39Z MOVES: two 7g claims false against the code) -> src/qia_check.py sha256 5a73358b...
7g's lines on the lone surrogate and the 400-digit integer were FALSE (Sage round 14): a lone surrogate crashed both modes at the page write and
left a 0-byte .html; a 400-digit integer crashed after mode wherever a change or CONFLICT row printed it. Fixed in 7h:
- pages and data are written with unencodable text replaced, so a lone-surrogate backend name writes full reports in both modes (tested: rc 0,
  no traceback in that test, no empty files).
- fmt() prints a number too large for a float as shortened text (999999999999...9999), so the change row prints and the figure is UNKNOWN (tested).
- --out (and the records folder) that cannot be resolved as a path is refused. Order, read from main() (corrected twice, Sage rounds 15 and 16):
  BEFORE mode: (1) the --pull note, (2) the record is chosen and, with --pull and no record, pulled, (3) this --out path check, (4) the
  record-file check, (5) the record's-own-folder check, (6) the record is read. AFTER mode: this path check runs first. Sage's builder ran
  //./CON/x and \\.\CON\x on Windows: clean rc 1 refusals in both modes.
- a JSON "unit": null is the same as a missing unit (no conflict between them; a T1/T2 with either is UNKNOWN "no unit given").
- stated (this code was already in 7g, not a 7h change): report file names are cut to 80 characters. safe() turns an empty name into "record",
  but that case is not reachable from the CLI (the stem always carries a prefix).
Repros unchanged. Still not done (listed in 7g): the three-file doubling, no "unit only" label on CONFLICT rows; --pull and Python 3.9 untested.

## Decided at 7h, not changed in code (Sage round 15 code verdict STANDS; text verdict round 16, 06:53Z)
- A shortened figure in a change row (700000000000...0123) does not say it is shortened; the UNKNOWN row prints all the digits, so nothing is hidden.
- A path with a NUL character still gives a traceback, reachable only through a crafted argv (no shell can send it).
- The 577-record result is verified on the staged copy in Sage's workshop, not on the Mac's live mirror, and her builder read it in-process,
  not through the CLI.
- A 5,000-digit integer makes the file skipped in after mode (and refused in before mode); the after page can still read "0 UNKNOWN"; the
  README now says a skipped file is not a pass and a clean page has nothing skipped.
- A null unit against a blank unit is no conflict, but on T1/T2 null reads UNKNOWN (no unit given) where blank reads as microseconds.
- The --out path refusal text does not say which path failed when the records folder is the bad one.
- --pull and Python 3.9 are untested; 1.0.1 ships with both stated as untested.
1.0.1 CANDIDATE: src/qia_check.py sha256 5a73358b... Publishing to PyPI waits for Wayfinder's word.
