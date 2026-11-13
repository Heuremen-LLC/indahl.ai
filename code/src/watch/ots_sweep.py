import subprocess, hashlib, os, re, sys, collections
from concurrent.futures import ThreadPoolExecutor
OTS = os.path.expanduser('~/bones-forge/qvenv/bin/ots'); L = [l.strip() for l in open(sys.argv[1]) if l.strip()]
def one(p):
    p = os.path.join(os.path.expanduser('~/bones-forge'), p)
    tgt = re.sub(r'\.ots(\.bak.*)?$', '', p)
    o = subprocess.run([OTS, 'info', p], capture_output=True, text=True).stdout
    m = re.search(r'File sha256 hash: ([0-9a-f]{64})', o)
    if not m: return ('UNREADABLE', p, '')
    if not os.path.exists(tgt): return ('TARGET MISSING', p, m.group(1)[:16])
    h = hashlib.sha256(open(tgt, 'rb').read()).hexdigest()
    return ('OK' if h == m.group(1) else 'MISMATCH', p, m.group(1)[:16])
with ThreadPoolExecutor(8) as ex: R = list(ex.map(one, L))
c = collections.Counter(r[0] for r in R); print(dict(c))
for r in sorted(R):
    if r[0] != 'OK': print(r[0], r[1].replace(os.path.expanduser('~/bones-forge') + '/', ''), r[2])
