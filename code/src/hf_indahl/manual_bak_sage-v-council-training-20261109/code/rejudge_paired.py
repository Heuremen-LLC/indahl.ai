#!/usr/bin/env python3
"""rejudge_paired.py <run_dir> (8 Nov, Sage: re-judge the STORED paired generations under the capped judge; no GPU). Same prompts, same outputs, same
grounding check; qwen3:8b q per claim (triangle judge prompt as realjob_eval) + minicheck on the true chunk; q capped at 0.2 when minicheck says No.
Accuracy = grounded AND capped q >= 0.5. Paired bootstrap over prompts, ALL and CLEAN (chunk set not in the run's training rows)."""
import json, re, sys, os, random
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H); import sage_v as V, sage_flywheel as F
W = sys.argv[1].rstrip('/'); ev = json.load(open(W + '/realjob_items.json')); out = json.load(open(W + '/realjob_out.json'))
tr = [json.loads(l) for f in ('train.jsonl', 'valid.jsonl') for l in open(f'{W}/data/{f}') if l.strip()]
ids = lambda p: frozenset(re.findall(r'\[chunk ([^\s|\]]+) \|', p)); trsets = {ids(r['messages'][1]['content']) for r in tr}
CH = re.compile(r'\[chunk ([^\s|\]]+) \|[^\]]*\]\n(.*?)(?=\n\n\[chunk |\n\nYOUR TRIANGLE CARRIED|\n\nAnswer the seed|\Z)', re.S)
tris = F.triangles()
def score(it, txt):
    ch = [{'id': a, 'text': b} for a, b in CH.findall(it['prompt'])]; by = {r['id']: r for r in ch}
    try: cl = F.parse_claims(json.loads(re.search(r'\{.*\}', txt, re.S).group(0)).get('claims'), ch)
    except Exception: return []
    if not cl: return []
    lines = '\n'.join(f"[{k}] CLAIM: {x['claim']}\n    QUOTE: \"{x['quote'][:300]}\"\n    CHUNK {x.get('true_chunk') or x['chunk']}: " + (F.around(by[x['true_chunk']]['text'], x['quote']) if x.get('true_chunk') in by else '(no such chunk was shown)') for k, x in enumerate(cl))
    jm, jh = tris[it['tri']]['judge']
    user = ("You are an EXTERNAL JUDGE. For each numbered claim, judge only from its chunk: is the claim right, and does the quote really say it? "
            "q is your probability (0 to 1) that the claim is right. A quote that is not in the chunk, or a chunk that was not shown, means q near 0.\n\n" + lines + '\n\nJSON {"scores": [{"k": 0, "q": 0.0, "why": "one short reason"}]}')
    jj, raw, ms, cause = F.ask(jh, jm, "You are a strict external judge of claims against source text. Answer only JSON.", user, 900); qs = {}
    for s in (jj or {}).get('scores', []) if isinstance(jj, dict) else []:
        try: qs[int(s.get('k'))] = max(0.0, min(1.0, float(s.get('q'))))
        except Exception: pass
    for k, x in enumerate(cl):
        x['q_raw'] = qs.get(k); x['mc'] = V.mc_verdict(x['claim'], by[x['true_chunk']]['text']) if x.get('true_chunk') in by else None
        x['q'] = min(x['q_raw'], 0.2) if (x['mc'] == 'No' and x['q_raw'] is not None) else x['q_raw']
        x['y'] = int(bool(x['grounded'] and x['q'] is not None and x['q'] >= 0.5)); x['cw'] = int(x['p'] is not None and x['p'] >= 0.8 and not x['y'])
    return cl
S = {a: [score(it, t) for it, t in zip(ev, out[a])] for a in ('base', 'adapter')}
def rate(rows, k): n = sum(len(r) for r in rows); return sum(x[k] for r in rows for x in r) / n if n else None
res = {}
for name, idx in (('ALL', list(range(len(ev)))), ('CLEAN', [i for i, e in enumerate(ev) if ids(e['prompt']) not in trsets])):
    d = {}
    for k in ('grounded', 'y', 'cw'):
        b, a = rate([S['base'][i] for i in idx], k), rate([S['adapter'][i] for i in idx], k); rng = random.Random(8); v = []
        for _ in range(2000):
            s = [rng.choice(idx) for _ in idx]; x_, y_ = rate([S['adapter'][i] for i in s], k), rate([S['base'][i] for i in s], k)
            if x_ is not None and y_ is not None: v.append(x_ - y_)
        v.sort(); d[{'y': 'accuracy', 'cw': 'confident_wrong', 'grounded': 'grounded'}[k]] = [round(b, 3), round(a, 3), round(v[int(.025 * len(v))], 3), round(v[int(.975 * len(v)) - 1], 3)]
    res[name] = {'n': len(idx), **d}; print(name, res[name], flush=True)
json.dump({'run': W, 'capped': True, 'res': res}, open(W + '/rejudge_capped.json', 'w'), indent=1)
