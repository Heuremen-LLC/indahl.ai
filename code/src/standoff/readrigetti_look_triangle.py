"""readrigetti_look_triangle.py -- the look on Cepheus timed from three positions. Raw, no verdict, nothing cut; wrapped and unwrapped kept side by side.
CHECK FIRST  the clocks' turn per us over the delays (the moved frame should give ~36 deg/us); printed before anything else.
OBSERVER     our laid look, 1.5 us.
WITNESS      per clock: turn per look (slope over k = 1-6, unwrapped from k = 0) / turn per us (slope over delays 0-9 us) = us per look; by links 1 / 2 / 3+, three hand bands.
TIME         the looked-at qubits (in |1>): read-1 after k looks against read-1 after the delays; equivalent delay per look = slope over k of the delay that gives the same read-1 (log-linear on the delay curve).
Ratios W / O, T / O, T / W per strength, the Bonefish's lines beside them (12/11, phi, phi x 11/12), and the nearest of the Seven's numbers."""
import json, math, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rigetti_look_triangle as L
import rigetti_triangle_c as C
QS = L.QS; idx = {q: QS.index(q) for q in QS}; ei = [idx[q] for q in L.EM]
LINK = {k: [idx[q] for q in C.CL if C.D[q] and min(C.D[q], 3) == k] for k in (1, 2, 3)}
PHI = (1 + 5 ** .5) / 2
SEV = {'12/11': 12 / 11, '13/12': 13 / 12, '11/12': 11 / 12, '10/12': 10 / 12, '9/12': .75, 'phi': PHI, '1/phi': 1 / PHI, 'phi x 11/12': PHI * 11 / 12, '1.5': 1.5, '1-1/pi': 1 - 1 / math.pi, '1/pi': 1 / math.pi, '4/3': 4 / 3, '6/5': 1.2}
near = lambda x: (lambda k: f'{k} {(x / SEV[k] - 1) * 100:+.2f}%')(min(SEV, key=lambda k: abs(x / SEV[k] - 1)))


def slope(x, y):
    x = np.asarray(x, float); A = np.vstack([x, np.ones_like(x)]).T; return np.linalg.lstsq(A, y, rcond=None)[0][0]


def main():
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(L.RT.OUT, os.environ.get('LOOK_NPZ', 'lookTri2.npz'))).items()}
    P = lambda key: raw[key].mean(0)
    H = lambda kind, a, x: (1 - 2 * P((kind, a, x, 'X'))) - 1j * (1 - 2 * P((kind, a, x, 'Y')))
    D = L.DELAYS
    ang_d = np.array([np.angle(H('delay', 0, d) / H('delay', 0, 0)) for d in D]); und = np.unwrap(ang_d, axis=0)
    rate = np.array([slope(D, und[:, i]) for i in range(len(QS))])                      # rad per us, per qubit
    cl = [idx[q] for q in C.CL]
    print(f'CHECK: clocks turn over the delays (unwrapped) median {np.degrees(np.median(rate[cl])):+.1f} deg/us [quartiles {np.degrees(np.percentile(rate[cl], 25)):+.1f}, {np.degrees(np.percentile(rate[cl], 75)):+.1f}]; '
          f'the moved frame alone gives {L.DETUNE * 360 / 1e6:.1f}; hand kept at 9 us median {np.median(np.abs(H("delay", 0, 9))[cl] / np.abs(H("delay", 0, 0))[cl]):.2f}')
    p1d = np.array([raw[('delay', 0, d, 'X')][:, ei].mean(0) for d in D]) * .5 + np.array([raw[('delay', 0, d, 'Y')][:, ei].mean(0) for d in D]) * .5
    print('TIME, looked-at read-1 over the delays (mean of 7): ' + ' '.join(f'{d}us {p:.4f}' for d, p in zip(D, p1d.mean(1))))
    O = L.LOOK
    for a in L.STRENGTHS:
        ks = [0] + L.KS
        ang = np.array([np.zeros(len(QS))] + [np.angle(H('look', a, k) / H('delay', 0, 0)) for k in L.KS])
        for tag, A in (('WRAPPED', ang), ('UNWRAPPED', np.unwrap(ang, axis=0))):
            per = np.array([slope(ks, A[:, i]) for i in range(len(QS))]); W = per / rate
            kept = np.abs(H('delay', 0, 0))
            out = []
            for c in (1, 2, 3):
                w = W[LINK[c]]; b = np.argsort(np.argsort(kept[LINK[c]])) * 3 // len(w)
                out.append(f'{c}{"+" if c == 3 else ""} link {np.nanmedian(w):.4f} us [{np.nanpercentile(w, 25):.3f}, {np.nanpercentile(w, 75):.3f}] bands {"/".join(f"{np.nanmedian(w[b == j]):.3f}" for j in range(3))}')
            Wall = np.nanmedian(W[cl])
            if tag == 'UNWRAPPED': Wu = Wall
            print(f'  strength {a}: WITNESS {tag:<9} us per look: all clocks {Wall:.4f} | ' + ' | '.join(out))
        p1k = np.array([.5 * raw[('look', a, k, 'X')][:, ei].mean(0) + .5 * raw[('look', a, k, 'Y')][:, ei].mean(0) for k in L.KS])
        teq = []
        for j in range(len(L.EM)):
            lg = np.log(np.clip(p1d[:, j], 1e-4, 1)); row = [0.0]
            for v in np.log(np.clip(p1k[:, j], 1e-4, 1)):
                row.append(float(np.interp(-v, -lg, D)))                              # delay giving the same read-1 (curve falls)
            teq.append(slope(ks, row))
        teq = np.array(teq); T = float(np.median(teq))
        print(f'  strength {a}: TIME own fall, us of delay per look, per qubit ' + ' '.join(f'q{q} {t:.3f}' for q, t in zip(L.EM, teq)) + f' | median {T:.4f} | read-1 after 1-6 looks ' + ' '.join(f'{x:.4f}' for x in p1k.mean(1)))
        for nm, x, call in (('W / O', Wu / O, 12 / 11), ('T / O', T / O, PHI), ('T / W', T / Wu, PHI * 11 / 12)):
            print(f'    {nm} = {x:.4f} | the Bonefish line {call:.4f} ({(x / call - 1) * 100:+.2f}%) | nearest of the Seven: {near(x)}')


if __name__ == '__main__':
    main()
