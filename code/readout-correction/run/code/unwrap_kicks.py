"""unwrap_kicks.py -- per-qubit TOTAL phase (M minus D) at N = 2, 4, 8 from the committed 21 Oct control run, arm S, copies pooled.
Branch rule (fixed before any keystone job): t2 = wrapped total at N=2 (alias-free while |kick| < 90 deg/readout); the N=4 total is the
branch of wrap(t4) nearest 2*t2; the N=8 total is the branch of wrap(t8) nearest 2*t4. kick = t8_unwrapped / 8. A qubit whose unwrapped
N=8 kick differs from the wrapped one is printed. Writes the unwrapped kick into committed_kicks_<chip>.json as field 'kick_unwrapped'."""
import json, sys, os, numpy as np
CR = os.path.expanduser('../earlier_runs/control_run'); sys.path.insert(0, CR)
from analyze import bits, wrap
HERE = os.path.dirname(os.path.abspath(__file__))
def near(x, ref): return x + 2 * np.pi * np.round((ref - x) / (2 * np.pi))
for chip in ('ibm_kingston', 'ibm_marrakesh'):
    rec = json.load(open(f'{CR}/job_{chip}.json')); z = np.load(f'{CR}/raw_{chip}.npz'); meta = rec['meta']; S = rec['S']
    idx = lambda **kw: [i for i, m in enumerate(meta) if all(m.get(k) == v for k, v in kw.items())]
    def ph(mode, N, k):
        a = {s: np.concatenate([z['fin_%d' % i] for c in (0, 1) for i in idx(copy=c, arm='S', mode=mode, N=N, setting=s)]) for s in ('XX', 'YY')}
        return np.arctan2((1 - 2 * bits(a['YY'], k)).mean(), (1 - 2 * bits(a['XX'], k)).mean())
    J = json.load(open(f'{HERE}/committed_kicks_{chip}.json')); K = J['kicks_deg_per_readout']; changed = []
    for k, q in enumerate(S):
        t = {N: wrap(ph('M', N, k) - ph('D', N, k)) for N in (2, 4, 8)}
        t4 = near(t[4], 2 * t[2]); t8 = near(t[8], 2 * t4); ku = float(np.degrees(t8) / 8)
        K[str(q)] = K[str(q)][:6] + [round(ku, 4), round(float(np.degrees(t[2]) / 2), 4), round(float(np.degrees(t4) / 4), 4)]
        if abs(ku - K[str(q)][0]) > 1: changed.append((q, K[str(q)][0], round(ku, 2), round(float(np.degrees(t[2]) / 2), 2), round(float(np.degrees(t4) / 4), 2)))
    J['fields'] = 'kick8_wrapped, lo95, hi95, coherenceD, kick8_copy0, kick8_copy1, kick_unwrapped(N=8 via N=2,4 branches), kick_N2, kick_N4_unwrapped'
    json.dump(J, open(f'{HERE}/committed_kicks_{chip}.json', 'w'), indent=0)
    ku = np.array([v[6] for v in K.values()])
    print(f'{chip}: unwrapped median {np.median(ku):+.3f}, range {ku.min():+.2f}..{ku.max():+.2f}; branch changed on {len(changed)} qubits: {changed}')
