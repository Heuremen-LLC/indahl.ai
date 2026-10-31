"""synth_keystone.py -- planted worlds through the UNCHANGED analyze_keystone.py readers (packed bit arrays in IBM's BitArray layout for
the S and P parts, counts for the C part). Kicks per qubit = the committed ibm_kingston table (unwrapped, per dose). Worlds:
  W0 null: no kick, no loss.          W1 stable: kick = committed table, no loss.   W2 drifted: kick = 0.7 x committed + N(0, 1 deg).
  W3 loss only: no kick, the look multiplies coherence by 0.9 (S, P) / 0.97 per clock qubit.   W4 both: committed kick and that loss.
In W1/W4 the truth is the committed table + N(0, 0.25 deg) (its own calibration noise); fresh table = truth + N(0, 0.15 deg). D carries a free precession N(0, 15 deg) per qubit (shared by D, M, MC,
MF); DE and ME a small residual N(0, 2 deg) (the echo refocuses it). Expected outcomes are written below BEFORE the run; mismatches are
listed one by one. Usage: synth_keystone.py [NDRAW] -> synth_results_keystone.text"""
import sys, os, json, itertools, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import keystone as K, analyze_keystone as A, pooters as PW
CHIP = os.environ.get('CHIP', 'ibm_kingston'); T = K.table(CHIP); S = [int(q) for q in T['S']]; PAIRS = [tuple(p) for p in T['pairs']]; SING = [int(q) for q in T['singles']]
K8 = K.committed_corr(CHIP, 8); K4 = K.committed_corr(CHIP, 4)
COH = {int(q): max(0.03, v[3]) for q, v in T['kicks_deg_per_readout'].items()}   # real coherences (floor 0.03; referee 31 Oct)
CLOCK = K.CLOCK.get(CHIP, (104, 105, 106))   # marrakesh: the plan's rule on the 31 Oct record (dry run)
def pack(B):
    """B: shots x nbits of 0/1 -> IBM BitArray bytes (big-endian bytes, bit k at byte nby-1-k//8, position k % 8)"""
    sh, nb = B.shape; nby = (nb + 7) // 8; P = np.zeros((sh, nby * 8), np.uint8); P[:, :nb] = B
    by = np.packbits(P.reshape(sh, nby, 8), axis=2, bitorder='little').reshape(sh, nby); return by[:, ::-1].copy()
_t = np.random.default_rng(1).integers(0, 2, (5, 21)); assert all((K.bits(pack(_t), k) == _t[:, k]).all() for k in range(21)), 'pack layout'

def world(name, rng):
    kick8 = {q: 0.0 for q in S}; kick4 = {q: 0.0 for q in S}; lam = 1.0; lamC = 1.0
    if name in ('W1', 'W4'):   # truth = the committed table + its own calibration noise (it was read from 2 x 1000 shots)
        kick8 = {q: K8[q] + rng.normal(0, 0.25) for q in S}; kick4 = {q: K4[q] + rng.normal(0, 0.25) for q in S}
    if name == 'W2':
        kick8 = {q: 0.7 * K8[q] + rng.normal(0, 1) for q in S}; kick4 = {q: 0.7 * K4[q] + rng.normal(0, 1) for q in S}
    if name in ('W3', 'W4'): lam, lamC = 0.9, 0.97
    fresh8 = {q: kick8[q] + rng.normal(0, 0.15) for q in S}; fresh4 = {q: kick4[q] + rng.normal(0, 0.15) for q in S}   # 4,000-shot calibration
    return dict(kick8=kick8, kick4=kick4, lam=lam, lamC=lamC, fresh8=fresh8, fresh4=fresh4)

def arm_phase(W, a, q, N, free):
    k = W['kick8' if N == 8 else 'kick4'][q]; corr = {'MC': (K8 if N == 8 else K4)[q], 'MF': W['fresh8' if N == 8 else 'fresh4'][q]}.get(a, 0.0)
    base = free['E'][q] if a in ('DE', 'ME') else free['D'][q]
    look = N * k if a in ('M', 'MC', 'MF') else 0.0          # the symmetric echo cancels a constant kick
    return np.radians(base + look - N * corr), (W['lam'] if a in ('M', 'MC', 'MF', 'ME') else 1.0)

def synth_S(W, free, rng, shots):
    Z = {}
    for a in K.ARMS:
        ph = np.array([arm_phase(W, a, q, 8, free)[0] for q in S]); lam = arm_phase(W, a, S[0], 8, free)[1]; c = np.array([COH[q] for q in S]) * lam
        tot = ph - np.pi / 2                                   # sx prepares phase -90 deg
        ev = {'X': c * np.cos(tot), 'Y': c * np.sin(tot), 'Z0': c * np.cos(ph)}   # Z0: sxdg maps the prepared axis back to +Z
        for st in K.SET_S:
            p1 = (1 - ev[st]) / 2; Z[(a, st)] = pack((rng.random((shots, len(S))) < p1).astype(np.uint8))
    return Z

def bell_probs(Phi, c, st):
    rho = np.zeros((4, 4), complex); rho[0, 0] = rho[3, 3] = 0.5; rho[0, 3] = 0.5 * c * np.exp(-1j * Phi); rho[3, 0] = np.conj(rho[0, 3])
    R = {'X': np.array([[1, 1], [1, -1]]) / np.sqrt(2), 'Y': np.array([[1, 1], [1, -1]]) / np.sqrt(2) @ np.diag([1, -1j]), 'Z': np.eye(2)}
    U = np.kron(R[st[0]], R[st[1]]); return np.real(np.diag(U @ rho @ U.conj().T)).clip(0)   # index = 2 b_a + b_c
def synth_P(W, free, rng, shots):
    Z = {}
    for a in K.ARMS:
        lam = arm_phase(W, a, S[0], 4, free)[1]
        for st in K.SET_P:
            B = np.zeros((shots, 2 * len(PAIRS) + len(SING)), np.uint8)
            for i, (x, y) in enumerate(PAIRS):
                Phi = arm_phase(W, a, x, 4, free)[0] + arm_phase(W, a, y, 4, free)[0]; c = min(COH[x], COH[y]) * lam ** 2
                p = bell_probs(Phi, c, st); p = p / p.sum(); o = rng.choice(4, shots, p=p); B[:, 2 * i] = o >> 1; B[:, 2 * i + 1] = o & 1
            Z[(a, st)] = pack(B)
    return Z

def clock_rho(W, a, free):
    """exact 3-qubit state (index x0*4 + x1*2 + xs): H, H, CRY(theta) c0->s, per-qubit total phase + dephasing, CRY(2 theta) c1->s"""
    psi = np.zeros((2, 2, 2), complex)
    for x0, x1 in itertools.product((0, 1), repeat=2): psi[x0, x1, :] = 0.5 * PW.ry(x0 * K.THETA)
    rho = np.outer(psi.reshape(8), psi.reshape(8).conj()); c0, s, c1 = CLOCK
    bitsm = np.array([[(i >> (2 - qq)) & 1 for qq in range(3)] for i in range(8)])
    for qi, q in ((0, c0), (1, c1), (2, s)):
        ph, lam = arm_phase(W, a, q, 4, free); lam = (W['lamC'] if a in ('M', 'MC', 'MF', 'ME') else 1.0) * (0.95 if qi < 2 else 0.9)
        U = [np.eye(2)] * 3; U = list(U); U[qi] = np.diag([np.exp(-1j * ph / 2), np.exp(1j * ph / 2)]); Uq = PW.kron3(*U); rho = Uq @ rho @ Uq.conj().T
        D = np.ones((8, 8)); D[bitsm[:, qi][:, None] != bitsm[:, qi][None, :]] = lam; rho = rho * D
    RY2 = np.array([[np.cos(K.THETA), -np.sin(K.THETA)], [np.sin(K.THETA), np.cos(K.THETA)]])
    P0, P1 = np.diag([1, 0]), np.diag([0, 1]); U = PW.kron3(np.eye(2), P0, np.eye(2)) + PW.kron3(np.eye(2), P1, RY2); return U @ rho @ U.conj().T
P10 = [0.00122, 0.00317, 0.00806]; P01 = [0.00732, 0.00879, 0.01221]
def synth_C(W, free, rng, shots):
    out = {}
    for a in K.ARMS:
        rho = clock_rho(W, a, free); out[a] = PW.sample(rho, P10, P01, shots, rng)
    return out

# expected FINAL outcomes, written before the run (C = CONSISTENT, A = ABOVE, B = BELOW, None = not scored)
EXP = {
 'KG kick M (deg/readout)':                      dict(W0='C', W1='B', W2='B', W3='C', W4='B'),
 'S1 signed residual MC (deg/readout)':          dict(W0='A', W1='C', W2='A', W3='A', W4='C'),
 'S1 signed residual MF (deg/readout)':          dict(W0='C', W1='C', W2='C', W3='C', W4='C'),
 'S1 signed residual ME (deg/readout)':          dict(W0='C', W1='C', W2='C', W3='C', W4='C'),
 'S2 SPLIT slope M vs 0 (all given back)':      dict(W0='C', W1='A', W2='A', W3='C', W4='A'),
 'S2b SPLIT slope M vs 1 (none given back)':    dict(W0=None, W1=None, W2=None, W3=None, W4=None),   # the ruler's ceiling: printed, not scored (regression dilution ~0.5-1 %)
 'S2 SPLIT slope MC vs 0 (all given back)':     dict(W0=None, W1='C', W2='B', W3=None, W4='C'),
 'S2b SPLIT slope MC vs 1 (none given back)':   dict(W0=None, W1='B', W2='B', W3=None, W4='B'),
 'S2 SPLIT slope MF vs 0 (all given back)':     dict(W0=None, W1='C', W2='C', W3=None, W4='C'),
 'S2b SPLIT slope MF vs 1 (none given back)':   dict(W0=None, W1='B', W2='B', W3=None, W4='B'),
 'S2 SPLIT slope ME vs 0 (all given back)':     dict(W0=None, W1='C', W2='C', W3=None, W4='C'),
 'S2b SPLIT slope ME vs 1 (none given back)':   dict(W0=None, W1='B', W2='B', W3=None, W4='B'),
 'S3 P(1) excess back-to-zero M':                dict(W0='C', W1='A', W2='A', W3='A', W4='A'),
 'S3 P(1) excess back-to-zero MC':               dict(W0='A', W1='C', W2='A', W3='A', W4='A'),
 'S3 P(1) excess back-to-zero MF':               dict(W0='C', W1='C', W2='C', W3='A', W4='A'),
 'S3 P(1) excess back-to-zero ME':               dict(W0='C', W1='C', W2='C', W3='A', W4='A'),
 'S4 coherence M minus none':                    dict(W0='C', W1='C', W2='C', W3='B', W4='B'),
 'S4 coherence MC minus none':                   dict(W0='C', W1='C', W2='C', W3='B', W4='B'),
 'S4 coherence MF minus none':                   dict(W0='C', W1='C', W2='C', W3='B', W4='B'),
 'S4 coherence ME minus none':                   dict(W0='C', W1='C', W2='C', W3='B', W4='B'),
 'S4b coherence MC minus M (frame only)':        dict(W0='C', W1='C', W2='C', W3='C', W4='C'),
 'S5 SPLIT slope MC minus MF (old vs fresh table)': dict(W0=None, W1='C', W2='B', W3=None, W4='C'),
 'S6 |kick| M minus |residual| MC (given back)': dict(W0='B', W1='A', W2='A', W3='B', W4='A'),
 'P1 Bell fidelity M minus none':                dict(W0='C', W1='B', W2='B', W3='B', W4='B'),
 'P1 Bell fidelity MC minus none':               dict(W0='B', W1='C', W2='B', W3='B', W4='B'),
 'P1 Bell fidelity MF minus none':               dict(W0='C', W1='C', W2='C', W3='B', W4='B'),
 'P1 Bell fidelity ME minus none':               dict(W0='C', W1='C', W2='C', W3='B', W4='B'),
 'P2 X-part concurrence M minus none':           dict(W0='C', W1='C', W2='C', W3='B', W4='B'),
 'P2 X-part concurrence MC minus none':          dict(W0='C', W1='C', W2='C', W3='B', W4='B'),
 'P2 X-part concurrence MF minus none':          dict(W0='C', W1='C', W2='C', W3='B', W4='B'),
 'P2 X-part concurrence ME minus none':          dict(W0='C', W1='C', W2='C', W3='B', W4='B'),
 'P3 Bell fidelity MC minus M (given back)':     dict(W0=None, W1='A', W2='A', W3=None, W4='A'),
 'P3b X-part concurrence MC minus M (frame only)': dict(W0='C', W1='C', W2='C', W3='C', W4='C'),
 'C1 dF M minus none':                           dict(W0='C', W1='B', W2=None, W3='B', W4='B'),   # F-based: secondary (baseline offsets, referee)
 'C1 dF MC minus none':                          dict(W0='B', W1='C', W2='B', W3='B', W4='B'),
 'C1 dF MF minus none':                          dict(W0='C', W1='C', W2='C', W3='B', W4='B'),
 'C1 dF ME minus none':                          dict(W0='C', W1='C', W2='C', W3='B', W4='B'),
 'C1 dF M with the total put back at the END minus D': dict(W0='B', W1='B', W2='B', W3='B', W4='B'),
 'C2 F(MC) minus F(M) (given back)':             dict(W0=None, W1='A', W2=None, W3=None, W4='A'),
 'C3 F(MC) minus F(M put back at the end)':      dict(W0=None, W1='A', W2=None, W3=None, W4='A'),
 'S2c SPLIT slope MC vs 0.5 (BELOW = more than half given back)': dict(W0=None, W1='B', W2='B', W3=None, W4='B'),
 'S2c SPLIT slope MF vs 0.5 (BELOW = more than half given back)': dict(W0=None, W1='B', W2='B', W3=None, W4='B'),
 'S2c SPLIT slope ME vs 0.5 (BELOW = more than half given back)': dict(W0=None, W1='B', W2='B', W3=None, W4='B'),
 'S2d SPLIT slope M minus MC (ABOVE = clears the ruler ceiling)': dict(W0=None, W1='A', W2='A', W3=None, W4='A'),
 'S2d SPLIT slope M minus MF (ABOVE = clears the ruler ceiling)': dict(W0=None, W1='A', W2='A', W3=None, W4='A'),
 'S2d SPLIT slope M minus ME (ABOVE = clears the ruler ceiling)': dict(W0=None, W1='A', W2='A', W3=None, W4='A'),
 'S7 share given back MC vs 0.5 (ABOVE = more than half)': dict(W0=None, W1='A', W2=None, W3=None, W4='A'),
 'S7 share given back MF vs 0.5 (ABOVE = more than half)': dict(W0=None, W1='A', W2='A', W3=None, W4='A'),
 'S7 share given back ME vs 0.5 (ABOVE = more than half)': dict(W0=None, W1='A', W2='A', W3=None, W4='A'),
 'P4a |pair phase| M minus copy floor (gate)':    dict(W0='C', W1='A', W2='A', W3='C', W4='A'),
 'P5 signed pair-phase residual MC (deg/step)':   dict(W0='A', W1='C', W2='A', W3='A', W4='C'),
 'P5 signed pair-phase residual MF (deg/step)':   dict(W0='C', W1='C', W2='C', W3='C', W4='C'),
 'P5 signed pair-phase residual ME (deg/step)':   dict(W0='C', W1='C', W2='C', W3='C', W4='C'),
 'P4 pair-phase share given back MC vs 0.5':      dict(W0=None, W1='A', W2=None, W3=None, W4='A'),
 'P4 pair-phase share given back MF vs 0.5':      dict(W0=None, W1='A', W2='A', W3=None, W4='A'),
 'P4 pair-phase share given back ME vs 0.5':      dict(W0=None, W1='A', W2='A', W3=None, W4='A'),
 'C4a look distance |E_M - E_D|^2 minus copy floor (gate)': dict(W0='C', W1='A', W2='A', W3=None, W4='A'),
 'C4 distance share given back MC vs 0.5':        dict(W0=None, W1='A', W2='A', W3=None, W4='A'),
 'C4 distance share given back MF vs 0.5':        dict(W0=None, W1='A', W2='A', W3=None, W4='A'),
 'C4 distance share given back ME vs 0.5':        dict(W0=None, W1='A', W2='A', W3=None, W4='A'),
}
L = {'C': 'CONSISTENT', 'A': 'ABOVE', 'B': 'BELOW'}

if __name__ == '__main__':
    NDRAW = int(sys.argv[1]) if len(sys.argv) > 1 else 6; rng = np.random.default_rng(20261031); t0 = time.time()
    tally = {}; fa = nf = mi = nm = 0; mism = []
    for wname in ('W0', 'W1', 'W2', 'W3', 'W4'):
        for d in range(NDRAW):
            W = world(wname, rng)
            freeD = {q: rng.normal(0, 15) for q in S}; freeE = {q: rng.normal(0, 2) for q in S}
            for q, off in zip(CLOCK, (-25.7, +36.0, +25.8)): freeD[q] = off   # the 24 Oct measured idle offsets (c0, s, c1), fixed (referee 31 Oct)
            cp = {}
            for lab in ('A', 'B'):
                free = dict(D=freeD, E=freeE)   # the same device in both copies
                cp[lab] = (synth_S(W, free, rng, K.SHOTS['S']), synth_P(W, free, rng, K.SHOTS['P']), synth_C(W, free, rng, K.SHOTS['C']))
            res = {}
            res.update(A.final(A.part_S(cp['A'][0], cp['B'][0], S, rng)))
            res.update(A.apply_gates(A.final(A.part_P(cp['A'][1], cp['B'][1], PAIRS, rng))))
            tot = [4 * K4[CLOCK[0]], 4 * K4[CLOCK[2]], 4 * K4[CLOCK[1]]]
            res.update(A.apply_gates(A.final(A.part_C(cp['A'][2], cp['B'][2], tot, rng, B=100))))
            for k, v in res.items():
                tally.setdefault((wname, k), {}).setdefault(v['final'], 0); tally[(wname, k)][v['final']] += 1
                want = EXP.get(k, {}).get(wname)
                if want is None: continue
                want = L[want]
                if want == 'CONSISTENT': nf += 1; fa += v['final'] != 'CONSISTENT'
                else: nm += 1; mi += v['final'] != want
                if v['final'] != want: mism.append(f'{wname} d{d} {k}: got {v["final"]} (A {v["A"]}, B {v["B"]}) value {v["v"]:+.4f} [{v["lo"]:+.4f},{v["hi"]:+.4f}] want {want}')
        print(f'{wname} done {time.time() - t0:.0f} s', flush=True)
    lines = [f'synth_keystone.py  {NDRAW} draws per world, chip table {CHIP}, shots S {K.SHOTS["S"]} P {K.SHOTS["P"]} C {K.SHOTS["C"]} per copy, two copies; FINAL outcomes']
    for (w, k), t in sorted(tally.items()): lines.append(f'  {w} {k:56s} ' + '  '.join(f'{o} {n}' for o, n in sorted(t.items())) + f'   (expected {EXP.get(k, {}).get(w)})')
    lines.append(f'FALSE CALLS (planted CONSISTENT read otherwise): {fa}/{nf} = {100 * fa / max(nf, 1):.1f} %   MISSES (planted ABOVE/BELOW read otherwise): {mi}/{nm} = {100 * mi / max(nm, 1):.1f} %')
    lines.append('MISMATCHES:'); lines += ['  ' + m for m in mism]
    open(f'{HERE}/synth_results_keystone' + ('' if CHIP == 'ibm_kingston' else '_' + CHIP) + '.text', 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines[-(len(mism) + 3):]))
