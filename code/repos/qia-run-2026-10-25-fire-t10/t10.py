"""t10.py -- Kumar fill for arXiv 2510.17692 (Nedev & Vitanov, Sofia University; no funder named): twinned DD T10 vs CPMG vs free, Ramsey readout.
Their torino figure (one qubit, one session): free T2* 238.3 us, XY4 274.0, CPMG 312.6, UR10 318.4, T10 344.6 us.
Built from their text: Ramsey = sx, then the sequence spanning delay t, then sx, measure (ideal P(1) = 1 at t = 0 for an identity sequence).
A sequence of 2n = 10 phased pi pulses, palindrome spacing tau/2 - pi - tau - ... - pi - tau/2 with tau = t/10. Phased pi about (cos p, sin p, 0):
rz(-p), x, rz(p). T10 phases (0, 3/5, 4/5, 3/5, 0, 1, 8/5, 9/5, 8/5, 1) pi (their Table I = formula (k-1)(n-k)/n pi, n = 5). CPMG10: ten pi_y (p = pi/2).
Free: plain delay t. All four chosen qubits carry the same sequence in one circuit (no two adjacent)."""
import numpy as np
from qiskit import QuantumCircuit
T10 = [x * np.pi for x in (0, 3 / 5, 4 / 5, 3 / 5, 0, 1, 8 / 5, 9 / 5, 8 / 5, 1)]
CPMG = [np.pi / 2] * 10
DELAYS_US = [0, 40, 80, 150, 250, 350, 450, 600]
SHOTS = 4000
def q16(x): return int(16 * round(x / 16))
def circuit(arm, t_us, qubits, dt):
    n = 156; qc = QuantumCircuit(n, len(qubits))
    tot = q16(t_us * 1e-6 / dt)
    for q in qubits: qc.sx(q)
    if arm == 'free' or tot == 0 and arm == 'free':
        for q in qubits:
            if tot: qc.delay(tot, q, unit='dt')
    else:
        ph = T10 if arm == 't10' else CPMG; tau = q16(tot / 10); half = q16(tau / 2)
        for q in qubits:
            if half: qc.delay(half, q, unit='dt')
            for k, p in enumerate(ph):
                qc.rz(-p, q); qc.x(q); qc.rz(p, q)
                if k < 9 and tau: qc.delay(tau, q, unit='dt')
            if half: qc.delay(half, q, unit='dt')
    for q in qubits: qc.sx(q)
    for i, q in enumerate(qubits): qc.measure(q, i)
    return qc
