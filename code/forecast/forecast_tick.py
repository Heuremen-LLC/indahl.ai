#!/usr/bin/env python3
"""forecast_tick.py: one FORECAST round for Nova's tick bus, per PLAN.md. Fetches NWS forecasts for stations that are due (6 hours since their last fetch, at most 10 per round),
scores periods that have ended against the station's hourly observations, rewrites summary_forecast.json and publishes it. Read-only, our user agent names this site."""
import os, sys, json, time, math, urllib.request, subprocess, datetime as D, collections as C
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); UA = 'heuremen-forecast/0.1 (+https://indahl.ai/forecast)'
ST = json.load(open('stations.json')); now = time.time()
def get(u):
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA, 'Accept': 'application/geo+json'}), timeout=30) as r: return json.loads(r.read())
        except Exception: time.sleep(2 * (a + 1))
iso = lambda s: D.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
def load(f): return [json.loads(l) for l in open(f)] if os.path.exists(f) else []
per, sc = load('data/periods.jsonl'), load('data/scores.jsonl'); fetched = {}
for p in per: fetched[p['station']] = max(fetched.get(p['station'], 0), p['fetched'])
grid = json.load(open('data/grid.json')) if os.path.exists('data/grid.json') else {}
nf = 0; out = open('data/periods.jsonl', 'a')
for s, lat, lon in ST:
    if nf >= 10: break
    if now - fetched.get(s, 0) < 6 * 3600: continue
    if s not in grid:
        d = get(f'https://api.weather.gov/points/{lat},{lon}'); time.sleep(0.5)
        if not d: continue
        grid[s] = d['properties']['forecast']
    fc = get(grid[s]); time.sleep(0.5)
    if not fc: continue
    for p in fc['properties']['periods']:
        st = iso(p['startTime']); lead = (st - now) / 3600
        if lead > 48: continue
        v = (p.get('probabilityOfPrecipitation') or {}).get('value')
        out.write(json.dumps(dict(id=f"{s}|{p['startTime']}|{int(now)}", station=s, fetched=now, start=st, end=iso(p['endTime']), lead_h=round(lead, 1), pop=v, stated=v is not None)) + '\n')
    nf += 1
out.close(); json.dump(grid, open('data/grid.json', 'w'))
per = load('data/periods.jsonl'); done = {x['id'] for x in sc}; obs_cache = {}
def event(o):
    p = o['properties']; pl = (p.get('precipitationLastHour') or {}).get('value')
    if pl is not None and pl > 0: return True
    return any(any(w in (x.get('weather') or '') for w in ('rain', 'drizzle', 'snow', 'sleet', 'hail', 'showers', 'thunderstorm')) for x in (p.get('presentWeather') or []))
nsc = 0; so = open('data/scores.jsonl', 'a')
for p in per:
    if p['id'] in done or not p['stated'] or p['end'] > now - 3600 or nsc >= 60: continue
    k = (p['station'], p['start'], p['end'])
    if k not in obs_cache:
        a = D.datetime.fromtimestamp(p['start'], D.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'); b = D.datetime.fromtimestamp(p['end'], D.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        d = get(f"https://api.weather.gov/stations/{p['station']}/observations?start={a}&end={b}&limit=500"); time.sleep(0.4); obs_cache[k] = d
    d = obs_cache[k]
    if not d: continue
    feats = d.get('features', []); hours = {iso(f['properties']['timestamp']) // 3600 for f in feats}; need = (p['end'] - p['start']) / 3600
    row = dict(id=p['id'], n_obs=len(feats), hours_with_obs=len(hours), unscorable=len(hours) < 0.75 * need, event=any(event(f) for f in feats)); so.write(json.dumps(row) + '\n'); nsc += 1
so.close(); sc = load('data/scores.jsonl'); sm = {x['id']: x for x in sc}
BINS = [(0, 5, '0 to 5'), (10, 20, '10 to 20'), (30, 40, '30 to 40'), (50, 60, '50 to 60'), (70, 80, '70 to 80'), (90, 100, '90 to 100')]; LEADS = [(0, 12, 'under 12 hours'), (12, 24, '12 to 24 hours'), (24, 48, '24 to 48 hours')]
import heuremen_kit as _K
def wil(k, n): return _K.wilson(k, n)   # 29 Oct: the local copy omitted the division by d; the kit's tested function replaces it
cells = []; unsc = 0; dropped = sum(1 for p in per if not p['stated']); scored = 0; lowev = [0, 0]
for p in per:
    r = sm.get(p['id'])
    if not r: continue
    if r['unscorable']: unsc += 1; continue
    scored += 1
    if p['pop'] in (0, 5): lowev[1] += 1; lowev[0] += r['event']
for lo, hi, nm in BINS:
    for l0, l1, ln in LEADS:
        xs = [(p, sm[p['id']]) for p in per if p['id'] in sm and not sm[p['id']]['unscorable'] and p['stated'] and lo <= p['pop'] <= hi and l0 <= p['lead_h'] < l1]
        n = len(xs)
        if not n: cells.append(dict(bin=nm, lead=ln, n=0)); continue
        k = sum(r['event'] for _, r in xs); ms = sum(p['pop'] for p, _ in xs) / n; a, b = wil(k, n)
        oc = 'CANNOT_TELL' if n < 30 else ('ABOVE' if a * 100 > ms else ('BELOW' if b * 100 < ms else 'CONSISTENT'))
        cells.append(dict(bin=nm, lead=ln, n=n, mean_stated=round(ms, 1), observed=round(100 * k / n, 1), lo=round(100 * a, 1), hi=round(100 * b, 1), outcome=oc))
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), stations=len(ST), forecasts_stored=len({(p['station'], p['fetched']) for p in per}), periods_stored=len(per), periods_scored=scored, unscorable=unsc, not_stated=dropped,
           floor=dict(periods=lowev[1], with_event=lowev[0]), cells=cells)
json.dump(out, open('summary_forecast.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'forecast_live', '--path', os.path.join(H, 'summary_forecast.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('forecast:', nf, 'fetched,', nsc, 'scored this round;', len(per), 'periods stored;', 'published' if p.returncode == 0 else 'publish FAILED')
