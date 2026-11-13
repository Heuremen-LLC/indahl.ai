"""readrigetti_triangle_g.py -- triangle G: the emitters' own populations with the other qubits in five states, solved with three readout models side by side. Raw, no verdict, nothing cut.
Rows: clock state x emitter start x window; columns: rung 1 / rung 2 under each model; and the raw read-1 fraction (no model) beside them."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import readrigetti_time as RR
import rigetti_triangle_c as C
import rigetti_triangle_g as G
QS = G.QS; idx = {q: QS.index(q) for q in QS}; EM = G.EM; ei = [idx[q] for q in EM]


def main():
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(C.OUT, 'triG.npz')).items()}
    cals = {m: RR.calib({('cal', k[1]): v for k, v in raw.items() if k[0] == f'cal_{m}'}) for m in G.MODELS}
    print(f'TRIANGLE G. Emitters {EM}. Readout models fitted: ' + ', '.join(f'{m} {sum(1 for q in EM if q in cals[m])}/{len(EM)}' for m in G.MODELS))
    for m in G.MODELS:
        X = np.array([cals[m][q]['x'] for q in EM if q in cals[m]])
        print(f'   model {m:<8}: medians p1 {np.median(X[:, 0]):.4f} p2 {np.median(X[:, 1]):.4f} r0 {np.median(X[:, 2]):.4f} m1 {np.median(X[:, 3]):.4f} m2 {np.median(X[:, 4]):.4f} eta {np.median(X[:, 5]):.4f}')
    print('\n   rows: clocks | start | window || RAW read-1 (plain) | ' + ' | '.join(f'{m} rung 1 / rung 2' for m in G.MODELS))
    for s in ('one', 'two'):
        for w in G.WIN:
            for ck in G.CLK:
                e = raw[(ck, s, w, 'e')]; b = raw[(ck, s, w, 'ba')]
                cols = []
                for m in G.MODELS:
                    p = np.array([RR.solve(cals[m][q]['x'], 1 - e[:, idx[q]].mean(), 1 - b[:, idx[q]].mean()) for q in EM if q in cals[m]])
                    cols.append(f'{p[:, 0].mean():.3f} / {p[:, 1].mean():.3f}')
                print(f'   {ck:<6} |{ {"one": 1, "two": 2}[s] }> {w:>3} us || {e[:, ei].mean():.4f} | ' + ' | '.join(cols))
            print()


if __name__ == '__main__':
    main()
