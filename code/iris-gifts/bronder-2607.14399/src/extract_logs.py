#!/usr/bin/env python3
"""Unpack theirs/zenodo/logs.tar.zst into theirs/zenodo/extract (Python 3.14 standard library: compression.zstd and tarfile, data filter)."""
import os, tarfile, compression.zstd as zstd
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); Z = os.path.join(H, 'theirs', 'zenodo')
with zstd.open(os.path.join(Z, 'logs.tar.zst')) as f, tarfile.open(fileobj=f, mode='r|') as t:
    t.extractall(os.path.join(Z, 'extract'), filter='data')
print('unpacked into', os.path.join(Z, 'extract'))
