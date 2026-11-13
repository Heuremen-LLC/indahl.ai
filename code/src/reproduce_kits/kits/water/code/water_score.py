"""water_score.py: the band cells of water_index/water_tick.py (r2(), line 34, verdict() and oc(), lines 180 to 186, the band cell in the cells
loop, lines 213 to 220, and head, line 464), as written, over the rows that run wrote to data/water.json. The gate result is the one the run
recorded in summary_water.json (its known-good reports need the report PDFs, about 1.6 GB). Writes out.json."""
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import json
import heuremen_kit as K
rows = json.load(open('data/water.json')); GATE = json.load(open('summary_water.json'))['gate'] == 'passed'
def r2(x): return None if x is None else round(x, 2)
def verdict(lo, hi, claim, band, neff):
    if neff < 10: return K.CANNOT_TELL
    if lo > claim: return K.ABOVE
    if hi < claim: return K.BELOW
    if lo >= band[0] and hi <= band[1]: return K.CONSISTENT
    return K.CANNOT_TELL
def oc(r): return r.get('outcome_before_gate') or r['outcome']
head = {}
for key in ('mead', 'powell'):
    L = 6
    rs = [r for r in rows if r['res'] == key and r['lead'] == L]
    b = [r for r in rs if r.get('band_lo') is not None and r['measured'] is not None]
    k = sum(1 for r in b if oc(r) == K.CONSISTENT)
    ab = sum(1 for r in b if oc(r) == K.ABOVE); be = sum(1 for r in b if oc(r) == K.BELOW)
    neff = len(set(r['wy'] for r in b)); keff = round(neff * k / len(b)) if b else 0; lo, hi = K.wilson(keff, neff)
    bo = verdict(lo, hi, 0.80, (0.70, 0.90), neff) if GATE else K.CANNOT_TELL
    head[key] = dict(band=dict(n=len(b), inside=k, above=ab, below=be, share=r2(k / len(b)) if b else None, n_wy=neff, k_wy=keff, lo=round(lo, 3), hi=round(hi, 3), outcome=bo))
json.dump(dict(gate='passed' if GATE else 'FAILED', headline_lead6=head), open('out.json', 'w'), indent=1)
