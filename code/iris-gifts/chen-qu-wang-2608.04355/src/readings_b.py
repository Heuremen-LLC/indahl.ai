#!/usr/bin/env python3
"""D1b, D2b, D4b of PLAN.md Addendum 1 (2bec264, committed before this ran; defined after the data). Our code; no reply text printed."""
import os, sys, json
import numpy as np
from scipy import stats
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from common import load_jsonl, is_bad, category, decompose, cell_path, DATA
from cells import CELLS
from tokenizers import Tokenizer
cells = list(CELLS)
ST = json.load(open(os.path.join(DATA, 'stats_tests.json')))['cells']
def key(lab):
    return os.path.basename(cell_path(lab))[len('stage2_'):-len('.jsonl')]
print('D1b per cell: helpful, harmful, exact McNemar p, and their bootstrap interval on the content margin (stats_tests.json)')
for lab in cells:
    d = decompose(load_jsonl(cell_path(lab))); b, c = d['helpful'], d['harmful']; m = b + c
    p = 1.0 if m == 0 else min(1.0, 2 * stats.binom.cdf(min(b, c), m, 0.5))
    ci = ST.get(key(lab), {}).get('ci', {}).get('delta_content')
    print('  %-24s helpful %2d harmful %2d | margin %+.4f | exact p %s | their bootstrap %s' % (lab, b, c, d['d_content'], ('%.3g' % p) if m else 'no discordant rows', ('[%+.4f, %+.4f]' % tuple(ci)) if ci else 'not in file'))
tok = Tokenizer.from_file(os.path.join(H, '..', 'tok', '0.8B', 'tokenizer.json')); CAP = {'mcq': 896, 'open': 1024, 'code': 512}
print('\nD2b the cap contrast by task kind, Qwen cells (at cap = re-encoded length at least cap minus 3)')
acc = {}
for lab in cells:
    if lab.startswith('Gemma'): continue
    rows = load_jsonl(cell_path(lab)); kind = rows[0]['kind']; cap = CAP[kind]; A = acc.setdefault(kind, [0, 0, 0, 0, 0, 0])
    for r in rows:
        la = len(tok.encode(r['a0_text'], add_special_tokens=False).ids) >= cap - 3; ba = is_bad(r['a0_answer'])
        A[0] += ba; A[1] += ba and la; A[2] += not ba; A[3] += (not ba) and la
        bf = is_bad(r['yf_answer'])
        if bf: A[4] += 1; A[5] += len(tok.encode(r['yf_text'], add_special_tokens=False).ids) >= cap - 3
for kind, A in sorted(acc.items()):
    print('  %-4s first answers: unparseable %d, at cap %d | parsed %d, at cap %d || final answers: unparseable %d, at cap %d' % (kind, *A))
T = [sum(acc[k][i] for k in acc if k != 'code') for i in range(6)]
print('  text cells together: unparseable first answers %d, at cap %d | parsed %d, at cap %d | unparseable final answers %d, at cap %d' % tuple(T))
print('\nD4b median closure over the cells where it is defined')
cmap = {"2B ARC": "2b_arc", "4B ARC": "4b_arc", "0.8B MMLU": "0.8b_mmlu", "2B MMLU": "2b_mmlu", "4B TruthfulQA-MC1": "4b_truthfulqa_mc1", "9B ARC": "9b_arc",
        "9B GSM8K": "9b_gsm8k", "9B MMLU": "9b_mmlu", "4B CommonsenseQA": "4b_commonsenseqa", "4B MMLU": "4b_mmlu", "4B GSM8K": "4b_gsm8k",
        "0.8B ARC": "0.8b_arc", "0.8B GSM8K": "0.8b_gsm8k", "2B GSM8K": "2b_gsm8k"}
CL = {}
for lab, k in cmap.items():
    c = load_jsonl(os.path.join(DATA, 'constrained', 'constrained_qwen35_%s.jsonl' % k)); s2 = decompose(load_jsonl(os.path.join(DATA, 'stage2_qwen35_%s.jsonl' % k)))
    o = sum(r['yf_correct_original'] - r['a0_correct_original'] for r in c) / len(c); q = sum(r['yf_correct_constrained'] - r['a0_correct_constrained'] for r in c) / len(c)
    CL[lab] = (1 - abs(q - s2['d_content']) / abs(o - s2['d_content'])) if abs(o - s2['d_content']) > 1e-12 else None
dfn = {l: v for l, v in CL.items() if v is not None}
print('  closure undefined (zero denominator): %s | defined on %d cells, median %.1f%%, mean %.1f%%' % ([l for l, v in CL.items() if v is None], len(dfn), 100 * np.median(list(dfn.values())), 100 * np.mean(list(dfn.values()))))
