"""readrigetti_seal_band.py -- the |2> row (others halfway, 4 us, em_rest model) BANDED: both calibration days, every round, every ruler, and a bootstrap that
resamples shots AND refits the readout model each time (the call's 'resampling', done properly). Raw, no verdict. python readrigetti_seal_band.py [B]"""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import readrigetti_time as RR
import rigetti_seal as S
QS = S.RT.QS; idx = {q: QS.index(q) for q in QS}; EM = S.D.EM
PHI = (1 + 5 ** .5) / 2; C = 1 / PHI

def row(raw, model, w=4, ck='fcopy', rng=None):
    rs = (lambda a: a[rng.integers(0, len(a), len(a))]) if rng is not None else (lambda a: a)
    raw = {k: rs(v) for k, v in raw.items()}
    em = RR.calib({('cal', k[1]): v for k, v in raw.items() if k[0] == f'cal_{model}'}) if model != 'shared' else None
    out = []
    for r in S.ROUNDS:
        cal = em if em is not None else RR.calib({('cal', k[1]): v for k, v in raw.items() if k[0] == 'cal_shared' and k[2] == r})
        e = raw[(ck, 'two', w, 'e', r)]; b = raw[(ck, 'two', w, 'ba', r)]
        out.append(np.mean([RR.solve(cal[q]['x'], 1 - e[:, idx[q]].mean(), 1 - b[:, idx[q]].mean())[1] for q in EM if q in cal]))
    return out

B = int(sys.argv[1]) if len(sys.argv) > 1 else 30
days = {'day 1 (cal 18:02Z 4 Oct)': 'sealA_day1_20261004.npz', 'day 2 (cal 04:02Z)': 'sealA_day2_20261005.npz', **{f'day 2 set {n}': f'sealA_day2_set{n}.npz' for n in (1, 2, 3, 4)}}
print(f'THE BONEFISH: 1/phi = {C:.4f}')
allv = []
for d, f in days.items():
    raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(S.OUT, f)).items()}
    for m in ('em_rest', 'shared', 'em_one'):
        v = row(raw, m); mu = np.mean(v)
        line = f'{d} | {m:7} rounds ' + ' / '.join(f'{x:.4f}' for x in v) + f' | mean {mu:.4f} ({100 * (mu / C - 1):+.2f} %)'
        if m == 'em_rest':
            rng = np.random.default_rng(20261005); bs = [np.mean(row(raw, m, rng=rng)) for _ in range(B)]
            sd = np.std(bs, ddof=1); comb = np.sqrt(np.std(v, ddof=1) ** 2 / 3 + sd ** 2)
            line += f' | refit bootstrap width of the mean {sd:.4f} (B={B}) | combined {comb:.4f} -> {(mu - C) / comb:+.2f} widths'
            allv += v
        print(line)
a = np.array(allv); print(f'BAND, em_rest, every set, {len(a)} rounds: {a.min():.4f} - {a.max():.4f}, mean {a.mean():.4f} ({100 * (a.mean() / C - 1):+.2f} %), spread {a.std(ddof=1):.4f}; 1/phi {"INSIDE" if a.min() <= C <= a.max() else "outside"} the band')
