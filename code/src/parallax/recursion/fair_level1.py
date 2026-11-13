"""fair_level1.py -- 7 Oct 2026. Level 1 with NO picking: every 'value +- width' pair written in the ledger's 6 Oct sections (§288-§322), pulled by regex.
Rule written before running: take every pair; use |value|; keep 0.05 <= |value| <= 10 (the Seven's range); drop pairs whose width is zero; dedupe identical
(value, width) pairs; units are not judged (a number in us counts like any other -- the jitter carries the same rule). Score: share inside one width of a Seven
number, beside the same values jittered 15 % (300 x)."""
import re, math, numpy as np
from patterns_of_patterns import S
t = open('../THIRD_RUNG_20260928.md').read(); a = t.index('§288 '); b = t.index('§322 '); b = t.index('\n§', b + 5) if '\n§' in t[b + 5:] else len(t)
txt = t[a:b]
pairs = {(abs(float(v)), float(w)) for v, w in re.findall(r'([+-]?\d+\.\d+)\s*\+-\s*(\d+\.\d+)', txt)}
vals = [(v, w) for v, w in pairs if 0.05 <= v <= 10 and w > 0]
SV = np.array(list(S.values()))
def share(vs): return np.mean([np.min(np.abs(v - SV)) / w <= 1 for v, w in vs])
real = share(vals); rng = np.random.default_rng(12)
null = [share([(v * math.exp(rng.normal(0, 0.15)), w) for v, w in vals]) for _ in range(300)]
print(f'{len(pairs)} pairs in §288-§322; {len(vals)} kept by the rule (0.05-10, width > 0)')
print(f'UNPICKED LEVEL 1: {real:.3f} inside one width | jitter {np.mean(null):.3f} +- {np.std(null):.3f} | excess {(real - np.mean(null)) / np.std(null):+.1f} widths')
w = np.array([w for _, w in vals]); print(f'widths: median {np.median(w):.4f}; relative median {np.median([w / v for v, w in vals]):.3f}')
for lo, hi in ((0, 0.02), (0.02, 0.05), (0.05, 10)):
    sub = [(v, w) for v, w in vals if lo <= w / v < hi]
    if len(sub) >= 5:
        nl = [share([(v * math.exp(rng.normal(0, 0.15)), w) for v, w in sub]) for _ in range(300)]
        print(f'   relative width {lo:.2f}-{hi:.2f}: n {len(sub):3d} | {share(sub):.3f} vs jitter {np.mean(nl):.3f} +- {np.std(nl):.3f} | {(share(sub) - np.mean(nl)) / np.std(nl):+.1f} w')
