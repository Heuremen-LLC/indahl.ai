#!/usr/bin/env python3
"""RANK desk pack: copies.json entry (run under ledger/site_lock.py). Idempotent."""
import json, os, shutil
P = os.path.expanduser('~/bones-forge/ledger/copies.json'); d = json.load(open(P))
if 'rank-data-pack' in d: print('copies entry present'); raise SystemExit
shutil.copy2(P, P + '.bak-20261110-rank')
d['rank-data-pack'] = {"canonical": "cloudflare-workers/heuremen-door/public/rank/rank-data-pack.zip", "copies": ["tools/desk_packs/dist/rank-data-pack.zip"],
                       "live": ["https://indahl.ai/rank/rank-data-pack.zip"], "_note": "10 Nov 2026: desk data pack, built and checked against the live feed by tools/desk_pack.py build rank. Rebuild, then release through ship.sh."}
json.dump(d, open(P, 'w'), indent=1, ensure_ascii=False); print('copies entry added')
