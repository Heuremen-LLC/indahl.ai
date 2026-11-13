"""readrigetti_time.py -- reads rigetti_time.py batches. Raw, plain, no verdict word. Per batch:
 1. each qubit's readout model from that batch's own 8 calibration sequences (rigetti_gamble.fit: rest p1, p2; r0, m1, m2 = P(read 0) from rungs 0/1/2; eta = swap);
 2. per arm, rung-1 and rung-2 populations from the plain and swap-then-flip reads, solved exactly on that model; widths from resampling shots;
 3. push trains against the qubit's own decay three ways: ONE (one exponential through its 30-us rung-1 level), CURVE (log-linear through 0 / 3 / 10 / 30 us),
    and per ruler copy (a, b, c). The halfway start has no no-push arm: its bookkeeping assumes a start of 0.5 (said so in the output).
Qubits kept: swap swing > 0.3 in today's tune, calibration fit converged with rung-2 readout width < 0.05.  python readrigetti_time.py K [K ...]"""
import json, math, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'time20261004'); sys.path.insert(0, HERE)
import rigetti_gamble as G
import rigetti_time as RT
QS = RT.QS; SEQS = RT.SEQS; NB = 30


def load(k):
    Z = dict(np.load(os.path.join(OUT, f'read{k}.npz'))); return {tuple(json.loads(t)[:2]): v for t, v in Z.items()}


def calib(Z):
    cal = {}
    for i, q in enumerate(QS):
        y = {s: 1 - Z[('cal', s)][:, i].mean() for s in SEQS if ('cal', s) in Z}; n = {s: Z[('cal', s)].shape[0] for s in SEQS if ('cal', s) in Z}
        if len(y) < 8: continue
        try: x, e, cst = G.fit(y, n)
        except Exception: continue
        cal[q] = {'x': x, 'e': e, 'cost': cst}
    return cal


def solve(x, y_e, y_ba):
    """exact (P1, P2) from P(read0) plain and after 'ba', on the per-qubit model x = (p1, p2, r0, m1, m2, eta)."""
    _, _, r0, m1, m2, eta = x
    def read0(P1, P2):
        P = np.array([1 - P1 - P2, P1, P2]); a = r0 * P[0] + m1 * P[1] + m2 * P[2]
        Pb = np.array([P[0], (1 - eta) * P[1] + eta * P[2], eta * P[1] + (1 - eta) * P[2]]); Pa = np.array([Pb[1], Pb[0], Pb[2]]) * .995 + Pb * .005
        return a, r0 * Pa[0] + m1 * Pa[1] + m2 * Pa[2]
    b0 = np.array(read0(0, 0)); A = np.column_stack([np.array(read0(1, 0)) - b0, np.array(read0(0, 1)) - b0])
    return np.linalg.solve(A, np.array([y_e, y_ba]) - b0)


def book(m0, q, n):
    on, off = m0, 1 - m0
    for _ in range(n): on, off = off + on * (1 - q), on * q
    return on


def stats(Z, cal, keep):
    def pops(key):
        P = []
        for q in keep:
            i = QS.index(q); ye = 1 - Z[(key, 'e')][:, i].mean(); yb = 1 - Z[(key, 'ba')][:, i].mean(); P.append(solve(cal[q]['x'], ye, yb))
        return np.array(P)                      # (qubits, 2): rung 1, rung 2
    out = {}; R = {}
    for cp in 'abc':
        for w in RT.RULER: R[(cp, w)] = pops(f'RULER|ON|w{w}|{cp}')
    on0 = np.array([1 - cal[q]['x'][2] if False else 1.0 for q in keep])
    for cp in 'abc':
        for w in RT.RULER: out[f'ruler |1> then {w:>2} us, copy {cp}: rung 1 / rung 2'] = (R[(cp, w)][:, 0].mean(), R[(cp, w)][:, 1].mean())
    idle = pops('RULER|OFF|w30'); out['idle |0> 30 us: rung 1 / rung 2'] = (idle[:, 0].mean(), idle[:, 1].mean())
    for st in ('OFF', 'ON', 'MID'):
        m0 = {'OFF': 0.0, 'ON': 1.0, 'MID': 0.5}[st]
        for g in RT.SPACINGS:
            P = pops(f'{st}|g{g}'); r1, r2 = P[:, 0], P[:, 1]
            out[f'{st} g{g:>2} us: rung 1 / rung 2'] = (r1.mean(), r2.mean())
            if g == 0: out[f'{st} g{g:>2} us: rung 1 minus start (no time between pushes)'] = ((r1 - book(m0, 1.0, RT.PUSHES)).mean(), np.nan); continue
            ones, curves = [], []
            for cp in 'abc':
                L30 = np.clip(R[(cp, 30)][:, 0], 0.02, 0.99); q1 = L30 ** (g / 30)
                ts = np.array([0.0] + RT.RULER); Ls = np.log(np.clip(np.vstack([np.ones(len(keep))] + [R[(cp, w)][:, 0] for w in RT.RULER]), 0.02, 1.0))
                j = int(min(max(np.searchsorted(ts, g) - 1, 0), len(ts) - 2)); f = (g - ts[j]) / (ts[j + 1] - ts[j]); qc = np.exp(np.clip(Ls[j] + f * (Ls[j + 1] - Ls[j]), -5, 0))
                ones.append((r1 - book(m0, q1, RT.PUSHES)).mean()); curves.append((r1 - book(m0, qc, RT.PUSHES)).mean())
            out[f'{st} g{g:>2} us: rung 1 minus ONE (copies a/b/c)'] = tuple(ones)
            out[f'{st} g{g:>2} us: rung 1 minus CURVE (copies a/b/c)'] = tuple(curves)
    return out


def main():
    for k in [int(a) for a in sys.argv[1:]] or [1]:
        Z = load(k); cal = calib(Z)
        fit = json.load(open(os.path.join(OUT, 'tune_fit.json')))
        allq = [q for q in QS if q in cal]                                           # every qubit with a fitted readout model; no cut
        wid = np.array([cal[q]['e'][4] if np.isfinite(cal[q]['e'][4]) else np.inf for q in allq]); band = np.argsort(np.argsort(wid)) * 3 // len(allq)
        print(f'readout-model bands by rung-2 readout width (tight / mid / loose): ' + ' / '.join(f"{int((band == b).sum())} qubits, width {np.median(wid[band == b]):.3f}" for b in range(3))
              + f' | no model: {[q for q in QS if q not in cal]} | swap not reached (swing <= 0.3): {[q for q in QS if fit[str(q)]["swing"] <= 0.3]}')
        for b, nm in enumerate(('TIGHT', 'MID', 'LOOSE')):
            sb = stats(Z, cal, [q for q, bb in zip(allq, band) if bb == b])
            print(f'   [{nm} band] OFF g 3 us rung 1 minus ONE / CURVE (copy a): {sb["OFF g 3 us: rung 1 minus ONE (copies a/b/c)"][0]:+.4f} / {sb["OFF g 3 us: rung 1 minus CURVE (copies a/b/c)"][0]:+.4f} | '
                  f'OFF g 3 us rung 2: {sb["OFF g 3 us: rung 1 / rung 2"][1]:+.4f} | idle |0> rung 2: {sb["idle |0> 30 us: rung 1 / rung 2"][1]:+.4f} | back-to-back OFF: {sb["OFF g 0 us: rung 1 minus start (no time between pushes)"][0]:+.4f}')
        keep = allq
        s = stats(Z, cal, keep)
        rng = np.random.default_rng(202610041 + k); B = []
        for _ in range(NB):
            Zb = {kk: v[rng.integers(0, v.shape[0], v.shape[0])] for kk, v in Z.items()}; B.append(stats(Zb, cal, keep))
        rest2 = np.array([cal[q]['x'][1] for q in keep]); m2 = np.array([cal[q]['x'][4] for q in keep]); eta = np.array([cal[q]['x'][5] for q in keep])
        print(f'\nRIGETTI TIME, batch {k}: all {len(keep)} of {len(QS)} qubits with a readout model (no cut). '
              f'Calibration medians: rest rung 2 {np.median(rest2):.4f}, P(read 0 | rung 2) {np.median(m2):.3f}, swap {np.median(eta):.3f}. Halfway start: bookkeeping assumes 0.5.')
        for key, v in s.items():
            vv = np.array(v, dtype=float); w = np.nanstd([np.array(b[key], dtype=float) for b in B], axis=0)
            print(f'   {key:<52} ' + '  '.join(f'{a:+.4f} +- {b:.4f}' if np.isfinite(a) else '--' for a, b in zip(np.atleast_1d(vv), np.atleast_1d(w))))


if __name__ == '__main__':
    main()
