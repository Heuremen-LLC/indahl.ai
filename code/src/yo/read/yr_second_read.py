"""yr_second_read.py (2 Nov 2026, internal, not a reading): YO Read seed 61 reads every List paper with a saved text (all splits) and writes
the papers where its answer and the List entry disagree, as a reread queue. Training papers are included, so agreement there is inflated
and nothing from this file is published or scored. A disagreement only sends a paper back for a full reread by hand."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(H)); sys.path.insert(0, H)
import yr_data as D
from mlx_lm import load, generate
from yo2_data import render
model, tok = load('Qwen/Qwen3-1.7B', adapter_path=H + '/adapters/read1')
out = open(H + '/second_read_queue.jsonl', 'w'); n = 0
for k, r, p in D.papers():
    text = open(p, errors='replace').read(); t = D.truth(r)
    for q in ('DATES', 'LINK', 'REQUEST'):
        c, _ = D.candidates(text, q); pr = D.prompt(q, c)
        a = generate(model, tok, prompt=render(pr), max_tokens=8, verbose=False)
        y = 'YES' if 'YES' in a.upper() else 'NO' if 'NO' in a.upper() else None
        if y and y != t[q]:
            out.write(json.dumps(dict(paper=k, link=r['link'], q=q, list=t[q], yo=y, split=D.split(k), cands=c[:20])) + '\n'); out.flush()
    n += 1
    if n % 50 == 0: print('papers', n, flush=True)
print('done', n)
