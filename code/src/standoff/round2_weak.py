"""ROUND 2 -- the three-box's WEAK VALUES, each box measured directly, with a pointer qubit (SIMULATION; nothing is sent).
2026-09-26, Bones. Rigetti Cepheus: natives rx, rz, CZ only (q0-q1 CZ fid 0.9933, q0-q9 0.9942); no coupler frames -> no small-angle CPHASE.

Why round 1's phase scan was not enough: a phase kick on level k gives P(eps) ~ 1 - 2(1-cos eps) W(1-W) -- it sees W(1-W), so
W and 1-W are twins (box A/B: +1 vs 0 identical; box C: -1 vs +2 identical). A POINTER breaks the twin: its Bloch vector
carries the sign.

THE POINTER. q1 starts in cos g|0> + sin g|1>. One CZ(q0, q1) puts a phase on q1's |1> when the qutrit sits in |1> -- and an
UNKNOWN phase zeta when it sits in |2> (a transmon CZ is built on |11>-|20>; level 2 is not a spectator). Shelving picks WHICH
box sits in |1> during the CZ:  config A: rx(pi) before + rx(-pi) after (box A in |1>);  B: nothing;  C: f12 pi swap 1<->2.
After post-selecting the qutrit on phi (V, read 0), the pointer is EXACTLY (any g, not only weak):
      c|0> + s R|1>,   R = sum_j W_j e^{i phi_j}      (W_j = <phi|P_j|psi>/<phi|psi>, sum W_j = 1)
      from its Bloch vector:  R = (x + i y) / (1 + z)   (at g = pi/4; general g rescales by tan g)
The per-level CZ phases phi_j (0, pi, zeta) are CALIBRATED in separate un-post-selected arms (qutrit in |0>/|1>/|2>, pointer
tomography), then W_A, W_B, W_C are fit (real, least squares) from the three configs' complex R. Sign is visible -> no twins.
Discard rate = 1 - |<phi|psi>|^2 = 8/9 of shots (reported per config from the sim).
  qvenv/bin/python round2_weak.py --sim
"""
import json, math, os, sys
import numpy as np
import braket_round1_step3 as s3

HERE = os.path.dirname(os.path.abspath(__file__))
S2 = json.load(open(os.path.join(HERE, 'step2_results.json')))['results']
RD = {r['prep']: r['p_read1'] for r in S2 if r['part'] == 'A' and r['read'] == 'a'}   # qutrit plain-read P(read 1) by level
PTR_ERR = 0.04          # ASSUMED pointer (q1) readout error, symmetric
CZ_DEPOL = 0.0067       # ASSUMED from Rigetti's published CZ fidelity 0.9933 (q0-q1), as 2-qubit depolarizing
ZETA_TRUE = 1.1         # ASSUMED unknown level-2 CZ phase for the sim (the calibration arms recover it)
F12_SCALE = 0.97        # measured-ish: 94% transfer -> ~3% short f12 angles
X_PHI = 0.0             # post-select phi (ideal model); hardware uses step 3's x0 - pi
TASK, SHOT = s3.PER_TASK, s3.PER_SHOT

I2 = np.eye(2); I3 = np.eye(3)
def q3(op, scale=1.0):
    if op[0] == 'f12': op = (op[0], op[1] * scale, op[2])
    return np.kron(s3.U(op), I2)
def rxp(t): return np.kron(I3, np.array([[math.cos(t/2), -1j*math.sin(t/2)], [-1j*math.sin(t/2), math.cos(t/2)]]))
def ryp(t): return np.kron(I3, np.array([[math.cos(t/2), -math.sin(t/2)], [math.sin(t/2), math.cos(t/2)]]))
def CZ(zeta):
    d = np.ones(6, dtype=complex); d[1*2+1] = -1; d[2*2+1] = np.exp(1j*zeta); return np.diag(d)
SHELVE = {'A': ([('rx', math.pi)], [('rx', -math.pi)]), 'B': ([], []), 'C': ([('f12', math.pi, 0.0)], [('f12', math.pi, math.pi)])}
BASIS = {'X': ryp(-math.pi/2), 'Y': rxp(math.pi/2), 'Z': np.eye(6)}

def depol(rho, p):
    return (1 - p) * rho + p * np.trace(rho) * np.eye(6) / 6

def run(ops_before, g, zeta, cfg, basis, noisy, post=True, prep_level=None):
    psi = np.zeros(6, dtype=complex); psi[0] = 1
    sc = F12_SCALE if noisy else 1.0
    U = np.eye(6, dtype=complex)
    seq = []
    if prep_level is None: seq += [q3(o, sc) for o in s3.PREPS['psi']]
    else:
        if prep_level >= 1: seq.append(q3(('rx', math.pi)))
        if prep_level == 2: seq.append(q3(('f12', math.pi, 0.0), sc))
    seq.append(ryp(2 * g))
    pre, postops = SHELVE[cfg]; seq += [q3(o, sc) for o in pre]
    for M in seq: psi = M @ psi
    rho = np.outer(psi, psi.conj())
    C = CZ(zeta); rho = C @ rho @ C.conj().T
    if noisy: rho = depol(rho, CZ_DEPOL)
    tail = [q3(o, sc) for o in postops]
    if post: tail += [q3(o, sc) for o in s3.V(X_PHI)]
    tail.append(BASIS[basis])
    for M in tail: rho = M @ rho @ M.conj().T
    P = np.real(np.diag(rho)).reshape(3, 2)          # P[level, pointer bit]
    # readout: qutrit "read 0" prob per level; pointer flip PTR_ERR
    r0 = np.array([1 - RD[0], 1 - RD[1], 1 - RD[2]]) if noisy else np.array([1.0, 0.0, 0.0])
    pe = PTR_ERR if noisy else 0.0
    out = {}
    for q in (0, 1):      # q = qutrit read 0 (1) or not (0)
        for b in (0, 1):
            w = r0 if q else (1 - r0)
            out[(q, b)] = float(sum(w[l] * (P[l, b] * (1 - pe) + P[l, 1 - b] * pe) for l in range(3)))
    return out

def bloch_from_counts(cnt, post=True):
    """cnt: {basis: {(q,b): prob}} -> pointer Bloch (x,y,z) conditioned on q==1 (read 0 = post-selected) or unconditioned."""
    v = []
    for B in ('X', 'Y', 'Z'):
        c = cnt[B]
        if post and NOISY:
            # UNMIX the qutrit post-selection readout (same numbers step 3 used): read-0 and read-1 ensembles are mixtures of
            # the true level-0 branch (post-selected) and the not-0 branch. Solve the 2x2 per Bloch component.
            e0 = RD[0]; en = 1 - (RD[1] + RD[2]) / 2          # P(read 1 | level 0), P(read 0 | not 0)
            r0 = c[(1, 0)] + c[(1, 1)]; p = (r0 - en) / ((1 - e0) - en)
            S0 = c[(1, 0)] - c[(1, 1)]; S1 = c[(0, 0)] - c[(0, 1)]
            M = np.array([[(1 - e0) * p, en * (1 - p)], [e0 * p, (1 - en) * (1 - p)]])
            v0, _ = np.linalg.solve(M, [S0, S1]); v.append(v0); continue
        if post: p0, p1 = c[(1, 0)], c[(1, 1)]
        else: p0, p1 = c[(0, 0)] + c[(1, 0)], c[(0, 1)] + c[(1, 1)]
        v.append((p0 - p1) / max(p0 + p1, 1e-12))
    # pointer readout correction (symmetric flip)
    return np.array(v) / (1 - 2 * (PTR_ERR if NOISY else 0))

def R_of(v, g):
    x, y, z = v
    return (x + 1j * y) / (1 + z) / math.tan(g) if (1 + z) > 1e-9 else complex('nan')

def phases_from_cal(cal):
    """cal[level] -> pointer Bloch after CZ, un-post-selected; phase of the |1> component relative to |0>."""
    return {l: math.atan2(cal[l][1], cal[l][0]) for l in (0, 1, 2)}

PERM = {'A': (1, 0, 2), 'B': (0, 1, 2), 'C': (0, 2, 1)}   # which CZ-slot each box (level) sits in during the CZ

def fit_W(Rs, ph):
    rows, rhs = [], []
    for cfg, R in Rs.items():
        e = [np.exp(1j * ph[PERM[cfg][k]]) for k in range(3)]
        rows.append([c.real for c in e]); rhs.append(R.real)
        rows.append([c.imag for c in e]); rhs.append(R.imag)
    rows.append([1, 1, 1]); rhs.append(1.0)             # sum rule, weight 1
    W, *_ = np.linalg.lstsq(np.array(rows), np.array(rhs), rcond=None)
    return W

NOISY = False
def experiment(g, noisy, shots, rng=None, zeta=ZETA_TRUE):
    global NOISY; NOISY = noisy
    def sample(d):
        if rng is None: return d
        keys = list(d); p = np.array([d[k] for k in keys]); p = np.clip(p, 0, None); p /= p.sum()
        n = rng.multinomial(shots, p); return {k: n[i] / shots for i, k in enumerate(keys)}
    cal = {}
    for l in (0, 1, 2):
        cnt = {B: sample(run(None, math.pi / 4, zeta, 'B', B, noisy, post=False, prep_level=l)) for B in 'XYZ'}
        cal[l] = bloch_from_counts(cnt, post=False)
    ph = phases_from_cal(cal)
    Rs, keep = {}, {}
    for cfg in 'ABC':
        cnt = {B: sample(run(None, g, zeta, cfg, B, noisy)) for B in 'XYZ'}
        Rs[cfg] = R_of(bloch_from_counts(cnt), g)
        keep[cfg] = np.mean([cnt[B][(1, 0)] + cnt[B][(1, 1)] for B in 'XYZ'])
    return fit_W(Rs, ph), ph, keep

def sim():
    psi = s3.run_ideal(s3.PREPS['psi']); phi = np.conj(s3.run_ideal(s3.V(X_PHI)).conj())
    # phi = V(x)^dagger |0>  ->  <phi| = <0| V
    Vm = np.eye(3, dtype=complex)
    for o in s3.V(X_PHI): Vm = s3.U(o) @ Vm
    bra = Vm[0]; ov = bra @ psi
    Wth = [(bra[k] * psi[k]) / ov for k in range(3)]
    print('THEORY W (A,B,C):', [f'{w.real:+.3f}{w.imag:+.3f}i' for w in Wth], f'  |<phi|psi>|^2 = {abs(ov)**2:.3f} (discard {1-abs(ov)**2:.1%})')
    for g in (math.pi / 4, math.pi / 8):
        W, ph, keep = experiment(g, False, None)
        print(f'\nIDEAL  g={g:.3f}: W = {np.round(W, 3)}  cal phases {[round(v, 3) for v in ph.values()]} (zeta true {ZETA_TRUE})')
        W, ph, keep = experiment(g, True, None)
        print(f'NOISY  g={g:.3f}: W = {np.round(W, 3)}  keep (post-select rate) {[round(v, 3) for v in keep.values()]}')
    n_tasks = 9 + 9 * 2     # calibration (3 levels x 3 bases) + 3 configs x 3 bases x 2 strengths
    print('\nshots/task   sigma(W_A, W_B, W_C) at g=pi/4 (noisy, bootstrap 300)     cost')
    rng = np.random.default_rng(212)
    for N in (1000, 3000, 6000, 10000):
        Ws = np.array([experiment(math.pi / 4, True, N, rng)[0] for _ in range(300)])
        m, s = Ws.mean(0), Ws.std(0)
        sepA = abs(1 - 0) / s[0]; sepC = abs(-1 - 2) / s[2]
        print(f'  {N:6d}   mean {np.round(m, 3)}  sigma {np.round(s, 3)}   A:+1 vs 0 {sepA:4.1f} sig, C:-1 vs +2 {sepC:4.1f} sig'
              f'   ${n_tasks * TASK + n_tasks * N * SHOT:6.2f} ({n_tasks} tasks)')
    # zeta sensitivity: if zeta ~ pi, level 2 is indistinguishable from level 1 in config B
    for z in (0.3, 2.8, math.pi):
        W, ph, _ = experiment(math.pi / 4, False, None, zeta=z)
        print(f'  zeta={z:.2f}: ideal fit W = {np.round(W, 3)}')

if __name__ == '__main__':
    if (sys.argv[1] if len(sys.argv) > 1 else '--sim') == '--sim': sim()
