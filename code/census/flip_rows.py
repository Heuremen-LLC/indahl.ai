#!/usr/bin/env python3
"""flip_rows.py: staged census.* ledger rows to live (the ship's lock holds the page build). --headline also flips live.census.headline, after the feed route is deployed."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/bones-forge/ledger')); import ledger as L
rows = L.load(); n = 0
for k, r in rows.items():
    if k.startswith('census.') or (k == 'live.census.headline' and '--headline' in sys.argv):
        if r['status'] == 'staged':
            r['status'] = 'live'; r['history'].append(dict(at=L.now(), change="status: 'staged' -> 'live'", why='page block is in build_site.py, so the row is live with it (the next ship builds the page)', evidence='census_index/CHECKS.md')); n += 1
L.save(rows); print('flipped', n)
