#!/usr/bin/env python3
"""seatC_carry_rulers.py -- TRIPLE PASS seat C. Read-only. 'IBM shots don't talk (-0.002 +- 0.002)' (ledger §151, LAWS_UPDATE_DRAFT Law 3),
re-read with the state-assignment ruler moved. Push runs 91-93 (ibm_pittsburgh), arm OFF|s10 (start |0>, ten X 30 us LAID apart), shots in the
order the payload stores them (the ledger's 'recorded order'); LAID inter-shot gap: 500 us repetition delay (+ the circuit).
Carry = P(next shot ends 1 | this shot ends 1) - P(next shot ends 1 | this shot ends 0), per readable qubit, mean over qubits; ends-1 by a cut on
the projected level at 0.5 (as the ledger) / 0.3 / 0.7; and the cut-free lag-1 correlation of the continuous level. Widths: SD over the three jobs / sqrt 3.
Writes only seatC_carry_rulers.txt beside this script."""
import hashlib, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); D = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/fire/ibm_pittsburgh'
OUT = os.path.join(HERE, 'seatC_carry_rulers.txt')


def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()


L = [f'# script sha256 {sha(os.path.abspath(__file__))}']
res = {}
for r in (91, 92, 93):
    z = np.load(os.path.join(D, f'run{r}_results.npz')); A = {k.split('__')[0]: np.asarray(z[k]).astype(complex) for k in z.files}
    L.append(f'# input run{r}_results.npz sha256 {sha(os.path.join(D, f"run{r}_results.npz"))}')
    c0 = A['OFF|p0'].mean(0); d = A['ON|p0'].mean(0) - c0; al = lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2
    sep = np.abs(d) / np.sqrt((np.abs(A['OFF|p0'] - c0) ** 2).mean(0) / 2); g = sep > 4
    for arm in ('OFF|s10', 'ON|s10', 'ON|n300'):
        x = al(A[arm])
        for cut in (0.3, 0.5, 0.7):
            b = x > cut; prev, nxt = b[:-1], b[1:]
            with np.errstate(invalid='ignore', divide='ignore'):
                p1 = (nxt & prev).sum(0) / prev.sum(0); p0 = (nxt & ~prev).sum(0) / (~prev).sum(0)
            ok = g & (prev.sum(0) >= 5) & ((~prev).sum(0) >= 5)
            res.setdefault((arm, f'cut {cut}'), []).append(np.nanmean((p1 - p0)[ok]))
        xc = x - x.mean(0); cor = (xc[:-1] * xc[1:]).mean(0) / xc.var(0)
        res.setdefault((arm, 'lag-1 correlation of the level (no cut)'), []).append(np.nanmean(cor[g]))
L.append("CARRY between consecutive shots [LAID gap 500 us + circuit], push runs 91-93, mean over readable qubits; each job, then mean (SD/sqrt3):")
for (arm, lab), v in res.items():
    v = np.array(v); L.append(f'   {arm:<8} {lab:<42} ' + '  '.join(f'{a:+.4f}' for a in v) + f'   | mean {v.mean():+.4f} ({v.std(ddof=1) / np.sqrt(3):.4f})')
open(OUT, 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
