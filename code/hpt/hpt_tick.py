#!/usr/bin/env python3
"""hpt_tick.py: HPT rider per PLAN.md. US hospital websites from Wikidata: cms-hpt.txt at the root, the file it links, and the template header.
Detaches into the background. DISAGREE rows of steps 2 and 3 and the ten step 1 sample rows are listed only after they are in data/hand_checked.json (key step|domain).
Publishes KV hpt_live. HPT_SUMMARY_ONLY=1 rebuilds the summary from stored data."""
import os, sys, re, json, time, random, collections as C, subprocess, fcntl, urllib.request, urllib.error, urllib.parse
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
if not os.environ.get('HPT_FORKED') and not os.environ.get('HPT_SUMMARY_ONLY'):
    subprocess.Popen([sys.executable, '-I', os.path.abspath(__file__)], env=dict(os.environ, HPT_FORKED='1'), stdout=open('data/last_run.log', 'w'), stderr=subprocess.STDOUT, start_new_session=True); print('hpt: started in the background'); sys.exit(0)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('hpt: plan not committed'); sys.exit(0)
_l = open('data/.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('hpt: another run holds the lock'); sys.exit(0)
UA = 'heuremen-hpt/0.1 (+https://indahl.ai/hpt)'; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); SUMMARY_ONLY = bool(os.environ.get('HPT_SUMMARY_ONLY'))
SPARQL = 'SELECT DISTINCT ?h ?site WHERE { ?h wdt:P31/wdt:P279* wd:Q16917 ; wdt:P17 wd:Q30 ; wdt:P856 ?site . FILTER NOT EXISTS { ?h wdt:P576 ?d } FILTER NOT EXISTS { ?h wdt:P582 ?e } }'
def http(url, rng=None, n=2):
    """-> (status or None, content_type, body bytes, final_url). status None = no connection"""
    for i in range(n):
        try:
            h = {'User-Agent': UA}
            if rng: h['Range'] = rng
            r = urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30); return r.status, r.headers.get('Content-Type', ''), r.read(rng and 4096 or 20000), r.geturl()
        except urllib.error.HTTPError as e: return e.code, e.headers.get('Content-Type', '') if e.headers else '', b'', url
        except Exception: time.sleep(1)
    return None, '', b'', url
def step1(host):
    for h in (host, 'www.' + host):
        st, ct, body, fin = http('https://%s/cms-hpt.txt' % h)
        if st is None: continue
        if st in (404, 410): return 'DISAGREE', 'no file at the root (HTTP %d)' % st, None
        if st == 200:
            t = body.decode('utf8', 'replace'); m = re.search(r'^\s*mrf-url\s*:\s*(\S+)', t, re.I | re.M)
            return ('AGREE', None, m.group(1)) if m else ('DISAGREE', 'a file is served with no mrf-url line', None)
        return 'NOT_COMPARABLE', 'blocked or server error (HTTP %d)' % st, None
    return 'NOT_COMPARABLE', 'site could not be reached', None
import zlib
def unpack(body):
    """Addendum 1: a gzip prefix is decoded before looking at it."""
    if body[:2] == b'\x1f\x8b':
        try: return zlib.decompressobj(31).decompress(body)[:4096]
        except Exception: return body
    return body
def looks_html(body):
    t = unpack(body).lstrip(b'\xef\xbb\xbf \r\n\t')[:300].lower(); return t.startswith(b'<') or b'<html' in t or b'<!doctype' in t
def step2(url):
    st, ct, body, fin = http(url, 'bytes=0-4095'); path = urllib.parse.urlparse(fin).path.lower()
    if st in (200, 206):
        if looks_html(body): return 'DISAGREE', 'a web page came back, not a data file (%s)' % (ct.split(';')[0] or 'no type'), body, False
        return 'AGREE', None, body, path.endswith('.zip') or 'zip' in ct.lower() or body[:4] == b'PK\x03\x04'
    if st in (404, 410): return 'DISAGREE', 'the linked file is gone (HTTP %d)' % st, body, False
    return 'NOT_COMPARABLE', 'blocked, error or no connection (%s)' % st, body, False
def step3(body):
    body = unpack(body)
    if body[:4] == b'PK\x03\x04': return 'NOT_COMPARABLE'
    if body.lstrip(b'\xef\xbb\xbf \r\n\t')[:1] in (b'{', b'['): return 'NOT_COMPARABLE'
    t = body.decode('utf8', 'replace').lower(); return 'AGREE' if all(k in t for k in ('hospital_name', 'last_updated_on', 'version')) else 'DISAGREE'
# gate
gate = step3(b'hospital_name,last_updated_on,version,x') == 'AGREE' and step3(b'name,date,x') == 'DISAGREE' and step3(b'{"hospital_name":"a","last_updated_on":"b","version":"c"}') == 'NOT_COMPARABLE' and step3(b'PK\x03\x04abc') == 'NOT_COMPARABLE' and looks_html(b'<!doctype html><html>') and not looks_html(b'\xef\xbb\xbfhospital_name,x') and looks_html(zlib.compress(b'<html>', 9, ) if False else __import__('gzip').compress(b'<html>x')) and not looks_html(__import__('gzip').compress(b'hospital_name,x'))
gate &= bool(re.search(r'^\s*mrf-url\s*:\s*(\S+)', 'location-name: A\nmrf-url: https://x/y.json', re.I | re.M)) and not re.search(r'^\s*mrf-url\s*:\s*(\S+)', 'location-name: A', re.I | re.M)
if not SUMMARY_ONLY: gate &= step1('indahl.ai')[0] == 'DISAGREE'
print('hpt: gate', 'passed' if gate else 'FAILED', flush=True)
store = json.load(open('data/domains.json')) if os.path.exists('data/domains.json') else {}; now = time.time()
if gate and os.environ.get('HPT_REREAD23'):
    # Addendum 1: steps 2 and 3 read again for every domain whose step 1 AGREE; step 1 results are kept
    n23 = 0
    for host, rec in store.items():
        if rec.get('s1') != 'AGREE': continue
        for k in ('s2', 'why2', 's3', 'why3'): rec.pop(k, None)
        c2, why2, body, isz = step2(rec['mrf']); time.sleep(0.4); rec.update(s2=c2, why2=why2)
        if c2 == 'AGREE':
            c3 = step3(body); rec['s3'] = c3; rec['why3'] = 'zip file' if (isz or body[:4] == b'PK\x03\x04') else ('JSON: the names can sit after the data' if c3 == 'NOT_COMPARABLE' else None)
        n23 += 1
        if n23 % 100 == 0: print('hpt: reread steps 2 and 3,', n23, flush=True)
    json.dump(store, open('data/domains.json.tmp', 'w')); os.replace('data/domains.json.tmp', 'data/domains.json'); SUMMARY_ONLY = True
if gate and not SUMMARY_ONLY:
    q = urllib.request.Request('https://query.wikidata.org/sparql?' + urllib.parse.urlencode({'query': SPARQL}), headers={'Accept': 'application/sparql-results+json', 'User-Agent': UA})
    rows = json.loads(urllib.request.urlopen(q, timeout=180).read())['results']['bindings']; open('data/listdate.txt', 'w').write(time.strftime('%Y-%m-%d', time.gmtime(now)))
    doms = C.defaultdict(set); shared = set()
    for r in rows:
        u = urllib.parse.urlparse(r['site']['value'].strip()); host = (u.hostname or '').lower().removeprefix('www.')
        if not host: continue
        if u.path.strip('/'): shared.add(host)
        else: doms[host].add(r['h']['value'].rsplit('/', 1)[1])
    for h in shared - set(doms): doms[h] = set()
    store = {}
    for i, (host, hs) in enumerate(sorted(doms.items())):
        rec = dict(read=now, domain=host, hospitals=len(hs))
        if not hs and host in shared: rec.update(s1='NOT_COMPARABLE', why1='website is a page on a shared site')
        else:
            c, why, mrf = step1(host); time.sleep(0.4); rec.update(s1=c, why1=why, mrf=mrf)
            if c == 'AGREE':
                c2, why2, body, isz = step2(mrf); time.sleep(0.4); rec.update(s2=c2, why2=why2)
                if c2 == 'AGREE': rec['s3'] = 'NOT_COMPARABLE' if isz else step3(body); rec['why3'] = 'zip file' if isz else None
        store[host] = rec
        if i % 100 == 99: json.dump(store, open('data/domains.json.tmp', 'w')); os.replace('data/domains.json.tmp', 'data/domains.json'); print('hpt: read', i + 1, 'of', len(doms), flush=True)
    json.dump(store, open('data/domains.json.tmp', 'w')); os.replace('data/domains.json.tmp', 'data/domains.json')
hc = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}
rs = list(store.values()); random.Random(7).shuffle(rs := sorted(rs, key=lambda r: r['domain'])); sample1 = {r['domain'] for r in [r for r in rs if r['s1'] == 'DISAGREE'][:10]}
def grp(key):
    cnt = C.Counter(r.get(key, 'NOT_RUN') for r in store.values()); comp = cnt['AGREE'] + cnt['DISAGREE']; lo, hi = K.wilson(cnt['DISAGREE'], comp)
    oc = K.CANNOT_TELL if (comp < 30 or not gate or key == 's1') else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))   # addendum 1: step 1 stays CANNOT_TELL, the hand check found non-subjects in the population
    return cnt, dict(of=comp, n=cnt['DISAGREE'], share=round(cnt['DISAGREE'] / comp, 4) if comp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc)
c1, g1 = grp('s1'); c2, g2 = grp('s2'); c3, g3 = grp('s3')
why = C.Counter(r.get('why1') for r in store.values() if r['s1'] == 'NOT_COMPARABLE')
shown = [dict(domain=r['domain'], step='1 no file at the root' if k == 's1' else ('2 link' if k == 's2' else '3 template header'), found=r.get('why1') if k == 's1' else (r.get('why2') or 'header names missing'), reason=hc.get(k[1] + '|' + r['domain'])) for k in ('s1', 's2', 's3') for r in store.values() if r.get(k) == 'DISAGREE' and (k[1] + '|' + r['domain']) in hc]
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), gate='passed' if gate else 'FAILED', domains=len(store), hospitals=sum(r['hospitals'] for r in store.values()), listdate=open('data/listdate.txt').read() if os.path.exists('data/listdate.txt') else '',
           comparison={'1 A cms-hpt.txt at the root of the domain': g1, '2 The file it links resolves to data': g2, '3 The file starts with the template header': g3},
           classes={'1 A cms-hpt.txt at the root of the domain': {c: c1[c] for c in ('AGREE', 'DISAGREE', 'NOT_COMPARABLE')}, '2 The file it links resolves to data': {c: c2[c] for c in ('AGREE', 'DISAGREE', 'NOT_COMPARABLE')}, '3 The file starts with the template header': {c: c3[c] for c in ('AGREE', 'DISAGREE', 'NOT_COMPARABLE')}},
           not_comparable_reasons={w: dict(n=n) for w, n in sorted(why.items(), key=lambda x: -x[1]) if w}, disagree_list=shown, awaiting=len([1 for k in ('s2', 's3') for r in store.values() if r.get(k) == 'DISAGREE' and (k[1] + '|' + r['domain']) not in hc]))
json.dump(out, open('summary_hpt.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'hpt_live', '--path', os.path.join(H, 'summary_hpt.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('hpt:', len(store), 'domains;', dict(c1), dict(c2), dict(c3), 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
