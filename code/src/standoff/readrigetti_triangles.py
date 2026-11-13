"""readrigetti_triangles.py -- reads rigetti_triangles.py A and B. Raw, plain, no verdict word, nothing cut, every ruler kept beside the others.
A  OBSERVER the laid window; WITNESS each clock's turn (q0 in |1> or |2>, minus at rest, same window), read wrapped AND unwrapped along the window ladder (both printed); TIME q0's own rung-1 / rung-2 after each window.
B  per round and neighbour state: the seven emitters after ten pushes from |0>, raw read-1 fraction AND rung 1 / rung 2 from the round's readout model, per qubit and together.
  python readrigetti_triangles.py A | B"""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import readrigetti_time as RR
import rigetti_triangles as T
OUT = T.OUT; QS = T.QS; idx = {q: QS.index(q) for q in QS}


def readA():
    Z = {tuple(json.loads(k)[:2]): v for k, v in np.load(os.path.join(OUT, 'triA.npz')).items()}
    Zc = {k: v for k, v in Z.items() if k[0] == 'cal'}; cal = RR.calib(Zc)
    p1 = lambda st, w, h: Z[(st, w) if st != 'ref' else ('ref', 0)][:, :]
    def H(st, w):
        kx = [k for k in np.load(os.path.join(OUT, 'triA.npz')).files if json.loads(k)[:3] == ([st, w, 'X'] if st != 'ref' else ['ref', 0, 'X'])]
        return None
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(OUT, 'triA.npz')).items()}
    P = lambda st, w, h: raw[(st, w, h)].mean(0)
    Hh = lambda st, w: (1 - 2 * P(st, w, 'X')) - 1j * (1 - 2 * P(st, w, 'Y'))
    H0 = Hh('ref', 0); W = T.A_WIN
    print(f'A -- THE q0 TRIANGLE ON CEPHEUS. q0 readout model from this batch: {"yes" if 0 in cal else "no"}.')
    print('   TIME, q0 itself after each window (rung 1 / rung 2, from its plain and swap-then-flip reads on this batch\'s model):')
    for st in T.A_STATES:
        row = []
        for w in W:
            p = RR.solve(cal[0]['x'], 1 - raw[(st, w, 'X')][:, idx[0]].mean(), 1 - raw[(st, w, 'Y')][:, idx[0]].mean()) if 0 in cal else (np.nan, np.nan)
            row.append(f'{w:>3} us {p[0]:+.3f} / {p[1]:+.3f}')
        print(f'     q0 {st:<5}: ' + ' | '.join(row))
    print('   WITNESS, turn in deg per us over each window (state minus rest, same window). WRAPPED = each window alone; UNWRAPPED = along the ladder 0 -> 0.5 -> ... -> 6 us. Hand kept at rest beside it.')
    def turns(q, st):
        a = np.array([np.angle(Hh(st, w)[idx[q]] / Hh('rest', w)[idx[q]]) for w in W]); u = np.unwrap(np.concatenate([[0.0], a]))[1:]
        return np.degrees(a) / np.array(W), np.degrees(u) / np.array(W)
    for q in sorted([q for q in T.A_CLOCKS if T.D.get(q, 99) <= 2], key=lambda q: (T.D[q], q)):
        for st in ('one', 'two'):
            wr, un = turns(q, st); hk = [abs(Hh('rest', w)[idx[q]] / H0[idx[q]]) for w in W]
            print(f'     q{q:<3} {T.D[q]} link(s) q0 {st}: WRAPPED ' + ' '.join(f'{x:+7.1f}' for x in wr) + ' | UNWRAPPED ' + ' '.join(f'{x:+7.1f}' for x in un) + ' | hand ' + ' '.join(f'{x:.2f}' for x in hk))
    far = [q for q in T.A_CLOCKS if T.D.get(q, 99) >= 3]
    for st in ('one', 'two'):
        WR = np.array([turns(q, st)[0] for q in far]); UN = np.array([turns(q, st)[1] for q in far])
        print(f'     3+ links ({len(far)} clocks) q0 {st}: WRAPPED median ' + ' '.join(f'{x:+6.2f}' for x in np.median(WR, 0)) + ' | UNWRAPPED median ' + ' '.join(f'{x:+6.2f}' for x in np.median(UN, 0))
              + ' | quartile width ' + ' '.join(f'{x:.2f}' for x in (np.percentile(WR, 75, 0) - np.percentile(WR, 25, 0))))
    print('   windows (us):', W)


def readB():
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(OUT, 'triB.npz')).items()}
    EM = T.EM; ei = [idx[q] for q in EM]
    print(f'B -- THE PUSH JUMP, NEIGHBOURS FROM TIME. Emitters {EM}; ten pushes back to back from |0>. RAW = read-1 fraction (no model); MODEL = rung 1 / rung 2 from the round\'s own calibration.')
    for r in T.B_ROUNDS:
        Zc = {(k[0], k[1]): v for k, v in raw.items() if k[0] == 'cal' and k[2] == r}; cal = RR.calib(Zc)
        X = np.array([cal[q]['x'] for q in EM if q in cal])
        print(f'   round {r}: readout model medians r0 {np.median(X[:, 2]):.4f} m1 {np.median(X[:, 3]):.4f} m2 {np.median(X[:, 4]):.4f} eta {np.median(X[:, 5]):.4f}')
        for ns in T.B_STATES:
            e = raw[(ns, 'e', r)][:, ei].mean(0); b = raw[(ns, 'ba', r)][:, ei]
            mod = np.array([RR.solve(cal[q]['x'], 1 - raw[(ns, 'e', r)][:, idx[q]].mean(), 1 - raw[(ns, 'ba', r)][:, idx[q]].mean()) for q in EM])
            print(f'     neighbours {ns:<6}: RAW {e.mean():.4f} (' + ' '.join(f'q{q} {x:.3f}' for q, x in zip(EM, e)) + f') | MODEL rung 1 {mod[:, 0].mean():+.4f} rung 2 {mod[:, 1].mean():+.4f}')


if __name__ == '__main__':
    {'A': readA, 'B': readB}[sys.argv[1]]()
