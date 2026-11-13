import json, subprocess, glob, tempfile, os, sys
d = tempfile.mkdtemp(); X = os.path.join(os.path.dirname(sys.executable), 'qia-check')
N = lambda n, v, t, u='': {'name': n, 'value': v, 'date': t, 'unit': u}
R = lambda qs, s='2026-11-01T12:00:00Z', b='ibm_kingston': {'backend_name': b, 'last_update_date': s, 'qubits': qs}
def after(recs, start, end):
    rd = os.path.join(d, 'recs'); os.makedirs(rd); o = os.path.join(d, 'out')
    for name, rec in recs.items(): json.dump(rec, open(os.path.join(rd, name), 'w'))
    subprocess.run([X, 'after', rd, '--start', start, '--end', end, '--out', o], check=True, capture_output=True)
    return json.load(open(glob.glob(o + '/*.json')[0])), open(glob.glob(o + '/*.html')[0], encoding='utf-8').read()
OLD = '2026-10-30T10:00:00Z'; q = [[N('T1', 150.0, OLD, 'us'), N('T2', 120.0, OLD, 'us')]]
j, h = after({'a.json': R(q, '2026-11-01T11:00:00Z')}, '2026-11-01T12:00:00Z', '2026-11-01T12:40:00Z')
print('STALE in html:', 'STALE' in h, '| flags key in json:', 'flags' in j); print('HOLE' if 'STALE' in h and 'flags' not in j else 'fixed')
