#!/usr/bin/env python3
"""pkglicense_tick.py: PKGLICENSE rider per PLAN.md. Top 1,000 PyPI projects: the license a project states against the license GitHub detects in the repository it points to.
Detaches into the background (about 12 minutes). DISAGREE rows are listed only after they are marked hand-checked in data/hand_checked.json. Publishes KV pkglicense_live."""
import os, sys, re, json, time, collections as C, subprocess, fcntl, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
if not os.environ.get('PKG_FORKED'):
    subprocess.Popen([sys.executable, '-I', os.path.abspath(__file__)], env=dict(os.environ, PKG_FORKED='1'), stdout=open('data/last_run.log', 'w'), stderr=subprocess.STDOUT, start_new_session=True); print('pkglicense: started in the background'); sys.exit(0)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('pkglicense: plan not committed'); sys.exit(0)
_l = open('data/.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('pkglicense: another run holds the lock'); sys.exit(0)
UA = {'User-Agent': 'heuremen-pkglicense/0.1 (+https://indahl.ai/pkglicense)'}; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
def fam(s):
    t = (s or '').lower().strip()
    if not t: return None
    if re.search(r'\bagpl|affero', t): return 'AGPL'
    if re.search(r'\blgpl|lesser general', t): return 'LGPL'
    if re.search(r'\bgpl|general public license', t):
        if re.search(r'(-|v|version\s*|\s)3(\.0)?\b|v3', t): return 'GPL-3.0'
        if re.search(r'(-|v|version\s*|\s)2(\.0)?\b|v2', t): return 'GPL-2.0'
        return 'GPL'
    if re.search(r'\b0?bsd|berkeley', t): return 'BSD'
    if re.search(r'\bapache', t): return 'Apache-2.0'
    if re.search(r'\bmit\b', t): return 'MIT'
    if re.search(r'\bisc\b', t): return 'ISC'
    if re.search(r'\bmpl|mozilla', t): return 'MPL-2.0'
    if re.search(r'\bpsf|python software foundation', t): return 'PSF'
    if re.search(r'unlicense', t): return 'Unlicense'
    if re.search(r'\bcc0|creative commons zero', t): return 'CC0'
    return 'OTHER'
def famset(parts): return {f for f in (fam(p) for p in parts) if f}
def compare(stated, repo):
    S = {f for f in stated if f != 'OTHER'}; R = {f for f in repo if f != 'OTHER'}
    if not S or not R: return 'NOT_COMPARABLE'
    for a in S:
        for b in R:
            if a == b or (a == 'GPL' and b in ('GPL-2.0', 'GPL-3.0')) or (b == 'GPL' and a in ('GPL-2.0', 'GPL-3.0')): return 'AGREE'
    return 'DISAGREE'
# planted pairs
P = [(['MIT'], ['MIT'], 'AGREE'), (['License :: OSI Approved :: Apache Software License'], ['Apache-2.0'], 'AGREE'), (['BSD-3-Clause'], ['BSD-2-Clause'], 'AGREE'), (['License :: OSI Approved :: GNU General Public License v3 (GPLv3)'], ['GPL-3.0'], 'AGREE'),
     (['MIT'], ['Apache-2.0'], 'DISAGREE'), (['Custom proprietary terms'], ['MIT'], 'NOT_COMPARABLE'), (['MIT', 'Apache-2.0'], ['Apache-2.0'], 'AGREE'), (['GPL'], ['GPL-3.0'], 'AGREE'), (['GPL-2.0'], ['GPL-3.0'], 'DISAGREE'), (['LGPL-3.0'], ['GPL-3.0'], 'DISAGREE')]
gate_pairs = all(compare(famset(a), famset(b)) == w for a, b, w in P)
def get(u):
    for a in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40))
        except Exception: time.sleep(2 * (a + 1))
def pypi(name):
    j = get('https://pypi.org/pypi/%s/json' % name)
    if not j: return None
    i = j['info']; parts = []
    if i.get('license_expression'): parts = [x for x in re.split(r'\s+(?:OR|AND|WITH)\s+|[()]', i['license_expression']) if x.strip()]
    elif [c for c in i.get('classifiers', []) if c.startswith('License ::')]: parts = [c for c in i['classifiers'] if c.startswith('License ::')]
    elif i.get('license') and len(i['license']) <= 100: parts = [i['license']]
    urls = i.get('project_urls') or {}; cand = []
    for k in ('Source', 'Repository', 'Code', 'Homepage', 'Source Code', 'GitHub', 'Home'):
        for kk, v in urls.items():
            if kk.lower() == k.lower(): cand.append(v)
    cand.append(i.get('home_page') or '')
    repo = None
    for u in cand:
        m = re.match(r'https?://(?:www\.)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?(?:[/#?].*)?$', u or '')
        if m: repo = (m.group(1), m.group(2)); break
    return dict(stated=parts, repo=repo)
def gh(pairs):
    body = ' '.join('r%d: repository(owner:"%s", name:"%s") { licenseInfo { spdxId name } }' % (i, o, n) for i, (o, n) in enumerate(pairs))
    r = subprocess.run(['gh', 'api', 'graphql', '-f', 'query={ ' + body + ' }'], capture_output=True, text=True)
    try: d = json.loads(r.stdout).get('data') or {}
    except Exception: return None
    return [((d.get('r%d' % i) or {}).get('licenseInfo') or {}).get('spdxId') if d.get('r%d' % i) is not None else 'NOT_FOUND' for i in range(len(pairs))]
top = get('https://hugovk.github.io/top-pypi-packages/top-pypi-packages.json'); listdate = top['last_update']; names = [r['project'] for r in top['rows'][:1000]]
projects = json.load(open('data/projects.json')) if os.path.exists('data/projects.json') else {}
now = time.time(); todo = [n for n in names if n not in projects or now - projects[n]['read'] > 30 * 86400]
# live controls first
live_ok = True
for c in ('requests', 'flask'):
    p = pypi(c); time.sleep(0.5); g = gh([p['repo']]) if p and p['repo'] else None
    live_ok &= bool(p and g and compare(famset(p['stated']), famset([g[0] or ''])) == 'AGREE')
gate = bool(gate_pairs and live_ok); print('pkglicense: gate', 'passed' if gate else 'FAILED', 'pairs', gate_pairs, 'live', live_ok, flush=True)
if gate:
    pend = []
    for n in todo:
        p = pypi(n); time.sleep(0.5)
        if p is None: projects[n] = dict(read=now, cls='NOT_COMPARABLE', why='not found on PyPI', stated=[], repo=None); continue
        projects[n] = dict(read=now, stated=p['stated'], repo=p['repo'], cls=None)
        if p['repo']: pend.append(n)
        else: projects[n]['cls'] = 'NOT_COMPARABLE'; projects[n]['why'] = 'no GitHub repository in the metadata'
    for k in range(0, len(pend), 100):
        chunk = pend[k:k + 100]; res = gh([tuple(projects[n]['repo']) for n in chunk])
        if res is None: continue
        for n, spdx in zip(chunk, res):
            projects[n]['repo_license'] = spdx
            projects[n]['cls'] = 'NOT_COMPARABLE' if spdx in (None, 'NOT_FOUND', 'NOASSERTION') or not projects[n]['stated'] else compare(famset(projects[n]['stated']), famset([spdx]))
            if projects[n]['cls'] == 'NOT_COMPARABLE': projects[n]['why'] = 'repository license not detected' if spdx in (None, 'NOASSERTION') else ('repository not found' if spdx == 'NOT_FOUND' else 'no stated license')
    json.dump(projects, open('data/projects.json.tmp', 'w')); os.replace('data/projects.json.tmp', 'data/projects.json')
rows = {n: projects[n] for n in names if n in projects and projects[n].get('cls')}; cnt = C.Counter(r['cls'] for r in rows.values()); comp = cnt['AGREE'] + cnt['DISAGREE']
lo, hi = K.wilson(cnt['DISAGREE'], comp); oc = K.CANNOT_TELL if (comp < 30 or not gate) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
hc = set(json.load(open('data/hand_checked.json'))['ids']) if os.path.exists('data/hand_checked.json') else set()
dis = [n for n, r in rows.items() if r['cls'] == 'DISAGREE']
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), gate='passed' if gate else 'FAILED', list_date=listdate, projects=len(names), read=len(rows), comparable=comp,
           classes={k: dict(n=v) for k, v in sorted(cnt.items())}, disagree=dict(n=cnt['DISAGREE'], of=comp, share=round(cnt['DISAGREE'] / comp, 4) if comp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc, hand_checked=len([n for n in dis if n in hc]), awaiting=len([n for n in dis if n not in hc])),
           disagree_list=[dict(project=n, stated='; '.join(rows[n]['stated'])[:90], repo='%s/%s' % tuple(rows[n]['repo']), repo_license=rows[n].get('repo_license')) for n in dis if n in hc][:150])
json.dump(out, open('summary_pkglicense.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'pkglicense_live', '--path', os.path.join(H, 'summary_pkglicense.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('pkglicense:', len(rows), 'read,', dict(cnt), 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
