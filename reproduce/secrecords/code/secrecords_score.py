"""secrecords_score.py: the summary step of secrecords_index/secrecords_tick.py (grp(), lines 140 to 143, and the comparison block of out), as written.
The gate result is the one the desk recorded in summary_secrecords.json. Reads data/domains.json, writes out.json."""
import json, collections as C
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import heuremen_kit as K
store = json.load(open('data/domains.json')); gate = json.load(open('summary_secrecords.json'))['gate'] == 'passed'; rs = list(store.values())
def grp(key):
    cnt = C.Counter(r[key + '_cls'] for r in rs); comp = cnt['AGREE'] + cnt['DISAGREE']; lo, hi = K.wilson(cnt['DISAGREE'], comp)
    oc = K.CANNOT_TELL if (comp < 30 or not gate) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
    return cnt, dict(of=comp, n=cnt['DISAGREE'], share=round(cnt['DISAGREE'] / comp, 4) if comp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc)
ch, cmp_h = grp('hsts'); cs, cmp_s = grp('spf')
json.dump(dict(gate='passed' if gate else 'FAILED', domains=len(rs), comparison={'HSTS preload header': cmp_h, 'SPF lookup limit': cmp_s}), open('out.json', 'w'), indent=1)
