"""circuits_lums.py -- the author's QAOA swap-network circuits for n = 8 (p = 3) and n = 10 (p = 4), rebuilt with OUR code from his
published construction (paper Sec. on the swap network; notebook NB16 as text, not executed): Ising mapping of
lam x'Sx - r'x + mu (sum x - B)^2 under x = (1 - z)/2, normalised by the largest |h|, |J|; H layer; per layer RZ(2 g h) then an
odd-even transposition network of CX-RZ(2 g J)-CX-CX (RZZ + SWAP); RX(2 b); measure position -> logical clbit."""
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import ParameterVector

def ising(r, S, lam, mu, B):
    n = len(r); Q = lam * S + mu * np.ones((n, n)); L = r + 2 * mu * B * np.ones(n); off = mu * B ** 2
    h = np.zeros(n); J = np.zeros((n, n))
    for i in range(n): off += Q[i, i] / 2 - L[i] / 2; h[i] += -Q[i, i] / 2 + L[i] / 2
    for i in range(n):
        for j in range(i + 1, n):
            c = 2 * Q[i, j]; off += c / 4; h[i] -= c / 4; h[j] -= c / 4; J[i, j] += c / 4
    sc = max(np.abs(h).max(), np.abs(J).max()); return h / sc, J / sc, off, sc

def swap_network(h, J, reps):
    n = len(h); be, ga = ParameterVector('b', reps), ParameterVector('g', reps)
    qc = QuantumCircuit(QuantumRegister(n, 'q'), ClassicalRegister(n, 'c')); qc.h(range(n)); perm = list(range(n))
    for L in range(reps):
        for pos in range(n):
            if h[perm[pos]]: qc.rz(2 * ga[L] * h[perm[pos]], pos)
        for step in range(n):
            for pos in range(step % 2, n - 1, 2):
                a, b = perm[pos], perm[pos + 1]; w = J[min(a, b), max(a, b)]
                qc.cx(pos, pos + 1); qc.rz(2 * ga[L] * w, pos + 1); qc.cx(pos + 1, pos); qc.cx(pos, pos + 1)
                perm[pos], perm[pos + 1] = b, a
        qc.rx(2 * be[L], range(n))
    for pos in range(n): qc.measure(pos, perm[pos])
    return qc

def build(d):
    p = d['provenance']; pr = d['problem']
    h, J, off, sc = ising(np.array(pr['expected_returns']), np.array(pr['covariance']), p['lam'], p['mu'], p['budget'])
    assert abs(off - pr['E_offset']) < 1e-6 and abs(sc - pr['E_scale']) < 1e-6, 'Ising mapping does not reproduce his stored offset/scale'
    return swap_network(h, J, p['p'])

def bind_rows(isa, rows, reps):
    order = [q.name for q in isa.parameters]; P = np.zeros((len(rows), len(order)))
    names = [f'b[{k}]' for k in range(reps)] + [f'g[{k}]' for k in range(reps)]
    for i, nm in enumerate(names): P[:, order.index(nm)] = np.array(rows)[:, i]
    return P
