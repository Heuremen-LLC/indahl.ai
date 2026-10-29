#!/usr/bin/env python3
# independent recount of AUDIT_PLAN.md A, B, C, D counts; shares no code with audit.py
import gzip, json, glob, datetime
def t(s): return datetime.datetime.strptime(s[:19].replace('T', ' '), '%Y-%m-%d %H:%M:%S').timestamp()
for d in sorted(glob.glob('records/ibm_*')):
    fs = sorted(glob.glob(d + '/*.json.gz')); na = nc = nb = 0; last = None
    for f in fs:
        r = json.load(gzip.open(f))
        for q in r['qubits']:
            m = {e['name']: e for e in q}
            if 'T1' in m and 'T2' in m:
                x = m['T2']['value'] / m['T1']['value']
                if x > 2.5: na += 1
                elif x > 2.0: nc += 1
                if abs(t(m['T1']['date']) - t(m['T2']['date'])) > 86400: nb += 1
    r = json.load(gzip.open(fs[-1])); s = t(r['last_update_date']); a24 = a7 = n = 0
    for q in r['qubits']:
        for e in q:
            if e.get('date'):
                n += 1; g = s - t(e['date'])
                a24 += g > 86400; a7 += g > 7 * 86400
    ch = []
    for f1, f2 in zip(fs, fs[1:]):
        A = {(i, e['name']): (e['value'], e['date']) for i, q in enumerate(json.load(gzip.open(f1))['qubits']) for e in q}
        B = {(i, e['name']): (e['value'], e['date']) for i, q in enumerate(json.load(gzip.open(f2))['qubits']) for e in q}
        ch.append('CHANGED' if any(A[k] != B[k] for k in A.keys() & B.keys()) else 'NO_CHANGE')
    print(d.split('/')[-1], 'records', len(fs), '| A ABOVE', na, 'CANNOT_TELL', nc, '| B mismatch', nb, '| >24h', a24, '>7d', a7, 'of', n, '| restamps', {k: ch.count(k) for k in set(ch)})
