"""known_good_circuit.py -- our rebuilt logical circuit, exact statevector at his stored incumbent after the first batched job (bps trace
x[0]; the search moved on job 1), CVaR against his stored noiseless ideal_cvar[0]. Pass: |diff| < 1e-9 for n = 8 and 10.
(First attempt compared at x0 = bps1 row 0 and failed: his stored value is at trace x[0], not x0; at x0 our circuit gives -3.4594029279
(n=8), equal to his own numpy model at x0. Kept as known_good_circuit_lums_FIRST_attempt.text.)"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lums, circuits_lums as CL
from qiskit.quantum_info import Statevector
ok = True
for n in (8, 10):
    d = lums.theirs(n); L = {j['tag']: j for j in d['ledger']['log']}; qc = CL.build(d); x0 = np.array(d['bps']['trace']['x'][0]); reps = d['provenance']['p']
    bind = {p: (x0[int(p.name[2:-1])] if p.name.startswith('b') else x0[reps + int(p.name[2:-1])]) for p in qc.parameters}
    q = qc.remove_final_measurements(inplace=False).assign_parameters(bind)
    # measurement maps position -> logical clbit via the final permutation; read it off the measure instructions
    perm = {qc.find_bit(ins.qubits[0]).index: qc.find_bit(ins.clbits[0]).index for ins in qc.data if ins.operation.name == 'measure'}
    pv = Statevector(q).probabilities(); P = np.zeros(2 ** n)
    for i, pr in enumerate(pv):
        j = 0
        for pos in range(n):
            if (i >> pos) & 1: j |= 1 << perm[pos]
        P[j] += pr
    cv = lums.Cvar(lums.energies(d)); ours = float(cv(P)); his = d['bps']['trace']['ideal_cvar'][0]
    p = abs(ours - his) < 1e-9; ok &= p; print(f'n={n}: noiseless CVaR at his trace x[0] ours {ours:+.10f} his stored {his:+.10f} -> {"PASS" if p else "FAIL"}')
print('CIRCUIT KNOWN-GOOD', 'PASS' if ok else 'FAIL')
