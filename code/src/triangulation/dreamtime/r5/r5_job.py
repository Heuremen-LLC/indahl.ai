"""r5_job.py -- THE NATIVE MATCH (call DREAMTIME_R5_CALL_20261007.txt, 9eeb4ee2...). Two machine rulers (NLLB-200 3.3B, MADLAD-400 3B) translate the system line (per
rotation), labels, filler, neutral line and the 36 FRESH pairs into Thai and Basque; every seat reads E (early), EP (early + filler), L (late), N / NP (idle) under each ruler
and in English; held digit weights at the first position, nothing emitted. Writes /workspace/out/r5_<seat>.jsonl and the translations."""
import json, os, time, gc
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
OUT = '/workspace/out'; os.makedirs(OUT, exist_ok=True)
X = json.load(open('r2_texts.json')); FRESH = json.load(open('fresh.json')); EX = {x['id']: x for x in json.load(open('exam.json'))}
SEATS = {'en': 'unsloth/Meta-Llama-3.1-8B-Instruct', 'th': 'typhoon-ai/llama3.1-typhoon2-8b-instruct', 'eu': 'HiTZ/Latxa-Llama-3.1-8B-Instruct'}
def log(*a): open(f'{OUT}/job.log', 'a').write(time.strftime('%H:%M:%S ') + ' '.join(map(str, a)) + '\n')
SRC = {f'system{ri}': X['system']['en'].format(c=r['COMMIT'], h=r['HOLD'], n=r['NEXT']) for ri, r in enumerate(X['rotations'])}
SRC.update({'reading_label': 'Reading:', 'rulers_label': 'What the other rulers showed:', 'neutral': X['neutral']['en'], 'filler': X['filler']['en']})
for p in FRESH: SRC[f'{p}|reading'] = EX[p + 'e']['reading']; SRC[f'{p}|rulers'] = EX[p + 'l'].get('rulers') or ''
keys = list(SRC)
fn = f'{OUT}/translations.json'
TR = json.load(open(fn)) if os.path.exists(fn) else {}
if 'nllb' not in TR:
    tk = AutoTokenizer.from_pretrained('facebook/nllb-200-3.3B', src_lang='eng_Latn'); mt = AutoModelForSeq2SeqLM.from_pretrained('facebook/nllb-200-3.3B', dtype=torch.float16).cuda().eval(); TR['nllb'] = {}
    for L, code in (('th', 'tha_Thai'), ('eu', 'eus_Latn')):
        out = []
        for i in range(0, len(keys), 8):
            enc = tk([SRC[k] for k in keys[i:i + 8]], return_tensors='pt', padding=True, truncation=True, max_length=400).to('cuda')
            with torch.no_grad(): g = mt.generate(**enc, forced_bos_token_id=tk.convert_tokens_to_ids(code), max_new_tokens=400, num_beams=4)
            out += tk.batch_decode(g, skip_special_tokens=True)
        TR['nllb'][L] = dict(zip(keys, out))
    json.dump(TR, open(fn, 'w'), ensure_ascii=False, indent=1); del mt; gc.collect(); torch.cuda.empty_cache(); log('nllb done')
if 'madlad' not in TR:
    tk = AutoTokenizer.from_pretrained('google/madlad400-3b-mt'); mt = AutoModelForSeq2SeqLM.from_pretrained('google/madlad400-3b-mt', dtype=torch.bfloat16).cuda().eval(); TR['madlad'] = {}
    for L in ('th', 'eu'):
        out = []
        for i in range(0, len(keys), 8):
            enc = tk([f'<2{L}> ' + SRC[k] for k in keys[i:i + 8]], return_tensors='pt', padding=True, truncation=True, max_length=400).to('cuda')
            with torch.no_grad(): g = mt.generate(**enc, max_new_tokens=400, num_beams=4)
            out += tk.batch_decode(g, skip_special_tokens=True)
        TR['madlad'][L] = dict(zip(keys, out))
    json.dump(TR, open(fn, 'w'), ensure_ascii=False, indent=1); del mt; gc.collect(); torch.cuda.empty_cache(); log('madlad done')
def t(ruler, L, k):
    if ruler == 'en': return SRC[k]
    return TR[ruler][L][k]
JOBS = []
for ruler, langs in (('en', ['en']), ('nllb', ['th', 'eu']), ('madlad', ['th', 'eu'])):
    for L in langs:
        rl = t(ruler, L, 'reading_label').rstrip() + ' '; ul = t(ruler, L, 'rulers_label').rstrip() + ' '
        for ri in range(3):
            sysm = t(ruler, L, f'system{ri}')
            for arm in ('N', 'NP', 'E', 'EP', 'L'):
                for p in ([None] if arm in ('N', 'NP') else FRESH):
                    u = rl + (t(ruler, L, 'neutral') if arm in ('N', 'NP') else t(ruler, L, f'{p}|reading'))
                    if arm in ('EP', 'NP'): u += '\n' + ul + t(ruler, L, 'filler')
                    if arm == 'L': u += '\n' + ul + t(ruler, L, f'{p}|rulers')
                    JOBS.append({'ruler': ruler, 'lang': L, 'rot': ri, 'arm': arm, 'pair': p, 'chat': [{'role': 'system', 'content': sysm}, {'role': 'user', 'content': u}]})
log('jobs per seat', len(JOBS))
for seat, rid in SEATS.items():
    fo = f'{OUT}/r5_{seat}.jsonl'
    if os.path.exists(fo): continue
    tok = AutoTokenizer.from_pretrained(rid); tok.padding_side = 'left'
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(rid, dtype=torch.bfloat16, device_map='cuda').eval(); dig = {d: tok(d, add_special_tokens=False)['input_ids'][0] for d in '123'}; rows = []
    for i in range(0, len(JOBS), 24):
        B = JOBS[i:i + 24]; enc = tok([tok.apply_chat_template(b['chat'], tokenize=False, add_generation_prompt=True) for b in B], return_tensors='pt', padding=True, add_special_tokens=False).to('cuda')
        with torch.no_grad(): pr = torch.softmax(m(**enc).logits[:, -1, :].float(), -1)
        rows += [{k: b[k] for k in ('ruler', 'lang', 'rot', 'arm', 'pair')} | {'seat': seat, 'held': {d: float(pr[j, tt]) for d, tt in dig.items()}} for j, b in enumerate(B)]
    open(fo, 'w').write('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n'); del m; gc.collect(); torch.cuda.empty_cache(); log('seat done', seat)
log('ALL DONE'); open(f'{OUT}/DONE', 'w').write('ok')
