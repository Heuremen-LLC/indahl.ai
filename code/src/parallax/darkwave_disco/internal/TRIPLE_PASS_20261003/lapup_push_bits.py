#!/usr/bin/env python3
"""TRIPLE PASS seat A: two ledger-only Pittsburgh push-run numbers re-derived from the raw jobs (runs 91-93), read-only.
 (a) PAPER:223 / ledger §151: the OFF-start spread-arm crossing bit by bit (438 qubit-reads: mean, median, share above 0, per-read medians);
 (b) LAWS:17 / PAPER:239 / ledger §151: 'shots talking' -- the next shot of an arm ends ON more often after an ON ending than after an OFF one.
     Ruler here (mine, stated): each shot called ON when its level along the bit's OFF->ON line is > 0.5; lean = P(next ON | ON) - P(next ON | OFF),
     per bit, then the mean over readable bits; width = sd over 200 bootstrap redraws of bits. Not the ledger's own code (none is on disk).
Frame, readable rule and bookkeeping are the frozen reader's (code/readclose.py push_stats). Writes only lapup_push_bits.txt here."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SANDBOX = os.path.join(HERE, 'rerun', 'qubit_fifth_run')
sys.path.insert(0, SANDBOX)
import readclose as RC
L = []


def load(chip, run):
    d = os.path.join(SANDBOX, 'data', 'fire', chip)
    z = np.load(os.path.join(d, f'run{run}_results.npz'))
    return {k: np.asarray(z[k]).astype(complex) for k in z.files}


def lean(levels):            # levels: shots x bits, in recorded shot order
    on = levels > 0.5
    a, b = on[:-1], on[1:]
    n1 = a.sum(0); n0 = (~a).sum(0)
    p1 = np.where(n1 > 0, (b & a).sum(0) / np.maximum(n1, 1), np.nan)
    p0 = np.where(n0 > 0, (b & ~a).sum(0) / np.maximum(n0, 1), np.nan)
    return p1 - p0, a.mean(0)


rng = np.random.default_rng(20261003)
for chip, runs in (('ibm_pittsburgh', (91, 92, 93)), ('ibm_marrakesh', (141,)), ('ibm_kingston', (141,))):
    allO, meds = [], []
    L.append(f'== {chip} runs {runs}')
    for r in runs:
        A = load(chip, r)
        al, sep = RC.frame(A, 'OFF|p0__L1', 'ON|p0__L1'); g = sep > 4
        lv = {k.split('__')[0]: al(v).mean(0) for k, v in A.items()}
        q = np.clip(lv['ON|n300'], 0.02, 0.98) ** 0.1
        dO = (lv['OFF|s10'] - RC.book(np.zeros_like(q), q, 10))[g]
        allO.append(dO); meds.append(np.median(dO))
        for arm in ('OFF|s10', 'ON|s10', 'ON|n300'):
            x = al(A[arm + '__L1'])[:, g]
            d, share = lean(x)
            ok = np.isfinite(d)
            bs = [np.nanmean(d[ok][rng.integers(0, ok.sum(), ok.sum())]) for _ in range(200)]
            L.append(f'   run {r} {arm:<8} lag-1 lean (mine) {np.nanmean(d[ok]):+.4f} +- {np.std(bs):.4f} over {ok.sum()} bits; share of shots ending ON {np.mean(share):.2f}')
    O = np.concatenate(allO)
    L.append(f'   OFF s10 crossing bit by bit [OWN; LAID 30-us intervals]: {O.size} bit-reads, mean {O.mean():+.4f}, median {np.median(O):+.4f}, share > 0 {np.mean(O > 0):.2f}; per-read medians ' + ' '.join(f'{m:+.4f}' for m in meds))
open(os.path.join(HERE, 'lapup_push_bits.txt'), 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
