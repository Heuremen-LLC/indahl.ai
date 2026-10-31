"""committed_kicks.py -- per-qubit kick (deg per readout) for ALL 117 untouched qubits on ibm_kingston and ibm_marrakesh from the
COMMITTED 21 Oct control run (job_ibm_<chip>.json + raw_ibm_<chip>.npz), through the committed analyze.py bits/wrap and the same
expv/phase arithmetic as earlier_runs/2026-10-24-page-wootters/kg_perqubit_from_control.py (arm S, N = 8, M vs D, copies pooled).
Output committed_kicks_<chip>.json: {qubit: [kick, lo95, hi95, coherenceD, kick_copy0, kick_copy1]}. These are the corrections of arm
MC (the 'calibration from ten days earlier'). Every qubit gets its point value; no qubit is selected or dropped by its kick."""
import json, sys, os, numpy as np
CR = os.path.expanduser('../earlier_runs/control_run'); sys.path.insert(0, CR)
from analyze import bits, wrap
HERE = os.path.dirname(os.path.abspath(__file__))
for chip in ('ibm_kingston', 'ibm_marrakesh'):
    rec = json.load(open(f'{CR}/job_{chip}.json')); z = np.load(f'{CR}/raw_{chip}.npz'); meta = rec['meta']; S = rec['S']
    idx = lambda **kw: [i for i, m in enumerate(meta) if all(m.get(k) == v for k, v in kw.items())]
    def arr(mode, setting, copies): return np.concatenate([z['fin_%d' % i] for c in copies for i in idx(copy=c, arm='S', mode=mode, N=8, setting=setting)])
    rng = np.random.default_rng(7); out = {}
    A = {cp: {k: arr(m, s, cps) for k, (m, s) in {'MX': ('M', 'XX'), 'MY': ('M', 'YY'), 'DX': ('D', 'XX'), 'DY': ('D', 'YY')}.items()}
         for cp, cps in (('pooled', (0, 1)), ('c0', (0,)), ('c1', (1,)))}
    f = lambda d: np.degrees(wrap(np.arctan2(d['MY'].mean(), d['MX'].mean()) - np.arctan2(d['DY'].mean(), d['DX'].mean()))) / 8
    for k, q in enumerate(S):
        b = {cp: {n: 1 - 2 * bits(a, k) for n, a in A[cp].items()} for cp in A}
        v = f(b['pooled']); bs = [f({n: rng.choice(x, len(x)) for n, x in b['pooled'].items()}) for _ in range(400)]
        out[int(q)] = [round(float(v), 4), round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4),
                       round(float(np.hypot(b['pooled']['DX'].mean(), b['pooled']['DY'].mean())), 4), round(float(f(b['c0'])), 4), round(float(f(b['c1'])), 4)]
    json.dump(dict(chip=chip, source_job=rec['job_id'], source_submitted=rec['submitted'], L_dt=rec['L_dt'], E=rec['E'], S=S, pairs=rec['pairs'],
                   singles=rec['singles'], kicks_deg_per_readout=out), open(f'{HERE}/committed_kicks_{chip}.json', 'w'), indent=0)
    ks = np.array([v[0] for v in out.values()]); res = sum(1 for v in out.values() if v[2] < 0 or v[1] > 0)
    print(f'{chip}: job {rec["job_id"]} {rec["submitted"]}; 117 kicks median {np.median(ks):+.3f}, range {ks.min():+.2f}..{ks.max():+.2f}, resolved (95% excludes 0) {res}/117')
