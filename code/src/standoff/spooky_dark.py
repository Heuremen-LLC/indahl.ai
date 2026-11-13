"""spooky_dark.py -- "four outcomes ... three that you will see". For each final outcome (L, P) = 00 / 01 / 10 / 11: TIED minus UNTIED on the clocks beside the pairs, with
widths from resampling the shots (200 draws). ENT1 - PROD2 and ENT3 - PROD2 per outcome per look k; pooled over k = 1 / 2 / 4. An outcome whose tied-untied difference
stands > 2 widths on BOTH tied arms, the same sign, is the one that stands apart. Plus the share of each outcome by look (which one goes dark)."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import spooky_four as F
S, raw, ix, own, OUT = F.S, F.raw, F.ix, F.own, F.OUT
rng = np.random.default_rng(20261007)
def hands(arm, k, side, o, rs=False):
    mX, mY = raw[('arm', arm, k, 'X')], raw[('arm', arm, k, 'Y')]
    if rs: mX = mX[rng.integers(0, len(mX), len(mX))]; mY = mY[rng.integers(0, len(mY), len(mY))]
    v = []
    for q, (sd, l, p) in own.items():
        if sd != side: continue
        sx = (mX[:, ix[l]] == int(o[0])) & (mX[:, ix[p]] == int(o[1])); sy = (mY[:, ix[l]] == int(o[0])) & (mY[:, ix[p]] == int(o[1]))
        if sx.sum() < 20 or sy.sum() < 20: continue
        v.append(abs((1 - 2 * mX[sx, ix[q]].mean()) - 1j * (1 - 2 * mY[sy, ix[q]].mean())))
    return np.median(v) if v else np.nan
for side in ('P', 'L'):
    print(f"{side}'s clocks: TIED minus UNTIED hand per outcome (pooled over k = 1 / 2 / 4), +- width")
    for o in OUT:
        cells = []
        for ent in ('ENT1', 'ENT3'):
            d = np.mean([hands(ent, k, side, o) - hands('PROD2', k, side, o) for k in [k for k in S.KS if k]])
            B = [np.mean([hands(ent, k, side, o, True) - hands('PROD2', k, side, o, True) for k in [k for k in S.KS if k]]) for _ in range(60)]
            w = np.nanstd(B); cells.append(f'{ent}-PROD2 {d:+.3f} +- {w:.3f} ({d / w:+.1f} w)')
        print(f'   {o}: ' + ' | '.join(cells))
