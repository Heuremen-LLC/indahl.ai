#!/usr/bin/env python3
"""F2 of PLAN.md Addendum 1 (1017b71, corrected before any factorial file was read): his section 6.6 drift statistics per arm against the
parent. Tables read with scout/pt_safe.py. usage: drift.py [ARM ...]; with no arm, the child known-good only."""
import os, sys
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.abspath(os.path.join(H, '..')); sys.path.insert(0, H)
from pt_safe import PT
W = G + '/theirs/hf_weights/vision-1b-checks'
ARMS = {'child': W + '/text_diag_repro_v0/text_diag_step_002202.pt', **{a: W + '/f3_factorial_v0/%s/text_diag_step_002202.pt' % a for a in ('narrow_highlr', 'narrow_lowlr', 'diverse_lowlr', 'diverse_highlr_seed42', 'diverse_highlr_seed43')}}
def table(path):
    t = PT(path); sd = t.find_state_dict(); k = [x for x in sd if x.endswith('tok_emb.weight')]; assert len(k) == 1, k
    return t.load(sd[k[0]], as_float32=True), sd[k[0]].ref.dtype
def bf16_rne(f):
    u = f.view(np.uint32).astype(np.uint64); return ((u + 0x7FFF + ((u >> 16) & 1)) >> 16).astype(np.uint16)
P, pdt = table(W + '/phase4a_v0_real_llm/llm_state_dict.pt'); P64 = P.astype(np.float64)
base = list(range(1000, 20001, 1000)); assert len(base) == 20
cos = lambda a, b: float(np.dot(a.astype(np.float64), b.astype(np.float64)) / (np.linalg.norm(a.astype(np.float64)) * np.linalg.norm(b.astype(np.float64))))
fro = lambda x: float(np.sqrt((x.astype(np.float64) ** 2).sum()))
print('parent %s, stored %s, table %s, Frobenius %.6f (fp64 sum of squares)' % ('phase4a_v0_real_llm', pdt, P.shape, fro(P)))
for arm in (sys.argv[1:] or ['child']):
    A, adt = table(ARMS[arm]); assert A.shape == P.shape
    d = np.abs(A.astype(np.float64) - P64); bc = [cos(A[i], P[i]) for i in base]
    print('%-22s stored %-16s | row 8 cosine %.8f, norm %.7f -> %.7f (%+.2e%%) | 20 baseline rows mean cosine %.8f, min %.8f | mean |drift| %.3g, max %.3g | Frobenius %.6f -> %.6f (relative %+.1e) | equal as stored %.1f%%, equal after bf16 rounding of both %.1f%%' % (
        arm, adt, cos(A[8], P[8]), np.linalg.norm(P[8].astype(np.float64)), np.linalg.norm(A[8].astype(np.float64)), 100 * (np.linalg.norm(A[8].astype(np.float64)) / np.linalg.norm(P[8].astype(np.float64)) - 1),
        np.mean(bc), np.min(bc), d.mean(), d.max(), fro(P), fro(A), fro(A) / fro(P) - 1, 100 * float((A == P).mean()), 100 * float((bf16_rne(A) == bf16_rne(P)).mean())), flush=True)
