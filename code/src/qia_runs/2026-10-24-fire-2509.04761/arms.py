"""arms.py -- the four arms + readout calibration for the 2509.04761 re-test on ibm_fez (our rebuild; aqcel_rebuild.py).
Arms (logical circuit -> generate_preset_pass_manager(backend=fez, optimization_level=3, seed_transpiler=SEED), as the paper: level 3):
  Q    Qiskit-only: the original 1-step QPS circuit
  V1   Aqcel-v1 (our exact-probability rebuild), threshold 0.01 (Table 2 main entries are threshold 0.01)
  V2   Aqcel-v2 (our rebuild), threshold 0.01
  CTRL the transpiled V2 ISA circuit with every cz instruction deleted (same physical qubits, same single-qubit layer, same measurements)
Calibration: CAL0 (measure the union of all arms' measured physical qubits) and CAL1 (X on each, then measure), for a tensored per-qubit
readout correction applied to every arm (stands in for the paper's M3; stated).
Layout in the job: ROUNDS rounds of [CAL0, CAL1, Q, V1, V2, CTRL]; arm shots SHOTS per copy, calibration CAL_SHOTS per copy."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import aqcel_rebuild as A
from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

THR = 0.01
SEED = 11
ROUNDS = 4
SHOTS = 5000
CAL_SHOTS = 2500
ARMS = ('Q', 'V1', 'V2', 'CTRL')


def logical():
    qc = A.qps1()
    v1 = A.aqcel(qc, THR, 1)[0]
    v2 = A.aqcel(qc, THR, 2)[0]
    return {'Q': qc, 'V1': v1, 'V2': v2}


def strip_cz(isa):
    out = isa.copy_empty_like()
    for ins in isa.data:
        if ins.operation.name != 'cz':
            out.append(ins.operation, ins.qubits, ins.clbits)
    return out


def measured_physical(isa):
    """clbit index -> physical qubit index for every measure"""
    m = {}
    for ins in isa.data:
        if ins.operation.name == 'measure':
            m[isa.find_bit(ins.clbits[0]).index] = isa.find_bit(ins.qubits[0]).index
    return [m[i] for i in range(6)]


def build(backend):
    L = logical()
    pm = generate_preset_pass_manager(backend=backend, optimization_level=3, seed_transpiler=SEED)
    isa = {k: pm.run(v) for k, v in L.items()}
    isa['CTRL'] = strip_cz(isa['V2'])
    meas = {k: measured_physical(isa[k]) for k in ARMS}
    union = sorted({q for k in ARMS for q in meas[k]})
    n = backend.num_qubits
    cal = {}
    for lab, flip in (('CAL0', False), ('CAL1', True)):
        c = QuantumCircuit(n, len(union))
        for j, q in enumerate(union):
            if flip:
                c.x(q)
        for j, q in enumerate(union):
            c.measure(q, j)
        cal[lab] = c
    # calibration circuits are already ISA (x and measure on physical qubits); no transpile so the qubits stay put
    plan, circs, shots = [], [], []
    for r in range(ROUNDS):
        for lab in ('CAL0', 'CAL1') + ARMS:
            plan.append((lab, r)); circs.append(cal[lab] if lab.startswith('CAL') else isa[lab])
            shots.append(CAL_SHOTS if lab.startswith('CAL') else SHOTS)
    return dict(logical=L, isa=isa, meas=meas, union=union, plan=plan, circs=circs, shots=shots)


def noiseless_isa_dist(isa, meas):
    """exact output over the 6 measured clbits of a transpiled circuit (statevector on the active physical qubits only)"""
    import numpy as np
    from qiskit.quantum_info import Statevector
    active = sorted({isa.find_bit(q).index for ins in isa.data for q in ins.qubits})
    idx = {p: i for i, p in enumerate(active)}
    small = QuantumCircuit(len(active))
    for ins in isa.data:
        if ins.operation.name in ('measure', 'barrier', 'delay'):
            continue
        small.append(ins.operation, [idx[isa.find_bit(q).index] for q in ins.qubits])
    pr = Statevector(small).probabilities([idx[p] for p in meas])
    return {format(k, '06b'): float(v) for k, v in enumerate(pr) if v > 1e-15}
