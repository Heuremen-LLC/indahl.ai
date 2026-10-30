"""zhukov.py -- free calibration run for A. Zhukov (independent), arXiv 2609.15411v2, DM-triangle study on ibm_kingston. Analysis only (fire is fire_zhukov.py).
His circuits are loaded as DATA (circuits.qpy via qiskit's loader; his code and raw/*/source were never run). Set S = 86 circuits = 76 of his (raw/003 control block: SPAM
packed 32 + SPAM solo lane 0 16 + axis 8 + Bell 12 = 68; raw/005 chain-C coherence at Jt = 4/3: exact and Strang r=8, XXX and YYY, rounds 0 and 1 = 8) plus 10 of OURS
(prep/readout separation arms: eight on physical qubit 16, two control copies on qubit 3, marked X). Four jobs in ABBA order: A1 B1 B2 A2; A = his order then ours, B = A reversed. 1024 shots, init_qubits True,
rep_delay 250 us, classified, DD off, twirling off (his runtime_options). Bit order: code = x1<<2|x2<<1|x3 with x1 = path[0] (q16 for lane 0); qiskit register tK clbit j <- path[j].

READINGS (each with four outcomes ABOVE / BELOW / CONSISTENT / CANNOT_TELL; 99 % intervals; scales fixed from HIS numbers, never from ours):
 (a) DELIVERED vs STATED on physical qubit 16 in his gateless SPAM controls: A1 P(read 1 | prep 0) packed, A2 P(read 0 | prep 1) packed, A3 / A4 the same solo; against the
     stated prob_meas1_prep0 / prob_meas0_prep1 in force (range over the five properties records saved before every job and after the last). ABOVE: delivered interval above the
     stated range; BELOW: below; CONSISTENT: overlaps it (a bound, printed); CANNOT_TELL: half-width > SCALE_A = 0.041 = 1 - 0.959, the worst control minimum he publishes.
     PREP vs READOUT: our arms. S0/S1 (MM) measure qubit 16 twice back to back after prep 0 / prep 1: Delta = P(r1 != r2) - 2 p(1-p), p = P(r1 = 1). Independent per-read assignment
     noise on a settled state predicts 0; a state already wrong before the readout predicts a negative Delta. BELOW rules OUT independent per-read noise; CONSISTENT rules out a
     persisting state; neither names a mechanism. D0 (DLY) = P(read 1 | prep 0, 100 us idle) - P(read 1 | prep 0, no idle). Outcome vs the band +-SCALE_A.
     SC = the MM statistic on qubit 3 (prep 0, healthy in his data): the control for 'a second read right after a first is never independent on this chip'.
 (b) DRIFT between jobs on his identical circuits: science lanes 1,2,3,5,6 of the packed circuits; T = chi2/dof of the 8-outcome histograms (cells with pooled count >= 10, his rule);
     B_WITHIN = median T over the pairs (A1,A2) and (B1,B2) (same circuit order, minutes apart); B_SLOT = median T of (A1+A2) against (B1+B2) (linear drift cancels; what is left is
     circuit-position / order). Null: shots permuted jointly across lanes between the two jobs. CANNOT_TELL if the null 99 % half-width of the median > SCALE_B = 0.41, half of the
     excess median T (1.72 observed vs 0.90 null) between his raw/003 and raw/004 on identical circuits 17 h apart (known_good_zhukov.text).
 (c) HIS CHAIN-C PHASE ERRORS: signed phase error of C1 = <X1> + i<Y1> against his stored exact-Hamiltonian probabilities at Jt = 4/3, chain C (lane 3), r=8 and exact, vs his value from
     raw/005 (46.3 deg, 2.9 deg), difference with BOTH sides' counting errors (S49 propagation) plus the job-to-job term; CANNOT_TELL if half-width > SCALE_C = 10 deg = one fifth of his
     published r=8 / r=16 contrast (46 vs 96). C_MIN: mean over the five chains of the minimum correct joint-outcome probability over the 24 raw/003 SPAM(standard)+axis controls, vs his
     value on the same circuits in raw/003 (parametric bootstrap both sides); CANNOT_TELL if half-width > SCALE_A. His published range 0.959-0.971 is for the raw/005 controls and is printed beside.
 (d) REPORTED, not scored: qubits 3 and 2 of the same register against their stated figures; solo minus packed (his +0.034 inside raw/003); per-chain minima.
Nothing here is a finding about his 16-17 Sep jobs: it is what these circuits read on this chip on the day, with the record in force."""
import json, os, sys, itertools, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TH = HERE + '/theirs'
LANES = [0, 1, 2, 3, 5, 6]; SCI = [1, 2, 3, 5, 6]; PATH = {0: [16, 3, 2], 1: [21, 36, 41], 2: [96, 103, 104], 3: [69, 68, 67], 5: [129, 118, 109], 6: [38, 49, 50]}
SHOTS = 1024; Z = 2.5758293035489; T3 = 3.182446305284263          # z 99 %, t(0.975, 3 dof) for 4 jobs
SCALE_A, SCALE_B, SCALE_C, DELAY_DT = 0.041, 0.41, 10.0, 25008     # DELAY_DT = 16 * 1563 dt, dt = 4 ns -> 100.03 us
ORDER = ['A1', 'B1', 'B2', 'A2']
EIG1 = np.array([1 - 2 * ((c >> 2) & 1) for c in range(8)], float)

# ---------------------------------------------------------------- his data
_cache = {}
def rows(exp):
    if exp not in _cache: _cache[exp] = json.load(open(f'{TH}/counts_{exp}.json'))['rows']
    return _cache[exp]
def codes_of(exp):
    k = 'c' + exp
    if k not in _cache: _cache[k] = np.load(f'{TH}/codes_{exp}.npz')['codes']
    return _cache[k]
def build_set():
    """S in order A: his raw/003 control block (his index order), his raw/005 chain-C Jt=4/3 circuits (his index order), then our 8."""
    S = []
    for i, r in enumerate(rows('003')):
        s = r['spec']
        if s['kind'] != 'dynamics': S.append(dict(src='003', row=i, kind=s['kind'], spec=s, lanes=s['lanes']))
    for i, r in enumerate(rows('005')):
        s = r['spec']
        if s['kind'] == 'dynamics' and s.get('experiment') == 'coherence' and abs(s['time'] - 4 / 3) < 1e-9:
            S.append(dict(src='005', row=i, kind='chainC', spec=s, lanes=s['lanes']))
    for name in ('MM0', 'MM1', 'DLY0', 'DLY1', 'MMC'):
        for rd in (0, 1): S.append(dict(src='X', row=None, kind='extra', spec=dict(name=name, round=rd), lanes=[0]))
    return S
SET = build_set(); NC = len(SET)
SETID = [f"{c['src']}:{c['row']}" if c['src'] != 'X' else f"X:{c['spec']['name']}_r{c['spec']['round']}" for c in SET]
def idx_where(f): return [i for i, c in enumerate(SET) if f(c)]
CTRL = idx_where(lambda c: c['src'] == '003' and ((c['kind'] == 'spam' and c['spec']['variant'] == 'standard') or c['kind'] == 'axis'))   # 24 controls
CHAINC = {(c['spec']['method'], c['spec']['basis']): [] for c in SET if c['src'] == '005'}
for i, c in enumerate(SET):
    if c['src'] == '005': CHAINC[(c['spec']['method'], c['spec']['basis'])].append(i)
XIDX = {n: idx_where(lambda c, n=n: c['src'] == 'X' and c['spec']['name'] == n) for n in ('MM0', 'MM1', 'DLY0', 'DLY1', 'MMC')}
SCIROWS = [i for i, c in enumerate(SET) if c['src'] != 'X' and 'solo' not in str(c['spec'].get('mode')) and len(c['lanes']) == 6]
A_ORDER = list(range(NC)); B_ORDER = A_ORDER[::-1]
def job_order(label): return A_ORDER if label[0] == 'A' else B_ORDER
def slot_pos(label):
    o = job_order(label); pos = np.zeros(NC, int)
    for p, i in enumerate(o): pos[i] = p
    return pos
def ref_probs(i, lane, key='hamiltonian_probabilities'):
    c = SET[i]; return np.array(rows(c['src'])[c['row']]['lanes'][str(lane)][key])
def counts8(code_vec): return np.bincount(code_vec.astype(int), minlength=8)[:8].astype(float)

# ---------------------------------------------------------------- stats helpers
def wilson(k, n, z=Z):
    if n == 0: return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return (c - h, c + h)
def combine(v, se_pool, z=Z):
    """v: per-job values; se_pool: standard error of their mean from counting statistics. half = max(z * se_pool, t3 * sd / sqrt(J))."""
    v = np.asarray(v, float); J = len(v); m = v.mean(); hb = T3 * v.std(ddof=1) / np.sqrt(J) if J > 1 else 0.0
    h = max(z * se_pool, hb); return m, m - h, m + h
def outcome_vs_range(lo, hi, rlo, rhi, scale):
    if not np.isfinite(lo) or (hi - lo) / 2 > scale: return 'CANNOT_TELL'
    return 'ABOVE' if lo > rhi else 'BELOW' if hi < rlo else 'CONSISTENT'
def outcome_band(lo, hi, m):
    if not np.isfinite(lo) or (hi - lo) / 2 > m: return 'CANNOT_TELL'
    if lo > m: return 'ABOVE'
    if hi < -m: return 'BELOW'
    return 'CONSISTENT' if (lo >= -m and hi <= m) else 'CANNOT_TELL'
def outcome_vs_zero(lo, hi, scale):
    if not np.isfinite(lo) or (hi - lo) / 2 > scale: return 'CANNOT_TELL'
    return 'ABOVE' if lo > 0 else 'BELOW' if hi < 0 else 'CONSISTENT'

# ---------------------------------------------------------------- stated record
def stated_q(props):
    return {i: {x['name']: x['value'] for x in ps} for i, ps in enumerate(props['qubits'])}
def stated_range(records, q):
    p10 = [stated_q(p)[q]['prob_meas1_prep0'] for p in records]; p01 = [stated_q(p)[q]['prob_meas0_prep1'] for p in records]
    return (min(p10), max(p10), min(p01), max(p01))

# ---------------------------------------------------------------- (a) delivered vs stated, qubit bits
BIT = {16: 2, 3: 1, 2: 0}
def arm(mode, prep):
    """circuit indices: SPAM with lane 0 active, packed (standard + register_permuted) or solo, qubit-16 prepared bit == prep."""
    return idx_where(lambda c: c['src'] == '003' and c['kind'] == 'spam' and (c['spec']['mode'] == 'solo') == (mode == 'solo') and ((c['spec']['pattern'] >> 2) & 1) == prep)
def arm_q(mode, prep, q):
    b = 2 - [16, 3, 2].index(q); return idx_where(lambda c: c['src'] == '003' and c['kind'] == 'spam' and (c['spec']['mode'] == 'solo') == (mode == 'solo') and ((c['spec']['pattern'] >> b) & 1) == prep)
def reads_one(codes_j, ids, q):
    bit = BIT[q]; a = np.concatenate([(codes_j[i, :, 0].astype(int) >> bit) & 1 for i in ids]); return int(a.sum()), int(len(a))
def reading_a_one(codes, mode, prep, q, srange):
    """codes (J, NC, S, 6). returns dict with delivered rate (P(read wrong)), interval, stated range, outcome. prep 0 -> P(read 1); prep 1 -> P(read 0)."""
    ids = arm_q(mode, prep, q); ks, ns = zip(*[reads_one(codes[j], ids, q) for j in range(len(codes))]); ks = np.array(ks, float); ns = np.array(ns, float)
    v = ks / ns if prep == 0 else 1 - ks / ns; K = ks.sum() if prep == 0 else ns.sum() - ks.sum(); N = ns.sum()
    wl, wh = wilson(K, N); m = v.mean(); hb = T3 * v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0
    lo, hi = min(wl, m - hb), max(wh, m + hb); rlo, rhi = (srange[0], srange[1]) if prep == 0 else (srange[2], srange[3])
    return dict(value=float(m), lo=float(lo), hi=float(hi), per_job=[float(x) for x in v], stated=(rlo, rhi), n=int(N), outcome=outcome_vs_range(lo, hi, rlo, rhi, SCALE_A))
def reading_a(codes, srange_by_q):
    out = {}
    for q in (16, 3, 2):
        for mode in ('packed', 'solo'):
            for prep in (0, 1): out[f'A q{q} {mode} prep{prep}'] = reading_a_one(codes, mode, prep, q, srange_by_q[q])
    return out

# ---------------------------------------------------------------- prep/readout separation arms (ours)
def mm_delta(cell):
    """cell: counts of (r1 r2) = 00,01,10,11 as index r1 + 2*r2 ... use k = r1 | r2<<1. returns Delta = P(r1 != r2) - 2 p (1-p) and its delta-method standard error."""
    n = cell.sum(); p = cell / n; r1 = p[1] + p[3]; d = p[1] + p[2]; g = d - 2 * r1 * (1 - r1)
    grad = np.array([0.0, 1 - (2 - 4 * r1), 1.0, 1 - (2 - 4 * r1)])      # d/dp_k of d - 2 r1 (1-r1): r1 = p1 + p3
    cov = (np.diag(p) - np.outer(p, p)) / n; se = float(max(np.sqrt(max(grad @ cov @ grad, 0.0)), 1.5 / n))      # floor: zero observed events still carry the rule-of-three width
    return float(g), se
def x_cells(codes_j, name):
    ids = XIDX[name]; v = np.concatenate([codes_j[i, :, 0].astype(int) for i in ids]); return v
def reading_sep(codes):
    out = {}
    for name, lab in (('MM0', 'S0 MM prep0'), ('MM1', 'S1 MM prep1'), ('MMC', 'SC MM prep0 on qubit 3 (control)')):
        vals, ses, cell_tot = [], [], np.zeros(4)
        for j in range(len(codes)):
            c = np.bincount(x_cells(codes[j], name) & 3, minlength=4).astype(float); g, se = mm_delta(c); vals.append(g); ses.append(se); cell_tot += c
        gpool, sepool = mm_delta(cell_tot); m, lo, hi = combine(vals, sepool)
        p1 = (cell_tot[1] + cell_tot[3]) / cell_tot.sum(); dobs = (cell_tot[1] + cell_tot[2]) / cell_tot.sum()
        out[lab] = dict(value=m, lo=lo, hi=hi, per_job=vals, p_read1_first=float(p1), disagree=float(dobs), outcome=outcome_band(lo, hi, SCALE_A))
    v0 = []; se0 = []
    tot_d = tot_m = 0
    for j in range(len(codes)):
        d = np.concatenate([x_cells(codes[j], 'DLY0') & 1]); m0 = np.concatenate([x_cells(codes[j], 'MM0') & 1])
        pd_, pm_ = d.mean(), m0.mean(); v0.append(pd_ - pm_); se0.append(max(np.sqrt(pd_ * (1 - pd_) / len(d) + pm_ * (1 - pm_) / len(m0)), 1.5 / len(d)))
    m, lo, hi = combine(v0, float(np.sqrt(np.sum(np.square(se0))) / len(v0)))
    out['D0 DLY prep0 100us minus none'] = dict(value=m, lo=lo, hi=hi, per_job=[float(x) for x in v0], outcome=outcome_band(lo, hi, SCALE_A))
    return out

# ---------------------------------------------------------------- (b) drift: chi2/dof of 8-outcome histograms, permutation null jointly over lanes
def _rows_T(X, Y, rng, B):
    """X (nA, 6), Y (nB, 6) codes for one circuit (uint8, lane order LANES). returns obs T per science row (R,), null T (B, R)."""
    nA, nB = len(X), len(Y); N = nA + nB; pool = np.concatenate([X, Y]); lab0 = np.concatenate([np.zeros(nA), np.ones(nB)]); obs, nul = [], []
    labs = rng.permuted(np.tile(lab0, (B, 1)), axis=1).astype(np.float32) if B else None
    for k in range(6):
        if LANES[k] not in SCI: continue
        c = pool[:, k].astype(int)
        if (c == 255).any(): continue
        h = np.bincount(c, minlength=8)[:8].astype(float); keep = h >= 10
        if keep.sum() < 2: continue
        oh = np.eye(8, dtype=np.float32)[c][:, keep]; hk = h[keep]; eA = hk * nA / N; eB = hk * nB / N
        a1 = (lab0[:, None].astype(np.float32) * oh).sum(0); chi = lambda cB: (((hk - cB) - eA) ** 2 / eA).sum(-1) + ((cB - eB) ** 2 / eB).sum(-1)
        obs.append(chi(a1) / (keep.sum() - 1))
        if B: nul.append(chi(labs @ oh) / (keep.sum() - 1))
    return np.array(obs), (np.stack(nul, axis=1) if B and nul else None)
def median_T(codesA, codesB, ids, rng, B=300):
    """codesA/B: (NC, S, 6). median T over rows of circuits `ids`; null (B,) of the same median under joint shot permutation."""
    obs, nul = [], []
    for i in ids:
        o, n = _rows_T(codesA[i], codesB[i], rng, B)
        if len(o): obs.append(o); nul.append(n)
    if not obs: return float('nan'), None, 0
    obs = np.concatenate(obs); nul = np.concatenate(nul, axis=1); return float(np.median(obs)), np.median(nul, axis=1), len(obs)
def reading_b(codes, rng, B=300):
    """codes (4, NC, S, 6) in ORDER A1 B1 B2 A2."""
    A1, B1, B2, A2 = codes; ids = SCIROWS; out = {}
    pr = {}
    for nm_, (X, Y) in (('AA', (A1, A2)), ('BB', (B1, B2))):
        ob, nu = [], []
        for i in ids:
            o, n = _rows_T(X[i], Y[i], rng, B)
            if len(o): ob.append(o); nu.append(n)
        pr[nm_] = (np.concatenate(ob), np.concatenate(nu, axis=1)) if ob else (np.zeros(0), None)
    def med(parts):
        o = np.concatenate([p[0] for p in parts])
        if len(o) == 0: return float('nan'), None, 0
        return float(np.median(o)), np.median(np.concatenate([p[1] for p in parts if len(p[0])], axis=1), axis=1), len(o)
    o1, n1, r1 = med([pr['AA']]); o2, n2, r2 = med([pr['BB']]); ow, nw, rw = med([pr['AA'], pr['BB']])
    AA = np.concatenate([A1, A2], axis=1); BB = np.concatenate([B1, B2], axis=1)
    os_, ns, rs = median_T(AA, BB, ids, rng, B)
    def verdict(o, n):
        if n is None or len(n) == 0 or not np.isfinite(o): return dict(value=float('nan'), lo=float('nan'), hi=float('nan'), null_median=float('nan'), rows=0, outcome='CANNOT_TELL')
        lo, hi = np.percentile(n, [0.5, 99.5]); med = float(np.median(n))
        oc = 'CANNOT_TELL' if (hi - lo) / 2 > SCALE_B else 'ABOVE' if o > hi else 'BELOW' if o < lo else 'CONSISTENT'
        return dict(value=o, lo=float(lo), hi=float(hi), null_median=med, rows=int(0), outcome=oc)
    out['B_WITHIN median T (A1|A2, B1|B2)'] = dict(verdict(ow, nw), rows=rw); out['B_SLOT median T (A1+A2 | B1+B2)'] = dict(verdict(os_, ns), rows=rs)
    out['B_pair_AA (reported)'] = dict(verdict(o1, n1), rows=r1); out['B_pair_BB (reported)'] = dict(verdict(o2, n2), rows=r2)
    return out

# ---------------------------------------------------------------- (c) phase and control minima
def c1_from_counts(cx, cy, ref):
    """C1 = <X1> + i<Y1> from 8-outcome counts of the XXX and YYY circuits; signed error = angle(meas * conj(ref)); SE by S49 propagation (counting error only)."""
    x = (cx / cx.sum()) @ EIG1; y = (cy / cy.sum()) @ EIG1; sx = np.sqrt(max(1 - x * x, 1e-12) / cx.sum()); sy = np.sqrt(max(1 - y * y, 1e-12) / cy.sum())
    m = x + 1j * y; r = ref[0] + 1j * ref[1]; e = np.degrees(np.angle(m * np.conj(r))); R2 = x * x + y * y
    se = np.degrees(np.sqrt(y * y * sx * sx + x * x * sy * sy) / R2) if R2 > 1e-9 else 90.0
    return float(e), float(se), float(abs(m))
def chainC_counts(codes_j, method):
    out = {}
    for b in ('XXX', 'YYY'):
        out[b] = sum(counts8(codes_j[i, :, 3]) for i in CHAINC[(method, b)])
    return out
def chainC_ref(method):
    ref = []
    for b in ('XXX', 'YYY'):
        i = CHAINC[(method, b)][0]; ref.append(float(ref_probs(i, 3) @ EIG1))
    return ref
def his_phase(method):
    r5 = rows('005'); out = {}
    for b in ('XXX', 'YYY'):
        out[b] = sum(np.array(r5[i_row]['lanes']['3']['counts'], float) for i_row in [SET[i]['row'] for i in CHAINC[(method, b)]])
    return c1_from_counts(out['XXX'], out['YYY'], chainC_ref(method)), out
def ctrl_correct(codes_j, ids, lane):
    """correct joint-outcome probability for each control circuit in ids (ideal modal code of that circuit and lane)."""
    ks = []
    for i in ids:
        idp = ref_probs(i, lane, 'ideal_probabilities'); ks.append(float((codes_j[i, :, LANES.index(lane)] == idp.argmax()).sum()))
    return np.array(ks)
def his_ctrl():
    out = {}
    for lane in SCI:
        k = []
        for i in CTRL:
            c = np.array(rows('003')[SET[i]['row']]['lanes'][str(lane)]['counts'], float); idp = ref_probs(i, lane, 'ideal_probabilities'); k.append(c[idp.argmax()])
        out[lane] = np.array(k)
    return out
def reading_c(codes, his_p=None, his_k=None, rng=None, B=3000):
    """his_p: {method: (counts_dict)} (default: his raw/005); his_k: {lane: correct counts over CTRL} (default his raw/003)."""
    rng = rng or np.random.default_rng(11); out = {}
    for method, lab, pub in (('strang8', 'C_STRANG8 signed phase error at Jt=4/3 (deg)', 46.3), ('exact', 'C_EXACT signed phase error at Jt=4/3 (deg)', 2.9)):
        if his_p is None: hv, hcnt = his_phase(method)
        else: hcnt = his_p[method]; hv = c1_from_counts(hcnt['XXX'], hcnt['YYY'], chainC_ref(method))
        ev, ses, mods = [], [], []
        for j in range(len(codes)):
            cc = chainC_counts(codes[j], method); e, se, mod = c1_from_counts(cc['XXX'], cc['YYY'], chainC_ref(method)); ev.append(e); ses.append(se); mods.append(mod)
        sepool = float(np.sqrt(np.sum(np.square(ses))) / len(ev)); m, lo, hi = combine(ev, np.sqrt(sepool ** 2 + hv[1] ** 2))     # his counting error enters the difference
        d = m - hv[0]; hw = (hi - lo) / 2
        out[lab] = dict(value=float(d), lo=float(d - hw), hi=float(d + hw), ours=float(m), his=float(hv[0]), per_job=[float(x) for x in ev], abs_ours=float(abs(m)), modulus=[float(x) for x in mods],
                        published=pub, outcome=outcome_vs_zero(d - hw, d + hw, SCALE_C))
    his_k = his_k or his_ctrl(); n = codes.shape[2]; per_job = []; boots = []
    for j in range(len(codes)):
        mins = []; bm = np.zeros(B)
        for lane in SCI:
            k = ctrl_correct(codes[j], CTRL, lane); mins.append((k / n).min())
            bm += (rng.binomial(n, np.clip(k / n, 1e-9, 1 - 1e-9), size=(B, len(k))) / n).min(axis=1)
        per_job.append(float(np.mean(mins))); boots.append(bm / len(SCI))
    hm = np.mean([(his_k[l] / SHOTS).min() for l in SCI]); hb = np.zeros(B)
    for lane in SCI: hb += (rng.binomial(SHOTS, np.clip(his_k[lane] / SHOTS, 1e-9, 1 - 1e-9), size=(B, len(his_k[lane]))) / SHOTS).min(axis=1)
    hb /= len(SCI); ours_b = np.mean(boots, axis=0); diff_b = ours_b - hb; obs = float(np.mean(per_job) - hm)
    lo, hi = np.percentile(diff_b, [0.5, 99.5]); lo, hi = obs + (lo - np.median(diff_b)), obs + (hi - np.median(diff_b))
    bj = T3 * np.std(per_job, ddof=1) / np.sqrt(len(per_job)); lo, hi = min(lo, obs - bj), max(hi, obs + bj)
    out['C_MIN mean over chains of min correct joint-outcome prob (ours - his, raw/003 controls)'] = dict(value=obs, lo=float(lo), hi=float(hi), ours=float(np.mean(per_job)), his=float(hm), per_job=per_job,
        outcome=outcome_vs_zero(lo, hi, SCALE_A))
    return out

# ---------------------------------------------------------------- everything
def analyse(codes, srange_by_q, his_p=None, his_k=None, rng=None, B=300):
    rng = rng or np.random.default_rng(24); res = {}
    res.update(reading_a(codes, srange_by_q)); res.update(reading_sep(codes)); res.update(reading_b(codes, rng, B)); res.update(reading_c(codes, his_p, his_k, rng))
    return res
SCORED = ['A q16 packed prep0', 'A q16 packed prep1', 'A q16 solo prep0', 'A q16 solo prep1', 'S0 MM prep0', 'S1 MM prep1', 'SC MM prep0 on qubit 3 (control)', 'D0 DLY prep0 100us minus none',
          'B_WITHIN median T (A1|A2, B1|B2)', 'B_SLOT median T (A1+A2 | B1+B2)', 'C_STRANG8 signed phase error at Jt=4/3 (deg)', 'C_EXACT signed phase error at Jt=4/3 (deg)',
          'C_MIN mean over chains of min correct joint-outcome prob (ours - his, raw/003 controls)']
def fmt(res):
    L = []
    for k, r in res.items():
        extra = ''
        if 'stated' in r: extra = f" stated [{r['stated'][0]:.4f}, {r['stated'][1]:.4f}]"
        if 'null_median' in r: extra = f" null median {r['null_median']:.3f} rows {r['rows']}"
        if 'his' in r: extra = f" ours {r['ours']:.4f} his {r['his']:.4f}"
        L.append(f"{k:92s} = {r['value']:.4f} [{r['lo']:.4f}, {r['hi']:.4f}]{extra} -> {r['outcome']}")
    return L

# ---------------------------------------------------------------- loading real data
def load_real():
    rec = json.load(open(f'{HERE}/job_zhukov.json')); codes = []
    for lab in ORDER:
        z = np.load(f'{HERE}/raw_zhukov_{lab}.npz'); codes.append(z['codes'])
    recs = [json.load(open(f'{HERE}/props_zhukov_before_{lab}.json')) for lab in ORDER] + [json.load(open(f'{HERE}/props_zhukov_after.json'))]
    return np.array(codes), recs, rec

# ---------------------------------------------------------------- KNOWN-GOOD on his raw data
def known_good():
    L, ok = [], True
    c5 = codes_of('005'); r5 = rows('005'); c3 = codes_of('003'); r3 = rows('003'); c4 = codes_of('004'); r4 = rows('004')
    dyn = [i for i, r in enumerate(r5) if r['spec']['kind'] == 'dynamics' and 0 in r['spec']['lanes']]
    p000 = float(np.min([(c5[i, :, 0] == 0).mean() for i in dyn])); g = round(p000, 3) == 0.288; ok &= g
    L.append(f'KG1 smallest P000 of the sentinel register over {len(dyn)} dynamical circuits, raw/005: {p000:.4f} -> rounds to {round(p000,3)}; published 0.288 -> {"PASS" if g else "FAIL"}')
    mins = []
    for lane in SCI:
        v = []
        for i, r in enumerate(r5):
            s = r['spec']
            if s['kind'] not in ('spam', 'axis') or str(lane) not in r['lanes']: continue
            L5 = r['lanes'][str(lane)]; cnt = np.array(L5['counts'], float); v.append(cnt[np.argmax(L5['ideal_probabilities'])] / cnt.sum())
        mins.append(min(v))
    g = round(min(mins), 3) == 0.959 and round(max(mins), 3) == 0.971; ok &= g
    L.append(f'KG2 control minima per chain (lanes 1,2,3,5,6), raw/005: ' + ', '.join(f'{m:.4f}' for m in mins) + f' -> {round(min(mins),3)} to {round(max(mins),3)}; published 0.959 to 0.971 -> {"PASS" if g else "FAIL"}')
    pub = {('strang8', '005'): 46.3, ('exact', '005'): 2.9}
    # phase from counts.json of 005 chain C (this module's code) and 003 r=16 / exact
    for method, ref in (('strang8', 46), ('exact', 3)):
        hv, _ = his_phase(method); g = abs(abs(hv[0]) - ref) < 1.0 if method == 'strang8' else abs(abs(hv[0]) - ref) < 0.5; ok &= g
        L.append(f'KG3 raw/005 chain C {method} Jt=4/3: signed phase error {hv[0]:.2f} deg (counting se {hv[1]:.2f}), |C1| {hv[2]:.3f}; published "approximately {ref}" -> {"PASS" if g else "FAIL"}')
    sel = lambda s, st: s.get('example') == 'full' and abs(s['time'] - 4 / 3) < 1e-9 and s['mode'] == 'packed' and s['method'] == st[0] and (st[1] is None or s['steps'] == st[1])
    for lab, st, ref in (('strang r=16', ('strang', 16), 96), ('exact', ('exact', None), 3)):
        cnt = {}; refp = {}
        for b in ('XXX', 'YYY'):
            ii = [i for i, r in enumerate(r3) if r['spec']['kind'] == 'dynamics' and sel(r['spec'], st) and r['spec']['basis'] == b]
            cnt[b] = sum(np.array(r3[i]['lanes']['3']['counts'], float) for i in ii); refp[b] = float(np.array(r3[ii[0]]['lanes']['3']['hamiltonian_probabilities']) @ EIG1)
        e, se, mod = c1_from_counts(cnt['XXX'], cnt['YYY'], (refp['XXX'], refp['YYY'])); g = abs(abs(e) - ref) < 1.0 if ref > 10 else abs(abs(e) - ref) < 0.5; ok &= g
        L.append(f'KG3 raw/003 chain C {lab} Jt=4/3: signed phase error {e:.2f} deg, |C1| {mod:.3f}; published "approximately {ref}" -> {"PASS" if g else "FAIL"}')
    # sentinel numbers from his SPAM controls (our decode of his codes; BONES FINAL values)
    codes3 = c3[:, :, [0]]
    def pooled(mode, prep):
        ids = [i for i, r in enumerate(r3) if r['spec']['kind'] == 'spam' and 0 in r['spec']['lanes'] and r['spec']['mode'] == mode and ((r['spec']['pattern'] >> 2) & 1) == prep]
        a = np.concatenate([(c3[i, :, 0].astype(int) >> 2) & 1 for i in ids]); return a.mean(), np.sqrt(a.mean() * (1 - a.mean()) / len(a))
    for mode, prep, want, wse in (('solo', 0, 0.7657, 0.0047), ('solo', 1, 0.8927, 0.0034), ('packed', 0, 0.7315, 0.0035)):
        v, se = pooled(mode, prep); g = abs(v - want) < 5e-4 and abs(se - wse) < 2e-4; ok &= g
        L.append(f'KG4 raw/003 qubit 16 {mode} prep{prep}: P(read 1) {v:.4f} +- {se:.4f}; Bones final {want} +- {wse} -> {"PASS" if g else "FAIL"}')
    # decode self-check: modal ideal code of the SPAM controls equals the pattern read as x1 = MSB
    bad = 0
    for i, r in enumerate(r3):
        s = r['spec']
        if s['kind'] == 'spam' and 0 in s['lanes']:
            idp = np.array(r['lanes']['0']['ideal_probabilities']); bad += int(idp.argmax() != s['pattern'])
    g = bad == 0; ok &= g; L.append(f'KG5 bit order: ideal modal code equals the SPAM pattern (x1 = MSB = q16) in {sum(1 for r in r3 if r["spec"]["kind"]=="spam" and 0 in r["spec"]["lanes"]) - bad} of {sum(1 for r in r3 if r["spec"]["kind"]=="spam" and 0 in r["spec"]["lanes"])} circuits -> {"PASS" if g else "FAIL"}')
    # scale B: median T of his identical circuits 17 h apart (003 vs 004), science lanes, packed dynamics, same keys
    rng = np.random.default_rng(7)
    def key(s): return (s['kind'], s.get('example'), s.get('method'), s.get('steps'), round(s.get('time', -1), 9), s.get('basis'), s.get('pattern'), s.get('input'), s['mode'])
    g3 = {}; g4 = {}
    for rr, cc, gg in ((r3, c3, g3), (r4, c4, g4)):
        for i, r in enumerate(rr):
            s = r['spec']
            if s['kind'] != 'dynamics' or s['mode'] != 'packed': continue
            gg.setdefault(key(s), []).append(cc[i][:, :])
    obs, nul = [], []
    for k in g4:
        if k in g3 and sum(len(a) for a in g3[k]) == sum(len(a) for a in g4[k]):
            X = np.concatenate(g3[k])[:, LANES]; Y = np.concatenate(g4[k])[:, LANES]; o, n = _rows_T(X, Y, rng, 200); obs.append(o); nul.append(n)
    obs = np.concatenate(obs); nul = np.concatenate(nul, axis=1); ob = float(np.median(obs)); nm = float(np.median(np.median(nul, axis=1)))
    g = abs(ob - 1.72) < 0.06 and abs(nm - 0.90) < 0.06 and abs((ob - nm) / 2 - SCALE_B) < 0.03; ok &= g
    L.append(f'KG6 SCALE_B: his raw/003 vs raw/004 identical circuits, {len(obs)} rows: median T {ob:.2f} vs null median {nm:.2f}; half the excess {(ob-nm)/2:.3f}; SCALE_B fixed at {SCALE_B} -> {"PASS" if g else "FAIL"}')
    L.append('R0 KNOWN-GOOD -> ' + ('PASS' if ok else 'FAIL')); return L, ok

if __name__ == '__main__':
    if '--real' in sys.argv:
        codes, recs, rec = load_real(); sr = {q: stated_range(recs, q) for q in (16, 3, 2)}
        print('\n'.join(fmt(analyse(codes, sr))))
    else:
        L, ok = known_good(); print('\n'.join(L)); sys.exit(0 if ok else 1)
