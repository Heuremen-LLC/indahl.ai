#!/usr/bin/env python3
"""forecast_tick.py: one FORECAST round for the HST tick bus, per PLAN.md. Fetches NWS forecasts for stations that are due (6 hours since their last fetch, at most 10 per round),
scores periods that have ended against the station's hourly observations, rewrites summary_forecast.json and publishes it. Read-only, our user agent names this site."""
import os, sys, json, time, math, urllib.request, subprocess, datetime as D, collections as C
import os as _pg_os, sys as _pg_sys, subprocess as _pg_sp   # 10 Nov 2026 (publish guard): the site KV is written only by a run the tick bus or the house clock started
_PUBLISH = '--publish' in _pg_sys.argv or _pg_os.environ.get('HEUREMEN_PUBLISH') == '1'   # (they export HEUREMEN_PUBLISH=1) or a run given --publish. A copy run for a reproduce kit or a test never publishes
if _PUBLISH: _pg_os.environ['HEUREMEN_PUBLISH'] = '1'   # passed on to the scripts this one starts, and kept across a detach or re-exec
def _kv_put(cmd, **kw):
    if _PUBLISH: return _pg_sp.run(cmd, **kw)
    print('publish guard: %s not put to the site KV (run with --publish, or from the tick bus)' % cmd[5], file=_pg_sys.stderr)
    return _pg_sp.CompletedProcess(cmd, 0, '' if kw.get('text') or kw.get('universal_newlines') else b'', '' if kw.get('text') or kw.get('universal_newlines') else b'')
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
def _cell_read(n, a, b, ms):
    # PLAN_ADDENDUM_std2.md: point figure (mean stated chance) with no tolerance, so bound=ms, closed edges, no size that matters. Under 30 periods is TOO_WIDE_TO_RESOLVE.
    if n < 30: return 'CANNOT_TELL', _K.TOO_WIDE_TO_RESOLVE
    return _K.read(a * 100, b * 100, bound=ms)
def wil(k, n): return _K.wilson(k, n)   # 29 Oct: the local copy omitted the division by d; the kit's tested function replaces it
cells = []
# 30 Oct (site pass H-10): the counts printed above the table are taken from the set the cells use. A period is a station and a start time, counted once however many forecasts of it were fetched. Only stated chances with a lead from 0 to 48 hours are read (Addendum 1). Rows are counted apart.
dropped = len({(p['station'], p['start']) for p in per if not p['stated']})
okp = {}; badp = set(); lowp = {}
for p in per:
    r = sm.get(p['id'])
    if not r or not p['stated'] or not (0 <= p['lead_h'] < 48): continue
    k = (p['station'], p['start'])
    if r['unscorable']: badp.add(k); continue
    okp[k] = True
    if p['pop'] in (0, 5): lowp[k] = lowp.get(k, False) or bool(r['event'])
scored = len(okp); unsc = len(badp - set(okp)); lowev = [sum(lowp.values()), len(lowp)]; cellkeys = set()
for lo, hi, nm in BINS:
    for l0, l1, ln in LEADS:
        xs = [(p, sm[p['id']]) for p in per if p['id'] in sm and not sm[p['id']]['unscorable'] and p['stated'] and lo <= p['pop'] <= hi and l0 <= p['lead_h'] < l1]
        _seen = {}; xs = [_seen.setdefault((p['station'], p['start']), (p, o)) for p, o in sorted(xs, key=lambda z: z[0]['fetched'])]; xs = list({(p['station'], p['start']): (p, o) for p, o in xs}.values())   # 29 Oct (audit): one period counts once per cell, the earliest fetch
        n = len(xs); cellkeys.update((p['station'], p['start']) for p, _ in xs)
        if not n: cells.append(dict(bin=nm, lead=ln, n=0, outcome='CANNOT_TELL', reason=_K.NO_INTERVAL_FORMABLE)); continue
        k = sum(r['event'] for _, r in xs); ms = sum(p['pop'] for p, _ in xs) / n; a, b = wil(k, n)
        oc, why = _cell_read(n, a, b, ms)   # 12 Nov 2026 (PLAN_ADDENDUM_std2.md): Faults and Guards 2.0 outcome rule
        cells.append(dict(bin=nm, lead=ln, n=n, mean_stated=round(ms, 2), observed=round(100 * k / n, 2), lo=round(100 * a, 2), hi=round(100 * b, 2), outcome=oc, reason=why))
# 10 Nov 2026 (PLAN.md Addendum 2, decided after the data): the NWS event rule, measurable precipitation of 0.01 inch or more, is the primary reading
# from today. The original rule above (any amount above zero or a present-weather entry) is kept beside it as the original committed rule.
# The amounts come from the routine hourly METAR totals in the Iowa Environmental Mesonet ASOS archive (measurable.py). Same periods, bins,
# leads, one count per period per cell, Wilson 95% and the same four outcomes.
import measurable as _M
try: _nm = _M.update(per, sc, now=now, max_stations=10)
except Exception as _e: _nm = 0; print('forecast: measurable read failed', type(_e).__name__, str(_e)[:80])
_mm = _M.load()
def _mev(p):
    r = sm.get(p['id']); m = _mm.get((p['station'], p['start'], p['end']))
    if not r or r['unscorable'] or not m or m['unscorable']: return None
    return bool(m['event'])
mcells = []; _mok = {}; _mbad = set(); _mlow = {}; _mkeys = set(); _mwait = set()
for p in per:
    r = sm.get(p['id'])
    if not r or r['unscorable'] or not p['stated'] or not (0 <= p['lead_h'] < 48): continue
    k = (p['station'], p['start']); m = _mm.get((p['station'], p['start'], p['end']))
    if not m: _mwait.add(k); continue
    if m['unscorable']: _mbad.add(k); continue
    _mok[k] = True
    if p['pop'] in (0, 5): _mlow[k] = _mlow.get(k, False) or bool(m['event'])
for lo, hi, nm in BINS:
    for l0, l1, ln in LEADS:
        xs = [(p, _mev(p)) for p in per if p['stated'] and lo <= (p['pop'] if p['pop'] is not None else -1) <= hi and l0 <= p['lead_h'] < l1]
        xs = [(p, e) for p, e in xs if e is not None]
        xs = list({(p['station'], p['start']): (p, e) for p, e in sorted(xs, key=lambda z: -z[0]['fetched'])}.values())   # earliest fetch per period wins
        n = len(xs); _mkeys.update((p['station'], p['start']) for p, _ in xs)
        if not n: mcells.append(dict(bin=nm, lead=ln, n=0, outcome='CANNOT_TELL', reason=_K.NO_INTERVAL_FORMABLE)); continue
        k = sum(1 for _, e in xs if e); ms = sum(p['pop'] for p, _ in xs) / n; a, b = wil(k, n)
        oc, why = _cell_read(n, a, b, ms)
        mcells.append(dict(bin=nm, lead=ln, n=n, mean_stated=round(ms, 2), observed=round(100 * k / n, 2), lo=round(100 * a, 2), hi=round(100 * b, 2), outcome=oc, reason=why))
measurable_out = dict(rule='Measurable precipitation, 0.01 inch or more, from the routine hourly reports of the station (the NWS definition). Primary from 10 Nov 2026, decided after the data (PLAN.md Addendum 2).',
                      source='Iowa Environmental Mesonet ASOS archive, routine hourly METAR precipitation totals, a trace read as zero',
                      periods_scored=len(_mok), unscorable=len(_mbad - set(_mok)), waiting=len(_mwait - set(_mok) - _mbad), periods_in_no_cell=len(set(_mok) - _mkeys),
                      cell_periods=sum(c['n'] for c in mcells), floor=dict(periods=len(_mlow), with_event=sum(_mlow.values())), cells=mcells,
                      req13=_K.req13(mcells, nothing_returned=0))   # 12 Nov 2026: REQ-13 beside the primary table. No cell read is a failed read, so none is listed apart
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), stations=len(ST), forecasts_stored=len({(p['station'], p['fetched']) for p in per}), period_rows=len(per), periods_stored=len({(p['station'], p['start']) for p in per}), negative_lead_rows=sum(1 for p in per if p['lead_h'] < 0),
           periods_scored=scored, unscorable=unsc, not_stated=dropped, periods_in_no_cell=len(set(okp) - cellkeys), periods_in_cells=len(cellkeys), cell_periods=sum(c['n'] for c in cells),
           floor=dict(periods=lowev[1], with_event=lowev[0]), cells=cells,
           original_rule='Any hourly amount above zero, or a present-weather entry for rain, drizzle, snow, sleet, hail, showers or thunderstorm (PLAN.md, committed 28 Oct 2026 before any forecast was stored). Kept beside the primary reading, never deleted.',
           measurable=measurable_out, primary='measurable', req13=_K.req13(cells, nothing_returned=0), outcome_rule='PLAN_ADDENDUM_std2.md (12 Nov 2026): point figure, no tolerance, ABOVE, BELOW or CANNOT_TELL, under 30 periods TOO_WIDE_TO_RESOLVE')
json.dump(out, open('summary_forecast.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = _kv_put(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'forecast_live', '--path', os.path.join(H, 'summary_forecast.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('forecast:', nf, 'fetched,', nsc, 'scored,', _nm, 'measurable read this round;', len(per), 'periods stored;', 'published' if p.returncode == 0 else 'publish FAILED')
