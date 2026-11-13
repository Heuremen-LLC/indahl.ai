#!/usr/bin/env python3
"""measurable.py: FORECAST, the NWS event rule (PLAN.md Addendum 2, 10 Nov 2026).

The NWS states its chance of precipitation for measurable precipitation, 0.01 inch or more. This module reads, for each scored period, the
hourly precipitation totals in the routine hourly METAR reports of the same station, from the Iowa Environmental Mesonet ASOS archive
(api.weather.gov keeps only about seven days of observations, so the earlier periods can no longer be read there). A trace is read as zero.
A period has measurable precipitation when the routine reports inside it (valid after its start and up to its end) sum to 0.01 inch or more.
A period is unscorable under this rule when fewer than 75 percent of its hours have a routine report with a precipitation total.

  measurable.py backfill     read every scored period that has no reading yet (one archive request per station)
  measurable.py selftest     planted reports against the rule
Imported by forecast_tick.py, which calls update() each round. Results go to data/measurable.jsonl, one row per station and period."""
import os, sys, json, time, urllib.request, datetime as D
H = os.path.dirname(os.path.abspath(__file__)); UA = 'heuremen-forecast/0.1 (+https://indahl.ai/forecast)'
OUT = os.path.join(H, 'data', 'measurable.jsonl'); THRESH_IN = 0.01
IEM = ('https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station={st}&data=p01i&year1={a.year}&month1={a.month}&day1={a.day}'
       '&year2={b.year}&month2={b.month}&day2={b.day}&tz=Etc/UTC&format=onlycomma&latlon=no&missing=M&trace=T&direct=no&report_type=3')


def fetch_reports(station, t0, t1):
    """Routine hourly reports of one station from t0 to t1 (epoch s): list of (epoch, inches or None). Trace -> 0.0, missing -> None."""
    a = D.datetime.fromtimestamp(t0 - 86400, D.timezone.utc); b = D.datetime.fromtimestamp(t1 + 2 * 86400, D.timezone.utc)
    u = IEM.format(st=station[1:] if station.startswith('K') else station, a=a, b=b)
    for k in range(3):
        try:
            txt = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=90).read().decode('utf8', 'replace'); break
        except Exception:
            time.sleep(5 * (k + 1))
    else:
        return None
    rows = []
    for line in txt.splitlines()[1:]:
        p = line.split(',')
        if len(p) < 3: continue
        try: t = D.datetime.strptime(p[1], '%Y-%m-%d %H:%M').replace(tzinfo=D.timezone.utc).timestamp()
        except ValueError: continue
        v = p[2].strip(); rows.append((t, 0.0 if v == 'T' else (None if v in ('M', '') else float(v))))
    return rows


def score(reports, start, end):
    """One period under the NWS rule. reports: (epoch, inches or None) for the station."""
    inside = [(t, v) for t, v in reports if start < t <= end]
    hours = {int(t // 3600) for t, v in inside if v is not None}
    need = (end - start) / 3600; tot = sum(v for _, v in inside if v is not None)
    return dict(sum_in=round(tot, 3), hours_with_total=len(hours), unscorable=len(hours) < 0.75 * need, event=tot >= THRESH_IN - 1e-9)


def load():
    return {(r['station'], r['start'], r['end']): r for r in (json.loads(l) for l in open(OUT))} if os.path.exists(OUT) else {}


def update(per, scores, now=None, max_stations=30, settle_h=3):
    """Read the NWS-rule result for every scored period that has none yet. A period is read once its end is settle_h hours past,
    so the archive holds its last routine report. Returns the number of new rows."""
    now = now or time.time(); have = load(); sm = {x['id']: x for x in scores}; todo = {}
    for p in per:
        r = sm.get(p['id'])
        if not r or not p.get('stated') or p['end'] > now - settle_h * 3600: continue
        k = (p['station'], p['start'], p['end'])
        if k in have: continue
        todo.setdefault(p['station'], set()).add(k)
    n = 0
    with open(OUT, 'a') as f:
        for st in sorted(todo)[:max_stations]:
            ks = sorted(todo[st]); reps = fetch_reports(st, min(k[1] for k in ks), max(k[2] for k in ks)); time.sleep(1)
            if reps is None: continue
            for k in ks:
                f.write(json.dumps(dict(station=st, start=k[1], end=k[2], read=int(now), **score(reps, k[1], k[2]))) + '\n'); n += 1
    return n


def selftest():
    s, e = 0, 12 * 3600
    full = [(3600 * h + 3180, 0.0) for h in range(12)]
    assert score(full, s, e) == dict(sum_in=0.0, hours_with_total=12, unscorable=False, event=False)
    trace = full[:5] + [(5 * 3600 + 3180, 0.0)] + full[6:]           # a trace is read as zero: no event
    assert not score(trace, s, e)['event']
    one = full[:5] + [(5 * 3600 + 3180, 0.01)] + full[6:]            # one hour at 0.01 inch: an event
    assert score(one, s, e)['event']
    split = full[:3] + [(3 * 3600 + 3180, 0.004), (4 * 3600 + 3180, 0.006)] + full[5:]   # two hours summing to 0.01: an event
    assert score(split, s, e)['event']
    under = full[:3] + [(3 * 3600 + 3180, 0.004), (4 * 3600 + 3180, 0.005)] + full[5:]   # 0.009: no event
    assert not score(under, s, e)['event']
    gaps = [(t, None) if i < 4 else (t, v) for i, (t, v) in enumerate(full)]   # 8 of 12 hours with a total: unscorable
    assert score(gaps, s, e)['unscorable']
    edge = full + [(e + 600, 0.5), (s - 600, 0.5)]                    # reports outside the period are not read
    assert not score(edge, s, e)['event']
    print('measurable selftest: 7 of 7 planted cases read as planted')


if __name__ == '__main__':
    os.chdir(H)
    if sys.argv[1:] == ['selftest']: selftest()
    elif sys.argv[1:] == ['backfill']:
        ld = lambda f: [json.loads(l) for l in open(f)] if os.path.exists(f) else []
        print('measurable: %d new rows' % update(ld('data/periods.jsonl'), ld('data/scores.jsonl')))
    else: print(__doc__)
