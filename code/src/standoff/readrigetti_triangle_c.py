"""readrigetti_triangle_c.py -- triangle C: the emitters' |1> time during the train, three ways, side by side. Raw, no verdict, nothing cut.
OBSERVER  laid: from |0>, the pushes put the emitter in |1> for every second gap: 5 g us.
TIME      booked from each emitter's own decay (this batch's ruler at 1 / 5 / 10 / 20 us, log-linear between points), and its end state on three rungs.
WITNESS   the echoed clocks: (turn in the train arm - turn at rest) / ((turn held - turn at rest) / L), per clock; by links 1 / 2 / 3+, and in three bands by hand kept (no cut)."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import readrigetti_time as RR
import rigetti_triangle_c as C
QS = C.QS; idx = {q: QS.index(q) for q in QS}; EM = C.EM


def main():
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(C.OUT, 'triC.npz')).items()}
    cal = RR.calib({(k[0], k[1]): v for k, v in raw.items() if k[0] == 'cal'})
    P = lambda a, g, h: raw[(a, g, h)].mean(0)
    H = lambda a, g: (1 - 2 * P(a, g, 'X')) - 1j * (1 - 2 * P(a, g, 'Y'))
    pop = lambda key_e, key_b, q: RR.solve(cal[q]['x'], 1 - raw[key_e][:, idx[q]].mean(), 1 - raw[key_b][:, idx[q]].mean())
    R = {w: np.array([pop(('emruler', w, 'e'), ('emruler', w, 'ba'), q) for q in EM]) for w in C.EMRULER}
    print(f'TRIANGLE C. Emitters {EM}. Readout models: {sum(1 for q in EM if q in cal)} of {len(EM)}.')
    print('   TIME, the emitters\' own decay (rung 1 / rung 2): ' + ' | '.join(f'{w} us {R[w][:, 0].mean():.3f} / {R[w][:, 1].mean():.3f}' for w in C.EMRULER))
    ts = np.array([0.0] + C.EMRULER); Ls = np.log(np.clip(np.vstack([np.ones(len(EM))] + [R[w][:, 0] for w in C.EMRULER]), 0.02, 1))
    def q_of(g):
        j = int(min(max(np.searchsorted(ts, g) - 1, 0), len(ts) - 2)); f = (g - ts[j]) / (ts[j + 1] - ts[j]); return np.exp(Ls[j] + f * (Ls[j + 1] - Ls[j]))
    for g in C.GAPS:
        L = 10 * g; q = q_of(g); tau = -g / np.log(np.clip(q, 1e-6, 0.999999))
        pop1 = np.zeros(len(EM)); booked = np.zeros(len(EM))
        for _ in range(C.RT.PUSHES):
            booked += pop1 * tau * (1 - np.exp(-g / tau)); pop1 = 1 - pop1 * np.exp(-g / tau)
        end = np.array([pop(('train', g, 'X'), ('train', g, 'Y'), qq) for qq in EM])
        print(f'\n   g {g} us (train L = {L:g} us):')
        print(f'     OBSERVER laid |1> time {5 * g:.2f} us | TIME booked from own decay {booked.mean():.2f} us | TIME end state after the train rung 1 {end[:, 0].mean():+.4f} rung 2 {end[:, 1].mean():+.4f}')
        Ht, Hr, Hh = H('train', g), H('rest', g), H('held', g)
        scale = np.angle(Hh / Hr) / L; est = np.angle(Ht / Hr) / np.where(scale == 0, np.nan, scale); kept = np.abs(Hr)
        for name, cls in (('1 link', lambda d: d == 1), ('2 links', lambda d: d == 2), ('3+ links', lambda d: d is not None and d >= 3)):
            Q = [qq for qq in C.CL if C.D[qq] is not None and cls(C.D[qq])]; i = [idx[qq] for qq in Q]
            e = est[i]; k = kept[i]; band = np.argsort(np.argsort(k)) * 3 // max(len(k), 1)
            print(f'     WITNESS {name:<9} ({len(Q)} clocks): |1> time read {np.nanmedian(e):+7.2f} us [quartiles {np.nanpercentile(e, 25):+.2f}, {np.nanpercentile(e, 75):+.2f}] | pull scale {np.degrees(np.median(scale[i])):+.2f} deg/us '
                  f'| by hand band low/mid/high {" / ".join(f"{np.nanmedian(e[band == b]):+.2f}" for b in range(3))} (hand {" / ".join(f"{np.median(k[band == b]):.2f}" for b in range(3))})')


if __name__ == '__main__':
    main()
