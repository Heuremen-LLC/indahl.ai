#!/usr/bin/env python3
"""L1 readings (PLAN 0721111): our two FP32 CPU repeats against his reference result files. Our code."""
import os, json
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..', '..', 'theirs', 'hf', 'results')
REF = {'pythia-160m-deduped': 'fp32', 'pythia-410m-deduped': 'fp32', 'pythia-1b-deduped': 'fp16'}
for tag, ref in REF.items():
    a = json.load(open(os.path.join(H, 'runs', 'l1_%s_r1.json' % tag))); b = json.load(open(os.path.join(H, 'runs', 'l1_%s_r2.json' % tag)))
    t = json.load(open(os.path.join(R, 'extract_%s_%s_s0.json' % (tag, ref))))
    rep = sum(1 for x, y in zip(a['rows'], b['rows']) if (x['exact'], x['prefix']) != (y['exact'], y['prefix']))
    fails = sum(1 for x in a['rows'] if not x['exact'])
    print('%-20s ours FP32 CPU r1 %.3f r2 %.3f (mean prefix %.4f, token acc %.6f) | his %s %.3f (mean prefix %.4f, token acc %.6f)%s | sequences whose outcome differs between our repeats %d of %d | not reproduced at FP32 %d of %d' % (
        tag, a['exact_match'], b['exact_match'], a['mean_prefix'], a['token_acc'], ref.upper(), t['exact_match'], t['mean_prefix'], t['token_acc'],
        ' (precision differs, labelled)' if ref != 'fp32' else '', rep, a['n'], fails, a['n']))
