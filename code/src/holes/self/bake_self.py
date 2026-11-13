"""SELF TEST 2: does the copper read differently while the MAC IS BAKING (GPU training flat out, Mac council voices stood aside)?
Per bake: mean dB inside the window minus mean dB in the 2 h around it (window excluded), same day. Effect = mean over bakes.
Null = 2000 copies with every bake window moved to a random start on the same day (not overlapping a real bake), same length."""
import csv, json, random, datetime as dt, bisect, math
R = [r for r in csv.DictReader(open('copper_self.csv')) if r['g200'] not in ('', 'nan') and r['plc_off'] == '0']
T = [dt.datetime.fromisoformat(r['ts']) for r in R]; bands = ['g200', 'g212', 'g300', 'e200', 'e212', 'e300']
V = {b: [float(r[b]) if r[b] not in ('', 'nan') else None for r in R] for b in bands}
bakes = [(dt.datetime.fromisoformat(s), dt.datetime.fromisoformat(e)) for s, e, _ in json.load(open('bakes.json'))]
bakes = [(s, e) for s, e in bakes if e - s >= dt.timedelta(minutes=15) and s >= T[0]]
def idx(a, b): return bisect.bisect_left(T, a), bisect.bisect_left(T, b)
def one(s, e):
    i0, i1 = idx(s, e); o0, _ = idx(s - dt.timedelta(hours=2), s); _, o1 = idx(e, e + dt.timedelta(hours=2))
    if i1 - i0 < 10: return None
    res = {}
    for b in bands:
        a = [x for x in V[b][i0:i1] if x is not None]; c = [x for x in V[b][o0:i0] + V[b][i1:o1] if x is not None]
        res[b] = sum(a) / len(a) - sum(c) / len(c) if len(a) >= 10 and len(c) >= 10 else None
    return res
def agg(wins):
    per = [x for x in (one(s, e) for s, e in wins) if x]
    return {b: (sum(p[b] for p in per if p[b] is not None) / max(1, sum(p[b] is not None for p in per))) for b in bands}, len(per)
obs, n = agg(bakes); rng = random.Random(424); null = {b: [] for b in bands}
for _ in range(2000):
    fake = []
    for s, e in bakes:
        L = e - s; day0 = dt.datetime.combine(s.date(), dt.time(0))
        for _t in range(20):
            fs = day0 + dt.timedelta(minutes=rng.randrange(0, 24 * 60 - int(L.total_seconds() // 60)))
            if not any(fs < be and fs + L > bs for bs, be in bakes): break
        fake.append((fs, fs + L))
    a, _ = agg(fake)
    for b in bands: null[b].append(a[b])
print(f'{n} bakes with >=10 copper cycles inside')
for b in bands:
    nv = null[b]; mu = sum(nv) / len(nv); sd = (sum((x - mu) ** 2 for x in nv) / len(nv)) ** .5
    p = (1 + sum(abs(x - mu) >= abs(obs[b] - mu) for x in nv)) / (1 + len(nv))
    print(f'{b}: baking minus around = {obs[b]:+.2f} dB | null {mu:+.2f} +/- {sd:.2f} | z {(obs[b]-mu)/sd:+.1f} p {p:.4f}')
