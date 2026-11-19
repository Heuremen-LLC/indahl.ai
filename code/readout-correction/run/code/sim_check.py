"""sim_check.py -- sign and placement check of the correction, exact statevectors (qiskit quantum_info), no hardware.
(1) a qubit prepared by sx and hit by rz(k) per step (the model of a kick k) reads phase(M) - phase(D) = N k through keystone.rot X/Y,
    with phase = atan2(<Y>, <X>) as the committed analysis: the measured kick IS the rz angle, so the correction is rz(-kick).
(2) the clock with the look in the middle, kick modelled as rz on c0, s, c1: F(D) = 1, F(M) < 1, F(MC with rz(-k) after each step) = 1,
    and F(M with the total put back at the END) < 1 when s carries a kick (the end cannot undo a phase that a later CRY has acted on)."""
import sys, os, numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, Pauli
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keystone as K, pooters as PW
out = []
k = np.radians(-7.6); N = 8
def ph(qc_prep):
    v = {}
    for b in ('X', 'Y'):
        qc = qc_prep.copy(); K.rot(qc, 0, b); p = Statevector(qc).probabilities([0]); v[b] = p[0] - p[1]
    return np.degrees(np.arctan2(v['Y'], v['X']))
d = QuantumCircuit(1); d.sx(0)
m = QuantumCircuit(1); m.sx(0)
for _ in range(N): m.rz(k, 0)
c = m.copy()
for _ in range(N): c.rz(-k, 0)
out.append(f'(1) planted rz {np.degrees(k):+.2f} deg/step x {N}: read (phase M - phase D)/N = {(ph(m) - ph(d)) / N:+.3f}; with rz(-kick) per step: {(ph(c) - ph(d)) / N:+.3f}')
kick = {0: np.radians(-3.07), 1: np.radians(-7.61), 2: np.radians(-18.12)}   # c0, s, c1 (logical 0, 2, 1 below)
def clock(arm, end_fix=False):
    qc = QuantumCircuit(3)   # logical: 0 = c0, 1 = c1, 2 = s
    qc.h(0); qc.h(1); qc.cry(K.THETA, 0, 2)
    for _ in range(4):
        if arm != 'D':
            qc.rz(kick[0], 0); qc.rz(kick[2], 1); qc.rz(kick[1], 2)
        if arm == 'MC':
            qc.rz(-kick[0], 0); qc.rz(-kick[2], 1); qc.rz(-kick[1], 2)
    qc.cry(2 * K.THETA, 1, 2)
    if end_fix: qc.rz(-4 * kick[0], 0); qc.rz(-4 * kick[2], 1); qc.rz(-4 * kick[1], 2)
    return Statevector(qc)
ideal = clock('D')
# qiskit little-endian: index = c0 + 2 c1 + 4 s; pooters ideal_psi index = x0*4 + x1*2 + xs -> compare by fidelity of states
def F(sv): return abs(np.vdot(ideal.data, sv.data)) ** 2
out.append(f'(2) clock, look in the middle: F(D) {F(clock("D")):.4f}  F(M) {F(clock("M")):.4f}  F(MC) {F(clock("MC")):.4f}  F(M, total put back at the end) {F(clock("M", True)):.4f}')
# cross-check against pooters' ideal history state (same physics, its own index order)
psi_q = clock('D').data.reshape(2, 2, 2)                     # axes (s, c1, c0) in qiskit order
psi_p = np.transpose(psi_q, (2, 1, 0)).reshape(8)           # -> (c0, c1, s)
out.append(f'    |<pooters ideal | circuit D>|^2 = {abs(np.vdot(PW.ideal_psi(), psi_p)) ** 2:.6f} (1 = the circuit builds the history state pooters.py scores against)')
open('sim_check_results.text', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
# (3) the 24 Oct data (look at the END): rotate the MEASURED idle tomography E_D by the committed kicks (pure rotation, no loss) and compare
#     with the MEASURED look E_M. An ideal-state ratio is not the comparison: the measured idle state is itself rotated off the ideal one.
import json
P24 = '../earlier_runs/2026-10-24-page-wootters'
C = {a: {st: {} for st in PW.SETTINGS} for a in 'DM'}
for j in ('J1', 'J2'):
    for e in json.load(open(f'{P24}/raw_pooters_{j}.json')):
        for kk, v in e['counts'].items(): C[e['arm']][e['setting']][kk] = C[e['arm']][e['setting']].get(kk, 0) + v
ED, EM = PW.evec(PW.to_P(C['D'])), PW.evec(PW.to_P(C['M']))
tot = np.radians([4 * -3.065, 4 * -18.1202, 4 * -7.6073])   # c0, c1, s (committed 21 Oct, per readout x 4)
T = PW.kron3(PW.qmap(tot[0], 1), PW.qmap(tot[1], 1), PW.qmap(tot[2], 1))
out.append(f'(3) 24 Oct look at the END: measured F(D) {PW.fidelity(ED):.4f}, measured F(M) {PW.fidelity(EM):.4f}, measured D rotated by the committed kicks '
           f'(no loss) {PW.fidelity(T @ ED):.4f}  (DEFINED AFTER THE 24 Oct DATA)')
open('sim_check_results.text', 'w').write('\n'.join(out) + '\n'); print(out[-1])
