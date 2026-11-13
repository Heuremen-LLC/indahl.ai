"""readpunch.py -- reads THE PUNCH (rigetti_look_punch.py) against CROSSTALK_PUNCH_CALL_20261007.txt. Per clock: turn per us over the delays (the ruler); STATES: phase
per look (slope over k = 1-4 of the unwrapped turn, / turn per us) and hand per look (log hand / the clock's own hand-fade per us), with the looked-at qubits in
|0>, |1>, half-way; ECHO: the echoed looks minus the echoed laid time (same pi, same laid us), in us per look on the clock's ruler. Rungs = looked-at qubits within
2 grid pitches; centre clocks 13 / 44 / 56 one by one. Raw, no verdict.   python readpunch.py [lookPunch_r1.npz]"""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('P2R_SAVE', 'lookPunch_r1'); os.environ['DOSE'] = '1'
import rigetti_look_punch as P
import cepheus_proximity as CP
L = P.L; QS = P.QS; slope = CP.slope; DL = np.array(P.DELAYS, float); laid = P.T + L.LT.RING
f = sys.argv[1] if len(sys.argv) > 1 else 'lookPunch_r1.npz'
raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(L.RT.OUT, f)).items()}
H = lambda key: (1 - 2 * raw[key + ('X',)].mean(0)) - 1j * (1 - 2 * raw[key + ('Y',)].mean(0))
DLS = sorted({k[2] for k in raw if k[0] == 'delay'}); DL = np.array(DLS, float)
h0 = H(('delay', '1', DLS[0])); Hd = np.array([H(('delay', '1', d)) / h0 for d in DLS])   # 7 Oct: reference = the batch's own first delay
rate = np.array([slope(DL, np.unwrap(np.angle(Hd[:, i]))) for i in range(len(QS))])
g = np.array([np.polyfit(DL, np.log(np.clip(np.abs(Hd[:, i]), 1e-3, None)), 1)[0] for i in range(len(QS))])
K = np.array(P.KS, float); ST = {}
for s in [s for s in P.STATES if ('state', s, 1, 'X') in raw]:
    Hk = np.array([H(('state', s, k)) for k in P.KS])
    ph = np.array([slope(K, np.unwrap(np.angle(Hk[:, i]))) for i in range(len(QS))]) / rate / laid
    hd = np.array([slope(K, np.log(np.clip(np.abs(Hk[:, i]), 1e-3, None))) / g[i] if g[i] < 0 else np.nan for i in range(len(QS))]) / laid
    ST[s] = (ph, hd)
EC = {}
for k in [k for k in P.ECHO_KS if ('echo', 'look', k, 'X') in raw]:
    a = np.angle(H(('echo', 'look', k)) / H(('echo', 'laid', k))); EC[k] = a / np.abs(rate) / k     # us per look the echo leaves
    EC[(k, 'hand')] = np.log(np.clip(np.abs(H(('echo', 'look', k))) / np.abs(H(('echo', 'laid', k))), 1e-3, None)) / g / k / laid
n2 = {q: CP.sight(q)[1] for q in P.CL}
print(f'{f}: looked-at {P.EM}; laid look {laid} us; median clock turn {np.degrees(np.median(np.abs(rate[[QS.index(q) for q in P.CL]]))):.1f} deg/us')
for lo, hi, lab in ((0, 0, '0 in sight'), (1, 1, '1 in sight'), (2, 2, '2 in sight'), (3, 3, '3 in sight'), (4, 99, '4+ in sight')):
    idx = np.array([QS.index(q) for q in P.CL if lo <= n2[q] <= hi])
    if len(idx) < 1: continue
    st = ' | '.join(f'{s}: ph {np.nanmedian(ST[s][0][idx]):.3f} hand {np.nanmedian(ST[s][1][idx]):.3f}' for s in ST) or '(states not in this file)'
    ec = ' | '.join(f'echo k{k}: {np.nanmedian(EC[k][idx]):+.3f} us/look, hand {np.nanmedian(EC[(k, "hand")][idx]):+.3f}' for k in P.ECHO_KS if k in EC)
    print(f'   {lab:11} n {len(idx):3} | STATES W/laid {st} || {ec}')
print('   CENTRE CLOCKS:')
for q in (13, 44, 56):
    i = QS.index(q)
    print(f'     clock {q} ({n2[q]} in sight) | ' + ' | '.join(f'{s}: ph {ST[s][0][i]:.3f} hand {ST[s][1][i]:.3f}' for s in ST) + ' || ' + ' | '.join(f'echo k{k} {EC[k][i]:+.3f} us/look' for k in P.ECHO_KS if k in EC))
