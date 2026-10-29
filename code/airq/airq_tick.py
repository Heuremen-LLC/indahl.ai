#!/usr/bin/env python3
"""airq_tick.py: AIRQ per PLAN.md. PurpleAir sensors within 200 m of EPA continuous PM2.5 monitors, June to September 2025, against the EPA's Table ES-2 targets."""
import os, sys, json, math, time, statistics, collections, urllib.request, urllib.parse, urllib.error, datetime, random, subprocess
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('airq: plan not committed'); sys.exit(0)
ACC = os.path.expanduser('~/Documents/Heuremen LLC/ACCOUNTS')
AQS_E, AQS_K = open(ACC + '/epa-aqs-key').read().split()[:2]; PA_K = open(ACC + '/purpleair-read-key').read().strip()
B0, B1 = '20250601', '20250930'; T0 = int(datetime.datetime(2025, 6, 1, tzinfo=datetime.timezone.utc).timestamp()); T1 = int(datetime.datetime(2025, 9, 30, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp())
RADIUS, MINDAYS, MINHOURS, STOP_POINTS = 200.0, 30, 18, 400000
def jget(u, headers=None, n=4, to=300):
    for i in range(n):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=headers or {}), timeout=to).read())
        except urllib.error.HTTPError as e:
            if e.code in (400, 404): return None
            time.sleep(4 * (i + 1))
        except Exception: time.sleep(4 * (i + 1))
def pa(path, **q):
    time.sleep(1.1); return jget('https://api.purpleair.com/v1/' + path + ('?' + urllib.parse.urlencode(q) if q else ''), {'X-API-Key': PA_K})
def points_left():
    d = pa('organization'); return d['remaining_points'] if d else None
# ---- metrics (PLAN: Table ES-2, Eq. 5 and 6)
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
def gate():
    rnd = random.Random(5); xs = [rnd.uniform(2, 60) for _ in range(80)]
    ok = meets(metrics(xs, xs)); ok &= not meets(metrics(xs, [2 * v for v in xs])); ok &= not meets(metrics(xs, [v + 8 for v in xs])); ok &= not meets(metrics(xs, [rnd.uniform(2, 60) for _ in xs]))
    ok &= abs(corrected(10, 50) - 6.68) < 0.006; ok &= ab_ok(3, 7.9) and not ab_ok(10, 30) and ab_ok(100, 150)
    return bool(ok)
if not gate(): print('airq: GATE FAILED'); sys.exit(1)
print('airq: gate passed', flush=True)
# ---- stage A: EPA monitors, hourly continuous PM2.5 into UTC-day means
states = jget('https://aqs.epa.gov/data/api/list/states?email=%s&key=%s' % (AQS_E, AQS_K))['Data']; time.sleep(6)
sites = {}; filter_only = set(); cont_sites = set()
for st in states:
    code = st['code']; cache = 'data/aqs_%s.json' % code
    if os.path.exists(cache): part = json.load(open(cache))
    else:
        d = None
        for t in range(3):
            d = jget('https://aqs.epa.gov/data/api/sampleData/byState?email=%s&key=%s&param=88101&bdate=%s&edate=%s&state=%s' % (AQS_E, AQS_K, B0, B1, code)); time.sleep(6)
            if d: break
        rows = (d or {}).get('Data') or []; acc = {}; fo = set(); cont = set()
        for r in rows:
            key = '%s-%s-%s' % (r['state_code'], r['county_code'], r['site_number'])
            if r['sample_duration'] != '1 HOUR': fo.add(key); continue
            if r.get('qualifier') or r.get('sample_measurement') is None: continue
            cont.add(key)
            s = acc.setdefault(key + '|%s' % r['poc'], dict(site=key, poc=r['poc'], lat=r['latitude'], lon=r['longitude'], hours=collections.defaultdict(list)))
            s['hours'][r['date_gmt']].append(r['sample_measurement'])
        part = dict(mon=[dict(site=v['site'], poc=v['poc'], lat=v['lat'], lon=v['lon'], days={dd: sum(vs) / len(vs) for dd, vs in v['hours'].items() if len(vs) >= MINHOURS}) for v in acc.values()], filter_only=sorted(fo), cont=sorted(cont), rows=len(rows), status=(d or {}).get('Header', [{}])[0].get('status') if d else 'no response')
        json.dump(part, open(cache, 'w'))
    for m in part['mon']:
        if len(m['days']) >= MINDAYS: sites.setdefault(m['site'], []).append(m)
    filter_only |= set(part['filter_only']); cont_sites |= set(part.get('cont', []))
    print('airq: aqs', code, part.get('status'), part.get('rows'), flush=True)
mons = {}
for k, v in sites.items(): mons[k] = max(v, key=lambda m: len(m['days']))   # the record with the most valid UTC days at the site
fo_only = sorted(filter_only - cont_sites)
print('airq: monitors with >= %d valid UTC days: %d; sites with only filter samples: %d' % (MINDAYS, len(mons), len(fo_only)), flush=True)
# ---- stage C: PurpleAir sensors near each monitor
near_cache = 'data/pa_near.json'; near = json.load(open(near_cache)) if os.path.exists(near_cache) else {}
for i, (k, m) in enumerate(sorted(mons.items())):
    if k in near: continue
    dlat = 0.0025; dlon = 0.0025 / max(0.2, math.cos(math.radians(m['lat'])))
    d = pa('sensors', fields='latitude,longitude,date_created,last_seen,location_type', location_type=0, max_age=0, nwlng=m['lon'] - dlon, nwlat=m['lat'] + dlat, selng=m['lon'] + dlon, selat=m['lat'] - dlat)
    out = []
    if d and d.get('data'):
        f = d['fields']
        for row in d['data']:
            r = dict(zip(f, row))
            if haversine(m['lat'], m['lon'], r['latitude'], r['longitude']) <= RADIUS and r['date_created'] <= T1 and r['last_seen'] >= T0: out.append(dict(id=r['sensor_index'], dist=round(haversine(m['lat'], m['lon'], r['latitude'], r['longitude']), 1)))
    near[k] = out
    if i % 50 == 49: json.dump(near, open(near_cache, 'w')); print('airq: pa near', i + 1, 'of', len(mons), flush=True)
json.dump(near, open(near_cache, 'w'))
sens = sorted({s['id'] for v in near.values() for s in v}); print('airq: sensors near monitors:', len(sens), flush=True)
# ---- stage D: daily UTC averages per sensor, with the points guard
unread = []; fields = 'pm2.5_atm_a,pm2.5_atm_b,pm2.5_cf_1_a,pm2.5_cf_1_b,humidity'
for i, sid in enumerate(sens):
    cache = 'data/pa_%d.json' % sid
    if os.path.exists(cache): continue
    if i % 25 == 0:
        left = points_left()
        if left is not None and left < STOP_POINTS: unread = sens[i:]; print('airq: points guard, stopping with', left, 'left;', len(unread), 'sensors not read', flush=True); break
    d = pa('sensors/%d/history' % sid, start_timestamp=T0, end_timestamp=T1, average=1440, fields=fields)
    json.dump(d if d else {'data': [], 'fields': []}, open(cache, 'w'))
    if i % 50 == 49: print('airq: pa history', i + 1, 'of', len(sens), flush=True)
# ---- stage E: pairs and metrics
def sensor_days(sid):
    p = 'data/pa_%d.json' % sid
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
    ms = [p[r] for p in unit]
    medians[NAME[r]] = dict(monitors=n, slope=round(statistics.median([m['slope'] for m in ms]), 2) if ms else None, intercept=round(statistics.median([m['intercept'] for m in ms]), 2) if ms else None, r2=round(statistics.median([m['r2'] for m in ms]), 2) if ms else None, rmse=round(statistics.median([m['rmse'] for m in ms]), 2) if ms else None)
    srt = sorted(unit, key=lambda p: p[r]['rmse']) if r == 'R3' else []
    if r == 'R3': json.dump(dict(largest=[dict(monitor=p['monitor'], sensor=p['sensor'], dist=p['dist'], n=p['n'], rmse=p['R3']['rmse']) for p in srt[-5:]], smallest=[dict(monitor=p['monitor'], sensor=p['sensor'], dist=p['dist'], n=p['n'], rmse=p['R3']['rmse']) for p in srt[:5]]), open('data/hand_check_pairs.json', 'w'), indent=1)
res = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), gate='passed', window='1 June to 30 September 2025', monitors_read=len(mons), monitors_with_sensor=len(by_mon), sensors=len(sens), sensors_not_read=len(unread), pairs=len(pairs), days_kept=kept_days, days_removed_ab=removed_ab, filter_only_sites=len(fo_only),
           comparison=comparison, medians=medians, headline_n=comparison[NAME['R3']]['n'], headline_of=comparison[NAME['R3']]['of'], headline=comparison[NAME['R3']])
json.dump(res, open('summary_airq.json', 'w'), indent=1); json.dump(pairs, open('data/pairs.json', 'w'))
print('airq: monitors', len(mons), 'with sensors', len(by_mon), 'pairs', len(pairs), '| comparison', {k: (v['n'], v['of'], v['outcome']) for k, v in comparison.items()}, flush=True)
