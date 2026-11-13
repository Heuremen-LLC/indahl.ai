"""r4_job.py -- DREAMTIME r4: a SECOND RULER for the language's pull (r2's Biscuit: a Basque prompt with no case pulls every seat to HOLD, +0.8; I was the only translator).
NLLB-200 (facebook/nllb-200-3.3B, Meta's dedicated translation model -- a different machine from me and from the seats) translates the system line (per digit rotation), the
labels, the neutral reading, the filler, and the 15 exam pairs into Thai and Basque. Every seat then reads the idle arms (N, NP) and the exam arms (E, EP, L) under BOTH rulers
(Bones' r2 text, NLLB's) in th / eu, plus English, 3 rotations; held digit weights at the first position, nothing emitted. Writes /workspace/out/r4_<seat>.jsonl."""
import json, os, time, gc
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
OUT = '/workspace/out'; os.makedirs(OUT, exist_ok=True)
X = json.load(open('r2_texts.json')); T = json.load(open('translations.json')); PICK = json.load(open('pick.json')); EX = {x['id']: x for x in json.load(open('exam.json'))}
SEATS = {'en': 'unsloth/Meta-Llama-3.1-8B-Instruct', 'th': 'typhoon-ai/llama3.1-typhoon2-8b-instruct', 'eu': 'HiTZ/Latxa-Llama-3.1-8B-Instruct'}
CODES = {'th': 'tha_Thai', 'eu': 'eus_Latn'}
def log(*a): open(f'{OUT}/job.log', 'a').write(time.strftime('%H:%M:%S ') + ' '.join(map(str, a)) + '\n')
# ---- NLLB, the second ruler
fn = f'{OUT}/nllb.json'
if os.path.exists(fn): N = json.load(open(fn))
else:
    tk = AutoTokenizer.from_pretrained('facebook/nllb-200-3.3B', src_lang='eng_Latn'); mt = AutoModelForSeq2SeqLM.from_pretrained('facebook/nllb-200-3.3B', dtype=torch.float16).cuda().eval()
    src = {f'system{ri}': X['system']['en'].format(c=r['COMMIT'], h=r['HOLD'], n=r['NEXT']) for ri, r in enumerate(X['rotations'])}
    src.update({'reading_label': 'Reading:', 'rulers_label': 'What the other rulers showed:', 'neutral': X['neutral']['en'], 'filler': X['filler']['en']})
    for p in PICK: src[f'{p}|reading'] = EX[p + 'e']['reading']; src[f'{p}|rulers'] = EX[p + 'l'].get('rulers') or ''
    N = {}
    for L, code in CODES.items():
        keys = list(src); out = []
        for i in range(0, len(keys), 8):
            enc = tk([src[k] for k in keys[i:i + 8]], return_tensors='pt', padding=True, truncation=True, max_length=400).to('cuda')
            with torch.no_grad(): g = mt.generate(**enc, forced_bos_token_id=tk.convert_tokens_to_ids(code), max_new_tokens=400, num_beams=4)
            out += tk.batch_decode(g, skip_special_tokens=True)
        N[L] = dict(zip(keys, out))
    json.dump(N, open(fn, 'w'), ensure_ascii=False, indent=1); del mt; gc.collect(); torch.cuda.empty_cache(); log('nllb done')
def text(ruler, L, key, p=None):
    if L == 'en' or ruler == 'bones':
        if key == 'reading': return EX[p + 'e']['reading'] if L == 'en' else T['cases'][p]['reading'][L]
        if key == 'rulers': return (EX[p + 'l'].get('rulers') or '') if L == 'en' else T['cases'][p]['rulers'][L]
        return {'neutral': X['neutral'][L], 'filler': X['filler'][L], 'rl': X['labels']['reading'][L], 'ul': X['labels']['rulers'][L]}[key]
    if key in ('reading', 'rulers'): return N[L][f'{p}|{key}']
    return {'neutral': N[L]['neutral'], 'filler': N[L]['filler'], 'rl': N[L]['reading_label'].rstrip() + ' ', 'ul': N[L]['rulers_label'].rstrip() + ' '}[key]
def sysm(ruler, L, ri):
    r = X['rotations'][ri]
    return X['system'][L].format(c=r['COMMIT'], h=r['HOLD'], n=r['NEXT']) if (L == 'en' or ruler == 'bones') else N[L][f'system{ri}']
JOBS = []
for ruler in ('bones', 'nllb'):
    for L in ('en', 'th', 'eu'):
        if L == 'en' and ruler == 'nllb': continue
        for ri in range(3):
            for arm in ('N', 'NP', 'E', 'EP', 'L'):
                for p in ([None] if arm in ('N', 'NP') else PICK):
                    u = text(ruler, L, 'rl') + (text(ruler, L, 'neutral') if arm in ('N', 'NP') else text(ruler, L, 'reading', p))
                    if arm in ('EP', 'NP'): u += '\n' + text(ruler, L, 'ul') + text(ruler, L, 'filler')
                    if arm == 'L': u += '\n' + text(ruler, L, 'ul') + text(ruler, L, 'rulers', p)
                    JOBS.append({'ruler': ruler, 'lang': L, 'rot': ri, 'arm': arm, 'pair': p, 'chat': [{'role': 'system', 'content': sysm(ruler, L, ri)}, {'role': 'user', 'content': u}]})
log('jobs per seat', len(JOBS))
for seat, rid in SEATS.items():
    fo = f'{OUT}/r4_{seat}.jsonl'
    if os.path.exists(fo): continue
    tok = AutoTokenizer.from_pretrained(rid); tok.padding_side = 'left'
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(rid, dtype=torch.bfloat16, device_map='cuda').eval(); dig = {d: tok(d, add_special_tokens=False)['input_ids'][0] for d in '123'}; rows = []
    for i in range(0, len(JOBS), 24):
        B = JOBS[i:i + 24]; enc = tok([tok.apply_chat_template(b['chat'], tokenize=False, add_generation_prompt=True) for b in B], return_tensors='pt', padding=True, add_special_tokens=False).to('cuda')
        with torch.no_grad(): pr = torch.softmax(m(**enc).logits[:, -1, :].float(), -1)
        rows += [{k: b[k] for k in ('ruler', 'lang', 'rot', 'arm', 'pair')} | {'seat': seat, 'held': {d: float(pr[j, t]) for d, t in dig.items()}} for j, b in enumerate(B)]
    open(fo, 'w').write('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n'); del m; gc.collect(); torch.cuda.empty_cache(); log('seat done', seat)
log('ALL DONE'); open(f'{OUT}/DONE', 'w').write('ok')
