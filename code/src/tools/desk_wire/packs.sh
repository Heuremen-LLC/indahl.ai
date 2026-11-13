#!/bin/bash
# packs.sh: desk data packs, copies.json entries and live-headline rows for FLU, STEO and SEASONAL (10 Nov 2026). Run inside ledger/site_lock.py.
set -e; cd ~/bones-forge
cp ledger/copies.json ledger/copies.json.bak-20261110-fcpacks
python3 tools/desk_pack.py build flu steo seasonal
python3 - <<'PY'
import json, os
p = os.path.expanduser('~/bones-forge/ledger/copies.json'); d = json.load(open(p))
for s in ('flu', 'steo', 'seasonal'):
    k = s + '-data-pack'
    if k in d: continue
    d[k] = {"canonical": "cloudflare-workers/heuremen-door/public/%s/%s-data-pack.zip" % (s, s), "copies": ["tools/desk_packs/dist/%s-data-pack.zip" % s],
            "live": ["https://indahl.ai/%s/%s-data-pack.zip" % (s, s)], "_note": "10 Nov 2026: desk data pack, built and checked against the live feed by tools/desk_pack.py build %s. Rebuild, then release through ship.sh." % s}
json.dump(d, open(p, 'w'), indent=1, ensure_ascii=False); print('copies.json: packs added')
PY
/usr/bin/python3 watch/readcheck.py check ledger/CHECKS.md && python3 ledger/live_headlines.py seed | tail -3 || echo "live_headlines seed skipped (ledger/CHECKS.md last entry not complete)"
python3 ledger/live_headlines.py run | tail -3
bash ledger/ship.sh "FLU, STEO, SEASONAL: desk data packs and live headline rows"
