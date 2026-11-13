#!/usr/bin/env python3
"""harvest.py (8 Nov): real-job training material for one seat, made on purpose instead of waiting for the council to drip it.
Granite's first adapter learned the plant test and got WORSE at the council's job (grounded 0.33 -> 0.13 on untrained council prompts).
So the training signal has to be the job itself: answer a seed from Sage's record with exact quotes and an honest p.
  1 PROMPTS  fresh R1 prompts built by the live builder (sage_flywheel.r1_prompt) from library pulls on harvest seeds. Never a council prompt,
             so the council's own prompts stay untrained and realjob_eval.py can still test on them.
  2 SAMPLE   the seat's MLX base (or its latest adapter, --from) answers each prompt K times at temperature 0.8. One GPU job; Mac lanes paused.
  3 CHECK    each answer: claims parsed by the live parser, exact-quote grounding by the live check, then q from a judge on Armature
             (qwen3:8b, a lab with no voice seat), in batches.
  4 KEEP     the best sample per prompt: only claims that are grounded AND q >= QMIN survive, each p set to its q (honest confidence), outcome kept.
             A prompt with no surviving claim keeps nothing (silence is not taught from a failure). Rows append to train/harvest/<seat>.jsonl.
Usage: harvest.py <seat> [n_prompts=48] [k=4] [--from <adapter_dir>]"""
import json, os, re, sys, time, random, hashlib, sqlite3, subprocess, fcntl, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import sage_flywheel as F, sage_v as V
PY = os.path.expanduser('~/sage-v/venv/bin/python')
args = [a for a in sys.argv[1:] if not a.startswith('--')]; ADP = sys.argv[sys.argv.index('--from') + 1] if '--from' in sys.argv else None
if ADP: args = [a for a in args if a != ADP]
seat = args[0]; N = int(args[1]) if len(args) > 1 else 48; K = int(args[2]) if len(args) > 2 else 4; QMIN = 0.7
base = json.load(open(H + '/seats.json'))['mlx_bases'][seat]
OUT = H + '/train/harvest'; os.makedirs(OUT, exist_ok=True); tag = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()); W = f'{OUT}/{seat.replace(":", "_")}_{tag}'; os.makedirs(W)
def log(m): print(m, flush=True); open(H + '/train/calib_train.log', 'a').write(time.strftime('%H:%M:%SZ ', time.gmtime()) + 'HARVEST ' + m + '\n')
# ---------- 1 PROMPTS ----------
c = sqlite3.connect(f'file:{H}/sage_v.db?mode=ro', uri=True, timeout=30)
council = {r[0] for r in c.execute('select prompt from prompts')}
seeds = list(V.SEEDS) + [r[0] for r in c.execute("select distinct seed from pq where demo=0 and seed is not null and seed != ''")]
HELD = set(json.load(open(H + f"/train/paired_{seat.replace(':', '_')}.json"))['held_out_seeds']) if os.path.exists(H + f"/train/paired_{seat.replace(':', '_')}.json") else set()
seeds = [s_ for s_ in seeds if s_ not in HELD]   # Sage 8 Nov: the paired set's seeds are never trained on
rng = random.Random(tag); system = V.voice_system(); items = []
for i in range(N * 3):
    if len(items) >= N: break
    seed = rng.choice(seeds); ch = F.pull(seed, 100000 + rng.randrange(10 ** 6))
    if len(ch) < 2: continue
    p = F.r1_prompt(seed, ch)
    if p in council: continue
    items.append({'seed': seed, 'prompt': p, 'chunks': [{'id': r['id'], 'text': r['text']} for r in ch]})
if len(items) < 8: log(f'{seat}: only {len(items)} prompts built; library unreachable?'); sys.exit(1)
json.dump({'system': system, 'items': items, 'k': K}, open(W + '/prompts.json', 'w'))
log(f'{seat}: {len(items)} fresh prompts x {K} samples from {base}' + (f' + adapter {ADP}' if ADP else ''))
# ---------- 2 SAMPLE (MLX, one GPU job) ----------
lk = open(H + '/.train.lock', 'w'); fcntl.flock(lk, fcntl.LOCK_EX)
open(H + '/PAUSE_MAC', 'w').write(f'harvest {seat}\n')
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
P = json.load(open("{W}/prompts.json")); model, tok = load("{base}", adapter_path={ADP!r})
ps = []
for it in P["items"]:
    t = tok.apply_chat_template([{{"role": "system", "content": P["system"]}}, {{"role": "user", "content": it["prompt"]}}], add_generation_prompt=True)
    ps += [t] * P["k"]
out = []
for i in range(0, len(ps), 8): out += batch_generate(model, tok, ps[i:i + 8], max_tokens=700, sampler=make_sampler(temp=0.8)).texts
json.dump(out, open("{W}/samples.json", "w"))
'''
open(W + '/gen.py', 'w').write(code)
try: r = subprocess.run([PY, W + '/gen.py'], capture_output=True, text=True); open(W + '/gen.log', 'w').write(r.stdout + r.stderr)
finally:
    try: os.remove(H + '/PAUSE_MAC')
    except FileNotFoundError: pass
    fcntl.flock(lk, fcntl.LOCK_UN); fcntl.flock(flk, fcntl.LOCK_UN)
if r.returncode != 0: log(f'{seat}: sampling failed rc {r.returncode}: {(r.stderr or "")[-300:]}'); sys.exit(1)
samples = json.load(open(W + '/samples.json'))
# ---------- 3 CHECK ----------
cands = []   # (item index, sample index, parsed json, claims)
for n, txt in enumerate(samples):
    i, s = divmod(n, K); it = items[i]
    try: j = json.loads(re.search(r'\{.*\}', txt, re.S).group(0))
    except Exception: continue
    cl = F.parse_claims(j.get('claims'), it['chunks'])
    if cl: cands.append((i, s, j, cl))
flat = [(ci, x) for ci, (_, _, _, cl) in enumerate(cands) for x in cl if x['grounded'] or x.get('cite_fault')]   # Sage (d): cite faults kept, id corrected by code below   # ungrounded claims are dropped without a judge call
JM, JH = 'qwen3:8b', V.ARM
for b in range(0, len(flat), 6):
    chunk = flat[b:b + 6]
    lines = '\n'.join(f"[{k}] CLAIM: {x['claim']}\n    QUOTE: \"{x['quote'][:300]}\"\n    CHUNK {x.get('true_chunk') or x['chunk']}: " +
                      next((F.around(r['text'], x['quote']) for r in items[cands[ci][0]]['chunks'] if r['id'] == (x.get('true_chunk') or x['chunk'])), '') for k, (ci, x) in enumerate(chunk))
    user = ("You are an EXTERNAL JUDGE. For each numbered claim, judge only from its chunk: is the claim right, and does the quote really say it? "
            "q is your probability (0 to 1) that the claim is right.\n\n" + lines + '\n\nJSON {"scores": [{"k": 0, "q": 0.0, "why": "one short reason"}]}')
    jj, raw, ms, cause = F.ask(JH, JM, "You are a strict external judge of claims against source text. Answer only JSON.", user, 700)
    for s_ in (jj or {}).get('scores', []) if isinstance(jj, dict) else []:
        try: chunk[int(s_['k'])][1]['q'] = max(0.0, min(1.0, float(s_['q'])))
        except Exception: pass
for ci, x in flat:   # Sage-ruled: second judge on every judged claim, document = the true chunk
    x['mc'] = V.mc_verdict(x['claim'], next((r['text'] for r in items[cands[ci][0]]['chunks'] if r['id'] == (x.get('true_chunk') or x['chunk'])), ''))
agree = lambda x: x.get('q') is not None and ((x.get('mc') == 'Yes' and x['q'] >= 0.5) or (x.get('mc') == 'No' and x['q'] < 0.5))
# ---------- 4 KEEP ----------
best = {}
for i, s, j, cl in cands:
    keep = [dict(x, chunk=x.get('true_chunk') or x['chunk']) for x in cl if (x['grounded'] or x.get('cite_fault')) and agree(x)]   # judges disagree -> excluded, never relabelled   # id set by code, never by a model   # 8 Nov review (Cerberus law, YO): keep low-q claims too, p = q, or p only ever learns 'high'
    score = sum(x['q'] for x in keep)
    if keep and score > best.get(i, (None, [], -1))[2]: best[i] = (j, keep, score)   # best sample = most judged-right quoted content
rows = []
for i, (j, keep, _) in best.items():
    tgt = {'claims': [{'claim': x['claim'], 'quote': x['quote'], 'chunk': x['chunk'], 'p': round(x['q'], 2)} for x in keep],
           'outcome': j.get('outcome') if j.get('outcome') in ('SUPPORTS', 'CONTRADICTS', 'CANNOT_TELL', 'UNLISTED') else 'SUPPORTS', 'next': str(j.get('next') or '')[:300]}
    rows.append({'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': items[i]['prompt']}, {'role': 'assistant', 'content': json.dumps(tgt)}]})
with open(f'{OUT}/{seat.replace(":", "_")}.jsonl', 'a') as f:
    for r_ in rows: f.write(json.dumps(r_) + '\n')
nc = sum(len(cl) for *_, cl in cands); ng = len(flat); nq = sum(1 for _, x in flat if (x.get('q') or 0) >= QMIN)
stats = {'seat': seat, 'prompts': len(items), 'samples': len(samples), 'parsed': len(cands), 'claims': nc, 'grounded': ng, 'grounded_q': nq, 'kept_prompts': len(rows), 'qmin': QMIN, 'from': ADP}
json.dump(stats, open(W + '/stats.json', 'w'), indent=1)
log(f"{seat}: {stats}")
