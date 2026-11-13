"""twin.py -- our re-implementation of the Cauca digital twin (read as TEXT from their notebook cell 33; nothing of theirs executed).
Inputs: their released run_0X/job_metadata.json (the transpiled circuits as submitted, QPY inside) and run_0X/properties.json (job.properties()).
Two versions exist. RELEASED notebook (zz='residual', readout='coded') reproduces their released processed/figures_data_*.json twin columns bit-exactly,
but those are NOT the twin numbers printed in the paper's Table A1. PAPER twin (zz='direct': ZZ probability = stated value, readout='ibm') reproduces
Table A1 (L2) to <= 0.0035 per N. Default here = the paper twin.
Construction (their notebook): per-qubit T1/T2; gates sx, x, id: thermal_relaxation(T1,T2,t_gate) composed with a depolarizing error solved so the total
average-gate infidelity equals the stated gate_error; gate cz on ordered pairs (i,i+1): thermal_q0 (x) thermal_q1, then ZZ Pauli error with
p_zz = (p_gate - infid_thermal)/(1 - infid_thermal); readout: ReadoutError [[1-P01,P01],[P10,1-P10]] with P01 = prob_meas0_prep1, P10 = prob_meas1_prep0.
Scale knobs: f2 multiplies the stated cz gate_error, f1 multiplies the stated sx/x/id gate_error (T1, T2, readout untouched).
Copy of fill_cauca_2605_30676/src/twin.py (paper twin = default), loaders pointed at this folder's theirs/. Use: venv_quantum python, run with -I."""
import json, base64, zlib, io, sys
import numpy as np
from collections import Counter
from qiskit import qpy
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error, pauli_error, thermal_relaxation_error
from qiskit.quantum_info import average_gate_fidelity
from scipy.optimize import brentq

import os
HERE = os.path.dirname(os.path.abspath(__file__))
NREP, SHOTS, NQ = 20, 2048, 9

def load_circuits(level):
    m = json.load(open(f'{HERE}/theirs/job_metadata_{level}.json'))
    cs = []
    for pub in m['params']['pubs']:
        raw = zlib.decompress(base64.b64decode(pub[0]['__value__']))
        cs.append(qpy.load(io.BytesIO(raw))[0])
    return cs

def load_props(path_or_dict):
    pr = path_or_dict if isinstance(path_or_dict, dict) else json.load(open(path_or_dict))
    def val(lst, name):
        for p in lst:
            if p['name'] == name: return p['value']
    T1, T2, P01, P10 = {}, {}, {}, {}
    for q in range(NQ):
        qp = pr['qubits'][q]
        T1[q] = val(qp, 'T1') * 1e-6; T2[q] = val(qp, 'T2') * 1e-6
        P01[q] = val(qp, 'prob_meas0_prep1'); P10[q] = val(qp, 'prob_meas1_prep0')
    ge, gt = {}, {}
    for g in pr['gates']:
        qs = tuple(g['qubits'])
        if g['gate'] == 'cz' and len(qs) == 2 and qs[1] == qs[0] + 1 and qs[0] < NQ - 1:
            ge[('cz', qs)] = val(g['parameters'], 'gate_error'); gt[('cz', qs)] = val(g['parameters'], 'gate_length')
        elif g['gate'] in ('sx', 'x', 'id') and len(qs) == 1 and qs[0] < NQ:
            ge[(g['gate'], qs[0])] = val(g['parameters'], 'gate_error'); gt[(g['gate'], qs[0])] = val(g['parameters'], 'gate_length')
    return dict(T1=T1, T2=T2, P01=P01, P10=P10, ge=ge, gt=gt, gates=sorted({g['gate'] for g in pr['gates']}), date=pr['last_update_date'])

def resid_depol(p, relax, nq):
    nt = 4 ** nq
    def f(lam): return (1 - average_gate_fidelity(depolarizing_error(lam, nq).compose(relax).to_quantumchannel())) - p
    if f(0.0) >= 0: return 0.0
    return brentq(f, 0.0, nt / (nt - 1))

def noise_model(P, f2=1.0, f1=1.0, zz='direct', readout='ibm'):
    nm = NoiseModel()
    for q in range(NQ):
        for g in ('sx', 'x', 'id'):
            if (g, q) in P['ge']:
                p = P['ge'][(g, q)] * f1; tg = P['gt'][(g, q)] * 1e-9
                th = thermal_relaxation_error(P['T1'][q], P['T2'][q], tg)
                nm.add_quantum_error(depolarizing_error(resid_depol(p, th, 1), 1).compose(th), g, [q])
    for (g, pair), p0 in P['ge'].items():
        if g != 'cz': continue
        p = p0 * f2; q0, q1 = pair; tg = P['gt'][(g, pair)] * 1e-9
        th = thermal_relaxation_error(P['T1'][q0], P['T2'][q0], tg).tensor(thermal_relaxation_error(P['T1'][q1], P['T2'][q1], tg))
        it = 1 - average_gate_fidelity(th.to_quantumchannel())
        pz = max(0.0, (p - it) / (1 - it)) if zz == 'residual' else min(1.0, p)
        nm.add_quantum_error(pauli_error([('ZZ', pz), ('II', 1 - pz)]).compose(th), g, [q0, q1])
    for q in range(NQ):
        a, b = P['P01'][q], P['P10'][q]   # a = prob_meas0_prep1, b = prob_meas1_prep0
        if readout == 'coded': mat = [[1 - a, a], [b, 1 - b]]       # released notebook as written: ideal0 -> read1 with a
        else: mat = [[1 - b, b], [a, 1 - a]]                         # IBM definition: ideal0 -> read1 with prob_meas1_prep0 = b
        nm.add_readout_error(ReadoutError(mat), [q])
    return nm

def target_prob_sampled(circs, nm):
    """their procedure: N=2..9, 20 reps, seeds 0..19, 2048 shots; target = all ones (c_state)."""
    out = []
    for i, N in enumerate(range(2, 10)):
        v = []
        for j in range(NREP):
            sim = AerSimulator(noise_model=nm, seed_simulator=j)
            c = sim.run(circs[i * NREP + j], shots=SHOTS).result().get_counts()
            tot = sum(c.values()); ones = '1' * N
            # their key handling: bs = bitstring[::-1].zfill(N)[-N:]; the target is all ones so ordering is irrelevant
            v.append(c.get(ones, 0) / tot)
        out.append((float(np.mean(v)), float(1.96 * np.std(v, ddof=1) / np.sqrt(NREP))))
    return out

def target_prob_exact(circs, nm, P, readout='ibm'):
    """exact P(read all ones) per N via density matrix on the unitary part (measures stripped), then the readout confusion applied analytically.
    Gate noise = the noise model's quantum errors (readout errors in nm are not used here; P gives them)."""
    from qiskit import QuantumCircuit
    out = []
    for i, N in enumerate(range(2, 10)):
        qc = circs[i * NREP]
        meas = [(qc.find_bit(ins.qubits[0]).index, qc.find_bit(ins.clbits[0]).index) for ins in qc.data if ins.operation.name == 'measure']
        qs = sorted(q for q, _ in meas)
        assert len(qs) == N, (N, meas)
        new = QuantumCircuit(qc.num_qubits)
        for ins in qc.data:
            if ins.operation.name in ('measure', 'barrier'): continue
            new.append(ins.operation, [qc.find_bit(q).index for q in ins.qubits])
        new.save_probabilities_dict(qs)
        sim = AerSimulator(noise_model=nm, method='density_matrix')
        pd = sim.run(new, shots=1).result().data()['probabilities']   # keys: hex or bitstring over qs, qs[0] is the LSB
        # readout: P(read all ones) = sum_s P(s) prod_q (1-P01[q] if s_q=1 else P10[q])
        tot = 0.0
        for k, p in pd.items():
            b = format(k if isinstance(k, int) else (int(k, 16) if str(k).startswith('0x') else int(k, 2)), f'0{N}b')[::-1]   # b[t] is the bit of qs[t]
            w = 1.0
            for t, q in enumerate(qs):
                # AS CODED in their notebook: ReadoutError([[1-P01,P01],[P10,1-P10]]), P01 = prob_meas0_prep1, P10 = prob_meas1_prep0;
                # Aer row = ideal bit, column = measured bit, so P(read1 | ideal1) = 1-P10 and P(read1 | ideal0) = P01.
                if readout == 'coded': w *= (1 - P['P10'][q]) if b[t] == '1' else P['P01'][q]
                else: w *= (1 - P['P01'][q]) if b[t] == '1' else P['P10'][q]
            tot += p * w
        out.append(tot)
    return out

