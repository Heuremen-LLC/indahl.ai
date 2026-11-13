#!/usr/bin/env python3
"""three_seats_run121.py -- THREE SEATS ON ONE EVENT: run 121, ibm_pittsburgh (the no-name shot). Bones, by hand, 2026-10-03. INTERNAL.
Read-only on the data, the frozen code and the ledger; writes only under parallax/darkwave_disco/internal/. Contacts no account, submits nothing.
No verdict word. Every number names its clock:
  LAID    = our laid times on the maker's tick (the realized stretch lengths, 9.984 / 30.016 / 89.984 us)
  WITNESS = the frame-held spectator's phase (degrees)
  OWN     = the emitter's own end level and its own fading rulers (R10 / R30 / R90 / R300 of the same job)
The seats, per emitter-witness pair:
  SEAT 1 (OWN, short clock): emitter end level minus the each-stretch-own-ruler book   (readnoname.book, survivals R10/R30/R90 per stretch)
  SEAT 2 (OWN, long clock):  emitter end level minus the one-clock book                 (readnoname.book, survival R300^(L/300) per stretch)
  SEAT 3 (WITNESS):          the witness's half-difference angle, emitters started ON minus started OFF (readnoname's 'half'), divided by the
                             5 LAID ON stretches; second reading: the reader's fitted coupling (readnoname.fit_witness, own and chip-typical fading)
Bootstrap over shots exactly as readnoname.py does (seed 20261004, NB = 100, every circuit resampled on its own). Because the draws are the reader's own,
the reader's run-121 read (reads/noname_read1.txt) is rebuilt line by line from the same resamples as a check.
  python3 three_seats_run121.py [--nb 100] [--nbe 2000] [--no-md]"""
import sys
sys.dont_write_bytecode = True                       # never leave a __pycache__ beside the frozen code
import argparse, datetime, hashlib, json, math, os, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = '/Users/heuremen/bones-forge/parallax/darkwave_disco/for_indahl_ai/data'
DATA = '/Users/heuremen/bones-forge/parallax/out/qubit_fifth_run/data/fire/ibm_pittsburgh'
RUN = 121
ROLES = os.path.join(FROZEN, 'reads', 'noname_roles.json')
READ1 = os.path.join(FROZEN, 'reads', 'noname_read1.txt')
COPY = os.path.join(HERE, 'readnoname_copy_20261003.py')
OUT_MD = os.path.join(HERE, 'THREE_SEATS_RUN121_20261003.md')
OUT_JSON = os.path.join(HERE, 'three_seats_run121_20261003.json')
sys.path.insert(0, HERE); sys.path.append(os.path.join(FROZEN, 'code'))
import readnoname_copy_20261003 as RD               # byte-identical copy of the frozen reader (checked below); its arms() imports the frozen noname.py

CORE = list(RD.CORE); ARMS = CORE + ['WA', 'WB']; POOLS = ['pool', 'core']
S3V = ['ahd5', 'ath_own', 'hd5', 'ath_typ']
S3NAME = {'ahd5': '|half-difference| / 5', 'ath_own': '|fitted coupling|, own fading', 'hd5': 'signed half-difference / 5',
          'ath_typ': '|fitted coupling|, chip-typical fading'}
EDGE_DEG = 33.0                                       # |theta| at or beyond this sits on the fit grid's edge (the grid stops at 34.38 deg)


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''): h.update(chunk)
    return h.hexdigest()


def integrity():
    sums = {}
    for line in open(os.path.join(FROZEN, 'SHA256SUMS.txt')):
        parts = line.split()
        if len(parts) == 2: sums[parts[1]] = parts[0]
    rows = []
    for rel in ('code/readnoname.py', 'code/noname.py', 'code/common.py', 'reads/noname_roles.json', 'reads/layout_156_family.json', 'reads/noname_read1.txt'):
        got = sha(os.path.join(FROZEN, rel)); rows.append([rel, got, sums.get(rel), got == sums.get(rel)])
    got = sha(COPY); rows.append(['internal/readnoname_copy_20261003.py (copy)', got, sums['code/readnoname.py'], got == sums['code/readnoname.py']])
    meta = json.load(open(os.path.join(DATA, f'run{RUN}_meta.json')))
    got = sha(os.path.join(DATA, f'run{RUN}_results.npz')); rows.append([f'run{RUN}_results.npz', got, meta['results_sha256'], got == meta['results_sha256']])
    rows.append([f'run{RUN}_meta.json', sha(os.path.join(DATA, f'run{RUN}_meta.json')), None, None])
    return rows


def chip_coords(edges, n=156):
    """grid position of every bit: main rows of 16 (q = 20 r + 0..15) at y = 2 r; bridge bits (20 r + 16..19) at y = 2 r + 1, under their upper neighbour."""
    nb = {q: set() for q in range(n)}
    for a, b in edges: nb[a].add(b); nb[b].add(a)
    xy = {}
    for q in range(n):
        blk, off = divmod(q, 20)
        xy[q] = (2 * blk, off) if off < 16 else (2 * blk + 1, min(nb[q]) % 20)
    return xy, nb


def laid(S, dt):
    """LAID clock: realized stretch lengths (the run's own _realize on the 16-dt grid at the chip's dt), ON / OFF / total per arm."""
    nn = sys.modules['noname']; out = {}
    for k, lab in [(c, c) for c in CORE] + [('WA|X', 'WA'), ('WB|X', 'WB')]:
        s = S[k]; st = s['pushes']; real = [nn._realize(dt, d)[1] for d in st]
        on_i = list(range(1, len(st), 2)) if s['start'] == 'OFF' else list(range(0, len(st), 2))
        pushes = len(st) + bool(s['flip']); end = s['start'] if pushes % 2 == 0 else ('ON' if s['start'] == 'OFF' else 'OFF')
        out[lab] = {'start': s['start'], 'end': end, 'stretches_us': st, 'pushes': pushes, 'flip': bool(s['flip']),
                    'on_us': sum(real[i] for i in on_i), 'off_us': sum(real) - sum(real[i] for i in on_i), 'total_us': sum(real), 'n_on': len(on_i)}
    return out


def seats(A, S, pairs, E):
    """the three seats for every pair (fixed pair list), from one set of shots. Mirrors readnoname.stats line for line where it overlaps."""
    al, pe, sep = RD.frame(A); g = sep > 4
    lv = {k: al(v).mean(0) for k, v in A.items()}; n = lv['F0'].shape[0]
    Rr = {L: np.clip(lv[f'R{L}'], 0.02, 1.2) for L in (10, 30, 90, 300)}
    own = lambda L: Rr[L]                                             # each stretch its own ruler (the reader's own())
    one = lambda L: np.clip(lv['R300'], 0.02, 0.98) ** (L / 300.0)   # one clock through the 300-us arm (the reader's one())
    LV, S1, S2 = {}, {}, {}
    for k in CORE:
        s = S[k]; start = np.zeros(n) if s['start'] == 'OFF' else np.ones(n)
        LV[k] = lv[k]
        S1[k] = lv[k] - RD.book(start, [own(L) for L in s['pushes']], s['flip'])
        S2[k] = lv[k] - RD.book(start, [one(L) for L in s['pushes']], s['flip'])
    q30 = np.clip(lv['R30'], 0.02, 0.999)                            # the reader's witness-section ruler
    for lab, st in (('WA', 0.0), ('WB', 1.0)):                         # the emitter in the witness arms: both hand arms averaged, as the reader does
        le = (lv[f'{lab}|X'] + lv[f'{lab}|Y']) / 2; start = np.full(n, st)
        LV[lab] = le; S1[lab] = le - RD.book(start, [q30] * 10, False); S2[lab] = le - RD.book(start, [one(30)] * 10, False)
    va = (2 * lv['WA|X'] - 1) + 1j * (1 - 2 * lv['WA|Y']); vb = (2 * lv['WB|X'] - 1) + 1j * (1 - 2 * lv['WB|Y'])
    typ = float(np.median(q30[g]))
    w = np.array([p[0] for p in pairs]); e = np.array([p[1] for p in pairs]); Ea = np.array(E)
    hd = np.degrees(np.angle(vb[w] * np.conj(va[w])) / 2)            # the reader's 'half', per witness, WITNESS degrees over the 5 LAID ON stretches
    tho, tht, mio, mit = [], [], [], []
    for wi, ei in pairs:
        mo, to = RD.fit_witness(va[wi], vb[wi], q30[ei]); mt, tt = RD.fit_witness(va[wi], vb[wi], typ)
        tho.append(math.degrees(to)); tht.append(math.degrees(tt)); mio.append(mo); mit.append(mt)
    tho = np.array(tho); tht = np.array(tht)
    P = {'hd': hd, 'hd5': hd / 5.0, 'ahd5': np.abs(hd) / 5.0, 'th_own': tho, 'th_typ': tht, 'ath_own': np.abs(tho), 'ath_typ': np.abs(tht),
         'mis_own': np.array(mio), 'mis_typ': np.array(mit), 'len_a': np.abs(va[w]), 'len_b': np.abs(vb[w]),
         'leftover': np.degrees(np.angle(va[w] * vb[w]) / 2), 'q30_e': q30[e], 'typ': typ, 'n_readable': int(g.sum()),
         'theta_median_own': float(np.median(np.abs(tho)))}
    for k in ARMS:
        P['S1|' + k] = S1[k][e]; P['S2|' + k] = S2[k][e]; P['LV|' + k] = LV[k][e]
        P['E|S1|' + k] = S1[k][Ea]; P['E|S2|' + k] = S2[k][Ea]; P['E|LV|' + k] = LV[k][Ea]
    for tag, arms_ in (('pool', ARMS), ('core', CORE)):
        P['S1|' + tag] = np.mean([P['S1|' + k] for k in arms_], 0); P['S2|' + tag] = np.mean([P['S2|' + k] for k in arms_], 0)
        P['E|S1|' + tag] = np.mean([P['E|S1|' + k] for k in arms_], 0); P['E|S2|' + tag] = np.mean([P['E|S2|' + k] for k in arms_], 0)
    return P


def pear(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float); ok = np.isfinite(x) & np.isfinite(y)
    x = x[ok] - x[ok].mean(); y = y[ok] - y[ok].mean(); d = math.sqrt(float((x * x).sum() * (y * y).sum()))
    return float((x * y).sum() / d) if d > 0 else float('nan')


def rank(x): return np.argsort(np.argsort(np.asarray(x, float))).astype(float)


def zs(x): x = np.asarray(x, float); return (x - x.mean()) / x.std()


def corr_set(P, E, eidx, ei=None):
    """every across-pair correlation of the tables, from one set of per-pair seats. ei = emitter positions to use (None = all once); the pairs follow
    their emitters (a redrawn emitter brings all its witnesses), which is how the second width (over emitters) is drawn."""
    ei = np.arange(len(E)) if ei is None else np.asarray(ei)
    pi = np.concatenate([eidx[E[j]] for j in ei])
    out = {}
    for s3 in S3V:
        for seat in ('S1', 'S2'):
            for arm in ARMS + POOLS: out[f'{s3}~{seat}|{arm}'] = pear(P[s3][pi], P[f'{seat}|{arm}'][pi])
            out[f'{s3}~{seat}|pool@spearman'] = pear(rank(P[s3][pi]), rank(P[f'{seat}|pool'][pi]))
            x = np.array([P[s3][eidx[E[j]]].mean() for j in ei])                  # emitter level: seat 3 averaged over the emitter's witnesses
            out[f'{s3}~{seat}|pool@emitters'] = pear(x, P[f'E|{seat}|pool'][ei])
    for arm in ARMS + POOLS: out[f'S1~S2|{arm}'] = pear(P[f'S1|{arm}'][pi], P[f'S2|{arm}'][pi])
    for seat in ('S1', 'S2', 'LV'):                  # LV: the end level itself (no book, so no shared ruler between the two arms)
        out[f'retest {seat} A30_30~WA'] = pear(P[f'E|{seat}|A30_30'][ei], P[f'E|{seat}|WA'][ei])
        out[f'retest {seat} B30_30~WB'] = pear(P[f'E|{seat}|B30_30'][ei], P[f'E|{seat}|WB'][ei])
    out['ahd5~ath_own'] = pear(P['ahd5'][pi], P['ath_own'][pi]); out['ath_own~ath_typ'] = pear(P['ath_own'][pi], P['ath_typ'][pi])
    out['ahd5~len'] = pear(P['ahd5'][pi], ((P['len_a'] + P['len_b']) / 2)[pi])
    return out


def fingerprints(P, E, eidx):
    """a pair's spread across the twelve arms: raw, and beyond the chip's own arm-to-arm pattern (the mean over the 35 emitters per arm)."""
    out = {}
    for seat in ('S1', 'S2'):
        M = np.array([P[f'{seat}|{k}'] for k in ARMS])
        chip = np.array([P[f'E|{seat}|{k}'].mean() for k in ARMS])
        out[f'{seat}|raw'] = M.std(0, ddof=1); out[f'{seat}|beyond'] = (M - chip[:, None]).std(0, ddof=1); out[f'{seat}|chip_pattern'] = chip
    return out


def comove(P):
    return {'c1': zs(P['ahd5']) * zs(P['S1|pool']), 'c2': zs(P['ahd5']) * zs(P['S2|pool'])}


def region_of(xy_e):
    y, x = xy_e
    ry = 'top (q0-55)' if y <= 4 else ('middle (q56-99)' if y <= 9 else 'bottom (q100-155)')
    rx = 'left (cols 0-4)' if x <= 4 else ('centre (cols 5-10)' if x <= 10 else 'right (cols 11-15)')
    return ry, rx


def parse_read1():
    out = {}
    for line in open(READ1):
        mm = re.match(r'^   (.*?)\s+([+-]\d+\.\d+)\((\d+\.\d+)\)\s+\|', line)
        if mm: out[mm.group(1).strip()] = (mm.group(2), mm.group(3))
    return out


def reproduce(rbase, rreps):
    file = parse_read1(); rows = []
    for k, (v, w) in file.items():
        if k not in rbase: rows.append((k, v, w, None, None, False)); continue
        mv = f'{rbase[k]:+.4f}'; mw = f'{np.nanstd([b[k] for b in rreps]):.4f}'
        rows.append((k, v, w, mv, mw, mv == v and mw == w))
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--nb', type=int, default=RD.NB); ap.add_argument('--nbe', type=int, default=2000)
    ap.add_argument('--no-md', action='store_true'); a = ap.parse_args()
    integ0 = integrity()
    bad = [r for r in integ0 if r[3] is False]
    if bad: raise SystemExit(f'integrity check failed before reading: {bad}')
    S = RD.arms(); m, A = RD.load(DATA, RUN)
    roles = json.load(open(ROLES)); roles['witness_of'] = {int(k): int(v) for k, v in roles['witness_of'].items()}
    xy, nbr = chip_coords(roles['edges'])
    al, pe, sep = RD.frame(A); g = sep > 4
    pairs = [(w, e) for w, e in roles['witness_of'].items() if g[w] and g[e]]          # the reader's witness set W, in the reader's order
    E = sorted(set(e for _, e in pairs)); eidx = {e: np.array([i for i, p in enumerate(pairs) if p[1] == e]) for e in E}
    dropped = [(w, e) for w, e in roles['witness_of'].items() if not (g[w] and g[e])]
    LAID = laid(S, m['chip_dt_s']); on30 = sys.modules['noname']._realize(m['chip_dt_s'], 30)[1]
    print(f'run {RUN}: {int(g.sum())} readable bits, {len(pairs)} pairs, {len(E)} emitters; LAID 30-us stretch = {on30:.3f} us', flush=True)

    base = seats(A, S, pairs, E); rbase = RD.stats(A, S, roles)
    rng = np.random.default_rng(20261004)              # the reader's own seed and draw order -> the very same shot resamples as its run-121 read
    reps, rreps = [], []
    for b in range(a.nb):
        B = {k: v[rng.integers(0, v.shape[0], v.shape[0])] for k, v in A.items()}
        rreps.append(RD.stats(B, S, roles)); reps.append(seats(B, S, pairs, E))
        if (b + 1) % 20 == 0: print(f'  resample {b + 1}/{a.nb}', flush=True)
    repro = reproduce(rbase, rreps)
    print(f'reader reproduced: {sum(r[5] for r in repro)} of {len(repro)} lines (value and width to the printed 4 decimals)', flush=True)

    n = A['F0'].shape[0]; cuts = [0, n // 3, 2 * n // 3, n]
    thirds = [seats({k: v[cuts[t]:cuts[t + 1]] for k, v in A.items()}, S, pairs, E) for t in range(3)]

    W = lambda key: np.nanstd(np.array([r[key] for r in reps]), axis=0)               # width over shots (ddof 0, as the reader's nanstd)
    theta_ens = float(rbase['coupling read by the witness (deg per 30-us ON stretch, median)'])  # the reader's ensemble median, deg per 30-us ON stretch
    tW = lambda x: on30 * np.asarray(x) / theta_ens                                    # WITNESS-equivalent ON time per LAID ON stretch (one constant for all pairs)

    # ---------- per-pair records
    pr = {}
    keys = ['hd', 'hd5', 'ahd5', 'th_own', 'th_typ', 'ath_own', 'ath_typ', 'mis_own', 'mis_typ', 'len_a', 'len_b', 'leftover', 'q30_e'] + \
           [f'{s}|{k}' for s in ('S1', 'S2', 'LV') for k in ARMS] + [f'{s}|{t}' for s in ('S1', 'S2') for t in POOLS]
    for k in keys: pr[k] = (base[k], W(k))
    hd2 = np.radians(2 * np.array([r['hd'] for r in reps]))                            # circular width for the signed half-difference
    pr['hd_circ_width'] = np.degrees(np.sqrt(-2 * np.log(np.clip(np.abs(np.exp(1j * hd2).mean(0)), 1e-12, 1)))) / 2
    thr = np.array([r['th_own'] for r in reps]); pr['th_own_jump'] = (np.abs(thr - base['th_own'][None, :]) > 10).mean(0)
    thr_t = np.array([r['th_typ'] for r in reps]); pr['th_typ_jump'] = (np.abs(thr_t - base['th_typ'][None, :]) > 10).mean(0)

    # ---------- per-arm pooled
    arm_rows = {}
    for k in ARMS + POOLS:
        row = {}
        for s in ('S1', 'S2') + (('LV',) if k in ARMS else ()):
            row[f'{s} pairs'] = (float(base[f'{s}|{k}'].mean()), float(np.nanstd([r[f'{s}|{k}'].mean() for r in reps])))
            row[f'{s} emitters'] = (float(base[f'E|{s}|{k}'].mean()), float(np.nanstd([r[f'E|{s}|{k}'].mean() for r in reps])))
        arm_rows[k] = row
    def rkey(k):
        return float(rbase[k]), float(np.nanstd([b[k] for b in rreps]))
    for k in CORE:
        arm_rows[k]['S1 all bits (reader)'] = rkey(f'{k}: minus each-stretch-own-ruler book'); arm_rows[k]['S2 all bits (reader)'] = rkey(f'{k}: minus one-clock book')
        arm_rows[k]['LV all bits (reader)'] = rkey(f'{k}: level')
    arm_rows['WA']['S1 emitters (reader)'] = rkey('emitters started OFF, minus own-ruler book (both hand arms)')
    arm_rows['WB']['S1 emitters (reader)'] = rkey('emitters started ON, minus own-ruler book (both hand arms)')
    s3pool = {}
    for s3 in S3V:
        s3pool[f'{s3} mean'] = (float(base[s3].mean()), float(np.nanstd([r[s3].mean() for r in reps])))
        s3pool[f'{s3} median'] = (float(np.median(base[s3])), float(np.nanstd([np.median(r[s3]) for r in reps])))
    s3pool['tW mean (us per LAID ON stretch)'] = (float(tW(base['ahd5']).mean()), float(np.nanstd([tW(r['ahd5']).mean() for r in reps])))
    s3pool['tW median (us per LAID ON stretch)'] = (float(np.median(tW(base['ahd5']))), float(np.nanstd([np.median(tW(r['ahd5'])) for r in reps])))
    s3pool['length |va| mean'] = (float(base['len_a'].mean()), float(np.nanstd([r['len_a'].mean() for r in reps])))
    s3pool['length |vb| mean'] = (float(base['len_b'].mean()), float(np.nanstd([r['len_b'].mean() for r in reps])))
    s3pool['leftover mean (deg)'] = (float(base['leftover'].mean()), float(np.nanstd([r['leftover'].mean() for r in reps])))
    s3pool['tW minus LAID, mean (us per LAID ON stretch)'] = (float(tW(base['ahd5']).mean() - on30), float(np.nanstd([tW(r['ahd5']).mean() for r in reps])))
    s3pool['pairs where |hd|/5 sits within one width of zero'] = int((base['ahd5'] < W('ahd5')).sum())
    s3pool['reader line: coupling median (its witness set redrawn per resample)'] = rkey('coupling read by the witness (deg per 30-us ON stretch, median)')
    s3pool['pairs with |theta_own| on the grid edge'] = int((base['ath_own'] >= EDGE_DEG).sum())
    s3pool['pairs with |theta_typ| on the grid edge'] = int((base['ath_typ'] >= EDGE_DEG).sum())
    s3pool['pairs with theta_own, theta_typ more than 10 deg apart'] = int((np.abs(base['th_own'] - base['th_typ']) > 10).sum())
    s3pool['pairs with theta_own < 0'] = int((base['th_own'] < 0).sum()); s3pool['pairs with half-difference < 0'] = int((base['hd'] < 0).sum())
    s3pool['median fraction of resamples where theta_own jumps > 10 deg'] = float(np.median(pr['th_own_jump']))
    s3pool['pairs where theta_own jumps > 10 deg in more than a third of resamples'] = int((pr['th_own_jump'] > 1 / 3).sum())
    # the reader's own model, chip-typical fading, at the ensemble coupling: what half-difference it books (OWN fading inside, WITNESS degrees out)
    th_r = math.radians(theta_ens); q_t = base['typ']
    vo = sum(RD.witness_split(q_t, 'OFF', th=th_r))[0]; vn = sum(RD.witness_split(q_t, 'ON', th=th_r))[0]
    s3pool['model half-difference, chip-typical fading, ensemble coupling (deg over 5 ON stretches)'] = float(math.degrees(np.angle(vn * np.conj(vo)) / 2))
    s3pool['chip-typical R30 survival (OWN)'] = q_t

    # ---------- correlations
    cb = corr_set(base, E, eidx); cr = [corr_set(r, E, eidx) for r in reps]
    corr = {k: (cb[k], float(np.nanstd([c[k] for c in cr]))) for k in cb}
    rng_e = np.random.default_rng(20261003)
    ce = [corr_set(base, E, eidx, rng_e.integers(0, len(E), len(E))) for _ in range(a.nbe)]     # second width: emitters redrawn, full-data seats
    ewid = {k: float(np.nanstd([c[k] for c in ce])) for k in cb}
    # thirds of the shots (shot order): each seat against itself (seats 1-2 over the 35 emitters, seat 3 over the 75 pairs)
    third_r = {}; third_noise = {}
    EKEYS = ('LV|A30_30', 'S1|pool', 'S2|pool', 'S1|A30_30', 'S1|A30_10', 'S1|B30_30', 'S1|WA', 'S1|WB'); PKEYS = ('ahd5', 'ath_own', 'hd5')
    for key in EKEYS + PKEYS:
        k_ = ('E|' + key) if key in EKEYS else key
        third_r[key] = [pear(thirds[i][k_], thirds[j][k_]) for i, j in ((0, 1), (0, 2), (1, 2))]
        # noise of one 216-shot reading, from the differences between shot-order thirds: var(t_i - t_j) / 2 is one 72-shot reading's noise; / 3 -> 216 shots
        third_noise[key] = float(math.sqrt(np.mean([np.var(thirds[i][k_] - thirds[j][k_], ddof=1) / 2 for i, j in ((0, 1), (0, 2), (1, 2))]) / 3))
    for key in ('ahd5~S1|pool', 'ahd5~S2|pool', 'ath_own~S1|pool', 'ath_own~S2|pool'):
        lhs, rhs = key.split('~'); third_r['within-third r ' + key] = [pear(t[lhs], t[rhs]) for t in thirds]
    # spread across pairs against the shot width (how much of the across-pair spread stands above shot noise)
    # seat 3 is an angle of a short vector: does its width scale like 1/sqrt(shots)? bootstrap |hd|/5 inside the first shot-order third (72 shots)
    wl = np.array([p[0] for p in pairs])
    def ahd5_only(A_):
        al_, _, _ = RD.frame(A_); lv_ = {k: al_(A_[k]).mean(0) for k in ('WA|X', 'WA|Y', 'WB|X', 'WB|Y')}
        va_ = (2 * lv_['WA|X'] - 1) + 1j * (1 - 2 * lv_['WA|Y']); vb_ = (2 * lv_['WB|X'] - 1) + 1j * (1 - 2 * lv_['WB|Y'])
        return np.abs(np.degrees(np.angle(vb_[wl] * np.conj(va_[wl])) / 2)) / 5.0
    rng72 = np.random.default_rng(20261005); A72 = {k: v[:n // 3] for k, v in A.items()}
    w72 = np.array([ahd5_only({k: v[rng72.integers(0, v.shape[0], v.shape[0])] for k, v in A72.items()}) for _ in range(a.nb)]).std(0)
    w216 = W('ahd5'); hl = (base['len_a'] + base['len_b']) / 2; sat = {'all': (float(np.sqrt((w216 ** 2).mean())), float(np.sqrt((w72 ** 2).mean())), len(pairs))}
    for lo, hi in ((0.0, 0.12), (0.12, 0.20), (0.20, 9.0)):
        s = (hl >= lo) & (hl < hi); sat[f'{lo:.2f}-{hi:.2f}'] = (float(np.sqrt((w216[s] ** 2).mean())), float(np.sqrt((w72[s] ** 2).mean())), int(s.sum()))
    spread = {}
    for key in EKEYS + PKEYS:
        if key in EKEYS:
            v = base['E|' + key]; wv = np.nanstd(np.array([r['E|' + key] for r in reps]), axis=0)
        else:
            v = base[key]; wv = W(key)
        spread[key] = {'sd_across': float(np.std(v, ddof=1)), 'rms_shot_width': float(np.sqrt(np.mean(wv ** 2))), 'thirds_noise': third_noise[key], 'n': int(len(v))}

    # seat 3 within one emitter (its witnesses read the same shots of the same emitter) against seat 3 between emitters
    multi = [e_ for e_ in E if len(eidx[e_]) >= 2]; idxm = np.concatenate([eidx[e_] for e_ in multi])
    def wb(P_):
        return (float(np.sqrt(np.mean([np.var(P_['ahd5'][eidx[e_]], ddof=1) for e_ in multi]))),
                float(np.std([P_['ahd5'][eidx[e_]].mean() for e_ in multi], ddof=1)))
    wb0 = wb(base); wbr = np.array([wb(r) for r in reps])
    within_between = {'emitters': len(multi), 'pairs': int(len(idxm)), 'within_sd': (wb0[0], float(np.nanstd(wbr[:, 0]))),
                      'between_sd_of_emitter_means': (wb0[1], float(np.nanstd(wbr[:, 1]))), 'rms_shot_width': float(np.sqrt((W('ahd5')[idxm] ** 2).mean())),
                      'witnesses_per_emitter': {int(e_): int(len(eidx[e_])) for e_ in multi}}
    # ---------- fingerprints
    fb = fingerprints(base, E, eidx); fr = [fingerprints(r, E, eidx) for r in reps]
    fpw = {k: np.nanstd(np.array([f[k] for f in fr]), axis=0) for k in fb}
    shot_rms = {s: np.sqrt(np.mean(np.array([W(f'{s}|{k}') for k in ARMS]) ** 2, axis=0)) for s in ('S1', 'S2')}
    # the spread across arms that shot noise alone draws: SD across the twelve arms of (resample minus full data), RMS over resamples. The arms share
    # their rulers (R10/R30/R90/R300), so their noise moves together; this keeps that, which the RMS of per-arm widths (shot_rms) does not.
    noise_spread = {}
    for s in ('S1', 'S2'):
        Mb = np.array([base[f'{s}|{k}'] for k in ARMS])
        v = np.array([np.var(np.array([r[f'{s}|{k}'] for k in ARMS]) - Mb, axis=0, ddof=1) for r in reps])
        noise_spread[s] = np.sqrt(v.mean(0))

    # ---------- chip map
    mb = comove(base); mr = [comove(r) for r in reps]; mw = {k: np.nanstd(np.array([x[k] for x in mr]), axis=0) for k in mb}
    regions = {}
    for i, (w, e) in enumerate(pairs):
        regions.setdefault(region_of(xy[e]), []).append(i)
    reg_rows = []
    for ry in ('top (q0-55)', 'middle (q56-99)', 'bottom (q100-155)'):
        for rx in ('left (cols 0-4)', 'centre (cols 5-10)', 'right (cols 11-15)'):
            idx = np.array(regions.get((ry, rx), []), int)
            if len(idx) == 0: reg_rows.append((ry, rx, 0, 0, None, None, None, None, [], {})); continue
            c1 = float(mb['c1'][idx].mean()); c1w = float(np.nanstd([x['c1'][idx].mean() for x in mr]))
            c2 = float(mb['c2'][idx].mean()); c2w = float(np.nanstd([x['c2'][idx].mean() for x in mr]))
            raw = {k: (float(base[k][idx].mean()), float(np.nanstd([r[k][idx].mean() for r in reps]))) for k in ('ahd5', 'S1|pool', 'S2|pool')}
            reg_rows.append((ry, rx, len(idx), len(set(pairs[j][1] for j in idx)), c1, c1w, c2, c2w, sorted(set(pairs[j][1] for j in idx)), raw))
    order = np.argsort(mb['c1']); terc = np.empty(len(pairs), object)
    nth = len(pairs) // 3
    for j, i in enumerate(order): terc[i] = '-' if j < nth else ('o' if j < len(pairs) - nth else '+')
    order2 = np.argsort(mb['c2']); terc2 = np.empty(len(pairs), object)
    for j, i in enumerate(order2): terc2[i] = '-' if j < nth else ('o' if j < len(pairs) - nth else '+')

    def chip_map(tc):
        sym = {q: '.' for q in range(156)}
        for q in range(156):
            if not g[q]: sym[q] = 'x'
        for w, e in dropped:
            if g[w]: sym[w] = 'w'
        for e in roles['emitters']: sym[e] = 'E' if e in E else 'x'
        for i, (w, e) in enumerate(pairs): sym[w] = tc[i]
        lines = ['             col ' + ' '.join(f'{x:x}' for x in range(16))]
        for y in range(15):
            row = [' '] * 16
            for q, (yy, xx) in xy.items():
                if yy == y: row[xx] = sym[q]
            lab = f'q{10 * y:>3}-{10 * y + 15:<3}' if y % 2 == 0 else f' bridges {10 * (y - 1) + 16}-{10 * (y - 1) + 19}'
            lines.append(f'{lab:<20} ' + ' '.join(row))
        return '\n'.join(lines)
    map1 = chip_map(terc); map2 = chip_map(terc2)

    integ1 = integrity()
    changed = [(r0[0], r0[1], r1[1]) for r0, r1 in zip(integ0, integ1) if r0[1] != r1[1]]
    pyc = [p for p in os.listdir(os.path.join(FROZEN, 'code')) if 'pycache' in p]

    # ---------- JSON
    def J(x):
        if isinstance(x, dict): return {str(k): J(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)): return [J(v) for v in x]
        if isinstance(x, np.ndarray): return J(x.tolist())
        if isinstance(x, (np.floating, float)): return None if not np.isfinite(x) else float(x)
        if isinstance(x, (np.integer,)): return int(x)
        return x
    perpair = []
    for i, (w, e) in enumerate(pairs):
        rec = {'witness': w, 'emitter': e, 'emitter_grid_yx': xy[e], 'witness_grid_yx': xy[w], 'region': region_of(xy[e])}
        for k in keys: rec[k] = [base[k][i], pr[k][1][i]]
        rec['hd_circ_width'] = pr['hd_circ_width'][i]; rec['th_own_jump_fraction'] = pr['th_own_jump'][i]; rec['th_typ_jump_fraction'] = pr['th_typ_jump'][i]
        rec['tW_us_per_LAID_ON_stretch'] = [float(tW(base['ahd5'][i])), float(tW(pr['ahd5'][1][i]))]
        for k in fb:
            if not k.endswith('chip_pattern'): rec['fingerprint ' + k] = [fb[k][i], fpw[k][i]]
        rec['fingerprint S1 rms of per-arm shot widths'] = shot_rms['S1'][i]; rec['fingerprint S2 rms of per-arm shot widths'] = shot_rms['S2'][i]
        rec['fingerprint S1 noise-only spread'] = noise_spread['S1'][i]; rec['fingerprint S2 noise-only spread'] = noise_spread['S2'][i]
        rec['comove c1 (S3 x S1 pooled)'] = [mb['c1'][i], mw['c1'][i]]; rec['comove c2 (S3 x S2 pooled)'] = [mb['c2'][i], mw['c2'][i]]
        perpair.append(rec)
    out = {'what': 'three seats on one event, run 121 ibm_pittsburgh', 'made': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
           'script_sha256': sha(os.path.abspath(__file__)), 'nb': a.nb, 'nbe': a.nbe, 'theta_ens_deg': theta_ens, 'laid_30us_stretch_us': on30,
           'shots': int(A['F0'].shape[0]), 'job_id': m.get('job_id'), 'job_running_at': m.get('job_running_at'),
           'laid': LAID, 'pairs': pairs, 'emitters': E, 'dropped_pairs': dropped, 'unreadable_bits': [int(q) for q in np.where(~g)[0]],
           'per_pair': perpair, 'per_arm': arm_rows, 'seat3_pooled': s3pool, 'corr': corr, 'corr_emitter_width': ewid, 'thirds': third_r, 'spread': spread,
           'seat3_width_216_vs_72_shots_by_hand_length': sat, 'seat3_within_vs_between_emitters': within_between,
           'chip_pattern': {k: fb[k] for k in fb if k.endswith('chip_pattern')}, 'regions': reg_rows, 'reproduce': repro,
           'integrity_before': integ0, 'integrity_after': integ1, 'changed_during_run': changed, 'pycache_in_frozen_code': pyc}
    json.dump(J(out), open(OUT_JSON, 'w'), indent=1)
    print('wrote', OUT_JSON, flush=True)
    if a.no_md: return
    write_md(out, base, pr, pairs, E, eidx, xy, LAID, arm_rows, s3pool, corr, ewid, third_r, spread, fb, fpw, noise_spread, mb, mw, reg_rows, map1, map2, repro,
             integ0, integ1, changed, pyc, theta_ens, on30, tW, dropped, g, a, sat)


def f4(v, w=None, nd=4):
    if v is None or (isinstance(v, float) and not np.isfinite(v)): return 'nan'
    return f'{v:+.{nd}f}' + (f' ({w:.{nd}f})' if w is not None else '')


def dag(v, w):                                       # dagger: the reading sits within one width of zero (too thin to read)
    return '†' if (w is not None and np.isfinite(v) and np.isfinite(w) and abs(v) < w) else ''


def write_md(out, base, pr, pairs, E, eidx, xy, LAID, arm_rows, s3pool, corr, ewid, third_r, spread, fb, fpw, noise_spread, mb, mw, reg_rows, map1, map2, repro,
             integ0, integ1, changed, pyc, theta_ens, on30, tW, dropped, g, a, sat):
    L = []; P = L.append
    P(f'# THREE SEATS ON ONE EVENT -- run 121, ibm_pittsburgh (the no-name shot)')
    P('')
    P(f'script: `internal/three_seats_run121.py`  sha256 `{out["script_sha256"]}`  ')
    P(f'made {out["made"]} by Bones, internal. Read-only on the data, the frozen code and the ledger. Nothing was submitted anywhere.  ')
    P(f'numbers in full: `internal/three_seats_run121_20261003.json`. Reader copy used: `internal/readnoname_copy_20261003.py` (byte-identical to the frozen reader).')
    P('')
    P('**Clocks (The Stake).** LAID = our laid times on the maker\'s tick (realized stretches 9.984 / 30.016 / 89.984 us). '
      'WITNESS = the frame-held spectator\'s phase, in degrees. OWN = the emitter\'s own end level and its own fading rulers (R10/R30/R90/R300, same job). '
      'Every width is over shots (the reader\'s bootstrap, NB = 100) unless it says otherwise. A † marks a reading within one width of zero: too thin to read.')
    P('')
    # ---------------- method
    P('## Method')
    P('')
    P(f'- **Data.** `run121_results.npz` (21 circuits x {out["shots"]} shots x 156 bits, kerneled IQ points), sha256 matches `run121_meta.json` results_sha256. '
      f'Roles from `reads/noname_roles.json` (Pittsburgh static wiring at fire; 39 emitters, 86 witnesses). Readable bits as the reader takes them '
      f'(cloud separation > 4 widths): {len(out["unreadable_bits"])} unreadable ({", ".join(map(str, out["unreadable_bits"]))}), leaving '
      f'**{len(pairs)} witness-emitter pairs on {len(E)} emitters** (the reader\'s 75 / 35). Dropped pairs: {", ".join(f"{w}-{e}" for w, e in dropped)}.')
    P('- **Level.** `readnoname.frame()`: every shot\'s IQ point projected on the line from the OFF cloud (F0) to the ON cloud (F1); a bit\'s level = mean over shots '
      '(0 = OFF cloud, 1 = ON cloud). Same function, same rule.')
    P('- **SEAT 1 (OWN, short clock)** = emitter end level minus `readnoname.book(start, [R_L per stretch], flip)`, where R_L is the same bit\'s ON-left-alone level '
      'at that stretch length (R10 / R30 / R90, clipped 0.02-1.2): the reader\'s "minus each-stretch-own-ruler book", per bit.')
    P('- **SEAT 2 (OWN, long clock)** = emitter end level minus `book(start, [R300^(L/300) per stretch], flip)` (R300 clipped 0.02-0.98): the reader\'s "minus one-clock book", per bit.')
    P('- **Arms where seats 1-2 are read (12).** The ten core arms (every bit pushed alike) and the two witness arms, where the emitter gets the same train as '
      'A30_30 (WA, started OFF) or B30_30 (WB, started ON) while its witnesses hold frame; there its level is the mean of the X-hand and Y-hand circuits and its '
      'own book uses R30 (clipped 0.02-0.999) for all ten stretches, exactly as the reader\'s witness section does. "pool" = equal-weight mean of a pair\'s twelve arms; '
      '"core" = mean of the ten core arms.')
    P('- **Arm names (from `noname.py`).** `A{off}_{on}`: start OFF; the FIRST stretch is OFF; stretches alternate OFF {off} us, ON {on} us, five of each, ten pushes '
      '(a push after every stretch), ends OFF. So **A30_10 = OFF stretches 30 us, ON stretches 10 us**. `f` = one more push at once at the end (ends flipped). '
      '`B30_30`: start ON, first stretch ON. N2 / N6: OFF start, 2 / 6 pushes, 30-us stretches. WA / WB: the witness arms (emitter as A30_30 / B30_30).')
    P(f'- **SEAT 3 (WITNESS).** Only the witness arms carry a witness reading: in every core arm the witness bits are pushed like everyone else and read on Z, '
      f'so they carry no phase. The witness vector per start is v = (2 level_X - 1) + i (1 - 2 level_Y) from its two hand circuits (the reader\'s va, vb). '
      f'Primary reading: the reader\'s half-difference, hd = angle(vb conj va) / 2, the part that flips with the emitter\'s start; it carries coupling x the '
      f'emitter\'s signed ON time over the **5 LAID ON stretches** of each start, so **seat 3 = |hd| / 5, WITNESS degrees per LAID ON stretch**. It uses no '
      f'emitter ruler, so it shares no OWN number with seats 1-2. Second reading: the reader\'s `fit_witness` coupling theta (deg per 30-us ON stretch) with the '
      f'emitter\'s own R30 fading inside the model (OWN inside, WITNESS out), and the same fit with the chip-typical R30 ({s3pool["chip-typical R30 survival (OWN)"]:.4f}). '
      f'hd lives in (-90, +90] deg, so |hd| / 5 has a ceiling at 18 deg per stretch (a reading past it folds back).')
    P(f'- **Equivalent time.** t_W = {on30:.3f} us x (|hd|/5) / {theta_ens:.4f} deg: the ON time per LAID {on30:.3f}-us ON stretch the witness reads if every pair '
      f'had the reader\'s ensemble coupling (median |theta|, own fading). One constant for all pairs, so per pair t_W is seat 3 on another scale; '
      f'per-pair coupling and per-pair ON time are not separated by this job (one stretch pattern in the witness arms).')
    P(f'- **Widths.** Shot bootstrap exactly as `readnoname.py` (seed 20261004, NB = {a.nb}, each of the 21 circuits resampled on its own, the pair list held '
      f'fixed from the full data). Because the draws are the reader\'s own, the reader\'s run-121 read was rebuilt from the same resamples: '
      f'**{sum(r[5] for r in repro)} of {len(repro)} lines of `reads/noname_read1.txt` reproduced exactly** (value and width, 4 decimals). '
      f'Correlations carry a second, labelled width over emitters (35 drawn with replacement, their witnesses with them, {a.nbe} draws, seed 20261003), because '
      f'pairs on one emitter share seats 1-2. Shot-order thirds (72 shots each) give each seat\'s agreement with itself.')
    P(f'- **Co-movement.** Pearson r across the {len(pairs)} pairs (each pair once; an emitter with three witnesses counts three times), per arm and pooled; '
      f'also Spearman and the 35-emitter version (seat 3 averaged over an emitter\'s witnesses) for the pooled seats.')
    ok_before = all(r[3] for r in integ0 if r[3] is not None); ok_after = not changed
    P(f'- **Integrity.** Frozen code/reads checked against `for_indahl_ai/data/SHA256SUMS.txt` and the data against the meta before the read: '
      f'{"all match" if ok_before else "MISMATCH"}; re-hashed after: {"unchanged" if ok_after else "CHANGED " + str(changed)}; '
      f'__pycache__ in the frozen code dir: {"none" if not pyc else pyc}.')
    P('')
    # ---------------- per-arm table
    P('## Per arm: the pooled seats')
    P('')
    P(f'Means over the {len(pairs)} pairs (each pair\'s emitter, so an emitter counts once per witness), width over shots. "150 bits" = the reader\'s own all-readable-bit '
      f'number for the same arm (seat 1 for WA/WB is the reader\'s 35-emitter line). Seat 3 exists only where a witness held frame.')
    P('')
    P('| arm | what the emitter got (LAID) | LAID ON / total us | end level (OWN), pairs | SEAT 1 OWN short, pairs | SEAT 2 OWN long, pairs | SEAT 1 / SEAT 2, 150 bits (reader) | SEAT 3 WITNESS, deg per LAID ON stretch |')
    P('|---|---|---|---|---|---|---|---|')
    for k in ARMS:
        d = LAID[k]; st = d['stretches_us']
        off_l, on_l = (st[0], st[1]) if d['start'] == 'OFF' else (st[1], st[0])
        what = (f"start {d['start']}, OFF {off_l} us / ON {on_l} us stretches, {len(st)} pushes" + (" + 1 at once" if d['flip'] else '') + f", ends {d['end']}")
        r = arm_rows[k]
        if k in CORE:
            allb = f"{f4(*r['S1 all bits (reader)'])} / {f4(*r['S2 all bits (reader)'])}"
        else:
            allb = f"{f4(*r['S1 emitters (reader)'])} / --"
        s3 = '--' if k in CORE else f"{s3pool['ahd5 mean'][0]:.2f} ({s3pool['ahd5 mean'][1]:.2f}), one reading for WA and WB together"
        P(f"| {k} | {what} | {d['on_us']:.2f} / {d['total_us']:.2f} | {f4(*r['LV pairs'])} | {f4(*r['S1 pairs'])}{dag(*r['S1 pairs'])} | "
          f"{f4(*r['S2 pairs'])}{dag(*r['S2 pairs'])} | {allb} | {s3} |")
    for k in POOLS:
        r = arm_rows[k]
        P(f"| {k} | {'all twelve arms, equal weight' if k == 'pool' else 'the ten core arms'} | -- | -- | {f4(*r['S1 pairs'])}{dag(*r['S1 pairs'])} | {f4(*r['S2 pairs'])}{dag(*r['S2 pairs'])} | -- | -- |")
    P('')
    P('Same rows over the 35 emitters (each once): ' + '; '.join(f"{k} {f4(*arm_rows[k]['S1 emitters'])} / {f4(*arm_rows[k]['S2 emitters'])}" for k in ARMS + POOLS) + ' (seat 1 / seat 2, OWN).')
    P('')
    P('**Seat 3 pooled (WITNESS):**')
    P('')
    P('| reading | value (width over shots) |')
    P('|---|---|')
    P(f"| |hd|/5, mean over 75 pairs, WITNESS deg per LAID ON stretch | {s3pool['ahd5 mean'][0]:.3f} ({s3pool['ahd5 mean'][1]:.3f}) |")
    P(f"| |hd|/5, median over pairs | {s3pool['ahd5 median'][0]:.3f} ({s3pool['ahd5 median'][1]:.3f}) |")
    P(f"| signed hd/5, mean over pairs (the reader's half-difference line / 5) | {s3pool['hd5 mean'][0]:+.3f} ({s3pool['hd5 mean'][1]:.3f}) |")
    P(f"| pairs with hd < 0 | {s3pool['pairs with half-difference < 0']} of {len(pairs)} |")
    P(f"| pairs where |hd|/5 sits within one width of zero (too thin to read one by one) | {s3pool['pairs where |hd|/5 sits within one width of zero']} of {len(pairs)} |")
    rl = s3pool['reader line: coupling median (its witness set redrawn per resample)']
    P(f"| |fitted coupling|, own fading, median, pair set held fixed (the reader's line, its witness set redrawn per resample: {rl[0]:+.4f} ({rl[1]:.4f})) | {s3pool['ath_own median'][0]:.3f} ({s3pool['ath_own median'][1]:.3f}) |")
    P(f"| |fitted coupling|, own fading, mean | {s3pool['ath_own mean'][0]:.3f} ({s3pool['ath_own mean'][1]:.3f}) |")
    P(f"| |fitted coupling|, chip-typical fading, median | {s3pool['ath_typ median'][0]:.3f} ({s3pool['ath_typ median'][1]:.3f}) |")
    P(f"| fitted coupling < 0 (own fading) | {s3pool['pairs with theta_own < 0']} of {len(pairs)} |")
    P(f"| fit on the grid edge (|theta| >= {EDGE_DEG:.0f} deg), own / typical fading | {s3pool['pairs with |theta_own| on the grid edge']} / {s3pool['pairs with |theta_typ| on the grid edge']} pairs |")
    P(f"| own-fading and typical-fading fits more than 10 deg apart | {s3pool['pairs with theta_own, theta_typ more than 10 deg apart']} pairs |")
    P(f"| own-fading fit jumps > 10 deg from its full-data value in > 1/3 of shot resamples | {s3pool['pairs where theta_own jumps > 10 deg in more than a third of resamples']} pairs (median jump fraction {s3pool['median fraction of resamples where theta_own jumps > 10 deg']:.2f}) |")
    P(f"| t_W, WITNESS-equivalent ON time per LAID {on30:.3f}-us ON stretch, mean / median | {s3pool['tW mean (us per LAID ON stretch)'][0]:.2f} ({s3pool['tW mean (us per LAID ON stretch)'][1]:.2f}) / {s3pool['tW median (us per LAID ON stretch)'][0]:.2f} ({s3pool['tW median (us per LAID ON stretch)'][1]:.2f}) us |")
    P(f"| t_W minus the LAID {on30:.3f} us, mean (WITNESS minus LAID, per ON stretch) | {s3pool['tW minus LAID, mean (us per LAID ON stretch)'][0]:+.2f} ({s3pool['tW minus LAID, mean (us per LAID ON stretch)'][1]:.2f}) us |")
    P(f"| the reader's own model, chip-typical OWN fading, at the {theta_ens:.2f}-deg coupling: half-difference it books over 5 LAID ON stretches | {s3pool['model half-difference, chip-typical fading, ensemble coupling (deg over 5 ON stretches)']:.2f} deg ({s3pool['model half-difference, chip-typical fading, ensemble coupling (deg over 5 ON stretches)'] / 5:.2f} per stretch; LAID-only, no fading: {5 * theta_ens:.2f}) |")
    P(f"| witness hand length, started OFF / ON (mean) | {s3pool['length |va| mean'][0]:.4f} ({s3pool['length |va| mean'][1]:.4f}) / {s3pool['length |vb| mean'][0]:.4f} ({s3pool['length |vb| mean'][1]:.4f}) |")
    P(f"| witness half-sum, its own leftover (mean, deg) | {s3pool['leftover mean (deg)'][0]:+.3f} ({s3pool['leftover mean (deg)'][1]:.3f}) |")
    P('')
    # ---------------- co-movement
    P('## Across pairs: how seat 3 moves with seats 1 and 2')
    P('')
    P(f'Pearson r across the {len(pairs)} pairs. First width over shots (the reader\'s resamples), second [in brackets] over emitters. Seat 3 here = |hd|/5 (WITNESS). '
      'Seat 3 is one reading per pair; each row pairs it with that arm\'s seats 1-2 (OWN). Last column: seat 1 against seat 2 in the same arm (they share the end level).')
    P('')
    P('| arm | r(seat 3, seat 1) | r(seat 3, seat 2) | r(seat 1, seat 2) |')
    P('|---|---|---|---|')
    for arm in ARMS + POOLS:
        k1 = f'ahd5~S1|{arm}'; k2 = f'ahd5~S2|{arm}'; k3 = f'S1~S2|{arm}'
        P(f"| {arm} | {corr[k1][0]:+.3f} ({corr[k1][1]:.3f}) [{ewid[k1]:.3f}]{dag(corr[k1][0], corr[k1][1])} | {corr[k2][0]:+.3f} ({corr[k2][1]:.3f}) [{ewid[k2]:.3f}]{dag(corr[k2][0], corr[k2][1])} | {corr[k3][0]:+.3f} ({corr[k3][1]:.3f}) [{ewid[k3]:.3f}] |")
    P('')
    P('Same table with seat 3 = the reader\'s fitted |coupling|, own fading (OWN R30 inside the fit):')
    P('')
    P('| arm | r(|theta own|, seat 1) | r(|theta own|, seat 2) |')
    P('|---|---|---|')
    for arm in ARMS + POOLS:
        k1 = f'ath_own~S1|{arm}'; k2 = f'ath_own~S2|{arm}'
        P(f"| {arm} | {corr[k1][0]:+.3f} ({corr[k1][1]:.3f}) [{ewid[k1]:.3f}]{dag(corr[k1][0], corr[k1][1])} | {corr[k2][0]:+.3f} ({corr[k2][1]:.3f}) [{ewid[k2]:.3f}]{dag(corr[k2][0], corr[k2][1])} |")
    P('')
    P('Pooled seats 1-2 against every seat-3 reading (Pearson over pairs; Spearman over pairs; Pearson over the 35 emitters):')
    P('')
    P('| seat 3 reading (WITNESS) | r(.., seat 1 pool) | r(.., seat 2 pool) | Spearman seat 1 / seat 2 | 35 emitters seat 1 / seat 2 |')
    P('|---|---|---|---|---|')
    for s3 in S3V:
        a1 = corr[f'{s3}~S1|pool']; a2 = corr[f'{s3}~S2|pool']; sp1 = corr[f'{s3}~S1|pool@spearman']; sp2 = corr[f'{s3}~S2|pool@spearman']
        e1 = corr[f'{s3}~S1|pool@emitters']; e2 = corr[f'{s3}~S2|pool@emitters']
        P(f"| {S3NAME[s3]} | {a1[0]:+.3f} ({a1[1]:.3f}) [{ewid[f'{s3}~S1|pool']:.3f}]{dag(*a1)} | {a2[0]:+.3f} ({a2[1]:.3f}) [{ewid[f'{s3}~S2|pool']:.3f}]{dag(*a2)} | "
          f"{sp1[0]:+.3f} ({sp1[1]:.3f}) / {sp2[0]:+.3f} ({sp2[1]:.3f}) | {e1[0]:+.3f} ({e1[1]:.3f}) [{ewid[f'{s3}~S1|pool@emitters']:.3f}] / {e2[0]:+.3f} ({e2[1]:.3f}) [{ewid[f'{s3}~S2|pool@emitters']:.3f}] |")
    P('')
    short = {'ahd5': '|hd|/5', 'ath_own': '|theta own|', 'hd5': 'signed hd/5', 'ath_typ': '|theta typ|'}
    def nice(k):
        s3, rest = k.split('~'); seat, arm = rest.split('|')
        arm = arm.replace('@spearman', ' (Spearman)').replace('@emitters', ' (35 emitters)')
        return f"{short[s3]} with seat {seat[1]}, {arm}"
    cand = sorted([(k, v) for k, v in corr.items() if '~' in k and k.split('~')[0] in S3V and k.split('~')[1][:2] in ('S1', 'S2')], key=lambda kv: -abs(kv[1][0]))
    ws = [v[1] for _, v in cand]
    P(f"**Largest |r| between a seat-3 reading and seat 1 or 2**, over every row of the three tables above ({len(cand)} correlations computed in all; their shot widths run "
      f"{min(ws):.3f}-{max(ws):.3f}): " + '; '.join(f"{nice(k)}: {v[0]:+.3f} ({v[1]:.3f}) [{ewid[k]:.3f}]" for k, v in cand[:6]) + '.')
    P('')
    P('**How much of each seat stands above its own shot noise.** SD across emitters (seats 1-2, the end level) or pairs (seat 3), against the noise of one reading two ways: '
      'the RMS of the shot-bootstrap widths, and the noise read from the differences between shot-order thirds (72 shots each, scaled to 216 shots), which uses no '
      'resampling at all. Last column: each seat against itself across the thirds (r for thirds 1-2, 1-3, 2-3).')
    P('')
    P('| seat | SD across | RMS shot width (bootstrap) | noise from thirds | r across thirds |')
    P('|---|---|---|---|---|')
    lab = {'LV|A30_30': 'end level A30_30 (OWN), 35 emitters, for reference', 'S1|pool': 'seat 1 pool (OWN), 35 emitters', 'S2|pool': 'seat 2 pool (OWN), 35 emitters',
           'S1|A30_30': 'seat 1 A30_30 (OWN), 35 emitters', 'S1|A30_10': 'seat 1 A30_10 (OWN), 35 emitters', 'S1|B30_30': 'seat 1 B30_30 (OWN), 35 emitters',
           'S1|WA': 'seat 1 WA (OWN), 35 emitters', 'S1|WB': 'seat 1 WB (OWN), 35 emitters', 'ahd5': 'seat 3 |hd|/5 (WITNESS deg), 75 pairs',
           'ath_own': 'seat 3 |theta own| (WITNESS deg), 75 pairs', 'hd5': 'seat 3 signed hd/5 (WITNESS deg), 75 pairs'}
    for k, v in spread.items():
        th = third_r.get(k)
        P(f"| {lab[k]} | {v['sd_across']:.4f} | {v['rms_shot_width']:.4f} | {v['thirds_noise']:.4f} | {', '.join(f'{x:+.2f}' for x in th) if th else '--'} |")
    P('')
    P(f"The thirds' scaling (noise of one 72-shot reading / 3 in variance) holds for seats 1-2 (sums of levels) and runs low for seat 3, an angle of a short vector "
      f"that saturates: the shot-bootstrap RMS width of |hd|/5 is {sat['all'][0]:.2f} deg at 216 shots and {sat['all'][1]:.2f} at 72 shots (ratio "
      f"{sat['all'][1] / sat['all'][0]:.2f}; 1/sqrt(shots) would give 1.73). By the witness hand length (mean of |va|, |vb|): " + '; '.join(
          f"{k} ({v[2]} pairs) {v[0]:.2f} at 216 / {v[1]:.2f} at 72" for k, v in sat.items() if k != 'all') +
      ". A reading spread evenly over 0-18 deg has SD 5.20. So for seat 3 the bootstrap width is the one used throughout.")
    P('')
    wbx = out['seat3_within_vs_between_emitters']
    P(f"Seat 3 inside one emitter: {wbx['emitters']} emitters have two or three readable witnesses ({wbx['pairs']} pairs); their witnesses read the same shots of the same "
      f"emitter. Seat 3 (|hd|/5, WITNESS deg per LAID ON stretch) spreads within an emitter by {wbx['within_sd'][0]:.2f} ({wbx['within_sd'][1]:.2f}), and the emitters' "
      f"means spread by {wbx['between_sd_of_emitter_means'][0]:.2f} ({wbx['between_sd_of_emitter_means'][1]:.2f}); one pair's shot width there is {wbx['rms_shot_width']:.2f}.")
    P('')
    P(f"The same push train read twice on each emitter (core arm vs witness arm), across the 35 emitters. End level (OWN, no book): A30_30 against WA r = "
      f"{corr['retest LV A30_30~WA'][0]:+.3f} ({corr['retest LV A30_30~WA'][1]:.3f}) [{ewid['retest LV A30_30~WA']:.3f}]; B30_30 against WB r = "
      f"{corr['retest LV B30_30~WB'][0]:+.3f} ({corr['retest LV B30_30~WB'][1]:.3f}) [{ewid['retest LV B30_30~WB']:.3f}]. "
      f"Seat 1: {corr['retest S1 A30_30~WA'][0]:+.3f} ({corr['retest S1 A30_30~WA'][1]:.3f}) [{ewid['retest S1 A30_30~WA']:.3f}] and "
      f"{corr['retest S1 B30_30~WB'][0]:+.3f} ({corr['retest S1 B30_30~WB'][1]:.3f}) [{ewid['retest S1 B30_30~WB']:.3f}]; "
      f"seat 2: {corr['retest S2 A30_30~WA'][0]:+.3f} ({corr['retest S2 A30_30~WA'][1]:.3f}) and {corr['retest S2 B30_30~WB'][0]:+.3f} ({corr['retest S2 B30_30~WB'][1]:.3f}) "
      f"(both arms' books are built from the same emitter's R30 / R300 shots, so the seat-1 and seat-2 retests carry the ruler's own shot noise twice). "
      f"Seat-3 readings against each other: |hd|/5 with |theta own| r = {corr['ahd5~ath_own'][0]:+.3f} ({corr['ahd5~ath_own'][1]:.3f}); |theta own| with |theta typ| r = {corr['ath_own~ath_typ'][0]:+.3f} ({corr['ath_own~ath_typ'][1]:.3f}); "
      f"|hd|/5 with the witness hand length r = {corr['ahd5~len'][0]:+.3f} ({corr['ahd5~len'][1]:.3f}).")
    P('')
    wl_ = {'ahd5~S1|pool': '|hd|/5 with pooled seat 1', 'ahd5~S2|pool': '|hd|/5 with pooled seat 2', 'ath_own~S1|pool': '|theta own| with pooled seat 1',
           'ath_own~S2|pool': '|theta own| with pooled seat 2'}
    P('Within each shot-order third (72 shots; thirds 1, 2, 3), r(seat 3 WITNESS, pooled seat OWN) over the 75 pairs: ' + '; '.join(
        f"{wl_[k.replace('within-third r ', '')]}: {', '.join(f'{x:+.2f}' for x in v)}" for k, v in third_r.items() if k.startswith('within')) + '.')
    P('')
    # ---------------- fingerprints
    P('## Per pair: fingerprints (top and bottom 10 by pooled seat 1)')
    P('')
    P('Spread = SD of the pair\'s seat across its twelve arms (OWN); "beyond" = the same after taking off the chip\'s own arm-to-arm pattern (the 35-emitter mean per arm); '
      '"noise-only" = the spread across the same twelve arms that shot noise alone draws (SD across arms of resample minus full data, RMS over the 100 resamples; '
      'the arms share their rulers, so their noise partly moves together and this keeps that). Pairs on one emitter share seats 1-2. '
      'Emitter grid place = (row on the doubled grid, column), see the map. "jump frac" = share of shot resamples in which the fitted coupling lands more than 10 deg '
      'from its full-data value.')
    P('')
    P('| # | witness-emitter | emitter at | SEAT 1 pool OWN | SEAT 2 pool OWN | SEAT 3 |hd|/5 WITNESS deg / LAID stretch | theta own WITNESS deg (jump frac) | t_W WITNESS us / LAID 30.016 us | seat-1 spread raw / beyond / noise-only | seat-2 spread raw / beyond / noise-only |')
    P('|---|---|---|---|---|---|---|---|---|---|')
    o = np.argsort(-base['S1|pool'])
    def prow(rank_lab, i):
        w, e = pairs[i]
        return (f"| {rank_lab} | {w}-{e} | {xy[e]} | {f4(base['S1|pool'][i], pr['S1|pool'][1][i])}{dag(base['S1|pool'][i], pr['S1|pool'][1][i])} | "
                f"{f4(base['S2|pool'][i], pr['S2|pool'][1][i])}{dag(base['S2|pool'][i], pr['S2|pool'][1][i])} | {base['ahd5'][i]:.2f} ({pr['ahd5'][1][i]:.2f}){dag(base['ahd5'][i], pr['ahd5'][1][i])} | "
                f"{base['th_own'][i]:+.2f} ({pr['th_own'][1][i]:.2f}) ({pr['th_own_jump'][i]:.2f}) | {float(tW(base['ahd5'][i])):.2f} ({float(tW(pr['ahd5'][1][i])):.2f}) | "
                f"{fb['S1|raw'][i]:.4f} / {fb['S1|beyond'][i]:.4f} / {noise_spread['S1'][i]:.4f} | {fb['S2|raw'][i]:.4f} / {fb['S2|beyond'][i]:.4f} / {noise_spread['S2'][i]:.4f} |")
    for j in range(10): P(prow(f'top {j + 1}', o[j]))
    P('| ... | | | | | | | | | |')
    for j in range(10): P(prow(f'bottom {10 - j}', o[len(o) - 10 + j]))
    P('')
    n1 = int((fb['S1|beyond'] > noise_spread['S1']).sum()); n2 = int((fb['S2|beyond'] > noise_spread['S2']).sum())
    ne1 = len(set(pairs[i][1] for i in range(len(pairs)) if fb['S1|beyond'][i] > noise_spread['S1'][i]))
    P(f"Over all {len(pairs)} pairs: seat-1 spread raw median {np.median(fb['S1|raw']):.4f}, beyond the chip pattern median {np.median(fb['S1|beyond']):.4f}, noise-only median {np.median(noise_spread['S1']):.4f} "
      f"({n1} of {len(pairs)} pairs, on {ne1} of {len(E)} emitters, spread beyond the chip pattern by more than their noise-only spread); "
      f"seat-2 spread raw median {np.median(fb['S2|raw']):.4f}, beyond {np.median(fb['S2|beyond']):.4f}, noise-only {np.median(noise_spread['S2']):.4f} ({n2} of {len(pairs)} pairs above their noise-only spread). "
      f"Chip pattern of seat 1 across the arms (35-emitter means, OWN): " + ', '.join(f'{k} {v:+.4f}' for k, v in zip(ARMS, fb['S1|chip_pattern'])) + '.')
    P('')
    # ---------------- chip map
    P('## Where on the chip the pairs that move together sit')
    P('')
    P('Each pair\'s share of the pooled correlation: c = z(seat 3) x z(pooled seat), z taken across the 75 pairs (the mean of c is r). '
      'Map marks each witness bit by its pair\'s c, in thirds of 25: `+` top third (seat 3 and the seat on the same side of their means: moving together), '
      '`o` middle third, `-` bottom third (on opposite sides). `E` emitter, `x` unreadable bit, `w` readable witness whose emitter is unreadable, `.` bit left alone. '
      'Rows: even rows are the 16-bit lines (q20r..20r+15), odd rows the four bridge bits under them. Layout: Pittsburgh\'s wiring as read at fire (`noname_roles.json` edges, '
      'identical to `layout_156_family.json`).')
    P('')
    P(f"**Seat 3 with pooled seat 1** (r = {corr['ahd5~S1|pool'][0]:+.3f} ({corr['ahd5~S1|pool'][1]:.3f})):")
    P('```'); P(map1); P('```')
    P(f"**Seat 3 with pooled seat 2** (r = {corr['ahd5~S2|pool'][0]:+.3f} ({corr['ahd5~S2|pool'][1]:.3f})):")
    P('```'); P(map2); P('```')
    P('')
    P('By region (3 x 3, placed by the emitter): mean c over the region\'s pairs, width over shots.')
    P('')
    P('| rows | columns | pairs (emitters) | emitters | SEAT 3 |hd|/5 WITNESS deg | SEAT 1 pool OWN | SEAT 2 pool OWN | mean c, seat 3 x seat 1 | mean c, seat 3 x seat 2 |')
    P('|---|---|---|---|---|---|---|---|---|')
    for ry, rx, npair, nem, c1, c1w, c2, c2w, ems, raw in reg_rows:
        if npair == 0: P(f'| {ry} | {rx} | 0 | -- | -- | -- | -- | -- | -- |'); continue
        P(f'| {ry} | {rx} | {npair} ({nem}) | {", ".join(map(str, ems))} | {raw["ahd5"][0]:.2f} ({raw["ahd5"][1]:.2f}) | '
          f'{f4(*raw["S1|pool"])}{dag(*raw["S1|pool"])} | {f4(*raw["S2|pool"])}{dag(*raw["S2|pool"])} | {c1:+.3f} ({c1w:.3f}){dag(c1, c1w)} | {c2:+.3f} ({c2w:.3f}){dag(c2, c2w)} |')
    P('')
    oc = np.argsort(-mb['c1'])
    P('Ten pairs with the largest c (seat 3 x pooled seat 1), with their raw seats: ' + '; '.join(
        f"{pairs[i][0]}-{pairs[i][1]} at {xy[pairs[i][1]]} c {mb['c1'][i]:+.2f} ({mw['c1'][i]:.2f}) [S3 {base['ahd5'][i]:.2f}, S1 {base['S1|pool'][i]:+.4f}]" for i in oc[:10]) + '.')
    P('')
    P('Ten pairs with the most negative c: ' + '; '.join(
        f"{pairs[i][0]}-{pairs[i][1]} at {xy[pairs[i][1]]} c {mb['c1'][i]:+.2f} ({mw['c1'][i]:.2f}) [S3 {base['ahd5'][i]:.2f}, S1 {base['S1|pool'][i]:+.4f}]" for i in oc[::-1][:10]) + '.')
    P('')
    hand = None                                      # the closing sections are written by hand; a rerun keeps them
    if os.path.exists(OUT_MD):
        old = open(OUT_MD).read(); j = old.find('## WHAT EACH SEAT READ')
        if j >= 0 and '(plain words, no verdict; filled in by hand' not in old[j:]: hand = old[j:].rstrip('\n')
    if hand: P(hand)
    else:
        P('## WHAT EACH SEAT READ'); P(''); P('(plain words, no verdict; filled in by hand from the tables above)'); P('')
        P('## Could not compute'); P(''); P('(filled in by hand)')
    P('')
    open(OUT_MD, 'w').write('\n'.join(L) + '\n')
    print('wrote', OUT_MD, flush=True)


if __name__ == '__main__':
    main()
