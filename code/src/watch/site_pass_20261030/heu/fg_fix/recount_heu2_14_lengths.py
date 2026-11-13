"""Length overlap of the cold and seated arms (HEU2-14). hook_fires.log first 374 rows."""
import re, numpy as np
L = open('/Users/heuremen/bones-forge/triangulation/triangle/runs/hook_fires.log').read().split('\n')[:374]
S, C = [], []
for l in L:
    m = re.match(r'(\S+) session (\S+) mode (\S+) words (\d+) (.*)', l)
    if not m: continue
    w = int(m.group(4)); f = 'Two-lane' in m.group(5)
    if m.group(2) == '1fecc2b7': S.append((w, f))
    elif m.group(2) != 'testtest': C.append((w, f))
sw = np.array([w for w, _ in S]); cw = np.array([w for w, _ in C])
q = [0, 10, 25, 50, 75, 90, 100]
for nm, a in (('seated', sw), ('cold', cw)):
    f = list(np.percentile(a, q)); v = [int(np.floor(x + 0.5)) for x in f]
    print(f'{nm} percentiles exact (numpy linear):', [float(x) for x in f])
    print(f'{nm} n {len(a)} words: min {v[0]} p10 {v[1]} p25 {v[2]} median {v[3]} p75 {v[4]} p90 {v[5]} max {v[6]}  (middle half {v[2]} to {v[4]}, half-up rounding)')
print('seated >= cold median', (sw >= np.median(cw)).sum(), 'of', len(sw))
print('cold <= seated median', (cw <= np.median(sw)).sum(), 'of', len(cw))
print('seated >= cold 25th pct', (sw >= np.percentile(cw, 25)).sum(), '  cold <= seated 75th pct', (cw <= np.percentile(sw, 75)).sum())
print('seated max', sw.max(), ' cold min', cw.min())
for lo, hi in ((297, 500), (500, 800), (800, 1013)):
    s = [f for w, f in S if lo <= w < hi]; c = [f for w, f in C if lo <= w < hi]
    print(f'{lo}-{hi}: seated {sum(s)}/{len(s)}  cold {sum(c)}/{len(c)}')
print('mean words cold/seated', round(cw.mean()), round(sw.mean()), 'ratio', round(cw.mean() / sw.mean(), 2), ' median ratio', round(np.median(cw) / np.median(sw), 2))
