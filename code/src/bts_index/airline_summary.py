#!/usr/bin/env python3
"""airline_summary.py: builds summary_airline.json from data/results.json (written by airline_tick.py) and publishes it to the KV key airline_live."""
import os, sys, json, time, subprocess
import os as _pg_os, sys as _pg_sys, subprocess as _pg_sp   # 10 Nov 2026 (publish guard): the site KV is written only by a run the tick bus or the house clock started
_PUBLISH = '--publish' in _pg_sys.argv or _pg_os.environ.get('HEUREMEN_PUBLISH') == '1'   # (they export HEUREMEN_PUBLISH=1) or a run given --publish. A copy run for a reproduce kit or a test never publishes
if _PUBLISH: _pg_os.environ['HEUREMEN_PUBLISH'] = '1'   # passed on to the scripts this one starts, and kept across a detach or re-exec
def _kv_put(cmd, **kw):
    if _PUBLISH: return _pg_sp.run(cmd, **kw)
    print('publish guard: %s not put to the site KV (run with --publish, or from the tick bus)' % cmd[5], file=_pg_sys.stderr)
    return _pg_sp.CompletedProcess(cmd, 0, '' if kw.get('text') or kw.get('universal_newlines') else b'', '' if kw.get('text') or kw.get('universal_newlines') else b'')
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
        row = dict(routes=v['routes'], outcome=v['outcome'], reason=v.get('reason'))   # 12 Nov 2026 (PLAN_ADDENDUM_std2.md): every CANNOT_TELL carries its reason
        if 'change' in v:
            row.update(change=v['change'], change_ci=[v['lo'], v['hi']], flown_change=v['flown_change'], interval_method=v.get('interval_method'))
            if 'outcome_pre_std2' in v: row.update(outcome_pre_std2=v['outcome_pre_std2'], change_ci_pre_std2=[v['lo_pre_std2'], v['hi_pre_std2']], method_pre_std2=v['method_pre_std2'])   # the 29 Oct reading, beside the new one
        la, lb = late(ya, c), late(yb, c)
        row['late'] = ('%.1f%% then %.1f%%' % (100 * la, 100 * lb)) if la is not None and lb is not None else ''
        t[NAME.get(c, c) + ' (' + c + ')'] = row
    return t
a, b = table('c26_25', 2025, 2026), table('c25_19', 2019, 2025)
nb = [k for k, v in a.items() if v['outcome'] == 'ABOVE']; n = len(a)   # 12 Nov 2026: an airline under 30 routes is CANNOT_TELL TOO_WIDE_TO_RESOLVE and is a reading, so it is in the denominator
lo, hi = K.wilson(len(nb), n)
R13 = K.req13([(v['outcome'], v.get('reason')) for v in a.values()], nothing_returned=0); R13b = K.req13([(v['outcome'], v.get('reason')) for v in b.values()], nothing_returned=0)
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), read=r['t'], months=r['months'], gate='passed', rows=r['rows'], now_vs_2025=a, y2025_vs_2019=b,
           headline_n=len(nb), headline_of=n, headline=dict(of=n, n=len(nb), share=round(len(nb) / n, 4) if n else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome='CANNOT_TELL', reason=K.NO_INTERVAL_FORMABLE, outcome_why='the plan names no bound or band for a count of airlines, so no outcome can be formed (PLAN_ADDENDUM_std2.md)', above=nb, req13=R13), req13_y2025_vs_2019=R13b, standard='Faults and Guards 2.0.0', seed=r.get('seed'))
json.dump(out, open('summary_airline.json', 'w'), indent=1)
W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = _kv_put(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'airline_live', '--path', os.path.join(H, 'summary_airline.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
with open('history.jsonl', 'a') as f: f.write(json.dumps(dict(t=out['updated'], above=len(nb), of=n)) + '\n')
print('airline:', len(nb), 'of', n, 'airlines ABOVE;', 'published' if pr.returncode == 0 else 'publish FAILED ' + (pr.stderr or pr.stdout)[-300:])
