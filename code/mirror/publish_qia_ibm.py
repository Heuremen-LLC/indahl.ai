#!/usr/bin/env python3
"""Pushes summary.json to the page's KV key (qia_ibm). Called at the end of every mirror run."""
import os, subprocess
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
r = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'qia_ibm', '--path', os.path.join(H, 'summary.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('qia_ibm published' if r.returncode == 0 else 'qia_ibm publish FAILED')
