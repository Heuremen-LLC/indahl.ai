#!/usr/bin/env python3
"""power_tide.py -- ROADMAP STEP 2: the 3080's power follows the tide (19 Oct 2026, Wayfinder and Bones). Rides COINYOS, one look per block.
One signal for everything that acts: the tide (coin/casa/marea.json). Cheap (STRIKE) = everything on the rigs: YO frozen (yo_tide), Casa seats
held (trece), and now the 3080 at its stock 320 W. Dear (LOOK) or unknown = 250 W. Heat guard: 78 C or more -> 250 W.
FIRED = a row in watch/power_tide.jsonl when the limit changes, with the GPU's own limit/draw/temp; scored by the 3080's hash by tide (km_live.log)."""
import json, os, subprocess, time
W = os.path.dirname(os.path.abspath(__file__)); LOG = os.path.join(W, 'power_tide.jsonl')
MAREA = os.path.expanduser('~/bones-forge/coin/casa/marea.json'); HARD, EASY, HOT = 320, 250, 78
REMOTE = r'''
import subprocess, sys, json
want, HOT, EASY = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
pl, draw, temp = subprocess.run(['nvidia-smi', '--query-gpu=power.limit,power.draw,temperature.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=15).stdout.strip().split(', ')
pl, draw, temp = float(pl), float(draw), int(temp); why = 'tide'
if temp >= HOT and want > EASY: want, why = EASY, 'heat'
acted = None
if abs(pl - want) > 0.5: acted = 'rc %d' % subprocess.run(['nvidia-smi', '-pl', str(want)], capture_output=True, timeout=15).returncode
print(json.dumps({'pl_before': pl, 'want': want, 'why': why, 'acted': acted, 'draw_w': draw, 'temp_c': temp}))
'''
def main():
    try:
        m = json.load(open(MAREA)); tide = m.get('tide') if time.time() - m.get('t', 0) < 600 else 'CANNOT_TELL'
    except Exception: tide = 'CANNOT_TELL'
    want = HARD if tide == 'STRIKE' else EASY
    try:
        r = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', 'armature', 'python - %d %d %d' % (want, HOT, EASY)], input=REMOTE, capture_output=True, text=True, timeout=40)
        d = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as e: d = {'outcome': 'NOTHING_RETURNED', 'why': '%s: %s' % (type(e).__name__, str(e)[:80])}
    if d.get('acted') or d.get('outcome'):
        d.update(at=time.strftime('%FT%T'), height=os.environ.get('COINYOS_HEIGHT'), tide=tide)
        open(LOG, 'a').write(json.dumps(d) + '\n')
if __name__ == '__main__': main()
