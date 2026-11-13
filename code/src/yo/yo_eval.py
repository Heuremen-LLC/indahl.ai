"""yo_eval.py MODE [ADAPTER] -- scores TEST items per PLAN_YO_V1. MODE: nothing (A null 1) | majority (B null 1) | base | yo.
Writes eval_<name>.jsonl (one row per item: job, id, score) for the bootstrap comparison."""
import json, sys, os, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
items = [json.loads(l) for l in open(f'{HERE}/data/test_items.jsonl')]
def f1(p, t):
    p, t = set(p), set(t)
    if not p and not t: return 1.0
    if not p or not t: return 0.0
    tp = len(p & t); return 0.0 if tp == 0 else 2 * tp / (len(p) + len(t))
def score(it, out):
    if it['job'] == 'B': return float(out.strip().split()[0].strip('.,"\'') == it['answer'] if out.strip() else 0.0)
    t = json.loads(it['answer'])
    try: p = json.loads(out[out.index('{'):out.rindex('}') + 1])
    except Exception: return 0.0
    try: return (f1([int(x) for x in p.get('stale', [])], t['stale']) + f1([str(x) for x in p.get('zero', [])], t['zero'])) / 2
    except Exception: return 0.0
mode = sys.argv[1]; name = mode if mode != 'yo' else 'yo_' + os.path.basename(sys.argv[2].rstrip('/'))
if mode in ('base', 'yo'):
    from mlx_lm import load, generate
    from yo_data import render
    model, tok = load('Qwen/Qwen3-1.7B', adapter_path=sys.argv[2] if mode == 'yo' else None)
maj = None
if mode == 'majority':
    tr = [l for l in open(os.path.expanduser('~/bones-forge/watch/tp_score.jsonl'))]
    maj = collections.Counter(json.loads(l)['lesson'] for l in tr if json.loads(l)['at'] < '2026-10-21').most_common(1)[0][0]
rows = []
for it in items:
    if mode == 'nothing': out = '{"stale": [], "zero": []}' if it['job'] == 'A' else ''
    elif mode == 'majority': out = maj if it['job'] == 'B' else ''
    else: out = generate(model, tok, prompt=render(it['prompt']), max_tokens=160, verbose=False)
    rows.append({'job': it['job'], 'id': it['id'], 'score': score(it, out), 'out': out[:300]})
with open(f'{HERE}/eval_{name}.jsonl', 'w') as f:
    for r in rows: f.write(json.dumps(r) + '\n')
for j in 'AB':
    s = [r['score'] for r in rows if r['job'] == j]; print(name, 'job', j, 'n', len(s), 'mean %.3f' % (sum(s) / len(s)))
