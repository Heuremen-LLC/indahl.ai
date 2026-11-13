#!/usr/bin/env python3
"""uptime_summary.py: scores UPTIME rounds per PLAN.md and writes summary_uptime.json. Buckets of 10 minutes. Seats: mac, pi, github-azure."""
import os, sys, json, math, time, glob, collections as C
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
sys.path.insert(0, os.path.join(H, '..', 'heuremen_kit')); import heuremen_kit as K   # 12 Nov 2026 (PLAN_ADDENDUM_std2.md): the canonical kit, imported by path
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
    n = dis = con = blip = quiet = unread = 0; ok_by = C.defaultdict(lambda: [0, 0]); dbuckets = []
    for (vv, b), s in pr.items():
        if vv != v: continue
        for seat, oks in s.items(): ok_by[seat][1] += 1; ok_by[seat][0] += all(oks)
        if len({('home' if k in ('mac', 'pi') else k) for k in s}) < 2: continue
        fails = {('home' if k in ('mac', 'pi') else k) for k, oks in s.items() if not all(oks)}   # 29 Oct (audit): the Mac and the Pi share one house network and are one seat
        if v in ctl:
            n += 1; dis += len(fails) >= 2; blip += len(fails) == 1; quiet += len(fails) == 0; continue
        ind = stat.get((v, b))
        if ind is None: unread += 1; continue   # 12 Nov 2026: a failed read of the status page, counted apart (NOTHING_RETURNED)
        n += 1
        if len(fails) >= 2: (dis if ind == 'none' else con).__class__  # no-op for readability
        if len(fails) >= 2 and ind == 'none': dis += 1; dbuckets.append(b)
        elif len(fails) >= 2: con += 1
        elif len(fails) == 1: blip += 1
        else: quiet += 1
    bs = sorted(set(dbuckets)); episodes = sum(1 for i, b in enumerate(bs) if i == 0 or b - bs[i - 1] > 1) if all(isinstance(b, int) for b in bs) else len(bs)
    res[v] = dict(status_unread=unread, episodes=episodes, rounds=n, disagree=dis, confirm=con, blips=blip, quiet=quiet, reach={k: round(100 * a / b, 1) for k, (a, b) in ok_by.items() if b})
cr = [res[c] for c in ctl if c in res]; cn = sum(c['rounds'] for c in cr); cm = sum(c['disagree'] for c in cr); floor = cm / cn if cn else 0.0
z = 1.96; floor_ub = ((cm / cn + z * z / (2 * cn) + z * math.sqrt((cm / cn) * (1 - cm / cn) / cn + z * z / (4 * cn * cn))) / (1 + z * z / cn)) if cn else 1.0   # 29 Oct (audit): zero misses in n rounds is not a zero rate
vend = []
for v in order:
    if v in ctl: continue
    r = res[v]; exp = floor_ub * r['rounds']
    # 12 Nov 2026 (PLAN_ADDENDUM_std2.md): one-sided. Agreement share = (rounds - disagreements) / rounds, Wilson 95 percent interval, bound = 1 - (exp + 2 sqrt(exp)) / rounds, edge closed, no size that matters named.
    thr = exp + 2 * math.sqrt(max(exp, 1e-9)); bnd = (1 - thr / r['rounds']) if r['rounds'] else None; ivl = None; why = None
    if r['rounds'] == 0: oc, why = 'CANNOT_TELL', K.NO_INTERVAL_FORMABLE
    elif r['rounds'] < 300: oc, why = 'CANNOT_TELL', K.TOO_WIDE_TO_RESOLVE
    else:
        wl, wh = K.wilson(r['rounds'] - r['disagree'], r['rounds']); ivl = [round(wl, 4), round(wh, 4)]
        oc, why = K.read(wl, wh, bound=bnd, edge='closed')
        if oc == 'BELOW' and r['episodes'] < 2: oc, why = 'CANNOT_TELL', K.TOO_WIDE_TO_RESOLVE
    r = dict(r, reason=why, agreement_interval=ivl, agreement_bound=None if bnd is None else round(bnd, 4))
    vend.append(dict(vendor=v, indicator_now=last_ind.get(v), incidents=inc.get(v, []), outcome=oc, expected_from_floor=round(exp, 2), **r))
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), seats=sorted(seats), seats_counted='the Mac and the Pi count as one seat', floor_upper_bound=round(floor_ub, 4), buckets=len({b for (_, b) in pr}), control=dict(rounds=cn, misses=cm, floor=round(floor, 4), targets=sorted(ctl)), vendors=vend,
           totals=dict(C.Counter(x['outcome'] for x in vend)), failed_reads=dict(status_page_unread={x['vendor']: x['status_unread'] for x in vend if x['status_unread']}),
           req13=K.req13([x for x in vend], nothing_returned=sum(x['status_unread'] for x in vend)), plan_addendum='PLAN_ADDENDUM_std2.md')
json.dump(out, open('summary_uptime.json', 'w'), indent=1); print(out['updated'], out['seats'], 'buckets', out['buckets'], 'control floor', out['control'])
