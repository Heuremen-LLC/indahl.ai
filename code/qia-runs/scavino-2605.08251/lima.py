"""lima.py -- free calibration run for arXiv:2605.08251 (Scavino Alfaro, independent researcher, Lima; ibm_marrakesh). Analysis only (fire is fire_lima.py).
His sentence (Sec. 7.4): his 95% interval "reflects shot noise within each job rather than drift between jobs". The drift between jobs is what we measure.
His protocol P: both ZNE scale factors (lambda 1 and 3, Richardson 1.5*m(1) - 0.5*m(3)) in ONE job. Our split S: the same circuits as TWO jobs.
Job order (ABBA over arms): P1, S1a, S1b, S2a, S2b, P2.  S1 = lambda 1 then lambda 3; S2 = lambda 3 then lambda 1.
Per graph g: m = mean of the MaxCut observable from counts; error = |m - y_ideal|; MAE = mean over his 10 graphs.
READINGS (fixed in advance; four outcomes each: ABOVE / BELOW / CONSISTENT / CANNOT_TELL; 95 %; shot-noise null = same statistic on resamples of the
POOLED counts of every job holding that (graph, lambda), 2000 draws; the statistic's own interval = resample of that job's counts, re-centred):
  R0 THEIR DATA (KNOWN-GOOD) his raw counts must give MAE(l=1) 0.06445, MAE(ZNE) 0.02810, 9 of 10 graphs improved.
  R1 DRIFT      MAE(l=1, P2) - MAE(l=1, P1).
  R2 SPLIT      A = mean_g ZNE(S1) - mean of ZNE(P1), ZNE(P2);  B = same for S2.  (A: l=1 job first, B: l=3 job first.)
  R2C LINEAR-FREE SPLIT  (A + B) / 2. Under drift linear in job number s per job, A = -2s and B = +2s (the S pair sits one job either side of the P
                mean, and the Richardson weights 1.5, -0.5 add the order term), so the mean is zero; a step at the middle also cancels. It is non-zero only
                for a job-level effect that is not drift of that shape. A and B alone are the drift exposure of a ZNE estimate split across two jobs.
  R3 GAIN       gain(P2) - gain(P1), gain = MAE(l=1) - MAE(ZNE), within-job pairs only (his protocol).
  R4 SHARE      for each S orientation k: D_k = mean_g |ZNE_g(S_k) - ZNE_g(mean of P1, P2)|, the mean per-graph move of the ZNE estimate when its pair is split.
                A per-graph error |ZNE - y| cannot change by more than the move, so D_k bounds what job-to-job drift can do to his per-graph improvement.
                Reported as a share of HIS PUBLISHED GAIN 0.06445 - 0.02810 = 0.03635, headline max_k D_k / 0.03635, next to the shot-noise floor of D_k.
                (Shot noise alone makes D_k positive, so ABOVE means beyond that floor.)
  RULE          value outside the shot-noise null's 95 % range -> ABOVE (greater) or BELOW (smaller); inside -> CONSISTENT. The re-centred interval is printed for size.
  RESOLVABILITY: CANNOT_TELL if the null half-width of a reading exceeds his published gain 0.03635 (fixed in advance from HIS number, never the measured one).
  A reading is the size of the between-job movement on this chip, today, for his circuits. It is not a finding about his 5 May 2026 jobs."""
import csv, glob, gzip, json, sys, numpy as np
HERE = __file__.rsplit('/', 1)[0] or '.'
PUB_MAE1, PUB_ZNE, PUB_IMPROVED = 0.06445, 0.02810, 9
PUB_GAIN = PUB_MAE1 - PUB_ZNE                      # 0.03635, his published numbers, fixed before any job
C1, C3 = 1.5, -0.5                                   # Richardson for scales [1, 3]: solve Vandermonde [[1,1],[1,3]] c = [1,0]
assert np.allclose(np.linalg.solve(np.array([[1, 1], [1.0, 3.0]]), [1, 0]), [C1, C3])
SEEDS = [606, 707, 808, 909, 1001, 1102, 1203, 1304, 1405, 1506]
ORDER = ['P1', 'S1a', 'S1b', 'S2a', 'S2b', 'P2']    # ABBA over arms; S1 = (l1, l3), S2 = (l3, l1)
LAMS = {'P1': (1, 3), 'S1a': (1,), 'S1b': (3,), 'S2a': (3,), 'S2b': (1,), 'P2': (1, 3)}

def load_theirs():
    rows = [r for r in csv.DictReader(open(f'{HERE}/theirs/ibm_qaoa_heldout10_counts.csv')) if r['row_type'] == 'measurement']
    edges, yid, cmean = {}, {}, {}
    for r in rows:
        s = int(r['graph_seed']); edges[s] = [tuple(e) for e in json.loads(r['edges'])]; yid[s] = float(r['y_ideal']); cmean[(s, int(float(r['scale_factor'])))] = float(r['mean'])
    counts = {}
    for s in SEEDS:
        for l in (1, 3):
            f = glob.glob(f'{HERE}/theirs/raw/*seed_{s}_n5_r1_lambda_{l}_ibm_marrakesh_4000.json.gz')[0]
            counts[(s, l)] = vec(json.loads(gzip.open(f).read())['counts'])
    return edges, np.array([yid[s] for s in SEEDS]), cmean, counts
def vec(cd):
    v = np.zeros(32)
    for k, c in cd.items(): v[int(k, 2)] += c
    return v
def obs_matrix(edges):
    """V[g, x] = normalised MaxCut value of bitstring x (Qiskit little-endian: qubit q is bit q of the integer), his definition."""
    V = np.zeros((len(SEEDS), 32))
    for gi, s in enumerate(SEEDS):
        E = edges[s]
        for x in range(32):
            cut = sum(((x >> u) & 1) ^ ((x >> v) & 1) for u, v in E); V[gi, x] = (cut - len(E) / 2) / (len(E) / 2)
    return V
def mae(m, y): return np.mean(np.abs(m - y), axis=-1)
def zne(a, b): return C1 * a + C3 * b
def their_known_good(edges, yid, cmean, counts, V):
    m = {l: np.array([counts[(s, l)] @ V[g] / counts[(s, l)].sum() for g, s in enumerate(SEEDS)]) for l in (1, 3)}
    csvmax = max(abs(m[l][g] - cmean[(s, l)]) for l in (1, 3) for g, s in enumerate(SEEDS))
    z = zne(m[1], m[3]); a1, az = float(mae(m[1], yid)), float(mae(z, yid)); imp = int(np.sum(np.abs(z - yid) < np.abs(m[1] - yid)))
    ok = abs(a1 - PUB_MAE1) < 6e-6 and abs(az - PUB_ZNE) < 6e-6 and imp == PUB_IMPROVED and csvmax < 1e-9
    return a1, az, imp, csvmax, ok

# ---- statistics on mean arrays: M[job][lam] -> array (..., 10) -------------------------------------------------------------------------
def gain(m1, m3, y): return mae(m1, y) - mae(zne(m1, m3), y)
def stats(M, y):
    Pz = lambda k: zne(M[k][1], M[k][3])
    Pm = (Pz('P1') + Pz('P2')) / 2
    z1, z2 = zne(M['S1a'][1], M['S1b'][3]), zne(M['S2b'][1], M['S2a'][3])
    A, B = np.mean(z1 - Pm, axis=-1), np.mean(z2 - Pm, axis=-1)
    return {'R1 DRIFT mae(l=1)': mae(M['P2'][1], y) - mae(M['P1'][1], y), 'R2 SPLIT A (l1 first)': A, 'R2 SPLIT B (l3 first)': B, 'R2C LINEAR-FREE': (A + B) / 2,
            'R3 GAIN P2-P1': gain(M['P2'][1], M['P2'][3], y) - gain(M['P1'][1], M['P1'][3], y), 'R4 |dZNE| S1': np.mean(np.abs(z1 - Pm), axis=-1), 'R4 |dZNE| S2': np.mean(np.abs(z2 - Pm), axis=-1)}
def draw(Pr, N, V, rng, B):
    """Pr[job][lam] -> (10,32) probabilities, N[job][lam] -> (10,) shots; returns M[job][lam] -> (B,10) resampled means."""
    M = {}
    for j, d in Pr.items():
        M[j] = {}
        for l, p in d.items():
            M[j][l] = np.stack([rng.multinomial(int(N[j][l][g]), p[g] / p[g].sum(), size=B) @ V[g] / N[j][l][g] for g in range(len(SEEDS))], axis=1)
    return M
def four(d, lo, hi, nlo, nhi, resolvable=True):
    if not resolvable: return 'CANNOT_TELL'
    if d > nhi: return 'ABOVE'
    if d < nlo: return 'BELOW'
    return 'CONSISTENT'
def means(Pr, V): return {j: {l: np.einsum('gx,gx->g', Pr[j][l], V) for l in Pr[j]} for j in Pr}
def analyse(jobs, V, y, rng, B=2000):
    """jobs: {label: {lam: counts (10,32)}}, all six labels. Returns (lines, results dict name -> (value, lo, hi, nlo, nhi, outcome))."""
    cnt = {j: {l: jobs[j][l] for l in LAMS[j]} for j in ORDER}
    N = {j: {l: cnt[j][l].sum(axis=1) for l in cnt[j]} for j in cnt}
    Pr = {j: {l: cnt[j][l] / N[j][l][:, None] for l in cnt[j]} for j in cnt}
    Mm = means(Pr, V); d = stats(Mm, y)
    bs = stats(draw(Pr, N, V, rng, B), y)
    pool = {l: sum(cnt[j][l] for j in ORDER if l in cnt[j]) for l in (1, 3)}                      # pooled counts per (graph, lambda)
    Ppool = {j: {l: pool[l] / pool[l].sum(axis=1, keepdims=True) for l in cnt[j]} for j in cnt}
    ns = stats(draw(Ppool, N, V, rng, B), y)
    out, lines = {}, []
    for k in d:
        v = float(d[k]); b = bs[k] + (v - np.median(bs[k])); lo, hi = np.percentile(b, [2.5, 97.5]); nlo, nhi = np.percentile(ns[k], [2.5, 97.5])
        res = (nhi - nlo) / 2 < PUB_GAIN; out[k] = (v, lo, hi, nlo, nhi, four(v, lo, hi, nlo, nhi, res))
        lines.append(f'{k:24s} = {v:+.5f} [{lo:+.5f}, {hi:+.5f}] shot-null [{nlo:+.5f}, {nhi:+.5f}] -> {out[k][5]}')
    sh = max(float(d['R4 |dZNE| S1']), float(d['R4 |dZNE| S2'])) / PUB_GAIN; fl = max(float(np.median(ns['R4 |dZNE| S1'])), float(np.median(ns['R4 |dZNE| S2']))) / PUB_GAIN
    g = lambda j: float(gain(Mm[j][1], Mm[j][3], y))
    lines.append(f'R4 SHARE  max D_k / his published gain {PUB_GAIN:.5f} = {float(sh):.3f}  (shot-noise floor {float(fl):.3f}; within-job gain P1 {g("P1"):+.5f}, P2 {g("P2"):+.5f}; his published 0.03635)')
    imp = {j: int(np.sum(np.abs(zne(Mm[j][1], Mm[j][3]) - y) < np.abs(Mm[j][1] - y))) for j in ('P1', 'P2')}
    lines.append(f'graphs improved by ZNE (his count 9/10): P1 {imp["P1"]}/10, P2 {imp["P2"]}/10')
    return lines, out

if __name__ == '__main__':
    edges, y, cmean, counts = load_theirs(); V = obs_matrix(edges)
    a1, az, imp, cm, ok = their_known_good(edges, y, cmean, counts, V)
    print(f'R0 KNOWN-GOOD (his raw counts): MAE lambda=1 {a1:.5f} (published {PUB_MAE1}), MAE after ZNE {az:.5f} (published {PUB_ZNE}), improved {imp}/10 (published {PUB_IMPROVED}/10), max |mean - his checkpoint mean| {cm:.1e} -> {"PASS" if ok else "FAIL"}')
    if len(sys.argv) > 1 and sys.argv[1] == '--real':
        rec = json.load(open(f'{HERE}/job_lima.json')); rng = np.random.default_rng(24); jobs = {}
        for j in rec['jobs']:
            raw = json.load(open(f'{HERE}/raw_lima_{j["label"]}.json')); jobs[j['label']] = {}
            for l in LAMS[j['label']]:
                jobs[j['label']][l] = np.array([vec(next(r['counts'] for r in raw if r['graph_seed'] == s and r['scale'] == l)) for s in SEEDS])
        miss = [j for j in ORDER if j not in jobs]
        if miss: print('INCOMPLETE: missing jobs', miss); sys.exit(1)
        print('\n'.join(analyse(jobs, V, y, rng)[0]))
