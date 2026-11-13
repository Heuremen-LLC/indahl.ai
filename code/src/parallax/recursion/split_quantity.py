"""split_quantity.py -- 7 Oct 2026. by_day's rule, split by the KIND of number. Rule written before running: a pair is a LOOK RATIO if its ledger line contains any of
W/O, T/W, T/O, RATIO, W/laid, look/check, a/b, conversion, maker look; everything else is OTHER. Null: the same values jittered 3 % (they stay in their own dense
region) and 15 %, 300 x. Pooled over 1-6 Oct and per day."""
import re, math, numpy as np
from by_day import S, SV, T, section_text, share, null, DAYS
KEYS = ('W/O', 'T/W', 'T/O', 'RATIO', 'W/laid', 'look/check', 'a/b', 'conversion', 'maker look')
def split(txt):
    look, other = set(), set()
    for line in txt.splitlines():
        kind = look if any(k in line for k in KEYS) else other
        for v, w in re.findall(r'([+-]?\d+\.\d+)\s*\+-\s*(\d+\.\d+)', line):
            v, w = abs(float(v)), float(w)
            if 0.05 <= v <= 10 and w > 0: kind.add((v, w))
    return sorted(look), sorted(other - look)
rng = np.random.default_rng(15); allL, allO = [], []
for name, a, b in DAYS:
    L, O = split(section_text(a, b)); allL += L; allO += O
    out = []
    for nm, vs in (('look', L), ('other', O)):
        if len(vs) >= 3:
            r = share(vs); m, s = null(vs, .03, rng); out.append(f'{nm} n {len(vs):3d} {r:.3f} vs {m:.3f} +- {s:.3f} ({(r - m) / s:+.1f} w)')
        else: out.append(f'{nm} n {len(vs):3d}')
    print(f'{name:8} | ' + ' | '.join(out))
for nm, vs in (('ALL LOOK RATIOS', allL), ('ALL OTHER', allO)):
    r = share(vs); m3, s3 = null(vs, .03, rng); m15, s15 = null(vs, .15, rng)
    tight = [(v, w) for v, w in vs if w / v < 0.02]; rt = share(tight); mt, st = null(tight, .03, rng)
    print(f'{nm:16} n {len(vs):3d}: {r:.3f} | 3 % {m3:.3f} +- {s3:.3f} ({(r - m3) / s3:+.1f} w) | 15 % {m15:.3f} ({(r - m15) / s15:+.1f} w) | tight n {len(tight)}: {rt:.3f} vs {mt:.3f} +- {st:.3f} ({(rt - mt) / st:+.1f} w)')
