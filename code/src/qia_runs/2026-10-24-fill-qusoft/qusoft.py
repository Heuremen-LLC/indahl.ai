"""qusoft.py -- free calibration run for arXiv:2610.20855 (Awuah, Guo; QuSoft / University of Amsterdam with AIMS Ghana; ibm_kingston). Analysis only (fire is fire_qusoft.py).
Their own words (Sec. 9.3): "Together, these two factors give 0.72 at n = 21, still well above the measured value" (measured 0.39); (Sec. 7.3) "In the cz basis, the measured target probability is below
P_HW (Table 11) for every n, by a factor of more than 5 for n >= 8."; (Sec. 5.5) "run-to-run drift on these devices is of the same order as these differences".
Design: three of THEIR circuits (SWAP chain n=21 and n=11 on the DFS line of their code, HP_8 at r*=7), 4096 shots, cz basis, no DD, no twirling, in four jobs ABBA (A1 B1 B2 A2).
Inside EVERY job, on the qubits those circuits use: (i) a readout circuit per target (prepare the target bit-string, measure: the exact string survival with no gates), (ii) per-edge two-qubit RB in
isolated batches (sweep.py's RB2 construction) on every edge the three circuits use. The same transpiled circuits, layout and seeds in all four jobs; B is A in reversed order.
Per job j and target c: P[j,c] = target-string probability, RO[j,c] = prepared-string survival, e[j,edge] = RB layer error (3/4 (1-p), IBM's own stated definition, includes the 1q layer).
MODELS (their form: P = P_noiseless x survival, incoherent):
  STATED    P_noiseless x prod_edge (1 - stated_cz)^W[c,edge] x prod_qubit (1 - stated_readout)   (stated record saved before each job, per edge and qubit)
  DELIVERED P_noiseless x prod_edge (1 - e_delivered)^W[c,edge] x RO[c]                          (pooled over the 4 jobs)
READINGS (fixed in advance; four outcomes each: ABOVE / BELOW / CONSISTENT / CANNOT_TELL; 95 %):
  R0 KNOWN-GOOD   Table 10 nine rows recompute (S, P_noiseless, P_HW) to 6 decimals; Table 20 per-vertex counts (probability x 4096 integer) reproduce every printed in-subspace sum and Table 12 target;
                  my rebuilt HP_8 circuit's noiseless target equals the printed Aer value; RB circuits return all-zero noiselessly (fire dry run).
  R1 CLOSED[c]    model STATED - model DELIVERED     how much of the model-vs-measured gap the delivered cz and readout on THEIR qubits close.      bootstrap of every count.
  R2 REMAIN[c]    model DELIVERED - measured         what is left after it.
  R3 CZRATIO      median over the 20 chain edges of e_delivered / stated_cz (edges stated 0 or 1 excluded).      R4 ROFAIL  sum(1-RO) / sum(1-stated readout survival), the three strings.
  D1 JOB-SD  D2 STEP  D3 SLOT   pooled RMS over the 6 probabilities (3 targets, 3 readout strings): sd over 4 jobs, (p3+p4-p1-p2)/2, (p1+p4-p2-p3)/2 (qfim.py's definitions).
  D4 CZ-SD  D5 CZ-STEP   sd over 4 jobs and |(c3+c4-c1-c2)/2| of c_j = median over the 20 chain edges of the per-job RB layer error.
  Shot-noise null for D = the same statistic on binomial redraws of every count at its pooled probability (RB at the pooled survival of that edge and length), 500 draws.
RESOLVABILITY (fixed in advance from THEIR published numbers, never from ours):
  R1, R2: CANNOT_TELL if the interval half-width exceeds 1/4 of THEIR model-minus-measured gap for that circuit (chain 21: 0.7184 - 0.3894; chain 11 and HP_8 the same way from their Table 18 / Table 11-12).
  R3, R4: CANNOT_TELL if the half-width exceeds 1/4 of (f - 1), f = the factor on their cz error (R3) or on their 1e-2 readout error (R4) that alone would bring their own model to their measured 0.3894 at n = 21
          (solved from their numbers: cz x6.1, readout x3.8); the interval is printed with its width, CONSISTENT is a bound.
  D1-D3: CANNOT_TELL if the null half-width exceeds the median |fractional - cz| target probability over n = 2..12 in their Table 12 (the differences they say 'may be due to changes in the device calibration').
  D4, D5: CANNOT_TELL if the null half-width exceeds (their n=21 gap) / (60 cz x 4), the cz-error change that 60 gates would turn into a quarter of their gap.
Nothing here is a finding about their 2026 jobs: it is the size of the terms on this chip, today, for their circuits. Their code was never executed; circuits are rebuilt from the construction."""
import json, os, re, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 4096; RB_SHOTS = 250; RB_SEEDS = 2; M2 = [1, 10, 30, 60, 100]; NRB = RB_SHOTS * RB_SEEDS
TARGETS = ['chain21', 'chain11', 'hp8']; NQ = {'chain21': 21, 'chain11': 11, 'hp8': 9}
ORDER = ['A1', 'B1', 'B2', 'A2']                                   # ABBA
P2Q, RO1 = 2.0e-3, 1.0e-2                                          # their p2q and readout per qubit (Sec. 7.2, 9.3)
GRID = np.linspace(0.90, 1.0, 301)

# ------------------------------------------------------------------ their published tables (text of arXiv:2610.20855 v1, theirs/paper.txt)
def _floats(s): return [float(x) for x in re.findall(r'\d\.\d{6}', s)]
def parse_theirs(path=None):
    L = open(path or f'{HERE}/theirs/paper.txt', errors='replace').read().split('\n'); T = {}
    def block(start_pat, end_pat, first=0):
        i0 = next(i for i, l in enumerate(L) if i >= first and re.match(start_pat, l)); i1 = next(i for i, l in enumerate(L) if i > i0 and re.match(end_pat, l)); return L[i0 + 1:i1], i0
    rows, i0 = block(r'^n rqubitsn 2q Pnoiseless S', r'^Table 10:'); T['t10'] = []
    for l in rows:
        t = l.split(); f = _floats(l)
        if len(t) >= 5 and len(f) == 3 and all(x.isdigit() for x in t[:4]): T['t10'].append(dict(n=int(t[0]), r=int(t[1]), q=int(t[2]), n2q=int(t[3]), pn=f[0], S=f[1], ph=f[2]))
    rows, _ = block(r'^nqubitsr . n2q Pnoiseless', r'^Table 11:'); T['t11'] = []
    for l in rows:
        t = l.split(); f = _floats(l)
        if len(t) >= 6 and len(f) == 2 and all(x.isdigit() for x in t[:4]): T['t11'].append(dict(n=int(t[0]), q=int(t[1]), r=int(t[2]), n2q=int(t[3]), pn=f[0], ph=f[1]))
    rows, _ = block(r'^czbasis fractional basis', r'^Table 12:'); T['t12'] = []
    for l in rows:
        t = l.split(); f = _floats(l)
        if len(t) >= 6 and len(f) == 3 and all(x.isdigit() for x in t[:4]): T['t12'].append(dict(n=int(t[0]), q=int(t[1]), r=int(t[2]), n2q=int(t[3]), aer=f[0], cz=f[1], frac=f[2]))
    rows, _ = block(r'^n n 2q in-subspace', r'^Table 18:'); T['t18'] = []
    for l in rows:
        t = l.split()
        if len(t) == 3 and t[0].isdigit() and t[1].isdigit():
            s = t[2]; T['t18'].append(dict(n=int(t[0]), n2q=int(t[1]), insub=float(s[:6]), P=float(s[6:14]), qpu=int(s[14:])))
    # Table 20: per-vertex rows, blocks '<n> (r= <r>)' ... 'in-subspace sum A B C'
    i0 = next(i for i, l in enumerate(L) if l.startswith('Table 20: Per-vertex')); i1 = next(i for i, l in enumerate(L) if i > i0 and l.startswith('Table 21:'))
    T['t20'] = {}; cur = None
    for l in L[i0:i1]:
        m = re.match(r'^(\d+) \(r= ?(\d+)\)$', l.strip())
        if m: cur = dict(n=int(m.group(1)), r=int(m.group(2)), aer=[], cz=[], frac=[], sum=None); T['t20'][cur['n']] = cur; continue
        if cur is None: continue
        if l.startswith('in-subspace sum'): v = _floats(l); cur['sum'] = dict(aer=v[0], cz=v[1], frac=v[2]); cur = None; continue
        k = len(cur['cz']); q = cur['n'] + 1; pre = str(k) + format(1 << k, f'0{q}b')
        if l.startswith(pre):
            v = _floats(l[len(pre):])
            if len(v) == 3: cur['aer'].append(v[0]); cur['cz'].append(v[1]); cur['frac'].append(v[2])
    return T
def counts_of(p): return int(round(p * SHOTS))

# ------------------------------------------------------------------ noiseless P for the Hamming-weighted path (numpy; their code is not run)
def U_hp(n, r, t=np.pi / 2):
    N = n + 1; dt = t / r; w = [np.sqrt(k * (n - k + 1)) for k in range(1, n + 1)]
    def edge(k, frac):
        th = 0.5 * w[k - 1] * frac * dt * 2; M = np.eye(N, dtype=complex); c, s = np.cos(th), -1j * np.sin(th)
        M[k - 1, k - 1] = c; M[k, k] = c; M[k - 1, k] = s; M[k, k - 1] = s; return M
    step = np.eye(N, dtype=complex)
    for k in range(1, n + 1): step = edge(k, 0.5) @ step
    for k in range(n, 0, -1): step = edge(k, 0.5) @ step
    return np.linalg.matrix_power(step, r)
def pnl_hp(n, r): return float(abs(U_hp(n, r)[n, 0]) ** 2)
NINE = [(4, 2), (4, 4), (4, 8), (8, 4), (8, 8), (12, 8), (16, 16), (20, 16), (20, 32)]

def known_good(T):
    lines, ok = [], True
    d10 = {(d['n'], d['r']): d for d in T['t10']}; n_ok = [0, 0, 0]; worst = 0.0
    for key in NINE:
        d = d10[key]; S = (1 - P2Q) ** d['n2q']; pn = pnl_hp(*key); ph = pn * S
        a = (f'{S:.6f}' == f'{d["S"]:.6f}', f'{pn:.6f}' == f'{d["pn"]:.6f}', f'{ph:.6f}' == f'{d["ph"]:.6f}')
        for i in range(3): n_ok[i] += a[i]
        worst = max(worst, abs(S - d['S']), abs(pn - d['pn']), abs(ph - d['ph']))
    allr = [(d['n'], d['r']) for d in T['t10']]; n25 = sum(f'{(1 - P2Q) ** d10[k]["n2q"]:.6f}' == f'{d10[k]["S"]:.6f}' and f'{pnl_hp(*k):.6f}' == f'{d10[k]["pn"]:.6f}' for k in allr)
    k1 = n_ok == [9, 9, 9]; ok &= k1
    lines.append(f'KG1 Table 10, the nine rows {NINE}: S = (1-2.0e-3)^n2q equal to 6 decimals {n_ok[0]}/9; P_noiseless (numpy, second-order Suzuki-Trotter on the single-excitation subspace) {n_ok[1]}/9; P_HW = P_noiseless x S {n_ok[2]}/9; max |diff| {worst:.1e} -> {"PASS" if k1 else "FAIL"}   (all {len(allr)} printed rows, S and P_noiseless both equal: {n25}/{len(allr)})')
    # raw counts: Table 20 per-vertex probabilities x 4096 are integers; sums and targets
    n_int = n_sum = n_tgt = n_blocks = 0; maxfrac = 0.0
    t12 = {d['n']: d for d in T['t12']}
    for n, b in sorted(T['t20'].items()):
        n_blocks += 1; q = n + 1
        if len(b['cz']) != q or b['sum'] is None: continue
        fr = [abs(p * SHOTS - round(p * SHOTS)) for p in b['cz']]; maxfrac = max(maxfrac, max(fr)); n_int += max(fr) < 2.5e-3
        K = [counts_of(p) for p in b['cz']]; n_sum += f'{sum(K) / SHOTS:.6f}' == f'{b["sum"]["cz"]:.6f}'
        n_tgt += f'{K[n] / SHOTS:.6f}' == f'{t12[n]["cz"]:.6f}'
    k2 = n_blocks == 19 and n_int == n_sum == n_tgt == 19; ok &= k2
    lines.append(f'KG2 Table 20 cz column, {n_blocks} HP_n blocks (n=2..20): per-vertex probability x 4096 is an integer count (max distance {maxfrac:.1e}) in {n_int}/{n_blocks}; the sum of the integer counts / 4096 equals the printed in-subspace sum to 6 decimals in {n_sum}/{n_blocks}; '
                 f'the target-vertex count / 4096 equals the Table 12 cz target probability in {n_tgt}/{n_blocks} -> {"PASS" if k2 else "FAIL"}   (e.g. n=21 chain: P(target) 0.389404 = {counts_of(0.389404)} / 4096; n=8 HP cz target {t12[8]["cz"]:.6f} = {counts_of(t12[8]["cz"])} / 4096)')
    t18 = {d['n']: d for d in T['t18']}; chain_ok = all(abs(d['P'] * SHOTS - round(d['P'] * SHOTS)) < 2.5e-3 for d in t18.values()); ok &= chain_ok
    lines.append(f'KG2b Table 18 SWAP chain, {len(t18)} rows: P(target) x 4096 integer in {sum(abs(d["P"] * SHOTS - round(d["P"] * SHOTS)) < 2.5e-3 for d in t18.values())}/{len(t18)} -> {"PASS" if chain_ok else "FAIL"}')
    return lines, ok

def their_gaps(T):
    t18 = {d['n']: d for d in T['t18']}; t11 = {d['n']: d for d in T['t11']}; t12 = {d['n']: d for d in T['t12']}
    m21 = (1 - P2Q) ** (3 * 20) * (1 - RO1) ** 21; m11 = (1 - P2Q) ** (3 * 10) * (1 - RO1) ** 11
    g = dict(chain21=m21 - t18[21]['P'], chain11=m11 - t18[11]['P'], hp8=t11[8]['ph'] - t12[8]['cz'])
    S_drift = float(np.median([abs(t12[n]['frac'] - t12[n]['cz']) for n in range(2, 13)]))
    return g, dict(chain21=m21, chain11=m11, hp8=t11[8]['ph']), S_drift

# ------------------------------------------------------------------ RB fit, vectorised (A p^m + 1/4, A free in [0, 3/4]; p on a grid, parabola refinement)
def rbfit_err(S, M=None, chunk=64):
    M = np.asarray(M2 if M is None else M, float); S = np.asarray(S, float); lead = S.shape[:-1]; Sf = S.reshape(-1, S.shape[-1]); out = np.empty(len(Sf))
    x = GRID[:, None] ** M[None, :]; xx = (x * x).sum(-1)
    for i in range(0, len(Sf), chunk):
        y = Sf[i:i + chunk, None, :] - 0.25; A = np.clip((y * x).sum(-1) / xx, 0, 0.75); res = ((y - A[..., None] * x) ** 2).sum(-1)
        gi = res.argmin(-1); g0 = np.clip(gi, 1, len(GRID) - 2); r = np.arange(len(res)); a, b, c = res[r, g0 - 1], res[r, g0], res[r, g0 + 1]
        den = a - 2 * b + c; sh = np.where(den > 1e-18, 0.5 * (a - c) / np.where(den > 1e-18, den, 1), 0.0); sh = np.clip(sh, -1, 1) * (gi == g0)
        out[i:i + chunk] = 0.75 * (1 - (GRID[g0] + sh * (GRID[1] - GRID[0])))
    return out.reshape(lead)

# ------------------------------------------------------------------ statistics
def stats(K, D):
    """K: Kt (...,4,3), Kr (...,4,3), Krb (...,4,E,L) successes. D: design dict of arrays. Returns dict name -> array (...)"""
    Kt, Kr, Krb = K['Kt'], K['Kr'], K['Krb']; out = {}
    Pm = Kt.sum(-2) / (4 * SHOTS); R = Kr.sum(-2) / (4 * SHOTS)
    e = rbfit_err(Krb.sum(-3) / (4 * NRB)); W = D['W']                                     # e (...,E), W (3,E)
    surv = np.exp(np.einsum('ce,...e->...c', W, np.log1p(-e)))
    mdel = D['pnl'] * surv * R; mst = D['model_stated']
    for i, c in enumerate(TARGETS): out[f'R1 CLOSED {c}'] = mst[i] - mdel[..., i]; out[f'R2 REMAIN {c}'] = mdel[..., i] - Pm[..., i]
    li = D['line_idx']; st = D['stated_cz'][li]; okm = np.isfinite(st) & (st > 0) & (st < 1)
    out['R3 CZRATIO'] = np.median(e[..., li][..., okm] / st[okm], axis=-1)
    out['R4 ROFAIL'] = (1 - R).sum(-1) / (1 - D['ro_stated_surv']).sum()
    Pj = np.concatenate([Kt / SHOTS, Kr / SHOTS], axis=-1)                                  # (...,4,6)
    rms = lambda x: np.sqrt(np.mean(x ** 2, axis=-1))
    out['D1 JOB-SD (RMS)'] = rms(Pj.std(axis=-2, ddof=1))
    out['D2 STEP (RMS)'] = rms((Pj[..., 2, :] + Pj[..., 3, :] - Pj[..., 0, :] - Pj[..., 1, :]) / 2)
    out['D3 SLOT (RMS)'] = rms((Pj[..., 0, :] + Pj[..., 3, :] - Pj[..., 1, :] - Pj[..., 2, :]) / 2)
    ej = rbfit_err(Krb / NRB); cj = np.median(ej[..., li], axis=-1)                         # (...,4)
    out['D4 CZ-SD'] = cj.std(axis=-1, ddof=1); out['D5 CZ-STEP'] = np.abs((cj[..., 2] + cj[..., 3] - cj[..., 0] - cj[..., 1]) / 2)
    return out
def redraw(K, rng, B, pooled, nt=None, nr=None, nrb=None):
    """binomial redraws (B,...) of every count, at each count's own proportion (bootstrap) or at the proportion pooled over the 4 jobs (shot-noise null)"""
    nt = SHOTS if nt is None else nt; nr = SHOTS if nr is None else nr; nrb = NRB if nrb is None else nrb
    def one(k, n):
        p = k / n
        if pooled: p = np.broadcast_to(p.mean(axis=0, keepdims=True), p.shape)
        return rng.binomial(n, np.broadcast_to(p, (B,) + p.shape))
    return dict(Kt=one(K['Kt'], nt), Kr=one(K['Kr'], nr), Krb=one(K['Krb'], nrb))
SIGNED = ('R1', 'R2'); RATIO = ('R3', 'R4'); DRIFT_P = ('D1', 'D2', 'D3'); DRIFT_CZ = ('D4', 'D5')
BAND = {k: (0.5, 99.5) for k in ('R1', 'R2', 'R3', 'R4', 'D1', 'D2', 'D3', 'D4', 'D5')}   # percentiles of the interval / shot-noise null; default (2.5, 97.5). ADDENDUM 1: widened from 2.5-97.5 after the synthetic NEITHER false-rate check (first pass: R1 hp8 19/200, D2 17/200; second pass with R1-R2, D widened: R4 20/200), before any job.
def band(k): return BAND.get(k[:2], (2.5, 97.5))
def four(v, lo, hi, resolvable, ref=0.0):
    if not resolvable: return 'CANNOT_TELL'
    return 'ABOVE' if lo > ref else 'BELOW' if hi < ref else 'CONSISTENT'
def scales(T, shots_scale=1.0):
    from scipy.optimize import brentq
    g, mp, sd = their_gaps(T); m21 = {d['n']: d for d in T['t18']}[21]['P']
    f_cz = brentq(lambda f: (1 - P2Q * f) ** 60 * (1 - RO1) ** 21 - m21, 1.0, 50.0); f_ro = brentq(lambda f: (1 - P2Q) ** 60 * (1 - RO1 * f) ** 21 - m21, 1.0, 50.0)
    return dict(gap=g, drift_p=sd, cz=g['chain21'] / (60 * 4), ratio=(f_cz - 1) / 4, ratio_ro=(f_ro - 1) / 4, f_need=(f_cz, f_ro), model_paper=mp)
def analyse(K, D, sc, rng, B=500):
    """returns (lines, out) with out[name] = (value, lo, hi, outcome, halfwidth)"""
    d = stats(K, D); out = {}; lines = []
    bs = stats(redraw(K, rng, B, pooled=False), D); ns = stats(redraw(K, rng, B, pooled=True), D)
    for k, v in d.items():
        v = float(v); tag = k[:2]
        if tag in SIGNED + RATIO:
            lo, hi = np.percentile(bs[k], band(k)); hw = (hi - lo) / 2
            if tag in SIGNED: c = k.split()[-1]; scale = sc['gap'][c] / 4; ref = 0.0
            else: scale = sc['ratio'] if tag == 'R3' else sc['ratio_ro']; ref = 1.0
            out[k] = (v, lo, hi, four(v, lo, hi, hw <= scale, ref), hw)
            lines.append(f'{k:26s} = {v:+.4f} [{lo:+.4f}, {hi:+.4f}] half-width {hw:.4f} (their scale {scale:.4f}) -> {out[k][3]}')
        else:
            nlo, nhi = np.percentile(ns[k], band(k)); hw = (nhi - nlo) / 2; scale = sc['drift_p'] if tag in DRIFT_P else sc['cz']
            lo, hi = np.percentile(bs[k], [2.5, 97.5]); rs = hw < scale
            out[k] = (v, lo, hi, 'CANNOT_TELL' if not rs else 'ABOVE' if v > nhi else 'BELOW' if v < nlo else 'CONSISTENT', hw, nlo, nhi)
            lines.append(f'{k:26s} = {v:.5f} [{lo:.5f}, {hi:.5f}] shot-null [{nlo:.5f}, {nhi:.5f}] (their scale {scale:.5f}) -> {out[k][3]}')
    return lines, out

# ------------------------------------------------------------------ real data
def stated_from_props(props, D):
    """stated cz per design edge and stated readout survival per target string from one saved backend record (sweep.py's reader)"""
    sys.path.insert(0, os.path.expanduser('~/bones-forge/arxiv_one_readout/sweep_run')); from sweep import stated
    st_q, st_g = stated(props); cz = []
    for a, b in D['edges']:
        v = st_g.get(('cz', (a, b)), st_g.get(('cz', (b, a)))); cz.append(np.nan if v is None else float(v))
    ro = []
    for c in TARGETS:
        s = 1.0
        for i, q in enumerate(D['phys'][c]): s *= 1 - st_q[q]['prob_meas0_prep1' if i == NQ[c] - 1 else 'prob_meas1_prep0']
        ro.append(s)
    return np.array(cz), np.array(ro)
def model_stated_of(D, cz, ro):
    bad = ~np.isfinite(cz) | (cz >= 1); lg = np.log1p(-np.where(bad, 0.0, cz)); m = D['pnl'] * np.exp(D['W'] @ lg) * ro
    return np.where(((D['W'] > 0) & bad[None, :]).any(axis=1), np.nan, m)
def counts_key_rate(counts, key): return counts.get(key, 0)
def load_design():
    d = json.load(open(f'{HERE}/design_qusoft.json'))
    D = dict(edges=[tuple(e) for e in d['edges']], W=np.array(d['W'], float), line_idx=np.array(d['line_idx']), pnl=np.array(d['pnl']), phys=d['phys'], rb_meta=d['rb_meta'])
    return D, d
def real_arrays(D, d, labels):
    E = len(D['edges']); L = len(M2); Kt = np.zeros((4, 3)); Kr = np.zeros((4, 3)); Krb = np.zeros((4, E, L))
    for j, lab in enumerate(labels):
        raw = json.load(open(f'{HERE}/raw_qusoft_{lab}.json'))
        for i, c in enumerate(TARGETS):
            key = '1' + '0' * (NQ[c] - 1); Kt[j, i] = raw[f'T_{c}'].get(key, 0); Kr[j, i] = raw[f'R_{c}'].get(key, 0)
            assert sum(raw[f'T_{c}'].values()) == SHOTS and sum(raw[f'R_{c}'].values()) == SHOTS
        for name, meta in D['rb_meta'].items():
            cnt = raw[name]; nb = 2 * len(meta['edge_idx']); li = M2.index(meta['m'])
            for jj, ei in enumerate(meta['edge_idx']):
                Krb[j, ei, li] += sum(v for s, v in cnt.items() if s[nb - 1 - 2 * jj] == '0' and s[nb - 2 - 2 * jj] == '0')
    return dict(Kt=Kt, Kr=Kr, Krb=Krb)

if __name__ == '__main__':
    T = parse_theirs(); lines, ok = known_good(T); print('\n'.join(lines)); sc = scales(T)
    print('their model-minus-measured gaps (arithmetic on their numbers): ' + ', '.join(f'{k} {v:.4f}' for k, v in sc['gap'].items()) + f'; drift scale {sc["drift_p"]:.4f}; cz scale {sc["cz"]:.2e}; factor on their cz error / readout error that alone closes their n=21 gap {sc["f_need"][0]:.2f} / {sc["f_need"][1]:.2f}')
    print('R0 KNOWN-GOOD ' + ('PASS' if ok else 'FAIL'))
    if '--real' in sys.argv:
        D, d = load_design(); labels = ORDER; miss = [l for l in labels if not os.path.exists(f'{HERE}/raw_qusoft_{l}.json')]
        if miss: print('INCOMPLETE: missing jobs', miss); sys.exit(1)
        cz_l, ro_l = [], []
        for l in labels:
            c_, r_ = stated_from_props(json.load(open(f'{HERE}/props_qusoft_before_{l}.json')), D); cz_l.append(c_); ro_l.append(r_)
        D['stated_cz'] = np.nanmean(cz_l, axis=0); D['ro_stated_surv'] = np.mean(ro_l, axis=0); D['model_stated'] = model_stated_of(D, D['stated_cz'], D['ro_stated_surv'])
        print(f'stated record across the 4 saved records: max |cz diff| {np.nanmax(np.nanmax(cz_l, axis=0) - np.nanmin(cz_l, axis=0)):.1e}, max |readout-survival diff| {np.max(np.max(ro_l, axis=0) - np.min(ro_l, axis=0)):.1e}')
        K = real_arrays(D, d, labels); print('\n'.join(analyse(K, D, sc, np.random.default_rng(24))[0]))
