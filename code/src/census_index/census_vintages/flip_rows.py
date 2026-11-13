#!/usr/bin/env python3
"""flip_rows.py: staged censusvin.* ledger rows to live (run inside the ship's lock, with the page block already in build_site.py)."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/bones-forge/ledger')); import ledger as L
rows = L.load(); n = 0
for k, r in rows.items():
    if k.startswith('censusvin.') and r['status'] == 'staged':
        r['status'] = 'live'; r['history'].append(dict(at=L.now(), change="status: 'staged' -> 'live'", why='page block is in build_site.py, so the row is live with it (the next ship builds the page)', evidence='census_index/census_vintages/CHECKS.md')); n += 1
L.save(rows); print('flipped', n)
