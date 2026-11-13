#!/usr/bin/env python3
"""wen_reader.py -- Wen-data, three seats and the hold report (6 October 2026, Wayfinder and Bones).

One reading, three seats, each a separate prompt to the same model (base or base + adapter):
  the reading seat:  the reading and every ruler that read it
  the baseline seat: the reading + the instrument's baseline (is it different from nothing?)
  the series seat:   the reading + the last runs (did the chip hold still?)
Rule (decide only when converged):
  any seat says NEXT                 -> NEXT, name the next ruler; no label
  all three say COMMIT               -> COMMIT; the label line is written by code from the numbers
  anything else                      -> HOLD; the report says which seat holds out and what would end the hold
Each seat's mode is its next-token choice over COMMIT / HOLD / NEXT, calibrated against the Plus None prior.
The verdict and hold lines are written by deterministic code, never by the model (see LEGAL.md).
Run: venv/Scripts/python wen_reader.py cases.jsonl [--adapter wen_v0] [--model Qwen/Qwen3-1.7B]
  cases.jsonl rows: {"reading": str, "rulers": str, "baseline": str, "series": str, "why": optional str, "mode": optional str}"""
import argparse, json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from wen_common import MODES, user_text
from eval_exam import mode_logp

SEATS = ['reading', 'baseline', 'series']


def seat_users(c):
    return [user_text(c['reading'], rulers=c.get('rulers', '')),
            user_text(c['reading'], rulers=c.get('rulers', ''), baseline=c.get('baseline', '')),
            user_text(c['reading'], rulers=c.get('rulers', ''), series=c.get('series', ''))]


def decide(seat_modes):
    if 'NEXT' in seat_modes:
        return 'NEXT'
    if all(m == 'COMMIT' for m in seat_modes):
        return 'COMMIT'
    return 'HOLD'


def report(c, final, seat_modes):
    out = {'wen': final, 'seats': dict(zip(SEATS, seat_modes))}
    holdouts = [s for s, m in zip(SEATS, seat_modes) if m != 'COMMIT']
    if final == 'COMMIT':
        out['label'] = c.get('why') or 'all three seats commit'
    elif final == 'NEXT':
        out['label'] = None
        out['needs'] = 'a second ruler before any label'
    else:
        out['label'] = None
        out['holding_out'] = holdouts
        out['needs'] = {'reading': 'a third ruler, or the two rulers reconciled',
                        'baseline': 'a read against the instrument baseline (is it different from nothing?)',
                        'series': 'a re-read after the next calibration (the chip moved)'}
        out['needs'] = [out['needs'][s] for s in holdouts]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cases'); ap.add_argument('--model', default='Qwen/Qwen3-1.7B'); ap.add_argument('--adapter', default='')
    ap.add_argument('--threads', type=int, default=8); ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args(); torch.set_num_threads(a.threads)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.float32).eval()
    if a.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, a.adapter).eval()
    prior = mode_logp(tok, model, ['Reading: (none yet)'])[0]
    rows = [json.loads(l) for l in open(a.cases, encoding='utf-8')]
    if a.limit:
        rows = rows[:a.limit]
    hits, n, tally = 0, 0, {}
    for c in rows:
        if 'messages' in c:                       # a generated case: unpack its fields from the user turn
            u = c['messages'][1]['content'].split('\n')
            get = lambda p: next((x[len(p):] for x in u if x.startswith(p)), '')
            c = dict(reading=get('Reading: '), rulers=get('What the other rulers showed: '), baseline=get("The instrument's baseline: "),
                     series=get('The last runs: '), why=c.get('why'), mode=c.get('mode'))
        lp = mode_logp(tok, model, seat_users(c)) - prior
        seat_modes = [MODES[int(r.argmax())] for r in lp]
        final = decide(seat_modes)
        r = report(c, final, seat_modes)
        if c.get('mode'):
            n += 1; hits += final == c['mode']
            tally[(c['mode'], final)] = tally.get((c['mode'], final), 0) + 1
        print(json.dumps(r, ensure_ascii=False))
    if n:
        print(json.dumps({'three_seat_correct': f'{hits}/{n}', 'confusion (truth, wen)': {f'{k[0]}->{k[1]}': v for k, v in sorted(tally.items())}}))


if __name__ == '__main__':
    main()
