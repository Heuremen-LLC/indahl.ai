"""hfsize_score.py: the summary step of hfsize_index/hfsize_tick.py (lines 56 to 57 and the comparison block of out, line 63), as written.
The gate result is the one the desk recorded in summary_hfsize.json. Reads data/repos.json, writes out.json."""
import json, collections as C
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import heuremen_kit as K
store = json.load(open('data/repos.json')); gate = json.load(open('summary_hfsize.json'))['gate'] == 'passed'
rs = list(store.values()); cnt = C.Counter(r['cls'] for r in rs); comp = cnt['AGREE'] + cnt['DISAGREE']; lo, hi = K.wilson(cnt['DISAGREE'], comp)
k_ = cnt['DISAGREE']   # 12 Nov 2026: Faults and Guards 2.0, as hfsize_tick.py read_share (PLAN_ADDENDUM_std2.md)
oc = K.CANNOT_TELL if (not gate or comp == 0 or comp < 30) else K.read(0.0 if k_ == 0 else lo, 1.0 if k_ == comp else hi, band=(0.0, 0.05), matters=0.10, edge='[)')[0]
json.dump(dict(gate='passed' if gate else 'FAILED', models=len(rs), comparison=dict(of=comp, n=cnt['DISAGREE'], share=round(cnt['DISAGREE'] / comp, 4) if comp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc)), open('out.json', 'w'), indent=1)
