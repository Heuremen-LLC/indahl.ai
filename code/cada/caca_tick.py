#!/usr/bin/env python3
"""caca_tick.py: one CACA round for Nova's tick bus. Probe, summarise, publish to the page's KV key."""
import os, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'); os.chdir(H)
subprocess.run([sys.executable, 'caca_probe.py'], timeout=900); subprocess.run([sys.executable, 'caca_summary.py'], timeout=120)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'caca_live', '--path', os.path.join(H, 'summary_caca.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('caca_live published' if p.returncode == 0 else 'caca_live publish FAILED')
