"""readrigetti_triangle_f.py -- triangle F: the ruler as the object. Raw, no verdict, nothing cut.
OBSERVER  laid windows 0.25-6 us, emitters held at rest / |1> / |2>.
TIME      the emitters' own rung populations at each window from the same shots (each round its own readout model); the rounds ~3 min apart; the clocks' own drift (rest in round r against round 1).
WITNESS   three pulls per window (|1>-|0>, |2>-|1>, |2>-|0>, deg/us), wrapped and unwrapped along the windows, 1 / 2 / 3+ links; and the pull per unit population: c1 = turn(|1>-|0>) / integral p1 (|1> held),
          c2 = (turn(|2>-|0>) - c1 x integral p1 (|2> held)) / integral p2 (|2> held), integrals by trapezoid from the prepared state at 0 through the measured windows (emitter mean)."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import readrigetti_time as RR
import rigetti_triangle_c as C
import rigetti_triangle_f as F
QS = F.QS; idx = {q: QS.index(q) for q in QS}; EM = F.EM; W = F.WIN
LINK = {k: [idx[q] for q in C.CL if C.D[q] and min(C.D[q], 3) == k] for k in (1, 2, 3)}


def main():
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(C.OUT, 'triF.npz')).items()}
    P = lambda s, w, h, r: raw[(s, w, h, r)].mean(0)
    H = lambda s, w, r: (1 - 2 * P(s, w, 'X', r)) - 1j * (1 - 2 * P(s, w, 'Y', r))
    print(f'TRIANGLE F. Emitters {EM}. Clocks 1 / 2 / 3+ links: {len(LINK[1])} / {len(LINK[2])} / {len(LINK[3])}. Windows {W} us.')
    C1 = {}; C2 = {}
    for r in F.ROUNDS:
        cal = RR.calib({(k[0], k[1]): v for k, v in raw.items() if k[0] == 'cal' and k[2] == r})
        pop = {s: np.array([[RR.solve(cal[q]['x'], 1 - raw[(s, w, 'X', r)][:, idx[q]].mean(), 1 - raw[(s, w, 'Y', r)][:, idx[q]].mean()) for q in EM] for w in W]).mean(1) for s in F.STATES}
        start = {'zero': (0, 0), 'one': (1, 0), 'two': (0, 1)}
        def integ(s, rung):
            t = np.array([0.0] + W); p = np.array([start[s][rung]] + list(pop[s][:, rung])); return np.array([np.trapezoid(p[:j + 2], t[:j + 2]) for j in range(len(W))])
        I1o, I1t, I2t = integ('one', 0), integ('two', 0), integ('two', 1)
        print(f'\n ROUND {r}. readout models {sum(1 for q in EM if q in cal)} of {len(EM)}.')
        print('   TIME populations rung 1 / rung 2:  |1> held ' + ' '.join(f'{a:.3f}/{b:.3f}' for a, b in pop['one']) + '\n                                      |2> held ' + ' '.join(f'{a:.3f}/{b:.3f}' for a, b in pop['two'])
              + '\n                                      rest     ' + ' '.join(f'{a:.3f}/{b:.3f}' for a, b in pop['zero']))
        if r > 1:
            dr = np.array([np.angle(H('zero', w, r) / H('zero', w, 1)) for w in W])
            print('   TIME the clocks\' own drift, rest vs round 1 (deg/us, all clocks median): ' + ' '.join(f'{np.degrees(np.median(dr[j])) / w:+.2f}' for j, w in enumerate(W)))
        A = {}
        for nm, a, b in (('|1>-|0>', 'one', 'zero'), ('|2>-|1>', 'two', 'one'), ('|2>-|0>', 'two', 'zero')):
            wr = np.array([np.angle(H(a, w, r) / H(b, w, r)) for w in W]); A[nm] = (wr, np.unwrap(np.vstack([np.zeros(len(QS)), wr]), axis=0)[1:])
        for k in (1, 2, 3):
            i = LINK[k]
            print(f'   WITNESS {k}{"+" if k == 3 else ""} link(s), pull deg/us per window, WRAPPED | UNWRAPPED:')
            for nm, (wr, un) in A.items():
                print(f'     {nm}: ' + ' '.join(f'{np.degrees(np.median(wr[j][i])) / w:+7.2f}' for j, w in enumerate(W)) + ' | ' + ' '.join(f'{np.degrees(np.median(un[j][i])) / w:+7.2f}' for j, w in enumerate(W)))
            for tag, sel in (('WRAPPED', 0), ('UNWRAPPED', 1)):
                a10 = A['|1>-|0>'][sel][:, i]; a20 = A['|2>-|0>'][sel][:, i]
                c1 = a10 / I1o[:, None]; c2 = (a20 - c1 * I1t[:, None]) / I2t[:, None]
                C1[(r, k, tag)] = np.degrees(np.median(c1, 1)); C2[(r, k, tag)] = np.degrees(np.median(c2, 1))
                print(f'     per unit population {tag:<9}: c1 ' + ' '.join(f'{x:+7.2f}' for x in C1[(r, k, tag)]) + ' | c2 ' + ' '.join(f'{x:+7.2f}' for x in C2[(r, k, tag)]) + ' | c2/c1 '
                      + ' '.join(f'{b / a if abs(a) > 1e-9 else np.nan:+6.2f}' for a, b in zip(C1[(r, k, tag)], C2[(r, k, tag)])))
    print('\n ACROSS ROUNDS, 1 link, UNWRAPPED, per window (round 1 / 2 / 3):')
    for nm, M in (('c1', C1), ('c2', C2)):
        print(f'   {nm}: ' + ' | '.join(f'{w} us ' + '/'.join(f'{M[(r, 1, "UNWRAPPED")][j]:+.2f}' for r in F.ROUNDS) for j, w in enumerate(W)))


if __name__ == '__main__':
    main()
