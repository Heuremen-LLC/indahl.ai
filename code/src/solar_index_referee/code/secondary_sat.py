src = open('/Users/heuremen/bones-forge/solar_index_referee/code/recount.py').read().split('# ---------- diff vs desk')[0]
exec(src)
lines = []   # (day_max, obs, cls letter)
for ds, tx in events_files():
    d0 = dt.date(int(ds[:4]), int(ds[4:6]), int(ds[6:]))
    for ln in tx.splitlines():
        if ' XRA ' not in ln: continue
        t = ln.split(); k = t.index('XRA'); mm = re.fullmatch(r'([A-Z])(\d+(?:\.\d+)?)', t[k+2])
        if not mm: continue
        pre = [x for x in t[:k] if x != '+']; b, m_ = hm(pre[1]), hm(pre[2])
        d = d0 + dt.timedelta(1) if (m_ is not None and b is not None and m_ < b) else d0
        lines.append((d, pre[4], mm[1]))
obs_all = C.Counter(o for _, o, _ in lines); print('XRA lines by observer:', dict(obs_all))
mon = C.defaultdict(C.Counter)
for d, o, l in lines: mon[(d.year, d.month)][o] += 1
prim = {k: v.most_common(1)[0][0] for k, v in mon.items()}
byday = C.defaultdict(lambda: C.defaultdict(set))
for d, o, l in lines: byday[d][o].add(l)
only_sec = []; days_m = 0
for d, dd in byday.items():
    if not any(l in 'MX' for ls in dd.values() for l in ls): continue
    days_m += 1
    p = prim[(d.year, d.month)]
    if not any(l in 'MX' for l in dd.get(p, set())): only_sec.append((str(d), {o: sorted(ls) for o, ls in dd.items()}))
print('M+ days', days_m, 'days where only a non-primary (month-majority) observer logged M or X:', len(only_sec)); print(only_sec[:10])
