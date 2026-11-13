"""sim_harness.py -- written by the design referee (31 Oct), kept unchanged except HERE: the real circ_S/circ_P/circ_C with the look replaced by a planted rz kick, exact statevectors, packed BitArray bits, the real readers. Output -> sim_harness_results.text"""
import os, sys, itertools
sys.dont_write_bytecode = True
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import keystone as K, pooters as PW
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
rng = np.random.default_rng(5)

def pack(B):
    sh, nb = B.shape; nby = (nb + 7) // 8; P = np.zeros((sh, nby * 8), np.uint8); P[:, :nb] = B
    by = np.packbits(P.reshape(sh, nby, 8), axis=2, bitorder='little').reshape(sh, nby); return by[:, ::-1].copy()

def simulate(qc, E, kicks):
    """replace each look-step measurement of E by planted rz(kick_q) on every non-E qubit; return (probs over fin bits in order, nbits)"""
    n = qc.num_qubits; out = QuantumCircuit(n); finmap = {}
    step_seen = set()
    for inst in qc.data:
        op = inst.operation; qs = [qc.find_bit(q).index for q in inst.qubits]
        if op.name == 'measure':
            cb = inst.clbits[0]; loc = qc.find_bit(cb).registers[0]
            reg, idx = loc[0].name, loc[1]
            if reg == 'fin': finmap[idx] = qs[0]
            else:
                if reg not in step_seen:
                    step_seen.add(reg)
                    for q, k in kicks.items(): out.rz(np.radians(k), q)
            continue
        if op.name in ('barrier', 'delay'): continue
        out.append(op, qs)
    nb = len(finmap); order = [finmap[j] for j in range(nb)]
    p = Statevector(out).probabilities(order)
    return p, nb

def sample_pack(p, nb, shots):
    p = np.clip(p, 0, None); p = p / p.sum(); idx = rng.choice(len(p), shots, p=p)
    B = ((idx[:, None] >> np.arange(nb)[None, :]) & 1).astype(np.uint8); return pack(B)

report = []
# ---------------- S ----------------
n = 7; E = [5, 6]; S = [3, 0, 4, 1, 2]
kicks = {3: -7.6, 0: 2.1, 4: -18.1, 1: 5.5, 2: -3.0}
Z = {}
for arm in K.ARMS:
    corr = kicks if arm in ('MC', 'MF') else {}
    for st in K.SET_S:
        qc = K.circ_S(n, E, S, arm, st, corr, 545)
        p, nb = simulate(qc, E, kicks if arm in ('M', 'MC', 'MF', 'ME') else {})
        Z[(arm, st)] = [sample_pack(p, nb, 200000)]
R = K.read_S(Z, S, rng)
for a in ('M', 'MC', 'MF', 'ME'):
    report.append(f'S {a}: kick per readout by fin index (expect planted {[kicks[q] for q in S]}) -> {np.round(R[a]["kick"], 2).tolist()}')
report.append(f'S D/DE phase (deg): {np.round(np.degrees(R["D"]["ph"]),1).tolist()} / {np.round(np.degrees(R["DE"]["ph"]),1).tolist()}  (expect -90)')
report.append(f'S Z0 P1 excess M: {np.round(R["M"]["p1"],4).tolist()} expect (1-cos(8k))/2 = {[round((1-np.cos(np.radians(8*kicks[q])))/2,4) for q in S]}; MC {np.round(R["MC"]["p1"],4).tolist()}')
# ---------------- P ----------------
n = 7; E = [5, 6]; pairs = [(0, 1), (3, 2)]; singles = [4]
kicks = {0: -7.6, 1: 2.1, 3: -18.1, 2: 5.5, 4: -3.0}
Zp = {}
for arm in K.ARMS:
    corr = kicks if arm in ('MC', 'MF') else {}
    for st in K.SET_P:
        qc = K.circ_P(n, E, pairs, singles, arm, st, corr, 545)
        p, nb = simulate(qc, E, kicks if arm in ('M', 'MC', 'MF', 'ME') else {})
        Zp[(arm, st)] = [sample_pack(p, nb, 300000)]
RP = K.read_P(Zp, pairs, rng)
for a in K.ARMS:
    exp = [round((1 + np.cos(np.radians(K.N_P * (kicks[x] + kicks[y]))))/2, 4) for x, y in pairs]
    report.append(f'P {a}: fbell {np.round(RP[a]["fbell"],4).tolist()} conc {np.round(RP[a]["conc"],4).tolist()}   (M expect F {exp})')
# ---------------- C ----------------
n = 5; E = [3, 4]; clock = (0, 1, 2)   # c0, s, c1
c0, s, c1 = clock
kc = {c0: -3.07, s: -7.61, c1: -18.12}
CC = {}
for arm in K.ARMS:
    corr = kc if arm in ('MC', 'MF') else {}
    CC[arm] = {}
    for st in K.SET_C:
        qc = K.circ_C(n, E, clock, arm, st, corr, 545)
        p, nb = simulate(qc, E, kc if arm in ('M', 'MC', 'MF', 'ME') else {})
        CC[arm][st] = K.counts3([sample_pack(p, nb, 400000)])
tot = [K.N_C * kc[c0], K.N_C * kc[c1], K.N_C * kc[s]]
F = K.read_C(CC, tot)
report.append('C F per arm: ' + ', '.join(f'{a} {v:.4f}' for a, v in F.items()) + '   (sim_check: D 1.0000, M 0.6259, MC 1.0000, M_end 0.9556; ME,DE expect 1, MF 1)')
print('\n'.join(report))
