"""readlone.py -- THE LONE-LOOK READ laid against THE TAIL RUN (and the jump run for the far stretches). By hand. All bits, no cut, no fit, no verdict word.
  kept0(w) = one look after a wait w, over one look after no wait            (NO earlier look)
  kept1(w) = look 2 after a wait w, over look 1                              (ONE earlier look; three reads)
  kept1/kept0 at each wait = what the first look took, with no clock in it."""
import json, os, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data', 'fire', 'ibm_pittsburgh'); TW = ['0', '6.7', '20', '60', '300']; med = lambda v: float(np.nanmedian(v))
def frame(z, offkeys, onkeys):
    L = lambda key, i: np.asarray(z[f'{key}__L{i}']).astype(complex)
    m0 = np.concatenate([L(k, 1) for k in offkeys]).mean(0); d = np.concatenate([L(k, 1) for k in onkeys]).mean(0) - m0
    return L, (lambda x: np.real((x - m0) * np.conj(d)) / np.abs(d) ** 2)
def load(run): return json.load(open(os.path.join(D, f'run{run}_meta.json'))), np.load(os.path.join(D, f'run{run}_results.npz'))
m, z = load(31); L, al = frame(z, ['OFF|w0'], ['ON|w0']); w = np.array([[c['pre_waits_realized_us'][0] for c in m['ledger']['circuits'] if c['key'] == f'ON|w{x}'][0] for x in TW])
K0 = {s: np.array([al(L(f'{s}|w{x}', 1)).mean(0) for x in TW]) for s in ('ON', 'MID')}; K0 = {s: v / v[0] for s, v in K0.items()}
sk = lambda v: ((v - v.mean(0)) ** 3).mean(0) / v.std(0) ** 3; SK0 = {s: [med(sk(al(L(f'{s}|w{x}', 1)))) for x in TW] for s in ('ON', 'MID')}
K1 = {'ON': [], 'MID': []}
for k in (1, 2, 3):
    mt, zt = load(20 + k); Lt, alt = frame(zt, ['OFF|w0'], [f'ON|w{x}' for x in TW])
    for s in K1: K1[s].append(np.array([alt(Lt(f'{s}|w{x}', 2)).mean(0) / alt(Lt(f'{s}|w{x}', 1)).mean(0) for x in TW]))
K1 = {s: np.array(v) for s, v in K1.items()}
print(f"THE LONE LOOK ({m['start_time'][11:16]}, one read) AGAINST THE TAIL RUN (10:08 10:12 10:16): ibm_pittsburgh, all {K0['ON'].shape[1]} bits; waits (us) " + ' '.join(f'{x:.2f}' for x in w))
def stretch(K, i, j): return (w[j] - w[i]) / np.log(K[i] / K[j])
for s in ('ON', 'MID'):
    k1 = np.nanmedian(K1[s], 0)
    print(f'\n==== start {s}')
    print('                                                        none      6.7       20        60        300')
    print('  kept, NO earlier look, middle bit:                   ' + '  '.join(f'{med(x):.4f}  ' for x in K0[s]))
    for i in range(3): print(f'  kept, ONE earlier look, read {i + 1}, middle bit:           ' + '  '.join(f'{med(x):.4f}  ' for x in K1[s][i]))
    ratio = K1[s] / K0[s][None]
    for i in range(3): print(f'  ONE over NONE, bit by bit, read {i + 1}, middle bit:         ' + '  '.join(f'{med(x):.4f}  ' for x in ratio[i]))
    rr = np.nanmedian(ratio, 0); print('  ONE over NONE, each bit over the 3 reads, middle bit:  ' + '  '.join(f'{med(x):.4f}  ' for x in rr) + '\n     quarter points:                                    ' + '  '.join(f'{np.nanpercentile(x, 25):.3f}-{np.nanpercentile(x, 75):.3f}' for x in rr))
    print('     each read minus the mean of the other two:        ' + ' | '.join(' '.join(f'{med(ratio[i, j] - np.delete(ratio, i, 0)[:, j].mean(0)):+.4f}' for j in range(5)) for i in range(3)))
    print('  THE CLOCK INSIDE EACH STRETCH (us), from the middle bits:      none->6.7   6.7->20   20->60   60->300')
    p0 = np.array([med(x) for x in K0[s]]); print('     NO earlier look:                                           ' + '   '.join(f'{stretch(p0, i, i + 1):6.0f}' for i in range(4)))
    for i in range(3):
        p1 = np.array([med(x) for x in K1[s][i]]); print(f'     ONE earlier look, read {i + 1}:                                  ' + '   '.join(f'{stretch(p1, j, j + 1):6.0f}' for j in range(4)))
    print('  the same, bit by bit, each over the 60->300 clock of that bit, middle bit:')
    b0 = np.array([stretch(K0[s], i, i + 1) for i in range(4)]); print('     NO earlier look:                                           ' + '   '.join(f'{med(b0[i] / b0[3]):6.3f}' for i in range(4)))
    b1 = np.nanmedian(np.array([[stretch(K1[s][r], i, i + 1) for i in range(4)] for r in range(3)]), 0); print('     ONE earlier look (over the 3 reads):                       ' + '   '.join(f'{med(b1[i] / b1[3]):6.3f}' for i in range(4)))
    print('  LOPSIDEDNESS of the lone look along the line, by wait: ' + '  '.join(f'{x:+.3f}' for x in SK0[s]))
# the far stretches from the jump run (8 reads): 60->240, 240->300, one earlier look
ws = None; S = []
for k in range(1, 9):
    mj, zj = load(10 + k); Lj, alj = frame(zj, ['OFF|w0', 'OFF|w300'], [f'ON|w{x}' for x in (0, 60, 240, 300)]); wr = {c['key']: c['pre_waits_realized_us'][1] for c in mj['ledger']['circuits']}
    F = np.array([alj(Lj(f'ON|w{x}', 2)).mean(0) for x in (60, 240, 300)]); p = [med(x) for x in F]; a = (wr['ON|w240'] - wr['ON|w60']) / np.log(p[0] / p[1]); b = (wr['ON|w300'] - wr['ON|w240']) / np.log(p[1] / p[2]); S.append((a, b))
S = np.array(S); print(f'\n==== THE FAR STRETCHES, jump run (8 reads, ON, one earlier look, middle bits): clock 60->240: {S[:, 0].mean():.0f} +-{S[:, 0].std(ddof=1) / np.sqrt(8):.0f} us;  240->300: {S[:, 1].mean():.0f} +-{S[:, 1].std(ddof=1) / np.sqrt(8):.0f} us   (reads: ' + ' '.join(f'{x:.0f}/{y:.0f}' for x, y in S) + ')')
print('\n==== ROWS: the short-clock bits, NO earlier look, kept at none / 6.7 / 20 / 60 / 300 (ON)')
for b in (31, 36, 57, 66, 90, 137): print(f'   q{b:<4} ' + ' '.join(f'{x:+.3f}' for x in K0['ON'][:, b]))
