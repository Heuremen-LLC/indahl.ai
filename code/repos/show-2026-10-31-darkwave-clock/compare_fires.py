"""compare_fires.py FIRST_DAYDIR SECOND_DAYDIR KEYSTONE_PROPS -- defined after the data (1 Nov 2026, after the outside referee of the second
ibm_marrakesh fire). For both fires of one chip: the per-qubit sign count of |residual M31| against |residual MT| (pooled and per copy, exact
two-sided sign test), the median size of each table's residual, the signed medians of MC and M31, and the count of qubits whose M31 residual is
opposite in sign to the kick. Then the IBM records: the one the 31 Oct table ran under (KEYSTONE_PROPS) against the second fire's record before
job C, per untouched qubit. Writes SECOND_DAYDIR/readings_compare.text. The FINAL rule and every committed reading are unchanged."""
import sys, os, json
from math import comb
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import keystone as K, clock as C
def load(D):
    rec = json.load(open(f'{D}/job_clock.json')); keys = [tuple(k) for k in rec['keys']]; S = rec['S']
    def Z(lab):
        z = np.load(f'{D}/raw_{lab}.npz'); o = list(range(len(keys))) if lab == 'A' else list(range(len(keys)))[::-1]
        return {keys[i]: z[f'fin_{i}'] for i in o}
    ZA, ZB = Z('A'), Z('B'); nq = len(S); rd = lambda Zc: C.read(Zc, nq, np.random.default_rng(31), B=10)[1]
    return rec, S, rd({k: [ZA[k], ZB[k]] for k in ZA}), rd({k: [v] for k, v in ZA.items()}), rd({k: [v] for k, v in ZB.items()})
def st(k):
    w = int(np.sum(np.abs(k['M31']) > np.abs(k['MT']))); b = int(np.sum(np.abs(k['M31']) < np.abs(k['MT']))); n = w + b
    return w, b, min(1.0, 2 * sum(comb(n, i) for i in range(min(w, b) + 1)) / 2 ** n)
L = ['DEFINED AFTER THE DATA (1 Nov 2026, after the outside referee). Both fires of one chip side by side; committed readings unchanged.']
for D in sys.argv[1:3]:
    rec, S, kp, ka, kb = load(D); n = os.path.basename(D.rstrip('/'))
    L.append(f'{n}: sign count pooled %d against %d p=%.3f | copy A %d against %d p=%.3f | copy B %d against %d p=%.3f' % (*st(kp), *st(ka), *st(kb)))
    L.append(f'{n}: median |residual| M31 {np.median(np.abs(kp["M31"])):.3f} MT {np.median(np.abs(kp["MT"])):.3f} | signed median MC {np.median(kp["MC"]):+.3f} M31 {np.median(kp["M31"]):+.3f} | median kick M {np.median(kp["M"]):+.3f} deg/readout')
    L.append(f'{n}: M31 residual opposite in sign to the kick (over-correction) on {int(np.sum(np.sign(kp["M31"]) != np.sign(kp["M"])))} of {len(S)} qubits')
    L.append(f'{n}: shot-noise scale (copy-to-copy half-difference median) M31 {np.median(np.abs(ka["M31"] - kb["M31"])) / 2:.3f} MT {np.median(np.abs(ka["MT"] - kb["MT"])) / 2:.3f} deg/readout')
a = json.load(open(sys.argv[3])); b = json.load(open(os.path.join(sys.argv[2], 'props_before_C.json'))); S = json.load(open(os.path.join(sys.argv[2], 'job_clock.json')))['S']
def g(d, q, nm):
    for p in d['qubits'][q]:
        if p['name'] == nm: return p['value']
L.append(f'IBM records: the 31 Oct table ran under {a["last_update_date"]}, the second fire under {b["last_update_date"]}')
for nm in ('T1', 'T2', 'readout_error', 'readout_length'):
    pr = [(g(a, q, nm), g(b, q, nm)) for q in S]; pr = [(x, y) for x, y in pr if x is not None and y is not None]
    L.append(f'  {nm} changed on {sum(x != y for x, y in pr)} of {len(pr)} untouched qubits')
out = os.path.join(sys.argv[2], 'readings_compare.text'); open(out, 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
