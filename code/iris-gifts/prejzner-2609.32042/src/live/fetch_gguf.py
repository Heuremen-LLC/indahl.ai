#!/usr/bin/env python3
"""Fetch the GGUF files for the live arm from the repos named in his docs/gguf_manifest.tsv and check each sha256 against it."""
import os, sys, hashlib, csv
from huggingface_hub import hf_hub_download
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.join(H, '..', '..'); M = os.path.join(G, 'models')
WANT = sys.argv[1:]
rows = {r['file']: r for r in csv.DictReader(open(os.path.join(G, 'theirs', 'docs', 'gguf_manifest.tsv')), delimiter='\t')}
for f in WANT:
    r = rows[f]; p = hf_hub_download(r['hf_repo'], f, local_dir=M)
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 24), b''): h.update(b)
    print(f, 'sha256 OK' if h.hexdigest() == r['sha256'] else 'SHA256 MISMATCH ' + h.hexdigest(), round(os.path.getsize(p) / 1e9, 2), 'GB', flush=True)
