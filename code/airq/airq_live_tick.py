#!/usr/bin/env python3
"""airq_live_tick.py: AIRQ live panel per PLAN.md addenda 2 and 3. PurpleAir sensors against the AirNow real-time hourly values of the same monitors, daily pairs rolling over 30 kept days, plus an hourly strip."""
import os, sys, re, json, math, time, datetime, statistics, random, collections, subprocess, urllib.request, urllib.error, fcntl
import os as _pg_os, sys as _pg_sys, subprocess as _pg_sp   # 10 Nov 2026 (publish guard): the site KV is written only by a run the tick bus or the house clock started
_PUBLISH = '--publish' in _pg_sys.argv or _pg_os.environ.get('HEUREMEN_PUBLISH') == '1'   # (they export HEUREMEN_PUBLISH=1) or a run given --publish. A copy run for a reproduce kit or a test never publishes
if _PUBLISH: _pg_os.environ['HEUREMEN_PUBLISH'] = '1'   # passed on to the scripts this one starts, and kept across a detach or re-exec
def _kv_put(cmd, **kw):
    if _PUBLISH: return _pg_sp.run(cmd, **kw)
    print('publish guard: %s not put to the site KV (run with --publish, or from the tick bus)' % cmd[5], file=_pg_sys.stderr)
    return _pg_sp.CompletedProcess(cmd, 0, '' if kw.get('text') or kw.get('universal_newlines') else b'', '' if kw.get('text') or kw.get('universal_newlines') else b'')
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data/an', exist_ok=True)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('airq-live: plan not committed'); sys.exit(0)
_l = open('data/.live.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('airq-live: another run holds the lock'); sys.exit(0)
PA_K = open(os.path.expanduser('~/bones-forge/.purpleair_read_key')).read().strip()   # 29 Oct: launchd riders may not read ~/Documents (macOS privacy), so the read key sits beside the IBM keys, mode 600
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
PA_N = collections.Counter()    # 30 Oct (site pass H-12): every PurpleAir answer is counted by kind, so a failed call is told from an empty one
def pa(path, **q):
    """-> the parsed answer, {} when the service answered that this sensor holds nothing (403 private, 404 gone), None when the call itself failed."""
    time.sleep(1.1); u = 'https://api.purpleair.com/v1/' + path + ('?' + '&'.join('%s=%s' % kv for kv in q.items()) if q else '')
    for i in range(3):
        try:
            d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=dict(UA, **{'X-API-Key': PA_K})), timeout=90).read()); PA_N['answered'] += 1; return d
        except urllib.error.HTTPError as e:
            if e.code in (403, 404): PA_N['refused_%d' % e.code] += 1; return {}
            if e.code == 402: PA_N['out_of_points'] += 1; return None
            time.sleep(3 * (i + 1))
        except Exception: time.sleep(3 * (i + 1))
    PA_N['failed'] += 1; return None
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
    if b is None: print('airq-live: AirNow file', dt.strftime('%Y%m%d%H'), 'not returned', flush=True); return None
    d = parse_airnow(b.decode('utf8', 'replace'), want)
    print('airq-live: AirNow file', dt.strftime('%Y%m%d%H'), len(b), 'bytes,', len(d), 'of our monitors', flush=True)
    # 30 Oct (site pass H-12): an hour is cached only when it is old enough and its file holds a normal number of our monitors. An empty or partial answer used to be cached for good (20261029 22:00 and 23:00, 20261030 09:00 and 10:00).
    if (dt.date() < today or dt < now - datetime.timedelta(hours=3)) and len(d) >= 0.6 * len(want): json.dump(d, open(f, 'w'))
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
# 30 Oct (site pass H-12): two faults found and fixed here.
# 1. The PurpleAir history service returns only the averaging buckets that are complete inside [start, end]. A bucket labelled with the start of a UTC day needs end_timestamp at or after the next midnight.
#    The old end of 23:59:59 on the last day dropped that last day from every call: 28 Oct was empty on the first run, and each later day closed alone and came back empty. Checked against the service on 30 Oct.
# 2. The old code wrote an empty record for every missing day before the call, so a day that returned nothing was marked read and never asked again. A day is now stored only when sensor rows come back,
#    and a day that returns nothing stays open for the next run. After three runs in which every sensor answered and none held a row, the day is stored as read, empty, and the count is printed.
sens_none = live.setdefault('sens_empty', {})
miss = [d for d in days if not sens.get(d.isoformat()) and sens_none.get(d.isoformat(), 0) < 3]
if miss:
    lp = left()
    if lp is not None and lp < STOP_POINTS: print('airq-live: points guard,', lp, 'left'); miss = []
runs = []
for d in miss:
    if runs and (d - runs[-1][-1]).days == 1: runs[-1].append(d)
    else: runs.append([d])
for run in runs:
    t0 = int(datetime.datetime(run[0].year, run[0].month, run[0].day, tzinfo=UTC).timestamp()); nx = run[-1] + datetime.timedelta(days=1); t1 = int(datetime.datetime(nx.year, nx.month, nx.day, tzinfo=UTC).timestamp())
    want = {d.isoformat() for d in run}; got = collections.defaultdict(dict); before = PA_N['failed'] + PA_N['out_of_points']
    for i, m in enumerate(mons):
        h = pa('sensors/%d/history' % sel[m], start_timestamp=t0, end_timestamp=t1, average=1440, fields=FIELDS)
        for row in (h or {}).get('data', []):
            r = dict(zip(h['fields'], row)); dd = datetime.datetime.fromtimestamp(r['time_stamp'], UTC).date().isoformat()
            if dd in want and all(r.get(f) is not None for f in FIELDS.split(',')): got[dd][m] = [r[f] for f in FIELDS.split(',')]
        if i % 30 == 29: print('airq-live: sensors', i + 1, 'of', len(mons), 'for', run[0], 'to', run[-1], flush=True)
    clean = PA_N['failed'] + PA_N['out_of_points'] == before
    for d in run:
        k = d.isoformat()
        if got.get(k): sens[k] = got[k]; sens_none.pop(k, None); print('airq-live: sensor day', k, len(got[k]), 'sensors with a row', flush=True)
        elif clean:
            sens_none[k] = sens_none.get(k, 0) + 1
            if sens_none[k] >= 3: sens[k] = {}
            print('airq-live: sensor day', k, 'no sensor returned a row, run', sens_none[k], 'of 3', flush=True)
        else: print('airq-live: sensor day', k, 'left open, some calls failed', flush=True)
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
    if r and len(r) >= 0.6 * len(want): hr = dt; ar = r; break   # 30 Oct (H-12): AirNow posts the newest hour's file part filled (4 of our 147 monitors eight minutes after the hour, 97 or more when whole), so a thin file is not the last complete hour
if hr:
    pick = random.Random(7).sample(mons, 10)
    for m in sorted(pick):
        h = pa('sensors/%d/history' % sel[m], start_timestamp=int(hr.timestamp()), end_timestamp=int(hr.timestamp()) + 3600, average=60, fields=FIELDS)   # 30 Oct (H-12): end at the next hour, not 3599 s in, or the bucket is never returned
        v = None
        for row in (h or {}).get('data', []):
            r = dict(zip(h['fields'], row))
            if r.get('time_stamp') == int(hr.timestamp()) and all(r.get(f) is not None for f in FIELDS.split(',')): v = r
        a = ar.get(aqsid(m))
        if v and a is not None:
            c = corrected((v['pm2.5_cf_1_a'] + v['pm2.5_cf_1_b']) / 2, v['humidity']); strip.append(dict(monitor=m, airnow=round(a, 1), sensor=round(c, 1), difference=round(c - a, 1)))
        else: strip.append(dict(monitor=m, airnow=(round(a, 1) if a is not None else None), sensor=None, difference=None))
# ---- publish: merge into the main summary
S = json.load(open('summary_airq.json'))
done_days = len([d for d in days if d.isoformat() in sens and sens[d.isoformat()]])
# 30 Oct (site pass H-12): the sensor side and the AirNow side each carry the date of their own newest day, so a stamp that moves every hour cannot hide a sensor side that has stopped.
sens_days = [d for d in days if sens.get(d.isoformat())]; ref_days = [d for d in days if any(v is not None for v in ref.get(d.isoformat(), {}).values())]
sens_through = max(sens_days) if sens_days else None; ref_through = max(ref_days) if ref_days else None
strip_n = len([s for s in strip if s['difference'] is not None]); fmt_d = lambda d: (d.strftime('%d %b') + ' UTC') if d else 'none yet'
S['live'] = dict(updated=now.strftime('%d %b %H:%M') + ' UTC', window='the last %d UTC days' % WINDOW, monitors_in_panel=len(mons), monitors_with_30_kept_days=used, days_read=done_days, comparison=live_cmp,
                 sensor_days_through=(sens_through.isoformat() if sens_through else None), airnow_days_through=(ref_through.isoformat() if ref_through else None), sensors_in_newest_day=(len(sens[sens_through.isoformat()]) if sens_through else 0),
                 strip_hour=(hr.strftime('%d %b %H:00 UTC') if hr else None), strip_sensors_with_a_reading=strip_n, strip={s['monitor']: dict(airnow=s['airnow'], sensor=s['sensor'], difference=s['difference']) for s in strip},
                 strip_median_difference=(round(statistics.median([s['difference'] for s in strip if s['difference'] is not None]), 2) if any(s['difference'] is not None for s in strip) else None))
S['live_line'] = 'Live panel: %d monitors, %d with 30 kept days. Sensor days read through %s, AirNow days read through %s. Last strip hour: %s, %d of %d sensors returned a reading. Updated %s.' % (
    len(mons), used, fmt_d(sens_through), fmt_d(ref_through), S['live']['strip_hour'], strip_n, len(strip), S['live']['updated'])
json.dump(S, open('summary_airq.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = _kv_put(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'airq_live', '--path', os.path.join(H, 'summary_airq.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
with open('live_history.jsonl', 'a') as f: f.write(json.dumps(dict(t=S['live']['updated'], panel=len(mons), with30=used, strip_hour=S['live']['strip_hour'], strip_n=strip_n, sensor_through=(sens_through.isoformat() if sens_through else None), pa=dict(PA_N))) + '\n')
# 30 Oct (site pass H-12): alert when the sensor side stops. strip_n of 0 in the last 3 logged runs, or a newest sensor day more than 2 UTC days old, is printed and written to data/last_run.log, which watch/alerts_check.py reads for Bones.
# The alert line is removed again by the first run that is healthy.
LOGF = 'data/last_run.log'; hist = [json.loads(l) for l in open('live_history.jsonl') if l.strip()][-3:]
stuck = len(hist) == 3 and all(h.get('strip_n') == 0 for h in hist); old = sens_through is None or (today - sens_through).days > 2
keep = [l for l in (open(LOGF).read().split('\n') if os.path.exists(LOGF) else []) if l and not l.startswith('airq-live: ALERT')]
if stuck or old:
    msg = 'airq-live: ALERT sensor side FAILED: %s%s (newest sensor day %s, PurpleAir answers %s)' % ('strip empty in the last 3 runs' if stuck else '', ' and sensor days stale' if (old and stuck) else ('sensor days stale' if old else ''), sens_through, dict(PA_N))
    print(msg, flush=True); keep.append(msg)
open(LOGF, 'w').write('\n'.join(keep) + ('\n' if keep else ''))
print('airq-live:', len(mons), 'monitors,', used, 'with 30 kept days; sensor days through', sens_through, 'PurpleAir answers', dict(PA_N), ';', {k: (v['n'], v['of'], v['outcome']) for k, v in live_cmp.items()}, 'strip', len(strip), 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
