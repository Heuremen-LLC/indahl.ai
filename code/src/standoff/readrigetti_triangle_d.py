"""readrigetti_triangle_d.py -- triangle D: the emitters' |2> time during a train on the upper pair of rungs, three seats side by side. Raw, no verdict, nothing cut.
OBSERVER  laid, three ways: the gaps alone (5 g), gaps + half of every 32 ns push, half of the whole train (L + 0.32 us) / 2.
TIME      booked from each emitter's own decay (|2> ruler 0.5 / 1 / 2 / 4 us, |1> ruler 1 / 4 us, log-linear; |2> falls into |1>), and its end state on three rungs.
WITNESS   free clocks: (turn train - turn held |1>) / ((turn held |2> - turn held |1>) / L), per clock; WRAPPED (each L alone) and UNWRAPPED (along L 0 -> 1 -> 2 -> 4 us) side by side;
          by links 1 / 2 / 3+, three bands by hand kept (no cut); and the third baseline (the |0> start) in the same |2>-pull units."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import readrigetti_time as RR
import rigetti_triangle_d as D
import rigetti_triangle_c as C
QS = D.QS; idx = {q: QS.index(q) for q in QS}; EM = D.EM; PUSH = 0.032


def main():
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(C.OUT, os.environ.get('TRID_NPZ', 'triD.npz'))).items()}
    cal = RR.calib({(k[0], k[1]): v for k, v in raw.items() if k[0] == 'cal'})
    P = lambda a, g, h: raw[(a, g, h)].mean(0)
    H = lambda a, g: (1 - 2 * P(a, g, 'X')) - 1j * (1 - 2 * P(a, g, 'Y'))
    pop = lambda ke, kb, q: RR.solve(cal[q]['x'], 1 - raw[ke][:, idx[q]].mean(), 1 - raw[kb][:, idx[q]].mean())
    R2 = {w: np.array([pop(('ruler_two', w, 'e'), ('ruler_two', w, 'ba'), q) for q in EM]) for w in D.R2}
    R1 = {w: np.array([pop(('ruler_one', w, 'e'), ('ruler_one', w, 'ba'), q) for q in EM]) for w in D.R1}
    print(f'TRIANGLE D. Emitters {EM}. Readout models: {sum(1 for q in EM if q in cal)} of {len(EM)}.')
    print('   TIME, own decay from |2> (rung 1 / rung 2): ' + ' | '.join(f'{w} us {R2[w][:, 0].mean():.3f} / {R2[w][:, 1].mean():.3f}' for w in D.R2))
    print('   TIME, own decay from |1> (rung 1 / rung 2): ' + ' | '.join(f'{w} us {R1[w][:, 0].mean():.3f} / {R1[w][:, 1].mean():.3f}' for w in D.R1))
    def curve(ts, rows):
        L = np.log(np.clip(np.vstack([np.ones(len(EM))] + rows), 0.02, 1)); ts = np.array([0.0] + ts)
        def at(t):
            j = int(min(max(np.searchsorted(ts, t) - 1, 0), len(ts) - 2)); f = (t - ts[j]) / (ts[j + 1] - ts[j]); return np.exp(L[j] + f * (L[j + 1] - L[j]))
        return at
    s2 = curve(D.R2, [R2[w][:, 1] for w in D.R2]); s1 = curve(D.R1, [R1[w][:, 0] for w in D.R1])
    def booked(start, g):
        k2 = -np.log(np.clip(s2(g), 1e-6, 0.999999)) / g; k1 = -np.log(np.clip(s1(g), 1e-6, 0.999999)) / g
        p2 = np.full(len(EM), 1.0 if start == 'two' else 0.0); p1 = np.full(len(EM), 1.0 if start == 'one' else 0.0); t2 = np.zeros(len(EM)); n = 200; dt = g / n
        for _ in range(D.RT.PUSHES):
            for _ in range(n):
                t2 += p2 * dt; d2 = p2 * k2 * dt; d1 = p1 * k1 * dt; p2 -= d2; p1 += d2 - d1
            p1, p2 = p2.copy(), p1.copy()
        return t2
    Ls = [10 * g for g in D.GAPS]
    turn = lambda a, b, g: np.angle(H(a, g) / H(b, g))
    def unwrap(a, b):
        A = np.array([turn(a, b, g) for g in D.GAPS]); return A, np.unwrap(np.vstack([np.zeros(len(QS)), A]), axis=0)[1:]
    W2, U2 = unwrap('held_two', 'held_one'); W0, U0 = unwrap('train_zero', 'held_one')
    for s in ('one', 'two'):
        Wt, Ut = unwrap(f'train_{s}', 'held_one')
        print(f'\n   START |{"1" if s == "one" else "2"}>:')
        for j, g in enumerate(D.GAPS):
            L = Ls[j]; end = np.array([pop((f'train_{s}', g, 'X'), (f'train_{s}', g, 'Y'), q) for q in EM])
            print(f'    g {g} us (L {L:g} us): OBSERVER laid |2> time {5 * g:.2f} / {5 * g + 10 * PUSH / 2:.2f} / {(L + 10 * PUSH) / 2:.2f} us | TIME booked {booked(s, g).mean():.2f} us '
                  f'| end state rung 1 {end[:, 0].mean():+.4f} rung 2 {end[:, 1].mean():+.4f}')
            kept = np.abs(H('held_one', g))
            for nm, tW, sW in (('WRAPPED', Wt[j], W2[j]), ('UNWRAPPED', Ut[j], U2[j])):
                scale = sW / L; est = tW / np.where(scale == 0, np.nan, scale)
                for name, cls in (('1 link', lambda d: d == 1), ('2 links', lambda d: d == 2), ('3+ links', lambda d: d >= 3)):
                    Q = [q for q in C.CL if C.D[q] and cls(C.D[q])]; i = [idx[q] for q in Q]; e = est[i]; k = kept[i]; band = np.argsort(np.argsort(k)) * 3 // len(k)
                    print(f'      WITNESS {nm:<9} {name:<8} ({len(Q)}): |2> time {np.nanmedian(e):+7.2f} us [quartiles {np.nanpercentile(e, 25):+.2f}, {np.nanpercentile(e, 75):+.2f}] '
                          f'| pull |2>-|1> {np.degrees(np.median(scale[i])):+.2f} deg/us | bands low/mid/high {" / ".join(f"{np.nanmedian(e[band == b]):+.2f}" for b in range(3))} '
                          f'(hand {" / ".join(f"{np.median(k[band == b]):.2f}" for b in range(3))})')
    print('\n   THIRD BASELINE, the |0> start against held |1>, in |2>-pull units (us), and the |1>-|0> pull itself:')
    for j, g in enumerate(D.GAPS):
        L = Ls[j]
        for nm, t0, sW in (('WRAPPED', W0[j], W2[j]), ('UNWRAPPED', U0[j], U2[j])):
            est = t0 / np.where(sW == 0, np.nan, sW / L)
            print(f'    L {L:g} us {nm:<9}: ' + ' | '.join(f'{name} {np.nanmedian(est[[idx[q] for q in C.CL if C.D[q] and cls(C.D[q])]]):+.2f} us, pull |1>-|0> '
                  f'{np.degrees(np.median(-t0[[idx[q] for q in C.CL if C.D[q] and cls(C.D[q])]] / L)):+.2f} deg/us'
                  for name, cls in (('1 link', lambda d: d == 1), ('2 links', lambda d: d == 2), ('3+', lambda d: d >= 3))))


if __name__ == '__main__':
    main()
