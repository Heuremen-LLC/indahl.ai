#!/usr/bin/env python3
"""fetch_weights.py: downloads the eight weight files listed in ../WEIGHTS.tsv (about 30 GB) into ../theirs and checks each sha256 against the
hub's record. A file already present with the right hash is kept. Needed only to rerun the decoder or the drift readings. Standard library only."""
import os, sys, hashlib, urllib.request, shutil
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); bad = n = 0
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 24), b''): h.update(b)
    return h.hexdigest()
for line in open(os.path.join(H, 'WEIGHTS.tsv')):
    if not line.strip() or line.startswith('#'): continue
    url, rel, want = line.rstrip('\n').split('\t'); dst = os.path.join(H, 'theirs', rel); os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not (os.path.exists(dst) and sha(dst) == want):
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'heuremen-recount/1'}), timeout=600) as r, open(dst, 'wb') as o: shutil.copyfileobj(r, o, 1 << 24)
    ok = sha(dst) == want; n += 1; bad += not ok; print(rel, 'sha256 OK' if ok else 'HASH MISMATCH', flush=True)
print('%d files, %d hash mismatches' % (n, bad)); sys.exit(1 if bad else 0)
