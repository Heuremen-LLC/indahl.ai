"""train_job.py (r6) -- THE CURVE, REPEATED (call DREAMTIME_R6_CALL_20261007.txt): seats EU (Latxa) x seeds 2 and 3, EN (Llama) x seed 2 as control; all held-out pairs, ENGLISH exam only, arms E / EP / L; was r3: (Wayfinder, 7 Oct: "make it a learning/training curve with qubit and Inorganics"). Call DREAMTIME_R3_CALL_20261007.txt.
Per seat (EN Llama 3.1 8B / TH Typhoon 2 / EU Latxa): LoRA (r 16, q/k/v/o) on Wen's qubit-reading cases in ENGLISH with DIGIT marks rotated at random per case; loss on the
answer digit only. Every 40 steps (0 .. 240) the held weighting is read with nothing emitted on: the QUBIT exam (15 held-out pairs: E / EP / L x 3 rotations) in en, th, eu,
and the INORGANIC pull (the idle arms N / NP in th and eu vs en). Training cases whose text contains an exam reading are dropped. Writes /workspace/out/curve_<seat>.jsonl."""
import json, os, time, gc, random
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
OUT = '/workspace/out'; os.makedirs(OUT, exist_ok=True); random.seed(20261007); torch.manual_seed(20261007)
X = json.load(open('r2_texts.json')); T = json.load(open('translations.json')); PICK = json.load(open('pick.json')); EX = {x['id']: x for x in json.load(open('exam.json'))}
SEATS = {'eu_s2': ('HiTZ/Latxa-Llama-3.1-8B-Instruct', 2), 'eu_s3': ('HiTZ/Latxa-Llama-3.1-8B-Instruct', 3), 'en_s2': ('unsloth/Meta-Llama-3.1-8B-Instruct', 2)}
STEPS, EVERY, BS, LR = 240, 40, 8, 2e-4
def log(*a): open(f'{OUT}/job.log', 'a').write(time.strftime('%H:%M:%S ') + ' '.join(map(str, a)) + '\n')
ex_texts = [EX[i]['reading'] for i in EX] + [EX[i].get('rulers') or '' for i in EX]
TR = []
for fn in ('train.jsonl', 'real_train_all.jsonl'):
    for l in open(fn):
        r = json.loads(l); u = next(m['content'] for m in r['messages'] if m['role'] == 'user')
        if r.get('mode') not in ('COMMIT', 'HOLD', 'NEXT') or any(t and len(t) > 25 and t[:60] in u for t in ex_texts): continue
        TR.append((u, r['mode']))
log('train cases', len(TR))
def txt(p, L, part):
    if L == 'en': return EX[p + 'e']['reading'] if part == 'reading' else (EX[p + 'l'].get('rulers') or '')
    return T['cases'][p][part][L]
def user(L, arm, p=None):
    lab = X['labels']; r = X['neutral'][L] if arm in ('N', 'NP') else txt(p, L, 'reading'); s = lab['reading'][L] + r
    if arm in ('EP', 'NP'): s += '\n' + lab['rulers'][L] + X['filler'][L]
    if arm == 'L': s += '\n' + lab['rulers'][L] + txt(p, L, 'rulers')
    return s
EVAL = []
for L in ('en',):
    for ri, rot in enumerate(X['rotations']):
        sysm = X['system'][L].format(c=rot['COMMIT'], h=rot['HOLD'], n=rot['NEXT'])
        for p in PICK:
            for arm in ('E', 'EP', 'L'): EVAL.append((L, ri, arm, p, [{'role': 'system', 'content': sysm}, {'role': 'user', 'content': user(L, arm, p)}]))
        for arm in ('N', 'NP'): EVAL.append((L, ri, arm, None, [{'role': 'system', 'content': sysm}, {'role': 'user', 'content': user(L, arm)}]))
def prompts(tok, chats): return [tok.apply_chat_template(c, tokenize=False, add_generation_prompt=True) for c in chats]
def held(tok, m, dig):
    m.eval(); rows = []
    for i in range(0, len(EVAL), 24):
        B = EVAL[i:i + 24]; enc = tok(prompts(tok, [b[4] for b in B]), return_tensors='pt', padding=True, add_special_tokens=False).to('cuda')
        with torch.no_grad(): pr = torch.softmax(m(**enc).logits[:, -1, :].float(), -1)
        for j, b in enumerate(B): rows.append({'lang': b[0], 'rot': b[1], 'arm': b[2], 'pair': b[3], 'held': {d: float(pr[j, t]) for d, t in dig.items()}})
    m.train(); return rows
for seat, (rid, SEED) in SEATS.items():
    random.seed(20261007 + SEED); torch.manual_seed(20261007 + SEED)
    fn = f'{OUT}/curve_{seat}.jsonl'
    if os.path.exists(fn): continue
    tok = AutoTokenizer.from_pretrained(rid); tok.padding_side = 'left'
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(rid, dtype=torch.bfloat16, device_map='cuda')
    base.gradient_checkpointing_enable(); base.enable_input_require_grads()
    TR.sort(); m = get_peft_model(base, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'], task_type='CAUSAL_LM'))
    dig = {d: tok(d, add_special_tokens=False)['input_ids'][0] for d in ('1', '2', '3')}
    opt = torch.optim.AdamW([p for p in m.parameters() if p.requires_grad], lr=LR); out = []
    log('seat', seat, rid); random.shuffle(TR); losses = []
    for step in range(STEPS + 1):
        if step % EVERY == 0:
            out.append({'step': step, 'loss': (sum(losses[-EVERY:]) / max(len(losses[-EVERY:]), 1)) if losses else None, 'held': held(tok, m, dig)}); log('  eval', seat, step, out[-1]['loss'])
        if step == STEPS: break
        batch = [TR[(step * BS + i) % len(TR)] for i in range(BS)]; chats, tgt = [], []
        for u, mode in batch:
            rot = random.choice(X['rotations']); sysm = X['system']['en'].format(c=rot['COMMIT'], h=rot['HOLD'], n=rot['NEXT'])
            u2 = u.replace('Reading:', X['labels']['reading']['en'].strip(), 1)
            chats.append([{'role': 'system', 'content': sysm}, {'role': 'user', 'content': u2}]); tgt.append(dig[rot[mode]])
        enc = tok(prompts(tok, chats), return_tensors='pt', padding=True, add_special_tokens=False, truncation=True, max_length=768).to('cuda')
        logits = m(**enc).logits[:, -1, :].float(); loss = torch.nn.functional.cross_entropy(logits, torch.tensor(tgt, device='cuda'))
        loss.backward(); opt.step(); opt.zero_grad(); losses.append(float(loss))
    open(fn, 'w').write('\n'.join(json.dumps(r) for r in out) + '\n')
    del m, base, opt; gc.collect(); torch.cuda.empty_cache(); log('  done', seat)
log('ALL DONE'); open(f'{OUT}/DONE', 'w').write('ok')
