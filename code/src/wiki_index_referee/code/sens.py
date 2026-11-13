import sys, gzip, json, collections as C
from decimal import Decimal
sys.path.insert(0, '.')
import recount as R
ROOT = '/Users/heuremen/bones-forge/wiki_index'
rows = json.load(gzip.open('out/ref_rows.json.gz','rt'))
srcs = {}
for gid, (prop, src, series, units) in R.G.items():
    if src == 'WB': cur, older, _, _ = R.wb_tables(series)
    else: cur, older, *_ = R.uis_tables(series)
    srcs[gid] = (cur, older)
res = C.defaultdict(C.Counter); ex = C.defaultdict(list)
for r in rows:
    cur, older = srcs[r['group']]
    v = Decimal(r['v']); u = Decimal(r['u']); uw = Decimal(r['uw'])
    b0 = r['bin']
    # 1) written unit without the three-digit floor
    if uw != u:
        b1 = R.bin_of(v, uw, r['iso'], r['year'], cur, older)[0]
        res[r['group']][f'floor matters: {b0} -> {b1}'] += 1
        if b1 != b0 and len(ex['floor'])<12: ex['floor'].append((r['group'], r['item'], r['year'], r['value'], str(u), str(uw), b0, b1, r['current']))
    # 2) no single-precision allowance
    b2 = R.bin_of(v, u, r['iso'], r['year'], cur, older, m=R.match_strict)[0]
    if b2 != b0:
        res[r['group']][f'f32 matters: {b0} -> {b2}'] += 1
        if len(ex['f32'])<12: ex['f32'].append((r['group'], r['item'], r['year'], r['value'], b0, b2, r['current']))
    # 3) Wikidata stated bounds as the tolerance (when present)
    if r['ubound'] is not None:
        ub, lb = Decimal(r['ubound']), Decimal(r['lbound'])
        half = max(ub - v, v - lb)
        res[r['group']][f'bounds half-width {half} vs u/2 {u/2}'] += 1
        def mb(vv, uu, rr): return (lb - Decimal('1e-9') <= rr <= ub + Decimal('1e-9')) or R.match(vv, uu, rr)
        b3 = R.bin_of(v, u, r['iso'], r['year'], cur, older, m=mb)[0]
        if b3 != b0:
            res[r['group']][f'bounds matter: {b0} -> {b3}'] += 1
            if len(ex['bounds'])<15: ex['bounds'].append((r['group'], r['item'], r['year'], r['value'], r['lbound'], r['ubound'], b0, b3, r['current']))
for g in res:
    print(g)
    for k, n in sorted(res[g].items()): print('   ', n, k)
for k, v in ex.items():
    print('EXAMPLES', k)
    for x in v: print('   ', x)
