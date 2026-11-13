# Recompute: how much of their N-player twin-hardware gap does scaling the stated CZ error by our delivered factor close? Their record, their hardware, paper twin.
import sys, json, numpy as np
R = sys.argv[1]; sys.path.insert(0, R); import os; os.chdir(R)
import twin_cauca as T
d = json.load(open('theirs/figures_data_L2.json')); print('fidelity keys', list(d['fidelity']))
hw = np.array(d['fidelity']['raw']['mean'])
circs = T.load_circuits('L2'); P = T.load_props('theirs/properties_L2.json')
base = np.array(T.target_prob_exact(circs, T.noise_model(P, zz='direct', readout='ibm'), P, readout='ibm'))
print('N        ', ' '.join(f'{n:7d}' for n in range(2, 10)))
print('hardware ', ' '.join(f'{v:7.4f}' for v in hw))
print('twin f2=1', ' '.join(f'{v:7.4f}' for v in base))
for f2 in (1.21, 1.30, 1.31, 1.39):
    t = np.array(T.target_prob_exact(circs, T.noise_model(P, f2=f2, zz='direct', readout='ibm'), P, readout='ibm'))
    closed = (base - t) / (base - hw)
    print(f'twin f2={f2}', ' '.join(f'{v:7.4f}' for v in t), '| share of gap closed', ' '.join(f'{v:+6.2f}' for v in closed))
print('their digital_twin column', ' '.join(f'{v:7.4f}' for v in d['fidelity']['digital_twin']['mean']) if isinstance(d['fidelity']['digital_twin'], dict) else d['fidelity']['digital_twin'])
for f2, f1 in ((1.21, 1.306), (1.30, 1.31), (1.39, 1.366)):
    t = np.array(T.target_prob_exact(circs, T.noise_model(P, f2=f2, f1=f1, zz='direct', readout='ibm'), P, readout='ibm'))
    closed = (base - t) / (base - hw)
    print(f'twin f2={f2} f1={f1}', ' '.join(f'{v:7.4f}' for v in t), '| closed', ' '.join(f'{v:+6.2f}' for v in closed))
