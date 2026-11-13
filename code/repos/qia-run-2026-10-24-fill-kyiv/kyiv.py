"""kyiv.py -- free calibration run for arXiv:2607.20377 (KNUBA Kyiv, single author; ibm_fez). Analysis only (fire is fire_kyiv.py).
Kernel entry K_ij = P(all-zero) of the compute-uncompute circuit for pair (i,j); RMSE over off-diagonal entries vs the statevector kernel
(their definition, scripts/09b: kernel_rmse = sqrt(mean((hw_off - sv_off)^2))).
READINGS, per pair of jobs (fixed in advance; four outcomes each, 95 %, shot-noise null by binomial resampling of every all-zero count, 2000 draws):
  R1 DRIFT     dH0 = RMSE(H0 job 3) - RMSE(H0 job 1), same transpiled circuits, ~3 min apart. ABOVE/BELOW if the interval of dH0 excludes
               the shot-noise null's 95 % range around 0; CONSISTENT if inside it (print the bound); CANNOT_TELL if the null half-width is wider than
               THEIR PUBLISHED H0-H2 gap 0.0451 (fixed in advance; the run cannot separate drift of that size).
  R2 ORDERING  gap_k = RMSE(H0 job k) - RMSE(H2 job k+1) for both pairs; the author's ordering (twirling lowers RMSE) HOLDS in a pair if gap_k > 0
               beyond its null; reported per pair and as the ratio |dH0| / mean gap (how much of their gap job-to-job drift could cover).
  R3 THEIR DATA (KNOWN-GOOD) published raw counts must reproduce published RMSE H0 0.08777, H1 0.08643, H2 0.04273 to 1e-4."""
import json, sys, numpy as np
PUB_GAP = 0.08777046763666438 - 0.042727419504658484   # their published H0 - H2 RMSE gap, fixed before any job
HERE = __file__.rsplit('/', 1)[0] or '.'
KSV = np.load(f'{HERE}/theirs/zz4_K_all_all.npy'); N = KSV.shape[0]; IU = np.triu_indices(N, 1)
def kernel_from_entries(entries):
    K = np.zeros((N, N)); c0 = np.zeros((N, N)); sh = np.zeros((N, N))
    for e in entries:
        m = e['metadata']['circuit_metadata']; i, j = m['i'], m['j']; z = e['counts'].get('0' * 4, 0); s = e['shots_observed']
        for a, b in ((i, j), (j, i)): K[a, b] = z / s; c0[a, b] = z; sh[a, b] = s
    return K, c0, sh
def rmse(K): d = K[IU] - KSV[IU]; return float(np.sqrt(np.mean(d ** 2)))
def resample(K, sh, rng, B=2000):
    p = K[IU]; n = sh[IU]; out = np.empty(B)
    for b in range(B): q = rng.binomial(n.astype(int), p) / n; out[b] = float(np.sqrt(np.mean((q - KSV[IU]) ** 2)))
    return out
def four(d, lo, hi, nlo, nhi, resolvable=True):
    if not resolvable: return 'CANNOT_TELL'
    if lo > nhi: return 'ABOVE'
    if hi < nlo: return 'BELOW'
    return 'CONSISTENT'
def compare(KA, shA, KB, shB, rng, B=2000):
    """d = RMSE(B) - RMSE(A); interval from resampling each; null = difference of two resamples of the POOLED kernel (no true change)."""
    a, b = resample(KA, shA, rng, B), resample(KB, shB, rng, B); d = rmse(KB) - rmse(KA)
    lo, hi = np.percentile(b - a + (d - np.median(b - a)), [2.5, 97.5])
    KP = (KA + KB) / 2; n0 = resample(KP, shA, rng, B) - resample(KP, shB, rng, B); nlo, nhi = np.percentile(n0, [2.5, 97.5])
    return d, lo, hi, nlo, nhi
def their_known_good():
    out = {}
    for h in ('H0', 'H1', 'H2'):
        d = json.load(open(f'{HERE}/theirs/zz4_{h}_raw_results.json')); out[h] = rmse(kernel_from_entries(d['entries'])[0])
    pub = {'H0': 0.08777046763666438, 'H1': 0.08642753836276364, 'H2': 0.042727419504658484}
    ok = all(abs(out[h] - pub[h]) < 1e-4 for h in pub)
    return out, pub, ok
def analyse(jobs, rng):
    """jobs: list of (label, regime, entries) in submission order H0, H2, H0, H2."""
    Ks = [(l, r) + kernel_from_entries(e)[::2] for l, r, e in jobs]
    lines = [f'  job {l} ({r}): RMSE {rmse(K):.5f}' for l, r, K, sh in Ks]
    (l1, _, K1, s1), (l2, _, K2, s2), (l3, _, K3, s3), (l4, _, K4, s4) = Ks[:4]
    d, lo, hi, nlo, nhi = compare(K1, s1, K3, s3, rng)
    g1 = compare(K2, s2, K1, s1, rng); g2 = compare(K4, s4, K3, s3, rng); gap = (g1[0] + g2[0]) / 2
    res = (nhi - nlo) / 2 < PUB_GAP
    lines.append(f'R1 DRIFT  dH0 = {d:+.5f} [{lo:+.5f}, {hi:+.5f}] shot-null [{nlo:+.5f}, {nhi:+.5f}] -> {four(d, lo, hi, nlo, nhi, res)}')
    for k, g in ((1, g1), (2, g2)):
        lines.append(f'R2 ORDER pair {k}: RMSE(H0) - RMSE(H2) = {g[0]:+.5f} [{g[1]:+.5f}, {g[2]:+.5f}] null [{g[3]:+.5f}, {g[4]:+.5f}] -> {four(*g)}')
    # R4 (ADDENDUM 1, committed after the jobs were submitted and BEFORE any result was read): order H0,H2,H0,H2 under a drift linear
    # in job number (step s per job) biases both pair gaps by -s; dH0 = 2s, so the drift-corrected twirl gap is gap + dH0/2.
    c = gap + d / 2
    w = (nhi - nlo); size = f'size read {(gap + c) / 2:+.5f}' if abs(c - gap) < w else 'size CANNOT_TELL (drift shape decides: step vs linear)'
    lines.append(f'R4 ADDENDUM twirl-gap size: R2 mean {gap:+.5f} | R4 linear-corrected {c:+.5f} | differ by {abs(c - gap):.5f} vs null width {w:.5f} -> {size}; defined after submission, before results')
    if len(Ks) >= 6:   # R5 (ADDENDUM 2, planned before jobs 5-6 fired): jobs 3-6 = H0 H2 H2 H0, cancels drift linear in job number
        (_, _, K5, s5), (_, _, K6, s6) = Ks[4], Ks[5]
        a3, a4, a5, a6 = (resample(K, sh, rng) for K, sh in ((K3, s3), (K4, s4), (K5, s5), (K6, s6)))
        r5 = (rmse(K3) + rmse(K6)) / 2 - (rmse(K4) + rmse(K5)) / 2; bs = (a3 + a6) / 2 - (a4 + a5) / 2; bs = bs + (r5 - np.median(bs))
        lo5, hi5 = np.percentile(bs, [2.5, 97.5]); KP = (K3 + K4 + K5 + K6) / 4
        n5 = (resample(KP, s3, rng) + resample(KP, s6, rng)) / 2 - (resample(KP, s4, rng) + resample(KP, s5, rng)) / 2; nl5, nh5 = np.percentile(n5, [2.5, 97.5])
        lines.append(f'R5 ABBA (jobs 3-6) twirl gap RMSE(H0) - RMSE(H2) = {r5:+.5f} [{lo5:+.5f}, {hi5:+.5f}] null [{nl5:+.5f}, {nh5:+.5f}] -> {four(r5, lo5, hi5, nl5, nh5)}; dH0(6-3) {rmse(K6) - rmse(K3):+.5f}')
    lines.append(f'R2 share: |dH0| / their published gap {PUB_GAP:.4f} = {abs(d) / PUB_GAP:.3f}; mean measured gap {gap:+.5f}')
    return lines
if __name__ == '__main__':
    out, pub, ok = their_known_good()
    print('R3 KNOWN-GOOD (their published data):', {h: round(out[h], 5) for h in out}, 'published', {h: round(pub[h], 5) for h in pub}, '->', 'PASS' if ok else 'FAIL')
    if len(sys.argv) > 1 and sys.argv[1] == '--real':
        rec = json.load(open(f'{HERE}/job_kyiv.json')); rng = np.random.default_rng(24)
        jobs = [(j['label'], j['regime'], json.load(open(f'{HERE}/raw_kyiv_{j["label"]}.json'))) for j in rec['jobs']]
        print('\n'.join(analyse(jobs, rng)))
