import sys, gzip, json, collections as C
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
sys.path.insert(0, '.')
import recount as R
rows = json.load(gzip.open('out/ref_rows.json.gz','rt'))
srcs = {}
for gid, (prop, src, series, units) in R.G.items():
    if src == 'WB': cur, older, _, _ = R.wb_tables(series)
    else: cur, older, *_ = R.uis_tables(series)
    srcs[gid] = (cur, older)
def lookup(t, iso, y):
    for i in iso:
        if (i, y) in t: return t[(i, y)]
def trunc_eq(v, u, r):
    # r truncated toward zero at unit u equals v
    q = (r / u).to_integral_value(rounding=ROUND_DOWN) * u
    return q == v
cat = C.defaultdict(C.Counter); ex = C.defaultdict(list)
for r in rows:
    cur, older = srcs[r['group']]
    v = Decimal(r['v']); u = Decimal(r['u'])
    c = lookup(cur, r['iso'], r['year'])
    strict = R.bin_of(v, u, r['iso'], r['year'], cur, older, m=R.match_strict)[0]
    # truncation-aware matcher: strict OR truncated copy
    def mt(vv, uu, rr): return R.match_strict(vv, uu, rr) or trunc_eq(vv, uu, rr)
    bt = R.bin_of(v, u, r['iso'], r['year'], cur, older, m=mt)[0]
    cat[r['group']][f'plan={r["bin"]} | strict={strict} | strict+trunc={bt}'] += 1
    if r['bin'] != bt and len(ex[r['group']]) < 6:
        ex[r['group']].append((r['item'], r['year'], r['value'], str(u), str(c), r['bin'], bt))
for g in cat:
    print(g)
    for k, n in sorted(cat[g].items(), key=lambda x: -x[1]): print('   ', n, k)
    for e in ex[g]: print('      ex', e)
