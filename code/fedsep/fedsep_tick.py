#!/usr/bin/env python3
"""fedsep_tick.py: FEDSEP rider per PLAN.md. September SEP medians and stated 70% error ranges against realized outcomes from FRED's public downloads.
Runs under the revise venv (pypdf). Publishes KV fedsep_live. The parsed projections are stored in data/projections.json (a page is read once)."""
import os, sys, re, io, csv, json, time, random, logging, statistics as S, subprocess, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True); logging.disable(logging.CRITICAL)
VPY = os.path.expanduser('~/bones-forge/revise_index/venv/bin/python')
if os.path.realpath(sys.executable) != os.path.realpath(VPY) and not os.environ.get('FEDSEP_VENV'):
    os.execv(VPY, [VPY, os.path.abspath(__file__)] + sys.argv[1:])
import heuremen_kit as K, sep_parse as P
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('fedsep: plan not committed'); sys.exit(0)
W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); UA = {'User-Agent': 'heuremen-fedsep/0.1 (+https://indahl.ai/fedsep)'}
SEPT = ['20150917', '20160921', '20170920', '20180926', '20190918', '20200916', '20210922', '20220921', '20230920', '20240918', '20250917']
VARS = ['Change in real GDP', 'Unemployment rate', 'PCE inflation', 'Federal funds rate']
def fred(sid):
    t = urllib.request.urlopen(urllib.request.Request('https://fred.stlouisfed.org/graph/fredgraph.csv?id=' + sid, headers=UA), timeout=90).read().decode()
    return {r[0]: float(r[1]) for r in list(csv.reader(io.StringIO(t)))[1:] if len(r) > 1 and r[1] not in ('', '.')}
def q4avg(d, y): v = [d.get('%d-%02d-01' % (y, m)) for m in (10, 11, 12)]; return sum(v) / 3 if all(x is not None for x in v) else None
def outcomes():
    g, u, p, f = fred('GDPC1'), fred('UNRATE'), fred('PCEPI'), fred('FEDFUNDS'); tu, tl = fred('DFEDTARU'), fred('DFEDTARL'); o = {}
    def ye(y):
        ds = sorted(d for d in tu if d <= '%d-12-31' % y and d in tl); return (tu[ds[-1]] + tl[ds[-1]]) / 2 if ds and ds[-1] >= '%d-12-01' % y else None
    for y in range(2014, 2026):
        a, b = g.get('%d-10-01' % y), g.get('%d-10-01' % (y - 1)); pa, pb = q4avg(p, y), q4avg(p, y - 1)
        o[y] = {'Change in real GDP': 100 * (a / b - 1) if a and b else None, 'Unemployment rate': q4avg(u, y), 'PCE inflation': 100 * (pa / pb - 1) if pa and pb else None, 'Federal funds rate': q4avg(f, y), 'Federal funds rate, year-end': ye(y)}
    return o, u
# gate
inside = lambda med, out, rng: abs(out - med) <= rng + 1e-9
gate = inside(2.0, 3.0, 1.0) and not inside(2.0, 3.01, 1.0) and inside(2.0, 1.0, 1.0)
proj = json.load(open('data/projections.json')) if os.path.exists('data/projections.json') else {}
for d in SEPT:
    if d in proj: continue
    h = P.get('https://www.federalreserve.gov/monetarypolicy/fomcprojtabl%s.htm' % d); y, t1 = P.table1(h)
    if int(d[:4]) >= 2021: _, t2 = P.table2_html(h)
    else: _, t2 = P.table2_pdf(P.get('https://www.federalreserve.gov/monetarypolicy/files/fomcminutes%s.pdf' % d, True))
    proj[d] = dict(t1=t1, t2=t2)
json.dump(proj, open('data/projections.json', 'w'), indent=0)
p25 = proj['20250917']; gate &= [p25['t1'][v][0] for v in VARS] == [1.6, 4.5, 3.0, 3.6] and [p25['t2'][v][0] for v in VARS] == [1.4, 0.5, 1.0, 0.5]
O, U = outcomes()
bls = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.bls.gov/publicAPI/v1/timeseries/data/LNS14000000', headers=UA), timeout=60).read())
bq = [float(x['value']) for x in bls['Results']['series'][0]['data'] if x['year'] == '2024' and x['period'] in ('M10', 'M11', 'M12')]
gate &= len(bq) == 3 and abs(sum(bq) / 3 - O[2024]['Unemployment rate']) <= 0.05
gate &= proj['20160921']['t2']['Change in real GDP'][:2] == [1.3, 1.9] and proj['20160921']['t2']['Unemployment rate'][:2] == [0.3, 1.0] and proj['20160921']['t1']['Change in real GDP'][:2] == [1.8, 2.0]   # 29 Oct (audit): a known-good case for the minutes-PDF parser
print('fedsep: gate', 'passed' if gate else 'FAILED', flush=True)
if not gate: sys.exit(0)
trip = []; SK = []
for d in SEPT:
    s = int(d[:4])
    for hz in (0, 1):
        ty = s + hz
        if ty > 2025: continue
        for v in VARS:
            alt = O.get(ty, {}).get('Federal funds rate, year-end') if v == 'Federal funds rate' else None
            med = proj[d]['t1'].get(v, [None] * 4)[hz]; rng = proj[d]['t2'].get(v, [None] * 4)[hz] if proj[d]['t2'].get(v) else None; out = O.get(ty, {}).get(v)
            if med is None or rng is None or out is None: SK.append((s, hz, v, 'no median' if med is None else ('no stated range' if rng is None else 'outcome not available yet'))); continue
            trip.append(dict(sept=s, horizon=hz, target=ty, var=v, median=med, rng=rng, outcome=round(out, 2), err=round(out - med, 2), outside=not inside(med, out, rng), outside_alt=(not inside(med, alt, rng)) if alt is not None else (not inside(med, out, rng))))
rnd = random.Random(7)
def pooled(hz, alt=False):
    flag = 'outside_alt' if alt else 'outside'
    ts = [t for t in trip if t['horizon'] == hz]; yrs = sorted({t['sept'] for t in ts}); by = {y: [t for t in ts if t['sept'] == y] for y in yrs}; k = sum(t[flag] for t in ts)
    bs = []
    for _ in range(4000):
        sm = [t for y in (rnd.choice(yrs) for _ in yrs) for t in by[y]]; bs.append(sum(t[flag] for t in sm) / len(sm))
    bs.sort(); lo, hi = bs[int(0.025 * 4000)], bs[int(0.975 * 4000)]
    oc = K.ABOVE if lo > 0.30 else (K.BELOW if hi < 0.30 else (K.CONSISTENT if (hi - lo) <= 0.45 else K.CANNOT_TELL))
    return dict(triples=len(ts), years=len(yrs), outside=k, share=round(k / len(ts), 4), share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc)
pool = {'This year, September projection': pooled(0), 'Next year, September projection': pooled(1)}
sens = {'This year, funds rate scored at year-end': pooled(0, True), 'Next year, funds rate scored at year-end': pooled(1, True)}
per = {}
for hz in (0, 1):
    for v in VARS:
        ts = [t for t in trip if t['horizon'] == hz and t['var'] == v]
        if not ts: continue
        k = sum(t['outside'] for t in ts); lo, hi = K.wilson(k, len(ts)); oc = K.ABOVE if lo > 0.30 else (K.BELOW if hi < 0.30 else (K.CONSISTENT if (hi - lo) <= 0.45 else K.CANNOT_TELL))
        miss = max((abs(t['err']) - t['rng'] for t in ts), default=0)
        per['%s, %s' % (v, 'this year' if hz == 0 else 'next year')] = dict(n=len(ts), outside=k, share=round(k / len(ts), 4), share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc, mean_error=round(S.mean(t['err'] for t in ts), 2), range_typical=round(S.median(t['rng'] for t in ts), 2))
hand = [dict(year=t['target'], variable=t['var'], median=t['median'], outcome_value=t['outcome'], stated_range=t['rng'], miss=round(abs(t['err']) - t['rng'], 2), note=('Outside by 0.02 beyond a range printed to one decimal. ' if abs(abs(t['err']) - t['rng']) <= 0.03 else '') + ('Scored on the fourth-quarter average. At the year-end target midpoint it is inside. ' if t['var'] == 'Federal funds rate' and not t['outside_alt'] else '') + 'Median and range read from the SEP page, outcome from FRED')  for t in trip if t['horizon'] == 0 and t['outside']]
import collections as _C
skipped = dict(_C.Counter(r for *_, r in SK))
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), gate='passed', not_comparable=dict(n=len(SK), reasons=skipped), horizon1_misses=[dict(year=t['target'], variable=t['var'], median=t['median'], outcome_value=t['outcome'], stated_range=t['rng'], miss=round(abs(t['err']) - t['rng'], 2), note='Not yet opened by hand') for t in trip if t['horizon'] == 1 and t['outside']], septs=len(SEPT), triples=len(trip), claim='about 70 percent inside, so about 30 percent outside', pooled=pool, sensitivity=sens, per_variable=per, misses=sorted(hand, key=lambda x: (x['year'], x['variable'])))
json.dump(out, open('summary_fedsep.json', 'w'), indent=1); json.dump(trip, open('data/triples.json', 'w'))
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'fedsep_live', '--path', os.path.join(H, 'summary_fedsep.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('fedsep:', len(trip), 'triples', pool, 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
