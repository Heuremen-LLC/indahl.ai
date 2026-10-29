#!/usr/bin/env python3
"""pkginstall_tick.py: PKGINSTALL rider per PLAN.md. Top 1,000 PyPI projects: the first pip install command in the description against pip's dry-run resolution
(wheels only, no package code runs). Runs under the venv's Python 3.12 and detaches. DISAGREE rows are listed only after they are in data/hand_checked.json.
Publishes KV pkginstall_live. PKGINSTALL_SUMMARY_ONLY=1 rebuilds the summary from stored data."""
import os, sys, re, json, time, shlex, collections as C, subprocess, fcntl, urllib.request, urllib.error
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
VPY = os.path.join(H, 'venv', 'bin', 'python')
if not os.environ.get('PI_FORKED') and not os.environ.get('PKGINSTALL_SUMMARY_ONLY'):
    subprocess.Popen([VPY, os.path.abspath(__file__)], env=dict(os.environ, PI_FORKED='1'), stdout=open('data/last_run.log', 'w'), stderr=subprocess.STDOUT, start_new_session=True); print('pkginstall: started in the background'); sys.exit(0)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('pkginstall: plan not committed'); sys.exit(0)
_l = open('data/.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('pkginstall: another run holds the lock'); sys.exit(0)
UA = {'User-Agent': 'heuremen-pkginstall/0.1 (+https://indahl.ai/pkginstall)'}; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); SUMMARY_ONLY = bool(os.environ.get('PKGINSTALL_SUMMARY_ONLY'))
LINE = re.compile(r'^\s*(?:[$>]\s*)?(?:(?:python3?|py)\s+-m\s+)?pip3?\s+install\s+(.+?)\s*$', re.I)
OKFLAG = {'-U', '--upgrade', '-q', '--quiet', '--user'}
def parse(text):
    """-> (targets or None, why or None)"""
    for ln in (text or '').splitlines():
        m = LINE.match(ln)
        if not m: continue
        rest = re.sub(r'\s+#.*$', '', m.group(1)).rstrip('\\ ').strip()
        if re.search(r'[<>]{1}[A-Za-z_ .-]+>|\.\.\.|\{|\}|\$\(', rest) and not re.search(r'[<>]=?\s*\d', rest.split('"')[0]): return None, 'placeholder in the command'
        try: toks = shlex.split(rest)
        except ValueError: return None, 'command could not be read'
        tg = []
        for t in toks:
            if t.startswith('-'):
                if t in OKFLAG: continue
                return None, 'command has other options'
            if '://' in t or t.startswith(('git+', '.', '/', '~')) or t.endswith(('.whl', '.tar.gz', '.zip', '.txt')) or '@' in t.split('[')[0] and 'git' in t: return None, 'target is a URL, file or path'
            tg.append(t)
        if any(re.search(r'XX|YOUR[_-]\w|<[^>]+>', t) for t in tg): return None, 'placeholder in the command'
        if not tg: return None, 'command has no target'
        return tg, None
    return None, 'no pip install line in the description'
def get(u, n=3):
    for i in range(n):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read())
        except urllib.error.HTTPError as e:
            if e.code == 404: return 404
            time.sleep(2 * (i + 1))
        except Exception: time.sleep(2 * (i + 1))
def dry(tg):
    p = subprocess.run([VPY, '-m', 'pip', 'install', '--dry-run', '--only-binary=:all:', '--no-cache-dir', '--no-input', '--disable-pip-version-check'] + tg, capture_output=True, text=True, timeout=300)
    return p.returncode, (p.stdout + p.stderr)
def err_line(o):
    ls = [l for l in o.splitlines() if l.startswith('ERROR') or 'ResolutionImpossible' in l or 'conflict' in l.lower()]
    return (ls[-1] if ls else o.strip().splitlines()[-1] if o.strip() else '')[:220]
def fits(name):
    """True when the project has a wheel for this Python and platform, from pip's own tag logic"""
    d = get('https://pypi.org/pypi/%s/json' % name)
    if d == 404 or not d: return None
    from pip._internal.models.wheel import Wheel
    from pip._internal.utils.compatibility_tags import get_supported
    sup = get_supported()
    for u in d.get('urls', []):
        if u.get('packagetype') == 'bdist_wheel':
            try:
                if Wheel(u['filename']).supported(sup): return True
            except Exception: pass
    return False
def names_project(project, tg):
    norm = lambda x: re.sub(r'[-_.]+', '-', x).lower()
    for t in tg:
        m = re.match(r'^([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[([^\]]*)\])?', t)
        if not m: continue
        base = norm(m.group(1))
        if base == norm(project): return True
        for ex in (m.group(2) or '').split(','):
            if ex.strip() and norm(project) == base + '-' + norm(ex.strip()): return True
    return False
def classify(tg):
    rc, o = dry(tg)
    if rc == 0: return 'AGREE', None
    e = err_line(o); names = [re.split(r'[\[=<>!~ ;]', t, 1)[0] for t in tg]
    for n in names:
        f = fits(n)
        if f is None: return 'DISAGREE', 'not on PyPI: ' + e
    if 'ResolutionImpossible' in o or 'conflict' in o.lower(): return 'DISAGREE', 'conflict: ' + e
    if 'No matching distribution' in o or 'Could not find a version' in o:
        if all(fits(n) for n in names): return 'DISAGREE', 'no matching version: ' + e
        return 'NOT_COMPARABLE', 'no wheel that fits this Python and platform'
    return 'DISAGREE', 'other: ' + e
# gate
PARSE = [('$ pip install foo', ['foo']), ('python -m pip install -U foo[extra]==1.2', ['foo[extra]==1.2']), ('pip3 install a b', ['a', 'b']), ('> pip install "foo>=1.0"', ['foo>=1.0'])]
NOPE = ['pip install nvidia-foo-cuXX', 'pip install YOUR_PACKAGE', 'pip install git+https://x/y', 'pip install -e .', 'pip install <name>', 'pip install -r r.txt', 'pip install foo --pre', 'pip install ./local', 'pip install https://x/y.whl', 'nothing here']
gate_names = names_project('psycopg-binary', ['psycopg[binary]']) and names_project('Foo_Bar', ['foo-bar>=1']) and not names_project('cffi', ['pytest']) and not names_project('thinc', ['pip', 'setuptools', 'wheel'])
gate_parse = gate_names and all(parse(t)[0] == w for t, w in PARSE) and all(parse(t)[0] is None for t in NOPE)
gate_run = classify(['requests'])[0] == 'AGREE' and classify(['requests==0.0.0001'])[0] == 'DISAGREE' and classify(['this-package-does-not-exist-heuremen-xyz'])[0] == 'DISAGREE'
gate = bool(gate_parse and gate_run) if not SUMMARY_ONLY else bool(gate_parse and json.load(open('summary_pkginstall.json')).get('gate') == 'passed'); print('pkginstall: gate', 'passed' if gate else 'FAILED', gate_parse, gate_run, flush=True)
store = json.load(open('data/projects.json')) if os.path.exists('data/projects.json') else {}
now = time.time()
if gate and not SUMMARY_ONLY:
    top = get('https://hugovk.github.io/top-pypi-packages/top-pypi-packages.json'); names = [r['project'] for r in top['rows'][:1000]]; listdate = top['last_update']; store = {}
    for i, n in enumerate(names):
        d = get('https://pypi.org/pypi/%s/json' % n); time.sleep(0.25)
        rec = dict(read=now, project=n, rank=i + 1)
        if d in (None, 404): rec.update(cls='NOT_COMPARABLE', why='description not readable')
        else:
            tg, why = parse((d.get('info') or {}).get('description') or '')
            if tg is not None and not names_project(n, tg): tg, why = None, 'command does not name this project'
            if tg is None: rec.update(cls='NOT_COMPARABLE', why=why)
            else:
                try: c, w = classify(tg)
                except subprocess.TimeoutExpired: c, w = 'NOT_COMPARABLE', 'pip timed out'
                rec.update(cls=c, targets=tg, detail=w, why=w if c == 'NOT_COMPARABLE' else None)
        store[n] = rec
        if i % 50 == 49: json.dump(store, open('data/projects.json.tmp', 'w')); os.replace('data/projects.json.tmp', 'data/projects.json'); print('pkginstall: read', i + 1, flush=True)
    json.dump(store, open('data/projects.json.tmp', 'w')); os.replace('data/projects.json.tmp', 'data/projects.json'); open('data/listdate.txt', 'w').write(listdate)
hc = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}
rs = list(store.values()); cnt = C.Counter(r['cls'] for r in rs); comp = cnt['AGREE'] + cnt['DISAGREE']; lo, hi = K.wilson(cnt['DISAGREE'], comp)
oc = K.CANNOT_TELL if (comp < 30 or not gate) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
dis = [r for r in rs if r['cls'] == 'DISAGREE']; why = C.Counter(r['why'] for r in rs if r['cls'] == 'NOT_COMPARABLE')
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), gate='passed' if gate else 'FAILED', projects=len(rs), pip=subprocess.run([VPY, '-m', 'pip', '--version'], capture_output=True, text=True).stdout.split()[1],
           comparison=dict(of=comp, n=cnt['DISAGREE'], share=round(cnt['DISAGREE'] / comp, 4) if comp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc, awaiting=len([r for r in dis if r['project'] not in hc])),
           classes={c: dict(n=cnt[c]) for c in ('AGREE', 'DISAGREE', 'NOT_COMPARABLE')}, not_comparable_reasons={w: dict(n=n) for w, n in sorted(why.items(), key=lambda x: -x[1])},
           disagree_list=[dict(project=r['project'], command='pip install ' + ' '.join(r['targets']), error=r['detail'], reason=hc[r['project']]) for r in dis if r['project'] in hc])
json.dump(out, open('summary_pkginstall.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'pkginstall_live', '--path', os.path.join(H, 'summary_pkginstall.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('pkginstall:', len(rs), 'projects;', dict(cnt), 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
