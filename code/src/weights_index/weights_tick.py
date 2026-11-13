#!/usr/bin/env python3
"""weights_tick.py: WEIGHTS per PLAN.md. Weight-file hashes of the 1,000 most downloaded Hugging Face models, compared pass to pass."""
import os, sys, re, json, time, fcntl, subprocess, urllib.request, urllib.error
import os as _pg_os, sys as _pg_sys, subprocess as _pg_sp   # 10 Nov 2026 (publish guard): the site KV is written only by a run the tick bus or the house clock started
_PUBLISH = '--publish' in _pg_sys.argv or _pg_os.environ.get('HEUREMEN_PUBLISH') == '1'   # (they export HEUREMEN_PUBLISH=1) or a run given --publish. A copy run for a reproduce kit or a test never publishes
if _PUBLISH: _pg_os.environ['HEUREMEN_PUBLISH'] = '1'   # passed on to the scripts this one starts, and kept across a detach or re-exec
def _kv_put(cmd, **kw):
    if _PUBLISH: return _pg_sp.run(cmd, **kw)
    print('publish guard: %s not put to the site KV (run with --publish, or from the tick bus)' % cmd[5], file=_pg_sys.stderr)
    return _pg_sp.CompletedProcess(cmd, 0, '' if kw.get('text') or kw.get('universal_newlines') else b'', '' if kw.get('text') or kw.get('universal_newlines') else b'')
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
SUMMARY_ONLY = bool(os.environ.get('WEIGHTS_SUMMARY_ONLY'))   # 30 Oct: rebuild and publish the summary from the stored passes without reading Hugging Face
if SUMMARY_ONLY:
    now = time.time(); store = json.load(open('data/repos.json')); hist0 = [json.loads(l) for l in open('history.jsonl')]; passno = hist0[-1]['pass_number']; unread = hist0[-1]['unreadable']
else:
    a1 = read('HuggingFaceTB/SmolLM2-135M'); a2 = read('HuggingFaceTB/SmolLM2-135M'); live_ok = a1[0] == 'OK' and a1 == a2 and len(a1[1]) > 0
    gone_ok = read('nonexistent-org/zzz-none-zzz')[0] == 'GONE'
    gate = bool(gate_pairs and live_ok and gone_ok); print('weights: gate', 'passed' if gate else 'FAILED', gate_pairs, live_ok, gone_ok, flush=True)
    if not gate: sys.exit(1)
    now = time.time(); store = json.load(open('data/repos.json')) if os.path.exists('data/repos.json') else {}
    st, lst = http('https://huggingface.co/api/models?sort=downloads&direction=-1&limit=1000')
    if st != 200 or not lst: print('weights: model list not read'); sys.exit(1)
    ids = [m['id'] for m in lst]; todo = list(dict.fromkeys(ids + [r for r in store if r not in ids])); unread = 0; passno = (max([r.get('passes', 0) for r in store.values()] or [0])) + 1
    sys.path.insert(0, os.path.expanduser('~/bones-forge/watch')); import desk_progress as DP   # 31 Oct: live progress bar on the page
    for i, rid in enumerate(todo):
        DP.report('weights', i, len(todo), rid, 'Pass %d' % passno)
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
    DP.finish('weights', len(todo), 'Pass %d' % passno)
hc = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}
def when(c): return time.strftime('%d %b %H:%M', time.gmtime(c['t']))
# 30 Oct (site pass I-3): the headline below keeps the plan's rule (the latest pair of each model). A model that changed on one pass and was the same on the next leaves it, so every pass-to-pass change is also kept in evs and shown apart, with no outcome.
evs = sorted([(i, c) for i, r in store.items() for c in r['changes'] if c['kind'] == 'CHANGED'], key=lambda x: x[1]['t'], reverse=True)
evkey = lambda i, c: '%s|%s' % (i, when(c))
cmp = [r for r in store.values() if r.get('last_pair') in ('SAME', 'CHANGED')]; ch = [r for r in cmp if r['last_pair'] == 'CHANGED']; gone = [i for i, r in store.items() if r.get('last_pair') == 'GONE']
nc = [i for i, r in store.items() if r.get('files') in ([], None) and r.get('passes')]
# 12 Nov 2026, PLAN_ADDENDUM_std2.md (Faults and Guards 2.0): size that matters 0.01, null 0, band [0, 0.01), edge '[)'. No model pair yet is CANNOT_TELL NO_INTERVAL_FORMABLE. NOTHING_RETURNED is a status of a failed read (the UNREADABLE models) and is never an outcome.
def _wil(k, n):   # exact ends: K.wilson(0, n) gives 6.9e-18 at the lower end, which misses the null at zero in K.read
    _l, _h = K.wilson(k, n); return (0.0 if k == 0 else _l, 1.0 if k == n else _h)
lo, hi = _wil(len(ch), len(cmp)) if cmp else (0, 1)
oc, why = K.read(lo, hi, band=(0.0, 0.01), matters=0.01, edge='[)', null=0.0) if cmp else (K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE)
ever_n = len({i for i, c in evs}); ever_of = len({i for i, r in store.items() if r.get('last_pair') in ('SAME', 'CHANGED')} | {i for i, c in evs}); elo, ehi = K.wilson(ever_n, ever_of) if ever_of else (0, 1)
hist = [json.loads(l) for l in open('history.jsonl')] if os.path.exists('history.jsonl') else []
upd = hist[-1]['t'] if SUMMARY_ONLY else time.strftime('%d %b %H:%M', time.gmtime(now))
this = dict(t=upd, pass_number=passno, compared=len(cmp), changed=len(ch), gone=len(gone), unreadable=unread)
def diff(c):
    b = {a: h for a, h in c['before']}; a_ = {a: h for a, h in c['after']}
    return dict(files_before=len(b), files_after=len(a_), added=len(set(a_) - set(b)), removed=len(set(b) - set(a_)), replaced=len([x for x in set(a_) & set(b) if a_[x] != b[x]]))
out = dict(updated=upd, gate='passed', pass_number=passno, models=len(store), retained=len([i for i, r in store.items() if not r.get('in_top')]), unreadable=unread, not_comparable=len(nc), awaiting=len([1 for i, c in evs if evkey(i, c) not in hc]),
           headline=dict(of=len(cmp), n=len(ch), share=round(len(ch) / len(cmp), 4) if cmp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc, reason=why, req13=K.req13([(oc, why)], nothing_returned=unread), awaiting=len([1 for i, c in evs if evkey(i, c) not in hc])),
           headline_n=len(ch), headline_of=len(cmp), gone=dict(models=len(gone), list=sorted(gone)[:50]),
           ever=dict(of=ever_of, n=ever_n, events=len(evs), share=round(ever_n / ever_of, 4) if ever_of else None, share_lo=round(elo, 4), share_hi=round(ehi, 4)),
           passes=(hist if SUMMARY_ONLY else hist + [this])[::-1],
           changed_list=[dict(repo=i, when=when(c), note=hc[evkey(i, c)], **diff(c)) for i, c in evs if evkey(i, c) in hc])
json.dump(out, open('summary_weights.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = _kv_put(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'weights_live', '--path', os.path.join(H, 'summary_weights.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
if not SUMMARY_ONLY:
    with open('history.jsonl', 'a') as f: f.write(json.dumps(this) + '\n')
print('weights: pass', passno, len(store), 'models; compared', len(cmp), 'changed', len(ch), 'gone', len(gone), 'unreadable', unread, 'published' if pr.returncode == 0 else 'publish FAILED ' + (pr.stderr or pr.stdout)[-200:], flush=True)
