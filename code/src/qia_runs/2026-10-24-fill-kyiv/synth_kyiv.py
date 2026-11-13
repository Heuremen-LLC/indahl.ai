"""synth_kyiv.py -- the analysis run on PLANTED data before any job. Truths are the author's own published H0 and H2 kernels.
Worlds: TWIRL (no drift, twirl helps), DRIFT (no twirl effect, the device moves from H0-level to H2-level between pairs), BOTH, NEITHER."""
import json, numpy as np, kyiv as A
d0 = json.load(open('theirs/zz4_H0_raw_results.json'))['entries']; d2 = json.load(open('theirs/zz4_H2_raw_results.json'))['entries']
K0 = A.kernel_from_entries(d0)[0]; K2 = A.kernel_from_entries(d2)[0]; KM = (K0 + K2) / 2
def fake(K, rng, shots=1024):
    out = []
    for i in range(A.N):
        for j in range(i, A.N):
            z = int(rng.binomial(shots, np.clip(K[i, j], 0, 1)))
            out.append(dict(counts={'0000': z, '0001': shots - z}, shots_observed=shots, metadata=dict(circuit_metadata=dict(i=i, j=j))))
    return out
WORLDS = {'TWIRL (expect R1 CONSISTENT, R2 ABOVE x2)': (K0, K2, K0, K2), 'DRIFT (expect R1 BELOW, R2 CONSISTENT x2)': (K0, K0, K2, K2),
          'BOTH (expect R1 BELOW, R2 ABOVE x2)': (K0, KM, KM, K2), 'NEITHER (expect all CONSISTENT)': (K0, K0, K0, K0),
          'LINEAR DRIFT + TWIRL (twirl gap = K0->K2 at job 1; drift step s per job toward K2; true instantaneous gaps 0.0450, 0.0427, 0.0393, 0.0345, mean 0.0404; expect R4 nearer that mean than the raw pair gap)':
              tuple(K0 + (K2 - K0) * (0.15 * k) if r == 'H0' else K2 + (K2 - K0) * (0.15 * k) for k, r in enumerate(('H0', 'H2', 'H0', 'H2'))),
          'ABBA LINEAR (6 jobs; same linear drift; jobs 3-6 true gaps 0.0393, 0.0345, ~0.029, ~0.022 by RMSE nonlinearity; expect R5 ABOVE, near their mean)':
              tuple(K0 + (K2 - K0) * (0.15 * k) if r == 'H0' else K2 + (K2 - K0) * (0.15 * k) for k, r in enumerate(('H0', 'H2', 'H0', 'H2', 'H2', 'H0'))),
          'ABBA NEITHER (6 jobs, all K0; expect R5 CONSISTENT)': (K0,) * 6}
rng = np.random.default_rng(5)
for name, Ts in WORLDS.items():
    jobs = [(str(k + 1), r, fake(T, rng)) for k, (r, T) in enumerate(zip(('H0', 'H2', 'H0', 'H2', 'H2', 'H0')[:len(Ts)], Ts))]
    print('==', name); print('\n'.join(A.analyse(jobs, rng)))
