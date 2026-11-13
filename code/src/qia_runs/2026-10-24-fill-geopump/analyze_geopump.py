"""analyze_geopump.py -- the readings of PLAN_GEOPUMP.md.text, run identically on synthetic and real data.
data[copy][tau] = dict(A={(d,b): (w, eL, eR)}, Ap={(d,b): (w, [(eL_k, eR_k, bins_k), ...])}, Bp=same as Ap with the SAME bins_k).
Bootstrap: shots resampled within each circuit; realizations k resampled jointly for Ap and Bp (paired); B draws.
R1  A today vs their published value at the same point (bound).    R2  Ap - Bp (readout cost beyond its waiting time; PRIMARY: Qtot_even).
R4  A - Ap_rec (control: random-basis preparation equivalent to theirs; Ap scored with its measured b_in, their estimator, so the assignment
    errors enter both the same way. Ap with PREPARED b_in is biased by uncancelled b_out assignment error -- found on synthetic data, 24 Oct,
    before any job -- and is used only in R2, where Bp carries the identical bias). R3 projection: 2 x R2 even part per bath / their missing even part.
Diagnostic: incoming-readout assignment error on aL, aR from Ap (recorded b_in vs prepared b_in).
FINAL per reading: CANNOT_TELL if the copy-gap interval excludes 0, else the outcome of the pooled interval (band from the plan)."""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import geopump as G
TAUS = (20.0, 60.0); DB = 0.45
MISSING = {20.0: (2.08 - 1.25, 1.73 - 1.25), 60.0: (3.57 - 3.21, 4.56 - 3.21)}   # SM Table 1: hw - sim, (L, R)

def _boot_means(q, rng, B):
    n = len(q); return q[rng.integers(0, n, (B, n))].mean(1)

def family_boot(fam, block, tau, rng, B):
    """bootstrap draws (B,) of each key for one family in one copy. block[(d,b)]."""
    acc = {}
    for (d, b), item in block.items():
        sch = G.schedule(DB, tau, d == 'rev')
        if fam == 'A':
            w, eL, eR = item; qL, qR = G.shot_heat(sch, 'A', eL, eR); acc[(d, b)] = (w, _boot_means(qL, rng, B), _boot_means(qR, rng, B), None)
        else:
            w, reals = item; ML, MR = [], []
            for eL, eR, bins in reals:
                qL, qR = G.shot_heat(sch, fam, eL, eR, bins); ML.append(_boot_means(qL, rng, B)); MR.append(_boot_means(qR, rng, B))
            acc[(d, b)] = (w, np.array(ML), np.array(MR), len(reals))
    return acc

def realize(acc, kidx):
    """apply a realization resample kidx[(d,b)] (B,K) -> means (B,) per (d,b)."""
    means = {}
    for key, (w, mL, mR, K) in acc.items():
        if K is None: means[key] = (w, (mL, mR))
        else:
            ix = kidx[key]; cols = np.arange(ix.shape[0])[:, None]
            means[key] = (w, (mL.T[cols, ix].mean(1), mR.T[cols, ix].mean(1)))
    return G.combine(means)

def copy_draws(cp, tau, rng, B):
    blk = cp[tau]; out = {}
    accA = family_boot('A', blk['A'], tau, rng, B); out['A'] = realize(accA, {})
    accAp = family_boot('Ap', blk['Ap'], tau, rng, B); accBp = family_boot('Bp', blk['Bp'], tau, rng, B); accAr = family_boot('Ap_rec', blk['Ap'], tau, rng, B)
    kidx = {key: rng.integers(0, v[3], (B, v[3])) for key, v in accAp.items()}   # same realizations for Ap, Ap_rec and Bp
    out['Ap'] = realize(accAp, kidx); out['Bp'] = realize(accBp, kidx); out['Ap_rec'] = realize(accAr, kidx)
    return out

def assign_err(cp, tau):
    """incoming readout: P(recorded != prepared) by prepared bit, per ancilla, from Ap."""
    r = {}
    for bath in 'LR':
        n = {0: [0, 0], 1: [0, 0]}
        for (d, b), (w, reals) in cp[tau]['Ap'].items():
            for eL, eR, bins in reals:
                e = np.asarray(eL if bath == 'L' else eR, int)[:, 0::2]; pb = bins[bath]
                for v in (0, 1):
                    m = pb == v; n[v][0] += int((e[:, m] != v).sum()); n[v][1] += int(m.sum() * e.shape[0])
        r[bath] = {v: n[v][0] / max(1, n[v][1]) for v in (0, 1)}
    return r

def lohi(x, band): a = (100 - band) / 2; return np.percentile(x, a), np.percentile(x, 100 - a)

def run(data, band=95.0, B=1000, seed=7, published=None, quiet=False):
    rng = np.random.default_rng(seed); res = {}
    for tau in TAUS:
        per = [copy_draws(cp, tau, rng, B) for cp in data]
        R = {}
        for name, f in (('R2_Ap_minus_Bp', lambda c: {k: c['Ap'][k] - c['Bp'][k] for k in G.KEYS}),
                        ('R4_A_minus_Aprec', lambda c: {k: c['A'][k] - c['Ap_rec'][k] for k in G.KEYS})):
            dc = [f(c) for c in per]
            for k in G.KEYS:
                gap = dc[0][k] - dc[1][k] if len(dc) > 1 else None; pooled = np.mean([d[k] for d in dc], 0)
                lo, hi = lohi(pooled, band); g = lohi(gap, band) if gap is not None else (0, 0)
                fin = 'CANNOT_TELL' if (g[0] > 0 or g[1] < 0) else G.outcome(lo, hi)
                R[(name, k)] = dict(val=float(np.median(pooled)), lo=float(lo), hi=float(hi), gap=(float(g[0]), float(g[1])), final=fin)
        if published is not None and tau in published:
            for k, (pv, pse) in published[tau].items():
                ours = np.mean([c['A'][k] for c in per], 0); d = ours - (pv + pse * rng.standard_normal(B)); lo, hi = lohi(d, band)
                R[('R1_A_today_minus_published', k)] = dict(val=float(np.median(d)), lo=float(lo), hi=float(hi), gap=None, final=G.outcome(lo, hi))
        mL, mR = MISSING[tau]
        for k, miss in (('QL_even', mL), ('QR_even', mR)):
            r2 = R[('R2_Ap_minus_Bp', k)]; R[('R3_projection_2xR2_over_missing', k)] = dict(val=2 * r2['val'] / miss, lo=2 * r2['lo'] / miss, hi=2 * r2['hi'] / miss, gap=None, final='PROJECTION')
        R[('diag_incoming_assignment', 'aL_aR')] = [assign_err(cp, tau) for cp in data]
        res[tau] = R
    if not quiet:
        for tau in TAUS:
            print(f'=== tau {tau:g}, delta_B {DB} (band {band:g}%)')
            for (name, k), v in res[tau].items():
                if name.startswith('diag'): print(f'   {name}: ' + '; '.join(f'copy{i+1} aL P(1|0) {c["L"][0]:.4f} P(0|1) {c["L"][1]:.4f}, aR P(1|0) {c["R"][0]:.4f} P(0|1) {c["R"][1]:.4f}' for i, c in enumerate(v))); continue
                gs = f'  copy gap [{v["gap"][0]:+.3f}, {v["gap"][1]:+.3f}]' if v['gap'] else ''
                print(f'   {name:34s} {k:9s} {v["val"]:+.4f} [{v["lo"]:+.4f}, {v["hi"]:+.4f}]{gs} -> {v["final"]}')
    return res
