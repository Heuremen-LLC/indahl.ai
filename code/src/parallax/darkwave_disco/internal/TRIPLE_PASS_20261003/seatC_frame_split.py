#!/usr/bin/env python3
"""seatC_frame_split.py -- TRIPLE PASS seat C. Read-only. The spectator's 'free precession 3.144 deg/us' (look-time runs 101-103) split into the
part set by the drive frame (the maker's calibrated qubit frequency: a LAID reference) and the part set by its emitter in |1> (ZZ: WITNESS),
using the stopwatch run 81 (same role seed, same spectators): there the emitter-ON phase is read against the emitter-OFF arm of the same 60-us
window, so the frame cancels and only the emitter's pull remains. Per spectator: frame rate = look-time rate (emitter ON throughout) minus the
run-81 pull rate over the first 20 us of emitter-ON. Two jobs ~1-2 h apart: the frame can drift between them (named, not removed).
Writes only seatC_frame_split.txt beside this script."""
import hashlib, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); D = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/fire/ibm_pittsburgh'
RO = json.load(open('/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/reads/looktime_roles.json'))
WOF = {int(k): v for k, v in RO['witness_of'].items()}; OUT = os.path.join(HERE, 'seatC_frame_split.txt')


def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def frame(A, f0, f1):
    c0 = A[f0].mean(0); d = A[f1].mean(0) - c0
    return (lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2), np.abs(d) / np.sqrt((np.abs(A[f0] - c0) ** 2).mean(0) / 2)


def look_rates(r):
    z = np.load(os.path.join(D, f'run{r}_results.npz')); A = {k: np.asarray(z[k]).astype(complex) for k in z.files}
    al, sep = frame(A, 'F0__L1', 'F1__L1'); fin = lambda key: [k for k in A if k.startswith(key + '__')][-1]
    H = {a: (2 * al(A[fin(a + '|X')]).mean(0) - 1) - 1j * (2 * al(A[fin(a + '|Y')]).mean(0) - 1) for a in ('T0', 'T30')}
    ok = np.array([w in WOF and abs(H['T0'][w]) > 0.15 and sep[w] > 3 and sep[WOF[w]] > 3 for w in range(156)])
    return np.degrees(np.angle(H['T30'] / H['T0'])) / 30, ok


z = np.load(os.path.join(D, 'run81_results.npz')); A = {k: np.asarray(z[k]).astype(complex) for k in z.files}
al, sep = frame(A, 'F0__L1', 'F1__L1')
H81 = {a: (2 * al(A[f'{a}|X__L1']).mean(0) - 1) - 1j * (2 * al(A[f'{a}|Y__L1']).mean(0) - 1) for a in ('A0', 'A1', 'A2', 'A3')}
pull = np.degrees(np.angle(H81['A1'] / H81['A0'])) / 20                        # deg/us while the emitter is ON (first 20 us), frame cancelled
ok81 = np.array([abs(H81['A0'][w]) > 0.15 for w in range(156)])
rates = []; oks = []
for r in (101, 102, 103):
    v, ok = look_rates(r); rates.append(v); oks.append(ok)
tot = np.mean(rates, 0); okL = oks[0] & oks[1] & oks[2]
W = np.array([w for w in sorted(WOF) if okL[w] and ok81[w]], int)
fr = tot[W] - pull[W]
L = [f'# script sha256 {sha(os.path.abspath(__file__))}'] + [f'# input run{r}_results.npz sha256 {sha(os.path.join(D, f"run{r}_results.npz"))}' for r in (81, 101, 102, 103)]
L.append(f'SPECTATORS readable in both jobs: {len(W)}. Rates in deg per us of LAID time; median over spectators [quartiles].')
q = lambda v: f'{np.median(v):+.3f} [{np.percentile(v, 25):+.3f}, {np.percentile(v, 75):+.3f}]'
L.append(f'   total turn, look-time runs (emitter ON; frame + pull), signed:           {q(tot[W])}   |median| {np.median(np.abs(tot[W])):.3f}  (the claimed 3.144 is this |.| over the 83 read there)')
L.append(f'   pull alone, run 81 (emitter ON vs OFF, same window; frame cancels), signed: {q(pull[W])}   |median| {np.median(np.abs(pull[W])):.3f}')
L.append(f'   frame alone = total - pull, signed:                                    {q(fr)}   |median| {np.median(np.abs(fr)):.3f}')
L.append(f'   share of |total| carried by |frame| (median of |frame|/|total|): {np.median(np.abs(fr) / np.abs(tot[W])):.2f};  correlation total vs pull across spectators: {np.corrcoef(tot[W], pull[W])[0, 1]:+.2f}')
open(OUT, 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
