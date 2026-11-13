"""vqc.py -- Kumar fill for Zenodo 10.5281/zenodo.23382139 (Patnaik, Saragadam, Chowdary; Raghu Engineering College / Miracle Education Society).
Their circuit vendored from their release (qcancer/circuits.py, data.py, hardware.py: plain functions, re-typed here, nothing run from the download):
ZFeatureMap(4, reps=1) composed with RealAmplitudes(4, reps=3, linear), measure_all, parity readout (class = parity of all 4 bits).
Features: Wisconsin (sklearn), stratified 80/20 split seed 42, StandardScaler -> PCA(4, seed 42) -> MinMax to [0, pi] fitted on train, test clipped.
Weights and the 84 test indices are their released hwset_wisconsin_z1_ibm_fez_s42.json. Their fez run: opt 3, physical [144, 143, 142, 141], 1,024 shots."""
import json, numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from qiskit.circuit.library import z_feature_map, real_amplitudes
from qiskit.quantum_info import Statevector, Operator
SHOTS = 1024
H = json.load(open(__file__.replace('vqc.py', 'hwset_wisconsin_z1_ibm_fez_s42.json')))
W = np.array(H['set']['weights']); IDX = H['set']['test_indices']
def features():
    d = load_breast_cancer(); X, y = d.data, (1 - d.target).astype(int)
    tr, te = train_test_split(np.arange(len(y)), test_size=0.2, stratify=y, random_state=42)
    sc = StandardScaler().fit(X[tr]); pca = PCA(n_components=4, random_state=42).fit(sc.transform(X[tr]))
    Ptr, Pte = pca.transform(sc.transform(X[tr])), pca.transform(sc.transform(X[te])); ang = MinMaxScaler((0, np.pi)).fit(Ptr)
    Q = np.clip(ang.transform(Pte), 0, np.pi); pos = {int(i): k for k, i in enumerate(te)}
    rows = [pos[i] for i in IDX]; return Q[rows], y[te][rows]
def circuit(x):
    fm, an = z_feature_map(4, reps=1), real_amplitudes(4, reps=3, entanglement='linear')
    c = fm.assign_parameters(dict(zip(fm.parameters, x))).compose(an.assign_parameters(dict(zip(an.parameters, W)))); c.measure_all(); return c
def p_exact(x):
    c = circuit(x).remove_final_measurements(inplace=False); pr = Statevector(c).probabilities()
    return float(sum(p for k, p in enumerate(pr) if bin(k).count('1') % 2 == 1))
def p1_counts(counts):
    n = sum(counts.values()); return sum(v for b, v in counts.items() if b.count('1') % 2 == 1) / n
