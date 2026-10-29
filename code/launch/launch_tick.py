#!/usr/bin/env python3
"""launch_tick.py: LAUNCH rider for Nova's tick bus (every 6 ticks), per PLAN.md + Addendum 1. Snapshots the stated launch time of upcoming launches,
scores launches that have flown against the time stated at 1, 7 and 30 days before, publishes launch_live. Read-only, user agent names this site."""
import os, sys, json, time, math, urllib.request, subprocess, datetime as D, collections as C
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); os.makedirs('data', exist_ok=True)
UA = 'heuremen-launch/0.1 (+https://indahl.ai/launch)'; BASE = 'https://ll.thespacedevs.com/2.3.0/launches/'
def get(u):
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=40) as r: return json.loads(r.read())
        except Exception as e:
            print('launch: retry', a, e, file=sys.stderr); time.sleep(4 * (a + 1))
iso = lambda s: D.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
now = time.time(); up = get(BASE + 'upcoming/?limit=100&mode=normal'); time.sleep(2); pv = get(BASE + 'previous/?limit=100&mode=normal')
def load(f): return [json.loads(l) for l in open(f)] if os.path.exists(f) else []
snaps = load('data/snapshots.jsonl'); last = {}
for s in snaps: last[s['id']] = s
def row(r, t):
    return dict(id=r['id'], name=r['name'], provider=(r.get('launch_service_provider') or {}).get('name'), net=r['net'], prec=(r.get('net_precision') or {}).get('name'), status=(r.get('status') or {}).get('abbrev'), read=t)
out = open('data/snapshots.jsonl', 'a'); nw = 0
for r in ((up or {}).get('results', []) + (pv or {}).get('results', [])):
    if not r.get('net'): continue
    n = row(r, now); l = last.get(n['id'])
    if l and (l['net'], l['prec'], l['status']) == (n['net'], n['prec'], n['status']) and now - l['read'] < 6 * 3600: continue
    out.write(json.dumps(n) + '\n'); last[n['id']] = n; nw += 1
out.close()
snaps = load('data/snapshots.jsonl'); hist = C.defaultdict(list)
for s in snaps: hist[s['id']].append(s)
FLOWN = {'Success', 'Failure', 'Partial Failure'}; USABLE = {'Second', 'Minute', 'Hour', 'Day'}
LEADS = [(1, '1 day'), (7, '7 days'), (30, '30 days')]
import heuremen_kit as _K
def wil(k, n): return _K.wilson(k, n)   # 29 Oct: the local copy omitted the division by d; the kit's tested function replaces it
scored = {L: [] for L, _ in LEADS}; flown = 0; waiting = 0; coarse = 0; cancelled = 0
for i, hs in hist.items():
    fin = hs[-1]
    if fin['status'] in FLOWN:
        flown += 1; act = iso(fin['net'])
        for L, _ in LEADS:
            before = [h for h in hs if h['read'] <= act - L * 86400]
            if not before: continue
            b = before[-1]
            if b['prec'] not in USABLE: coarse += 1; continue
            scored[L].append((fin['provider'], (act - iso(b['net'])) / 3600))
    elif fin['status'] in ('Launch Failure',): pass
    elif iso(fin['net']) > now: waiting += 1
cells = []
def cell(lbl, ll, rows):
    n = len(rows)
    if not n: return None
    sl = sorted(abs(x) for _, x in rows); med = sl[n // 2] if n % 2 else (sl[n // 2 - 1] + sl[n // 2]) / 2; k = sum(1 for _, x in rows if abs(x) > 24); a, b = wil(k, n)
    oc = 'CANNOT_TELL' if (n < 30 or ll != '7 days') else ('ABOVE' if a > 0.25 else ('CONSISTENT' if b < 0.10 else 'CANNOT_TELL'))
    return dict(who=lbl, lead=ll, n=n, median_abs_slip_h=round(med, 1), over_24h=k, share=round(k / n, 3), lo=round(a, 3), hi=round(b, 3), outcome=oc)
for L, ll in LEADS:
    c = cell('All providers', ll, scored[L]); cells.append(c) if c else None
    byp = C.defaultdict(list)
    for p, x in scored[L]: byp[p or 'Unknown'].append((p, x))
    for p, rs in sorted(byp.items(), key=lambda kv: -len(kv[1])):
        if len(rs) >= 10:
            c = cell(p, ll, rs); cells.append(c) if c else None
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), launches_tracked=len(hist), snapshots=len(snaps), first_read=time.strftime('%Y-%m-%d', time.gmtime(min(s['read'] for s in snaps))) if snaps else None,
           flown=flown, waiting=waiting, coarse_precision=coarse, scored={ll: len(scored[L]) for L, ll in LEADS}, cells=cells)
json.dump(out, open('summary_launch.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'launch_live', '--path', os.path.join(H, 'summary_launch.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('launch:', nw, 'new snapshots;', len(hist), 'launches;', flown, 'flown;', 'published' if p.returncode == 0 else 'publish FAILED')
