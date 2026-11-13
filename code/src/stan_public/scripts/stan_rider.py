#!/usr/bin/env python3
"""stan_rider.py (12 Nov 2026): tick-bus rider, every 6 ticks. live_status.py writes stan/results/live.json, push_live.py puts it to the site KV,
results_push.py copies code and numbers to GitHub and Hugging Face when they changed (at most every 20 minutes). Read-only on the pipeline."""
import os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); PY = '/opt/homebrew/bin/python3'
env = dict(os.environ, HEUREMEN_PUBLISH='1', PATH='/opt/homebrew/bin:/usr/bin:/bin')
for s in ('live_status.py', 'push_live.py', 'results_push.py'):
    r = subprocess.run([PY, '-I', D + '/' + s], capture_output=True, text=True, timeout=900, env=env); print((r.stdout + r.stderr).strip()[-300:])
    if r.returncode != 0 and s == 'live_status.py': break
