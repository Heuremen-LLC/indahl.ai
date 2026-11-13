#!/usr/bin/env python3
"""fetch_eia.py: caches the two public EIA history files (no key) under data/raw. Never re-fetches a cached file. Delete the file to refresh (the rider does this)."""
import os, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__)); D = H + '/data/raw'; os.makedirs(D, exist_ok=True)
for f in ('WCRFPUS2w.xls', 'MCRFPUS2m.xls'):
    out = '%s/%s' % (D, f)
    if os.path.exists(out) and '--refresh' not in sys.argv: print('cached', f); continue
    tmp = out + '.new'
    r = subprocess.run(['curl', '-sSL', '-m', '90', '-A', 'Mozilla/5.0 (Macintosh) Safari/605', '-o', tmp, '-w', '%{http_code}', 'https://www.eia.gov/dnav/pet/hist_xls/' + f], capture_output=True, text=True)
    if r.stdout.strip() == '200' and open(tmp, 'rb').read(4) == b'\xd0\xcf\x11\xe0': os.replace(tmp, out); print('fetched', f)
    else:
        if os.path.exists(tmp): os.remove(tmp)
        print('FAILED', f, r.stdout); sys.exit(1)
