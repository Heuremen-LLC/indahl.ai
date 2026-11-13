"""levels.py -- 7 Oct 2026. The recursion, level by level, each level beside its own jitter (Wayfinder: "go for level three and take the three stooges
bonefished with you"). Level 1 = the values (6 Oct reads + the four miner stooges' speeds); level n+1 = every ratio between two level-n HITS, in its propagated
width. At each level: the share of values inside one width of a Seven number, beside the same pipeline run on level-1 values jittered 15 % (300 x)."""
import math, itertools, numpy as np
from patterns_of_patterns import S, V
STOOGES = [('moe/shep speed', 0.9800, 0.0020), ('larry/shep speed', 0.9881, 0.0026), ('curly/shep speed', 0.9220, 0.0032)]
L1 = V + STOOGES
SV = np.array(list(S.values())); SK = list(S.keys())
def hit(v, w): d = np.abs(v - SV) / w; i = int(np.argmin(d)); return d[i] <= 1, SK[i], d[i]
def level_up(items, cap=4000):
    out = []
    for (a, va, wa), (b, vb, wb) in itertools.combinations(items, 2):
        r = max(va, vb) / min(va, vb)
        if r < 1.0005: continue
        out.append((f'({a})/({b})', r, r * math.hypot(wa / va, wb / vb)))
        if len(out) >= cap: break
    return out
def run(items, levels=3):
    shares, hits_at = [], []
    cur = items
    for lv in range(levels):
        h = [(n, v, w) for n, v, w in cur if hit(v, w)[0]]
        shares.append(len(h) / max(len(cur), 1)); hits_at.append(h)
        cur = level_up(h)
    return shares, hits_at
real, hits = run(L1)
rng = np.random.default_rng(11); null = []
for _ in range(300):
    jit = [(n, v * math.exp(rng.normal(0, 0.15)), w) for n, v, w in L1]
    null.append(run(jit)[0])
null = np.array(null)
for lv in range(3):
    m, s = null[:, lv].mean(), null[:, lv].std()
    print(f'LEVEL {lv + 1}: {real[lv]:.3f} of values inside one width ({len(hits[lv])} hits) | jitter {m:.3f} +- {s:.3f} | excess {(real[lv] - m) / s:+.1f} widths')
print('\nthe stooges at level 1:', '; '.join(f'{n} {v:.4f} -> {hit(v, w)[1]} at {hit(v, w)[2]:.1f} w' for n, v, w in STOOGES))
st = [h for h in hits[1] if 'shep speed' in h[0]]
print(f'the stooges inside level-2 hits: {len(st)}; tightest:')
for n, v, w in sorted(st, key=lambda h: hit(h[1], h[2])[2])[:5]: print(f'   {n[:90]} = {v:.4f} +- {w:.4f} -> {hit(v, w)[1]} at {hit(v, w)[2]:.2f} w')
print('tightest level-3 rows:')
for n, v, w in sorted(hits[2], key=lambda h: hit(h[1], h[2])[2])[:5]: print(f'   {v:.5f} +- {w:.5f} -> {hit(v, w)[1]} at {hit(v, w)[2]:.3f} w   [{n[:110]}]')
