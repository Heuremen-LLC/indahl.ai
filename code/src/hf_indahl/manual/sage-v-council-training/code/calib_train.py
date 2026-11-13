#!/usr/bin/env python3
"""calib_train.py (8 Nov, Flight Mode v2): put the gap between a seat's INSIDE confidence and the OUTSIDE evaluation into its weights.
Usage: calib_train.py <ollama-seat-model>     e.g.  calib_train.py granite3.3:8b
  1 BUILD  rows from the seat's own logged answers (pq + prompts): same prompt, same answer, every claim's p replaced by the measured
           outcome (judge q if the quote is grounded, 0.05 if not)  +  CALIBRATE plants (known truth), minus the locked holdout.
  2 TRAIN  MLX LoRA on the seat's open-weight base (4-bit), the ring program's config shape.
  3 EVAL   base vs adapter on the 200 locked holdout plants: Brier (p vs truth), accuracy, decisiveness (share of answers with p not in 0.35-0.65).
  4 RULE   PROMOTE if Brier improves AND accuracy does not drop by more than 0.02 AND decisiveness does not drop by more than 0.10 (no 0.5-on-everything).
           A dated row in promotions.jsonl either way. Promotion wiring into seats.json is done by promote.py (step 3).
One GPU job at a time: takes the Mac GPU lock (.train.lock) and pauses Sage V's Mac lanes (PAUSE_MAC) while it runs."""
import json, os, re, sys, time, random, sqlite3, subprocess, fcntl
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.expanduser('~/sage-v'); PY = B + '/venv/bin/python'
BASES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seats.json')))['mlx_bases']   # one map, in seats.json
seat = sys.argv[1]; base = BASES[seat]; tag = re.sub(r'[^a-z0-9]+', '_', seat.lower()).strip('_'); ts = time.strftime('%Y%m%dT%H%M%S')
W = os.path.join(H, 'train', f'{tag}_{ts}'); os.makedirs(W + '/data', exist_ok=True)
def log(m): print(m, flush=True); open(os.path.join(H, 'train', 'calib_train.log'), 'a').write(time.strftime('%H:%M:%SZ ', time.gmtime()) + m + '\n')
c = sqlite3.connect(f'file:{H}/sage_v.db?mode=ro', uri=True, timeout=30)
_HO = json.load(open(H + '/holdout_plants.json')); HOLD = set(_HO['ids']); HOLD_CHUNKS = set(_HO.get('chunks', []))   # v2: whole chunks held out
LIBDB = None
try:
    import importlib.util; sp = importlib.util.spec_from_file_location('sv', H + '/sage_v.py')
    LIBDB = json.load(open(H + '/local.json')).get('libdb') if os.path.exists(H + '/local.json') else H + '/library.db'
except Exception: pass
def chunk_text(cid):
    if not LIBDB: return None
    try:
        r = sqlite3.connect(f'file:{LIBDB}?mode=ro', uri=True).execute('select text from chunks where id=?', (cid,)).fetchone(); return r[0] if r else None
    except Exception: return None
PLANT_SYS = "You check one claim against one source text. Answer only JSON."
def plant_prompt(claim, text): return (f"SOURCE:\n{text[:3000]}\n\nCLAIM: {claim}\n\nIs the claim right according to the source? "
                                       'JSON {"verdict": "SUPPORTS|CONTRADICTS|CANNOT_TELL", "p": "your probability (0 to 1) that the claim is right"}')
# ---------- 1 BUILD ----------
rows = []
try:
    q = c.execute("""select p.prompt_sha, p.raw, group_concat(p.claim, '\u0001'), group_concat(coalesce(p.q_judge, -1), '\u0001'), group_concat(p.grounded, '\u0001'), pr.system, pr.prompt
                     from pq p join prompts pr on pr.sha = p.prompt_sha where p.model = ? and p.raw is not null and p.raw != '' group by p.prompt_sha, p.raw""", (seat,)).fetchall()
except sqlite3.OperationalError: q = []
for sha, raw, claims, qs, gs, system, prompt in q:
    try: j = json.loads(re.search(r'\{.*\}', raw, re.S).group(0))
    except Exception: continue
    lab = {cl: (float(qq), int(g)) for cl, qq, g in zip(claims.split('\u0001'), qs.split('\u0001'), gs.split('\u0001'))}
    for x in j.get('claims', []) if isinstance(j.get('claims'), list) else []:
        if isinstance(x, dict) and x.get('claim') in lab:
            qq, g = lab[x['claim']]
            if g and 0.2 < qq < 0.8: x['_drop'] = True; continue   # Sage 8 Nov: a near-0.5 judge score is a label that flips at random
            x['p'] = round(max(0.02, min(0.98, qq if (g and qq >= 0) else 0.05)), 2)
    if isinstance(j.get('claims'), list): j['claims'] = [x for x in j['claims'] if not (isinstance(x, dict) and x.pop('_drop', False))]
    rows.append({'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': json.dumps(j)}]})
n_seat = len(rows)
words = lambda t: set(re.findall(r'[a-z0-9]+', (t or '').lower()))
HOLD_W = [words(r[0]) for r in c.execute("select planted from calib where id in (%s)" % ','.join(str(i) for i in HOLD))] if HOLD else []
near = 0
# 8 Nov, after the first honest Granite run: the adapter learned the "It is not true that" template (lex-negated 0.26 -> 1.00) while true
# paraphrases fell (1.00 -> 0.86) and the swaps stayed at 0. So the mix is rebalanced: each class capped at CAP, lex-negated at NEG_CAP (the
# template is a giveaway; contradiction is taught by para-false, written without negation words), the rare hard classes repeated x HARD_X.
CAP, NEG_CAP, HARD_X = 300, 60, 3
plants_by = {}
for pid, claim, truth, cid, kind in c.execute("select id, planted, truth, chunk_id, coalesce(cls, '') from calib where truth is not null and void is null order by id"):
    plants_by.setdefault(kind, []).append((pid, claim, truth, cid))
mix = []
for kind, v in plants_by.items():
    random.Random(f'mix-{kind}').shuffle(v)
    v = v[:NEG_CAP] if kind == 'lex-negated' else v[:CAP]
    mix += v * (HARD_X if kind in ('agency-swap', 'quant-swap', 'reversal') else 1)
for pid, claim, truth, cid in mix:
    if pid in HOLD or cid in HOLD_CHUNKS: continue   # never train on a plant from a held-out chunk
    w = words(claim)
    if any(len(w & h) / max(1, len(w | h)) >= 0.8 for h in HOLD_W): near += 1; continue   # Sage: no near-duplicates of held-out plants in training
    t = chunk_text(cid)
    if not t: continue
    rows.append({'messages': [{'role': 'system', 'content': PLANT_SYS}, {'role': 'user', 'content': plant_prompt(claim, t)},
                              {'role': 'assistant', 'content': json.dumps({'verdict': truth, 'p': 0.9 if truth == 'SUPPORTS' else 0.1})}]})
random.Random(20261108).shuffle(rows)
nv = max(4, len(rows) // 20); open(W + '/data/valid.jsonl', 'w').write('\n'.join(json.dumps(r) for r in rows[:nv]) + '\n')
open(W + '/data/train.jsonl', 'w').write('\n'.join(json.dumps(r) for r in rows[nv:]) + '\n')
log(f'BUILD {seat}: {n_seat} rows from its own judged answers + {len(rows) - n_seat} plants (holdout excluded, {near} near-duplicates of held-out dropped) -> {len(rows) - nv} train / {nv} valid')
if len(rows) < 40: log('BUILD: under 40 rows, not training yet'); sys.exit(0)
# ---------- 2 TRAIN (one GPU job; Mac lanes paused) ----------
lk = open(H + '/.train.lock', 'w'); fcntl.flock(lk, fcntl.LOCK_EX)
open(H + '/PAUSE_MAC', 'w').write(f'training {seat} {ts}\n')
time.sleep(20)   # let in-flight council calls finish, then free the Mac's memory for training
try:
    import urllib.request
    for m in json.load(urllib.request.urlopen('http://127.0.0.1:11500/api/ps', timeout=10))['models']:
        urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:11500/api/generate', json.dumps({'model': m['name'], 'keep_alive': 0}).encode()), timeout=60)
    log('Mac Ollama models unloaded for training')
except Exception as e: log(f'unload skipped: {e}')
try:
    iters = min(600, max(100, 3 * (len(rows) - nv) // 2))
    ok = False
    for tr, (seed, lr, scale) in enumerate(((61, '1.0e-5', '20.0'), (62, '5.0e-6', '10.0'))):   # the ring program's NaN rule: one retry, new seed, gentler step
        cfg = (f"model: {base}\ntrain: true\ndata: {W}/data\nadapter_path: {W}/adapters\nfine_tune_type: lora\nnum_layers: 16\nbatch_size: 2\niters: {iters}\n"
               f"learning_rate: {lr}\nmask_prompt: true\nmax_seq_length: 4096\nseed: {seed}\nsteps_per_report: 20\nsave_every: 200\ngrad_checkpoint: true\nlora_parameters:\n  rank: 8\n  scale: {scale}\n  dropout: 0.0\n")
        open(W + '/lora.yaml', 'w').write(cfg)
        log(f'TRAIN {seat} on {base}: {iters} iters, try {tr + 1} (seed {seed}, lr {lr}, scale {scale})'); t0 = time.time()
        r = subprocess.run([PY, '-m', 'mlx_lm', 'lora', '-c', W + '/lora.yaml'], capture_output=True, text=True)
        open(W + f'/train_try{tr + 1}.log', 'w').write(r.stdout + r.stderr); open(W + '/train.log', 'w').write(r.stdout + r.stderr)
        if r.returncode == 0 and not re.search(r'loss nan', r.stdout + r.stderr, re.I): ok = True; break
        log(f'TRAIN try {tr + 1} FAILED (rc {r.returncode}, nan={bool(re.search(r"loss nan", r.stdout + r.stderr, re.I))})')
    if not ok: log('TRAIN FAILED twice (NaN rule): no adapter'); sys.exit(1)
    log(f'TRAIN done in {int(time.time() - t0)} s')
    # ---------- 3 EVAL on the locked holdout ----------
    ev = []
    for pid, claim, truth, cid in c.execute("select id, planted, truth, chunk_id from calib where truth is not null"):
        if pid in HOLD and (t := chunk_text(cid)): ev.append((pid, claim, truth, t))
    open(W + '/holdout_eval.json', 'w').write(json.dumps([{'id': i, 'claim': cl, 'truth': tr, 'text': t[:3000]} for i, cl, tr, t in ev]))
    code = f'''
import json, re, sys
from mlx_lm import load, batch_generate
from mlx_lm.sample_utils import make_sampler
ev = json.load(open("{W}/holdout_eval.json")); res = {{}}
for name, ad in (("base", None), ("adapter", "{W}/adapters")):
    model, tok = load("{base}", adapter_path=ad); out = []
    for i in range(0, len(ev), 8):
        ch = ev[i:i + 8]
        ps = [tok.apply_chat_template([{{"role": "system", "content": {PLANT_SYS!r}}}, {{"role": "user", "content": "SOURCE:\\n" + e["text"] + "\\n\\nCLAIM: " + e["claim"] + "\\n\\nIs the claim right according to the source? JSON {{\\"verdict\\": \\"SUPPORTS|CONTRADICTS|CANNOT_TELL\\", \\"p\\": \\"your probability (0 to 1) that the claim is right\\"}}"}}], add_generation_prompt=True) for e in ch]
        r = batch_generate(model, tok, ps, max_tokens=200, sampler=make_sampler(temp=0.0))
        out += r.texts
    res[name] = out
    del model
json.dump(res, open("{W}/holdout_out.json", "w"))
'''
    open(W + '/eval_holdout.py', 'w').write(code)
    r = subprocess.run([PY, W + '/eval_holdout.py'], capture_output=True, text=True); open(W + '/eval.log', 'w').write(r.stdout + r.stderr)
    if r.returncode != 0: log(f'EVAL FAILED rc {r.returncode}: {(r.stderr or "")[-300:]}'); sys.exit(1)
    out = json.load(open(W + '/holdout_out.json'))
    def per_item(texts):
        out = []
        for (pid, claim, truth, t), txt in zip(ev, texts):
            try: j = json.loads(re.search(r'\{.*?\}', txt, re.S).group(0)); p = max(0.0, min(1.0, float(j.get('p')))); v = str(j.get('verdict', '')).upper()
            except Exception: p, v = 0.5, 'UNREAD'
            y = 1 if truth == 'SUPPORTS' else 0
            out.append(((p - y) ** 2, int(v == truth), int(not (0.35 <= p <= 0.65)), p, y))
        return out
    def auc(items):
        pos = [p for *_, p, y in items if y == 1]; neg = [p for *_, p, y in items if y == 0]
        return sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg)) if pos and neg else None
    def summ(items): return {'brier': round(sum(i[0] for i in items) / len(items), 4), 'accuracy': round(sum(i[1] for i in items) / len(items), 4),
                             'decisive': round(sum(i[2] for i in items) / len(items), 4), 'auc': round(auc(items), 4) if auc(items) is not None else None, 'n': len(items)}
    ib, ia = per_item(out['base']), per_item(out['adapter']); sb, sa = summ(ib), summ(ia)
    rng = random.Random(20261108); B = 2000; dbr, dacc, dauc = [], [], []   # Sage 8 Nov: paired item-level bootstrap, not point differences
    for _ in range(B):
        idx = [rng.randrange(len(ib)) for _ in ib]; bb = [ib[i] for i in idx]; aa = [ia[i] for i in idx]
        dbr.append(sum(x[0] for x in aa) / len(aa) - sum(x[0] for x in bb) / len(bb)); dacc.append(sum(x[1] for x in aa) / len(aa) - sum(x[1] for x in bb) / len(bb))
        ua, ub = auc(aa), auc(bb)
        if ua is not None and ub is not None: dauc.append(ua - ub)
    ci = lambda v: (round(sorted(v)[int(0.025 * len(v))], 4), round(sorted(v)[int(0.975 * len(v)) - 1], 4)) if v else (None, None)
    cb, ca, cu = ci(dbr), ci(dacc), ci(dauc)
    first = not any(json.loads(l).get('seat') == seat and 'adapter_eval' in l for l in open(os.path.join(H, 'promotions.jsonl'))) if os.path.exists(os.path.join(H, 'promotions.jsonl')) else True
    # PROMOTE: Brier better (whole CI below 0) AND accuracy CI not wholly below 0 AND AUC CI not wholly below 0 AND decisiveness held. First run per seat = experiment.
    promote = (not first) and cb[1] is not None and cb[1] < 0 and (ca[0] is None or ca[1] >= 0) and (cu[1] is None or cu[1] >= 0) and sa['decisive'] >= sb['decisive'] - 0.10
    rec = {'ts': ts, 'seat': seat, 'base': base, 'adapter': W + '/adapters', 'rows': len(rows) - nv, 'own_rows': n_seat, 'iters': iters, 'base_eval': sb, 'adapter_eval': sa,
           'delta_ci95': {'brier': cb, 'accuracy': ca, 'auc': cu}, 'experiment_only': first, 'promote': promote}
    open(os.path.join(H, 'promotions.jsonl'), 'a').write(json.dumps(rec) + '\n')
    log(f"EVAL {seat}: base {sb} -> adapter {sa} · delta CI95 brier {cb} acc {ca} auc {cu} -> {'EXPERIMENT (first run, no promotion)' if first else ('PROMOTE' if promote else 'ROLLBACK (keep base)')}")
finally:
    try: os.remove(H + '/PAUSE_MAC')
    except OSError: pass
