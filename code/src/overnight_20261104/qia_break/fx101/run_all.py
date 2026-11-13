"""Runner for the qia-check break fixtures (DRAFT, Sage, 2026-11-03).

Usage:  python run_all.py --venv PATH_TO_VENV  [--results DIR]
Regenerates ./data with make_fixtures.py, then runs every case through the *installed* package's console script
(PATH_TO_VENV/Scripts/qia-check.exe, the public CLI). Nothing is monkeypatched and no package file is read or written
except through the CLI. Writes results.json and results.md into --results (default ./results).

Verdicts: HOLDS = the package does what a careful referee requires; HOLE = it does not (a silent pass on
missing or unreadable data is always a HOLE); CANNOT TELL = this installed package cannot exercise the case."""
import argparse, glob, html, json, os, re, shutil, subprocess, sys
import make_fixtures

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda *p: os.path.join(make_fixtures.DATA, *p)
EXE = None
RES = None
_n = [0]


def run(mode, target, *args):
    _n[0] += 1
    out = os.path.join(RES, 'reports', f'run{_n[0]:03d}')
    cmd = [EXE, mode, target, '--out', out, *args]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    r = dict(cmd=' '.join(['qia-check', mode, os.path.relpath(target, HERE), *args]), rc=p.returncode,
             stdout=p.stdout.strip(), stderr=p.stderr.strip(), json=None, sections={}, meta=[])
    js = glob.glob(os.path.join(out, '*.json'))
    hs = glob.glob(os.path.join(out, '*.html'))
    if js:
        r['json'] = json.load(open(js[0], encoding='utf-8'))
        r['meta'] = r['json'].get('meta', [])
    if hs:
        r['sections'] = parse_html(open(hs[0], encoding='utf-8').read())
        r['html_text'] = re.sub(r'<[^>]+>', ' ', open(hs[0], encoding='utf-8').read())
    r['err_last'] = (r['stderr'].splitlines() or [''])[-1]
    return r


def parse_html(h):
    secs = {}
    for part in h.split('<h2>')[1:]:
        title = html.unescape(part.split('</h2>')[0])
        heads = [html.unescape(x) for x in re.findall(r'<th>(.*?)</th>', part)]
        rows = []
        for tr in re.findall(r'<tr>((?:<td>.*?</td>)+)</tr>', part):
            rows.append(dict(zip(heads, [html.unescape(x) for x in re.findall(r'<td>(.*?)</td>', tr)])))
        secs[title] = rows
    return secs


def flags(r):
    """Flag rows from a before (json) or after (html 'Flags in that record') run."""
    if r['json'] and 'flags' in r['json']:
        return r['json']['flags']
    for t, rows in r['sections'].items():
        if t.startswith('Flags'):
            return [dict(x, qubit=int(x['qubit'])) for x in rows]
    return []


def fq(r, q):
    return sorted((f['check'], f['field']) + ((f['outcome'],) if f.get('outcome') else ()) for f in flags(r) if f['qubit'] == q)


def short(r):
    if r['rc'] != 0:
        return f"exit {r['rc']}: {r['err_last'][:160]}"
    return 'exit 0, flags=' + json.dumps([(f['qubit'], f['check'], f['field'], f.get('outcome', '')) for f in flags(r)])


CASES = []


def case(cid, title, source):
    def deco(fn):
        CASES.append((cid, title, source, fn))
        return fn
    return deco


# ============================ plan fixtures ============================
@case('P01', 'init_error measured 84 d before stamp, T1/T2 fresh', 'plan 1 (Q10)')
def _():
    r = run('before', D('P01', 'record.json'))
    hit = [f for f in flags(r) if 'init' in f['field']]
    return dict(expected='flag on init_error age (84 d)', observed=short(r), verdict='HOLDS' if hit else 'HOLE',
                notes='init_error is not in FIELDS (qia_check.py:30), so load() drops it (line 46); no check can see it.', runs=[r])


@case('P02', 'prob_meas0_prep1 97 h older than readout_error', 'plan 2 (Q11)')
def _():
    r = run('before', D('P02', 'record.json'))
    hit = [f for f in flags(r) if f['field'] in ('prob_meas0_prep1', 'readout_error') and f['check'] != 'ZERO']
    return dict(expected='flag: readout-family dates disagree by 97 h (and 99.5 h before stamp)', observed=short(r),
                verdict='HOLDS' if hit else 'HOLE', notes='STALE loops over T1, T2 only (line 52); error-field dates are loaded but never compared.', runs=[r])


@case('P03', 'stamped 72 h before the run, T1 measured 1 h before the stamp', 'plan 3')
def _():
    rb = run('before', D('P03', 'record.json'))
    ra = run('after', D('P03', 'records'), '--start', '2026-11-04T12:00:00Z', '--end', '2026-11-04T12:40:00Z')
    hit = flags(rb) + flags(ra)
    age_meta = [m for m in rb['meta'] if 'before this check' in m]
    return dict(expected='flag: T1 is 73 h old at run time', observed=f'before: {short(rb)}; after (start = stamp + 72 h): {short(ra)}',
                verdict='HOLDS' if hit else 'HOLE',
                notes='Staleness is S - date with S = last_update_date (lines 47, 53). The run time is used only to choose the record '
                      '(line 131); before mode prints the record age as prose meta only (line 112-113): ' + (age_meta[0][:110] if age_meta else ''),
                runs=[rb, ra])


@case('P04', 'T1 absent / null / NaN (plus date-null, T1 = 0, T2 NaN, T2 absent)', 'plan 4')
def _():
    r = run('before', D('P04', 'record.json'))
    names = ['T1 absent', 'T1 null', 'T1 NaN', 'T1 date null', 'T1 = 0', 'T2 NaN', 'T2 absent', 'control (T2/T1 2.63)']
    obs = {names[q]: fq(r, q) for q in range(8)}
    silent = [n for q, n in enumerate(names[:7]) if not fq(r, q)]
    return dict(expected='UNKNOWN (or an explicit flag) for every qubit with an unreadable T1/T2; control q7 ABOVE',
                observed=f'exit {r["rc"]}; per qubit: ' + json.dumps(obs), verdict='HOLE' if silent else 'HOLDS',
                notes=f'silent (no row at all) on: {", ".join(silent)}. No UNKNOWN outcome exists in the code; guards at lines 53, 56, 57 '
                      'skip quietly and the report says "Nothing flagged" for those qubits.', runs=[r])


@case('P05', 'zz = 0.00 on an edge with calibrated CZ error', 'plan 5 (Q7)')
def _():
    r = run('before', D('P05', 'record.json'))
    hit = [f for f in flags(r) if 'zz' in f['field'].lower()]
    return dict(expected='flag zz on edge 0-1 as missing', observed=short(r), verdict='HOLDS' if hit else 'HOLE',
                notes='load() never reads d["gates"]; only qubit Nduvs named in FIELDS are kept (lines 45-46).', runs=[r])


@case('P06', 'T1 age 24h00m00s / 23h59m59s (control 24h00m01s)', 'plan 6')
def _():
    r = run('before', D('P06', 'record.json'))
    o = [bool([f for f in flags(r) if f['qubit'] == q and f['check'] == 'STALE']) for q in range(3)]
    ok = o == [False, False, True]
    return dict(expected='document side; consistent with the docstring "more than 24 hours"',
                observed=f'24h00m00s STALE={o[0]}; 23h59m59s STALE={o[1]}; 24h00m01s STALE={o[2]}', verdict='HOLDS' if ok else 'HOLE',
                notes='Strict ">" 86400 s (line 53): exactly 24 h is NOT stale; first stale instant is 24 h + 1 microsecond.', runs=[r])


@case('P07', 'same instant as EDT offset, Z, +00:00, naive, (and "EDT" text)', 'plan 7')
def _():
    rs = {k: run('before', D('P07', k + '.json')) for k in ('a_edt_offset', 'b_utc_Z', 'c_plus0000', 'd_naive_utc_wall',
                                                           'e_naive_edt_wall', 'f_edt_abbrev')}
    obs = {k: short(v) for k, v in rs.items()}
    core = {short(rs[k]) for k in ('a_edt_offset', 'b_utc_Z', 'c_plus0000', 'd_naive_utc_wall')}
    naive_wrong = short(rs['e_naive_edt_wall']) != short(rs['b_utc_Z'])
    crash = rs['f_edt_abbrev']['rc'] != 0
    v = 'HOLE' if (len(core) > 1 or naive_wrong or crash) else 'HOLDS'
    return dict(expected='identical results; a naive time refused or flagged, never silently assumed',
                observed=json.dumps(obs), verdict=v,
                notes=f'EDT/Z/+00:00 and naive-UTC-wall agree: {len(core) == 1}. A naive string is silently read as UTC (line 35): '
                      f'the EDT wall-clock naive spelling gives a different result ({naive_wrong}). The CLI refuses naive --start/--end '
                      f'(line 94) but the record parser does not. "EDT" suffix: traceback, no report ({crash}).', runs=list(rs.values()))


@case('P08', 'readout 1e-17, -0.0, "0", 1/1024 (control 0)', 'plan 8')
def _():
    r = run('before', D('P08', 'record.json'))
    z = [bool([f for f in flags(r) if f['qubit'] == q and f['check'] == 'ZERO']) for q in range(5)]
    hole = not z[2] or not z[1] or not z[4]          # 1e-17 is per the documented "exactly 0" rule: spec gap, reported not scored
    return dict(expected='ZERO on 0 and -0.0; "0" flagged or rejected (not silently passed); 1e-17 flagged as below 1/shots; '
                         '1/1024 passes with the 0-of-1024 bound stated',
                observed=f'ZERO fired: 1e-17={z[0]}, -0.0={z[1]}, "0"={z[2]}, 1/1024={z[3]}, 0={z[4]}',
                verdict='HOLE' if hole else 'HOLDS',
                notes='Test is `value == 0` (line 56): -0.0 == 0 is True; "0" == 0 is False, so a string zero passes silently; 1e-17 '
                      'passes although no 1024/4096/8192-shot estimate can produce it. The report states no shot bound: an observed '
                      '0 of 1024 still allows p up to 1-0.05**(1/1024) = 0.2921 % (95 % one-sided).', runs=[r])


@case('P09', 'T2/T1 = 2.0, 2.0000001, 2.5, 2.5000001 (+ two decimal-exact 2.5)', 'plan 9')
def _():
    r = run('before', D('P09', 'record.json'))
    exp = ['OK', 'CANNOT_TELL', 'CANNOT_TELL', 'ABOVE', 'CANNOT_TELL', 'CANNOT_TELL']
    got = []
    for q in range(6):
        f = [x for x in flags(r) if x['qubit'] == q and x['check'] == 'T2>2T1']
        got.append(f[0]['outcome'] if f else 'OK')
    plan_ok = got[:4] == exp[:4]
    return dict(expected='q0-q3 ' + '/'.join(exp[:4]) + '; q4 0.0003085/0.0001234 and q5 358.025/143.21 are exactly 2.5 in decimal -> CANNOT_TELL',
                observed='got ' + '/'.join(got), verdict='HOLDS' if got == exp else 'HOLE',
                notes=f'plan four cases {"match" if plan_ok else "DO NOT match"}. Ratio is a float division compared with strict > 2.0 and '
                      '> 2.5 (line 58-59); 0.0003085/0.0001234 = 2.5000000000000004 in binary and reads ABOVE. Multiplying by 2 is '
                      'exact in binary, so the 2.0 edge does not move; the 2.5 edge does.', runs=[r])


@case('P10', 'T1 and T2 dates exactly 24 h apart (PAIR boundary)', 'plan 10')
def _():
    r = run('before', D('P10', 'record.json'))
    o = [bool([f for f in flags(r) if f['qubit'] == q and f['check'] == 'PAIR']) for q in range(3)]
    return dict(expected='document side; consistent with "more than 24 hours apart"',
                observed=f'24h00m00s PAIR={o[0]}; 24h00m01s PAIR={o[1]}; 23h59m59s PAIR={o[2]}',
                verdict='HOLDS' if o == [False, True, False] else 'HOLE',
                notes='gap > 24 h strictly (line 62), abs() so order does not matter. Exactly 24 h is not flagged.', runs=[r])


@case('P11', 'run window spanning a restamp', 'plan 11')
def _():
    r = run('after', D('P11', 'records'), '--start', '2026-11-01T12:00:00Z', '--end', '2026-11-01T12:40:00Z')
    j = r['json'] or {}
    during = j.get('records_during', [])
    ch = [(c['qubit'], c['field'], c['before'], c['after']) for c in j.get('changes', [])]
    ok = j.get('record_at_start', '').startswith('2026-11-01T11:00') and during == ['2026-11-01T12:20:00+00:00'] and (0, 'T1', '152.3', '97.4') in ch
    return dict(expected='record at start (11:00) and the 12:20 restamp both surfaced; q0 T1 change listed; 13:00 excluded',
                observed=f'record_at_start={j.get("record_at_start")}, records_during={during}, changes={ch}',
                verdict='HOLDS' if ok else 'HOLE', notes='lines 131-149. See D03: the 12:20 record is listed but its own figures are not checked.', runs=[r])


@case('P12', 'stamp moved, all T1/T2 values and dates frozen (Q6)', 'plan 12')
def _():
    fs = sorted(glob.glob(D('P12', 'records', '*.json')))
    rb = [run('before', f) for f in fs]
    stale = [bool([x for x in flags(r) if x['check'] == 'STALE']) for r in rb]
    ra = run('after', D('P12', 'records'), '--start', '2026-11-01T18:00:00Z', '--end', '2026-11-02T01:00:00Z')
    j = ra['json'] or {}
    ok = stale == [False, False, True]
    return dict(expected='age grows with the stamp, not with the run',
                observed=f'before on stamps +0 h/+12 h/+36 h: STALE={stale}; after across the +12 h restamp: '
                         f'records_during={j.get("records_during")}, changes={len(j.get("changes", []))}',
                verdict='HOLDS' if ok else 'HOLE',
                notes='Confirmed: same frozen dates go 1 h -> 13 h -> 37 h old purely because last_update_date moved. In after mode a '
                      'restamp with no new measurement shows as "Records stamped during the run: 1" with an empty change table; '
                      'nothing says the stamp moved without new figures.', runs=rb + [ra])


@case('P13', 'grid: 1/1024 values written as rounded decimals (0.00293)', 'plan 13')
def _():
    r = run('before', D('P13', 'record.json'))
    txt = r.get('html_text', '') + json.dumps(r['json'] or {})
    mention = bool(re.search(r'shot|1024|4096|8192', txt, re.I))
    return dict(expected='shot count inferred from the grid must not flip 1024 -> 4096 on rounded decimals',
                observed=f'{short(r)}; report mentions shots or a grid: {mention}', verdict='CANNOT TELL',
                notes='qia-check 1.0.0 has no shot-count or grid inference anywhere (153 lines, no "shot"). The case belongs to '
                      'whatever code infers shots (YO / the site), which is not in this package. Not scored HOLDS.', runs=[r])


@case('P14', 'YO vs code on the 23h59m59s and 1e-17 cases', 'plan 14')
def _():
    r = run('before', D('P14', 'record.json'))
    sp = (glob.glob(os.path.join(os.path.dirname(os.path.dirname(EXE)), 'lib', 'python*', 'site-packages')) or [os.path.join(os.path.dirname(os.path.dirname(EXE)), 'Lib', 'site-packages')])[0]
    yo = [p for p in os.listdir(sp) if 'yo' in p.lower()]
    return dict(expected='page shows the code answer as authoritative when YO disagrees',
                observed=f'code answer: {short(r)}; YO files in site-packages: {yo or "none"}', verdict='CANNOT TELL',
                notes='TESTED.md: "Not yet tested inside this package: the YO reader (yo/yo_audit.py)". The PyPI wheel ships only '
                      'qia_check.py, so YO cannot be run from the installed package. The code side is recorded: 23h59m59s is not '
                      'STALE and 1e-17 is not ZERO.', runs=[r])


# ============================ extra fixtures ============================
@case('E01', 'malformed JSON (truncated, trailing comma, list top-level, no stamp)', 'task 5')
def _():
    rs = [run('before', D('E01', n)) for n in ('truncated.json', 'trailing_comma.json', 'list_top.json', 'no_stamp.json')]
    ra = run('after', D('E01', 'dir'), '--start', '2026-11-01T12:00:00Z', '--end', '2026-11-01T12:40:00Z')
    clean = all(r['rc'] != 0 and 'not a calibration record' in r['stderr'] and 'Traceback' not in r['stderr'] and r['json'] is None for r in rs)
    listed = any('bad.json' in m for m in ra['meta'])
    return dict(expected='clean refusal, no report; in after mode the bad file is named, not silently dropped',
                observed='; '.join(short(r) for r in rs) + f' | after: skipped listed in meta={listed}',
                verdict='HOLDS' if clean and listed else 'HOLE', notes='lines 109-110, 126-127, 132.', runs=rs + [ra])


@case('E02', 'empty qubit list; a qubit with an empty property list', 'task 5')
def _():
    r1 = run('before', D('E02', 'empty.json'))
    r2 = run('before', D('E02', 'empty.json'), '--qubits', '0,1')
    r3 = run('before', D('E02', 'empty_qubit.json'))
    m3 = [m for m in r3['meta'] if 'Qubits checked' in m]
    return dict(expected='refuse or say UNKNOWN: nothing was checkable',
                observed=f'empty: {short(r1)} meta={r1["meta"][0][-22:]!r}; with --qubits 0,1: {short(r2)} ({[m for m in r2["meta"] if "Not in" in m]}); '
                         f'empty qubit 0: {short(r3)}, {m3[0][-20:] if m3 else ""}',
                verdict='HOLE', notes='Exit 0 with "Flags (0) / Nothing flagged." An empty qubit block is counted as "checked" '
                                      '(line 46 makes it {}, line 51 then skips every check).', runs=[r1, r2, r3])


@case('E03', 'duplicate entries for one qubit with conflicting values', 'task 5')
def _():
    a = run('before', D('E03', 'stale_first.json'))
    b = run('before', D('E03', 'stale_last.json'))
    c = run('before', D('E03', 'ratio_conflict.json'))
    return dict(expected='flag the conflict (or refuse); result must not depend on list order',
                observed=f'stale T1 first: {short(a)}; stale T1 last: {short(b)}; T1 150 then 210 with T2 400: {short(c)}',
                verdict='HOLDS' if (flags(a) == flags(b) and 'DUPLICATE' in json.dumps(flags(a))) else 'HOLE',
                notes='dict comprehension at line 46: the last Nduv with a given name silently wins. Same data, order swapped, opposite answer.',
                runs=[a, b, c])


@case('E04', 'negative T1', 'task 5')
def _():
    r = run('before', D('E04', 'record.json'))
    return dict(expected='flag an impossible T1 (or UNKNOWN); PAIR still evaluated on the dates',
                observed=f'q0: {fq(r, 0)}; q1 (dates 30 h apart): {fq(r, 1)}', verdict='HOLE' if not fq(r, 0) or not [x for x in fq(r, 1) if x[0] == 'PAIR'] else 'HOLDS',
                notes='`t1[0] > 0` (line 57) skips the ratio quietly, and PAIR sits inside the same if-block (line 60), so it is skipped too.', runs=[r])


@case('E05', 'T1 in s / ms vs T2 in us (unit confusion)', 'task 5')
def _():
    r = run('before', D('E05', 'record.json'))
    return dict(expected='normalise units or refuse mixed units; true ratios are 0.79 (q0), 2.66 (q1), 2.66 (q2)',
                observed=f'q0 (T1 s, T2 us): {fq(r, 0)}; q1 (T1 us, T2 s): {fq(r, 1)}; q2 (T1 ms, T2 us): {fq(r, 2)}',
                verdict='HOLE', notes='unit is loaded (line 46) and never read. q0 is a false ABOVE (ratio ~790,000); q1 misses a real ABOVE '
                                      '(ratio 2.66e-6); q2 reads ABOVE only by accident (ratio ~2,663 instead of 2.66).', runs=[r])


@case('E06', 'string-typed numbers', 'task 5')
def _():
    a = run('before', D('E06', 'numbers_as_strings.json'))
    b = run('before', D('E06', 'zero_as_string.json'))
    c = run('before', D('E06', 'err_as_string_nonzero.json'))
    return dict(expected='coerce, or refuse with a clean message; never a traceback, never a silent pass',
                observed=f'T1/T2 strings: {short(a)}; readout "0.0" and p01 "0": {short(b)}; T2 "400.0" with T1 150.0: {short(c)}',
                verdict='HOLE', notes='"152.31" > 0 raises TypeError at line 57 (uncaught: traceback, no report). String zeros pass ZERO silently (line 56).',
                runs=[a, b, c])


@case('E07', 'leap second and DST fall-back timestamps', 'task 5')
def _():
    a = run('before', D('E07', 'leap_t1.json'))
    b = run('before', D('E07', 'leap_stamp.json'))
    c = run('before', D('E07', 'dst_aware.json'))
    d = run('before', D('E07', 'dst_naive_walls.json'))
    st_c = [x for x in flags(c) if x['check'] == 'STALE']
    st_d = [x for x in flags(d) if x['check'] == 'STALE']
    return dict(expected='leap second parsed or refused cleanly; DST: true age 24.5 h -> STALE whatever the spelling',
                observed=f'leap in T1 date: {short(a)}; leap in stamp: {short(b)}; DST with offsets: STALE={bool(st_c)}; DST naive walls: STALE={bool(st_d)}',
                verdict='HOLE', notes='fromisoformat rejects second=60. In a field date the ValueError escapes check_record (line 53) as a '
                                      'traceback; in the stamp it is reported as "not a calibration record". DST with offsets HOLDS (parsed to UTC); '
                                      'naive wall-clock times are read as UTC and the 24.5 h age reads 23.5 h.', runs=[a, b, c, d])


@case('E08', 'readout_error / prob_meas* dated 84 d before fresh T1/T2 (Q10 shape)', 'task 5 (Q10)')
def _():
    r = run('before', D('E08', 'record.json'))
    return dict(expected='flag the readout-family figures as stale', observed=short(r),
                verdict='HOLDS' if flags(r) else 'HOLE', notes='Same root as P01/P02: STALE covers T1 and T2 only (line 52).', runs=[r])


# ============================ derived from the source ============================
@case('D01', 'T1 value null or negative hides a 30 h T1/T2 date gap', 'source line 57-62')
def _():
    r = run('before', D('D01', 'record.json'))
    p = [bool([x for x in flags(r) if x['qubit'] == q and x['check'] == 'PAIR']) for q in range(3)]
    return dict(expected='PAIR on all three (dates are 30 h apart)', observed=f'PAIR null={p[0]}, negative={p[1]}, control={p[2]}',
                verdict='HOLDS' if all(p) else 'HOLE', notes='PAIR is nested in the T1-value guard at line 57.', runs=[r])


@case('D02', 'after mode with records from two backends in one folder', 'source line 128-136')
def _():
    r = run('after', D('D02', 'records'), '--start', '2026-11-01T12:00:00Z', '--end', '2026-11-01T12:40:00Z', '--qubits', '0,1')
    j = r['json'] or {}
    return dict(expected='record in force chosen per backend, or a refusal when backends mix',
                observed=f'backend chosen={j.get("backend")}, record_at_start={j.get("record_at_start")}; {short(r)}',
                verdict='HOLDS' if j.get('backend') == 'ibm_kingston' else 'HOLE',
                notes='recs are sorted by stamp only; under[-1] is whichever backend was stamped last before --start.', runs=[r])


@case('D03', 'record stamped during the run is listed but not checked', 'source line 139-147')
def _():
    r = run('after', D('D03', 'records'), '--start', '2026-11-01T12:00:00Z', '--end', '2026-11-01T12:40:00Z')
    fl = flags(r)
    ch = (r['json'] or {}).get('changes', [])
    return dict(expected='the mid-run record\'s ZERO readout and 60 h stale T1 on q1 are flagged',
                observed=f'flags={[(f["qubit"], f["check"], f["field"]) for f in fl]}; changes={[(c["qubit"], c["field"], c["before"], c["after"]) for c in ch]}',
                verdict='HOLDS' if any(f['check'] == 'ZERO' for f in fl) else 'HOLE',
                notes='check_record runs only on under[-1] (line 139). The ZERO shows up only as a value change 0.0122 -> 0, unlabelled.', runs=[r])


@case('D04', 'two files, same stamp, different contents', 'source line 128')
def _():
    r = run('after', D('D04', 'records'), '--start', '2026-11-01T12:00:00Z', '--end', '2026-11-01T12:40:00Z')
    return dict(expected='conflict reported as a conflict; result not decided by file name',
                observed=f'{short(r)}; meta={[m for m in r["meta"] if "same stamp" in m]}', verdict='HOLE',
                notes='The alphabetically first file wins; the other is listed as "(same stamp as another file)" without saying its figures differ '
                      '(b.json carries a 50 h stale T1 of 41 us that never gets checked).', runs=[r])


@case('D05', 'after-mode JSON output carries no flags (HTML does)', 'source line 150')
def _():
    r = run('after', D('D02', 'records'), '--start', '2026-11-01T12:00:00Z', '--end', '2026-11-01T12:40:00Z')
    in_html = len([x for t, rows in r['sections'].items() if t.startswith('Flags') for x in rows])
    in_json = len((r['json'] or {}).get('flags', []))
    return dict(expected='the machine-readable report carries the same flags as the HTML',
                observed=f'HTML flag rows={in_html}; JSON keys={sorted((r["json"] or {}).keys())}; JSON flags={in_json}',
                verdict='HOLDS' if in_json == in_html else 'HOLE',
                notes='after-mode data dict (line 150) has backend, record_at_start, records_during, changes, skipped; no flags.', runs=[r])


def main():
    global EXE, RES
    ap = argparse.ArgumentParser()
    ap.add_argument('--venv', required=True)
    ap.add_argument('--results', default=os.path.join(HERE, 'results'))
    a = ap.parse_args()
    EXE = os.path.join(os.path.abspath(a.venv), 'Scripts', 'qia-check.exe')
    if not os.path.exists(EXE):
        EXE = os.path.join(os.path.abspath(a.venv), 'bin', 'qia-check')
    RES = os.path.abspath(a.results)
    if os.path.isdir(RES):
        shutil.rmtree(RES)
    os.makedirs(RES)
    make_fixtures.build()
    py = os.path.join(os.path.dirname(EXE), 'python')
    ver = subprocess.run([py, '-c', 'import importlib.metadata as m, sys, qia_check; print(m.version("qia-check"), qia_check.__file__, sys.version.split()[0])'],
                         capture_output=True, text=True).stdout.strip()
    out = []
    for cid, title, src, fn in CASES:
        r = fn()
        r.update(id=cid, title=title, source=src)
        r['runs'] = [{k: x[k] for k in ('cmd', 'rc', 'stdout', 'stderr')} for x in r['runs']]
        out.append(r)
        print(f'{cid:4} {r["verdict"]:12} {title}')
    json.dump(dict(package=ver, cases=out), open(os.path.join(RES, 'results.json'), 'w', encoding='utf-8'), indent=1)
    with open(os.path.join(RES, 'results.md'), 'w', encoding='utf-8') as f:
        f.write(f'# qia-check break results (DRAFT)\n\nqia-check / module / python: {ver}\n\n| id | verdict | case | expected | observed |\n|---|---|---|---|---|\n')
        for r in out:
            f.write(f'| {r["id"]} | {r["verdict"]} | {r["title"]} | {r["expected"]} | {r["observed"].replace("|", "/")} |\n')
    c = {v: sum(1 for r in out if r['verdict'] == v) for v in ('HOLDS', 'HOLE', 'CANNOT TELL')}
    print('package:', ver)
    print('totals:', c)


if __name__ == '__main__':
    main()
