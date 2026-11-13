"""yf_lang.py -- Sage 5 Nov translation pass, step 1: which primary, sensitivity and trained papers are not in English?
Detector: share of common English function words among the first 300 word tokens of (title + text file); below 0.08 = non-English
candidate. Known positive that must be caught: zenodo.18154889 (Turkish). Inputs only."""
import json, os, re, glob, builtins, collections
H = os.path.expanduser('~/bones-forge/yo/read/fresh'); Q = os.path.expanduser('~/bones-forge/qia_leads/')
src = open(H + '/yf_primary.py').read().split('\n'); exec('\n'.join(src[5:14]).replace('__file__', repr(H + '/yf_primary.py')))
_o = builtins.open
def _op(p, *a, **k): return _o(Q + 'matrix_page/list.json.pre-removal-20261102' if p == Q + 'matrix_page/list.json' else p, *a, **k)
builtins.open = _op; P688 = {k: p for k, _, p in yd.papers()}; builtins.open = _o
M = json.load(open(H + '/contam/meta_cache.json'))
EN = set('the of and to in a is that for on with as by this are we be from at an it which or not can our these has have was were its their than also been between'.split())
fresh = {}
for l in open(H + '/data/test_items_fresh.jsonl'):
    r = json.loads(l); fresh[r['paper']] = Q + r['text_file']; assert os.path.exists(fresh[r['paper']]), r['text_file']
prim = set(open(H + '/primary_ids.txt').read().split()); sens = set(open(H + '/sensitivity_ids.txt').read().split())
trained = {k: p for k, p in P688.items() if yd.split(k) in ('TRAIN', 'VALID')}
def score(k, p):
    t = (M.get(k, {}).get('title') or '') + ' ' + (open(p, errors='replace').read() if p and os.path.exists(p) else '')
    t = re.sub(r'(?i)zenodo|skip to main|you are using an outdated browser.*?experience\.|communities my dashboard log in sign up|scheduled maintenance.*?upgrade\.', ' ', t)
    w = re.findall(r'[^\W\d_]+', t.lower())[:300]
    return (sum(x in EN for x in w) / len(w)) if w else 0.0, len(w)
rows = []
for name, ks in (('fresh', {k: fresh[k] for k in prim | sens}), ('trained', trained)):
    for k, p in ks.items():
        s, n = score(k, p); rows.append((s, n, name, k))
rows.sort()
print('known positive zenodo.18154889:', [r for r in rows if r[3] == 'doi:10.5281/zenodo.18154889'])
cand = [r for r in rows if r[0] < 0.08]
print(f'non-English candidates (share < 0.08): {len(cand)} of {len(rows)}')
for s, n, name, k in cand: print(f'  {name:7} {k}  share {s:.3f} (n {n})  | {(M.get(k, {}).get("title") or "")[:110]}')
