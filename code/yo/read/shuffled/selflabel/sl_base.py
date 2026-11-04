"""sl_base.py -- SELF-LABEL arm, step 1 (PLAN_YO_SHUFFLED Addenda 2-5). The frozen base model answers every train and valid prompt.
Decoding as Addendum 2: mlx_lm.generate, greedy, max_tokens 8, prompt rendered by yo2_data.render exactly as yr_eval.py; parse = yr_eval.py line 12
(case-sensitive \\b(YES|NO)\\b). Off-format items are left out of training, never filled. Writes raw_<split>.jsonl, data/<split>.jsonl, BASE_RATES.text."""
import json, os, re, sys, collections
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(H + '/../..'); sys.path.insert(0, os.path.dirname(R))
from mlx_lm import load, generate
from yo2_data import render
Q = {'DATES': 'Does the paper print a date or date range of its own quantum hardware runs',
     'LINK': 'Does the paper print a URL, DOI or repository for its own data or code',
     'REQUEST': 'Does the paper say its data or code are available on request?'}
def qof(p):
    hit = [k for k, v in Q.items() if v in p]; assert len(hit) == 1, hit; return hit[0]
def parse(o):
    m = re.search(r'\b(YES|NO)\b', o or ''); return m.group(1) if m else None
model, tok = load('Qwen/Qwen3-1.7B')
lines = ['SELF-LABEL base-rate report (Addenda 2-5), written before any self-label adapter trains. Base Qwen/Qwen3-1.7B snapshot 70d244cc, greedy, max_tokens 8.']
tot = collections.Counter()
for split in ('train', 'valid'):
    items = [json.loads(l) for l in open(f'{R}/data/{split}.jsonl')]
    raw, keep = [], []
    for n, it in enumerate(items):
        out = generate(model, tok, prompt=render(it['prompt']), max_tokens=8, verbose=False); p = parse(out)
        raw.append(dict(n=n, q=qof(it['prompt']), real=it['completion'].strip(), self=p, out=out[:200]))
        if p is not None: keep.append(dict(prompt=it['prompt'], completion=p))
        if n % 100 == 0: print(split, n, 'of', len(items), flush=True)
    with open(f'{H}/raw_{split}.jsonl', 'w') as f:
        for r in raw: f.write(json.dumps(r) + '\n')
    with open(f'{H}/data/{split}.jsonl', 'w') as f:
        for r in keep: f.write(json.dumps(r) + '\n')
    for q in Q:
        rs = [r for r in raw if r['q'] == q]; read = [r for r in rs if r['self'] is not None]; off = len(rs) - len(read)
        sy = sum(r['self'] == 'YES' for r in read); ry = sum(r['real'] == 'YES' for r in rs)
        tot['n'] += len(rs); tot['off'] += off
        lines.append(f"{split:5s} {q:8s}: n {len(rs)}; self-label YES {sy}/{len(read)} = {sy / max(1, len(read)):.3f}; real YES {ry}/{len(rs)} = {ry / len(rs):.3f}; off-format {off} ({off / len(rs):.1%})")
lines.append(f"overall off-format {tot['off']}/{tot['n']} = {tot['off'] / tot['n']:.1%} (Addendum 3 flag above 5 % overall or 10 % for one question)")
open(H + '/BASE_RATES.text', 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines))
