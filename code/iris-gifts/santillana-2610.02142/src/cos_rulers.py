#!/usr/bin/env python3
"""Known-good resolution for F2 (defined after the data): the row-8 cosine between the reproduced child and the parent under three rulers.
His section 6.6 prints 0.99999583 and norms 3.6246328 -> 3.6246383. Needs torch."""
import os, sys, numpy as np, torch, torch.nn.functional as F
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.abspath(os.path.join(H, '..')); sys.path.insert(0, H)
from pt_safe import PT
W = G + '/theirs/hf_weights/vision-1b-checks'
def tab(p):
    t = PT(p); sd = t.find_state_dict(); k = [x for x in sd if x.endswith('tok_emb.weight')][0]; return t.load(sd[k], as_float32=True)
P = tab(W + '/phase4a_v0_real_llm/llm_state_dict.pt'); A = tab(W + '/text_diag_repro_v0/text_diag_step_002202.pt'); a, b = A[8], P[8]
a64, b64 = a.astype(np.float64), b.astype(np.float64)
print('fp64:                       cosine %.8f | norms %.7f -> %.7f' % (a64 @ b64 / (np.linalg.norm(a64) * np.linalg.norm(b64)), np.linalg.norm(b64), np.linalg.norm(a64)))
print('numpy fp32 dot and norms:   cosine %.8f | norms %.7f -> %.7f' % (np.float32(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b)), np.linalg.norm(b), np.linalg.norm(a)))
ta, tb = torch.from_numpy(a.copy())[None], torch.from_numpy(b.copy())[None]
print('torch fp32 cosine_similarity: cosine %.8f | norms %.7f -> %.7f' % (F.cosine_similarity(ta, tb).item(), tb.norm().item(), ta.norm().item()))
print('torch fp32 .norm() of the whole table: %.7f and %.7f (fp64 sum of squares: %.6f and %.6f)' % (torch.from_numpy(P).norm().item(), torch.from_numpy(A).norm().item(), np.sqrt((P.astype(np.float64) ** 2).sum()), np.sqrt((A.astype(np.float64) ** 2).sum())))
