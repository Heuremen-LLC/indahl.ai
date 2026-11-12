"""secrecords_score.py: the summary step of secrecords_index/secrecords_tick.py (read_share() and grp(), lines 150 to 160, and the comparison block of out), as written; 12 Nov 2026 moved to the Faults and Guards 2.0 read with the desk.
The gate result is the one the desk recorded in summary_secrecords.json. Reads data/domains.json, writes out.json."""
import json, collections as C
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import heuremen_kit as K
store = json.load(open('data/domains.json')); gate = json.load(open('summary_secrecords.json'))['gate'] == 'passed'; rs = list(store.values())
def read_share(k, n, gate):
    lo, hi = K.wilson(k, n); lo = 0.0 if k == 0 else lo; hi = 1.0 if k == n else hi
    if not gate or n == 0: return K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE
    if n < 30: return K.CANNOT_TELL, K.TOO_WIDE_TO_RESOLVE
    return K.read(lo, hi, band=(0.0, 0.05), matters=0.10, edge='[)')
def grp(key):
    cnt = C.Counter(r[key + '_cls'] for r in rs); comp = cnt['AGREE'] + cnt['DISAGREE']; lo, hi = K.wilson(cnt['DISAGREE'], comp)
    oc, _why = read_share(cnt['DISAGREE'], comp, gate)
    return cnt, dict(of=comp, n=cnt['DISAGREE'], share=round(cnt['DISAGREE'] / comp, 4) if comp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc)
ch, cmp_h = grp('hsts'); cs, cmp_s = grp('spf')
json.dump(dict(gate='passed' if gate else 'FAILED', domains=len(rs), comparison={'HSTS preload header': cmp_h, 'SPF lookup limit': cmp_s}), open('out.json', 'w'), indent=1)
