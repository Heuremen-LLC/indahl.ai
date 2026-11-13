"""readrigetti_triangle_e.py -- triangle E: the emitters' |2> time on the upper pair of rungs, pushes N = 4 / 10 / 20 across L = 1 / 2 / 4 us, three seats per row. Raw, no verdict, nothing cut.
OBSERVER  laid: gaps alone (N/2 x g), and gaps + half of every 32 ns push.   TIME  booked from own decay (|2> falls into |1>, |1> into |0>; log-linear rulers) and the end state on three rungs.
WITNESS   free clocks, (turn train - turn held |1>) / ((turn held |2> - turn held |1>) / L); WRAPPED (each L alone) and UNWRAPPED (along L 0 -> 1 -> 2 -> 4) side by side; 1 link with quartiles and
          three hand bands (no cut), 2 and 3+ links as medians. Ratios printed both ways beside the rows; the |0> start in the same units as the third baseline."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import readrigetti_time as RR
import rigetti_triangle_c as C
import rigetti_triangle_e as E
QS = E.QS; idx = {q: QS.index(q) for q in QS}; EM = E.EM; PUSH = 0.032
LINK = {k: [idx[q] for q in C.CL if C.D[q] and min(C.D[q], 3) == k] for k in (1, 2, 3)}


def main():
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(C.OUT, 'triE.npz')).items()}
    cal = RR.calib({(k[0], k[1]): v for k, v in raw.items() if k[0] == 'cal'})
    P = lambda key: raw[key].mean(0)
    H = lambda a, N, L: (1 - 2 * P((a, N, L, 'X'))) - 1j * (1 - 2 * P((a, N, L, 'Y')))
    pop = lambda ke, kb, q: RR.solve(cal[q]['x'], 1 - raw[ke][:, idx[q]].mean(), 1 - raw[kb][:, idx[q]].mean())
    R2 = {w: np.array([pop(('ruler_two', w, 'e'), ('ruler_two', w, 'ba'), q) for q in EM]) for w in E.D.R2}
    R1 = {w: np.array([pop(('ruler_one', w, 'e'), ('ruler_one', w, 'ba'), q) for q in EM]) for w in E.D.R1}
    print(f'TRIANGLE E. Emitters {EM}. Readout models {sum(1 for q in EM if q in cal)} of {len(EM)}. Clocks 1 / 2 / 3+ links: {len(LINK[1])} / {len(LINK[2])} / {len(LINK[3])}.')
    print('   TIME own decay from |2> (rung 1 / 2): ' + ' | '.join(f'{w} us {R2[w][:, 0].mean():.3f} / {R2[w][:, 1].mean():.3f}' for w in E.D.R2)
          + '   from |1>: ' + ' | '.join(f'{w} us {R1[w][:, 0].mean():.3f} / {R1[w][:, 1].mean():.3f}' for w in E.D.R1))
    def curve(ts, rows):
        Lg = np.log(np.clip(np.vstack([np.ones(len(EM))] + rows), 0.02, 1)); ts = np.array([0.0] + ts)
        def at(t):
            j = int(min(max(np.searchsorted(ts, t) - 1, 0), len(ts) - 2)); f = (t - ts[j]) / (ts[j + 1] - ts[j]); return np.exp(Lg[j] + f * (Lg[j + 1] - Lg[j]))
        return at
    s2 = curve(E.D.R2, [R2[w][:, 1] for w in E.D.R2]); s1 = curve(E.D.R1, [R1[w][:, 0] for w in E.D.R1])
    def booked(start, N, g):
        k2 = -np.log(np.clip(s2(g), 1e-6, 0.999999)) / g; k1 = -np.log(np.clip(s1(g), 1e-6, 0.999999)) / g
        p2 = np.full(len(EM), 1.0 if start == 'two' else 0.0); p1 = np.full(len(EM), 1.0 if start == 'one' else 0.0); t2 = np.zeros(len(EM)); n = 200; dt = g / n
        for _ in range(N):
            for _ in range(n):
                t2 += p2 * dt; d2 = p2 * k2 * dt; d1 = p1 * k1 * dt; p2 -= d2; p1 += d2 - d1
            p1, p2 = p2.copy(), p1.copy()
        return t2.mean()
    def series(a, Na, b, Nb):
        A = np.array([np.angle(H(a, Na, L) / H(b, Nb, L)) for L in E.LS]); return A, np.unwrap(np.vstack([np.zeros(len(QS)), A]), axis=0)[1:]
    W2, U2 = series('held_two', 0, 'held_one', 0)
    print('   pull |2>-|1> at 1 link (deg/us), wrapped / unwrapped: ' + ' | '.join(f'L {L} {np.degrees(np.median(W2[j][LINK[1]])) / L:+.2f} / {np.degrees(np.median(U2[j][LINK[1]])) / L:+.2f}' for j, L in enumerate(E.LS)))
    for s in ('one', 'two', 'zero'):
        print(f'\n   START |{ {"one": 1, "two": 2, "zero": 0}[s] }>' + ('   (third baseline: the swap with nothing to swap)' if s == 'zero' else ''))
        for N in E.NS:
            Wt, Ut = series(f'train_{s}', N, 'held_one', 0)
            for j, L in enumerate(E.LS):
                g = E.gap(L, N); lay = N / 2 * g; lay2 = lay + N * PUSH / 2; bk = booked(s, N, g)
                end = np.array([pop((f'train_{s}', N, L, 'X'), (f'train_{s}', N, L, 'Y'), q) for q in EM])
                ests = {nm: tw / np.where(sw == 0, np.nan, sw / L) for nm, tw, sw in (('w', Wt[j], W2[j]), ('u', Ut[j], U2[j]))}
                e1 = ests['u'][LINK[1]]; k = np.abs(H('held_one', 0, L))[LINK[1]]; band = np.argsort(np.argsort(k)) * 3 // len(k)
                w1 = np.nanmedian(ests['w'][LINK[1]]); u1 = np.nanmedian(e1)
                row = (f'    N {N:>2} L {L} (g {g:.3f}): OBSERVER laid {lay:.2f} / {lay2:.2f} | TIME booked {bk:.2f}, end rung 1 {end[:, 0].mean():.3f} rung 2 {end[:, 1].mean():.3f} '
                       f'| WITNESS 1 link {w1:+.2f}w {u1:+.2f}u [q {np.nanpercentile(e1, 25):+.2f}, {np.nanpercentile(e1, 75):+.2f}] bands {" / ".join(f"{np.nanmedian(e1[band == b]):+.2f}" for b in range(3))}'
                       f' | 2 links {np.nanmedian(ests["u"][LINK[2]]):+.2f} | 3+ {np.nanmedian(ests["u"][LINK[3]]):+.2f}')
                if s != 'zero': row += f' || witness/booked {u1 / bk:.3f} | booked/laid {bk / lay:.3f} | witness/laid {u1 / lay:.3f}'
                print(row)


if __name__ == '__main__':
    main()
