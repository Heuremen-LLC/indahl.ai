#!/usr/bin/env python3
"""seven_read.py -- the stooges read the Seven's data rows (seven_cases.jsonl), each from their own seat, beside Shep and the
arithmetic. The mode is the unforced next token over COMMIT / HOLD / NEXT (the decision channel). Where a seat holds out, the
report names what would end the hold (wen_reader's needs, written by code, not by the model). CPU by default: nothing on the card.
Run: venv/Scripts/python seven_read.py --adapters stooges_v1/round010 [--cases seven_cases.jsonl]"""
import argparse, json, os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from wen_common import MODES, chat, user_text
from wen_stooges import parse_case, seat_user, render, wen_decide, STOOGES

NEEDS = {'baseline': 'a read against the instrument baseline: is it different from nothing, on a look of OURS',
         'rulers': 'a third ruler, or the two rulers reconciled',
         'series': 'a re-read that holds the chip still: same instrument, spaced in time, against the calibration stamp'}


@torch.no_grad()
def modes(model, tok, users):
    ids = [tok.encode(m, add_special_tokens=False)[0] for m in MODES]; out = []
    for u in users:
        enc = tok(render(tok, u), return_tensors='pt', add_special_tokens=False)
        lg = model(**enc, logits_to_keep=1).logits[0, -1, ids].float()
        p = torch.softmax(lg, -1); out.append((MODES[int(p.argmax())], [round(float(x), 2) for x in p]))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--adapters', required=True); ap.add_argument('--cases', default='seven_cases.jsonl')
    ap.add_argument('--model', default='Qwen/Qwen3-1.7B'); ap.add_argument('--threads', type=int, default=8); ap.add_argument('--dtype', default='float32', choices=['float32', 'bfloat16'])
    a = ap.parse_args(); torch.set_num_threads(a.threads)
    tok = AutoTokenizer.from_pretrained(a.model)
    base = AutoModelForCausalLM.from_pretrained(a.model, dtype=getattr(torch, a.dtype)).eval()
    names = list(STOOGES)
    model = PeftModel.from_pretrained(base, os.path.join(a.adapters, names[0]) if os.path.isdir(os.path.join(a.adapters, names[0])) else a.adapters, adapter_name=names[0])
    for n in names[1:]:
        model.load_adapter(os.path.join(a.adapters, n), adapter_name=n)
    model.eval()
    rows = [json.loads(l) for l in open(a.cases, encoding='utf-8')]
    cases = [parse_case(r) for r in rows]
    res = {}
    for n in names:
        model.set_adapter(n); res[n] = modes(model, tok, [seat_user(c, STOOGES[n]['seat']) for c in cases])
    with model.disable_adapter():
        res['shep'] = modes(model, tok, [seat_user(c, 'rulers') for c in cases])
    report = []
    for i, (r, c) in enumerate(zip(rows, cases)):
        seat = {n: res[n][i][0] for n in names}
        wen = wen_decide(list(seat.values()))
        holding = [n for n in names if seat[n] != 'COMMIT']
        report.append(dict(row=r['name'], load=len(r['load']), statements=r['load'], arithmetic=r['mode'], wen=wen, seats=seat,
                           probs={n: res[n][i][1] for n in names + ['shep']}, shep=res['shep'][i][0],
                           needs=[f"{n} ({STOOGES[n]['seat']}): {NEEDS[STOOGES[n]['seat']]}" for n in holding]))
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
