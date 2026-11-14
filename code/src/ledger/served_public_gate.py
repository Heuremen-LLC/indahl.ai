#!/usr/bin/env python3
"""Every file the indahl.ai worker serves from public/ must be tracked in the public indahl.ai repo, and so must worker.js.
14 Nov 2026: the claim "everything on the site is in the public git" was never checked; 85 served files and the worker were missing."""
import os, subprocess, sys
B = os.path.expanduser('~/bones-forge'); W = B + '/cloudflare-workers/heuremen-door'; M = B + '/public_mirror/indahl.ai'
tracked = set(subprocess.run(['git', '-C', M, 'ls-files'], capture_output=True, text=True).stdout.split('\n'))
served = [os.path.relpath(os.path.join(d, f), W + '/public') for d, _, fs in os.walk(W + '/public') for f in fs]
miss = [x for x in served if x not in tracked] + [x for x in ('code/worker/worker.js', 'code/worker/wrangler.toml') if x not in tracked]
print('served-public gate: %d served files, %d missing from the public repo' % (len(served), len(miss)))
for x in miss[:20]: print('  MISSING', x)
sys.exit(1 if miss else 0)
