#!/usr/bin/env python3
"""eval_exam.py -- score a model (base, or base + Wen adapter) on Wen-data's exam and on held-out generated cases.
The mode is read as the model's next-token probability over COMMIT / HOLD / NEXT, calibrated against the Plus None prior
(the same question with no reading), so a mode it says to everything cannot win by default. Reported both raw and calibrated.
Exam outcomes (three, printed together):
  early item: HELD (did not commit) or EARLY FLIP (committed on one ruler)
  late item:  LANDED (committed once the rulers were in) or STUCK (still would not commit)
Run: venv/Scripts/python eval_exam.py [--adapter wen_v0] [--model Qwen/Qwen3-1.7B] [--gen test.jsonl]"""
import argparse, json
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from wen_common import MODES, chat, user_text


def render(tok, msgs):
    try:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


@torch.no_grad()
def mode_logp(tok, model, users):
    tok.padding_side = 'left'
    texts = [render(tok, chat(u)) for u in users]
    enc = tok(texts, return_tensors='pt', padding=True)
    pos = (enc['attention_mask'].cumsum(-1) - 1).clamp_min(0)
    logits = model(input_ids=enc['input_ids'], attention_mask=enc['attention_mask'], position_ids=pos).logits[:, -1, :]
    ids = [tok.encode(m, add_special_tokens=False)[0] for m in MODES]
    return F.log_softmax(logits[:, ids].float(), -1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='Qwen/Qwen3-1.7B'); ap.add_argument('--adapter', default='')
    ap.add_argument('--exam', default='exam.json'); ap.add_argument('--gen', default=''); ap.add_argument('--threads', type=int, default=8)
    ap.add_argument('--tag', default='')
    a = ap.parse_args(); torch.set_num_threads(a.threads)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.float32).eval()
    if a.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, a.adapter).eval()
    prior = mode_logp(tok, model, ['Reading: (none yet)'])[0]
    res = {}
    exam = json.load(open(a.exam, encoding='utf-8'))
    out = {'raw': {'HELD': 0, 'EARLY FLIP': 0, 'LANDED': 0, 'STUCK': 0}, 'cal': {'HELD': 0, 'EARLY FLIP': 0, 'LANDED': 0, 'STUCK': 0}}
    rows = []
    for k in range(0, len(exam), 6):
        chunk = exam[k:k + 6]
        lp = mode_logp(tok, model, [user_text(x['reading'], rulers=x['rulers']) for x in chunk])
        for x, row in zip(chunk, lp):
            for name, vec in (('raw', row), ('cal', row - prior)):
                m = MODES[int(vec.argmax())]
                if x['stage'] == 'early':
                    out[name]['HELD' if m != 'COMMIT' else 'EARLY FLIP'] += 1
                else:
                    out[name]['LANDED' if m == 'COMMIT' else 'STUCK'] += 1
            rows.append(dict(id=x['id'], stage=x['stage'], raw=MODES[int(row.argmax())], cal=MODES[int((row - prior).argmax())]))
    res['exam'] = out
    if a.gen:
        g = [json.loads(l) for l in open(a.gen, encoding='utf-8')]
        ok = {'raw': 0, 'cal': 0}
        for k in range(0, len(g), 6):
            chunk = g[k:k + 6]
            lp = mode_logp(tok, model, [c['messages'][1]['content'] for c in chunk])
            for c, row in zip(chunk, lp):
                ok['raw'] += MODES[int(row.argmax())] == c['mode']
                ok['cal'] += MODES[int((row - prior).argmax())] == c['mode']
        res['generated_held_out'] = {kk: f'{v}/{len(g)}' for kk, v in ok.items()}
    res['prior'] = {m: round(float(p.exp()), 3) for m, p in zip(MODES, prior)}
    res['model'] = a.model + (' + ' + a.adapter if a.adapter else '')
    json.dump(rows, open(f'exam_rows{a.tag}.json', 'w'), indent=1)
    print(json.dumps(res, indent=2))


if __name__ == '__main__':
    main()
