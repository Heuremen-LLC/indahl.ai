"""fedsep_score.py: the scoring step of fedsep_index/fedsep_tick.py (inside, line 24, the triples loop and pooled(), lines 49 to 69), as written,
with the same random.Random(7) stream in the same call order. Reads data/projections.json (the SEP tables as parsed) and data/outcomes_day.json
(the outcomes read from BEA, BLS and the Board on the day of the run), writes out.json."""
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import json, random
import heuremen_kit as K
SEPT = ['20150917', '20160921', '20170920', '20180926', '20190918', '20200916', '20210922', '20220921', '20230920', '20240918', '20250917']
VARS = ['Change in real GDP', 'Unemployment rate', 'PCE inflation', 'Federal funds rate']
inside = lambda med, out, rng: abs(out - med) <= rng + 1e-9
proj = json.load(open('data/projections.json')); O = {int(k): v for k, v in json.load(open('data/outcomes_day.json'))['O'].items()}
trip = []; SK = []
for d in SEPT:
    s = int(d[:4])
    for hz in (0, 1):
        ty = s + hz
        if ty > 2025: continue
        for v in VARS:
            alt = O.get(ty, {}).get('Federal funds rate, year-end') if v == 'Federal funds rate' else None
            med = proj[d]['t1'].get(v, [None] * 4)[hz]; rng = proj[d]['t2'].get(v, [None] * 4)[hz] if proj[d]['t2'].get(v) else None; out = O.get(ty, {}).get(v)
            if med is None or rng is None or out is None: SK.append((s, hz, v)); continue
            trip.append(dict(sept=s, horizon=hz, target=ty, var=v, median=med, rng=rng, outcome=round(out, 2), err=round(out - med, 2), outside=not inside(med, out, rng), outside_alt=(not inside(med, alt, rng)) if alt is not None else (not inside(med, out, rng))))
rnd = random.Random(7)
def pooled(hz, alt=False):
    flag = 'outside_alt' if alt else 'outside'
    ts = [t for t in trip if t['horizon'] == hz]; yrs = sorted({t['sept'] for t in ts}); by = {y: [t for t in ts if t['sept'] == y] for y in yrs}; k = sum(t[flag] for t in ts)
    bs = []
    for _ in range(4000):
        sm = [t for y in (rnd.choice(yrs) for _ in yrs) for t in by[y]]; bs.append(sum(t[flag] for t in sm) / len(sm))
    bs.sort(); lo, hi = bs[int(0.025 * 4000)], bs[int(0.975 * 4000)]
    ok_ = len(ts) > 0 and len(yrs) >= 2; oc = K.read(lo if ok_ else None, hi if ok_ else None, bound=0.30)[0]   # 12 Nov 2026: Faults and Guards 2.0, as fedsep_tick.py
    return dict(triples=len(ts), years=len(yrs), outside=k, share=round(k / len(ts), 4), share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc)
pool = {'This year, September projection': pooled(0), 'Next year, September projection': pooled(1)}
json.dump(dict(pooled=pool), open('out.json', 'w'), indent=1)
