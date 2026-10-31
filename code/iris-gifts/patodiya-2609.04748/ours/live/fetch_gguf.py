#!/usr/bin/env python3
"""Fetch the Qwen2.5-7B GGUFs for the live bridge at the revision the scout read (8911e8a4) and check each sha256 against her MODEL_SHA256SUMS."""
import os, sys, hashlib
from huggingface_hub import hf_hub_download
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.join(H, '..', '..'); M = os.path.join(G, 'models')
REPO, REV = 'bartowski/Qwen2.5-7B-Instruct-GGUF', '8911e8a47f92bac19d6f5c64a2e2095bd2f7d031'
sums = {}
for l in open(os.path.join(G, 'theirs', 'repo_bc0551d', 'results', 'MODEL_SHA256SUMS')):
    p = l.split()
    if len(p) >= 2: sums[os.path.basename(p[-1])] = p[0]
for f in sys.argv[1:]:
    p = hf_hub_download(REPO, f, revision=REV, local_dir=M)
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 24), b''): h.update(b)
    print(f, 'sha256 OK' if h.hexdigest() == sums.get(f) else 'SHA256 MISMATCH ' + h.hexdigest(), round(os.path.getsize(p) / 1e9, 2), 'GB', flush=True)
