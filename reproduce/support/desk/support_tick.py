#!/usr/bin/env python3
"""support_tick.py: SUPPORT rider per PLAN.md. Reads endoflife.date, tests stated support windows against release activity, publishes KV support_live.
Detaches into the background so the tick bus is not held (about 6 minutes for the whole product list)."""
import os, sys, re, json, time, datetime as D, collections as C, subprocess, fcntl, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
if not os.environ.get('SUPPORT_FORKED'):
    subprocess.Popen([sys.executable, '-I', os.path.abspath(__file__)], env=dict(os.environ, SUPPORT_FORKED='1'), stdout=open('data/last_run.log', 'w'), stderr=subprocess.STDOUT, start_new_session=True); print('support: started in the background'); sys.exit(0)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('support: plan not committed'); sys.exit(0)
_l = open('data/.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('support: another run holds the lock'); sys.exit(0)
UA = {'User-Agent': 'heuremen-support/0.1 (+https://indahl.ai/support)'}; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
def get(u):
    for a in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40))
        except Exception: time.sleep(3 * (a + 1))
today = D.date.today()
def d(x):
    try: return D.date.fromisoformat(x) if isinstance(x, str) else None
    except Exception: return None
def score(c):
    """returns (state, unreleased, gap_days_after_eol) for one cycle dict"""
    eol, sup, rel, last = c.get('eol'), c.get('support'), d(c.get('releaseDate')), d(c.get('latestReleaseDate'))
    eold = d(eol); supd = d(sup)
    if last is None: return 'NO_RELEASE_DATE', None, None
    if eol is True: return 'EOL_NO_DATE', None, None          # addendum 1: boolean true means ended, no date given
    if eold is not None and eold <= today:
        return 'EOL_PASSED', None, (last - eold).days
    # 10 Nov 2026 (Addendum 3, newsletter audit): the plan's rule. A cycle is SUPPORTED only if its stated support end has not passed, whatever
    # its end of life says, and it is tested only if it was released more than 400 days ago, which needs a release date. Until 10 Nov the code
    # tested a cycle whose support end had passed whenever its end of life was in the future, and tested cycles with no release date.
    if supd is not None and supd <= today: return ('SUPPORT_ENDED_NO_EOL' if eold is None else 'SUPPORT_ENDED'), None, None
    if rel is None: return 'NO_CYCLE_RELEASE_DATE', None, None
    if (today - rel).days <= 400: return 'SUPPORTED_TOO_NEW', None, None
    return 'SUPPORTED', (today - last).days > 365, None
def score_old(c):
    """The rule the code ran until 10 Nov 2026, kept only to print its count beside the plan's (labelled on the page)."""
    eol, sup, rel, last = c.get('eol'), c.get('support'), d(c.get('releaseDate')), d(c.get('latestReleaseDate'))
    eold = d(eol); supd = d(sup)
    if last is None or eol is True or (eold is not None and eold <= today): return None
    if supd is not None and supd <= today and eold is None: return None
    if rel is not None and (today - rel).days <= 400: return None
    return (today - last).days > 365
SUMMARY_ONLY = bool(os.environ.get('SUPPORT_SUMMARY_ONLY'))
prods = [] if SUMMARY_ONLY else (get('https://endoflife.date/api/all.json') or [])
def cyc(p): return get('https://endoflife.date/api/%s.json' % p)
# gate
py = {} if SUMMARY_ONLY else {c['cycle']: c for c in (cyc('python') or [])}
g1 = py.get('3.8') and score(py['3.8'])[0] == 'EOL_PASSED' and score(py['3.8'])[2] is not None and score(py['3.8'])[2] <= 0
g2 = py.get('3.15') and score(py['3.15'])[0] in ('SUPPORTED', 'SUPPORTED_TOO_NEW') and score(py['3.15'])[1] is not True
gate = bool(g1 and g2) if not SUMMARY_ONLY else (json.load(open('summary_support.json')).get('gate') == 'passed'); print('support: gate', 'passed' if gate else 'FAILED')
rows = []; none = 0
if gate and not SUMMARY_ONLY:
    for p in prods:
        cs = cyc(p); time.sleep(0.7)
        if not cs: none += 1; continue
        for c in cs:
            st, unreleased, gap = score(c); rows.append(dict(product=p, cycle=str(c.get('cycle')), state=st, unreleased=unreleased, gap=gap, last=c.get('latestReleaseDate'), eol=c.get('eol'), support=c.get('support'), released=c.get('releaseDate'), old_rule=score_old(c)))
    json.dump(rows, open('data/cycles.json.tmp', 'w')); os.replace('data/cycles.json.tmp', 'data/cycles.json')
elif os.path.exists('data/cycles.json'):
    rows = json.load(open('data/cycles.json'))
    for _r in rows:
        if 'unreleased' not in _r: _r['unreleased'] = _r.pop('silent', False)   # 29 Oct: rows saved before the class was renamed
if SUMMARY_ONLY and not rows: sys.exit('no cycles')
tested = [r for r in rows if r['state'] == 'SUPPORTED']; sil = [r for r in tested if r['unreleased']]
import random
def boot_cluster(byprod, n_boot=4000):
    rnd = random.Random(7); P = list(byprod); est = []
    for _ in range(n_boot):
        ch = [rnd.choice(P) for _ in P]; n = sum(len(byprod[p]) for p in ch); k = sum(sum(byprod[p]) for p in ch); est.append(k / n if n else 0)
    est.sort(); return est[int(0.025 * n_boot)], est[int(0.975 * n_boot) - 1]
def cell(n, k):
    lo, hi = K.wilson(k, n); oc = K.CANNOT_TELL if (n < 30 or not gate) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
    return dict(tested=n, unreleased=k, share=round(k / n, 4) if n else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc)
byp = C.defaultdict(list)
for r in tested: byp[r['product']].append(r)
products = {p: cell(len(v), sum(1 for r in v if r['unreleased'])) for p, v in byp.items() if sum(1 for r in v if r['unreleased']) > 0}
products = dict(sorted(products.items(), key=lambda kv: -kv[1]['unreleased'])[:60])
eolr = [r for r in rows if r['state'] == 'EOL_PASSED']; bk = C.Counter('before' if r['gap'] <= 0 else ('within 90 days after' if r['gap'] <= 90 else ('90 to 365 days after' if r['gap'] <= 365 else 'more than a year after')) for r in eolr)
after = {k: dict(cycles=bk[k]) for k in ('before', 'within 90 days after', '90 to 365 days after', 'more than a year after')}
silent_list = sorted([dict(product=r['product'], cycle=r['cycle'], last=r['last'], eol=str(r['eol']), days=(today - D.date.fromisoformat(r['last'])).days) for r in sil], key=lambda x: -x['days'])[:150]
byprod_all = {p: [bool(r['unreleased']) for r in v] for p, v in byp.items()}
c_lo, c_hi = boot_cluster(byprod_all) if byprod_all else (0, 1)
allc = cell(len(tested), len(sil)); allc.update(wilson_lo=allc['share_lo'], wilson_hi=allc['share_hi'], share_lo=round(c_lo, 4), share_hi=round(c_hi, 4), products_tested=len(byprod_all))
allc['outcome'] = K.CANNOT_TELL if (len(tested) < 30 or not gate) else (K.ABOVE if c_lo > 0.10 else (K.CONSISTENT if c_hi < 0.05 else K.CANNOT_TELL))
_old = [r for r in rows if r.get('old_rule') is not None]
old_rule_cell = None   # top level in the feed, since a nested object in 'all' would break the page's flat table
if _old: old_rule_cell = dict(tested=len(_old), unreleased=sum(1 for r in _old if r['old_rule']), share=round(sum(1 for r in _old if r['old_rule']) / len(_old), 4), rule='the rule the code ran until 10 Nov 2026: a cycle whose stated support end had passed was still tested when its end of life was in the future, and cycles with no release date were tested')
anyp = sum(1 for v in byprod_all.values() if any(v)); allp = sum(1 for v in byprod_all.values() if v and all(v))
product_level = {'Products with at least one unreleased supported cycle': cell(len(byprod_all), anyp), 'Products where every tested supported cycle is unreleased': cell(len(byprod_all), allp)}
for k2 in product_level.values(): k2['tested'] = k2.pop('tested'); 
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), gate='passed' if gate else 'FAILED', all_old_rule=old_rule_cell, products=len({r['product'] for r in rows}), no_cycles=none, cycles=len(rows), supported_tested=len(tested), all=allc, product_level=product_level, by_product=products, after_eol=after, silent_list=silent_list,
           apart=dict(eol_no_date=sum(1 for r in rows if r['state'] == 'EOL_NO_DATE'), no_release_date=sum(1 for r in rows if r['state'] == 'NO_RELEASE_DATE'), too_new=sum(1 for r in rows if r['state'] == 'SUPPORTED_TOO_NEW'), support_ended_no_eol=sum(1 for r in rows if r['state'] == 'SUPPORT_ENDED_NO_EOL'), support_ended=sum(1 for r in rows if r['state'] == 'SUPPORT_ENDED'), no_cycle_release_date=sum(1 for r in rows if r['state'] == 'NO_CYCLE_RELEASE_DATE')))
json.dump(out, open('summary_support.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
if os.environ.get('SUPPORT_NO_PUBLISH'): print('support: summary written, not published (SUPPORT_NO_PUBLISH)'); sys.exit(0)
for _try in range(3):   # 31 Oct: one transient wrangler failure left the feed stale; retry, and log the error when it still fails
    pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'support_live', '--path', os.path.join(H, 'summary_support.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
    if pr.returncode == 0: break
    print('support: publish attempt %d failed: %s' % (_try + 1, (pr.stderr or pr.stdout or '').strip().splitlines()[-1:] ), flush=True); time.sleep(20)
print('support:', len(prods), 'products,', len(rows), 'cycles,', len(tested), 'tested,', len(sil), 'unreleased,', out['all']['outcome'], 'published' if pr.returncode == 0 else 'publish FAILED')
