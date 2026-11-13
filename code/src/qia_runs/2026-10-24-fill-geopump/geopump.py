"""geopump.py -- our own implementation (24 Oct 2026) of the Caselli-Manuel-Arrachea-Cornaglia geometric heat pump (arXiv 2610.09062v2,
Zenodo 10.5281/zenodo.23339851), rebuilt from their PUBLISHED equations and circuit description (README, SM I.1-I.8). Their code is never run.

Model (their Eqs., units T = 1): B(phi) = B0 + dB f(cos phi), theta(phi) = theta0 + dtheta f(sin phi), f(x) = tanh(k x)/tanh(k);
N cells of dt = tau/N; per cell: R_y(theta_{j-1} - theta_j) on S (j > 0), R_z(2 B_j dt), four collisions L, R, R, L with
lambda = 1 - exp(-Gamma dt / 2), varphi = arcsin sqrt(lambda), ancilla excited population p_exc = 1/(1 + exp(2B)); bit 0 = excited (+B).
Heat per collision Q = 2 B_j (b_in - b_out). odd = (fwd - rev)/2, even = (fwd + rev)/2, each direction a weighted mix of two branches.

Three circuit families, same physical qubits (S, aL, aR):
  A   their protocol: reset a, R_y(prep) a, MEASURE a (b_in), XXPlusYY(2 varphi) (S, a), measure a (b_out).
  Ap  b_in drawn at random per realization (bit 0 w.p. p_exc), prepared as a basis state (reset, X if b_in = 1), MEASURE a (b_in kept),
      XXPlusYY, measure a (b_out).  Ideally identical in distribution to A.
  Bp  as Ap, but the incoming measurement is replaced by a DELAY of the measurement's scheduled length on a (545 dt on kingston).
      Ideally identical to Ap: measuring a basis state does nothing. Ap - Bp = what 4N incoming readouts cost beyond their waiting time.
Heat in Ap and Bp uses the PREPARED b_in (like for like); Ap's measured b_in gives the incoming-readout assignment error on aL, aR."""
import numpy as np

B0, THETA0, DTHETA, KAPPA, OMEGA_C, GL, GR = 0.61, np.pi / 4, 2 * np.pi / 9, 2.5, 120.0, 1.0, 1.0
N = 48
ORDER = ('L', 'R', 'R', 'L')


# ---------------- model ----------------
def loop(u, dB):
    phi = 2 * np.pi * u; tk = np.tanh(KAPPA)
    B = B0 + dB * np.tanh(KAPPA * np.cos(phi)) / tk; th = THETA0 + DTHETA * np.tanh(KAPPA * np.sin(phi)) / tk
    return B * np.sin(th), B * np.cos(th)

def cell(Bx, Bz, dt):
    B = float(np.hypot(Bx, Bz)); g = float(np.arctan2(Bx, Bz)); w = 2 * B
    spec = w * np.exp(-w / OMEGA_C) / np.tanh(B)
    GLr = GL ** 2 * 0.25 * np.cos(g) ** 2 * spec; GRr = GR ** 2 * 0.25 * np.sin(g) ** 2 * spec
    lL, lR = 1 - np.exp(-GLr * dt / 2), 1 - np.exp(-GRr * dt / 2)
    return dict(B=B, g=g, phi_drive=2 * B * dt, lam_L=lL, lam_R=lR, th_L=float(np.arcsin(np.sqrt(lL))), th_R=float(np.arcsin(np.sqrt(lR))),
                p_exc=float(1 / (1 + np.exp(w))), veq=float(-np.tanh(B)))

def schedule(dB, tau, reverse=False):
    u = (np.arange(N) + 0.5) / N
    if reverse: u = u[::-1]
    return [cell(*loop(float(x), dB), tau / N) for x in u]

def _ry(v, a):
    c, s = np.cos(a), np.sin(a); return np.array([c * v[0] + s * v[2], v[1], -s * v[0] + c * v[2]])
def _rz(v, a):
    c, s = np.cos(a), np.sin(a); return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1], v[2]])

def traverse(v0, sch, heat=False):
    v = np.array(v0, float); QL = QR = 0.0; gp = sch[0]['g']
    for m, c in enumerate(sch):
        if m > 0: v = _ry(v, gp - c['g'])
        v = _rz(v, c['phi_drive'])
        for bath in ORDER:
            lam = c['lam_L'] if bath == 'L' else c['lam_R']; q = c['B'] * lam * (v[2] - c['veq'])
            if bath == 'L': QL += q
            else: QR += q
            k = np.sqrt(max(0, 1 - lam)); v = np.array([k * v[0], k * v[1], (1 - lam) * v[2] + lam * c['veq']])
        gp = c['g']
    v = _ry(v, gp - sch[0]['g'])
    return (v, QL, QR) if heat else v

def periodic(sch):
    b = traverse(np.zeros(3), sch); A = np.column_stack([traverse(np.eye(3)[j], sch) - b for j in range(3)])
    v = np.linalg.solve(np.eye(3) - A, b); n = np.linalg.norm(v)
    return v / n if n > 1 else v

def branches(v):
    s = float(np.linalg.norm(v)); n = v / s if s > 1e-14 else np.array([0, 0, 1.0])
    return [('plus', 0.5 * (1 + s), n), ('minus', 0.5 * (1 - s), -n)]

def ideal(dB, tau):
    out = {}
    for d, rev in (('fwd', False), ('rev', True)):
        sch = schedule(dB, tau, rev); v0 = periodic(sch); _, ql, qr = traverse(v0, sch, True); out[d] = (ql, qr)
    f, r = out['fwd'], out['rev']
    return dict(QL_odd=(f[0] - r[0]) / 2, QR_odd=(f[1] - r[1]) / 2, QL_even=(f[0] + r[0]) / 2, QR_even=(f[1] + r[1]) / 2)


# ---------------- circuits ----------------
def draw_bin(sch, rng):
    """incoming bits per bath in collision order: dict bath -> array (2N,), bit 0 (excited) w.p. p_exc."""
    out = {'L': [], 'R': []}
    for c in sch:
        for bath in ORDER: out[bath].append(0 if rng.random() < c['p_exc'] else 1)
    return {k: np.array(v, int) for k, v in out.items()}

def build(sch, init, family, bins=None, meas_dt=545, name='c'):
    """family 'A' (theirs), 'Ap' (random basis b_in, measured), 'Bp' (random basis b_in, delay instead of incoming measurement)."""
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.circuit.library import XXPlusYYGate
    q = QuantumRegister(3, 'q'); w = 4 * N if family in ('A', 'Ap') else 2 * N
    eL, eR, sy = ClassicalRegister(w, 'eL'), ClassicalRegister(w, 'eR'), ClassicalRegister(1, 'sys')
    qc = QuantumCircuit(q, eL, eR, sy, name=name); S, AL, AR = 0, 1, 2
    x, y, z = init; th = float(np.arccos(np.clip(z, -1, 1))); ph = float(np.arctan2(y, x))
    if abs(th) > 1e-14: qc.ry(th, S)
    if abs(ph) > 1e-14: qc.rz(ph, S)
    idx = {'L': 0, 'R': 0}; gp = sch[0]['g']
    for m, c in enumerate(sch):
        if m > 0 and abs(gp - c['g']) > 1e-14: qc.ry(float(gp - c['g']), S)
        qc.rz(float(c['phi_drive']), S)
        for bath in ORDER:
            anc, cr = (AL, eL) if bath == 'L' else (AR, eR); vp = c['th_L'] if bath == 'L' else c['th_R']; i = idx[bath]
            qc.reset(anc)
            if family == 'A':
                pr = 2 * np.arccos(np.sqrt(np.clip(c['p_exc'], 0, 1)))
                if abs(pr) > 1e-14: qc.ry(float(pr), anc)
                qc.measure(anc, cr[2 * i]); out = 2 * i + 1
            else:
                if bins[bath][i] == 1: qc.x(anc)
                if family == 'Ap': qc.measure(anc, cr[2 * i]); out = 2 * i + 1
                else: qc.delay(meas_dt, anc, unit='dt'); out = i
            if vp > 1e-14: qc.append(XXPlusYYGate(2 * float(vp)), [S, anc])
            qc.measure(anc, cr[out]); idx[bath] += 1
        gp = c['g']
    if abs(gp - sch[0]['g']) > 1e-14: qc.ry(float(gp - sch[0]['g']), S)
    qc.measure(S, sy[0])
    return qc


# ---------------- estimator ----------------
def Bvec(sch):
    return np.repeat([c['B'] for c in sch], 2)   # per bath, 2 collisions per cell, collision order

def shot_heat(sch, family, eLbits, eRbits, bins=None):
    """per-shot heat (QL, QR) for one circuit. A and Ap_rec: in/out bits interleaved, both measured; Ap: b_in = PREPARED; Bp: out bits only, b_in prepared."""
    Bv = Bvec(sch); res = []
    for bits, bath in ((eLbits, 'L'), (eRbits, 'R')):
        e = np.asarray(bits, np.int64)
        if family in ('A', 'Ap_rec'): bi, bo = e[:, 0::2], e[:, 1::2]      # Ap_rec = Ap scored with its MEASURED b_in (their estimator)
        elif family == 'Ap': bi, bo = np.broadcast_to(bins[bath], e[:, 1::2].shape), e[:, 1::2]
        else: bi, bo = np.broadcast_to(bins[bath], e.shape), e
        res.append((2 * Bv[None, :] * (bi - bo)).sum(1))
    return res

def combine(means):
    """means[(dir, branch)] = (QL, QR) means; weights inside. returns dict of odd/even per bath."""
    out = {}
    for k, bath in ((0, 'L'), (1, 'R')):
        f = sum(w * m[k] for (d, b), (w, m) in means.items() if d == 'fwd'); r = sum(w * m[k] for (d, b), (w, m) in means.items() if d == 'rev')
        out[f'Q{bath}_odd'] = (f - r) / 2; out[f'Q{bath}_even'] = (f + r) / 2
    out['Qtot_even'] = out['QL_even'] + out['QR_even']
    return out

KEYS = ('QL_odd', 'QR_odd', 'QL_even', 'QR_even', 'Qtot_even')

def outcome(lo, hi):
    return 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT'
