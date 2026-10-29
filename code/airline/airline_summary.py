#!/usr/bin/env python3
"""airline_summary.py: builds summary_airline.json from data/results.json (written by airline_tick.py) and publishes it to the KV key airline_live."""
import os, sys, json, time, subprocess
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('airline: plan not committed'); sys.exit(0)
NAME = dict(AA='American', AS='Alaska', B6='JetBlue', DL='Delta', F9='Frontier', G4='Allegiant', HA='Hawaiian', MQ='Envoy', NK='Spirit', OH='PSA', OO='SkyWest', UA='United', WN='Southwest', YX='Republic')
r = json.load(open('data/results.json')); L = r['late15']
def late(y, c):
    v = L[str(y)].get(c); return None if not v or not v[1] else v[0] / v[1]
def table(key, ya, yb):
    t = {}
    for c, v in r[key].items():
        row = dict(routes=v['routes'], outcome=v['outcome'])
        if 'change' in v:
            row.update(change=v['change'], change_ci=[v['lo'], v['hi']], flown_change=v['flown_change'])
        la, lb = late(ya, c), late(yb, c)
        row['late'] = ('%.1f%% then %.1f%%' % (100 * la, 100 * lb)) if la is not None and lb is not None else ''
        t[NAME.get(c, c) + ' (' + c + ')'] = row
    return t
a, b = table('c26_25', 2025, 2026), table('c25_19', 2019, 2025)
nb = [k for k, v in a.items() if v['outcome'] == 'ABOVE']; n = len([v for v in a.values() if v['outcome'] != 'NOTHING_RETURNED'])
lo, hi = K.wilson(len(nb), n)
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), read=r['t'], months=r['months'], gate='passed', rows=r['rows'], now_vs_2025=a, y2025_vs_2019=b,
           headline_n=len(nb), headline_of=n, headline=dict(of=n, n=len(nb), share=round(len(nb) / n, 4) if n else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome='CANNOT_TELL', above=nb))
json.dump(out, open('summary_airline.json', 'w'), indent=1)
W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'airline_live', '--path', os.path.join(H, 'summary_airline.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
with open('history.jsonl', 'a') as f: f.write(json.dumps(dict(t=out['updated'], above=len(nb), of=n)) + '\n')
print('airline:', len(nb), 'of', n, 'airlines ABOVE;', 'published' if pr.returncode == 0 else 'publish FAILED ' + (pr.stderr or pr.stdout)[-300:])
