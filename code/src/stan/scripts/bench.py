"""bench.py (12 Nov): the scoreboard. Any Ollama model on any host labels the gold DEV claims with the same teacher prompt and the same
label rules, then is scored with score.py exactly as the teachers and STAN are. Gold test is never read here. Nothing here trains anything.
  python3 bench.py <host> <model>      -> runs/bench_<model>.jsonl, results/bench.json (one row per model)"""
import json, sys, time, os
from common import *; from score import *
host, model = sys.argv[1], sys.argv[2]; tag = model.replace(':', '_').replace('/', '_')
out = S + '/runs/bench_%s.jsonl' % tag
items = [(g['id'], g['text']) for g in json.load(open(S + '/data/gold_items.json')) if g.get('text') and g['split'] == 'dev']
done = {r['id'] for r in jl_read(out)}
with open(out, 'a') as f:
    for i, text in items:
        if i in done: continue
        t = time.time()
        try: raw = ollama(host, model, teacher_prompt(text))
        except Exception as e: continue
        o = parse_obj(raw); labs = {c: norm_label(c, (o or {}).get(c), text) for c in CODES}
        f.write(json.dumps({'set': 'gold', 'id': i, 'raw': raw, 'labels': labs, 'secs': round(time.time() - t, 1)}) + '\n'); f.flush()
G = gold(); V = agree_vec(jl_read(out), G, 'dev')
R = json.load(open(S + '/results/bench.json')) if os.path.exists(S + '/results/bench.json') else {}
R[model] = {'host': host, 'per_code': table(V, G, 'dev'), 'pooled': pooled_rate(V), 'n_items': len(items), 'labelled': len(jl_read(out))}
json.dump(R, open(S + '/results/bench.json', 'w'), indent=1); print(model, R[model]['pooled'])
