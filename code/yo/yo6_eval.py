"""yo6_eval.py (yo5_eval.py for PLAN_YO_V6) SET MODE [ADAPTER] -- SET test6 scores data6/test_items.jsonl, SET future6 scores
data6/future_items.jsonl (PLAN_YO_V6.md FUTURE6, built once by yo6_future.py). Scorer and decoding as yo4_eval.py. MODE: oracle (known-good: the code's own answers) |
nothing (A null) | consistent (C null) | binary (C null) | base | yo. Writes eval2_<name>.jsonl, one row per item. Greedy decoding."""
import json, sys, os, re, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
SET = sys.argv.pop(1); assert SET in ('test6', 'future6', 'future7', 'test8c'), SET
items = [json.loads(l) for l in open((f'{HERE}/data8/test8c_items.jsonl' if SET == 'test8c' else f'{HERE}/data7/future_items.jsonl' if SET == 'future7' else f'{HERE}/data6/' + ('test_items.jsonl' if SET == 'test6' else 'future_items.jsonl')))]
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
    elif mode == 'all': out = json.dumps({'stale': sorted(int(q) for q in re.findall(r'^q(\d+):', it['prompt'], re.M)), 'zero': []}) if it['job'] == 'A' else ''   # PLAN_YO_V4 null: flag every qubit
    elif mode == 'consistent': out = 'CONSISTENT' if it['job'] == 'C' else ''
    elif mode == 'daterule':   # PLAN_YO_V3 baseline: zeros exactly, plus stale = a T1/T2 date two or more calendar days before the stamp
        if it['job'] == 'A':
            import re as _re, datetime as _dt
            _S = _dt.datetime.strptime(_re.search(r'stamp (\d{4}-\d\d-\d\d) ', it['prompt']).group(1), '%Y-%m-%d').date(); _st = []; _z = []
            for _l in it['prompt'].splitlines():
                _m = _re.match(r'q(\d+): (.*)', _l)
                if not _m: continue
                _q = int(_m.group(1)); _ds = [_dt.datetime.strptime(d, '%Y-%m-%d').date() for d in _re.findall(r'T[12]=[^ ]+ \((\d{4}-\d\d-\d\d) ', _m.group(2))]
                if _ds and (_S - min(_ds)).days >= 2: _st.append(_q)
                _z += [f'{_q}:{f}' for f in ('readout_error', 'prob_meas1_prep0', 'prob_meas0_prep1') if _re.search(f + r'=0 ', _m.group(2) + ' ') or _re.search(f + r'=0\b(?![.e])', _m.group(2))]
            out = json.dumps({'stale': sorted(_st), 'zero': sorted(set(_z))})
        else: out = ''
    elif mode == 'binary': out = ('ABOVE' if it['lo'] > it['r'] else 'BELOW' if it['hi'] < it['r'] else 'CONSISTENT') if it['job'] == 'C' else ''
    else: out = generate(model, tok, prompt=render(it['prompt']), max_tokens=200 if it['job'] == 'A' else 8, verbose=False)
    s, p = score(it, out)
    rows.append({'job': it['job'], 'id': it['id'], 'record': it['record'], 'score': s, 'pred': p, 'truth': it['answer'] if it['job'] == 'C' else None, 'out': out[:300]})
    if mode in ('base', 'yo') and n % 50 == 0: print(SET, name, 'item', n, 'of', len(items), flush=True)
with open(f'{HERE}/eval6_{SET}_{name}.jsonl', 'w') as f:
    for r in rows: f.write(json.dumps(r) + '\n')
for j in 'AC':
    s = [r['score'] for r in rows if r['job'] == j]
    if (mode in ('nothing', 'daterule', 'all') and j == 'C') or (mode in ('consistent', 'binary') and j == 'A'): continue   # a one-job null has no score on the other job
    if not s: continue
    line = f'{SET} {name} job {j} n {len(s)} mean {sum(s) / len(s):.3f}'
    if j == 'C':
        ct = [r for r in rows if r['job'] == 'C' and r['truth'] == 'CANNOT_TELL']; line += f' | forced-verdict rate {sum(r["pred"] != "CANNOT_TELL" for r in ct) / len(ct):.3f}'
        line += ' | confusion ' + json.dumps({t: dict(collections.Counter(r['pred'] for r in rows if r['job'] == 'C' and r['truth'] == t)) for t in LAB})
    else: line += ' | unparsed %d' % sum(r['pred'] == 'unparsed' for r in rows if r['job'] == 'A')
    print(line)
