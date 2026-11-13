"""synth_lums.py -- planted worlds through the committed lums.analyse. Base: the author's own released row distributions (bps1 and its
repeat pooled), n = 8 and 10, 8 jobs in ORDER, his shots per row. Planted in CVaR units (resolution scale fixed from HIS numbers: his
n=8 shift 0.0426 for one pair = sqrt(2) x a job SD of ~0.03):
  neither | drift (common per-job SD 0.03, both arms) | instance_rows (row-specific per-job SD 0.03, T only) | instance_job (common per-job SD 0.03,
  T only) | both (drift + instance_rows) | below (drift SD 0.005)
Perturbation: p' = (1-eps) p + eps u, eps per (job,row) = 0.2 + shift / slope_r, slope_r = dCVaR/deps at eps 0.2 by central difference
(CVaR is not linear in eps; the realised planted SD is measured and printed per world).
A false call = ABOVE/BELOW/CANNOT_TELL on a reading whose planted truth is 'none'; a miss = planted present but not ABOVE."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lums
WORLDS = {'neither': (0, 0, 0), 'drift': (0.03, 0, 0), 'instance_rows': (0, 0.03, 0), 'instance_job': (0, 0, 0.03), 'both': (0.03, 0.03, 0), 'below': (0.005, 0, 0)}
TRUTH = {'R1_drift_O_CM': lambda w: w in ('drift', 'both'), 'R1b_T_CM': lambda w: w in ('drift', 'both', 'instance_job'),
         'R2_twirl_job_var_T_minus_O': lambda w: w == 'instance_job', 'R2b_twirl_rows_T_minus_O': lambda w: w in ('instance_rows', 'both')}
def run(ndraw, seed):
    rng = np.random.default_rng(seed); fc = {k: [0, 0] for k in TRUTH}; ms = {k: [0, 0] for k in TRUTH}; lines = []
    for n in (8, 10):
        d = lums.theirs(n); cv = lums.Cvar(lums.energies(d)); L = {j['tag']: j for j in d['ledger']['log']}; shots = L['bps1']['shots']
        base = lums.counts_to_P(L['bps1']['counts'], n) + lums.counts_to_P(L['drift_repeat']['counts'], n); base /= base.sum(1, keepdims=True)
        u = np.full(2 ** n, 2.0 ** -n); R = base.shape[0]
        mix = lambda e: (1 - e) * base + e * u; slope = (cv(mix(0.21)) - cv(mix(0.19))) / 0.02
        for w, (sd, si, sj) in WORLDS.items():
            calls = {k: {} for k in TRUTH}; real = []
            for _ in range(ndraw):
                J = len(lums.ORDER); drift = rng.normal(0, sd, J) if sd else np.zeros(J); job_i = rng.normal(0, sj, J) if sj else np.zeros(J)
                N = np.empty((J, R, 2 ** n), int); cj = []
                for j, a in enumerate(lums.ORDER):
                    inst = (rng.normal(0, si, R) if si else np.zeros(R)) + (job_i[j] if a == 'T' else 0) if a == 'T' else np.zeros(R)
                    eps = np.clip(0.2 + (drift[j] + inst) / slope, 0, 1)
                    P = (1 - eps[:, None]) * base + eps[:, None] * u; cj.append((cv(P) - cv(mix(0.2))).mean())
                    N[j] = rng.multinomial(shots, P)
                real.append(np.std(cj, ddof=1)); out = lums.analyse(N, lums.ORDER, shots, cv, rng)
                for k in TRUTH:
                    oc = out[k]['outcome']; calls[k][oc] = calls[k].get(oc, 0) + 1
                    if TRUTH[k](w): ms[k][1] += 1; ms[k][0] += oc != 'ABOVE'
                    else: fc[k][1] += 1; fc[k][0] += oc != 'CONSISTENT'
            lines.append(f'n={n:2d} {w:13s} realised job-mean SD {np.mean(real):.4f} | ' + ' | '.join(f'{k}: ' + ', '.join(f'{o} {c}' for o, c in sorted(calls[k].items())) for k in TRUTH))
            print(lines[-1], flush=True)
    tf = sum(v[0] for v in fc.values()); tn = sum(v[1] for v in fc.values()); tm = sum(v[0] for v in ms.values()); tp = sum(v[1] for v in ms.values())
    print('FALSE CALLS per reading: ' + ', '.join(f'{k} {v[0]}/{v[1]}' for k, v in fc.items()) + f'  TOTAL {tf}/{tn} = {100*tf/tn:.1f} %')
    print('MISSES per reading: ' + ', '.join(f'{k} {v[0]}/{v[1]}' for k, v in ms.items()) + f'  TOTAL {tm}/{tp} = {100*tm/tp:.1f} %')
if __name__ == '__main__':
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 40, 7)
