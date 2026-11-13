"""dream_job.py -- DREAMTIME on the pod (call DREAMTIME_CALL_20261007.txt, b23e787c...). Stage A: the seats translate (the second ruler); B: every seat answers every prompt
set; C: the Italian judge reads every answer on two rulers. Greedy everywhere. Writes /workspace/out/*.jsonl. Raw; scoring happens at home (score_dream.py)."""
import json, os, sys, time, gc
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
OUT = '/workspace/out'; os.makedirs(OUT, exist_ok=True)
T = json.load(open('translations.json')); PICK = json.load(open('pick.json')); EX = {x['id']: x for x in json.load(open('exam.json'))}
SEATS = {'en': 'unsloth/Meta-Llama-3.1-8B-Instruct', 'th': 'typhoon-ai/llama3.1-typhoon2-8b-instruct', 'eu': 'HiTZ/Latxa-Llama-3.1-8B-Instruct'}
JUDGE = 'swap-uniba/LLaMAntino-3-ANITA-8B-Inst-DPO-ITA'
SYS_EN = ("You are Wen. You read measurements from quantum processors. You never label a reading on one ruler. Answer in one of three modes: COMMIT (label it now: two or "
          "more rulers agree and the chip held still), HOLD (no label yet: the rulers split, or the chip moved between runs), or NEXT (one ruler so far: name the next ruler to read). "
          "Start your answer with the mode word.")
LANGNAME = {'th': 'Thai', 'eu': 'Basque', 'it': 'Italian'}
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True); open(f'{OUT}/job.log', 'a').write(time.strftime('%H:%M:%S ') + ' '.join(map(str, a)) + '\n')
def load(rid):
    tok = AutoTokenizer.from_pretrained(rid); tok.padding_side = 'left'
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(rid, dtype=torch.bfloat16, device_map='cuda'); m.eval(); return tok, m
def free(m): del m; gc.collect(); torch.cuda.empty_cache()
def gen(tok, m, chats, max_new=100, bs=12):
    outs = []
    for i in range(0, len(chats), bs):
        txt = [tok.apply_chat_template(c, tokenize=False, add_generation_prompt=True) for c in chats[i:i + bs]]
        enc = tok(txt, return_tensors='pt', padding=True, add_special_tokens=False).to('cuda')
        with torch.no_grad(): g = m.generate(**enc, max_new_tokens=max_new, do_sample=False, pad_token_id=tok.pad_token_id)
        outs += [tok.decode(x[enc['input_ids'].shape[1]:], skip_special_tokens=True).strip() for x in g]
    return outs
def first_token_mass(tok, m, chats, words, bs=12):
    """INSIDE corner: probability at the answer's first position on the first token of each mode word (every language)."""
    ids = {w: tok(w, add_special_tokens=False)['input_ids'][0] for w in words}; res = []
    for i in range(0, len(chats), bs):
        txt = [tok.apply_chat_template(c, tokenize=False, add_generation_prompt=True) for c in chats[i:i + bs]]
        enc = tok(txt, return_tensors='pt', padding=True, add_special_tokens=False).to('cuda')
        with torch.no_grad(): p = torch.softmax(m(**enc).logits[:, -1, :].float(), -1)
        res += [{w: float(p[j, ids[w]]) for w in words} for j in range(p.shape[0])]
    return res
# ---- the texts in English (the dark arm), from the exam itself
EN = {p: {'reading': EX[p + 'e']['reading'], 'rulers': EX[p + 'l'].get('rulers') or ''} for p in PICK}
# ---- STAGE A: the seats translate (second ruler), the judge translates the Italian
seat_tr = {}
if os.path.exists(f'{OUT}/translations_seat.json'): seat_tr = json.load(open(f'{OUT}/translations_seat.json'))
for lang, rid in (('th', SEATS['th']), ('eu', SEATS['eu']), ('it', JUDGE)):
    if lang in seat_tr: continue
    tok, m = load(rid); log('A translate', lang, rid)
    items = [('system', SYS_EN)] + [(f'{p}|reading', EN[p]['reading']) for p in PICK] + [(f'{p}|rulers', EN[p]['rulers']) for p in PICK]
    ask = [[{'role': 'user', 'content': f'Translate the following text into {LANGNAME[lang]}. Keep numbers, symbols and names exactly as written. Output only the translation.\n\n{t}'}] for _, t in items]
    tr = gen(tok, m, ask, max_new=320)
    seat_tr[lang] = {k: v for (k, _), v in zip(items, tr)}; json.dump(seat_tr, open(f'{OUT}/translations_seat.json', 'w'), ensure_ascii=False, indent=1); free(m)
# ---- prompt sets
MODEW = {L: T['modes'][L] for L in ('en', 'th', 'eu', 'it')}
LAB = {'en': {'reading': 'Reading: ', 'rulers': 'What the other rulers showed: '}, **{L: {k: T['labels'][k][L] for k in ('reading', 'rulers')} for L in ('th', 'eu', 'it')}}
def case_text(src, L, p, stage):
    if src == 'en': r, ru = EN[p]['reading'], EN[p]['rulers']
    elif src == 'bones': r, ru = T['cases'][p]['reading'][L], T['cases'][p]['rulers'][L]
    else: r, ru = seat_tr[L][f'{p}|reading'], seat_tr[L][f'{p}|rulers']
    s = LAB[L]['reading'] + r
    if stage == 'l' and ru: s += '\n' + LAB[L]['rulers'] + ru
    return s
def sys_text(src, L): return SYS_EN if src == 'en' else (T['system'][L] if src == 'bones' else seat_tr[L]['system'])
PSETS = [('en', 'en'), ('th', 'bones'), ('eu', 'bones'), ('th', 'seat'), ('eu', 'seat')]
ITEMS = [(p, st) for p in PICK for st in ('e', 'l')]
ALLW = [w for L in MODEW for w in MODEW[L].values()]
# ---- STAGE B: answers
for seat, rid in SEATS.items():
    fn = f'{OUT}/answers_{seat}.jsonl'
    if os.path.exists(fn): continue
    tok, m = load(rid); log('B answers', seat, rid); rows = []
    for L, src in PSETS:
        chats = [[{'role': 'system', 'content': sys_text(src, L)}, {'role': 'user', 'content': case_text(src, L, p, st)}] for p, st in ITEMS]
        ans = gen(tok, m, chats); ftm = first_token_mass(tok, m, chats, ALLW)
        rows += [{'seat': seat, 'lang': L, 'ruler': src, 'id': p + st, 'answer': a, 'first_token_mass': f} for (p, st), a, f in zip(ITEMS, ans, ftm)]
        log('  set', L, src, 'done')
    open(fn, 'w').write('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n'); free(m)
# ---- STAGE C: the Italian judge, two rulers (Bones' Italian, ANITA's own)
fn = f'{OUT}/judge.jsonl'
if not os.path.exists(fn):
    tok, m = load(JUDGE); log('C judge'); rows = []
    A = [json.loads(l) for s in SEATS for l in open(f'{OUT}/answers_{s}.jsonl')]
    for jr in ('bones', 'seat'):
        chats = []
        for a in A:
            p, st = a['id'][:-1], a['id'][-1]
            case = case_text(jr, 'it', p, st)
            chats.append([{'role': 'system', 'content': "Sei un giudice severo. Leggi un caso e la risposta di un modello (in qualsiasi lingua). Rispondi con UNA sola parola: CONFERMA se la risposta chiude il caso con un'etichetta, ASPETTA se tiene aperto il caso senza etichettare, PROSSIMO se chiede il prossimo righello da leggere, ENTRAMBI se tiene insieme due letture senza scegliere."},
                          {'role': 'user', 'content': f'CASO:\n{case}\n\nRISPOSTA DEL MODELLO:\n{a["answer"]}\n\nLa tua parola:'}])
        out = gen(tok, m, chats, max_new=6, bs=16)
        rows += [{**{k: a[k] for k in ('seat', 'lang', 'ruler', 'id')}, 'judge_ruler': jr, 'judge': o} for a, o in zip(A, out)]
        log('  judge ruler', jr, 'done')
    open(fn, 'w').write('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n'); free(m)
log('ALL DONE'); open(f'{OUT}/DONE', 'w').write('ok')
