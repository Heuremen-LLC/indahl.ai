#!/usr/bin/env python3
"""fetch_now.py -- pull adapters and logs off RUNNING pods, before the balance dies.

The launcher only fetches at the end of a run. At round ~60 of 400 with the balance
about to run out, that means the training is paid for and unreachable. This pulls it
down mid-flight and touches nothing on the pod, so the runs keep going.
"""
import os, subprocess, sys
sys.path.insert(0, os.path.expanduser('~/bones-forge/pocket-sage/bakeoff_runpod'))
import runpod_bake as R

PODS = {'bakeoff-wen-v6-hold1':'djl70ky24q28sq','bakeoff-wen-v6-hold3':'w7g6y42lrf74va',
        'bakeoff-wen-v6-hold6':'hwg1uvhd55c4we','bakeoff-wen-v7-seed':'ovbq3rn3awafvi',
        'bakeoff-wen-v7-lr':'qfno8xfolx5f1m','bakeoff-wen-v7-margin':'duw5xsw3y3qvgn',
        'bakeoff-wen-v7-cases':'qtyrikbeci9hyz'}
HERE = os.path.dirname(os.path.abspath(__file__))

# GO QUIET WHEN THERE IS NOTHING TO FETCH, WHICH IS WHAT THE DOCSTRING ALREADY CLAIMED.
# The pod ids below are hardcoded. When the balance terminates them this file printed seven
# "no ssh target: RuntimeError" lines every three of her ticks, all night, against pods that
# no longer exist -- and a failure that prints forever is indistinguishable from one that
# just started. So ask the account which pods are alive FIRST and intersect. An empty
# intersection is one line, not seven, and it says the real thing: the lane is out of money.
try:
    _live = {p.get('id') for p in R.pods() or []}
except Exception as _e:
    print('  runpod unreachable (%s) -- not fetching, not guessing' % type(_e).__name__)
    raise SystemExit(0)
PODS = {n: i for n, i in PODS.items() if i in _live}
if not PODS:
    try:
        _bal = R.gql('query { myself { clientBalance } }')['myself']['clientBalance']
        print('  no pods running, balance $%.2f -- the training lane is stopped on money, not on a fault' % _bal)
    except Exception:
        print('  no pods running -- nothing to fetch')
    raise SystemExit(0)

for name, pid in PODS.items():
    tag = name.replace('bakeoff-wen-', '')
    out = os.path.join(HERE, 'pods', tag)
    os.makedirs(out, exist_ok=True)
    try:
        tgt = R.ssh_target(pid)
    except Exception as e:
        print('  %-12s no ssh target: %s' % (tag, type(e).__name__)); continue
    ok = R.scp(tgt, ['root@%s:/workspace/out/.' % tgt[0]], out)
    n = sum(len(f) for _, _, f in os.walk(out))
    print('  %-12s %s   %d files local' % (tag, 'fetched' if ok else 'FETCH FAILED', n))
