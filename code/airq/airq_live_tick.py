#!/usr/bin/env python3
"""airq_live_tick.py: AIRQ live panel per PLAN.md addenda 2 and 3. PurpleAir sensors against the AirNow real-time hourly values of the same monitors, daily pairs rolling over 30 kept days, plus an hourly strip."""
import os, sys, re, json, math, time, datetime, statistics, random, collections, subprocess, urllib.request, urllib.error, fcntl
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data/an', exist_ok=True)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('airq-live: plan not committed'); sys.exit(0)
_l = open('data/.live.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('airq-live: another run holds the lock'); sys.exit(0)
PA_K = open(os.path.expanduser('~/Documents/Heuremen LLC/ACCOUNTS/purpleair-read-key')).read().strip()
UA = {'User-Agent': 'heuremen-airq/0.1 (+https://indahl.ai/airq)'}; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
UTC = datetime.timezone.utc; MINDAYS, WINDOW, STOP_POINTS = 30, 60, 400000
FIELDS = 'pm2.5_atm_a,pm2.5_atm_b,pm2.5_cf_1_a,pm2.5_cf_1_b,humidity'
def get(u, headers=None, n=3, to=90):
    for i in range(n):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=dict(UA, **(headers or {}))), timeout=to).read()
        except urllib.error.HTTPError as e:
            if e.code in (404, 403): return None
            time.sleep(3 * (i + 1))
        except Exception: time.sleep(3 * (i + 1))
def pa(path, **q):
    time.sleep(1.1); b = get('https://api.purpleair.com/v1/' + path + ('?' + '&'.join('%s=%s' % kv for kv in q.items()) if q else ''), {'X-API-Key': PA_K})
    return json.loads(b) if b else None
def metrics(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n; sxx = sum((a - mx) ** 2 for a in x); sxy = sum((a - mx) * (b - my) for a, b in zip(x, y)); syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0: return None
    s = sxy / sxx; rmse = math.sqrt(sum((b - a) ** 2 for a, b in zip(x, y)) / n)
    return dict(slope=s, intercept=my - s * mx, r2=sxy * sxy / (sxx * syy), rmse=rmse, nrmse=(100 * rmse / mx if mx > 0 else None))
def meets(m): return bool(m and 0.65 <= m['slope'] <= 1.35 and -5 <= m['intercept'] <= 5 and m['r2'] >= 0.70 and (m['rmse'] <= 7 or (m['nrmse'] is not None and m['nrmse'] <= 30)))
def corrected(cf1, rh): return 0.524 * cf1 - 0.0862 * rh + 5.75
def ab_ok(a, b):
    d = abs(a - b); return d < 5 or (a + b > 0 and 2 * d / (a + b) * 100 < 61)
def outcome(n_not, n):
    if n < 30: return K.CANNOT_TELL if n else 'NOTHING_RETURNED'
    lo, hi = K.wilson(n_not, n); return K.ABOVE if lo > 0.5 else (K.CONSISTENT if hi < 0.5 else K.CANNOT_TELL)
def aqsid(site): return site.replace('-', '')
def parse_airnow(text, want):
    """-> {aqsid: value} for PM2.5 lines of the wanted site ids"""
    out = {}
    for ln in text.split('\n'):
        p = ln.split('|')
        if len(p) >= 8 and p[5] == 'PM2.5' and p[2] in want:
            try: out[p[2]] = float(p[7])
            except ValueError: pass
    return out
def day_mean(vals, minh=18): return (sum(vals) / len(vals)) if len(vals) >= minh else None
def gate():
    ok = parse_airnow('10/29/26|16:00|060195001|Fresno|-8|PM2.5|UG/M3|7.5|AirNow\n10/29/26|16:00|060195001|Fresno|-8|OZONE|PPB|30|AirNow\n10/29/26|16:00|999999999|X|-8|PM2.5|UG/M3|9|AirNow', {'060195001'}) == {'060195001': 7.5}
    ok &= aqsid('06-019-5001') == '060195001'; ok &= day_mean([1.0] * 19) == 1.0 and day_mean([1.0] * 17) is None and abs(corrected(10, 50) - 6.68) < 0.006
    xs = [float(i % 17) + 3 for i in range(40)]; ok &= meets(metrics(xs, xs)) and not meets(metrics(xs, [2 * v for v in xs]))
    print('airq-live: gate', 'passed' if ok else 'FAILED', flush=True); return bool(ok)
if not gate(): sys.exit(1)
now = datetime.datetime.now(UTC); today = now.date()
# ---- selected sensors: the median-RMSE pair of each monitor of the main read
pairs = json.load(open('data/pairs.json')); by = collections.defaultdict(list)
for p in pairs: by[p['monitor']].append(p)
sel = {}
for m, ps in by.items():
    ps = sorted([p for p in ps if p.get('R3')], key=lambda p: p['R3']['rmse'])
    if ps: sel[m] = ps[(len(ps) - 1) // 2]['sensor']
mons = sorted(sel); want = {aqsid(m) for m in mons}
# ---- AirNow hourly files, cached as small files holding only our monitors
def an_path(dt):
    n = dt.strftime('%Y%m%d%H')
    return 'https://files.airnowtech.org/airnow/%s/HourlyData_%s.dat' % (('today' if dt.date() == today else dt.strftime('%Y/%Y%m%d')), n)
def an_hour(dt):
    f = 'data/an/%s.json' % dt.strftime('%Y%m%d%H')
    if os.path.exists(f): return json.load(open(f))
    b = get(an_path(dt)); time.sleep(0.15)
    if b is None: return None
    d = parse_airnow(b.decode('utf8', 'replace'), want)
    if dt.date() < today or dt < now - datetime.timedelta(hours=3): json.dump(d, open(f, 'w'))
    return d
days = [today - datetime.timedelta(days=k) for k in range(WINDOW, 0, -1)]
if now.hour < 6: days = days[:-1]    # yesterday closes after 06:00 UTC
live = json.load(open('data/live_days.json')) if os.path.exists('data/live_days.json') else {}
need = [d for d in days if d.isoformat() not in live.get('ref', {})]
ref = live.setdefault('ref', {}); sens = live.setdefault('sens', {})
for d in need:
    vals = collections.defaultdict(list)
    for h in range(24):
        r = an_hour(datetime.datetime(d.year, d.month, d.day, h, tzinfo=UTC))
        for k, v in (r or {}).items(): vals[k].append(v)
    ref[d.isoformat()] = {m: day_mean(vals.get(aqsid(m), [])) for m in mons}
    print('airq-live: AirNow day', d, flush=True)
json.dump(live, open('data/live_days.json', 'w'))
# ---- sensor daily averages, one call per sensor for the missing range
def left():
    d = pa('organization'); return d['remaining_points'] if d else None
miss = [d for d in days if d.isoformat() not in sens]
if miss:
    lp = left()
    if lp is not None and lp < STOP_POINTS: print('airq-live: points guard,', lp, 'left'); miss = []
if miss:
    t0 = int(datetime.datetime(miss[0].year, miss[0].month, miss[0].day, tzinfo=UTC).timestamp()); t1 = int(datetime.datetime(miss[-1].year, miss[-1].month, miss[-1].day, 23, 59, 59, tzinfo=UTC).timestamp())
    for d in miss: sens[d.isoformat()] = {}
    for i, m in enumerate(mons):
        h = pa('sensors/%d/history' % sel[m], start_timestamp=t0, end_timestamp=t1, average=1440, fields=FIELDS)
        for row in (h or {}).get('data', []):
            r = dict(zip(h['fields'], row)); dd = datetime.datetime.fromtimestamp(r['time_stamp'], UTC).date().isoformat()
            if dd in sens and all(r.get(f) is not None for f in FIELDS.split(',')): sens[dd][m] = [r[f] for f in FIELDS.split(',')]
        if i % 30 == 29: print('airq-live: sensors', i + 1, 'of', len(mons), flush=True)
json.dump(live, open('data/live_days.json', 'w'))
# ---- rolling evaluation
res = {'R1': [], 'R2': [], 'R3': []}; used = 0
for m in mons:
    X = []; R = {'R1': [], 'R2': [], 'R3': []}
    for d in days:
        rf = ref.get(d.isoformat(), {}).get(m); s = sens.get(d.isoformat(), {}).get(m)
        if rf is None or not s: continue
        aa, ab, ca, cb, rh = s
        if not ab_ok(ca, cb): continue
        X.append(rf); R['R1'].append((aa + ab) / 2); R['R2'].append((ca + cb) / 2); R['R3'].append(corrected((ca + cb) / 2, rh))
    if len(X) < MINDAYS: continue
    used += 1; X = X[-MINDAYS:]
    for k in R: res[k].append(metrics(X, R[k][-MINDAYS:]))
NAME = {'R1': 'Map reading (atm channels, raw)', 'R2': 'cf_1 channels, raw', 'R3': 'cf_1 corrected for humidity (Barkjohn 2021)'}
live_cmp = {}
for k in ('R1', 'R2', 'R3'):
    ms = [m for m in res[k] if m]; n = len(ms); nn = sum(1 for m in ms if not meets(m)); lo, hi = K.wilson(nn, n) if n else (0, 1)
    live_cmp[NAME[k]] = dict(of=n, n=nn, share=round(nn / n, 4) if n else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=outcome(nn, n) if n >= 30 else 'NOTHING_RETURNED')
# ---- the strip: 10 sensors, last complete hour with an AirNow file
strip = []; hr = None
cand = [now.replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=k) for k in (1, 2, 3, 4)]
for dt in cand:
    r = an_hour(dt)
    if r: hr = dt; ar = r; break
if hr:
    pick = random.Random(7).sample(mons, 10)
    for m in sorted(pick):
        h = pa('sensors/%d/history' % sel[m], start_timestamp=int(hr.timestamp()), end_timestamp=int(hr.timestamp()) + 3599, average=60, fields=FIELDS)
        v = None
        for row in (h or {}).get('data', []):
            r = dict(zip(h['fields'], row))
            if all(r.get(f) is not None for f in FIELDS.split(',')): v = r
        a = ar.get(aqsid(m))
        if v and a is not None:
            c = corrected((v['pm2.5_cf_1_a'] + v['pm2.5_cf_1_b']) / 2, v['humidity']); strip.append(dict(monitor=m, airnow=round(a, 1), sensor=round(c, 1), difference=round(c - a, 1)))
        else: strip.append(dict(monitor=m, airnow=(round(a, 1) if a is not None else None), sensor=None, difference=None))
# ---- publish: merge into the main summary
S = json.load(open('summary_airq.json'))
done_days = len([d for d in days if d.isoformat() in sens and sens[d.isoformat()]])
S['live'] = dict(updated=now.strftime('%d %b %H:%M'), window='the last %d UTC days' % WINDOW, monitors_in_panel=len(mons), monitors_with_30_kept_days=used, days_read=done_days, comparison=live_cmp,
                 strip_hour=(hr.strftime('%d %b %H:00 UTC') if hr else None), strip={s['monitor']: dict(airnow=s['airnow'], sensor=s['sensor'], difference=s['difference']) for s in strip},
                 strip_median_difference=(round(statistics.median([s['difference'] for s in strip if s['difference'] is not None]), 2) if any(s['difference'] is not None for s in strip) else None))
S['live_line'] = 'Live panel: %d monitors, %d with 30 kept days. Last strip hour: %s. Updated %s.' % (len(mons), used, S['live']['strip_hour'], S['live']['updated'])
json.dump(S, open('summary_airq.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'airq_live', '--path', os.path.join(H, 'summary_airq.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
with open('live_history.jsonl', 'a') as f: f.write(json.dumps(dict(t=S['live']['updated'], panel=len(mons), with30=used, strip_hour=S['live']['strip_hour'], strip_n=len([s for s in strip if s['difference'] is not None]))) + '\n')
print('airq-live:', len(mons), 'monitors,', used, 'with 30 kept days;', {k: (v['n'], v['of'], v['outcome']) for k, v in live_cmp.items()}, 'strip', len(strip), 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
