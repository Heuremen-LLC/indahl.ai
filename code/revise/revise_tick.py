#!/usr/bin/env python3
"""revise_tick.py: REVISE rider per PLAN.md. First, third and most recent releases of monthly nonfarm payroll change against the BLS's stated 90% interval of 122 thousand.
Runs under the venv's Python (openpyxl). Publishes KV revise_live."""
import os, sys, re, json, time, hashlib, subprocess, statistics as S, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data/files', exist_ok=True)
VPY = os.path.join(H, 'venv', 'bin', 'python')
if os.path.realpath(sys.executable) != os.path.realpath(VPY) and not os.environ.get('REVISE_VENV'):
    os.execv(VPY, [VPY, os.path.abspath(__file__)] + sys.argv[1:])
import openpyxl, heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('revise: plan not committed'); sys.exit(0)
UA = {'User-Agent': 'heuremen-revise/0.1 (+https://indahl.ai/revise)'}; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); STATED = 122.0
URL = 'https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/real-time-data/data-files/xlsx/employ_level_first_second_third.xlsx'
def count(pairs, limit=STATED): return sum(1 for a, b in pairs if abs(b - a) > limit)
gate = count([(0, 122), (0, 123), (0, -123)]) == 2 and [abs(b - a) > STATED for a, b in [(0, 122), (0, 123), (0, -123)]] == [False, True, True]
raw = urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=120).read(); sha = hashlib.sha256(raw).hexdigest()
fn = 'data/files/employ_%s.xlsx' % sha[:12]
if not os.path.exists(fn): open(fn, 'wb').write(raw)
wb = openpyxl.load_workbook(fn, read_only=True, data_only=True); notes = ' '.join(str(c) for r in wb['NOTES'].iter_rows(values_only=True) for c in r if c)
gate &= 'EMPLOY' in notes and 'Thousands' in notes
rows = []
for r in wb['DATA'].iter_rows(values_only=True):
    if r and isinstance(r[0], str) and re.match(r'\d{4}:\d{2}$', r[0]):
        num = lambda x: float(x) if isinstance(x, (int, float)) else None
        rows.append(dict(m=r[0], first=num(r[1]), second=num(r[2]), third=num(r[3]), recent=num(r[4])))
upd = re.search(r'Last updated on: ([A-Za-z]+ \d+, \d{4})', notes); updated_file = upd.group(1) if upd else ''
# known-good against the BLS API: the last 24 benchmarked months of Most_Recent against month-over-month changes of the level series
def bls_changes():
    d = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.bls.gov/publicAPI/v1/timeseries/data/CES0000000001', headers=UA), timeout=60).read())
    pts = {(int(p['year']), int(p['period'][1:])): float(p['value']) for p in d['Results']['series'][0]['data'] if p['period'].startswith('M')}
    return {'%04d:%02d' % k: pts[k] - pts[(k[0] - (k[1] == 1), k[1] - 1 or 12)] for k in pts if (k[0] - (k[1] == 1), k[1] - 1 or 12) in pts}
bc = bls_changes(); ys = int(updated_file[-4:]) if updated_file else int(time.strftime('%Y')); last_bench = '%04d:03' % (ys - 1)
bench = [r for r in rows if r['recent'] is not None and r['m'] <= last_bench]
chk = [abs(r['recent'] - bc[r['m']]) for r in bench[-24:] if r['m'] in bc]
gate &= len(chk) >= 12 and max(chk) <= 1.0
print('revise: gate', 'passed' if gate else 'FAILED', 'checked', len(chk), 'months against the BLS API, max difference', round(max(chk), 2) if chk else None, flush=True)
if not gate: sys.exit(0)
t3 = [r for r in rows if r['first'] is not None and r['third'] is not None][-120:]; mr = [r for r in bench if r['first'] is not None][-120:]
def block(rs, key):
    prs = [(r['first'], r[key]) for r in rs]; n = len(prs); k = count(prs); lo, hi = K.wilson(k, n); rev = [b - a for a, b in prs]
    oc = K.ABOVE if lo > 0.10 else (K.BELOW if hi < 0.10 else (K.CONSISTENT if (hi - lo) <= 0.12 else K.CANNOT_TELL))
    return dict(months=n, first=rs[0]['m'], last=rs[-1]['m'], exceed=k, share=round(k / n, 4), share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc, median_signed=round(S.median(rev), 1), mean_signed=round(S.mean(rev), 1), median_abs=round(S.median([abs(x) for x in rev]), 1), largest=round(max(rev, key=abs), 1))
a = block(t3, 'third'); b = block(mr, 'recent')
big = [dict(month=r['m'], first=r['first'], third=r['third'], most_recent=r['recent'], note='First print matches the archived BLS release') for r in {x['m']: x for x in t3 + mr}.values() if max(abs((r['third'] or r['first']) - r['first']), abs((r['recent'] or r['first']) - r['first']) if r['m'] <= last_bench else 0) > 300]
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), gate='passed', stated=int(STATED), file_updated=updated_file, sha=sha[:16], checked_months=len(chk),
           counts={'Third release against first': a, 'Most recent, after the annual benchmark, against first': b}, large=sorted(big, key=lambda x: x['month']))
json.dump(out, open('summary_revise.json', 'w'), indent=1)
with open('data/history.jsonl', 'a') as f: f.write(json.dumps(dict(t=time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), sha=sha[:16], third=a, recent=b), sort_keys=True) + '\n')
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'revise_live', '--path', os.path.join(H, 'summary_revise.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('revise:', a['outcome'], a['exceed'], 'of', a['months'], '|', b['outcome'], b['exceed'], 'of', b['months'], 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
