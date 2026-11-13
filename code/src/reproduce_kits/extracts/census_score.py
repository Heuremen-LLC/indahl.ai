"""census_score.py: the cell step of census_index/census_tick.py (cells(), the Wilson interval and the outcome rule against 90 percent, as written),
for the national total cells. Reads data/census.json (every row with its outcome) and summary_census.json (the gate result of the same run), writes out.json."""
import json, collections as C
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import heuremen_kit as K
rows = json.load(open('data/census.json')); gate_ok = json.load(open('summary_census.json'))['gates']['passed']
out = []
for s in ('SALES', 'STARTS', 'COMPLETIONS', 'RETAIL'):
    for st in ('S1', 'S2', 'S3'):
        rs = [r for r in rows if r['series'] == s and r['geo'] == 'US' and r['step'] == st and r['width_basis'] == 'as served 2026']
        c = C.Counter(r['outcome'] for r in rs); k = c[K.CONSISTENT]; n = k + c[K.ABOVE] + c[K.BELOW]; lo, hi = K.wilson(k, n)
        oc = K.CANNOT_TELL if (n < 10 or not gate_ok) else (K.ABOVE if lo > 0.90 else (K.BELOW if hi < 0.90 else K.CONSISTENT))
        out.append(dict(series=s, geo='US', step=st, scored=n, inside=k, above=c[K.ABOVE], below=c[K.BELOW], share=(k / n) if n else None, lo=lo, hi=hi, outcome=oc))
json.dump(dict(cells=out), open('out.json', 'w'), indent=1)
