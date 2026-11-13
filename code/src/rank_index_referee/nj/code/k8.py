"""Referee recompute of NJ K-8 display figures (levels 4+5 weighted by valid scores), both years."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import xl

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL = os.path.join(HERE, 'dl')
K8 = {
    '31-4010-310': ('School 28', 96, 97), '27-0785-060': ('Milton Avenue', 98, 95), '13-3190-070': ('Glenwood', 92, 94),
    '17-2390-340': ('Cornelia F. Bradford', 89, 92), '80-6081-967': ('Thomas Edison EnergySmart', 89, 94),
    '80-7540-930': ('Princeton Charter', 90, 88), '13-2730-090': ('Harrison', 85, 88), '25-4980-050': ('H W Mountz', 87, 92),
    '03-1760-065': ('Alexander Hamilton', 91, 87), '03-4390-120': ('Orchard', 88, 87), '17-2390-002': ('Infinity Institute', 100, 100),
    '27-3100-060': ('Mendham Township MS', 89, 98), '25-4570-050': ('Forrestdale', 85, 91), '25-2720-050': ('Markham Place', 83, 94),
    '80-6036-921': ('Hoboken Dual Language CS', 78, 91), '17-5240-140': ('Sara M. Gilmore', 75, 92),
}
MATH = ['MAT03', 'MAT04', 'MAT05', 'MAT06', 'MAT07', 'MAT08', 'ALG01', 'GEO01', 'ALG02']
ELA = ['ELA03', 'ELA04', 'ELA05', 'ELA06', 'ELA07', 'ELA08', 'ELA09']


def load(t, y):
    p = os.path.join(DL, f'{t}_{y}.xlsx')
    out = {}
    for _, r, a in xl.rows(p):
        if r <= 3 or len(a) < 12:
            continue
        k = f'{a[0]}-{a[2]}-{a[4]}'
        if k in K8 and a[6] == 'Total':
            out[k] = (r, a[10], a[15] if len(a) > 15 else '', a[16] if len(a) > 16 else '')
    return out


def num(x):
    try:
        return float(x)
    except Exception:
        return None


res = {}
for y in ('2324', '2425'):
    data = {t: load(t, y) for t in MATH + ELA}
    for k, (nm, um, ur) in K8.items():
        for subj, tests, usn in (('math', MATH, um), ('read', ELA, ur)):
            n = d = 0.0
            supp, used = [], []
            for t in tests:
                row = data[t].get(k)
                if not row:
                    continue
                r, v, l4, l5 = row
                if num(v) is None:
                    supp.append(t)
                    continue
                n += num(v) * ((num(l4) or 0) + (num(l5) or 0))
                d += num(v)
                used.append(f'{t}:{int(num(v))}')
            val = round(n / d, 2) if d else None
            res.setdefault(nm, {})[f'{subj}_{y}'] = dict(all_rows=None if supp else val, valid_only=val, valid=int(d), suppressed=supp, used=used, usn=usn)

json.dump(res, open(os.path.join(HERE, 'out', 'k8_recompute.json'), 'w'), indent=1)
for nm, d in res.items():
    for subj in ('math', 'read'):
        a, b = d[f'{subj}_2324'], d[f'{subj}_2425']
        print(f"{nm[:22]:22} {subj} usn {a['usn']:>3} | 23-24 {a['all_rows']} (valid-only {a['valid_only']}, n={a['valid']}, supp {a['suppressed']}) | 24-25 {b['all_rows']} (valid-only {b['valid_only']}, n={b['valid']}, supp {b['suppressed']})")
