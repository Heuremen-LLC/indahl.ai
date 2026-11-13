"""readcube.py -- THE JUMP RUN AS A CUBE (place on the chip x place on the chip x time), not flattened. By hand, outside the freeze. No guess written, no verdict word.
A NODE here = a CROSSING: the step between two reads where a bit goes from its long clock to its short one, or back. Each has a place and a moment.
Reads data/reads/jump_run.json (written by readjump.py) and data/reads/layout_156_family.json (the chip family's wiring, from a local snapshot; the chip was not asked).
Three looks at where the crossings fall: IN TIME, IN SPACE (by wiring distance), IN CLOCK. The second ruler throughout is MID (its own circuits).
  python readcube.py [--cut 4]"""
import argparse, json, os
from collections import deque
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RD = os.path.join(HERE, 'data', 'reads')
ap = argparse.ArgumentParser(); ap.add_argument('--cut', type=float, default=4.0); a = ap.parse_args()
J = json.load(open(os.path.join(RD, 'jump_run.json'))); lay = json.load(open(os.path.join(RD, 'layout_156_family.json')))
nbr = {int(k): v for k, v in lay['neighbours'].items()}; rows = {r['bit']: r for r in J['rows']}; bits = sorted(rows); n = len(J['reads']); times = [t[11:16] for t in J['times']]


def dist_from(s):
    d = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        for v in nbr.get(u, []):
            if v not in d: d[v] = d[u] + 1; q.append(v)
    return d


DIST = {b: dist_from(b) for b in bits}
T = np.array([rows[b]['tau'] for b in bits]); W = np.array([rows[b]['w'] for b in bits]); TM = np.array([rows[b]['tauMID'] for b in bits])
jump = [b for b in bits if rows[b]['chi1'] > a.cut and 'labels' in rows[b]]
print(f'THE CUBE: {len(bits)} readable bits x {n} reads ({" ".join(times)}); bits that do not sit on one level (above {a.cut:g}): {len(jump)}')

# ---- 1. IN TIME
cross = {b: [i for i in range(n - 1) if rows[b]['labels'][i] != rows[b]['labels'][i + 1]] for b in jump}
per = [sum(1 for b in jump if i in cross[b]) for i in range(n - 1)]; down = [sum(1 for b in jump if i in cross[b] and rows[b]['labels'][i] == 'L') for i in range(n - 1)]
short_now = [sum(1 for b in jump if rows[b]['labels'][i] == 'S') for i in range(n)]
print('\n-- 1. IN TIME')
print('   bits in their SHORT clock at each read:        ' + ' '.join(f'{x:4d}' for x in short_now))
print('   crossings in each step between reads:             ' + ' '.join(f'{x:4d}' for x in per) + f'    (all: {sum(per)})')
print('   of those, long -> short:                          ' + ' '.join(f'{x:4d}' for x in down))
nc = [len(cross[b]) for b in jump]; print('   crossings per bit: ' + ' '.join(f'{k}x:{nc.count(k)}' for k in sorted(set(nc))))

# ---- 2. IN SPACE
print('\n-- 2. IN SPACE (wiring distance between two bits: 1 = wired neighbours)')
ev = [(b, i) for b in jump for i in cross[b]]
for label, same in (('crossing in the SAME step', lambda i, j: i == j), ('crossing ONE step apart', lambda i, j: abs(i - j) == 1)):
    print(f'   pairs of crossings on two different bits, {label}, by distance:')
    cnt, tot = {}, {}
    for x in range(len(ev)):
        for y in range(x + 1, len(ev)):
            (b1, i1), (b2, i2) = ev[x], ev[y]
            if b1 == b2: continue
            d = min(DIST[b1].get(b2, 99), 6); tot[d] = tot.get(d, 0) + 1
            if same(i1, i2): cnt[d] = cnt.get(d, 0) + 1
    print('      distance:            ' + ' '.join(f'{("6+" if d == 6 else d):>7}' for d in sorted(tot)))
    print('      pairs like that:     ' + ' '.join(f'{cnt.get(d, 0):>7}' for d in sorted(tot)))
    print('      of all pairs there:  ' + ' '.join(f'{tot[d]:>7}' for d in sorted(tot)))
    print('      share:               ' + ' '.join(f'{cnt.get(d, 0) / tot[d]:>7.3f}' for d in sorted(tot)))
# every bit, no cut: do two bits' clocks move together across the reads, by distance? ON with ON, and ON of one with MID of the other (second ruler)
Z = (T - T.mean(1, keepdims=True)) / W.mean(1, keepdims=True); ZM = (TM - TM.mean(1, keepdims=True)) / TM.std(1, keepdims=True).clip(1e-9)
Zs = Z / np.sqrt((Z ** 2).sum(1, keepdims=True)).clip(1e-9); ZMs = (ZM - ZM.mean(1, keepdims=True)); ZMs = ZMs / np.sqrt((ZMs ** 2).sum(1, keepdims=True)).clip(1e-9)
C = Zs @ Zs.T; CM = Zs @ ZMs.T; by, byM = {}, {}
for x, b1 in enumerate(bits):
    for y, b2 in enumerate(bits):
        if y <= x: continue
        d = min(DIST[b1].get(b2, 99), 6); by.setdefault(d, []).append(C[x, y]); byM.setdefault(d, []).append((CM[x, y] + CM[y, x]) / 2)
print('   EVERY readable bit, no cut: how alike two bits\' clock-over-time shapes are (-1..1), by distance. Width = spread / root(pairs).')
print('      distance:                 ' + ' '.join(f'{("6+" if d == 6 else d):>8}' for d in sorted(by)))
print('      pairs:                    ' + ' '.join(f'{len(by[d]):>8}' for d in sorted(by)))
print('      ON with ON, mean:         ' + ' '.join(f'{np.mean(by[d]):>+8.3f}' for d in sorted(by)))
print('      width:                    ' + ' '.join(f'{np.std(by[d]) / np.sqrt(len(by[d])):>8.3f}' for d in sorted(by)))
print('      ON with the other\'s MID:  ' + ' '.join(f'{np.mean(byM[d]):>+8.3f}' for d in sorted(byM)))
own = np.diag(CM); print(f'      a bit\'s ON with its OWN MID (the two rulers on one bit): mean {own.mean():+.3f}, middle {np.median(own):+.3f}; among the jumping bits: {np.mean([own[bits.index(b)] for b in jump]) if jump else float("nan"):+.3f}')
# the whole chip breathing together? first shared shape across all bits
u, s, vt = np.linalg.svd(Zs, full_matrices=False); print('   shared shapes across ALL bits (share of all the movement carried by the 1st, 2nd, 3rd): ' + ' '.join(f'{x:.3f}' for x in (s ** 2 / (s ** 2).sum())[:3]) + f'   (even split would be {1 / (n - 1):.3f} each)')
print('      first shared shape over the reads: ' + ' '.join(f'{x:+.2f}' for x in vt[0]))

# ---- 3. IN CLOCK
print('\n-- 3. IN CLOCK: the two levels of each jumping bit (us), ON; and where the levels of ALL jumping bits sit')
if jump:
    S = np.array([rows[b]['short'] for b in jump]); L = np.array([rows[b]['long'] for b in jump])
    print(f'   long levels:  middle {np.median(L):.0f}, quarter points {np.percentile(L, 25):.0f} {np.percentile(L, 75):.0f}    short levels: middle {np.median(S):.0f}, quarter points {np.percentile(S, 25):.0f} {np.percentile(S, 75):.0f}')
    print(f'   long minus short: middle {np.median(L - S):.0f} us;  short / long: middle {np.median(S / L):.3f}  (the stone: 260/365 = 0.712, 13/20 = 0.650; 105/365 = 0.288 is the difference over the wave)')
    print(f'   (long - short) / long: middle {np.median((L - S) / L):.3f}')
    c = np.corrcoef(L, S)[0, 1]; print(f'   do long and short go together bit to bit? correlation {c:+.2f};  straight line short = a x long: a = {np.sum(S * L) / np.sum(L * L):.3f}')
