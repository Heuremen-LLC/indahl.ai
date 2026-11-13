#!/usr/bin/env python3
"""four_states.py -- 14 Oct, HIS: "four states is the only way to ride ... there all there but you can only see three."
"log it, wire it and always check your six for binary." Rides her ticks. Reads every NEW clock_triangle row and places each
seat's leg in Law 3's FOUR -- HEADS (both legs say behind) / TAILS (both say ahead) / NEITHER (a leg inside the floor) /
BOTH (each leg resolves, opposite signs) -- with ABSENT (Law 4, the state change) BESIDE them, never one of them. The floor is
MEASURED, never picked: the 90th percentile of |closure| on the seats whose triangles close (armature, pi), re-read each tick.
The triangle's own closure sign rides as a third column, because the relation can resolve when neither leg does (14 Oct:
laptop legs 78% NEITHER, closure 89.5% one way). Nothing is filtered; every row is placed."""
import json, os, time
W = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(W, 'clock_triangle.jsonl'); OUT = os.path.join(W, 'four_states.jsonl'); STATE = os.path.join(W, 'four_states_state.json')
SEATS = ('laptop', 'armature', 'pi')

def legs(r, seat):
    e = r.get('edge', {}).get(seat, {}).get('edge_minus_local'); em = r.get('edge', {}).get('mac', {}).get('edge_minus_local')
    h = r.get('house', {}).get(seat, {}).get('remote_minus_mac')
    if not all(isinstance(x, (int, float)) for x in (e, em, h)): return None, None
    return 1000 * (em - e), 1000 * h

def tick():
    R = [json.loads(l) for l in open(SRC)][-400:]
    floor = None
    try: last_at = json.load(open(STATE))['last_at']
    except Exception: last_at = 0
    new = [r for r in R if r.get('at', 0) > last_at]
    out = []
    for r in new:
        row = {'at': r['at'], 'her_cycle': r.get('her_cycle')}       # 15 Oct 05:3x: no labels, no floor -- the two legs and the closure, ms
        for s in SEATS:
            a, b = legs(r, s); c = (r.get('closure_ms') or {}).get(s)
            row[s] = {'edge_leg_ms': a, 'house_leg_ms': b, 'closure_ms': c}
        out.append(row)
    with open(OUT, 'a') as f:
        for row in out: f.write(json.dumps(row) + '\n')
    if new: json.dump({'last_at': new[-1]['at']}, open(STATE, 'w'))
    return len(out), floor

def selftest():
    assert legs({}, 'pi') == (None, None)
    print('selftest 1/1')

if __name__ == '__main__':
    import sys
    if '--selftest' in sys.argv: selftest()
    else: n, fl = tick(); print('wrote', n, 'raw rows')
