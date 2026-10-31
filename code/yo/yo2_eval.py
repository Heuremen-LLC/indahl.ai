"""yo2_eval.py MODE [ADAPTER] -- scores data2/test_items.jsonl per PLAN_YO_V2.md. MODE: oracle (known-good: the code's own answers) |
nothing (A null) | consistent (C null) | binary (C null) | base | yo. Writes eval2_<name>.jsonl, one row per item. Greedy decoding."""
import json, sys, os, re, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
items = [json.loads(l) for l in open(f'{HERE}/data2/test_items.jsonl')]
LAB = ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')
def f1(p, t):
    p, t = set(p), set(t)
    if not p and not t: return 1.0
    if not p or not t: return 0.0
    tp = len(p & t); return 0.0 if tp == 0 else 2 * tp / (len(p) + len(t))
def parse_c(out):   # rule fixed before any output was read: first label-like token, "CANNOT TELL" accepted for CANNOT_TELL
    m = re.search(r'\b(ABOVE|BELOW|CONSISTENT|CANNOT[ _]TELL)\b', out.upper())
    return m.group(1).replace(' ', '_') if m else None
def score(it, out):
    if it['job'] == 'C':
        p = parse_c(out); return float(p == it['answer']), p
    t = json.loads(it['answer'])
    try: p = json.loads(out[out.index('{'):out.rindex('}') + 1])
    except Exception: return 0.0, 'unparsed'
    try: return (f1([int(x) for x in p.get('stale', [])], t['stale']) + f1([str(x) for x in p.get('zero', [])], t['zero'])) / 2, 'json'
    except Exception: return 0.0, 'unparsed'
mode = sys.argv[1]; name = mode if mode != 'yo' else 'yo_' + os.path.basename(sys.argv[2].rstrip('/'))
if mode in ('base', 'yo'):
    from mlx_lm import load, generate
    from yo2_data import render
    model, tok = load('Qwen/Qwen3-1.7B', adapter_path=sys.argv[2] if mode == 'yo' else None)
rows = []
for n, it in enumerate(items):
    if mode == 'oracle': out = it['answer']
    elif mode == 'nothing': out = '{"stale": [], "zero": []}' if it['job'] == 'A' else ''
    elif mode == 'consistent': out = 'CONSISTENT' if it['job'] == 'C' else ''
    elif mode == 'binary': out = ('ABOVE' if it['lo'] > it['r'] else 'BELOW' if it['hi'] < it['r'] else 'CONSISTENT') if it['job'] == 'C' else ''
    else: out = generate(model, tok, prompt=render(it['prompt']), max_tokens=200 if it['job'] == 'A' else 8, verbose=False)
    s, p = score(it, out)
    rows.append({'job': it['job'], 'id': it['id'], 'record': it['record'], 'score': s, 'pred': p, 'truth': it['answer'] if it['job'] == 'C' else None, 'out': out[:300]})
    if mode in ('base', 'yo') and n % 50 == 0: print(name, 'item', n, 'of', len(items), flush=True)
with open(f'{HERE}/eval2_{name}.jsonl', 'w') as f:
    for r in rows: f.write(json.dumps(r) + '\n')
for j in 'AC':
    s = [r['score'] for r in rows if r['job'] == j]
    if (mode == 'nothing' and j == 'C') or (mode in ('consistent', 'binary') and j == 'A'): continue   # a one-job null has no score on the other job
    line = f'{name} job {j} n {len(s)} mean {sum(s) / len(s):.3f}'
    if j == 'C':
        ct = [r for r in rows if r['job'] == 'C' and r['truth'] == 'CANNOT_TELL']; line += f' | forced-verdict rate {sum(r["pred"] != "CANNOT_TELL" for r in ct) / len(ct):.3f}'
        line += ' | confusion ' + json.dumps({t: dict(collections.Counter(r['pred'] for r in rows if r['job'] == 'C' and r['truth'] == t)) for t in LAB})
    else: line += ' | unparsed %d' % sum(r['pred'] == 'unparsed' for r in rows if r['job'] == 'A')
    print(line)
