"""posthoc_aqcel.py -- DEFINED AFTER THE DATA (not in the plan): F_V1 - F_V2 with a bootstrap interval, same estimator as analyze_aqcel."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, analyze_aqcel as Z
meta = json.load(open(f'{HERE}/meta_aqcel.json')); ents = json.load(open(f'{HERE}/raw_aqcel.json'))
pv = Z.pvec(meta['p']); e0u, e1u, n0, n1 = Z.cal_errors(ents, len(meta['union'])); pos = {q: j for j, q in enumerate(meta['union'])}
rng = np.random.default_rng(7); B = 2000; fb = {}
for a in ('V1', 'V2'):
    pooled = np.sum([Z.vec(c) for l, r, c in ents if l == a], axis=0); N = int(pooled.sum()); ix = [pos[q] for q in meta['meas'][a]]
    fb[a] = np.array([Z.fid(pv, Z.correct(rng.multinomial(N, pooled / N).astype(float), rng.binomial(n0, e0u[ix]) / n0, rng.binomial(n1, e1u[ix]) / n1)) for _ in range(B)])
    fb[a + '_pt'] = Z.fid(pv, Z.correct(pooled, e0u[ix], e1u[ix]))
d = fb['V1'] - fb['V2']; lo, hi = np.percentile(d, [2.5, 97.5])
txt = f"POST-HOC F_V1 - F_V2 = {fb['V1_pt'] - fb['V2_pt']:+.4f} [{lo:+.4f}, {hi:+.4f}] (V1 49 CZ, V2 31 CZ) -> {'CONSISTENT' if lo <= 0 <= hi else 'ABOVE' if lo > 0 else 'BELOW'} (defined after the data)"
print(txt); open(f'{HERE}/posthoc_aqcel.text', 'w').write(txt + '\n')
