"""yf_build.py -- builds the FRESH TEST items per PLAN_YO_FRESH.md with yr_data.py's own functions (candidates, prompt, truth, regex, norm), unchanged.
Writes data/test_items_fresh.jsonl and DATA_YO_FRESH.sha256 (items + the List file it read). Runs no model."""
import json, os, sys, hashlib, collections, importlib.util
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H); Q = os.path.expanduser('~/bones-forge/qia_leads/')
spec = importlib.util.spec_from_file_location('yd', R + '/yr_data.py'); yd = importlib.util.module_from_spec(spec); spec.loader.exec_module(yd)
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained('Qwen/Qwen3-1.7B')
used = {k for k, _, _ in yd.papers()}
LF = Q + 'matrix_page/list.json'; L = json.load(open(LF)); rows = L if isinstance(L, list) else next(v for v in L.values() if isinstance(v, list))
full = {}
for r in rows:
    if str(r.get('read', '')).startswith('Full text'): full.setdefault(yd.norm(r['link']), r)
def key(fn):
    b = fn[:-4]
    if b.startswith('arxiv_'): return 'ax:' + b[6:]
    if b.startswith('doi_'): return 'doi:' + b[4:].replace('_', '/', 1).lower()
have = {}
for d in ('sweep_20261101/texts_read', 'sweep_20261101/texts', 'backfill_20261101/texts'):
    for f in sorted(os.listdir(Q + d)):
        if f.endswith('.txt'):
            k = key(f)
            if k: have.setdefault(k, Q + d + '/' + f)
keys = sorted(k for k in full if k not in used and k in have); empty = 0; items = []
for k in keys:
    text = open(have[k], errors='replace').read()
    if not text.strip(): empty += 1; continue
    t = yd.truth(full[k])
    for q in ('DATES', 'LINK', 'REQUEST'):
        c, _ = yd.candidates(text, q); pr = yd.prompt(q, c); n = len(tok(pr)['input_ids'])
        while n > 1900 and c: c = c[:-1]; pr = yd.prompt(q, c); n = len(tok(pr)['input_ids'])
        items.append(dict(id=f'{k}|{q}', paper=k, q=q, split='FRESH', prompt=pr, answer=t[q], regex=yd.regex(q, c), majority='NO', n_tok=n, text_file=os.path.relpath(have[k], Q)))
assert not ({i['paper'] for i in items} & used)
os.makedirs(H + '/data', exist_ok=True)
with open(H + '/data/test_items_fresh.jsonl', 'w') as f:
    for i in items: f.write(json.dumps(i) + '\n')
sys.path.insert(0, R); from yr_known_good import known_good; print('known-good', known_good(items))
os.system(f'cd {H} && shasum -a 256 data/test_items_fresh.jsonl {LF} > DATA_YO_FRESH.sha256')
yes = {q: sum(i['answer'] == 'YES' for i in items if i['q'] == q) for q in ('DATES', 'LINK', 'REQUEST')}
print('papers', len(keys) - empty, 'empty text left out', empty, 'items', len(items), 'YES per field', yes)
