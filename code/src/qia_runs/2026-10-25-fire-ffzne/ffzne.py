"""ffzne.py -- Kumar fill for arXiv 2603.13949 (IISc Bangalore; no funder named): FF-ZNE, 'layout as the noise knob'.
Vendored from their released notebook (github dream-lab/quantum-FF-ZNE, vqe/zne_vqe_50qubits_reps_123_HW.ipynb), re-typed, nothing run from the download:
build_qic (H on all, CX chain, H on all; Clifford, ideal <Z>avg = 1), observable = mean of Z_i over 50 qubits, cost_func (record-built layout error
score at opt 0 with T1/T2 idle error), idle_error. Their hardware options: Estimator, resilience 0, TREX on, gate twirling auto, DD XY4, 10,000 shots.
FF-ZNE: three layouts (best / equidistant middle / worst score), linear extrapolation of <Z> to score 0."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
N = 50
def build_qic(n=N, reps=1):
    qc = QuantumCircuit(n)
    for r in range(reps):
        for q in range(n): qc.h(q)
        for i in range(n - 1): qc.cx(i, i + 1)
        for q in range(n): qc.h(q)
        if r != reps - 1: qc.barrier()
    return qc
def observable(n=N):
    return SparsePauliOp(['I' * (i - 1) + 'Z' + 'I' * (n - i) for i in range(1, n + 1)], coeffs=[1 / n] * n)
def idle_error(time, t1, t2):
    t2 = min(t1, t2); p_reset = 1 - np.exp(-time / t1); p_z = (1 - p_reset) * (1 - np.exp(-time * (1 / t2 - 1 / t1))) / 2; return p_z + p_reset
def cost_func(circ, layouts, backend, props):
    """theirs (paths through a qubit with no record T1/T2 are excluded before scoring, so the None guard never fires on a chosen path), with the record passed in (so every score uses the one record saved before the job)."""
    out = []; dt = backend.configuration().dt; nq = backend.configuration().num_qubits
    t1s, t2s = [], []
    for q in range(nq):
        try: t1s.append(props.qubit_property(q, 'T1')[0]); t2s.append(props.qubit_property(q, 'T2')[0])
        except Exception: t1s.append(None); t2s.append(None)
    for layout in layouts:
        sch = generate_preset_pass_manager(optimization_level=0, backend=backend, initial_layout=layout).run(circ)
        fid = 1.0; touched = set()
        for it in sch.data:
            nm = it.operation.name
            if nm in ('cx', 'cz', 'ecr'):
                q0, q1 = sch.find_bit(it.qubits[0]).index, sch.find_bit(it.qubits[1]).index; fid *= 1 - props.gate_error(nm, [q0, q1]); touched |= {q0, q1}
            elif nm in ('sx', 'x'):
                q0 = sch.find_bit(it.qubits[0]).index; fid *= 1 - props.gate_error(nm, q0); touched.add(q0)
            elif nm == 'measure':
                q0 = sch.find_bit(it.qubits[0]).index; fid *= 1 - props.readout_error(q0); touched.add(q0)
            elif nm == 'delay':
                q0 = sch.find_bit(it.qubits[0]).index
                if q0 in touched and t1s[q0] is not None: fid *= 1 - idle_error(it.operation.duration * dt, t1s[q0], t2s[q0])
        out.append((1 - fid, list(layout)))
    return out
def midpoint_index(L):
    """theirs (find_approx_equidistant_midpoint), as a direct search: the index minimising |(L[i]-L[0]) - (L[-1]-L[i])|."""
    return int(np.argmin([abs((x - L[0]) - (L[-1] - x)) for x in L]))
