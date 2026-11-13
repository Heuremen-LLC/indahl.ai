"""readjump.py -- reads THE JUMP RUN (every bit of ibm_pittsburgh, the same job every few minutes). By hand, outside the freeze. No verdict word.
THREE RULERS on every bit in every read, each from its OWN circuits:  (1) the ON clock  (2) the MID clock  (3) the no-time bite (look, look again, no wait).
Then, per bit across the reads: does its clock sit on ONE level, TWO, or THREE (each bit's own shot widths are the yardstick), and where a bit has two,
short clock / long clock -- from ON, and again from MID using ON's sorting of the reads (MID never chose which reads were 'short', so the cut that picks
jumping bits cannot pile MID's number up).
  python readjump.py [--boot 40] [--shapes-only]"""
import argparse, itertools, json, os, sys, warnings
import numpy as np
from scipy.optimize import curve_fit
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data', 'fire', 'ibm_pittsburgh')
WS = [60, 240, 300]; STONE = {'260/365': 260 / 365, '13/20': 13 / 20}


def fit_tau(ws, Y):
    """Y: waits x bits -> tau per bit (log-linear start, then least squares); nan where it cannot be placed."""
    out = np.full(Y.shape[1], np.nan); ws = np.asarray(ws, float)
    for b in range(Y.shape[1]):
        y = Y[:, b]
        if not np.all(np.isfinite(y)) or y[0] <= 0.05: continue
        try:
            p, _ = curve_fit(lambda w, G, t: G * np.exp(-w / t), ws, y, p0=[max(y[0], 0.1) * 1.2, 250.0], maxfev=2000)
            if 5 < p[1] < 3000: out[b] = p[1]
        except Exception: pass
    return out


def one_read(k, boot, rng):
    m = json.load(open(os.path.join(D, f'run{10 + k}_meta.json')))
    if m.get('complete') is not True: raise RuntimeError('not complete')
    z = np.load(os.path.join(D, f'run{10 + k}_results.npz')); wr = {c['pre_waits_us'][1]: c['pre_waits_realized_us'][1] for c in m['ledger']['circuits']}
    L = lambda key, i: np.asarray(z[f'{key}__L{i}']).astype(complex)
    off1 = np.concatenate([L('OFF|w0', 1), L('OFF|w300', 1)]); on1 = np.concatenate([L(f'ON|w{w}', 1) for w in [0] + WS])
    m0 = off1.mean(0); d = on1.mean(0) - m0; pr = lambda x: np.real((x - m0) * np.conj(d)) / np.abs(d) ** 2
    sep = np.abs(d) / np.sqrt((np.abs(off1 - m0) ** 2).mean(0) / 2)
    ws = [wr[w] for w in WS]; P = {s: [pr(L(f'{s}|w{w}', 2)) for w in WS] for s in ('ON', 'MID')}
    r = {'time': m.get('start_time'), 'sep': sep, 'bits': m['all_q']}
    for s in ('ON', 'MID'):
        r[f'tau_{s}'] = fit_tau(ws, np.array([p.mean(0) for p in P[s]]))
        reps = [fit_tau(ws, np.array([p[rng.integers(0, len(p), len(p))].mean(0) for p in P[s]])) for _ in range(boot)]
        r[f'w_{s}'] = np.nanstd(reps, 0)
        g = pr(L(f'{s}|w0', 2)) - pr(L(f'{s}|w0', 1)); r[f'none_{s}'] = g.mean(0); r[f'wnone_{s}'] = g.std(0, ddof=1) / np.sqrt(len(g))
        r[f'F60_{s}'] = P[s][0].mean(0)
    o = pr(L('OFF|w300', 2)); r['off300'] = o.mean(0); r['woff300'] = o.std(0, ddof=1) / np.sqrt(len(o))
    return r


def levels(t, w, k):
    """best split of the reads into k levels (reads sorted by clock, cuts between neighbours); returns (chi2 per degree of freedom, labels, level means)."""
    n = len(t); order = np.argsort(t); best = None
    for cuts in itertools.combinations(range(1, n), k - 1):
        lab = np.zeros(n, int); edges = (0,) + cuts + (n,)
        for j in range(k): lab[order[edges[j]:edges[j + 1]]] = j
        mu = np.array([np.sum(t[lab == j] / w[lab == j] ** 2) / np.sum(1 / w[lab == j] ** 2) for j in range(k)])
        c = float(np.sum(((t - mu[lab]) / w) ** 2))
        if best is None or c < best[0]: best = (c, lab, mu)
    return best[0] / max(n - k, 1), best[1], best[2]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--boot', type=int, default=40); ap.add_argument('--shapes-only', action='store_true'); a = ap.parse_args()
    ks = [k for k in range(1, 9) if os.path.exists(os.path.join(D, f'run{10 + k}_meta.json'))]
    if a.shapes_only:
        for k in ks:
            z = np.load(os.path.join(D, f'run{10 + k}_results.npz')); print(f'read {k}:', len(z.files), 'arrays, shape', z[z.files[0]].shape)
        return
    rng = np.random.default_rng(20261120); R = [one_read(k, a.boot, rng) for k in ks]; n = len(R); nb = len(R[0]['bits'])
    print(f'THE JUMP RUN: ibm_pittsburgh, {nb} bits, {n} reads at ' + ' '.join(r['time'][11:16] for r in R))
    T = np.array([r['tau_ON'] for r in R]); W = np.array([r['w_ON'] for r in R]); TM = np.array([r['tau_MID'] for r in R]); WM = np.array([r['w_MID'] for r in R])
    NB = np.array([r['none_ON'] for r in R]); NBM = np.array([r['none_MID'] for r in R]); SEP = np.array([r['sep'] for r in R]); OFF = np.array([r['off300'] for r in R])
    ok = (SEP.min(0) >= 3) & np.isfinite(T).all(0) & np.isfinite(W).all(0) & (W > 0).all(0) & np.isfinite(TM).all(0) & (WM > 0).all(0)
    print(f"bits readable in every read (clouds apart by 3 widths or more, both clocks placed): {int(ok.sum())} of {nb}.  CAN'T READ: {int((~ok).sum())} bits (rows kept in the json)")
    idx = np.where(ok)[0]
    print(f'\n-- EACH READ, middle bit of the readable ones:')
    for i, r in enumerate(R): print(f"   read {ks[i]} {r['time'][11:19]}  ON clock {np.median(T[i, idx]):6.1f} us  MID clock {np.median(TM[i, idx]):6.1f}  no-time bite ON {np.median(NB[i, idx]):+.4f}  MID {np.median(NBM[i, idx]):+.4f}  OFF after the long wait {np.median(OFF[i, idx]):+.4f}")
    print(f'   shot width of one bit\'s ON clock in one read, middle: {np.median(W[:, idx]):.1f} us; MID: {np.median(WM[:, idx]):.1f} us')
    rows = []
    for b in idx:
        c1, _, _ = levels(T[:, b], W[:, b], 1); c2, lab, mu = levels(T[:, b], W[:, b], 2) if n >= 3 else (np.nan, None, None)
        c3 = levels(T[:, b], W[:, b], 3)[0] if n >= 4 else np.nan
        row = {'bit': int(b), 'chi1': c1, 'chi2': c2, 'chi3': c3, 'tau': T[:, b].tolist(), 'w': W[:, b].tolist(), 'tauMID': TM[:, b].tolist(), 'none': NB[:, b].tolist()}
        if lab is not None:
            lo, hi = (0, 1) if mu[0] < mu[1] else (1, 0); s, l = lab == lo, lab == hi
            row.update({'short': float(mu[lo]), 'long': float(mu[hi]), 'ratio_ON': float(mu[lo] / mu[hi]), 'n_short': int(s.sum()),
                        'ratio_MID': float(np.mean(TM[s, b]) / np.mean(TM[l, b])), 'none_short': float(NB[s, b].mean()), 'none_long': float(NB[l, b].mean()),
                        'labels': ''.join('S' if x else 'L' for x in s)})
        rows.append(row)
    c1 = np.array([r['chi1'] for r in rows]); c2 = np.array([r['chi2'] for r in rows]); c3 = np.array([r['chi3'] for r in rows])
    print(f"\n-- ONE LEVEL, TWO, OR THREE? (each bit's clock across the {n} reads, scatter in units of its own shot widths, squared; 1 = sits on the levels)")
    print(f'   one level:   middle {np.median(c1):.2f};  bits above 2: {int((c1 > 2).sum())}, above 4: {int((c1 > 4).sum())}, above 9: {int((c1 > 9).sum())} of {len(rows)}')
    print(f'   two levels:  middle {np.nanmedian(c2):.2f};  bits still above 2: {int((c2 > 2).sum())}')
    print(f'   three levels: middle {np.nanmedian(c3):.2f};  bits still above 2: {int((c3 > 2).sum())}')
    for cut in (4, 9):
        J = [r for r in rows if r['chi1'] > cut and 'ratio_ON' in r]
        if not J: print(f"\n-- bits that do NOT sit on one level (above {cut}): none"); continue
        ro = np.array([r['ratio_ON'] for r in J]); rm = np.array([r['ratio_MID'] for r in J]); rm = rm[np.isfinite(rm)]
        bs = lambda x: float(np.std([np.median(rng.choice(x, len(x))) for _ in range(400)], ddof=1)) if len(x) > 1 else float('nan')
        print(f"\n-- BITS THAT DO NOT SIT ON ONE LEVEL (above {cut}): {len(J)} bits;  of them sitting on two levels (two-level scatter under 2): {sum(r['chi2'] < 2 for r in J)}")
        print(f'   short clock / long clock, ON (the ruler that chose the bits; piles up by the cut): middle {np.median(ro):.3f} +-{bs(ro):.3f}   quarter points {np.percentile(ro, 25):.3f} {np.percentile(ro, 75):.3f}')
        print(f"   short clock / long clock, MID on ON's sorting (did not choose):               middle {np.median(rm):.3f} +-{bs(rm):.3f}   quarter points {np.percentile(rm, 25):.3f} {np.percentile(rm, 75):.3f}")
        for nm, v in STONE.items(): print(f'      distance of the MID middle from {nm} = {v:.3f}: {(np.median(rm) - v) / bs(rm):+.1f} of its own widths;  ON middle: {(np.median(ro) - v) / bs(ro):+.1f}')
        print('      blank box: (left blank)')
        h, e = np.histogram(rm, bins=np.arange(0.2, 1.21, 0.05)); print('   MID ratios, count per 0.05 from 0.20: ' + ' '.join(str(x) for x in h))
        h, e = np.histogram(ro, bins=np.arange(0.2, 1.21, 0.05)); print('   ON ratios,  count per 0.05 from 0.20: ' + ' '.join(str(x) for x in h))
        ns, nl = np.array([r['none_short'] for r in J]), np.array([r['none_long'] for r in J])
        print(f'   no-time bite on those bits: in their SHORT reads middle {np.median(ns):+.4f}, in their LONG reads {np.median(nl):+.4f}; short minus long, middle {np.median(ns - nl):+.4f} +-{bs(ns - nl):.4f}')
        if cut == 4:
            print('   the first 25 (bit: clocks per read | sorting | ON ratio, MID ratio):')
            for r in sorted(J, key=lambda r: -r['chi1'])[:25]: print(f"     q{r['bit']:<4} " + ' '.join(f'{t:4.0f}' for t in r['tau']) + f"  | {r['labels']} | {r['ratio_ON']:.2f} {r['ratio_MID']:.2f}")
    json.dump({'reads': ks, 'times': [r['time'] for r in R], 'rows': rows, 'unreadable_bits': [int(b) for b in np.where(~ok)[0]]}, open(os.path.join(HERE, 'data', 'reads', 'jump_run.json'), 'w'))


if __name__ == '__main__':
    main()
