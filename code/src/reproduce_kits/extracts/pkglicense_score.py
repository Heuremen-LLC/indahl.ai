"""pkglicense_score.py: the summary step of pkglicense_index/pkglicense_tick.py (lines 97 to 98 and the disagree block of out, line 102), as written.
The desk scores the top 1,000 PyPI projects of its list date and does not store that list. The same list, of the same date, is stored by the
PKGINSTALL desk with each project's rank (pkginstall/data/projects.json), so the names are read from there in rank order. The gate result is the
one the desk recorded in summary_pkglicense.json, which also names the list date. Reads data/projects.json, writes out.json."""
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import json, collections as C
import heuremen_kit as K
prev = json.load(open('summary_pkglicense.json')); gate = prev['gate'] == 'passed'
top = json.load(open('pkginstall/data/projects.json')); names = [r['project'] for r in sorted(top.values(), key=lambda r: r['rank'])][:1000]
if open('pkginstall/data/listdate.txt').read().strip() != prev['list_date'].strip(): _s.exit('the PKGINSTALL list is not the list date PKGLICENSE scored')
projects = json.load(open('data/projects.json'))
rows = {n: projects[n] for n in names if n in projects and projects[n].get('cls')}; cnt = C.Counter(r['cls'] for r in rows.values()); comp = cnt['AGREE'] + cnt['DISAGREE']
lo, hi = K.wilson(cnt['DISAGREE'], comp); oc = K.CANNOT_TELL if (comp < 30 or not gate) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
json.dump(dict(gate='passed' if gate else 'FAILED', projects=len(names), read=len(rows), comparable=comp, disagree=dict(n=cnt['DISAGREE'], of=comp, share=round(cnt['DISAGREE'] / comp, 4) if comp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc)), open('out.json', 'w'), indent=1)
