import json, subprocess, glob, tempfile, os, sys
d = tempfile.mkdtemp(); X = os.path.join(os.path.dirname(sys.executable), 'qia-check')
N = lambda n, v, t, u='': {'name': n, 'value': v, 'date': t, 'unit': u}
R = lambda qs, s='2026-11-01T12:00:00Z', b='ibm_kingston': {'backend_name': b, 'last_update_date': s, 'qubits': qs}
def before(rec):
    p = os.path.join(d, 'r%d.json' % len(os.listdir(d))); json.dump(rec, open(p, 'w')); o = p + '_out'
    r = subprocess.run([X, 'before', p, '--out', o], capture_output=True, text=True)
    return r.returncode, (r.stderr.strip().splitlines() or [''])[-1][:110], (json.load(open(glob.glob(o + '/*.json')[0]))['flags'] if r.returncode == 0 else None)
for t, s in (('2016-12-31T23:59:60Z', '2017-01-01T06:00:00Z'), ('2026-10-31T10:00:00 EDT', '2026-11-01T12:00:00Z')):
    rc, err, fl = before(R([[N('T1', 150.0, t, 'us'), N('T2', 120.0, s, 'us')]], s=s)); print(rc, err)
print('HOLE' if 'ValueError' in err else 'fixed')
