"""tele.py -- circuits and per-block estimators for the Tehran teleportation fill (Zenodo 23634581, Abdolhosseini).
Circuits rebuilt from their protocol (src/telecorr/protocol.py: circuit(); version A = Alice measured, Bob's corrections as a
software Pauli frame, docs/frame). Plain numpy functions vendored from their release by reading, not import: rotation, u_matrix,
so3, su2, angles (qiskit U3 decomposer), procrustes, the Pauli frame, linear tomography F, TOMO-9 least squares.
Their logical roles q0..q5 on a 6-qubit path in the order (q4, q2, q0, q1, q3, q5); their chain on kingston = 21-36-41-42-43-44."""
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
I2 = np.eye(2, dtype=complex); X = np.array([[0, 1], [1, 0]], complex); Y = np.array([[0, -1j], [1j, 0]]); Z = np.diag([1, -1]).astype(complex)
SIG = (X, Y, Z); PAULI = {'I': I2, 'X': X, 'Y': Y, 'Z': Z}
THETA_BELL = float(2 * np.arcsin(np.sqrt(0.7)))
NOISE = {2: ((0.1, -0.5, -0.1), 0.5), 3: ((-0.7, 1.0, 0.1), 1.3)}                  # their NOMINAL_NOISE (N1)
CORR_N1 = [0.4420491315360544, 0.07187565322993317, 0.09936683421260309, 1.319954704354623, -2.4561317649927905, 2.4570065482774948]  # their Round 2 N1 correction (8d_round2.json corr.N1)
R_CYC = np.array([[0.0, 0, 1], [1, 0, 0], [0, 1, 0]])
BASES9 = [a + b for a in 'XYZ' for b in 'XYZ']                                     # (q4 basis, q5 basis)
PROBES = (('|00>', 'Z'), ('|++>', 'X'), ('|+i+i>', 'Y'))
ROLE_ORDER = ('q4', 'q2', 'q0', 'q1', 'q3', 'q5')                                  # path position -> logical role
def rotation(axis, ang):
    n = np.asarray(axis, float) / np.linalg.norm(axis); return np.cos(ang / 2) * I2 - 1j * np.sin(ang / 2) * sum(c * p for c, p in zip(n, SIG))
def u_matrix(t, p, l):
    c, s = np.cos(t / 2), np.sin(t / 2); return np.array([[c, -np.exp(1j * l) * s], [np.exp(1j * p) * s, np.exp(1j * (p + l)) * c]])
def so3(V):
    Vd = V.conj().T; return np.array([[0.5 * np.trace(SIG[a] @ V @ SIG[b] @ Vd).real for b in range(3)] for a in range(3)])
def su2(R):
    t = np.trace(R)
    if t > 0:
        s = 2 * np.sqrt(t + 1); w, x, y, z = s / 4, (R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2 * np.sqrt(1 + R[0, 0] - R[1, 1] - R[2, 2]); w, x, y, z = (R[2, 1] - R[1, 2]) / s, s / 4, (R[0, 1] + R[1, 0]) / s, (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = 2 * np.sqrt(1 + R[1, 1] - R[0, 0] - R[2, 2]); w, x, y, z = (R[0, 2] - R[2, 0]) / s, (R[0, 1] + R[1, 0]) / s, s / 4, (R[1, 2] + R[2, 1]) / s
    else:
        s = 2 * np.sqrt(1 + R[2, 2] - R[0, 0] - R[1, 1]); w, x, y, z = (R[1, 0] - R[0, 1]) / s, (R[0, 2] + R[2, 0]) / s, (R[1, 2] + R[2, 1]) / s, s / 4
    return w * I2 - 1j * (x * X + y * Y + z * Z)
def angles(V):
    from qiskit.synthesis import OneQubitEulerDecomposer
    return [float(a) for a in OneQubitEulerDecomposer('U3').angles(np.asarray(V, complex))]
def procrustes(T):
    U, _, Wt = np.linalg.svd(T); d = np.sign(np.linalg.det(Wt.T @ U.T)) or 1.0; return Wt.T @ np.diag([1.0, 1.0, d]) @ U.T
def rot_angle(R): return float(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))
def message_state(name):
    a = u_matrix(0, 0, 0)
    if name == 'product_HT':
        v = np.diag([1, np.exp(1j * np.pi / 4)]) @ (np.array([1, 1]) / np.sqrt(2)); return np.kron(v, v)
    v = np.zeros(4, complex); v[0] = np.sqrt(0.3); v[3] = np.sqrt(0.7); return v              # qiskit order |q1 q0>
# ------------------------------------------------------------------ circuits (their protocol, version A, barriers as theirs)
def _prep(qc, name):
    if name == 'product_HT':
        for q in (0, 1): qc.h(q); qc.t(q)
    elif name == 'bell_30_70':
        qc.ry(THETA_BELL, 0); qc.cx(0, 1)
    elif name == '|++>':
        for q in (0, 1): qc.h(q)
    elif name == '|+i+i>':
        for q in (0, 1): qc.h(q); qc.s(q)
def circuit(message, basis, block, setting=None):
    """block: 'native' (no channel, no correction), 'N1none' (injected N1), 'N1corr' (N1 + their learned correction),
    'probe' (no channel; correction box = setting rotation of TOMO-9). basis = (q4, q5) measurement bases."""
    q = QuantumRegister(6, 'q'); al, bo = ClassicalRegister(4, 'alice'), ClassicalRegister(2, 'bob')
    qc = QuantumCircuit(q, al, bo)
    _prep(qc, message); qc.barrier()
    qc.h(2); qc.cx(2, 4); qc.h(3); qc.cx(3, 5); qc.barrier()
    if block in ('N1none', 'N1corr'):
        for k in (2, 3): qc.u(*angles(rotation(*NOISE[k])), k)
        qc.barrier()
    if block == 'N1corr':
        qc.u(*CORR_N1[:3], 2); qc.u(*CORR_N1[3:], 3); qc.barrier()
    if block == 'probe' and setting is not None:
        a = angles(su2(setting)); qc.u(*a, 2); qc.u(*a, 3); qc.barrier()
    qc.cx(0, 2); qc.h(0); qc.cx(1, 3); qc.h(1); qc.barrier()
    qc.measure([0, 1, 2, 3], al); qc.barrier()
    for qb, b in zip((4, 5), basis):
        if b == 'X': qc.h(qb)
        elif b == 'Y': qc.sdg(qb); qc.h(qb)
    qc.measure([4, 5], bo)
    return qc
def block_circuits(block, message):
    return [(f'{block}_{message}_{b}', circuit(message, b, block)) for b in BASES9]
def probe_circuits():
    out = []
    for j, S in enumerate([np.eye(3), R_CYC, R_CYC @ R_CYC]):
        for name, ax in PROBES: out.append((f'probe_s{j}_{ax}', circuit(name, ax * 2, 'probe', None if j == 0 else S)))
    return out
# ------------------------------------------------------------------ estimators from per-shot (alice, bob) integers
def frame_keys(al, bo, bases):
    al = np.asarray(al); bo = np.asarray(bo); z4, z5, x4, x5 = al & 1, (al >> 1) & 1, (al >> 2) & 1, (al >> 3) & 1
    fl = {'Z': lambda z, x: x, 'X': lambda z, x: z, 'Y': lambda z, x: z ^ x}
    return ((bo >> 1) & 1 ^ fl[bases[1]](z5, x5)) * 2 + ((bo & 1) ^ fl[bases[0]](z4, x4))
def tables(shots9):
    """shots9 = {basis: (alice ints, bob ints)} -> {basis: counts[4]} frame-corrected."""
    return {b: np.bincount(frame_keys(a, o, b), minlength=4) for b, (a, o) in shots9.items()}
def lin_F(tabs, psi):
    rho = np.zeros((4, 4), complex)
    for p4 in 'IXYZ':
        for p5 in 'IXYZ':
            vals = []
            for bs, c in tabs.items():
                if (p4 != 'I' and bs[0] != p4) or (p5 != 'I' and bs[1] != p5): continue
                k = np.arange(4); s = (-1.0) ** (((k & 1) if p4 != 'I' else 0) + ((k >> 1) if p5 != 'I' else 0)); vals.append((s * c).sum() / c.sum())
            rho += np.mean(vals) * np.kron(PAULI[p5], PAULI[p4]) / 4
    return float(np.real(np.conj(psi) @ rho @ psi))
def F_with_se(tabs, psi, boot=200, seed=1):
    rng = np.random.default_rng(seed); f0 = lin_F(tabs, psi); bs = []
    for _ in range(boot):
        bs.append(lin_F({b: rng.multinomial(int(c.sum()), c / c.sum()) for b, c in tabs.items()}, psi))
    return f0, float(np.std(bs, ddof=1))
def fingerprint(probe_tabs):
    """probe_tabs = {f'probe_s{j}_{ax}': counts[4]} -> {leg: rotation angle (rad) of the nearest rotation to the TOMO-9 T}."""
    Rs = [np.eye(3), R_CYC, R_CYC @ R_CYC]; out = {}
    for leg, bit in ((2, 0), (3, 1)):
        A = np.zeros((9, 9)); y = np.zeros(9)
        for j in range(3):
            for i, (_, ax) in enumerate(PROBES):
                a = 'XYZ'.index(ax); c = probe_tabs[f'probe_s{j}_{ax}']; k = np.arange(4)
                p0 = c[((k >> bit) & 1) == 0].sum() / c.sum(); y[3 * j + a] = 2 * p0 - 1
                A[3 * j + a, [3 * cc + a for cc in range(3)]] = Rs[j][a, :]
        T = np.linalg.solve(A, y).reshape(3, 3); out[leg] = rot_angle(procrustes(T).T)
    return out
def recovered(c, n, a):
    """f = (c - n)/(a - n) with delta-method sd; c, n, a = (value, sd)."""
    D = a[0] - n[0]; f = (c[0] - n[0]) / D
    return f, float(np.sqrt(c[1] ** 2 + f ** 2 * a[1] ** 2 + (1 - f) ** 2 * n[1] ** 2) / abs(D))
