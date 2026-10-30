#!/usr/bin/env python3
"""fetch_theirs.py: downloads every file listed in ../FILES.tsv (url, path under theirs/, sha256) into ../theirs and checks each hash.
Standard library only. Run: python3 -I src/fetch_theirs.py"""
import os, sys, hashlib, urllib.request
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); bad = 0; n = 0
for line in open(os.path.join(H, 'FILES.tsv')):
    if not line.strip() or line.startswith('#'): continue
    url, rel, sha = line.rstrip('\n').split('\t'); dst = os.path.join(H, 'theirs', rel); os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not (os.path.exists(dst) and hashlib.sha256(open(dst, 'rb').read()).hexdigest() == sha):
        data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'heuremen-recount/1'}), timeout=120).read(); open(dst, 'wb').write(data)
    ok = hashlib.sha256(open(dst, 'rb').read()).hexdigest() == sha; n += 1; bad += not ok
    if not ok: print('HASH MISMATCH', rel)
print('%d files, %d hash mismatches' % (n, bad)); sys.exit(1 if bad else 0)
