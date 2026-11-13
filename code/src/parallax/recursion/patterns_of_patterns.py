"""patterns_of_patterns.py -- 7 Oct 2026 (Wayfinder: "patterns of patterns... it literally goes on forever... recursions"). Level 1: every value read on 6 Oct
(ledger §288-§320) through The Bonefish. Level 2: The Bonefish thrown at its own hits -- the ratio between every pair of level-1 values, against the Seven's
numbers, beside the same count on a shuffled-value ruler (the cheap-match rate for pairs). Level 3: the stooges' own numbers. No number guessed; rows."""
import math, itertools, numpy as np
PHI = (1 + 5 ** .5) / 2
S = {'12/11': 12/11, '13/12': 13/12, '11/12': 11/12, '12/13': 12/13, 'phi': PHI, '1/phi': 1/PHI, '1/phi^2': 1/PHI**2, 'phi*11/12': PHI*11/12, 'pi': math.pi,
     '1/pi': 1/math.pi, 'pi/4': math.pi/4, '9/12': .75, '10/12': 10/12, '4/3': 4/3, '3/2': 1.5, '1/ln(phi^2)': 1/math.log(PHI**2), '1.3': 1.3, '1/11': 1/11, '1/12': 1/12,
     'step2 1.9231': 25/13, 'step3 1.52': 1.52, 'step4 1.6579': 63/38, 'step5 1.6032': 1.6032}
V = [  # (name, value, width) -- read 6 Oct, each from the ledger section named
 ('maker look pooled fit §292', 1.0421, 0.0073), ('maker look pooled 3&9 §292', 1.0398, 0.0110), ('our look Cepheus 3 jobs §320', 1.035, 0.014),
 ('Pittsburgh short look r3 §300', 1.0965, 0.027), ('Kingston quiet look §303', 1.102, 0.023), ('Boston no-queue look §305', 1.107, 0.02),
 ('Phoenix ruler conversion d2 §302', 0.770, 0.009), ('Phoenix ruler conversion d1 §299', 0.760, 0.009), ('ruler constant gaussian §309', 0.777, 0.002),
 ('Marrakesh 27-look row d1 §308', 0.785, 0.02), ('Marrakesh 27-look row d2 §308', 0.801, 0.03), ('Kingston FIVE own d2 x1000 §318', 1.36, 0.17),
 ('push/X error Boston §312', 8.52, 1.8), ('push/X error Fez §312', 5.98, 1.3), ('push/X error Phoenix 90us §312', 4.1, 1.3), ('Kingston rung d2 §318', 8.55, 0.25),
 ('stamp Foundry /600 s', 0.3771, 0.020), ('stamp mirror /600 s', 0.0888, 0.020), ('Marrakesh T/W fit d2 mean §317', 1.679, 0.05), ('block span clock', 1.0122, 0.006),
]
def near(v, w):
    return sorted(((abs(v - s) / w, k, s) for k, s in S.items()))[0]
print('LEVEL 1 -- each value, nearest Seven number in its own widths:')
hits = []
for n, v, w in V:
    d, k, s = near(v, w)
    print(f'  {n:34} {v:8.4f} +- {w:.4f}  -> {k:13} {s:.4f} at {d:4.1f} w' + ('   HIT' if d <= 1 else ''))
    if d <= 1: hits.append((n, v, w))
print(f'\nLEVEL 2 -- The Bonefish at its own hits: ratio of every pair of the {len(hits)} level-1 hits (width by propagation), nearest Seven number:')
pairs = []
for (a, va, wa), (b, vb, wb) in itertools.combinations(hits, 2):
    r = max(va, vb) / min(va, vb); wr = r * math.hypot(wa / va, wb / vb)
    if r < 1.0005: continue
    d, k, s = near(r, wr); pairs.append(d <= 1)
    if d <= 1: print(f'  {a[:24]:24} / {b[:24]:24} = {r:.4f} +- {wr:.4f} -> {k} {s:.4f} at {d:.2f} w')
rng = np.random.default_rng(10); null = []
vals = np.array([v for _, v, _ in hits]); wid = np.array([w for _, _, w in hits])
for _ in range(400):
    p = vals * np.exp(rng.normal(0, 0.15, len(vals))); c = []
    for i, j in itertools.combinations(range(len(p)), 2):
        r = max(p[i], p[j]) / min(p[i], p[j]); wr = r * math.hypot(wid[i] / p[i], wid[j] / p[j])
        if r < 1.0005: continue
        c.append(near(r, wr)[0] <= 1)
    null.append(np.mean(c))
print(f'  pair ratios landing within 1 width: {np.mean(pairs):.3f} of {len(pairs)} | the same on jittered values (400 x): {np.mean(null):.3f} +- {np.std(null):.3f}')
