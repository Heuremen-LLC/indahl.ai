#!/usr/bin/env python3
"""uptime_summary.py: scores UPTIME rounds per PLAN.md and writes summary_uptime.json. Buckets of 10 minutes. Seats: mac, pi, github-azure."""
import os, json, math, time, glob, collections as C
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
rows = []
for f in ('data/probe_mac.jsonl', 'data/probe_pi.jsonl', 'data/probe_runner.jsonl'):
    if os.path.exists(f):
        for l in open(f):
            try: rows.append(json.loads(l))
            except Exception: pass
B = lambda t: t // 600
V = json.load(open('vendors.json')); order = [v['name'] for v in V]; ctl = {v['name'] for v in V if v.get('control')}
stat = {}; pr = C.defaultdict(lambda: C.defaultdict(list)); seats = set()
for r in rows:
    b = B(r['round'])
    if r['kind'] == 'status' and r.get('indicator') is not None: stat[(r['vendor'], b)] = r['indicator']
    elif r['kind'] == 'probe': pr[(r['vendor'], b)][r['seat']].append(r['ok']); seats.add(r['seat'])
inc = json.load(open('incidents.json')) if os.path.exists('incidents.json') else {}
last_ind = {}
for (v, b), i in sorted(stat.items(), key=lambda x: x[0][1]): last_ind[v] = i
res = {}
for v in order:
    n = dis = con = blip = quiet = 0; ok_by = C.defaultdict(lambda: [0, 0])
    for (vv, b), s in pr.items():
        if vv != v: continue
        for seat, oks in s.items(): ok_by[seat][1] += 1; ok_by[seat][0] += all(oks)
        if len(s) < 2: continue
        fails = {k for k, oks in s.items() if not all(oks)}
        if v in ctl:
            n += 1; dis += len(fails) >= 2; blip += len(fails) == 1; quiet += len(fails) == 0; continue
        ind = stat.get((v, b))
        if ind is None: continue
        n += 1
        if len(fails) >= 2: (dis if ind == 'none' else con).__class__  # no-op for readability
        if len(fails) >= 2 and ind == 'none': dis += 1
        elif len(fails) >= 2: con += 1
        elif len(fails) == 1: blip += 1
        else: quiet += 1
    res[v] = dict(rounds=n, disagree=dis, confirm=con, blips=blip, quiet=quiet, reach={k: round(100 * a / b, 1) for k, (a, b) in ok_by.items() if b})
cr = [res[c] for c in ctl if c in res]; cn = sum(c['rounds'] for c in cr); cm = sum(c['disagree'] for c in cr); floor = cm / cn if cn else 0.0
vend = []
for v in order:
    if v in ctl: continue
    r = res[v]; exp = floor * r['rounds']
    oc = 'CANNOT_TELL' if r['rounds'] < 300 else ('BELOW' if r['disagree'] > exp + 2 * math.sqrt(max(exp, 1e-9)) else 'CONSISTENT')
    vend.append(dict(vendor=v, indicator_now=last_ind.get(v), incidents=inc.get(v, []), outcome=oc, expected_from_floor=round(exp, 2), **r))
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), seats=sorted(seats), buckets=len({b for (_, b) in pr}), control=dict(rounds=cn, misses=cm, floor=round(floor, 4), targets=sorted(ctl)), vendors=vend,
           totals=dict(C.Counter(x['outcome'] for x in vend)))
json.dump(out, open('summary_uptime.json', 'w'), indent=1); print(out['updated'], out['seats'], 'buckets', out['buckets'], 'control floor', out['control'])
