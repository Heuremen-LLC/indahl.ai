import sys, json, numpy as np, os
R=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, R); os.chdir(R)
import twin_cauca as T
d = json.load(open('theirs/figures_data_L2.json'))
hw = np.array(d['fidelity']['raw']['mean'])
circs = T.load_circuits('L2'); P = T.load_props('theirs/properties_L2.json')
base = np.array(T.target_prob_exact(circs, T.noise_model(P, zz='direct', readout='ibm'), P, readout='ibm'))
for f2, f1 in ((1.302,1.306),(1.311,1.366),(1.345,1.344),(1.345,1.366),(1.302,1.366),(1.21,1.306),(1.39,1.366)):
    t = np.array(T.target_prob_exact(circs, T.noise_model(P, f2=f2, f1=f1, zz='direct', readout='ibm'), P, readout='ibm'))
    closed = (base - t) / (base - hw)
    print(f'f2={f2} f1={f1}', ' '.join(f'{v:+.4f}' for v in closed))
