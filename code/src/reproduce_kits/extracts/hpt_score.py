"""hpt_score.py: the summary step of hpt_index/hpt_tick.py (grp(), lines 121 to 124, and the comparison block of out, line 128), as written.
The gate result is the one the desk recorded in summary_hpt.json (its live probes cannot be replayed). Reads data/domains.json, writes out.json."""
import json, collections as C
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import heuremen_kit as K
store = json.load(open('data/domains.json')); gate = json.load(open('summary_hpt.json'))['gate'] == 'passed'
def grp(key):
    cnt = C.Counter(r.get(key, 'NOT_RUN') for r in store.values()); comp = cnt['AGREE'] + cnt['DISAGREE']; lo, hi = K.wilson(cnt['DISAGREE'], comp)
    oc = K.CANNOT_TELL if (comp < 30 or not gate or key == 's1') else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
    return cnt, dict(of=comp, n=cnt['DISAGREE'], share=round(cnt['DISAGREE'] / comp, 4) if comp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc)
c1, g1 = grp('s1'); c2, g2 = grp('s2'); c3, g3 = grp('s3')
json.dump(dict(gate='passed' if gate else 'FAILED', domains=len(store), comparison={'1 A cms-hpt.txt at the root of the domain': g1, '2 The file it links resolves to data': g2, '3 The file starts with the template header': g3}), open('out.json', 'w'), indent=1)
