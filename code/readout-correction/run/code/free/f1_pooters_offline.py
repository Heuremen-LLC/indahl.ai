"""F1 (free, zero QPU, DEFINED AFTER THE 24 Oct DATA): apply a Z-frame correction offline to the 24 Oct Pooters arm-M tomography.
Correction = the COMMITTED 21 Oct per-qubit kicks (control run, same qubits), x 4 readouts, NOT the kicks fitted from these data.
Also printed: correction with the kicks fitted from these data (in-sample ceiling, circular, labelled)."""
import sys, json, itertools, numpy as np
P = '../earlier_runs/2026-10-24-page-wootters'; sys.path.insert(0, P)
import pooters as T
COMMITTED = {'c0': -3.06, 'c1': -18.12, 's': -7.61}   # deg/readout, RESULT_POOTERS.md.text known-good column (21 Oct control run)
def corr(E, phis_deg):
    M = T.kron3(T.qmap(np.radians(-phis_deg[0]), 1), T.qmap(np.radians(-phis_deg[1]), 1), T.qmap(np.radians(-phis_deg[2]), 1))
    return M @ E
rng = np.random.default_rng(31)
for J in ('J1', 'J2', 'pooled'):
    if J == 'pooled':
        raws = [json.load(open(f'{P}/raw_pooters_{j}.json')) for j in ('J1', 'J2')]
        C = {a: {st: {} for st in T.SETTINGS} for a in 'DM'}
        for raw in raws:
            for e in raw:
                for k, v in e['counts'].items(): C[e['arm']][e['setting']][k] = C[e['arm']][e['setting']].get(k, 0) + v
    else:
        raw = json.load(open(f'{P}/raw_pooters_{J}.json')); C = {a: {e['setting']: e['counts'] for e in raw if e['arm'] == a} for a in 'DM'}
    def F_all(CD, CM, fit=False):
        ED, EM = T.evec(T.to_P(CD)), T.evec(T.to_P(CM))
        tot = [4 * COMMITTED[k] for k in ('c0', 'c1', 's')]
        out = [T.fidelity(ED), T.fidelity(EM), T.fidelity(corr(EM, tot))]
        if fit:
            phi, lam, _ = T.fit_look(ED, EM); out.append(T.fidelity(corr(EM, list(phi)))); out.append(list(np.round(phi, 1)))
        return out
    pt = F_all(C['D'], C['M'], fit=True)
    bs = np.array([F_all(T.resample(C['D'], rng), T.resample(C['M'], rng))[:3] for _ in range(200)])
    lo, hi = np.percentile(bs, [0.5, 99.5], axis=0)
    rec = bs[:, 2] - bs[:, 1]; rlo, rhi = np.percentile(rec, [0.5, 99.5]); gap = bs[:, 0] - bs[:, 2]; glo, ghi = np.percentile(gap, [0.5, 99.5])
    print(f'{J}: F(D) {pt[0]:.3f} [{lo[0]:.3f},{hi[0]:.3f}]  F(M) {pt[1]:.3f} [{lo[1]:.3f},{hi[1]:.3f}]  '
          f'F(M, committed-kick frame correction) {pt[2]:.3f} [{lo[2]:.3f},{hi[2]:.3f}]  recovered {pt[2]-pt[1]:+.3f} [{rlo:+.3f},{rhi:+.3f}]  '
          f'left vs D {pt[0]-pt[2]:+.3f} [{glo:+.3f},{ghi:+.3f}]  | in-sample fit ceiling {pt[3]:.3f} (fitted totals c0,c1,s {pt[4]} deg)')
