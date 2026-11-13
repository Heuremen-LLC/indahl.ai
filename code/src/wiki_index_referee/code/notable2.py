import sys, gzip, json, collections as C
from decimal import Decimal
sys.path.insert(0, '.')
import recount as R
# DHY / XKS alias readings
rows = json.load(gzip.open('out/ref_rows.json.gz','rt'))
tabs = {}
for gid in ('WB-POP','WB-GDP','WB-GINI'):
    cur, older, _, _ = R.wb_tables(R.G[gid][2]); tabs[gid] = (cur, older)
alias = {'DHY': 'BEN', 'XKS': 'XKX'}
cnt = C.Counter()
for r in rows:
    if r['bin'] == 'SOURCE_UNREADABLE' and r['group'].startswith('WB'):
        cur, older = tabs[r['group']]
        b, hits, c = R.bin_of(Decimal(r['v']), Decimal(r['u']), [alias[r['iso'][0]]], r['year'], cur, older)
        cnt[b] += 1
        print(r['group'], r['iso'][0], '->', alias[r['iso'][0]], r['year'], r['value'], b, (hits[0][1], hits[-1][1]) if hits else None, 'current under alias', c)
print(dict(cnt))
# Argentina Gini 2020 and Germany 1995 across releases
cur, older = tabs['WB-GINI']
for iso, y in (('ARG', 2020), ('DEU', 1995)):
    vals = C.OrderedDict()
    for rid, lab, t in older:
        if t and (iso, y) in t: vals.setdefault(str(t[(iso, y)]), []).append(lab)
    print(iso, y, 'current', cur.get((iso, y)), {k: (v[0], v[-1], len(v)) for k, v in vals.items()})
# South Sudan LE 2016 across UIS versions and WB releases
cu, olderu, dflt, vs, utabs = R.uis_tables('SP.DYN.LE00.IN')
print('UIS SSD 2016 by version:', [(v, str(utabs[v].get(('SSD', 2016)))) for v, _ in vs])
print('UIS SSD 2013-2019 current:', [(y, str(cu.get(('SSD', y)))) for y in range(2010, 2021)])
wcur, wold, _, _ = R.wb_tables('SP.DYN.LE00.IN')
vals = C.OrderedDict()
for rid, lab, t in wold:
    if t and ('SSD', 2016) in t: vals.setdefault(str(t[('SSD', 2016)]), []).append(lab)
print('WB current SSD 2016 LE', wcur.get(('SSD', 2016)), 'WB archives:', {k: (v[0], v[-1], len(v)) for k, v in vals.items()})
print('WB current SSD LE 2010-2020', [(y, str(wcur.get(('SSD', y)))) for y in range(2010, 2021)])
