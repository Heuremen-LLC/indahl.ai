# Their L2 record's qubit 1 readout entry: what is it, and what does the paper twin give with it replaced by the median of the other qubits?
import sys, json, numpy as np, os
R = sys.argv[1]; sys.path.insert(0, R); os.chdir(R)
import twin_cauca as T
d = json.load(open('theirs/figures_data_L2.json')); hw = np.array(d['fidelity']['raw']['mean'])
circs = T.load_circuits('L2'); P = T.load_props('theirs/properties_L2.json')
print('keys in P', list(P)[:12])
print('P01 (meas0|prep1) q0..q9', [round(P['P01'][q], 4) for q in sorted(P["P01"])])
print('P10 (meas1|prep0) q0..q9', [round(P['P10'][q], 4) for q in sorted(P["P01"])])
base = np.array(T.target_prob_exact(circs, T.noise_model(P, zz='direct', readout='ibm'), P, readout='ibm'))
import copy; P2 = copy.deepcopy(P)
others = [q for q in P["P01"] if q != 1]
P2['P01'][1] = float(np.median([P['P01'][q] for q in others])); P2['P10'][1] = float(np.median([P['P10'][q] for q in others]))
fix = np.array(T.target_prob_exact(circs, T.noise_model(P2, zz='direct', readout='ibm'), P2, readout='ibm'))
print('N              ', ' '.join(f'{n:7d}' for n in range(2, 10)))
print('hardware       ', ' '.join(f'{v:7.4f}' for v in hw))
print('twin as printed', ' '.join(f'{v:7.4f}' for v in base), '| gap', ' '.join(f'{v:+7.3f}' for v in base - hw))
print('twin q1 median ', ' '.join(f'{v:7.4f}' for v in fix), '| gap', ' '.join(f'{v:+7.3f}' for v in fix - hw))
