"""dream_job.py (r2) -- DREAMTIME r2 on the pod (call DREAMTIME_R2_CALL_20261007.txt, ee1b1634...). Every seat x language x digit rotation x arm (E, EP, L per pair; N, NP idle):
the HELD weighting over the digits 1 / 2 / 3 at the first position (nothing emitted) and a 3-token spoken answer. Greedy. Writes /workspace/out/held_<seat>.jsonl."""
import json, os, time, gc
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
OUT = '/workspace/out'; os.makedirs(OUT, exist_ok=True)
X = json.load(open('r2_texts.json')); T = json.load(open('translations.json')); PICK = json.load(open('pick.json')); EX = {x['id']: x for x in json.load(open('exam.json'))}
SEATS = {'en': 'unsloth/Meta-Llama-3.1-8B-Instruct', 'th': 'typhoon-ai/llama3.1-typhoon2-8b-instruct', 'eu': 'HiTZ/Latxa-Llama-3.1-8B-Instruct'}
def log(*a): open(f'{OUT}/job.log', 'a').write(time.strftime('%H:%M:%S ') + ' '.join(map(str, a)) + '\n')
def txt(p, L, part):
    if L == 'en': return EX[p + 'e']['reading'] if part == 'reading' else (EX[p + 'l'].get('rulers') or '')
    return T['cases'][p][part][L]
def user(L, arm, p=None):
    lab = X['labels']; r = X['neutral'][L] if arm in ('N', 'NP') else txt(p, L, 'reading'); s = lab['reading'][L] + r
    if arm in ('EP', 'NP'): s += '\n' + lab['rulers'][L] + X['filler'][L]
    if arm == 'L': s += '\n' + lab['rulers'][L] + txt(p, L, 'rulers')
    return s
JOBS = []
for L in ('en', 'th', 'eu'):
    for ri, rot in enumerate(X['rotations']):
        sysm = X['system'][L].format(c=rot['COMMIT'], h=rot['HOLD'], n=rot['NEXT'])
        for p in PICK:
            for arm in ('E', 'EP', 'L'): JOBS.append({'lang': L, 'rot': ri, 'arm': arm, 'pair': p, 'chat': [{'role': 'system', 'content': sysm}, {'role': 'user', 'content': user(L, arm, p)}]})
        for arm in ('N', 'NP'): JOBS.append({'lang': L, 'rot': ri, 'arm': arm, 'pair': None, 'chat': [{'role': 'system', 'content': sysm}, {'role': 'user', 'content': user(L, arm)}]})
log('jobs per seat', len(JOBS))
for seat, rid in SEATS.items():
    fn = f'{OUT}/held_{seat}.jsonl'
    if os.path.exists(fn): continue
    tok = AutoTokenizer.from_pretrained(rid); tok.padding_side = 'left'
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(rid, dtype=torch.bfloat16, device_map='cuda'); m.eval(); log('seat', seat, rid)
    dig = {d: tok('1' if d == '1' else d, add_special_tokens=False)['input_ids'][0] for d in ('1', '2', '3')}
    rows = []
    for i in range(0, len(JOBS), 16):
        B = JOBS[i:i + 16]; tx = [tok.apply_chat_template(j['chat'], tokenize=False, add_generation_prompt=True) for j in B]
        enc = tok(tx, return_tensors='pt', padding=True, add_special_tokens=False).to('cuda')
        with torch.no_grad():
            pr = torch.softmax(m(**enc).logits[:, -1, :].float(), -1)
            g = m.generate(**enc, max_new_tokens=3, do_sample=False, pad_token_id=tok.pad_token_id)
        for j, b in enumerate(B):
            rows.append({k: b[k] for k in ('lang', 'rot', 'arm', 'pair')} | {'seat': seat, 'held': {d: float(pr[j, t]) for d, t in dig.items()},
                         'spoken': tok.decode(g[j][enc['input_ids'].shape[1]:], skip_special_tokens=True).strip()})
    open(fn, 'w').write('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n')
    del m; gc.collect(); torch.cuda.empty_cache(); log('  done', seat)
log('ALL DONE'); open(f'{OUT}/DONE', 'w').write('ok')
