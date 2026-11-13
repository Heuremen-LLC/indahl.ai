"""synth_tele.py -- the analysis run on planted worlds (exact circuit probabilities of OUR rebuilt circuits + planted noise, multinomial shots).
Noise planted: depolarising mix of Bob's outcome with weight e (per layout / job) and a coherent z-rotation theta on channel qubit q3 (the
fingerprint). Worlds: NULL (all equal), LAYOUT (e differs by layout), DRIFT (job B e + 0.03), FINGER (theta 0.16 on their chain only),
BOTH (LAYOUT + DRIFT), NEITHER-but-rotated (theta 0.16 on every layout: fingerprint resolved, CONSISTENT across layouts).
Floor: 30 NULL replicates (boot 40), count of ABOVE/BELOW per reading."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tele import *
from tele_fill import analyse, MSGS, LAYS, BLOCKS
from qiskit.quantum_info import Statevector
from qiskit.circuit import CircuitInstruction
from qiskit.circuit.library import RZGate
SH, SHP = 3000, 2000
CACHE = {}
def probs(label, qc, theta):
    key = (label, round(theta, 6))
    if key in CACHE: return CACHE[key]
    q = qc.copy_empty_like(); nb = 0
    for ins in qc.data:
        if ins.operation.name == 'measure': continue
        q.append(ins)
        if ins.operation.name == 'barrier':
            nb += 1
            if nb == 2 and theta: q.append(CircuitInstruction(RZGate(theta), [q.qubits[3]]))
    CACHE[key] = Statevector(q).probabilities(); return CACHE[key]
CIRC = {l: c for b in BLOCKS for m in MSGS for l, c in block_circuits(b, m)}; CIRC.update(dict(probe_circuits()))
def draw(rng, label, e, theta, shots):
    p = probs(label, CIRC[label], theta).reshape(4, 16)          # [bob, alice]
    pal = p.sum(0); p = (1 - e) * p + e * pal[None, :] / 4
    idx = rng.choice(64, size=shots, p=(p.ravel() / p.sum())); return (idx % 16, idx // 16)
def world(seed, eL, eB, thL, boot=200):
    rng = np.random.default_rng(seed); raw = {}
    for L in LAYS:
        for b in BLOCKS:
            for m in MSGS:
                for bs in BASES9: raw[f'{L}|{b}_{m}_{bs}'] = draw(rng, f'{b}_{m}_{bs}', eL[L], thL[L], SH)
        for j in range(3):
            for _, ax in PROBES: raw[f'{L}|probe_s{j}_{ax}'] = draw(rng, f'probe_s{j}_{ax}', eL[L], thL[L], SHP)
    for bs in BASES9: raw[f'kg|native_product_HT_{bs}'] = draw(rng, f'native_product_HT_{bs}', eL['theirs'], thL['theirs'], SH)
    for b in BLOCKS:
        for m in MSGS:
            for bs in BASES9: raw[f'jobB|{b}_{m}_{bs}'] = draw(rng, f'{b}_{m}_{bs}', eB, thL['theirs'], SH)
    return analyse(raw, boot)
def brief(r):
    o = {'KG': r['KNOWN_GOOD']['passed']}
    for m in MSGS:
        o[m] = dict(f_theirs=round(r['THEIRS'][m]['f_one_job']['f'], 3), f_minus_1=r['THEIRS'][m]['f_minus_1']['outcome'], drift_native=r['DRIFT'][m]['native']['outcome'],
                    f_shift=round(r['DRIFT'][m]['f_cross_minus_f_one_job']['shift'], 3), layout_native=r['LAYOUT'][m]['native']['outcome'][:5], layout_f=r['LAYOUT'][m]['f']['outcome'][:5])
    o['finger_leg3'] = {L: (round(r['FINGER']['per_layout'][L][3]['angle'], 3), r['FINGER']['per_layout'][L][3]['resolved']) for L in LAYS}
    o['finger_chi2_leg3'] = r['FINGER']['chi2_leg3']['outcome'][:5]
    return o
if __name__ == '__main__':
    E = 0.15; same = {L: E for L in LAYS}; z = {L: 0.0 for L in LAYS}
    W = {'NULL': (same, E, z), 'LAYOUT': ({'theirs': 0.15, 'best': 0.08, 'q50': 0.25}, 0.15, z), 'DRIFT': (same, E + 0.03, z),
         'FINGER': (same, E, {'theirs': 0.16, 'best': 0.0, 'q50': 0.0}), 'BOTH': ({'theirs': 0.15, 'best': 0.08, 'q50': 0.25}, 0.18, z),
         'NEITHER_but_rotated': (same, E, {L: 0.16 for L in LAYS})}
    res = {}
    for i, (k, (eL, eB, th)) in enumerate(W.items()):
        res[k] = brief(world(100 + i, eL, eB, th)); print(k, json.dumps(res[k]), flush=True)
    fl = {}; ang = {2: [], 3: []}
    for rep in range(30):
        r_ = world(1000 + rep, same, E, z, boot=40); b = brief(r_)
        for q in (2, 3): ang[q] += [r_['FINGER']['per_layout'][L][q]['angle'] for L in LAYS]
        for m in MSGS:
            for key in ('f_minus_1', 'drift_native', 'layout_native', 'layout_f'):
                fl.setdefault(f'{m}.{key}', {}).setdefault(b[m][key], 0); fl[f'{m}.{key}'][b[m][key]] += 1
        fl.setdefault('finger_chi2_leg3', {}).setdefault(b['finger_chi2_leg3'], 0); fl['finger_chi2_leg3'][b['finger_chi2_leg3']] += 1
        fl.setdefault('KG_fail', 0); fl['KG_fail'] += int(not b['KG'])
    floor = {str(q): float(np.percentile(ang[q], 95)) for q in (2, 3)}; fl['finger_null_angle_p95'] = floor
    res['FLOOR_30_null_reps'] = fl; print('FLOOR', json.dumps(fl), flush=True)
    if '--write-floor' in sys.argv: json.dump(floor, open('finger_floor.json', 'w'))
    pw = {'product_HT': {}, 'bell_30_70': {}}
    for rep in range(20):
        b = brief(world(2000 + rep, same, E + 0.03, z, boot=40))
        for m in MSGS: pw[m].setdefault(b[m]['drift_native'], 0); pw[m][b[m]['drift_native']] += 1
    res['POWER_DRIFT_e+0.03_20reps'] = pw; print('POWER', json.dumps(pw))
    open('synth_results_tele.text', 'w').write(json.dumps(res, indent=1))
