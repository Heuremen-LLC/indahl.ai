#!/usr/bin/env python3
"""stack_tick.py: STACK rider per PLAN.md. Reads the public feeds of the other pages and lines their headline tests up in one table. Adds no reading of its own."""
import os, sys, json, time, subprocess, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('stack: plan not committed'); sys.exit(0)
W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
def feed(slug):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request('https://indahl.ai/%s/live.json?x=%d' % (slug, time.time()), headers={'User-Agent': 'heuremen-stack/0.1'}), timeout=40).read())
    except Exception: return None
def at(d, path):
    for k in path:
        if isinstance(d, dict) and k in d: d = d[k]
        else: return None
    return d
def trials_outcome(lo, hi): return 'ABOVE' if lo > 0.25 else ('CONSISTENT' if hi < 0.10 else 'CANNOT_TELL')
# (page, slug, test, path, of key, failing key, share key, lo key, hi key, outcome key or None)
SPEC = [('SUPPORT', 'support', 'Supported cycles that had stopped releasing', ['all'], 'tested', 'silent', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('SUPPORT', 'support', 'Products with at least one such cycle', ['product_level', 'Products with at least one silent supported cycle'], 'tested', 'silent', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('PKGLICENSE', 'pkglicense', 'Stated license against the repository license', ['disagree'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('HFLICENSE', 'hflicense', 'Models: stated license against the license file', ['comparison', 'Models'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('HFLICENSE', 'hflicense', 'Datasets: stated license against the license file', ['comparison', 'Datasets'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('HFSIZE', 'hfsize', 'Size in the name against the weights', ['comparison'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('SECRECORDS', 'secrecords', 'HSTS preload header against its own requirements', ['comparison', 'HSTS preload header'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('SECRECORDS', 'secrecords', 'SPF record against the 10-lookup limit', ['comparison', 'SPF lookup limit'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('PKGINSTALL', 'pkginstall', 'Install command against pip resolution', ['comparison'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('LINKROT', 'linkrot', 'Stated code links that are gone', ['all'], 'links', 'gone', 'rot_share', 'lo', 'hi', 'outcome'),
        ('TRIALS', 'trials', 'Results due against results posted: records with no results', ['all'], 'n', 'no_results', 'share_no_results', 'lo', 'hi', None),
        ('TRIALS', 'trials', 'Stopped records with no reason given', ['cancelled', 'tests', 'Stopped records with no reason given'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'),
        ('TRIALS', 'trials', 'Withdrawn records that list participants enrolled', ['cancelled', 'tests', 'Withdrawn records that list participants enrolled'], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome')]
SPEC.append(('REVISE', 'revise', 'Payroll: first estimate moved by more than the stated margin by the third release', ['counts', 'Third release against first'], 'months', 'exceed', 'share', 'share_lo', 'share_hi', 'outcome'))
SPEC.append(('REVISE', 'revise', 'Payroll: first estimate moved by more than the stated margin by the benchmarked value', ['counts', 'Most recent, after the annual benchmark, against first'], 'months', 'exceed', 'share', 'share_lo', 'share_hi', 'outcome'))
for k, name in (('1 A cms-hpt.txt at the root of the domain', 'Hospital website: a cms-hpt.txt at the root'), ('2 The file it links resolves to data', 'Hospital price file: the linked file resolves to data'), ('3 The file starts with the template header', 'Hospital price file: starts with the template header')):
    SPEC.append(('HPT', 'hpt', name, ['comparison', k], 'of', 'n', 'share', 'share_lo', 'share_hi', 'outcome'))
rows = []; cache = {}
for page, slug, test, path, ok, fk, sk, lk, hk, ck in SPEC:
    if slug not in cache: cache[slug] = feed(slug)
    d = at(cache[slug], path) if cache[slug] else None
    if not isinstance(d, dict) or d.get(ok) in (None, 0) and d.get(fk) is None:
        rows.append(dict(page=page, slug=slug, test=test, of=None, n=None, share=None, share_lo=None, share_hi=None, outcome='NOTHING_RETURNED')); continue
    oc = d.get(ck) if ck else (trials_outcome(d[lk], d[hk]) if d.get(lk) is not None else 'NOTHING_RETURNED')
    rows.append(dict(page=page, slug=slug, test=test, of=d.get(ok), n=d.get(fk), share=d.get(sk), share_lo=d.get(lk), share_hi=d.get(hk), outcome=oc or 'NOTHING_RETURNED'))
ORDER = ['ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL', 'NOTHING_RETURNED']
rows.sort(key=lambda r: (ORDER.index(r['outcome']) if r['outcome'] in ORDER else 9, -(r['share_lo'] or 0)))
tally = {o: sum(1 for r in rows if r['outcome'] == o) for o in ORDER}
# pages that report many separate items: tally by the outcome of each item
def walk(d, out):
    if isinstance(d, dict):
        if isinstance(d.get('outcome'), str): out.append(d['outcome'])
        for v in d.values(): walk(v, out)
    elif isinstance(d, list):
        for v in d: walk(v, out)
items = []
for page, slug in (('TIME', 'time'), ('COIN', 'coin'), ('UPTIME', 'uptime'), ('FORECAST', 'forecast'), ('CADENCE', 'cadence'), ('CADA', 'cada'), ('LAUNCH', 'launch'), ('ARXIVDRIFT', 'arxivdrift')):
    d = feed(slug); o = []; walk(d, o); c = {x: o.count(x) for x in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')}
    if sum(c.values()): items.append(dict(page=page, slug=slug, **c))
rows_out = [dict(r, test_key=i) for i, r in enumerate(rows)]
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), tests=len(rows), tally={o: dict(n=tally[o]) for o in ORDER if tally[o]}, rows=[dict(page=r['page'], test=r['test'], of=r['of'], n=r['n'], share=r['share'], share_lo=r['share_lo'], share_hi=r['share_hi'], outcome=r['outcome']) for r in rows],
           items={i['page']: {k: v for k, v in i.items() if k not in ('page', 'slug')} for i in items})
json.dump(out, open('summary_stack.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'stack_live', '--path', os.path.join(H, 'summary_stack.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('stack:', len(rows), 'tests;', out['tally'], 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
