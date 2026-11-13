"""readpickle.py -- reads THE PICKLE (rigetti_look_pickle.py) against PICKLE_CALL_20261007.txt + _AMEND. Per clock, on the batch's own delays: turn per us (phase ruler)
and hand fade per us (hand ruler). For each looked-at state (|0> / |1> / half), tone offset (-1.5 / 0 / +1.5 MHz, and DARK = no tone when present) and k (1 / 2 / 4):
  COST per look (slope over k): phase in laid looks, hand in laid looks;
  LIGHT MINUS DARK at each k (r2): the light arm over the dark arm of the same state and k -> phase and hand cost per look of the light alone;
  HALF minus the |0>/|1> AVERAGE, per rung, per offset, per k (the superposition seat), with its width over clocks (resampled).
Rungs = looked-at qubits within 2 grid pitches (0 / 1 / 2+). Raw, no verdict.   python readpickle.py lookPickle_r1.npz | lookPickle_r2.npz"""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ['DOSE'] = '1'
import rigetti_look_dose as D
import cepheus_proximity as CP
L = D.L; QS = L.QS; CL = L.CL; slope = CP.slope; laid = 1.0 + L.LT.RING; rng = np.random.default_rng(20261007)
f = sys.argv[1]
raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(L.RT.OUT, f)).items()}
key = lambda t: tuple(None if (isinstance(x, float) and np.isnan(x)) else x for x in t)
raw = {key(k): v for k, v in raw.items()}
H = lambda k: (1 - 2 * raw[k + ('X',)].mean(0)) - 1j * (1 - 2 * raw[k + ('Y',)].mean(0))
DLS = sorted({k[1] for k in raw if k[0] == 'delay'}); DL = np.array(DLS, float); h0 = H(('delay', DLS[0]))
Hd = np.array([H(('delay', d)) / h0 for d in DLS])
rate = np.array([slope(DL, np.unwrap(np.angle(Hd[:, i]))) for i in range(len(QS))])
g = np.array([np.polyfit(DL, np.log(np.clip(np.abs(Hd[:, i]), 1e-3, None)), 1)[0] for i in range(len(QS))])
OFFS = sorted({k[2] for k in raw if k[0] == 'state'}, key=lambda o: (o is None, o if o is not None else 0)); KS = sorted({k[3] for k in raw if k[0] == 'state'})
n2 = {q: CP.sight(q)[1] for q in CL}; RUNG = [(0, 0, '0 in sight'), (1, 1, '1 in sight'), (2, 99, '2+ in sight')]
print(f'{f}: ruler on its own delays {DLS[0]}-{DLS[-1]} us ({len(DLS)}); median clock turn {np.degrees(np.median(np.abs(rate[[QS.index(q) for q in CL]]))):.1f} deg/us; offsets {OFFS}; k {KS}')
def cost(s, o):
    Hk = np.array([H(('state', s, o, k)) for k in KS]); K = np.array(KS, float)
    ph = np.array([slope(K, np.unwrap(np.angle(Hk[:, i]))) for i in range(len(QS))]) / rate / laid
    hd = np.array([slope(K, np.log(np.clip(np.abs(Hk[:, i]), 1e-3, None))) / g[i] if g[i] < 0 else np.nan for i in range(len(QS))]) / laid
    return ph, hd
C = {(s, o): cost(s, o) for s in ('0', '1', 'half') for o in OFFS}
print('COST PER LOOK (slope over k), medians: phase | hand  -- and HALF minus the |0>/|1> AVERAGE (width over clocks):')
for lo, hi, lab in RUNG:
    idx = np.array([QS.index(q) for q in CL if lo <= n2[q] <= hi])
    for o in OFFS:
        cells = []
        for j, nm in ((0, 'phase'), (1, 'hand')):
            v = {s: C[(s, o)][j][idx] for s in ('0', '1', 'half')}; dev = v['half'] - (v['0'] + v['1']) / 2
            w = np.nanstd([np.nanmedian(dev[rng.integers(0, len(dev), len(dev))]) for _ in range(200)])
            cells.append(f'{nm} 0 {np.nanmedian(v["0"]):.3f} 1 {np.nanmedian(v["1"]):.3f} half {np.nanmedian(v["half"]):.3f} | half-avg {np.nanmedian(dev):+.3f}+-{w:.3f}')
        print(f'   {lab:11} n {len(idx):2} tone {"DARK" if o is None else f"{o / 1e6:+.1f} MHz":9} | ' + ' || '.join(cells))
if None in OFFS:
    print('LIGHT MINUS DARK at each k (cost per look of the light alone), HALF minus AVERAGE by k -- the TIME seat:')
    for lo, hi, lab in RUNG:
        idx = np.array([QS.index(q) for q in CL if lo <= n2[q] <= hi])
        for o in [o for o in OFFS if o is not None]:
            line = []
            for k in KS:
                r = {s: H(('state', s, o, k)) / H(('state', s, None, k)) for s in ('0', '1', 'half')}
                hd = {s: np.log(np.clip(np.abs(r[s][idx]), 1e-3, None)) / g[idx] / k / laid for s in r}
                ph = {s: np.angle(r[s][idx]) / rate[idx] / k / laid for s in r}
                dh = hd['half'] - (hd['0'] + hd['1']) / 2; dp = ph['half'] - (ph['0'] + ph['1']) / 2
                line.append(f'k{k}: hand 0/1/half {np.nanmedian(hd["0"]):+.3f}/{np.nanmedian(hd["1"]):+.3f}/{np.nanmedian(hd["half"]):+.3f} half-avg {np.nanmedian(dh):+.3f}; phase half-avg {np.nanmedian(dp):+.3f}')
            print(f'   {lab:11} {o / 1e6:+.1f} MHz | ' + ' || '.join(line))
