#!/usr/bin/env python3
"""caca_summary.py: reads data/queries.jsonl and writes summary_caca.json per PLAN.md. Share blocked of alive domains per resolver and checkpoint with Wilson 95%."""
import json, os, math, time, collections as C
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
import heuremen_kit as _K
def wil(k, n):   # 29 Oct: kit's tested Wilson; the cadence copy omitted the division by d
    if not n: return None
    p = k / n; lo, hi = _K.wilson(k, n); return [round(100 * p), round(100 * lo), round(100 * hi)]
rows = [json.loads(l) for l in open('data/queries.jsonl')] if os.path.exists('data/queries.jsonl') else []
by = C.defaultdict(dict)
for r in rows: by[(r['domain'], r['cp'])][r['resolver']] = r
res = {}; CP = [0, 3600, 21600, 86400]; ALIVE = C.Counter(); notalive = C.Counter(); status = C.defaultdict(C.Counter); domains = set()
for (d, cp), rs in by.items():
    domains.add(d); ctl = [r for r in rs.values() if r['group'] == 'control' and r['cls'] == 'ANSWERED']
    sets = C.Counter(tuple(sorted(r['ips'])) for r in ctl); alive = bool(sets) and max(sets.values()) >= 2
    if not alive: notalive[cp] += 1; continue
    ALIVE[cp] += 1
    for n, r in rs.items():
        if r['group'] != 'filtered': continue
        x = res.setdefault(n, {c: [0, 0] for c in CP}); x[cp][1] += 1; x[cp][0] += r['cls'] in ('NXDOMAIN', 'REFUSED', 'SINK'); status[n][r['cls']] += 1
feeds = [json.loads(l) for l in open('data/feed_reads.jsonl')] if os.path.exists('data/feed_reads.jsonl') else []
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), tracked=len(domains), alive={str(c): ALIVE[c] for c in CP}, not_alive={str(c): notalive[c] for c in CP},
           feed_reads=len([f for f in feeds if f.get('status') == 'COMMITTED' and not f.get('baseline')]), resolvers=[
    dict(resolver=n, checkpoints={str(c): dict(k=v[c][0], n=v[c][1], wilson=wil(*v[c])) for c in CP}, classes=dict(status[n])) for n, v in sorted(res.items())])
json.dump(out, open('summary_caca.json', 'w'), indent=1); print('caca summary:', out['tracked'], 'domains,', out['feed_reads'], 'fresh reads')
