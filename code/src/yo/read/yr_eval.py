"""yr_eval.py -- scores one arm on YO Read TEST items (PLAN_YO_READ). Modes: truth (KNOWN-GOOD), regex, majority, base, yo <adapter>.
Parse fixed in the plan: the first YES or NO word in the reply; anything else is unread and scored wrong. Writes eval_<arm>.jsonl."""
import json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(H))
items = [json.loads(l) for l in open(H + '/data/test_items.jsonl')]
mode = sys.argv[1]; name = mode if mode != 'yo' else 'yo_' + os.path.basename(sys.argv[2].rstrip('/'))
if mode in ('base', 'yo'):
    from mlx_lm import load, generate
    from yo2_data import render
    model, tok = load('Qwen/Qwen3-1.7B', adapter_path=sys.argv[2] if mode == 'yo' else None)
def parse(o):
    m = re.search(r'\b(YES|NO)\b', o or ''); return m.group(1) if m else None
rows = []
for n, it in enumerate(items):
    if mode == 'truth': out = it['answer']
    elif mode in ('regex', 'majority'): out = it[mode]
    else: out = generate(model, tok, prompt=render(it['prompt']), max_tokens=8, verbose=False)
    p = parse(out); rows.append(dict(id=it['id'], paper=it['paper'], q=it['q'], pred=p, score=float(p == it['answer']), out=out[:200]))
    if mode in ('base', 'yo') and n % 50 == 0: print(name, 'item', n, 'of', len(items), flush=True)
with open(f'{H}/eval_{name}.jsonl', 'w') as f:
    for r in rows: f.write(json.dumps(r) + '\n')
print(name, 'n', len(rows), 'unread', sum(r['pred'] is None for r in rows), 'mean', f"{sum(r['score'] for r in rows) / len(rows):.3f}")
