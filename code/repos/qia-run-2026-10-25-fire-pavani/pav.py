"""pav.py -- Kumar fill for Zenodo 10.5281/zenodo.21206538 (Roberto Pavani, 'When does MWI branching occur?').
Their circuit, built from their own description (the supplementary code is not in the record): H on system qubits 0-3; CNOTs from q0 into
q1, q2, q3 (each becomes 'differs from q0'); detector q4 flipped iff q1 = q2 = q3 = 0 (a 3-control X, ctrl_state 000); only q4 measured.
Ideal P(q4 = 1) = 2/16 = 0.125. Their printed 'result' is the expectation (~512 of 4,096), not a count."""
import numpy as np
from qiskit import QuantumCircuit
SHOTS = 4096
IDEAL = 0.125
def circuit():
    qc = QuantumCircuit(5, 1)
    for q in range(4): qc.h(q)
    for q in (1, 2, 3): qc.cx(0, q)
    qc.mcx([1, 2, 3], 4, ctrl_state='000')
    qc.measure(4, 0)
    return qc
def p1(counts):
    n = sum(counts.values()); k = counts.get('1', 0); return k / n, n, k
def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return [float(c - h), float(c + h)]
def four(p, se, ref, width_ok):
    lo, hi = p - 1.96 * se, p + 1.96 * se
    if not width_ok: return 'CANNOT_TELL'
    return 'ABOVE' if lo > ref else 'BELOW' if hi < ref else 'CONSISTENT'
