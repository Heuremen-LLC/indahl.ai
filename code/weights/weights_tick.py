#!/usr/bin/env python3
"""weights_tick.py: WEIGHTS per PLAN.md. Weight-file hashes of the 1,000 most downloaded Hugging Face models, compared pass to pass."""
import os, sys, re, json, time, fcntl, subprocess, urllib.request, urllib.error
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('weights: plan not committed'); sys.exit(0)
_l = open('data/.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('weights: another run holds the lock'); sys.exit(0)
UA = {'User-Agent': 'heuremen-weights/0.1 (+https://indahl.ai/weights)'}; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
WEIGHT = re.compile(r'(\.safetensors|\.gguf|\.pt|\.pth|\.onnx)$|^pytorch_model.*\.bin$')
def http(u, n=3):
    """-> (status, json or None). status 0 = network failure."""
    for i in range(n):
        try: return 200, json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read())
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 404): return e.code, None
            time.sleep(2 * (i + 1))
        except Exception: time.sleep(2 * (i + 1))
    return 0, None
def weights_of(tree):
    return sorted([x['path'], (x.get('lfs') or {}).get('oid') or x.get('oid')] for x in tree if x.get('type') == 'file' and WEIGHT.search(x['path']))
def pair(prev, cur):
    """prev, cur: list of [file, hash] or the strings 'GONE'. -> SAME / CHANGED / GONE / NOT_COMPARABLE"""
    if cur == 'GONE': return 'GONE'
    if not prev or not cur: return 'NOT_COMPARABLE'
    return 'SAME' if prev == cur else 'CHANGED'
def read(rid):
    st, tree = http('https://huggingface.co/api/models/%s/tree/main' % rid)
    if st == 200: return 'OK', weights_of(tree)
    if st == 0: return 'UNREADABLE', None
    ist, info = http('https://huggingface.co/api/models/%s' % rid)
    if ist in (401, 404): return 'GONE', 'GONE'
    return 'UNREADABLE', None
A = [['a.safetensors', 'h1'], ['b.safetensors', 'h2']]
cases = [(A, A, 'SAME'), (A, [['a.safetensors', 'h1'], ['b.safetensors', 'h9']], 'CHANGED'), (A, A + [['c.gguf', 'h3']], 'CHANGED'), (A, A[:1], 'CHANGED'),
         (A, [['x.safetensors', 'h1'], ['b.safetensors', 'h2']], 'CHANGED'), ([], A, 'NOT_COMPARABLE'), (A, 'GONE', 'GONE')]
gate_pairs = all(pair(p, c) == w for p, c, w in cases)
a1 = read('HuggingFaceTB/SmolLM2-135M'); a2 = read('HuggingFaceTB/SmolLM2-135M'); live_ok = a1[0] == 'OK' and a1 == a2 and len(a1[1]) > 0
gone_ok = read('nonexistent-org/zzz-none-zzz')[0] == 'GONE'
gate = bool(gate_pairs and live_ok and gone_ok); print('weights: gate', 'passed' if gate else 'FAILED', gate_pairs, live_ok, gone_ok, flush=True)
if not gate: sys.exit(1)
now = time.time(); store = json.load(open('data/repos.json')) if os.path.exists('data/repos.json') else {}
st, lst = http('https://huggingface.co/api/models?sort=downloads&direction=-1&limit=1000')
if st != 200 or not lst: print('weights: model list not read'); sys.exit(1)
ids = [m['id'] for m in lst]; todo = list(dict.fromkeys(ids + [r for r in store if r not in ids])); unread = 0; passno = (max([r.get('passes', 0) for r in store.values()] or [0])) + 1
for i, rid in enumerate(todo):
    k, cur = read(rid); time.sleep(0.25)
    rec = store.setdefault(rid, dict(first=now, files=None, passes=0, last_pair=None, changes=[], in_top=False))
    rec['in_top'] = rid in ids
    if k == 'UNREADABLE': unread += 1; rec['unreadable'] = rec.get('unreadable', 0) + 1; continue
    prev = rec['files']
    if prev is not None and prev != 'GONE':
        rec['last_pair'] = pair(prev, cur)
        if rec['last_pair'] in ('CHANGED', 'GONE'): rec['changes'].append(dict(t=now, kind=rec['last_pair'], before=prev, after=cur))
    elif prev is None: rec['last_pair'] = None
    rec['files'] = cur; rec['passes'] = passno; rec['last_read'] = now
    if (i + 1) % 100 == 0: print('weights: read', i + 1, 'of', len(todo), flush=True); json.dump(store, open('data/repos.json.tmp', 'w')); os.replace('data/repos.json.tmp', 'data/repos.json')
json.dump(store, open('data/repos.json.tmp', 'w')); os.replace('data/repos.json.tmp', 'data/repos.json')
hc = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}
cmp = [r for r in store.values() if r.get('last_pair') in ('SAME', 'CHANGED')]; ch = [r for r in cmp if r['last_pair'] == 'CHANGED']; gone = [i for i, r in store.items() if r.get('last_pair') == 'GONE']
nc = [i for i, r in store.items() if r.get('files') in ([], None) and r.get('passes')]
lo, hi = K.wilson(len(ch), len(cmp)) if cmp else (0, 1)
oc = 'NOTHING_RETURNED' if not cmp else (K.ABOVE if lo > 0.01 else (K.CONSISTENT if hi < 0.01 else K.CANNOT_TELL))
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), gate='passed', pass_number=passno, models=len(store), unreadable=unread, not_comparable=len(nc),
           headline=dict(of=len(cmp), n=len(ch), share=round(len(ch) / len(cmp), 4) if cmp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc, awaiting=len([i for i, r in store.items() if r.get('last_pair') == 'CHANGED' and i not in hc])),
           headline_n=len(ch), headline_of=len(cmp), gone=dict(models=len(gone), list=sorted(gone)[:50]),
           changed_list=[dict(repo=i, note=hc[i]) for i, r in store.items() if r.get('last_pair') == 'CHANGED' and i in hc])
json.dump(out, open('summary_weights.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'weights_live', '--path', os.path.join(H, 'summary_weights.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
with open('history.jsonl', 'a') as f: f.write(json.dumps(dict(t=out['updated'], pass_number=passno, compared=len(cmp), changed=len(ch), gone=len(gone), unreadable=unread)) + '\n')
print('weights: pass', passno, len(store), 'models; compared', len(cmp), 'changed', len(ch), 'gone', len(gone), 'unreadable', unread, 'published' if pr.returncode == 0 else 'publish FAILED ' + (pr.stderr or pr.stdout)[-200:], flush=True)
