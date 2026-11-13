#!/usr/bin/env python3
"""realjob_eval.py (8 Nov, Sage's point c): does a trained seat do the council's REAL job better, not just the plant test?
  1 PICK   the seat's latest real council prompts (non-demo) that were NOT in its training or validation set (up to N, default 30).
  2 ANSWER base and adapter (MLX, temp 0) answer each prompt exactly as the council asked it. One GPU job; Mac lanes paused.
  3 JUDGE  both answers' claims go through the same grounding check (exact quote in a shown chunk) and the triangle's own external judge.
  4 READ   per arm: answered (parsable claims), claims per prompt, no-p rate, grounded rate, accuracy (grounded AND q >= 0.5), Brier (p vs that).
           Paired bootstrap over prompts (2,000). Plus the plant test per class from the training run's holdout output.
  5 RULE   REAL_OK only if NO measure is wholly worse: answered, grounded and accuracy CIs not wholly below 0, Brier CI not wholly above 0,
           and no plant class drops by more than 0.10. Writes <run>/realjob.json and a promotions.jsonl row.
Usage: realjob_eval.py <seat> <run_dir> [N]"""
import json, os, re, sys, time, random, sqlite3, subprocess, fcntl, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import sage_flywheel as F, sage_v as V
PY = os.path.expanduser('~/sage-v/venv/bin/python')
FRESH = '--fresh' in sys.argv; sys.argv = [a for a in sys.argv if a != '--fresh']
seat, W = sys.argv[1], sys.argv[2].rstrip('/'); N = int(sys.argv[3]) if len(sys.argv) > 3 else 30
base = json.load(open(H + '/seats.json'))['mlx_bases'][seat]
def log(m): print(m, flush=True); open(H + '/train/calib_train.log', 'a').write(time.strftime('%H:%M:%SZ ', time.gmtime()) + 'REALJOB ' + m + '\n')
# ---------- 1 PICK ----------
seen = set()
for f in ('train.jsonl', 'valid.jsonl'):
    for l in open(f'{W}/data/{f}'):
        if l.strip(): seen.add(json.loads(l)['messages'][1]['content'])
c = sqlite3.connect(f'file:{H}/sage_v.db?mode=ro', uri=True, timeout=30)
items = []
for sha, tri, system, prompt in c.execute("""select p.prompt_sha, p.triangle, pr.system, pr.prompt from pq p join prompts pr on pr.sha = p.prompt_sha
                                             where p.model = ? and p.demo = 0 group by p.prompt_sha order by max(p.id) desc""", (seat,)):
    if prompt in seen: continue
    items.append({'sha': sha, 'tri': tri, 'system': system, 'prompt': prompt})
    if len(items) >= N: break
if FRESH:   # Sage 8 Nov: paired set built before training from held-out seeds (prepare_paired.py)
    items = [{'sha': x['sha'], 'tri': x['tri'], 'system': x['system'], 'prompt': x['prompt']} for x in json.load(open(H + f"/train/paired_{seat.replace(':', '_')}.json"))['items'] if x['prompt'] not in seen][:N]
if len(items) < 10: log(f'{seat}: only {len(items)} untrained real prompts, need 10 -> CANNOT_TELL'); json.dump({'verdict': 'CANNOT_TELL', 'n': len(items)}, open(W + '/realjob.json', 'w')); sys.exit(0)
json.dump(items, open(W + '/realjob_items.json', 'w'))
# ---------- 2 ANSWER (MLX, one GPU job) ----------
lk = open(H + '/.train.lock', 'w'); fcntl.flock(lk, fcntl.LOCK_EX)
open(H + '/PAUSE_MAC', 'w').write(f'realjob eval {seat}\n')
flk = open(H + '/.flywheel.lock', 'w'); fcntl.flock(flk, fcntl.LOCK_EX)   # 8 Nov: wait for the running deep cycle to END (its later stages reloaded the Mac models mid-harvest), and hold the lock so no new one starts
time.sleep(5)

try:
    for m in json.load(urllib.request.urlopen('http://127.0.0.1:11500/api/ps', timeout=10))['models']:
        urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:11500/api/generate', json.dumps({'model': m['name'], 'keep_alive': 0}).encode()), timeout=60)
except Exception as e: log(f'unload skipped: {e}')
code = f'''
import json
from mlx_lm import load, batch_generate
from mlx_lm.sample_utils import make_sampler
ev = json.load(open("{W}/realjob_items.json")); res = {{}}
for name, ad in (("base", None), ("adapter", "{W}/adapters")):
    model, tok = load("{base}", adapter_path=ad); out = []
    for i in range(0, len(ev), 4):
        ch = ev[i:i + 4]
        ps = [tok.apply_chat_template([{{"role": "system", "content": e["system"]}}, {{"role": "user", "content": e["prompt"]}}], add_generation_prompt=True) for e in ch]
        out += batch_generate(model, tok, ps, max_tokens=900, sampler=make_sampler(temp=0.0)).texts
    res[name] = out
    del model
json.dump(res, open("{W}/realjob_out.json", "w"))
'''
open(W + '/realjob_gen.py', 'w').write(code)
try:
    r = subprocess.run([PY, W + '/realjob_gen.py'], capture_output=True, text=True); open(W + '/realjob_gen.log', 'w').write(r.stdout + r.stderr)
finally:
    try: os.remove(H + '/PAUSE_MAC')
    except FileNotFoundError: pass
    fcntl.flock(lk, fcntl.LOCK_UN); fcntl.flock(flk, fcntl.LOCK_UN)
if r.returncode != 0: log(f'{seat}: generation failed rc {r.returncode}: {(r.stderr or "")[-300:]}'); sys.exit(1)
out = json.load(open(W + '/realjob_out.json'))
# ---------- 3 JUDGE (same grounding check, the triangle's own judge) ----------
CH = re.compile(r'\[chunk ([^\s|\]]+) \|[^\]]*\]\n(.*?)(?=\n\n\[chunk |\n\nYOUR TRIANGLE CARRIED|\n\nAnswer the seed|\Z)', re.S)
tris = F.triangles()
def score(it, txt):
    ch = [{'id': m.group(1), 'text': m.group(2)} for m in CH.finditer(it['prompt'])]
    try: j = json.loads(re.search(r'\{.*\}', txt, re.S).group(0)); cl = F.parse_claims(j.get('claims'), ch)
    except Exception: return {'answered': 0, 'claims': []}
    if not cl: return {'answered': 0, 'claims': []}
    by = {r['id']: r for r in ch}
    lines = '\n'.join(f"[{k}] CLAIM: {x['claim']}\n    QUOTE: \"{x['quote'][:300]}\"\n    CHUNK {x['chunk']}: " + (by[x['chunk']]['text'][:700] if x['chunk'] in by else '(no such chunk was shown)') for k, x in enumerate(cl))
    jm, jh = tris[it['tri']]['judge']
    user = ("You are an EXTERNAL JUDGE. For each numbered claim, judge only from its chunk: is the claim right, and does the quote really say it? "
            "q is your probability (0 to 1) that the claim is right. A quote that is not in the chunk, or a chunk that was not shown, means q near 0.\n\n" + lines +
            '\n\nJSON {"scores": [{"k": 0, "q": 0.0, "why": "one short reason"}]}')
    jj, raw, ms, cause = F.ask(jh, jm, "You are a strict external judge of claims against source text. Answer only JSON.", user, 900)
    qs = {}
    for s in (jj or {}).get('scores', []) if isinstance(jj, dict) else []:
        try: qs[int(s.get('k'))] = max(0.0, min(1.0, float(s.get('q'))))
        except Exception: pass
    for k, x in enumerate(cl): x['q'] = qs.get(k); x['y'] = int(bool(x['grounded'] and x['q'] is not None and x['q'] >= 0.5))
    return {'answered': 1, 'claims': cl}
S = {arm: [score(it, t) for it, t in zip(items, out[arm])] for arm in ('base', 'adapter')}
# ---------- 4 READ ----------
def per_prompt(s):   # one row per prompt: answered, n claims, grounded share, accuracy share, brier sum, p count, no-p count
    cl = s['claims']; ps = [x for x in cl if x['p'] is not None]
    return (s['answered'], len(cl), sum(x['grounded'] for x in cl), sum(x['y'] for x in cl), sum((x['p'] - x['y']) ** 2 for x in ps), len(ps), len(cl) - len(ps))
def summ(rows):
    n_cl = sum(r[1] for r in rows); n_p = sum(r[5] for r in rows)
    return {'prompts': len(rows), 'answered': round(sum(r[0] for r in rows) / len(rows), 3), 'claims_per_prompt': round(n_cl / len(rows), 2),
            'grounded': round(sum(r[2] for r in rows) / n_cl, 3) if n_cl else None, 'accuracy': round(sum(r[3] for r in rows) / n_cl, 3) if n_cl else None,
            'brier': round(sum(r[4] for r in rows) / n_p, 3) if n_p else None, 'no_p': round(sum(r[6] for r in rows) / n_cl, 3) if n_cl else None}
B_, A_ = [per_prompt(s) for s in S['base']], [per_prompt(s) for s in S['adapter']]
sb, sa = summ(B_), summ(A_)
def ratio(rows, i, d): t = sum(r[d] for r in rows); return sum(r[i] for r in rows) / t if t else None
rng = random.Random(20261108); D = {'answered': [], 'grounded': [], 'accuracy': [], 'brier': []}
for _ in range(2000):
    idx = [rng.randrange(len(B_)) for _ in B_]; bb = [B_[i] for i in idx]; aa = [A_[i] for i in idx]
    D['answered'].append(sum(r[0] for r in aa) / len(aa) - sum(r[0] for r in bb) / len(bb))
    for k, i, d in (('grounded', 2, 1), ('accuracy', 3, 1), ('brier', 4, 5)):
        x, y = ratio(aa, i, d), ratio(bb, i, d)
        if x is not None and y is not None: D[k].append(x - y)
ci = lambda v: (round(sorted(v)[int(0.025 * len(v))], 3), round(sorted(v)[int(0.975 * len(v)) - 1], 3)) if v else (None, None)
CI = {k: ci(v) for k, v in D.items()}
# plant test per class, from the training run's holdout output
cls_drop = {}
try:
    ho = json.load(open(W + '/holdout_eval.json')); hout = json.load(open(W + '/holdout_out.json'))
    kind = {i: k for i, k in c.execute("select id, cls from calib where id in (%s)" % ','.join(str(e['id']) for e in ho))}
    def right(txt, truth):
        try: return int(str(json.loads(re.search(r'\{.*?\}', txt, re.S).group(0)).get('verdict', '')).upper() == truth)
        except Exception: return 0
    acc = {}
    for arm in ('base', 'adapter'):
        for e, t in zip(ho, hout[arm]): acc.setdefault(kind.get(e['id']) or 'unlabelled', {}).setdefault(arm, []).append(right(t, e['truth']))
    for k, v in acc.items(): cls_drop[k] = {'n': len(v['base']), 'base': round(sum(v['base']) / len(v['base']), 3), 'adapter': round(sum(v['adapter']) / len(v['adapter']), 3)}
except Exception as e: log(f'per-class plant read skipped: {e}')
worse = [k for k in ('answered', 'grounded', 'accuracy') if CI[k][1] is not None and CI[k][1] < 0] + (['brier'] if CI['brier'][0] is not None and CI['brier'][0] > 0 else [])
drops = [k for k, v in cls_drop.items() if v['base'] - v['adapter'] > 0.10]
verdict = 'REAL_OK' if not worse and not drops else 'REAL_FAIL'
rec = {'ts': time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()), 'seat': seat, 'run': W, 'realjob': {'base': sb, 'adapter': sa, 'ci95_delta': CI, 'worse': worse,
       'plant_classes': cls_drop, 'class_drops': drops, 'verdict': verdict}}
json.dump(rec, open(W + '/realjob.json', 'w'), indent=1)
open(H + '/promotions.jsonl', 'a').write(json.dumps(rec) + '\n')
log(f"{seat}: {len(items)} real prompts · base {sb} -> adapter {sa} · CI95 {CI} · worse {worse} · plant class drops {drops} -> {verdict}")
