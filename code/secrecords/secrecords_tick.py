#!/usr/bin/env python3
"""secrecords_tick.py: SECRECORDS rider per PLAN.md. Top 1,000 Tranco domains: an HSTS preload header against its own requirements, and an SPF record against the 10-lookup limit.
Detaches into the background. DISAGREE rows are listed only after they are in data/hand_checked.json (key kind|domain). Publishes KV secrecords_live.
SECRECORDS_SUMMARY_ONLY=1 rebuilds the summary from stored data."""
import os, sys, re, io, json, time, zipfile, collections as C, subprocess, fcntl, urllib.request, urllib.error, urllib.parse, ssl
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
if not os.environ.get('SR_FORKED') and not os.environ.get('SECRECORDS_SUMMARY_ONLY'):
    subprocess.Popen([sys.executable, '-I', os.path.abspath(__file__)], env=dict(os.environ, SR_FORKED='1'), stdout=open('data/last_run.log', 'w'), stderr=subprocess.STDOUT, start_new_session=True); print('secrecords: started in the background'); sys.exit(0)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('secrecords: plan not committed'); sys.exit(0)
_l = open('data/.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('secrecords: another run holds the lock'); sys.exit(0)
UA = 'heuremen-secrecords/0.1 (+https://indahl.ai/secrecords)'; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); SUMMARY_ONLY = bool(os.environ.get('SECRECORDS_SUMMARY_ONLY'))
def hsts_class(h):
    if not h: return 'NOT_COMPARABLE', 'no HSTS header'
    d = [x.strip().lower() for x in h.split(';')]
    if 'preload' not in d: return 'NOT_COMPARABLE', 'header does not state preload'
    ma = next((int(x.split('=', 1)[1].strip('" ')) for x in d if x.startswith('max-age=') and x.split('=', 1)[1].strip('" ').isdigit()), None)
    ok = ma is not None and ma >= 31536000 and 'includesubdomains' in d
    return ('AGREE' if ok else 'DISAGREE'), None
def doh(name, typ='TXT', n=3):
    u = 'https://cloudflare-dns.com/dns-query?' + urllib.parse.urlencode({'name': name, 'type': typ})
    for i in range(n):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={'accept': 'application/dns-json', 'User-Agent': UA}), timeout=20).read())
            return [a['data'].replace('" "', '').strip('"') for a in r.get('Answer', []) if a.get('type') == 16]
        except Exception: time.sleep(1 + i)
    return None
def spf_of(name, fetch):
    t = fetch(name)
    if t is None: return None, False
    s = [x for x in t if x.lower().startswith('v=spf1')]
    return (s[0] if s else ''), True
def spf_count(name, fetch, depth=0, path=()):
    """-> (lookups, complete). RFC 7208 section 4.6.4: every include, a, mx, ptr, exists and redirect term counts 1 each time it is evaluated, plus whatever the included or redirected record needs.
    29 Oct (internal audit): an include met twice is evaluated twice and counts twice. Only a cycle (a record that includes itself through its own chain) is cut."""
    if depth > 10 or name in path: return 0, depth <= 10
    rec, ok = spf_of(name, fetch)
    if not ok: return 0, False
    n = 0; complete = True
    for tok in rec.split()[1:]:
        t = tok.lstrip('+-~?').lower()
        m = re.match(r'(include|redirect)[:=](\S+)', t)
        if m:
            n += 1; k, c = spf_count(m.group(2), fetch, depth + 1, path + (name,)); n += k; complete &= c
        elif re.match(r'(a|mx|ptr|exists)([:/]|$)', t): n += 1
    return n, complete
def spf_class(name, fetch):
    rec, ok = spf_of(name, fetch)
    if not ok: return 'NOT_COMPARABLE', 'DNS read failed', None
    if not rec: return 'NOT_COMPARABLE', 'no SPF record', None
    n, c = spf_count(name, fetch)
    if n > 10: return 'DISAGREE', None, n
    if not c: return 'NOT_COMPARABLE', 'count cut short', n
    return 'AGREE', None, n
# gate
HS = [('max-age=31536000; includeSubDomains; preload', 'AGREE'), ('max-age=300; preload', 'DISAGREE'), ('max-age=63072000; preload', 'DISAGREE'), ('max-age=31536000; includeSubDomains', 'NOT_COMPARABLE'), ('MAX-AGE=31536000; INCLUDESUBDOMAINS; PRELOAD', 'AGREE'), (None, 'NOT_COMPARABLE')]
gate_h = all(hsts_class(h)[0] == w for h, w in HS)
P = {'dup.test': ['v=spf1 include:rep.test include:rep.test -all'], 'rep.test': ['v=spf1 a mx ptr exists:x.test a:y.test mx:z.test -all'], 'a.test': ['v=spf1 include:i1.test include:i2.test include:i3.test -all'], 'i1.test': ['v=spf1 ip4:1.2.3.4 -all'], 'i2.test': ['v=spf1 ip4:1.2.3.5 -all'], 'i3.test': ['v=spf1 ip6:::1 -all'],
     'b.test': ['v=spf1 include:c1.test -all'], 'd.test': ['v=spf1 redirect=i1.test'], 'e.test': ['v=spf1 ip4:1.2.3.4 ~all']}
for k in range(1, 12): P['c%d.test' % k] = ['v=spf1 include:c%d.test a mx' % (k + 1) if k < 11 else 'v=spf1 ip4:1.1.1.1 -all']
fp = lambda n: P.get(n)
r1 = spf_count('a.test', fp)[0] == 3; r2 = spf_class('b.test', fp)[0] == 'DISAGREE'; r3 = spf_count('d.test', fp)[0] == 1; r4 = spf_count('e.test', fp)[0] == 0; r5 = spf_count('b.test', fp)[0] > 10
r6 = spf_count('dup.test', fp)[0] == 14
gate_s = all((r1, r2, r3, r4, r5, r6)); live_ok = True
if not SUMMARY_ONLY:
    try:
        rq = urllib.request.urlopen(urllib.request.Request('https://github.com/', headers={'User-Agent': UA}), timeout=20); live_ok &= hsts_class(rq.headers.get('Strict-Transport-Security'))[0] == 'AGREE'
        c, _, n = spf_class('google.com', doh); live_ok &= c == 'AGREE'
    except Exception: live_ok = False
gate = bool(gate_h and gate_s and live_ok) if not SUMMARY_ONLY else bool(gate_h and gate_s and json.load(open('summary_secrecords.json')).get('gate') == 'passed')
print('secrecords: gate', 'passed' if gate else 'FAILED', gate_h, gate_s, live_ok, flush=True)
store = json.load(open('data/domains.json')) if os.path.exists('data/domains.json') else {}; now = time.time()
if gate and not SUMMARY_ONLY:
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(urllib.request.Request('https://tranco-list.eu/top-1m.csv.zip', headers={'User-Agent': UA}), timeout=300).read()))
    rows = [l.split(',') for l in z.read(z.namelist()[0]).decode().splitlines()[:1000]]; store = {}
    open('data/listdate.txt', 'w').write(time.strftime('%Y-%m-%d', time.gmtime(now)))
    ctx = ssl.create_default_context()
    for i, (rk, dom) in enumerate(rows):
        dom = dom.strip(); rec = dict(read=now, domain=dom, rank=int(rk))
        try:
            rq = urllib.request.urlopen(urllib.request.Request('https://%s/' % dom, headers={'User-Agent': UA}), timeout=15, context=ctx); h = rq.headers.get('Strict-Transport-Security'); rec['final'] = urllib.parse.urlparse(rq.geturl()).hostname; rec['hsts'] = h
            rec['hsts_cls'], rec['hsts_why'] = hsts_class(h)
        except urllib.error.HTTPError as e:
            h = e.headers.get('Strict-Transport-Security'); rec['hsts'] = h; rec['hsts_cls'], rec['hsts_why'] = hsts_class(h)
        except Exception as e: rec.update(hsts=None, hsts_cls='NOT_COMPARABLE', hsts_why='HTTPS request failed')
        rec['spf_cls'], rec['spf_why'], rec['spf_n'] = spf_class(dom, doh)
        if rec['spf_cls'] != 'NOT_COMPARABLE' or rec['spf_why'] == 'count cut short': rec['spf'] = (spf_of(dom, doh)[0] or '')[:400]
        d = doh('_dmarc.' + dom); pol = next((re.search(r'p=(\w+)', x, re.I).group(1).lower() for x in (d or []) if x.lower().startswith('v=dmarc1') and re.search(r'p=(\w+)', x, re.I)), None)
        rec['dmarc'] = ('p=' + pol) if pol else ('read failed' if d is None else 'no record')
        store[dom] = rec; time.sleep(0.1)
        if i % 50 == 49: json.dump(store, open('data/domains.json.tmp', 'w')); os.replace('data/domains.json.tmp', 'data/domains.json'); print('secrecords: read', i + 1, flush=True)
    json.dump(store, open('data/domains.json.tmp', 'w')); os.replace('data/domains.json.tmp', 'data/domains.json')
if os.environ.get('SECRECORDS_SPF_REREAD') and gate:
    for i, (dom, rec) in enumerate(store.items()):
        if rec.get('spf_cls') == 'NOT_COMPARABLE' and rec.get('spf_why') in ('no SPF record',): continue
        c, w, n = spf_class(dom, doh); rec['spf_cls'], rec['spf_why'], rec['spf_n'] = c, w, n
        if c != 'NOT_COMPARABLE' or w == 'count cut short': rec['spf'] = (spf_of(dom, doh)[0] or '')[:400]
        time.sleep(0.05)
        if i % 100 == 99: json.dump(store, open('data/domains.json.tmp', 'w')); os.replace('data/domains.json.tmp', 'data/domains.json'); print('secrecords: spf reread', i + 1, flush=True)
    json.dump(store, open('data/domains.json.tmp', 'w')); os.replace('data/domains.json.tmp', 'data/domains.json')
hc = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}
rs = list(store.values())
def grp(key, kind):
    cnt = C.Counter(r[key + '_cls'] for r in rs); comp = cnt['AGREE'] + cnt['DISAGREE']; lo, hi = K.wilson(cnt['DISAGREE'], comp)
    oc = K.CANNOT_TELL if (comp < 30 or not gate) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
    return cnt, dict(of=comp, n=cnt['DISAGREE'], share=round(cnt['DISAGREE'] / comp, 4) if comp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc, awaiting=len([r for r in rs if r[key + '_cls'] == 'DISAGREE' and kind + '|' + r['domain'] not in hc]))
ch, cmp_h = grp('hsts', 'hsts'); cs, cmp_s = grp('spf', 'spf'); dm = C.Counter(('p=' + r['dmarc'] if r['dmarc'] in ('none', 'quarantine', 'reject') else r['dmarc']) for r in rs); anyh = len([r for r in rs if r.get('hsts')]); anys = len([r for r in rs if r.get('spf_cls') in ('AGREE', 'DISAGREE') or r.get('spf_why') == 'count cut short'])
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), gate='passed' if gate else 'FAILED', domains=len(rs), listdate=open('data/listdate.txt').read() if os.path.exists('data/listdate.txt') else '',
           comparison={'HSTS preload header': cmp_h, 'SPF lookup limit': cmp_s}, classes={'HSTS preload header': {c: ch[c] for c in ('AGREE', 'DISAGREE', 'NOT_COMPARABLE')}, 'SPF lookup limit': {c: cs[c] for c in ('AGREE', 'DISAGREE', 'NOT_COMPARABLE')}},
           descriptive={'Domains whose HTTPS response carries an HSTS header': dict(n=anyh, of=len(rs)), 'Domains that publish an SPF record': dict(n=anys, of=len(rs))},
           dmarc={k: dict(n=v) for k, v in sorted(dm.items(), key=lambda x: -x[1])},
           disagree_list=[dict(domain=r['domain'], claim='HSTS preload header', record=r.get('hsts'), reason=hc.get('hsts|' + r['domain'])) for r in rs if r['hsts_cls'] == 'DISAGREE' and 'hsts|' + r['domain'] in hc] + [dict(domain=r['domain'], claim='SPF lookup limit', record='%s lookups: %s' % (r['spf_n'], (r.get('spf') or '')[:120]), reason=hc.get('spf|' + r['domain'])) for r in rs if r['spf_cls'] == 'DISAGREE' and 'spf|' + r['domain'] in hc])
json.dump(out, open('summary_secrecords.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'secrecords_live', '--path', os.path.join(H, 'summary_secrecords.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('secrecords:', len(rs), 'domains;', dict(ch), dict(cs), 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
