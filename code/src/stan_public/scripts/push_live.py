#!/usr/bin/env python3
"""push_live.py (12 Nov 2026): puts stan/results/live.json to KV stan_live, served at https://indahl.ai/iris/lab/stan.json. Copy of petrol_index/push_live.py's put.
Publish guard: only with --publish or HEUREMEN_PUBLISH=1 (the tick bus exports it). Numbers and fixed words only, already guarded by live_status.py."""
import os, subprocess, sys
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
if not ('--publish' in sys.argv or os.environ.get('HEUREMEN_PUBLISH') == '1'):
    print('publish guard: stan_live not put to the site KV (run with --publish, or from the tick bus)', file=sys.stderr); raise SystemExit(0)
r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'stan_live', '--path', S + '/results/live.json', '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                   cwd=W, capture_output=True, text=True, env=dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/bin:/bin'))
print('stan live:', 'published' if r.returncode == 0 else 'FAILED ' + (r.stderr or '')[-200:]); raise SystemExit(r.returncode)
