#!/usr/bin/env python3
"""L1c, F2b, F2c of PLAN.md Addendum 3 (caec408, committed before this ran; defined after the data). Our code; tables read with pt_safe."""
import os, sys
import numpy as np
from scipy import stats
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.abspath(os.path.join(H, '..')); sys.path.insert(0, H)
from pt_safe import PT
print('L1c his printed intervals against the binomial quantiles of k/269 (2.5% and 97.5%)')
for nm, k, printed in (('600M, pass', 249, '[0.892, 0.955]'), ('parent, pass', 27, '[0.067, 0.138]'), ('child, pass', 258, '[0.933, 0.981]'), ('diverse/low, pass', 268, '[0.989, 1.000]'),
                       ('600M, well-formed on any row', 248, ''), ('parent, well-formed on any row', 5, ''), ('child, well-formed on any row', 256, '')):
    lo, hi = stats.binom.ppf(0.025, 269, k / 269) / 269, stats.binom.ppf(0.975, 269, k / 269) / 269
    print('  %-32s k %3d: [%.3f, %.3f]%s' % (nm, k, lo, hi, ('  printed %s' % printed) if printed else ''))
W = G + '/theirs/hf_weights/vision-1b-checks'
def tab(p):
    t = PT(p); sd = t.find_state_dict(); k = [x for x in sd if x.endswith('tok_emb.weight')][0]; return t.load(sd[k], as_float32=True).astype(np.float64)
P = tab(W + '/phase4a_v0_real_llm/llm_state_dict.pt'); Pn = np.linalg.norm(P, axis=1)
print('\nF2b row 8 among all 32,768 rows: fp64 cosine of each row to the parent; share of rows with a higher cosine (less moved than row 8)')
arms = {'child': W + '/text_diag_repro_v0/text_diag_step_002202.pt', **{a: W + '/f3_factorial_v0/%s/text_diag_step_002202.pt' % a for a in ('narrow_highlr', 'narrow_lowlr', 'diverse_lowlr', 'diverse_highlr_seed42', 'diverse_highlr_seed43')}}
for a, p in arms.items():
    A = tab(p); c = (A * P).sum(1) / (np.linalg.norm(A, axis=1) * Pn); c8 = c[8]
    print('  %-22s row 8 cosine %.8f | table median %.8f | rows less moved than row 8 (higher cosine): %.1f%% | rows with exactly cosine 1: %d' % (a, c8, np.median(c), 100 * float((c > c8).mean()), int((c == 1).sum())))
print('\nF2c his printed pair for the child (section 6.6): row 8 cosine 0.99999583 against his baseline mean 0.99999678; the row-8 cosine is %s the baseline mean, so row 8 moved %s than his baseline average' % (
    'below' if 0.99999583 < 0.99999678 else 'above', 'more' if 0.99999583 < 0.99999678 else 'less'))
