"""Referee recompute of NJ high school figures from the state's own files (re-pulled by the referee)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import xl

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL = os.path.join(HERE, 'dl')
HS = {
    ('03', '0290', '020'): 'Bergen County Academies',
    ('03', '0290', '070'): 'Bergen County Technical High School - Teterboro',
    ('17', '2390', '075'): 'Dr. Ronald E McNair High School',
    ('23', '3150', '010'): 'Edison Academy Magnet School',
    ('23', '3150', '070'): 'Woodbridge Academy Magnet School',
    ('25', '3260', '010'): 'High Technology High School',
    ('25', '3260', '028'): 'Biotechnology High School',
    ('39', '5260', '020'): 'Academy for Allied Health Sciences',
    ('39', '5260', '030'): 'Academy for Information Technology',
    ('39', '5260', '040'): 'Union County Magnet High School',
}


def test_rows(f):
    out = {}
    for name, r, a in xl.rows(os.path.join(DL, f)):
        if r <= 3 or len(a) < 12:
            continue
        key = (a[0], a[2], a[4])
        if key in HS and a[6] == 'Total':
            out[key] = dict(row=r, school=a[5], reg=a[8], nt=a[9], valid=a[10],
                            L=[x for x in a[12:]])
    return out


def f(x):
    try:
        return float(x)
    except Exception:
        return None


res = {k: {'name': v} for k, v in HS.items()}
for t in ['ALG01', 'GEO01', 'ALG02', 'ELA09', 'SC11']:
    rows = test_rows(f'{t}_2324.xlsx')
    for k in HS:
        res[k][t] = rows.get(k)

for k, d in res.items():
    num = den = 0.0
    parts = []
    for t in ['ALG01', 'GEO01', 'ALG02']:
        r = d.get(t)
        if r and f(r['valid']):
            v = f(r['valid'])
            p = (f(r['L'][3]) or 0) + (f(r['L'][4]) or 0)
            num += v * p
            den += v
            parts.append(f"{t} {p:.1f} of {int(v)} (row {r['row']})")
    d['math'] = round(num / den, 2) if den else None
    d['math_parts'] = parts
    r = d.get('ELA09')
    d['read'] = round(f(r['L'][3]) + f(r['L'][4]), 2) if r and f(r['valid']) else None
    r = d.get('SC11')
    d['sci'] = round(f(r['L'][2]) + f(r['L'][3]), 2) if r and f(r['valid']) else None

# SPR graduation, 2023-24 file, FederalGraduationRates
grad = {}
hdr = None
for name, r, a in xl.rows(os.path.join(DL, 'spr2324.xlsx'), sheet='FederalGraduationRates'):
    if hdr is None:
        hdr = a
        print('GRAD HDR', a)
        continue
    key = (a[0], a[2], a[4])
    if key in HS:
        grad.setdefault(key, []).append((r, a))
for k in HS:
    res[k]['grad_rows'] = grad.get(k, [])

json.dump({'|'.join(k): v for k, v in res.items()}, open(os.path.join(HERE, 'out', 'hs_recompute.json'), 'w'), indent=1)
for k, d in res.items():
    print(d['name'], '| math', d['math'], d['math_parts'], '| read', d['read'], '| sci', d['sci'])
    for r, a in d['grad_rows']:
        print('   grad row', r, a[5:])
