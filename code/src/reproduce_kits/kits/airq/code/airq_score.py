"""airq_score.py: the 2026 window read of airq_index/airq_tick.py (AIRQ_WINDOW=2026), offline, from what that read kept in data/w2026/. The
constants, metrics(), meets(), corrected(), ab_ok(), haversine() and outcome() are copied as written, stage A runs over the kept per-state AQS
files (aqs_NN.json, the daily means the read built from the hourly records) in state-code order as the read did, stage C takes the kept list of
sensors near each monitor (pa_near.json) and stage E, copied as written, scores the kept PurpleAir daily histories (pa_<sensor>.json). No key
and no network: the tick reads its keys and the AQS state list only to fetch, and every fetch it would make was already kept. Writes out.json."""
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import os, json, math, statistics, collections, datetime, glob
import heuremen_kit as K
DD = 'data/w2026'
RADIUS, MINDAYS, MINHOURS, STOP_POINTS = 200.0, 30, 18, 400000
def metrics(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n; sxx = sum((a - mx) ** 2 for a in x); sxy = sum((a - mx) * (b - my) for a, b in zip(x, y)); syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0: return None
    slope = sxy / sxx; b0 = my - slope * mx; r2 = sxy * sxy / (sxx * syy); rmse = math.sqrt(sum((b - a) ** 2 for a, b in zip(x, y)) / n); nr = 100 * rmse / mx if mx > 0 else None
    return dict(n=n, slope=slope, intercept=b0, r2=r2, rmse=rmse, nrmse=nr)
def meets(m): return bool(m and 0.65 <= m['slope'] <= 1.35 and -5 <= m['intercept'] <= 5 and m['r2'] >= 0.70 and (m['rmse'] <= 7 or (m['nrmse'] is not None and m['nrmse'] <= 30)))
def corrected(cf1, rh): return 0.524 * cf1 - 0.0862 * rh + 5.75
def ab_ok(a, b):
    d = abs(a - b); return d < 5 or (a + b > 0 and 2 * d / (a + b) * 100 < 61)
def haversine(la1, lo1, la2, lo2):
    p = math.pi / 180; a = math.sin((la2 - la1) * p / 2) ** 2 + math.cos(la1 * p) * math.cos(la2 * p) * math.sin((lo2 - lo1) * p / 2) ** 2; return 12742000 * math.asin(math.sqrt(a))
def outcome(n_not, n):
    if n < 30: return K.CANNOT_TELL
    lo, hi = K.wilson(n_not, n); return K.ABOVE if lo > 0.5 else (K.CONSISTENT if hi < 0.5 else K.CANNOT_TELL)
sites = {}; filter_only = set(); cont_sites = set()
for cache in sorted(glob.glob(DD + '/aqs_*.json')):
    part = json.load(open(cache))
    for m in part['mon']:
        if len(m['days']) >= MINDAYS: sites.setdefault(m['site'], []).append(m)
    filter_only |= set(part['filter_only']); cont_sites |= set(part.get('cont', []))
mons = {}
for k, v in sites.items(): mons[k] = max(v, key=lambda m: len(m['days']))
near = json.load(open(DD + '/pa_near.json'))
def sensor_days(sid):
    p = DD + '/pa_%d.json' % sid
    if not os.path.exists(p): return {}
    d = json.load(open(p)); f = d.get('fields') or []; out = {}
    for row in d.get('data') or []:
        r = dict(zip(f, row)); day = datetime.datetime.fromtimestamp(r['time_stamp'], datetime.timezone.utc).strftime('%Y-%m-%d')
        v = [r.get(x) for x in ('pm2.5_atm_a', 'pm2.5_atm_b', 'pm2.5_cf_1_a', 'pm2.5_cf_1_b', 'humidity')]
        if any(z is None for z in v): continue
        out[day] = v
    return out
pairs = []; removed_ab = 0; kept_days = 0
for k, m in mons.items():
    for s in near.get(k, []):
        sd = sensor_days(s['id']); X = []; R = {'R1': [], 'R2': [], 'R3': []}
        for day, ref in sorted(m['days'].items()):
            if day not in sd: continue
            aa, ab, ca, cb, rh = sd[day]
            if not ab_ok(ca, cb): removed_ab += 1; continue
            X.append(ref); R['R1'].append((aa + ab) / 2); R['R2'].append((ca + cb) / 2); R['R3'].append(corrected((ca + cb) / 2, rh))
        if len(X) >= MINDAYS:
            kept_days += len(X); pairs.append(dict(monitor=k, sensor=s['id'], dist=s['dist'], n=len(X), **{r: metrics(X, R[r]) for r in R}, mean_ref=sum(X) / len(X), max_ref=max(X)))
by_mon = collections.defaultdict(list)
for p in pairs: by_mon[p['monitor']].append(p)
NAME = {'R1': 'Map reading (atm channels, raw)', 'R2': 'cf_1 channels, raw', 'R3': 'cf_1 corrected for humidity (Barkjohn 2021)'}
comparison = {}; medians = {}
for r in ('R1', 'R2', 'R3'):
    unit = []
    for k, ps in by_mon.items():
        ps = [p for p in ps if p[r]]; 
        if ps: unit.append(sorted(ps, key=lambda p: p[r]['rmse'])[(len(ps) - 1) // 2])
    n = len(unit); n_not = sum(1 for p in unit if not meets(p[r])); lo, hi = K.wilson(n_not, n) if n else (0, 1)
    comparison[NAME[r]] = dict(of=n, n=n_not, share=round(n_not / n, 4) if n else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=outcome(n_not, n))
json.dump(dict(window='1 March to 30 June 2026', comparison=comparison), open('out.json', 'w'), indent=1)
