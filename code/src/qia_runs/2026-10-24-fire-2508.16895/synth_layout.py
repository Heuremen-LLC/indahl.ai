"""synth_layout.py -- planted worlds for analyze_layout.gap_reading (binomial, 1000 shots, one copy per arm): NULL (L2 = L1 = 0.13 x exact), GAP (L2 = 0.85 x exact, L1 = 0.13 x exact)."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from swaprun import *; from analyze_layout import gap_reading
P = select(curves()); ex = np.array([p['F'] for p in P]); rng = np.random.default_rng(24102026)
draw = lambda t: 2 * rng.binomial(SHOTS, (1 + np.clip(t, -1, 1)) / 2) / SHOTS - 1
for name, k1, k2, n in (('NULL both arms 0.13 x exact', 0.13, 0.13, 400), ('NULL both arms 0.85 x exact', 0.85, 0.85, 400), ('GAP L1 0.13, L2 0.85', 0.13, 0.85, 100), ('SMALL GAP L1 0.80, L2 0.85', 0.80, 0.85, 100)):
    t = {}
    for _ in range(n): o = gap_reading(draw(k1 * ex), draw(k2 * ex), P)['outcome']; t[o] = t.get(o, 0) + 1
    print(f'{name:<28} ({n} runs): {t}')
