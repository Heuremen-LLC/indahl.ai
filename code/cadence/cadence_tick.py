#!/usr/bin/env python3
"""cadence_tick.py: one CADENCE round for the HST tick bus, per PLAN.md. Fetches the one portal data.json that is due (24 hours since its last read), spot-checks up to 25 sampled download links with HEAD,
rewrites summary_cadence.json from everything stored, and publishes it. Read-only, our user agent names this site."""
import os, re, sys, json, time, math, hashlib, urllib.request, urllib.error, subprocess, datetime as D, email.utils, collections as C
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); UA = 'heuremen-cadence/0.1 (+https://indahl.ai/cadence)'; now = time.time()
PORTALS = [('CMS', 'https://data.cms.gov/data.json'), ('CDC', 'https://data.cdc.gov/data.json'), ('HealthData.gov', 'https://healthdata.gov/data.json'), ('Veterans Affairs', 'https://data.va.gov/data.json'),
           ('Energy', 'https://www.energy.gov/data.json'), ('Labor', 'https://www.dol.gov/data.json'), ('FEMA', 'https://www.fema.gov/data.json'), ('HealthCare.gov', 'https://data.healthcare.gov/data.json'), ('BLS', 'https://data.bls.gov/data.json')]
WORDS = {'daily': 1, 'weekly': 7, 'biweekly': 14, 'bi-weekly': 14, 'monthly': 30, 'bimonthly': 61, 'quarterly': 91, 'semiannual': 182, 'semiannually': 182, 'annually': 365, 'annual': 365, 'yearly': 365, 'biennial': 730, 'biennially': 730}
def interval_days(s):
    if not s: return None
    s = s.strip().lower()
    if s in WORDS: return WORDS[s]
    m = re.fullmatch(r'r/p(?:(\d+)y)?(?:(\d+)m)?(?:(\d+)w)?(?:(\d+)d)?(?:t(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?)?', s)
    if not m or not any(m.groups()): return None
    y, mo, w, d, h, mi, se = [int(x or 0) for x in m.groups()]; return y * 365 + mo * 30 + w * 7 + d + h / 24 + mi / 1440 + se / 86400
def get(u, head=False):
    req = urllib.request.Request(u, headers={'User-Agent': UA}, method='HEAD' if head else 'GET')
    try:
        with urllib.request.urlopen(req, timeout=120 if not head else 20) as r: return r.status, (r.info() if head else r.read())
    except urllib.error.HTTPError as e: return e.code, None
    except Exception: return None, None
def pdate(s):
    try:
        s = s.replace('Z', '+00:00'); d = D.datetime.fromisoformat(s) if 'T' in s or ' ' in s else D.datetime.fromisoformat(s + 'T23:59:59+00:00')
        return (d if d.tzinfo else d.replace(tzinfo=D.timezone.utc)).timestamp()
    except Exception: return None
state = json.load(open('data/state.json')) if os.path.exists('data/state.json') else {}
due = next(((n, u) for n, u in PORTALS if now - state.get(n, 0) > 24 * 3600), None)
if due:
    n, u = due; code, body = get(u)
    if code == 200:
        ds = json.loads(body).get('dataset', []); rows = []
        for x in ds:
            dist = (x.get('distribution') or [{}]); url = next((y.get('downloadURL') or y.get('accessURL') for y in dist if (y.get('downloadURL') or y.get('accessURL'))), None)
            pub = x.get('publisher') or {}; ag = pub.get('name') if isinstance(pub, dict) else None
            rows.append(dict(id=x.get('identifier') or x.get('title'), title=(x.get('title') or '')[:140], agency=ag, cadence=x.get('accrualPeriodicity'), modified=x.get('modified'), landing=x.get('landingPage') or x.get('identifier'), url=url))
        json.dump(dict(fetched=now, n_total=len(ds), rows=[r for r in rows if r['cadence']]), open(f'data/portal_{re.sub("[^a-z0-9]+", "_", n.lower())}.json', 'w')); state[n] = now; print('cadence:', n, len(ds), 'datasets read')
    else: print('cadence:', n, 'NOTHING_RETURNED', code); state[n] = now - 20 * 3600
json.dump(state, open('data/state.json', 'w'))
heads = [json.loads(l) for l in open('data/heads.jsonl')] if os.path.exists('data/heads.jsonl') else []; hd = {(h['portal'], h['id']) for h in heads}; nh = 0; hf = open('data/heads.jsonl', 'a')
for n, _ in PORTALS:
    f = f'data/portal_{re.sub("[^a-z0-9]+", "_", n.lower())}.json'
    if not os.path.exists(f) or nh >= 25: continue
    P = json.load(open(f)); cand = sorted([r for r in P['rows'] if r['url'] and interval_days(r['cadence']) and (n, r['id']) not in hd], key=lambda r: hashlib.sha1((n + str(r['id'])).encode()).hexdigest())
    have = sum(1 for h in heads if h['portal'] == n)
    for r in cand[:max(0, min(5, 200 - have))]:
        code, info = get(r['url'], head=True); lm = info.get('Last-Modified') if info else None; t = email.utils.parsedate_to_datetime(lm).timestamp() if lm else None
        hf.write(json.dumps(dict(portal=n, id=r['id'], status=code, last_modified_header=lm, header_ts=t, listed_modified=r['modified'], listed_ts=pdate(r['modified']) if r['modified'] else None)) + '\n'); nh += 1
        time.sleep(0.5)
hf.close(); heads = [json.loads(l) for l in open('data/heads.jsonl')]
import heuremen_kit as _K
def wil(k, n):   # 29 Oct: kit's tested Wilson; the cadence copy omitted the division by d
    if not n: return None
    p = k / n; lo, hi = _K.wilson(k, n); return [round(100 * p), round(100 * lo), round(100 * hi)]
def cls(d): return 'daily or faster' if d <= 1.5 else 'weekly' if d <= 8 else 'monthly' if d <= 35 else 'quarterly' if d <= 100 else 'yearly or slower'
out = []; over = []; why = C.Counter()
for n, _ in PORTALS:
    f = f'data/portal_{re.sub("[^a-z0-9]+", "_", n.lower())}.json'
    if not os.path.exists(f): continue
    P = json.load(open(f)); ok = bad = ct = 0; bycl = C.defaultdict(lambda: [0, 0]); ser = {}
    for r in P['rows']:
        lk = r['landing']; lk = lk.get('accessURL') if isinstance(lk, dict) else lk; key = lk or ('id:' + str(r['id'])); r['landing'] = lk
        mt0 = pdate(r['modified']) if r.get('modified') else None
        if key not in ser or (mt0 or 0) > (ser[key][1] or 0): ser[key] = (r, mt0)
    nrec = len(P['rows']); rows_s = [v[0] for v in ser.values()]
    for r in rows_s:
        d = interval_days(r['cadence']); mt = pdate(r['modified']) if r.get('modified') else None
        if d is None: ct += 1; why[(n, 'cadence not in the table')] += 1; continue
        if mt is None: ct += 1; why[(n, 'modified missing or unreadable')] += 1; continue
        I = max(d, 2); age = (P.get('fetched') or now) - mt; k = cls(d); bycl[k][1] += 1   # 29 Oct (audit): age is fetch time minus modified, as the plan says
        if age <= 2 * I * 86400: ok += 1
        else: bad += 1; bycl[k][0] += 1; over.append(dict(portal=n, title=r['title'], agency=r['agency'], cadence=r['cadence'], modified=r['modified'], age_days=round(age / 86400), ratio=round(age / 86400 / I, 1), link=r['landing']))
    hh = [h for h in heads if h['portal'] == n]; ag = [h for h in hh if h['status'] == 200 and h['header_ts'] and h['listed_ts']]; agree = sum(1 for h in ag if abs(h['header_ts'] - h['listed_ts']) <= 2 * 86400)
    out.append(dict(portal=n, read=time.strftime('%d %b %H:%M', time.gmtime(P['fetched'])), datasets_total=P['n_total'], stating_cadence=nrec, series=len(rows_s), readable=ok + bad, consistent=ok, below=bad, cannot_tell=ct, below_share=wil(bad, ok + bad),
                    by_class={k: dict(n=v[1], below=v[0], share=wil(v[0], v[1])) for k, v in bycl.items()}, heads=dict(sampled=len(hh), reachable=sum(1 for h in hh if h['status'] == 200), comparable=len(ag), agree=agree)))
over.sort(key=lambda x: -x['ratio']); summ = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), portals=out, most_overdue=over[:20])
json.dump(summ, open('summary_cadence.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'cadence_live', '--path', os.path.join(H, 'summary_cadence.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('cadence:', len(out), 'portals;', nh, 'head checks this round;', 'published' if p.returncode == 0 else 'publish FAILED')
