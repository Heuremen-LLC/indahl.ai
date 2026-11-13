import re, sys, glob, os, html, json
sys.path.insert(0, '.')
import parse as P
pages = {os.path.basename(f)[:-5]: P.parse(f) for f in sorted(glob.glob('pages/*.html'))}
T = P.text
INT = re.compile(r'\[\s*[-+−]?\d[\d.,e\-−+]*\s*,\s*[-+−]?\d[\d.e\-−+]*\s*\]|±|&plusmn;|\+/-|\+-|half-width|\bCI\b|interval|confidence|credible|standard error|std|\bsigma\b|σ|bootstrap|Wilson|error bar|uncertaint')
LVL = re.compile(r'95\s*%|99\s*%|90\s*%|68\s*%|standard error|std\.? err|\bs\.e\.|\bSE\b|1\s*σ|one sigma|1-sigma|standard deviation|\bsd\b|\bSD\b|bootstrap|Wilson|confidence level|credible', re.I)
out = []
for n, p in pages.items():
    s = p['sections']
    for fld in ('Published', 'Measured or recounted', 'QIA Calibration'):
        t = T(s[fld])
        for m in INT.finditer(t):
            out.append((n, fld, m.group(0), t[max(0, m.start()-80):m.end()+80]))
import collections
byp = collections.defaultdict(list)
for o in out: byp[o[0]].append(o)
print('pages with interval-ish tokens', len(byp))
nolvl = []
for n, os_ in byp.items():
    p = pages[n]
    full = T(p['sections']['Published'] + p['sections']['Measured or recounted'] + p['sections']['QIA Calibration'] + p['sections']['How'])
    lv = LVL.search(full)
    nolvl.append((n, bool(lv), len(os_)))
print('with level word:', sum(1 for x in nolvl if x[1]), 'without:', sum(1 for x in nolvl if not x[1]))
json.dump(out, open('intervals_all.json', 'w'))
for n, hl, c in nolvl:
    if not hl: print(n, c)
