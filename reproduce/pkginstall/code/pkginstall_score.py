"""pkginstall_score.py: the summary step of pkginstall_index/pkginstall_tick.py (lines 112 to 113 and the comparison block of out, line 116), as written.
It recounts the class pip gave each project's install command when the desk read it. pip and the live PyPI index cannot be replayed, so the classes
are inputs. The gate result is the one the desk recorded in summary_pkginstall.json. Reads data/projects.json, writes out.json."""
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import json, collections as C
import heuremen_kit as K
store = json.load(open('data/projects.json')); gate = json.load(open('summary_pkginstall.json'))['gate'] == 'passed'
rs = list(store.values()); cnt = C.Counter(r['cls'] for r in rs); comp = cnt['AGREE'] + cnt['DISAGREE']; lo, hi = K.wilson(cnt['DISAGREE'], comp)
oc = K.CANNOT_TELL if (comp < 30 or not gate) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
json.dump(dict(gate='passed' if gate else 'FAILED', projects=len(rs), comparison=dict(of=comp, n=cnt['DISAGREE'], share=round(cnt['DISAGREE'] / comp, 4) if comp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc)), open('out.json', 'w'), indent=1)
