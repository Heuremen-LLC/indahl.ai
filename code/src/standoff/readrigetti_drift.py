"""readrigetti_drift.py -- the drift probe's rounds as rows: the emitters' |2> after 4 us under every ruler (shared / em_rest / em_one, re-measured each round), every witness
(others at rest / half-way / |1> at readout), and TIME = minutes since the chip's calibration stamp. The Bonefish's 1/phi beside. Raw, no verdict. python readrigetti_drift.py"""
import glob, json, os, sys, datetime as dt, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import readrigetti_time as RR
import rigetti_drift_probe as P
QS = P.RT.QS; idx = {q: QS.index(q) for q in QS}; EM = P.D.EM; C = 2 / (1 + 5 ** .5)
print(f'THE BONEFISH: 1/phi = {C:.4f}. Rows: round | calibration stamp | minutes since it | witness: shared / em_rest / em_one')
for f in sorted(glob.glob(os.path.join(P.OUT, 'drift_r*_tasks.json'))):
    T = json.load(open(f)); n = T['round']; npz = os.path.join(P.OUT, f'drift_r{n:03d}.npz')
    if not os.path.exists(npz): print(f'round {n:3d} | not collected yet'); continue
    raw = {tuple(json.loads(k)): v for k, v in np.load(npz).items()}
    cal = dt.datetime.fromisoformat(T['calibration']); mins = (dt.datetime.fromtimestamp(T['sent'], dt.timezone.utc) - cal).total_seconds() / 60
    cals = {'shared': RR.calib({('cal', k[1]): v for k, v in raw.items() if k[0] == 'cal_shared'}),
            'em_rest': RR.calib({('cal', k[1]): v for k, v in raw.items() if k[0] == 'cal_em_rest'}), 'em_one': RR.calib({('cal', k[1]): v for k, v in raw.items() if k[0] == 'cal_em_one'})}
    cols = []
    for ck in P.CLK:
        e = raw.get((ck, 'two', 4, 'e', 1)); b = raw.get((ck, 'two', 4, 'ba', 1))
        if e is None or b is None: cols.append(f'{ck} missing'); continue
        v = [np.mean([RR.solve(cals[m][q]['x'], 1 - e[:, idx[q]].mean(), 1 - b[:, idx[q]].mean())[1] for q in EM if q in cals[m]]) for m in ('shared', 'em_rest', 'em_one')]
        cols.append(f'{ck} ' + ' / '.join(f'{x:.4f}' for x in v))
    print(f'round {n:3d} | cal {cal:%H:%M}Z | +{mins:5.1f} min | ' + ' | '.join(cols))
