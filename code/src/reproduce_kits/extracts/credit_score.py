"""credit_score.py: ruler one for 2025 of credit_index/credit_tick.py (PRINTED, line 23, the constants, line 39, seed_of() and boot(), lines 128 to
141, the company-month blocks, lines 143 to 149, r4(), line 150, and the ruler-one row, lines 195 to 200), as written, with the same numpy seed.
Reads the company-month counts the run aggregated from the CFPB complaint file (data/cache/agg_<first 16 of the file's sha256>.json, its T table),
writes out.json."""
import os as _o, sys as _s, glob as _g; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import json, zlib, collections as C
import numpy as np
import heuremen_kit as K
PRINTED = {2025: ('99.6%', 0.9955, 0.9965, 5900000, 'more than 5.9 million')}
MIN_ROWS, MIN_MONTHS, NBOOT, SEED = 1000, 10, 2000, 20261110
fs = _g.glob('data/cache/agg_*.json')
if len(fs) != 1: _s.exit('expected one aggregate file, found %d' % len(fs))
AG = json.load(open(fs[0]))
def seed_of(name): return [SEED, zlib.crc32(name.encode())]
def boot(num, den, name):
    num = np.asarray(num, float); den = np.asarray(den, float); B = len(num)
    if B == 0 or den.sum() == 0: return None, None, None
    est = num.sum() / den.sum()
    rng = np.random.default_rng(seed_of(name)); out = []; left = NBOOT; step = max(1, min(NBOOT, 4_000_000 // max(B, 1)))
    while left > 0:
        k = min(step, left); w = rng.multinomial(B, np.full(B, 1.0 / B), size=k)
        dd = w @ den; nn = w @ num; ok = dd > 0; out.extend((nn[ok] / dd[ok]).tolist()); left -= k
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(est), float(lo), float(hi)
T = C.defaultdict(lambda: [0, 0])
for co, m, fam, n, no in AG['T']:
    x = T[(co, m)]; x[0] += n; x[1] += no
def blocks(sel):
    num, den = [], []
    for (co, m), (n, no) in T.items():
        if sel(co, m): num.append(n - no); den.append(n)
    return num, den
def r4(x): return None if x is None else round(x, 6)
ruler1 = []
for y in (2025,):
    num, den = blocks(lambda co, m, y=y: m.startswith(str(y)))
    e, lo, hi = boot(num, den, 'pooled %d' % y); txt, blo, bhi, sent, senttxt = PRINTED[y]
    ruler1.append(dict(year=y, rows=int(sum(den)), not_timely=int(sum(den) - sum(num)), company_months=len(den), timely=r4(e), lo=r4(lo), hi=r4(hi), printed=txt, band=[blo, bhi], outcome=K.classify(lo, hi, blo, bhi)))
json.dump(dict(ruler1=ruler1), open('out.json', 'w'), indent=1)
