"""readrigetti_seal.py -- SEAL A: the emitters' |2> held 2-6 us with the other qubits at rest / F-copy / |1> at readout, three readout models, three rounds. Raw, no verdict, nothing cut.
Per round and window: rung 1 / rung 2 under each model (shared = that round's; emitter-only models from round 1), the raw read-1 fraction beside them; then ratios to the rest arm and the decay shape, all models."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import readrigetti_time as RR
import rigetti_seal as S
QS = S.RT.QS; idx = {q: QS.index(q) for q in QS}; EM = S.D.EM; ei = [idx[q] for q in EM]


def main():
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(S.OUT, 'sealA.npz')).items()}
    em = {m: RR.calib({('cal', k[1]): v for k, v in raw.items() if k[0] == f'cal_{m}'}) for m in ('em_rest', 'em_one')}
    R2 = {}
    for r in S.ROUNDS:
        cals = {'shared': RR.calib({('cal', k[1]): v for k, v in raw.items() if k[0] == 'cal_shared' and k[2] == r}), **em}
        X = np.array([cals['shared'][q]['x'] for q in EM if q in cals['shared']])
        print(f'ROUND {r}: models fitted ' + ', '.join(f'{m} {sum(1 for q in EM if q in cals[m])}/7' for m in S.MODELS) + f' | shared medians r0 {np.median(X[:, 2]):.4f} m2 {np.median(X[:, 4]):.4f} eta {np.median(X[:, 5]):.4f}')
        print('   clocks | window || RAW read-1 | ' + ' | '.join(f'{m} rung 1 / rung 2' for m in S.MODELS))
        for ck in S.CLK:
            for w in S.WIN:
                e = raw[(ck, 'two', w, 'e', r)]; b = raw[(ck, 'two', w, 'ba', r)]; cols = []
                for m in S.MODELS:
                    p = np.array([RR.solve(cals[m][q]['x'], 1 - e[:, idx[q]].mean(), 1 - b[:, idx[q]].mean()) for q in EM if q in cals[m]])
                    R2[(r, ck, w, m)] = p[:, 1].mean(); cols.append(f'{p[:, 0].mean():.3f} / {p[:, 1].mean():.3f}')
                print(f'   {ck:<6} | {w:>3} us || {e[:, ei].mean():.4f} | ' + ' | '.join(cols))
        print()
    print('RATIOS, rung 2 (per model: shared / em_rest / em_one), rounds 1 / 2 / 3:')
    for ck in ('fcopy', 'late'):
        for w in S.WIN:
            print(f'   {ck}/rest at {w:>3} us: ' + ' | '.join('/'.join(f'{R2[(r, ck, w, m)] / R2[(r, "rest", w, m)]:.3f}' for r in S.ROUNDS) for m in S.MODELS))
    for ck in S.CLK:
        print(f'   decay shape {ck:<6} 6 us / 2 us: ' + ' | '.join('/'.join(f'{R2[(r, ck, 6, m)] / R2[(r, ck, 2, m)]:.3f}' for r in S.ROUNDS) for m in S.MODELS))


if __name__ == '__main__':
    main()
