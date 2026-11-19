"""kg_perqubit_from_control.py -- per-qubit kick (deg per readout) on ibm_kingston from the COMMITTED 21 Oct control run, through the
committed analyze.py functions (bits, wrap) and its expv/phase lines copied verbatim (arm S, N = 8, M vs D8, copies pooled).
Width: shot bootstrap (400 draws). Used only to choose the known-good rule for the Page-Wootters run, before any Page-Wootters job."""
import json, sys, os, numpy as np
CR = '../earlier_runs/control_run'; sys.path.insert(0, CR)
from analyze import bits, wrap
rec = json.load(open(f'{CR}/job_ibm_kingston.json')); z = np.load(f'{CR}/raw_ibm_kingston.npz'); meta = rec['meta']; S = rec['S']
def idx(**kw): return [i for i, m in enumerate(meta) if all(m.get(k) == v for k, v in kw.items())]
def arr(arm, mode, N, setting): return np.concatenate([z['fin_%d' % i] for c in (0, 1) for i in idx(copy=c, arm=arm, mode=mode, N=N, setting=setting)])
want = [int(x) for x in sys.argv[1:]] or S
rng = np.random.default_rng(7)
A = {k: arr('S', m, 8, s) for k, (m, s) in {'MX': ('M', 'XX'), 'MY': ('M', 'YY'), 'DX': ('D', 'XX'), 'DY': ('D', 'YY')}.items()}
for q in want:
    k = S.index(q); b = {n: 1 - 2 * bits(a, k) for n, a in A.items()}
    f = lambda d: np.degrees(wrap(np.arctan2(d['MY'].mean(), d['MX'].mean()) - np.arctan2(d['DY'].mean(), d['DX'].mean()))) / 8
    v = f(b); bs = [f({n: rng.choice(x, len(x)) for n, x in b.items()}) for _ in range(400)]
    print(f'q{q}: kick {v:+.2f} deg/readout [{np.percentile(bs,2.5):+.2f}, {np.percentile(bs,97.5):+.2f}]  coherence D {np.hypot(b["DX"].mean(), b["DY"].mean()):.2f}')
