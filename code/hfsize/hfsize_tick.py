#!/usr/bin/env python3
"""hfsize_tick.py: HFSIZE rider per PLAN.md. Top 1,000 Hugging Face models by downloads: the size the name states against the safetensors total.
DISAGREE rows are listed only after they are in data/hand_checked.json (id -> reason). Publishes KV hfsize_live."""
import os, sys, re, json, time, collections as C, subprocess, fcntl, urllib.request, urllib.error
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('hfsize: plan not committed'); sys.exit(0)
_l = open('data/.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('hfsize: another run holds the lock'); sys.exit(0)
UA = {'User-Agent': 'heuremen-hfsize/0.1 (+https://indahl.ai/hfsize)'}; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
PACKED = re.compile(r'awq|gptq|gguf|bnb|[1-8]bit|int4|int8|fp8|fp4|nvfp4|mxfp4|w4a16|w8a8|quantized', re.I)
TOK = re.compile(r'(?<![A-Za-z0-9.])(\d+(?:\.\d+)?)([BMKbmk])(?![A-Za-z])')
def stated(name):
    """-> (size or None, reason or None)"""
    if re.search(r'\d+x\d+(?:\.\d+)?[Bb]', name) or re.search(r'(?<![A-Za-z0-9])A\d+(?:\.\d+)?B', name): return None, 'mixture-of-experts name'
    toks = {float(n) * {'b': 1e9, 'm': 1e6, 'k': 1e3}[u.lower()] for n, u in TOK.findall(name)}
    if not toks: return None, 'no size in the name'
    if len(toks) > 1: return None, 'more than one size in the name'
    return toks.pop(), None
def compare(s, a):
    if s is None or a is None: return 'NOT_COMPARABLE'
    return 'AGREE' if 0.70 <= a / s <= 1.35 else 'DISAGREE'
def get(u, n=3):
    for i in range(n):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read())
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 404): return None
            time.sleep(2 * (i + 1))
        except Exception: time.sleep(2 * (i + 1))
PAIRS = [(7e9, 7.24e9, 'AGREE'), (7e9, 7e10, 'DISAGREE'), (7e9, 7e8, 'DISAGREE'), (135e6, 1.345e8, 'AGREE'), (7e9, 4.9e9, 'AGREE'), (7e9, 9.45e9, 'AGREE'), (7e9, 9.5e9, 'DISAGREE'), (None, 5e9, 'NOT_COMPARABLE'), (7e9, None, 'NOT_COMPARABLE')]
NAMES = [('Qwen2.5-7B-Instruct', 7e9), ('all-MiniLM-L6-v2', None), ('bge-m3', None), ('SmolLM2-135M', 1.35e8), ('gpt2-medium', None), ('Mixtral-8x7B-v0.1', None), ('Qwen3-30B-A3B', None), ('distil-7B-to-1B', None), ('Llama-3.2-1B', 1e9), ('t5-3b', 3e9), ('Mistral-7B-v0.1', 7e9)]
gate_pairs = all(compare(s, a) == w for s, a, w in PAIRS) and all(stated(n)[0] == w for n, w in NAMES)
live_ok = True
for rid in ('Qwen/Qwen2.5-7B-Instruct', 'HuggingFaceTB/SmolLM2-135M'):
    m = get('https://huggingface.co/api/models/' + rid); tot = ((m or {}).get('safetensors') or {}).get('total'); live_ok &= compare(stated(rid.split('/')[-1])[0], tot) == 'AGREE'
gate = bool(gate_pairs and live_ok); print('hfsize: gate', 'passed' if gate else 'FAILED', gate_pairs, live_ok)
now = time.time(); store = json.load(open('data/repos.json')) if os.path.exists('data/repos.json') else {}
if gate:
    lst = get('https://huggingface.co/api/models?sort=downloads&direction=-1&limit=1000&expand[]=safetensors&expand[]=tags') or []
    store = {}
    for i, m in enumerate(lst):
        rid = m['id']; name = rid.split('/')[-1]; tags = ' '.join(m.get('tags') or []); st = m.get('safetensors') or {}; tot = st.get('total'); psum = sum((st.get('parameters') or {}).values()) or None
        rec = dict(read=now, id=rid, rank=i + 1, total=tot, psum=psum)
        if PACKED.search(name + ' ' + tags): rec.update(cls='NOT_COMPARABLE', why='packed or quantized')
        else:
            s, why = stated(name); rec['stated'] = s
            if s is None: rec.update(cls='NOT_COMPARABLE', why=why)
            elif not tot: rec.update(cls='NOT_COMPARABLE', why='no safetensors total')
            elif psum and tot != psum: rec.update(cls='NOT_COMPARABLE', why='Hugging Face total does not match its own breakdown')
            else: rec.update(cls=compare(s, tot), ratio=round(tot / s, 3))
        store[rid] = rec
    json.dump(store, open('data/repos.json.tmp', 'w')); os.replace('data/repos.json.tmp', 'data/repos.json')
hc = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}
rs = list(store.values()); cnt = C.Counter(r['cls'] for r in rs); comp = cnt['AGREE'] + cnt['DISAGREE']; lo, hi = K.wilson(cnt['DISAGREE'], comp)
oc = K.CANNOT_TELL if (comp < 30 or not gate) else (K.ABOVE if lo > 0.10 else (K.CONSISTENT if hi < 0.05 else K.CANNOT_TELL))
dis = [r for r in rs if r['cls'] == 'DISAGREE']; why = C.Counter(r['why'] for r in rs if r['cls'] == 'NOT_COMPARABLE')
def fmt(x): return ('%.2f B' % (x / 1e9)) if x >= 1e9 else ('%.0f M' % (x / 1e6))
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), gate='passed' if gate else 'FAILED', models=len(rs),
           comparison=dict(of=comp, n=cnt['DISAGREE'], share=round(cnt['DISAGREE'] / comp, 4) if comp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc, organizations=len({r['id'].split('/')[0] for r in dis}), awaiting=len([r for r in dis if r['id'] not in hc])),
           classes={c: dict(n=cnt[c]) for c in ('AGREE', 'DISAGREE', 'NOT_COMPARABLE')}, not_comparable_reasons={w: dict(n=n) for w, n in sorted(why.items(), key=lambda x: -x[1])},
           api_mismatch=[dict(repo=r['id'], total=r['total'], breakdown=r['psum'], stated=fmt(r['stated']) if r.get('stated') else None) for r in rs if r.get('why') == 'Hugging Face total does not match its own breakdown'],
           disagree_list=[dict(repo=r['id'], stated=fmt(r['stated']), actual=fmt(r['total']), ratio=r['ratio'], reason=hc[r['id']]) for r in dis if r['id'] in hc])
json.dump(out, open('summary_hfsize.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'hfsize_live', '--path', os.path.join(H, 'summary_hfsize.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('hfsize:', len(rs), 'models;', dict(cnt), 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
