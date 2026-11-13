src = open('/Users/heuremen/bones-forge/solar_index_referee/code/recount.py').read().split('# ---------- diff vs desk')[0]
exec(src)
old = {}
for r in allparsed:
    k = r['iss'].date()
    if k < dt.date(2021,1,1): continue
    if k not in old or r['iss'] < old[k]['iss']: old[k] = r
for ev in ('M', 'X', 'MID5', 'HI5'):
    added = []
    for d, r in stated.items():
        tg = d + dt.timedelta(1)
        if r['d1'] != tg or r['iss'] >= dt.datetime.combine(tg, dt.time()) or tg >= SETTLED: continue
        o, w = obs(ev, tg)
        if o is None: continue
        ro = old.get(d)
        if ro is None or ro['d1'] != d + dt.timedelta(1):   # not scorable under the old key
            added.append((r[{'M':'M','X':'X','MID5':'mid_mi','HI5':'hi_mi'}[ev]][0], o))
    n = len(added); print(ev, 'lead-1 rows added by the new report-day rule:', n, 'event days among them', sum(o for p, o in added), 'share %.2f' % (sum(o for p, o in added) / max(n, 1)))
