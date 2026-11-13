"""Write and run the minimal reproducers (DRAFT, Sage). Each R*.py is standalone, <= 15 lines, drives the installed
`qia-check` console script that sits next to the python running it, and prints HOLE (or 'fixed') on its last line.
Usage: VENV/Scripts/python build_and_run_repros.py"""
import os, subprocess, sys

HB = '''import json, subprocess, glob, tempfile, os, sys
d = tempfile.mkdtemp(); X = os.path.join(os.path.dirname(sys.executable), 'qia-check')
N = lambda n, v, t, u='': {'name': n, 'value': v, 'date': t, 'unit': u}
R = lambda qs, s='2026-11-01T12:00:00Z', b='ibm_kingston': {'backend_name': b, 'last_update_date': s, 'qubits': qs}
def before(rec):
    p = os.path.join(d, 'r%d.json' % len(os.listdir(d))); json.dump(rec, open(p, 'w')); o = p + '_out'
    r = subprocess.run([X, 'before', p, '--out', o], capture_output=True, text=True)
    return r.returncode, (r.stderr.strip().splitlines() or [''])[-1][:110], (json.load(open(glob.glob(o + '/*.json')[0]))['flags'] if r.returncode == 0 else None)
'''
HA = '''import json, subprocess, glob, tempfile, os, sys
d = tempfile.mkdtemp(); X = os.path.join(os.path.dirname(sys.executable), 'qia-check')
N = lambda n, v, t, u='': {'name': n, 'value': v, 'date': t, 'unit': u}
R = lambda qs, s='2026-11-01T12:00:00Z', b='ibm_kingston': {'backend_name': b, 'last_update_date': s, 'qubits': qs}
def after(recs, start, end):
    rd = os.path.join(d, 'recs'); os.makedirs(rd); o = os.path.join(d, 'out')
    for name, rec in recs.items(): json.dump(rec, open(os.path.join(rd, name), 'w'))
    subprocess.run([X, 'after', rd, '--start', start, '--end', end, '--out', o], check=True, capture_output=True)
    return json.load(open(glob.glob(o + '/*.json')[0])), open(glob.glob(o + '/*.html')[0], encoding='utf-8').read()
'''
F = "F = '2026-11-01T09:00:00Z'   # fresh: 3 h before the stamp\n"
REPROS = {
 'R01_readout_family_never_aged': (HB, F + '''OLD = '2026-08-09T12:00:00Z'   # 84 d before the stamp
q = [N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us'), N('readout_error', 0.012, OLD),
     N('prob_meas0_prep1', 0.015, OLD), N('prob_meas1_prep0', 0.009, OLD), N('init_error', 0.003, OLD)]
rc, err, fl = before(R([q])); print('flags:', fl); print('HOLE' if fl == [] else 'fixed')
'''),
 'R02_staleness_ignores_run_time': (HB, '''T = '2026-11-01T11:00:00Z'   # 1 h before the stamp; the stamp is days old when you run this
rc, err, fl = before(R([[N('T1', 150.0, T, 'us'), N('T2', 120.0, T, 'us')]]))
print('flags:', fl); print('HOLE' if fl == [] else 'fixed')
'''),
 'R03_silent_on_missing_null_nan_negative': (HB, F + '''qs = [[N('T2', 120.0, F, 'us')], [N('T1', None, F, 'us'), N('T2', 120.0, F, 'us')],
      [N('T1', float('nan'), F, 'us'), N('T2', 120.0, F, 'us')],
      [N('T1', -150.0, '2026-10-31T06:00:00Z', 'us'), N('T2', 400.0, F, 'us')]]   # q3 T1/T2 dates 27 h apart
rc, err, fl = before(R(qs)); print('flags:', fl)
print('HOLE' if not [f for f in fl if f['qubit'] < 3 or f['check'] == 'PAIR'] else 'fixed')
'''),
 'R04_empty_record_passes': (HB, '''rc, err, fl = before(R([])); print('exit', rc, 'flags:', fl)
print('HOLE' if rc == 0 and fl == [] else 'fixed')
'''),
 'R05_gates_and_zz_never_read': (HB, F + '''rec = R([[N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us')]] * 2)
rec['gates'] = [{'gate': 'cz', 'qubits': [0, 1], 'name': 'cz0_1', 'parameters': [N('gate_error', 0.0042, F), N('zz', 0.0, F, 'kHz')]}]
rc, err, fl = before(rec); print('flags:', fl); print('HOLE' if fl == [] else 'fixed')
'''),
 'R06_naive_time_silently_utc': (HB, '''# one instant, 2026-10-31 14:00 UTC (22 h before the stamp): aware, then as a naive EDT wall-clock string
a = before(R([[N('T1', 150.0, '2026-10-31T10:00:00-04:00', 'us'), N('T2', 120.0, '2026-10-31T10:00:00-04:00', 'us')]]))[2]
b = before(R([[N('T1', 150.0, '2026-10-31T10:00:00', 'us'), N('T2', 120.0, '2026-10-31T10:00:00', 'us')]]))[2]
print(a, b); print('HOLE' if a != b else 'fixed')
'''),
 'R07_unparseable_date_traceback': (HB, '''for t, s in (('2016-12-31T23:59:60Z', '2017-01-01T06:00:00Z'), ('2026-10-31T10:00:00 EDT', '2026-11-01T12:00:00Z')):
    rc, err, fl = before(R([[N('T1', 150.0, t, 'us'), N('T2', 120.0, s, 'us')]], s=s)); print(rc, err)
print('HOLE' if 'ValueError' in err else 'fixed')
'''),
 'R08_string_zero_passes_ZERO': (HB, F + '''q = [N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us'), N('readout_error', '0', F), N('prob_meas0_prep1', '0.0', F)]
rc, err, fl = before(R([q])); print('flags:', fl); print('HOLE' if fl == [] else 'fixed')
'''),
 'R09_string_numbers_crash': (HB, F + '''rc, err, fl = before(R([[N('T1', '150.0', F, 'us'), N('T2', '120.0', F, 'us')]]))
print(rc, err); print('HOLE' if 'TypeError' in err else 'fixed')
'''),
 'R10_float_edge_at_2p5': (HB, F + '''rc, err, fl = before(R([[N('T1', 0.0001234, F, 's'), N('T2', 0.0003085, F, 's')]]))   # T2 = 2.5 x T1 exactly, in decimal
print('flags:', fl); print('HOLE' if fl and fl[0].get('outcome') == 'ABOVE' else 'fixed')
'''),
 'R11_duplicate_entry_last_wins': (HB, F + '''OLD = '2026-10-30T12:00:00Z'   # 48 h before the stamp
a = before(R([[N('T1', 150.0, OLD, 'us'), N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us')]]))[2]
b = before(R([[N('T1', 150.0, F, 'us'), N('T1', 150.0, OLD, 'us'), N('T2', 120.0, F, 'us')]]))[2]
print(a, b); print('HOLE' if a != b else 'fixed')
'''),
 'R12_units_ignored': (HB, F + '''rc, err, fl = before(R([[N('T1', 150.2, F, 'us'), N('T2', 0.0004, F, 's')]]))   # T2 = 400 us = 2.66 x T1
print('flags:', fl); print('HOLE' if fl == [] else 'fixed')
'''),
 'R13_after_mixes_backends': (HA, F + '''q = [[N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us')]]
j, h = after({'k.json': R(q, '2026-11-01T11:00:00Z'), 'f.json': R(q, '2026-11-01T11:50:00Z', 'ibm_fez')},
             '2026-11-01T12:00:00Z', '2026-11-01T12:40:00Z')
print('record in force:', j['backend'], j['record_at_start']); print('HOLE' if j['backend'] == 'ibm_fez' else 'fixed')
'''),
 'R14_mid_run_record_unchecked': (HA, F + '''ok = [[N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us'), N('readout_error', 0.012, F)]]
bad = [[N('T1', 150.0, '2026-10-29T12:00:00Z', 'us'), N('T2', 120.0, F, 'us'), N('readout_error', 0.0, F)]]
j, h = after({'a.json': R(ok, '2026-11-01T11:00:00Z'), 'b.json': R(bad, '2026-11-01T12:20:00Z')},
             '2026-11-01T12:00:00Z', '2026-11-01T12:40:00Z')
print('ZERO' in h, 'STALE' in h); print('HOLE' if 'ZERO' not in h and 'STALE' not in h else 'fixed')
'''),
 'R15_same_stamp_conflict_by_filename': (HA, F + '''good = [[N('T1', 150.0, F, 'us'), N('T2', 120.0, F, 'us')]]
bad = [[N('T1', 41.0, '2026-10-30T10:00:00Z', 'us'), N('T2', 120.0, F, 'us')]]
j, h = after({'a.json': R(good, '2026-11-01T11:00:00Z'), 'b.json': R(bad, '2026-11-01T11:00:00Z')},
             '2026-11-01T12:00:00Z', '2026-11-01T12:40:00Z')
print(j['skipped'], 'STALE' in h); print('HOLE' if 'STALE' not in h else 'fixed')
'''),
 'R16_after_json_has_no_flags': (HA, '''OLD = '2026-10-30T10:00:00Z'; q = [[N('T1', 150.0, OLD, 'us'), N('T2', 120.0, OLD, 'us')]]
j, h = after({'a.json': R(q, '2026-11-01T11:00:00Z')}, '2026-11-01T12:00:00Z', '2026-11-01T12:40:00Z')
print('STALE in html:', 'STALE' in h, '| flags key in json:', 'flags' in j); print('HOLE' if 'STALE' in h and 'flags' not in j else 'fixed')
'''),
}

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__)); bad = 0
    for name, (head, body) in REPROS.items():
        src = head + body; n = len(src.strip().splitlines())
        open(os.path.join(here, name + '.py'), 'w', encoding='utf-8').write(src)
        p = subprocess.run([sys.executable, os.path.join(here, name + '.py')], capture_output=True, text=True, timeout=120)
        last = (p.stdout.strip().splitlines() or ['(no output) ' + p.stderr[-200:]])[-1]
        ok = n <= 15 and last == 'HOLE'; bad += not ok
        print(f'{name:42} lines={n:2} -> {last}' + ('' if ok else '   <-- CHECK'))
        for line in p.stdout.strip().splitlines()[:-1]: print('      ', line[:200])
    sys.exit(1 if bad else 0)
