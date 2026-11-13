"""r4_both_variants.py -- ADDENDUM 1 promise: R4 (twin - hardware) with BOTH twin variants side by side, from the record saved before job 1.
Also (POST-HOC, defined after the data): per-clbit loss at N=2 from our counts, mapped to physical qubits through their transpiled circuit."""
import json, sys, numpy as np
sys.path.insert(0, '.'); import twin_cauca as T, cauca as C
circs = T.load_circuits('L2'); P = T.load_props('props_cauca_before_1.json')
hw = np.array(C.job_P(1)) if hasattr(C, 'job_P') else None
paper = np.array(T.target_prob_exact(circs, T.noise_model(P, zz='direct', readout='ibm'), P, readout='ibm'))
nb = np.array(T.target_prob_exact(circs, T.noise_model(P, zz='residual', readout='coded'), P, readout='coded'))
print('N           ', '  '.join(f'{n:6d}' for n in range(2, 10)))
print('twin PAPER  ', '  '.join(f'{v:6.4f}' for v in paper)); print('twin NOTEBK ', '  '.join(f'{v:6.4f}' for v in nb))
raw = json.load(open('raw_cauca_1.json')); c2 = [e['counts'] for e in raw if e['N'] == 2]
tot = {}; [tot.__setitem__(k, tot.get(k, 0) + v) for c in c2 for k, v in c.items()]; n = sum(tot.values())
print('N=2 job1 counts', tot, 'P(11) =', round(tot.get('11', 0) / n, 4))
c = circs[0]; mm = [(c.find_bit(i.qubits[0]).index, c.find_bit(i.clbits[0]).index) for i in c.data if i.operation.name == 'measure']
print('N=2 measure map (physical qubit -> clbit):', mm)
for q, cb in mm:
    lost = sum(v for k, v in tot.items() if k[::-1][cb] == '0'); print(f'  physical q{q} (clbit {cb}): read 0 on {lost}/{n} = {lost/n:.4f} of shots meant to read 1; record prob_meas0_prep1 =', [x['value'] for x in P['qubits'][q] if x['name']=='prob_meas0_prep1'] if isinstance(P, dict) and 'qubits' in P else 'see props')
