#!/usr/bin/env python3
"""RANK: worker route /rank/live.json (KV rank_live), run under ledger/site_lock.py before ship.sh. Idempotent."""
import os, shutil
W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door/worker.js')
s = open(W).read()
if "'/rank/live.json'" in s: print('route already present'); raise SystemExit
anchor = "    if ((host === 'indahl.ai' || host === 'www.indahl.ai') && u.pathname === '/wiki/live.json' && env.IRIS_BENCH)"
assert anchor in s
line = "    if ((host === 'indahl.ai' || host === 'www.indahl.ai') && u.pathname === '/rank/live.json' && env.IRIS_BENCH) { const v = await env.IRIS_BENCH.get('rank_live'); return new Response(v || '{}', { headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } }); }   // 10 Nov: RANK (OY), republished about once a day by rank_index/rank_tick.py\n"
shutil.copy2(W, W + '.bak-20261110-rank')
open(W, 'w').write(s.replace(anchor, line + anchor, 1)); print('route added')
