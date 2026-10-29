#!/usr/bin/env python3
"""coin_public.py: tick-bus rider (every 24 ticks). Reruns the COIN trends analysis on whatever is held, copies the scripts and progress file into the public tree and pushes it with ledger/push_public.sh. Read-only on the chain."""
import os, subprocess, sys, shutil
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); pub = os.path.expanduser('~/bones-forge/public_mirror/indahl.ai/code/coin')
r = subprocess.run([sys.executable, '-I', 'coin_trends.py'], capture_output=True, text=True)
print('coin_public: trends', 'ok' if r.returncode == 0 else 'FAILED ' + r.stderr[-200:])
for f in ('PLAN_TRENDS.md', 'rvn_history.py', 'rvn_txs.py', 'coin_trends.py', 'btc_control.py', 'history_run.sh', 'coin_public.py'):
    if os.path.exists(f): shutil.copy(f, pub)
p = subprocess.run(['bash', os.path.expanduser('~/bones-forge/ledger/push_public.sh'), 'COIN trends: progress refresh'], capture_output=True, text=True)
print('coin_public:', (p.stdout.strip().splitlines() or ['no output'])[-1])
