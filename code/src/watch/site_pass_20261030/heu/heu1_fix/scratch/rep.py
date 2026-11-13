"""rep.py FILE PAIRSFILE : apply exact (old,new) replacements; each old must occur exactly once. PAIRSFILE is python: PAIRS=[(old,new),...]"""
import sys
f, pf = sys.argv[1], sys.argv[2]
ns = {}; exec(open(pf).read(), ns); pairs = ns['PAIRS']
s = open(f).read()
for i,(o,n) in enumerate(pairs):
    c = s.count(o)
    if c != 1:
        sys.exit(f'pair {i}: found {c} times: {o[:120]!r}')
    s = s.replace(o, n)
open(f,'w').write(s)
print(f'ok {len(pairs)} replacements in {f}')
