"""circuits.py -- my own rebuild of the state-preparation circuit published in build_2.py (read as text, never run):
build_state_prep_circuit(): QuantumCircuit(n); H on every qubit (init 'plus'); PauliEvolutionGate(H_op, time=t, synthesis=LieTrotter(reps));
measure_all.  get_samples(mode='aer_noise'): two circuits, t0 = 0.6 at shots*(1-eta) and t1 = 1.2 at shots*eta with eta = 0.2, counts
merged; trotter_reps default 1.  These are the ONLY released settings: the paper does not print t, reps, layout or shots for its
ibmq_pittsburgh samples (flagged in the plan).  Control (ours): the same H layer, no evolution, measure_all (no entangling gate).
Readout seats (ours): |0...0> and X on all -> |1...1>, measure_all."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.synthesis.evolution import LieTrotter
from assqd import sparse_pauli_op

T0, T1, ETA, SHOTS, SEAT_SHOTS = 0.6, 1.2, 0.2, 3000, 1000
SH0 = int(SHOTS * (1 - ETA)); SH1 = int(SHOTS * ETA)          # 2400 / 600, as build_2 int(shots*(1-c)), int(shots*c)

def trotter(n, terms, t, reps=1, name=''):
    qc = QuantumCircuit(n, name=name); qc.h(range(n))
    qc.append(PauliEvolutionGate(sparse_pauli_op(n, terms), time=t, synthesis=LieTrotter(reps=reps)), list(range(n))); qc.measure_all(); return qc

def control(n, name='ctrl'):
    qc = QuantumCircuit(n, name=name); qc.h(range(n)); qc.measure_all(); return qc

def seat(n, one, name=''):
    qc = QuantumCircuit(n, name=name)
    if one: qc.x(range(n))
    qc.measure_all(); return qc

def ideal_probs(qc):
    """noiseless output distribution over integers (qubit q = bit q)"""
    from qiskit.quantum_info import Statevector
    from qiskit import transpile
    q = transpile(qc.remove_final_measurements(inplace=False), basis_gates=['cx', 'rz', 'sx', 'x', 'h', 'rx', 'ry', 'rzz', 'rxx', 'ryy'], optimization_level=0)
    return np.abs(Statevector(q).data) ** 2

def rings(cmap_edges, size=12):
    """all simple cycles of length `size` in the undirected coupling graph (heavy-hex cells are 12-rings)"""
    import networkx as nx
    G = nx.Graph(); G.add_edges_from(cmap_edges); out = set(); res = []
    for cyc in nx.simple_cycles(G, length_bound=size):
        if len(cyc) == size:
            key = frozenset(cyc)
            if key not in out: out.add(key); res.append(cyc)
    return res
