#!/usr/bin/env python3
"""airline_tick.py: AIRLINE per PLAN.md. Scheduled minus flown time per airline route, 2019 vs 2025 vs 2026 (Jan to Aug)."""
import os, sys, io, csv, json, zipfile, random, time, pickle, urllib.request, statistics
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('airline: plan not committed'); sys.exit(0)
B = 'https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_%d_%d.zip'
YEARS = (2019, 2025, 2026); MONTHS = range(1, 9); MINF = 30; MINR = 30; DRAWS = 2000; TOL = 1.0
SEED = 20261112   # PLAN_ADDENDUM_std2.md: named seed, one K.bootstrap call per airline and comparison. The 29 Oct read used one shared stream seeded 20261029, kept beside it as *_pre_std2.
def med(c):
    n = sum(c.values()); h = (n + 1) / 2.0; acc = 0; vals = sorted(c)
    lo = hi = None
    for v in vals:
        acc += c[v]
        if lo is None and acc >= int(h): lo = v
        if hi is None and acc >= int(h + 0.5): hi = v; break
    return (lo + hi) / 2.0
def outcome(lo, hi):
    """Faults and Guards 2.0 (PLAN_ADDENDUM_std2.md): band minus 1 to plus 1 minute, closed edges, the size that matters is 1 minute in either direction, null 0. Returns (outcome, reason)."""
    return K.read(lo, hi, band=(-TOL, TOL), matters=TOL, direction='both', null=0.0)
OLD = json.load(open('data/results_plan_20261029.json')) if os.path.exists('data/results_plan_20261029.json') else {}
def compare(padA, padB, key=None):
    """padX: {(carrier,route): (median_pad, median_flown, n)}. Units with >= MINF flights in both periods; airlines with >= MINR such routes."""
    by = {}
    for k in padA:
        if k in padB and padA[k][2] >= MINF and padB[k][2] >= MINF: by.setdefault(k[0], []).append((k[1], padB[k][0] - padA[k][0], padB[k][1] - padA[k][1]))
    out = {}
    for car, rows in sorted(by.items()):
        if len(rows) < MINR: out[car] = dict(outcome='CANNOT_TELL', reason=K.TOO_WIDE_TO_RESOLVE, routes=len(rows), interval_method='none formed, under 30 routes'); continue   # O3: under the plan's minimum sample
        d = [r[1] for r in rows]; lo, hi, meth = K.bootstrap(d, statistics.median, draws=DRAWS, seed=SEED, level=0.95); oc, why = outcome(lo, hi)
        out[car] = dict(outcome=oc, reason=why, routes=len(rows), change=statistics.median(d), lo=lo, hi=hi, flown_change=statistics.median([r[2] for r in rows]), interval_method=meth)
        o = ((OLD.get(key) or {}).get(car)) if key else None   # the 29 Oct reading, kept beside the new one (a new seed and percentile rule is a new reading)
        if o and 'lo' in o: out[car].update(outcome_pre_std2=o['outcome'], lo_pre_std2=o['lo'], hi_pre_std2=o['hi'], method_pre_std2='percentile bootstrap over routes, 2000 draws, one stream seeded 20261029 shared by all airlines in file order, nearest ordered draw, 95 percent')
    return out
def gate():
    rng = random.Random(7); res = {}   # the planted data only
    for name, shift, sd in (('plus5', 5, 0.5), ('zero', 0, 0.5), ('minus5', -5, 0.5), ('noisy_zero', 0, 4.0)):
        A = {}; Bp = {}
        for i in range(60):
            A[('X', i)] = (10 + rng.gauss(0, sd), 100.0, 50); Bp[('X', i)] = (10 + shift + rng.gauss(0, sd), 100.0, 50)
        r = compare(A, Bp)['X']; res[name] = r['outcome'] if r['reason'] is None else '%s %s' % (r['outcome'], r['reason'])
    ok = res == {'plus5': 'ABOVE', 'zero': 'CONSISTENT', 'minus5': 'BELOW', 'noisy_zero': 'CANNOT_TELL TOO_WIDE_TO_RESOLVE'}
    print('airline: gate', res); return ok
def read_month(y, m):
    cache = 'data/m_%d_%02d.pkl' % (y, m)
    if os.path.exists(cache): return pickle.load(open(cache, 'rb'))
    z = 'data/%d_%d.zip' % (y, m)
    if not os.path.exists(z): urllib.request.urlretrieve(B % (y, m), z)
    agg = {}; rows = 0
    with zipfile.ZipFile(z) as zf:
        name = zf.namelist()[0]
        with zf.open(name) as f:
            for r in csv.DictReader(io.TextIOWrapper(f, 'utf-8')):
                rows += 1
                if r['Cancelled'] != '0.00' or r['Diverted'] != '0.00': continue
                try: s = int(float(r['CRSElapsedTime'])); a = int(float(r['ActualElapsedTime']))
                except ValueError: continue
                k = (r['Reporting_Airline'], r['Origin'] + '-' + r['Dest']); e = agg.get(k)
                if e is None: e = agg[k] = [Counter(), Counter(), 0, 0]
                e[0][s] += 1; e[1][a] += 1; e[2] += 1; e[3] += 1 if r['ArrDel15'] == '1.00' else 0
    pickle.dump((agg, rows), open(cache, 'wb')); os.remove(z); return agg, rows
def period(y):
    tot = {}; rows = 0
    for m in MONTHS:
        agg, n = read_month(y, m); rows += n; print('airline: read', y, m, n, flush=True)
        for k, e in agg.items():
            t = tot.get(k)
            if t is None: t = tot[k] = [Counter(), Counter(), 0, 0]
            t[0].update(e[0]); t[1].update(e[1]); t[2] += e[2]; t[3] += e[3]
    pad = {k: (med(e[0]) - med(e[1]), med(e[1]), e[2]) for k, e in tot.items() if e[2] >= MINF}
    late = {}
    for k, e in tot.items(): late.setdefault(k[0], [0, 0]); late[k[0]][0] += e[3]; late[k[0]][1] += e[2]
    return pad, late, rows
if not gate(): print('airline: GATE FAILED'); sys.exit(1)
P = {}
for y in YEARS: P[y] = period(y)
res = dict(t=time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), months='January to August', rows={y: P[y][2] for y in YEARS},
           c25_19=compare(P[2019][0], P[2025][0], 'c25_19'), c26_25=compare(P[2025][0], P[2026][0], 'c26_25'), standard='Faults and Guards 2.0.0', seed=SEED,
           late15={y: {c: [v[0], v[1]] for c, v in P[y][1].items()} for y in YEARS})
json.dump(res, open('data/results.json', 'w'), indent=1)
for key in ('c25_19', 'c26_25'):
    print(key); [print(' ', c, v['outcome'], v.get('reason'), v.get('routes'), 'chg %.2f [%.2f,%.2f]' % (v['change'], v['lo'], v['hi']) if 'change' in v else '') for c, v in res[key].items()]
