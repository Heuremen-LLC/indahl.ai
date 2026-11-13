"""readspooky.py -- reads SPOOKY (rigetti_spooky.py) against SPOOKY_CALL_20261007.txt. CHECK: <Y_L Z_P> per pair per arm from the check tasks. CLOCKS on the batch's own
ruler (delays): for each frame k, ENT minus PROD2 read on the clocks -- PHASE as us of laid time (angle(H_ENT / H_PROD) / turn per us), HAND as us of laid fade
(log |H_ENT / H_PROD| / fade per us) -- for P's clocks (neighbours of a P, not of any L), L's clocks (neighbours of an L, not of any P) and the far clocks. Raw.
  python readspooky.py [spooky_r1.npz]"""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('SPOOKY_SAVE', 'spooky_r1')
import rigetti_spooky as S
import rigetti_triangles as T
sys.path.insert(0, os.path.expanduser('~/bones-forge/parallax/out/qubit_fifth_run'))
from readclock_triangle import bonefish
RT = S.RT; QS = S.QS; f = sys.argv[1] if len(sys.argv) > 1 else 'spooky_r1.npz'
raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(RT.OUT, f)).items()}
ix = {q: QS.index(q) for q in QS}
print(f'{f}: pairs {S.PAIRS}')
for a in S.ARMS:
    m = raw[('check', a)]; z = 1 - 2 * m
    print(f'   CHECK {a:5}: <Y_L Z_P> per pair ' + ' '.join(f'{np.mean(z[:, ix[l]] * z[:, ix[p]]):+.3f}' for l, p in S.PAIRS) + f'  | <Z_P> ' + ' '.join(f'{np.mean(z[:, ix[p]]):+.2f}' for l, p in S.PAIRS))
H = lambda key: (1 - 2 * raw[key + ('X',)].mean(0)) - 1j * (1 - 2 * raw[key + ('Y',)].mean(0))
DL = np.array(S.DELAYS, float); h0 = H(('delay', 0)); Hd = np.array([H(('delay', d)) / h0 for d in S.DELAYS])
slope = lambda x, y: np.polyfit(np.asarray(x, float), y, 1)[0]
rate = np.array([slope(DL, np.unwrap(np.angle(Hd[:, i]))) for i in range(len(QS))]); g = np.array([slope(DL, np.log(np.clip(np.abs(Hd[:, i]), 1e-3, None))) for i in range(len(QS))])
Ls = {l for l, p in S.PAIRS}; Ps = {p for l, p in S.PAIRS}
nbL = {q for l in Ls for q in T.NB[l]} - Ls - Ps; nbP = {q for p in Ps for q in T.NB[p]} - Ls - Ps
groups = {"P's clocks": sorted((nbP - nbL) & set(S.CL)), "L's clocks": sorted((nbL - nbP) & set(S.CL)), 'far clocks': sorted(set(S.CL) - nbL - nbP)}
print('ENT minus PROD2, as the clocks read it (median us; phase | hand), frame by frame:')
for gname, qs in groups.items():
    idx = np.array([ix[q] for q in qs])
    for ent in ('ENT1', 'ENT3'):
        cells = []
        for k in S.KS:
            r = H(('arm', ent, k))[idx] / H(('arm', 'PROD2', k))[idx]
            ph = np.angle(r) / rate[idx]; hd = np.log(np.clip(np.abs(r), 1e-3, None)) / g[idx]
            cells.append(f'k{k}: {np.nanmedian(ph):+.3f} | {np.nanmedian(hd):+.3f}')
        print(f'   {gname:11} n {len(idx):2} {ent} - PROD2  ' + '   '.join(cells))
    rr = [np.nanmedian(np.abs(H(('arm', 'ENT1', k))[idx]) / np.abs(H(('arm', 'PROD2', k))[idx])) for k in S.KS]
    print(f'   {"":11}        hand ratio ENT1/PROD2 by k: ' + ' '.join(f'{x:.4f}' for x in rr) + f'  [k0: {bonefish(rr[0])}]')
