"""readnoname.py -- reads THE NO-NAME SHOT (runs 121-123, ibm_pittsburgh). By hand, outside every freeze. A run is read only when all three reads have landed.
All bits, no cut beyond the readable-clouds rule (separation > 4 widths), means over bits, widths from shot resampling, each read against the other two.
No verdict word. Two bookkeepings stand side by side (the ruler is a measurement):
  EACH STRETCH ITS OWN RULER  -- the fading at 10 / 30 / 90 us read off the ON-left-alone arms of the same job, bit by bit
  ONE CLOCK                   -- the old bookkeeping: one exponential through the 300-us arm (what the +0.020 was measured against)
The witnesses: hands X / Y -> angle and length per witness; the half-difference between emitters started ON and OFF is the coupling times the emitter's ON time,
the half-sum is the witness's own leftover. A model of the witness, built from its emitter's fading (own, and the chip's typical), is held against both.
  python readnoname.py [--runs 121,122,123] [--dir data/fire/ibm_pittsburgh]"""
import argparse, json, math, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); NB = 100; RNG = np.random.default_rng(20261004)
CORE = ['A30_30', 'A10_30', 'A90_30', 'A30_10', 'A30_90', 'A30_30f', 'B30_30', 'B30_30f', 'N2', 'N6']
sys.path.insert(0, HERE)


def arms():
    import noname                                                   # the run's own arm list (importing it contacts nothing)
    return {s['key']: s for s in noname.specs()}


def load(d, r):
    m = json.load(open(os.path.join(d, f'run{r}_meta.json')))
    if m.get('complete') is not True and not m.get('synthetic_iq'): raise SystemExit(f'run {r} not complete: not read')
    z = np.load(os.path.join(d, f'run{r}_results.npz')); return m, {k.split('__')[0]: np.asarray(z[k]).astype(complex) for k in z.files}


def frame(A):
    c0 = A['F0'].mean(0); d = A['F1'].mean(0) - c0
    sep = np.abs(d) / np.sqrt((np.abs(A['F0'] - c0) ** 2).mean(0) / 2)
    return (lambda x: np.real((x - c0) * np.conj(d)) / np.abs(d) ** 2), (lambda x: np.imag((x - c0) * np.conj(d)) / np.abs(d) ** 2), sep


def book(start, qs, flip):
    on = np.asarray(start, float) * 1.0; off = 1 - on
    for q in qs: on, off = off + on * (1 - q), on * q
    if flip: on, off = off, on
    return on


def stats(A, S, roles):
    al, pe, sep = frame(A); g = sep > 4; lv = {k: al(v).mean(0) for k, v in A.items()}
    out = {'_bits': int(g.sum())}
    R = {L: np.clip(lv[f'R{L}'], 0.02, 1.2) for L in (10, 30, 90, 300)}
    own = lambda L: R[L]                                             # each stretch its own ruler (the bit's own fading at that length)
    one = lambda L: np.clip(lv['R300'], 0.02, 0.98) ** (L / 300.0)   # one clock through the 300-us arm
    for L in (10, 30, 90, 300): out[f'ruler: ON left alone {L} us (level)'] = lv[f'R{L}'][g].mean()
    for L in (10, 30, 90): out[f'ruler shape: ON {L} us minus one clock through 300'] = (lv[f'R{L}'] - one(L))[g].mean()
    out['ruler: OFF left alone 300 us (level)'] = lv['Z300'][g].mean()
    # a third level, three rulers that cover each other (Shuttle, 10/2): the flip identity is blind at x2 = 0.5, the halfway band sees exactly there,
    # and across-the-line sees anything off the line. Bands are counted beyond a plain two-cloud mix with the same along.
    c0 = A['F0'].mean(0); c1 = A['F1'].mean(0); s0 = np.sqrt((np.abs(A['F0'] - c0) ** 2).mean(0) / 2); s1 = np.sqrt((np.abs(A['F1'] - c1) ** 2).mean(0) / 2)
    half = lambda x: ((al(x) > 0.3) & (al(x) < 0.7)).mean(0); both = lambda x: ((np.abs(x - c0) > 3 * s0) & (np.abs(x - c1) > 3 * s1)).mean(0)
    h0, h1, b0, b1 = half(A['F0']), half(A['F1']), both(A['F0']), both(A['F1'])
    for k in ('A30_30', 'A30_30f', 'B30_30', 'B30_30f', 'A90_30', 'A30_90'):
        f = np.clip(lv[k], 0, 1)
        out[f'{k}: halfway band beyond the two-cloud mix'] = (half(A[k]) - ((1 - f) * h0 + f * h1))[g].mean()
        out[f'{k}: off both clouds beyond the two-cloud mix'] = (both(A[k]) - ((1 - f) * b0 + f * b1))[g].mean()
    out['flip identity, OFF start: level(ends OFF) + level(one more push) - 1  [= P2 (2 x2 - 1)]'] = (lv['A30_30'] + lv['A30_30f'] - 1)[g].mean()
    out['flip identity, ON start: level(ends ON) + level(one more push) - 1  [= P2 (2 x2 - 1)]'] = (lv['B30_30'] + lv['B30_30f'] - 1)[g].mean()
    for k in CORE:
        s = S[k]; start = np.zeros_like(lv['F0']) if s['start'] == 'OFF' else np.ones_like(lv['F0'])
        b_own = book(start, [own(L) for L in s['pushes']], s['flip']); b_one = book(start, [one(L) for L in s['pushes']], s['flip'])
        out[f'{k}: level'] = lv[k][g].mean()
        out[f'{k}: minus each-stretch-own-ruler book'] = (lv[k] - b_own)[g].mean()
        out[f'{k}: minus one-clock book'] = (lv[k] - b_one)[g].mean()
        out[f'{k}: across the line'] = pe(A[k]).mean(0)[g].mean()
    # witnesses
    if roles:
        W = [w for w in roles['witness_of'] if g[w] and g[roles['witness_of'][w]]]
        E = sorted(set(roles['witness_of'][w] for w in W))
        xa = 2 * lv['WA|X'] - 1; ya = 1 - 2 * lv['WA|Y']; xb = 2 * lv['WB|X'] - 1; yb = 1 - 2 * lv['WB|Y']
        va = xa + 1j * ya; vb = xb + 1j * yb; W_ = np.array(W, int)
        ang_a = np.angle(va[W_]); ang_b = np.angle(vb[W_])
        out['_witnesses'] = len(W); out['_emitters'] = len(E)
        out['witness length, emitters started OFF'] = np.abs(va[W_]).mean(); out['witness length, emitters started ON'] = np.abs(vb[W_]).mean()
        out['witness angle, emitters started OFF (deg)'] = np.degrees(np.angle(va[W_].mean())); out['witness angle, emitters started ON (deg)'] = np.degrees(np.angle(vb[W_].mean()))
        half = np.angle(vb[W_] * np.conj(va[W_])) / 2; out['witness half-difference ON minus OFF start (deg, mean over witnesses)'] = np.degrees(half).mean()
        out['witness half-sum, its own leftover (deg)'] = np.degrees(np.angle(va[W_] * vb[W_]) / 2).mean()
        E_ = np.array(E, int)
        q30 = np.clip(lv['R30'], 0.02, 0.999)
        out['emitters (in witness arms) started OFF: level'] = lv['WA|X'][E_].mean()
        bA = book(np.zeros(len(E_)), [q30[E_]] * 10, False); bB = book(np.ones(len(E_)), [q30[E_]] * 10, False)
        out['emitters started OFF, minus own-ruler book (both hand arms)'] = (((lv['WA|X'] + lv['WA|Y']) / 2)[E_] - bA).mean()
        out['emitters started ON, minus own-ruler book (both hand arms)'] = (((lv['WB|X'] + lv['WB|Y']) / 2)[E_] - bB).mean()
        # model of each witness from its emitter's fading: own vs the chip's typical, coupling and leftover fitted per witness
        typ = np.median(q30[g]); mis_own, mis_typ, thetas = [], [], []
        for w in W:
            e = roles['witness_of'][w]
            m_o, th_o = fit_witness(va[w], vb[w], q30[e]); m_t, _ = fit_witness(va[w], vb[w], typ)
            mis_own.append(m_o); mis_typ.append(m_t); thetas.append(th_o)
        out['witness model misfit, own emitter fading'] = np.mean(mis_own); out['witness model misfit, chip typical fading'] = np.mean(mis_typ)
        out['witness model misfit, own minus typical'] = np.mean(np.array(mis_own) - np.array(mis_typ))
        out['coupling read by the witness (deg per 30-us ON stretch, median)'] = np.degrees(np.median(np.abs(thetas)))
        # same shots: the witness's hand when its emitter ENDED ON vs ENDED OFF, measured, and the fitted witness's own expectation from its emitter's fading
        fits = {w: fit_witness(va[w], vb[w], q30[roles['witness_of'][w]], full=True) for w in W}
        for st, arms_ in (('OFF', (('WA|X', 'X', 0), ('WA|Y', 'Y', 1))), ('ON', (('WB|X', 'X', 0), ('WB|Y', 'Y', 1)))):
            for arm, lab, j in arms_:
                a = al(A[arm]); dm, dp = [], []
                for w in W:
                    e = roles['witness_of'][w]; on = a[:, e] > 0.5
                    if on.sum() >= 5 and (~on).sum() >= 5:
                        dm.append(a[on, w].mean() - a[~on, w].mean())
                        _, th, gn = fits[w]; dp.append(model_split_levels(q30[e], th, gn, st)[j])
                key = f'hand {lab} (emitters started {st}): witness level, emitter ENDED ON minus ENDED OFF'
                out[key + ', measured'] = np.nanmean(dm) if dm else float('nan')
                out[key + ', fitted witness from own fading'] = np.nanmean(dp) if dp else float('nan')
    return out


TH = np.linspace(-0.6, 0.6, 241)


def witness_split(q, start, n=10, steps=24, th=None):
    """expected witness vector, for every coupling on the grid TH at once (or one coupling th), from a two-state chain: the emitter ON fades with survival q per
    stretch (exponential within it), never rises; ON in stretch k adds theta * (+1 odd, -1 even) to the witness angle (the frame-held-still sign); the pushes swap
    ON/OFF. Returns the parts carried by the shots whose emitter ENDS ON and ENDS OFF."""
    T = TH if th is None else np.array([th], float)
    q = float(min(max(q, 1e-6), 0.999999)); lam = -math.log(q); u = (np.arange(steps) + 0.5) / steps; dens = lam * np.exp(-lam * u) / steps
    on = np.full(len(T), 1.0 if start == 'ON' else 0.0, complex); off = 1.0 - on
    for k in range(1, n + 1):
        sgn = 1 if k % 2 == 1 else -1
        stay = on * q * np.exp(1j * T * sgn); fall = on * (np.exp(1j * T[:, None] * sgn * u[None, :]) @ dens)
        on, off = off + fall, stay                                       # fade (staying ON keeps adding, falling stops part-way), then the push swaps
    return on, off


def witness_vecs(q, start, n=10, steps=24):
    on, off = witness_split(q, start, n, steps); return on + off


def fit_witness(va, vb, q, full=False):
    """fit coupling theta (per stretch), leftover angle and length (one complex gain) so that gain x V(q, theta) matches both measured vectors; (misfit, theta)."""
    ma = witness_vecs(q, 'OFF'); mb = witness_vecs(q, 'ON')
    c = (np.conj(ma) * va + np.conj(mb) * vb) / (np.abs(ma) ** 2 + np.abs(mb) ** 2)
    r = np.abs(va - c * ma) + np.abs(vb - c * mb); i = int(np.argmin(r))
    return (float(r[i]), float(TH[i]), complex(c[i])) if full else (float(r[i]), float(TH[i]))


def model_split_levels(q, th, gain, start):
    """the fitted witness, split by how its emitter ENDS: predicted hand-X and hand-Y LEVELS for ended-ON minus ended-OFF shots."""
    on, off = witness_split(q, start, th=th); p_on, p_off = (np.real(x[0]) for x in witness_split(q, start, th=0.0))
    if p_on < 1e-6 or p_off < 1e-6: return float('nan'), float('nan')
    v_on = gain * on[0] / p_on; v_off = gain * off[0] / p_off
    return (np.real(v_on) - np.real(v_off)) / 2, -(np.imag(v_on) - np.imag(v_off)) / 2      # level = (1 + X)/2 ; level = (1 - Y)/2


def three(vals, widths):
    v = np.array(vals); w = np.array(widths); mean = v.mean(); wid = np.sqrt((w ** 2).sum()) / len(v)
    return mean, wid, [v[i] - np.mean(np.delete(v, i)) for i in range(len(v))]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--runs', default='121,122,123'); ap.add_argument('--dir', default=os.path.join(HERE, 'data', 'fire', 'ibm_pittsburgh'))
    ap.add_argument('--roles', default=os.path.join(HERE, 'data', 'reads', 'noname_roles.json')); ap.add_argument('--nb', type=int, default=NB)
    a = ap.parse_args(); runs = [int(x) for x in a.runs.split(',')]; S = arms()
    roles = None
    if os.path.exists(a.roles):
        roles = json.load(open(a.roles)); roles['witness_of'] = {int(k): int(v) for k, v in roles['witness_of'].items()}
    per = []; stamps = []
    for r in runs:
        m, A = load(a.dir, r)
        if roles and A['F0'].shape[1] != roles['n']:          # dry run: few bits; map roles onto the drawn bits
            aq = m['all_q']; idx = {q: i for i, q in enumerate(aq)}
            rr = {'n': len(aq), 'witness_of': {idx[w]: idx[e] for w, e in roles['witness_of'].items() if w in idx and e in idx}}
        else: rr = roles
        base = stats(A, S, rr); boots = []
        for _ in range(a.nb):
            B = {k: v[RNG.integers(0, v.shape[0], v.shape[0])] for k, v in A.items()}
            boots.append(stats(B, S, rr))
        per.append({k: (base[k], np.nanstd([b[k] for b in boots])) for k in base}); stamps.append(m.get('end_time') or m.get('start_time'))
    print(f"THE NO-NAME SHOT, ibm_pittsburgh, runs {runs}, reads at {', '.join(str(s)[11:16] for s in stamps)}; readable bits {[int(p['_bits'][0]) for p in per]}"
          + (f"; witnesses {[int(p['_witnesses'][0]) for p in per]}, their emitters {[int(p['_emitters'][0]) for p in per]}" if '_witnesses' in per[0] else ''))
    print('   each line: read1 read2 read3 | all three (width) | each minus the other two')
    for k in per[0]:
        if k.startswith('_'): continue
        v = [p[k][0] for p in per]; w = [p[k][1] for p in per]; mn, wd, oth = three(v, w)
        print(f'   {k:<92} ' + '  '.join(f'{x:+.4f}({y:.4f})' for x, y in zip(v, w)) + f'  | {mn:+.4f} ({wd:.4f}) | ' + ' '.join(f'{o:+.4f}' for o in oth))


if __name__ == '__main__':
    main()
