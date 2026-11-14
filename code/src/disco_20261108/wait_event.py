#!/usr/bin/env python3
"""Wait for the next training event (a new line in scheduler.log or a new promotions row), not a timer.
Fallback cap (default 1800 s) only because the tick bus can go silent (9 Nov: silent 2.5 h)."""
import os, sys, time
H = os.path.expanduser('~/bones-forge/sage_library/council')
F = [H + '/scheduler.log', H + '/promotions.jsonl']
cap = int(sys.argv[1]) if len(sys.argv) > 1 else 1800
m0 = [os.path.getsize(f) if os.path.exists(f) else 0 for f in F]; t0 = time.time()
while time.time() - t0 < cap:
    m = [os.path.getsize(f) if os.path.exists(f) else 0 for f in F]
    if m != m0:
        print('EVENT'); [print(open(f).read()[a:].strip()[-1500:]) for f, a, b in zip(F, m0, m) if b > a]; sys.exit(0)
    time.sleep(15)
print(f'NO EVENT in {cap} s')
