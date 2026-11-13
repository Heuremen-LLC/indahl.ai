"""cone_score.py: the whole-path cells of cone_index/cone_tick.py (constants, lines 18 to 25, boot() and cell_read(), lines 200 to 222, sel() and the
whole-path cells, lines 398 to 401), as written, over the scored paths that run wrote to data/cone.json. A failed gate is already written into the
stored paths (lines 391 to 394). Writes out.json."""
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import json, math, random, collections as C
import heuremen_kit as K
WP_BAND = (0.60, 0.70); B_RESAMPLES = 2000; SEED = 20261110; MIN_STORMS = 10; MIN_ROWS = 30
INSIDE, OUTSIDE = 'INSIDE', 'OUTSIDE'
paths = json.load(open('data/cone.json'))['paths']
def boot(groups, stat='share', seed=SEED, B=B_RESAMPLES):
    g = [x for x in groups if x[1] > 0]
    if not g: return None, None
    rng = random.Random(seed); m = len(g); vals = []
    for _ in range(B):
        k = n = 0
        for _i in range(m):
            a, b = g[rng.randrange(m)]; k += a; n += b
        vals.append(k / n)
    vals.sort(); return vals[int(0.025 * B)], vals[min(B - 1, int(math.ceil(0.975 * B)) - 1)]
def cell_read(rows, band):
    by = C.defaultdict(lambda: [0, 0]); cnt = C.Counter(); why = C.Counter()
    for r in rows:
        cnt[r['outcome']] += 1
        if r.get('why'): why[r['why']] += 1
        if r['outcome'] in (INSIDE, OUTSIDE): by[r['storm']][1] += 1; by[r['storm']][0] += (r['outcome'] == INSIDE)
    k, n = cnt[INSIDE], cnt[INSIDE] + cnt[OUTSIDE]; storms = len(by)
    lo, hi = boot(list(by.values())) if n else (None, None)
    if storms < MIN_STORMS or n < MIN_ROWS: o = K.CANNOT_TELL
    else: o = K.classify(lo, hi, band[0], band[1])
    return dict(scored=n, inside=k, outside=cnt[OUTSIDE], storms=storms, share=round(k / n, 4) if n else None, lo=None if lo is None else round(lo, 4), hi=None if hi is None else round(hi, 4),
                band=list(band), outcome=o, nothing_returned=cnt[K.NOTHING_RETURNED], nothing_returned_why=dict(why), cannot_tell=cnt[K.CANNOT_TELL])
BN = {'AL': 'Atlantic', 'EP': 'East Pacific'}
def sel(rs, **kw): return [r for r in rs if r['outcome'] != 'NO_RADII' and all(r[k] == v for k, v in kw.items())]
cells = []
for b in ('AL', 'EP'):
    c = cell_read(sel(paths, basin=b, grp='final'), WP_BAND); c.update(cell='%s, whole path' % BN[b], basin=b, kind='whole path', lead=None); cells.append(c)
json.dump(dict(cells=cells), open('out.json', 'w'), indent=1)
