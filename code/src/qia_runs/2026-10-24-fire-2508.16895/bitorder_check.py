"""bitorder_check.py -- fhat() on noiseless Qiskit-format counts (Statevector.sample_counts, clbit 0 rightmost) for every planned pair: must equal exact within shot noise."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from swaprun import *
from qiskit.quantum_info import Statevector
P = select(curves()); np.random.seed(7); bad = 0
for p in P:
    qc = build(p['a'], p['b']); qc.remove_final_measurements(); c = Statevector(qc).sample_counts(20000)
    f, n = fhat(c); z = (f - p['F']) / np.sqrt(max(1 - p['F'] ** 2, 1e-9) / n); bad += abs(z) > 4
    print(f"{p['cls']:>6} {p['A']:>3}-{p['B']:<3} exact {p['F']:.4f} fhat {f:.4f} z {z:+.2f}")
print('BIT-ORDER CHECK', 'PASS' if bad == 0 else f'FAIL ({bad})')
