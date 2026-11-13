"""by_day.py -- 7 Oct 2026. fair_level1's rule (every 'value +- width', |v| 0.05-10, width > 0, deduped, unpicked) on each day's ledger sections. Null = the same
values jittered at 3 % (values stay where they physically live) and 15 %; and the tightest values (relative width < 2 %) alone at 3 %."""
import re, math, numpy as np
from patterns_of_patterns import S
SV = np.array(list(S.values())); T = open('../THIRD_RUNG_20260928.md').read()
def section_text(a, b):
    i = T.index(f'\n§{a} '); j = T.index(f'\n§{b + 1} ') if f'\n§{b + 1} ' in T else len(T); return T[i:j]
def vals(txt):
    p = {(abs(float(v)), float(w)) for v, w in re.findall(r'([+-]?\d+\.\d+)\s*\+-\s*(\d+\.\d+)', txt)}
    return [(v, w) for v, w in p if 0.05 <= v <= 10 and w > 0]
def share(vs): return np.mean([np.min(np.abs(v - SV)) / w <= 1 for v, w in vs]) if vs else float('nan')
def null(vs, sc, rng): n = [share([(v * math.exp(rng.normal(0, sc)), w) for v, w in vs]) for _ in range(300)]; return np.mean(n), np.std(n)
rng = np.random.default_rng(14)
DAYS = (('1 Oct', 77, 101), ('2-3 Oct', 102, 185), ('4 Oct', 186, 251), ('5 Oct', 252, 274), ('6 Oct', 275, 323))
for name, a, b in DAYS:
    vs = vals(section_text(a, b)); r = share(vs); m3, s3 = null(vs, .03, rng); m15, s15 = null(vs, .15, rng)
    tight = [(v, w) for v, w in vs if w / v < 0.02]; rt = share(tight); mt, st = null(tight, .03, rng) if len(tight) >= 5 else (float('nan'), float('nan'))
    print(f'{name:8} §{a}-§{b}: n {len(vs):3d} | {r:.3f} vs 3 % {m3:.3f} +- {s3:.3f} ({(r - m3) / s3:+.1f} w), 15 % {m15:.3f} ({(r - m15) / s15:+.1f} w) | '
          f'tight n {len(tight):2d}: {rt:.3f} vs 3 % {mt:.3f} +- {st:.3f} ({(rt - mt) / st if st == st and st > 0 else float("nan"):+.1f} w)')
