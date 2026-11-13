"""linkrot_score.py: the summary step of linkrot_index/linkrot_tick.py (cell() and combined(), lines 84 to 92, and the all cell of out, line 101), as written.
The gate result is the one the desk recorded in summary_linkrot.json (its live probes cannot be replayed). Reads data/links.json, writes out.json."""
import json, collections as C
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import heuremen_kit as K
links = json.load(open('data/links.json')); gate_ok = json.load(open('summary_linkrot.json'))['gate'] == 'passed'
def cell(rows):
    c = C.Counter(r for r in rows); live, gone, dns = c['LIVE'], c['GONE'], c['DNS_FAIL']; rd = live + gone + dns; rot = gone + dns
    lo, hi = K.wilson(rot, rd)
    oc = K.CANNOT_TELL if (rd < 30 or not gate_ok) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
    return dict(links=len(rows), live=live, gone=gone, dns_fail=dns, blocked=c['BLOCKED'], timeout=c['TIMEOUT'], rot_share=round(rot / rd, 4) if rd else None, lo=round(lo, 4), hi=round(hi, 4), outcome=oc)
def combined(e):
    a = e['hist'][-1]; b = e.get('seat2'); bad = ('GONE', 'DNS_FAIL')
    if b and abs(a[0] - b[0]) <= 14 * 86400:
        if (a[1] == 'LIVE' and b[1] in bad) or (a[1] in bad and b[1] == 'LIVE'): return 'BLOCKED'
    return a[1]
cur = {u: combined(e) for u, e in links.items() if e['hist']}
json.dump(dict(gate='passed' if gate_ok else 'FAILED', all=cell(list(cur.values()))), open('out.json', 'w'), indent=1)
