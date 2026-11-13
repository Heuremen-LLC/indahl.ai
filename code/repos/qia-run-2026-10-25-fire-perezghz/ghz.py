"""ghz.py -- Kumar fill for Zenodo 10.5281/zenodo.20538557 (Jesus Perez Expolio, 'Empirical scaling law for GHZ state fidelity').
Their circuit: H on q0, CX chain q0->q1->...->q(N-1), measure all; opt 1, no initial layout; 8,192 shots. Their 'fidelity' F = P(0..0) + P(1..1).
Their drift reading: N = 12 on fez, two runs hours apart, 0.692 and 0.503 (Delta 0.189), attributed to device temporal drift.
Parity circuits for the coherence C: after the GHZ, rz(phi) then h on every qubit, measure all; ideal parity = cos(N phi). Fidelity = (P + C)/2."""
import numpy as np
from qiskit import QuantumCircuit
N, SHOTS = 12, 8192
PHIS = [2 * np.pi * k / (8 * N) for k in range(8)]
def ghz(n=N, phi=None):
    qc = QuantumCircuit(n, n); qc.h(0)
    for i in range(n - 1): qc.cx(i, i + 1)
    if phi is not None:
        for q in range(n): qc.rz(phi, q); qc.h(q)
    qc.measure(range(n), range(n)); return qc
def population(c):
    n = sum(c.values()); k = c.get('0' * N, 0) + c.get('1' * N, 0); p = k / n; return p, float(np.sqrt(p * (1 - p) / n))
def parity(c):
    n = sum(c.values()); s = sum(v * (1 - 2 * (b.count('1') % 2)) for b, v in c.items()); m = s / n; return m, float(np.sqrt(max(1 - m * m, 1e-12) / n))
def coherence(par):
    """par: list of (phi, mean, se). Weighted fit mean = a cos(N phi) + b sin(N phi); C = sqrt(a^2 + b^2) with propagated se."""
    X = np.array([[np.cos(N * f), np.sin(N * f)] for f, _, _ in par]); y = np.array([m for _, m, _ in par]); w = np.array([1 / s ** 2 for _, _, s in par])
    W = np.diag(w); cov = np.linalg.inv(X.T @ W @ X); a, b = cov @ X.T @ W @ y; C = float(np.hypot(a, b))
    g = np.array([a, b]) / C if C > 0 else np.array([1.0, 0.0]); return C, float(np.sqrt(g @ cov @ g))
