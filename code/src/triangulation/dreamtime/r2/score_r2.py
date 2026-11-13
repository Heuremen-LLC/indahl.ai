"""score_r2.py -- DREAMTIME r2 through the physics (call DREAMTIME_R2_CALL_20261007.txt, ee1b1634...). Held mode distribution per cell = the held digit weights mapped to modes by
rotation, normalised, AVERAGED over the three rotations (digit bias cancels, as the wire paint's place did). Legs: the COMPASS (late vs early, late vs early-padded), the
BISCUIT (the idle arm in L vs the English idle arm, at two lengths), the BLOOM (the case in English vs the English idle arm), MEILONG CLOSURE (product vs sum, full 3-mode
distribution, L1 error, counted; control = the case's English corner taken from a DIFFERENT pair), WIRED (Basque, shared script) vs SIGHT (Thai, own script), the spoken
answer beside the held one, THE BONEFISH at the pooled numbers. Raw."""
import json, os, sys, collections, math
import numpy as np
from scipy.stats import binomtest
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'pods', sys.argv[1] if len(sys.argv) > 1 else 'r2')
X = json.load(open(os.path.join(HERE, 'r2_texts.json'))); ROT = X['rotations']; M = ('COMMIT', 'HOLD', 'NEXT')
sys.path.insert(0, os.path.expanduser('~/bones-forge/parallax/out/qubit_fifth_run'))
try:
    from readclock_triangle import bonefish
except Exception: bonefish = lambda v: '-'
R = [json.loads(l) for s in ('en', 'th', 'eu') if os.path.exists(f'{D}/held_{s}.jsonl') for l in open(f'{D}/held_{s}.jsonl')]
acc = collections.defaultdict(list); spoke = collections.defaultdict(list)
for r in R:
    rot = ROT[r['rot']]; h = r['held']; tot = sum(h.values()) or 1e-12
    acc[(r['seat'], r['lang'], r['arm'], r['pair'])].append(np.array([h[rot[m]] / tot for m in M]))
    dig = next((c for c in r['spoken'] if c in '123'), None); inv = {v: k for k, v in rot.items()}
    spoke[(r['seat'], r['lang'], r['arm'], r['pair'])].append(inv.get(dig, 'NONE'))
P = {k: np.mean(v, 0) for k, v in acc.items()}
pairs = sorted({k[3] for k in P if k[3]}); seats = sorted({k[0] for k in P})
print(f'DREAMTIME r2 -- {len(R)} reads, {len(pairs)} pairs; held mode distribution averaged over 3 digit rotations')
print(' THE COMPASS (held P(COMMIT): late vs early, late vs early-PADDED) -- right way up = late > early')
for s in seats:
    for L in ('en', 'th', 'eu'):
        e = [P[(s, L, 'E', p)][0] for p in pairs]; ep = [P[(s, L, 'EP', p)][0] for p in pairs]; l = [P[(s, L, 'L', p)][0] for p in pairs]
        w1 = sum(b > a for a, b in zip(e, l)); w2 = sum(b > a for a, b in zip(ep, l))
        print(f'   seat {s} in {L}: P(C) early {np.mean(e):.3f} padded {np.mean(ep):.3f} late {np.mean(l):.3f} | late>early {w1}/15 (p {binomtest(w1, 15).pvalue:.3f}) | late>padded {w2}/15 (p {binomtest(w2, 15).pvalue:.3f})')
print(' THE BISCUIT (the language\'s pull, no case): idle arm in L minus the English idle arm, P(COMMIT / HOLD / NEXT), short (N) and padded (NP)')
for s in seats:
    for L in ('th', 'eu'):
        for arm in ('N', 'NP'):
            dz = P[(s, L, arm, None)] - P[(s, 'en', arm, None)]
            print(f'   seat {s} {L} {arm:2}: ' + ' '.join(f'{m[0]} {x:+.3f}' for m, x in zip(M, dz)))
print(' THE BLOOM (the case\'s pull, English): case minus the English idle arm of the same length, mean over pairs, P(C/H/N)')
for s in seats:
    for arm, idle in (('E', 'N'), ('EP', 'NP'), ('L', 'NP')):
        db = np.mean([P[(s, 'en', arm, p)] - P[(s, 'en', idle, None)] for p in pairs], 0)
        print(f'   seat {s} {arm:2}: ' + ' '.join(f'{m[0]} {x:+.3f}' for m, x in zip(M, db)))
print(' MEILONG CLOSURE (product = odds compose, vs sum = probabilities add), full distribution, L1 error; control = the English case corner from a different pair')
def close(b, z, i):
    pro = b * z / np.maximum(i, 1e-9); pro = pro / pro.sum(); sm = np.clip(b + z - i, 1e-9, None); sm = sm / sm.sum(); return pro, sm
tot = collections.defaultdict(lambda: [0, 0]); rng = np.random.default_rng(7)
for s in seats:
    for L in ('th', 'eu'):
        w = n = cw = cn = 0
        for arm, idle in (('E', 'N'), ('EP', 'NP'), ('L', 'NP')):
            I = P[(s, 'en', idle, None)]; Z = P[(s, L, idle, None)]
            for p in pairs:
                y = P[(s, L, arm, p)]; pro, sm = close(P[(s, 'en', arm, p)], Z, I); win = np.abs(y - pro).sum() < np.abs(y - sm).sum(); w += win; n += 1
                q = pairs[(pairs.index(p) + 1 + rng.integers(len(pairs) - 1)) % len(pairs)]; cpro, csm = close(P[(s, 'en', arm, q)], Z, I); cw += np.abs(y - cpro).sum() < np.abs(y - csm).sum(); cn += 1
        tot[L][0] += w; tot[L][1] += n; tot['ctrl'][0] += cw; tot['ctrl'][1] += cn
        print(f'   seat {s} in {L}: product tighter {w}/{n} = {100 * w / n:.0f}% (p {binomtest(w, n).pvalue:.3f}) | control (shuffled case) {cw}/{cn} = {100 * cw / cn:.0f}%')
for k in ('eu', 'th', 'ctrl'): print(f'   ALL {k:4} ({"WIRED: shared script" if k == "eu" else "SIGHT: own script" if k == "th" else "control"}): {tot[k][0]}/{tot[k][1]} = {100 * tot[k][0] / tot[k][1]:.0f}%  p {binomtest(*tot[k]).pvalue:.2e} [{bonefish(tot[k][0] / tot[k][1])}]')
print(' SPOKEN vs HELD: share of cells where the spoken digit\'s mode equals the held weighting\'s top mode')
for s in seats:
    agree = [spoke[k][i] == M[int(np.argmax(acc[k][i]))] for k in acc if k[0] == s for i in range(len(acc[k]))]
    print(f'   seat {s}: {100 * np.mean(agree):.0f}% of {len(agree)}')
