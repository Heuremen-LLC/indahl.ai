#!/usr/bin/env python3
"""arxivdrift_tick.py: ARXIVDRIFT rider per PLAN.md. Reads the QIA and IRIS lists, compares the arXiv version we read with the version that stands now, publishes KV arxivdrift_live.
At most 24 API requests per run, one per 3 seconds. Each study is read again after 7 days. Known-good controls first."""
import os, sys, re, json, time, collections as C, subprocess, fcntl, urllib.request, datetime as D, xml.etree.ElementTree as ET
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('arxivdrift: plan not committed'); sys.exit(0)
_lock = open('data/.lock', 'w')
try: fcntl.flock(_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('arxivdrift: another run holds the lock'); sys.exit(0)
UA = {'User-Agent': 'heuremen-arxivdrift/0.1 (+https://indahl.ai/arxivdrift)'}; NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
NUM = re.compile(r'(?<![\w.])\d+(?:\.\d+)?%?'); BUDGET = [24]
W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
def api(ids):
    if BUDGET[0] <= 0: return None
    BUDGET[0] -= 1
    for a in range(3):
        try:
            t = urllib.request.urlopen(urllib.request.Request('https://export.arxiv.org/api/query?max_results=%d&id_list=%s' % (len(ids), ','.join(ids)), headers=UA), timeout=60).read()
            time.sleep(3); break
        except Exception: time.sleep(5 * (a + 1)); t = None
    if t is None: return None
    out = {}
    for e in ET.fromstring(t).findall('a:entry', NS):
        m = re.match(r'https?://arxiv\.org/abs/(.+?)(v\d+)$', e.findtext('a:id', '', NS))
        if not m or not e.findtext('a:summary', '', NS).strip(): continue
        s = re.sub(r'\s+', ' ', e.findtext('a:summary', '', NS)).strip(); ti = re.sub(r'\s+', ' ', e.findtext('a:title', '', NS)).strip(); cm = e.findtext('x:comment', '', NS) or ''
        out[m.group(1) + m.group(2)] = dict(id=m.group(1), version=m.group(2), title=ti, abstract=s, comment=cm)
    return out
norm = lambda s: re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()
def classify(read, latest, readv):
    if latest is None: return 'NOTHING_RETURNED', {}
    pat = r'^\W*(this\s+(paper|article|submission|preprint)\s+(has\s+been\s+|is\s+)?withdrawn|withdrawn\b)'
    if re.search(pat, latest['abstract'].lower()) or re.search(pat, latest['comment'].lower()): return 'WITHDRAWN', {}
    if int(latest['version'][1:]) <= int(readv[1:]): return 'UNCHANGED', {}
    if read is None: return 'PENDING', {}
    a, b = C.Counter(NUM.findall(read['abstract'])), C.Counter(NUM.findall(latest['abstract']))
    if a != b: return 'REVISED_NUMBERS', dict(only_read=sorted((a - b).elements()), only_latest=sorted((b - a).elements()))
    if norm(read['title']) != norm(latest['title']) or norm(read['abstract']) != norm(latest['abstract']): return 'REVISED_TEXT', {}
    return 'REVISED_SAME', {}
# known-good
def ctl(i, readv):
    lt = api([i]); lat = lt.get(i + sorted(v for v in [k[len(i):] for k in (lt or {})])[-1]) if lt else None
    rd = api([i + readv]) if lat and int(lat['version'][1:]) > int(readv[1:]) else None
    return classify((rd or {}).get(i + readv), lat, readv)[0]
c1 = ctl('1706.03762', 'v1'); c2 = ctl('1512.03385', 'v1'); gate = (c1 == 'REVISED_NUMBERS' and c2 == 'UNCHANGED'); print('arxivdrift: gate', 'passed' if gate else 'FAILED', c1, c2)
# lists
studies = json.load(open('data/studies.json')) if os.path.exists('data/studies.json') else {}
for d in ('qia', 'iris'):
    try: L = json.load(urllib.request.urlopen(urllib.request.Request('https://indahl.ai/%s/list.json' % d, headers=UA), timeout=60))['studies']
    except Exception: continue
    for r in L:
        m = re.search(r'arxiv\.org/abs/(.+?)(v\d+)$', r.get('link', ''))
        if m:
            e = studies.setdefault(m.group(1), dict(read_version=m.group(2), title=r['study'], division=d, indexed=r.get('indexed'), hist=[]))
            e['read_version'] = m.group(2)
now = time.time(); due = [i for i, e in studies.items() if not e['hist'] or now - e['hist'][-1][0] > 7 * 86400]
latest_cache = {}
if gate:
    for k in range(0, len(due), 50):
        batch = due[k:k + 50]; got = api(batch)
        if got is None: break
        best = {}
        for key, e in got.items():
            if e['id'] not in best or int(e['version'][1:]) > int(best[e['id']]['version'][1:]): best[e['id']] = e
        for i in batch: latest_cache[i] = best.get(i)
    need = [i for i in latest_cache if latest_cache[i] and int(latest_cache[i]['version'][1:]) > int(studies[i]['read_version'][1:]) and not studies[i].get('read_abs') and classify(None, latest_cache[i], studies[i]['read_version'])[0] != 'WITHDRAWN']
    for k in range(0, len(need), 10):
        batch = need[k:k + 10]; got = api([i + studies[i]['read_version'] for i in batch])
        if got is None: break
        for i in batch:
            r = got.get(i + studies[i]['read_version'])
            if r: studies[i]['read_abs'] = dict(title=r['title'], abstract=r['abstract'])
    for i, lat in latest_cache.items():
        e = studies[i]; cls, det = classify(e.get('read_abs') and dict(title=e['read_abs']['title'], abstract=e['read_abs']['abstract']), lat, e['read_version'])
        e.update(latest_version=lat['version'] if lat else None, **det); e['hist'].append([now, cls])
    json.dump(studies, open('data/studies.json.tmp', 'w')); os.replace('data/studies.json.tmp', 'data/studies.json')
cur = {i: e['hist'][-1][1] for i, e in studies.items() if e['hist']}
cls_n = C.Counter(cur.values()); read = sum(v for k, v in cls_n.items() if k not in ('PENDING', 'NOTHING_RETURNED')); change = cls_n['REVISED_NUMBERS'] + cls_n['REVISED_TEXT'] + cls_n['WITHDRAWN']
lo, hi = K.wilson(change, read)
classes = {k: dict(n=v, share=round(v / read, 4) if read else None, share_lo=round(K.wilson(v, read)[0], 4), share_hi=round(K.wilson(v, read)[1], 4)) for k, v in sorted(cls_n.items())}
bym = C.defaultdict(C.Counter)
for i, c in cur.items(): bym[(studies[i].get('indexed') or '')[:7]][c] += 1
by_month = {m: dict(n=sum(v.values()), unchanged=v['UNCHANGED'], revised_same=v['REVISED_SAME'], revised_text=v['REVISED_TEXT'], revised_numbers=v['REVISED_NUMBERS'], withdrawn=v['WITHDRAWN']) for m, v in sorted(bym.items()) if m}
drifted = [dict(title=studies[i]['title'][:110], id=i, read=studies[i]['read_version'], latest=studies[i].get('latest_version'), cls=c, numbers_read=', '.join(studies[i].get('only_read', [])[:8]), numbers_latest=', '.join(studies[i].get('only_latest', [])[:8]), division=studies[i]['division'].upper())
           for i, c in cur.items() if c in ('REVISED_NUMBERS', 'WITHDRAWN')][:200]
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), gate='passed' if gate else 'FAILED', studies=len(studies), read=read, due=len([i for i, e in studies.items() if not e['hist'] or now - e['hist'][-1][0] > 7 * 86400]),
           any_change=dict(n=change, of=read, share=round(change / read, 4) if read else None, share_lo=round(lo, 4), share_hi=round(hi, 4)), classes=classes, by_month=by_month, drifted=drifted)
json.dump(out, open('summary_arxivdrift.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'arxivdrift_live', '--path', os.path.join(H, 'summary_arxivdrift.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('arxivdrift:', len(studies), 'studies,', read, 'read,', dict(cls_n), 'published' if p.returncode == 0 else 'publish FAILED')
