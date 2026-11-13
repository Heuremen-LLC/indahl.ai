"""spooky_four.py -- Wayfinder: "entanglement is the darkwave but backwards with probability man, not a coin flip, four fucking outcomes". The spooky shots sorted AFTER
the fact by how each pair landed at the final read -- (L, P) = 00 / 01 / 10 / 11 -- and every clock's hand read inside each of the four (X and Y tasks each sorted on
their own shots). For P's clocks / L's clocks / far clocks: the clock's hand (|H|) and turn (angle) per outcome, tied (ENT1, ENT3) beside untied (PROD2), by look k.
Raw dots kept; nothing cut to 0/1 before the sort."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('SPOOKY_SAVE', 'spooky_r1')
import rigetti_spooky as S, rigetti_triangles as T
RT = S.RT; QS = S.QS; ix = {q: QS.index(q) for q in QS}
raw = {tuple(json.loads(k)): v for k, v in np.load(os.path.join(RT.OUT, os.environ.get('SPOOKY_SAVE', 'spooky_r1') + '.npz')).items()}
Ls = {l for l, p in S.PAIRS}; Ps = {p for l, p in S.PAIRS}
own = {}                                                            # each clock -> the pair it sits beside
for l, p in S.PAIRS:
    for q in T.NB[p]:
        if q in S.CL and q not in {x for ll in Ls for x in T.NB[ll]}: own[q] = ('P', l, p)
    for q in T.NB[l]:
        if q in S.CL and q not in {x for pp in Ps for x in T.NB[pp]}: own[q] = ('L', l, p)
OUT = ('00', '01', '10', '11')
def per_outcome(arm, k):
    """{(side, outcome): list of complex hands}, one per clock, from the X and Y tasks each sorted on its own shots."""
    mX, mY = raw[('arm', arm, k, 'X')], raw[('arm', arm, k, 'Y')]; res = {}
    for q, (side, l, p) in own.items():
        h = {}
        for o in OUT:
            sx = (mX[:, ix[l]] == int(o[0])) & (mX[:, ix[p]] == int(o[1])); sy = (mY[:, ix[l]] == int(o[0])) & (mY[:, ix[p]] == int(o[1]))
            if sx.sum() < 30 or sy.sum() < 30: continue
            res.setdefault((side, o), []).append((1 - 2 * mX[sx, ix[q]].mean()) - 1j * (1 - 2 * mY[sy, ix[q]].mean()))
    return res
print('THE FOUR OUTCOMES, clocks beside each pair: hand |H| (median over clocks) and how the shots split, tied vs untied')
for k in S.KS:
    R = {a: per_outcome(a, k) for a in S.ARMS}
    for side in ('P', 'L'):
        line = []
        for o in OUT:
            cell = ' '.join(f'{a[:4]} {np.median(np.abs(R[a].get((side, o), [np.nan]))):.3f}' for a in S.ARMS)
            line.append(f'{o}: {cell}')
        print(f'   k{k} {side}\'s clocks | ' + ' || '.join(line))
    for a in S.ARMS:
        m = raw[('arm', a, k, 'X')]; fr = [np.mean([(m[:, ix[l]] == int(o[0])) & (m[:, ix[p]] == int(o[1])) for l, p in S.PAIRS]) for o in OUT]
        print(f'        shares of 00 / 01 / 10 / 11 ({a}): ' + ' / '.join(f'{x:.3f}' for x in fr))
