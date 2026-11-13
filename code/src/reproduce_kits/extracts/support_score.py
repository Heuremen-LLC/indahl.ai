"""support_score.py: the summary step of support_index/support_tick.py (lines 66 to 74 and the all cell, lines 85 to 87), as written. The state and
unreleased class of each cycle were set when the desk read endoflife.date, and are stored per row. The gate result is the one the desk recorded in
summary_support.json. Reads data/cycles.json, writes out.json."""
import json, random, collections as C
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import heuremen_kit as K
rows = json.load(open('data/cycles.json')); gate = json.load(open('summary_support.json'))['gate'] == 'passed'
for _r in rows:
    if 'unreleased' not in _r: _r['unreleased'] = _r.pop('silent', False)
tested = [r for r in rows if r['state'] == 'SUPPORTED']; sil = [r for r in tested if r['unreleased']]
def boot_cluster(byprod, n_boot=4000):
    rnd = random.Random(7); P = list(byprod); est = []
    for _ in range(n_boot):
        ch = [rnd.choice(P) for _ in P]; n = sum(len(byprod[p]) for p in ch); k = sum(sum(byprod[p]) for p in ch); est.append(k / n if n else 0)
    est.sort(); return est[int(0.025 * n_boot)], est[int(0.975 * n_boot) - 1]
def cell(n, k):
    lo, hi = K.wilson(k, n); oc = K.CANNOT_TELL if (n < 30 or not gate) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
    return dict(tested=n, unreleased=k, share=round(k / n, 4) if n else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc)
byp = C.defaultdict(list)
for r in tested: byp[r['product']].append(r)
byprod_all = {p: [bool(r['unreleased']) for r in v] for p, v in byp.items()}
c_lo, c_hi = boot_cluster(byprod_all) if byprod_all else (0, 1)
allc = cell(len(tested), len(sil)); allc.update(wilson_lo=allc['share_lo'], wilson_hi=allc['share_hi'], share_lo=round(c_lo, 4), share_hi=round(c_hi, 4), products_tested=len(byprod_all))
allc['outcome'] = K.CANNOT_TELL if (len(tested) < 30 or not gate) else (K.ABOVE if c_lo > 0.10 else (K.CONSISTENT if c_hi < 0.05 else K.CANNOT_TELL))
json.dump(dict(gate='passed' if gate else 'FAILED', all=allc), open('out.json', 'w'), indent=1)
