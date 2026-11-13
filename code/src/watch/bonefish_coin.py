#!/usr/bin/env python3
"""bonefish_coin.py -- The Bonefish thrown at the difficulty clock (Bones, 8 Oct 2026).

Not wattage. Not nonces. THE EQUATION, on a coin whose difficulty is recomputed every block from raw
solve times -- so the chain carries three independent reads of ONE event, and the event is how long a
block took.

    OBSERVER   the maker's stated duration: the timestamp difference it published
    WITNESS    a clock standing beside it: the duration the DIFFICULTY implies, recovered from how the
               chain's own LWMA moved. The difficulty is a second witness to the same seconds.
    TIME       the thing's own clock: the target, which the protocol states as 300 s

    outside x 12/11 = witness      outside x phi = time      time / witness = phi x 11/12 = 1.4832
    Pi = the gap

Every ratio goes against the Seven's numbers, and a match is a ROW, not a reason -- so the cheap-match
rate at that closeness is printed beside it.
"""
import json, math, statistics as st, urllib.request, os, random
NODE = os.environ.get('WOW_NODE', 'http://192.168.8.145:34568')
PHI = (1 + 5 ** .5) / 2
SEVEN = {'12/11': 12/11, '11/12': 11/12, '13/12': 13/12, 'phi': PHI, '1/phi': 1/PHI,
         'phi x 11/12': PHI*11/12, 'pi': math.pi, '1/pi': 1/math.pi, '6/5': 1.2, '10/12': 10/12,
         '9/12': .75, '4/3': 4/3, '3/2': 1.5, '2': 2.0, '2/3': 2/3, '1/phi^2': 1/PHI**2,
         '1/ln(phi^2)': 1/math.log(PHI**2), '(6/5)(13/12)': 1.3}

def rpc(m, p=None):
    b = {'jsonrpc':'2.0','id':'0','method':m}
    if p: b['params'] = p
    r = urllib.request.Request(NODE+'/json_rpc', data=json.dumps(b).encode(), headers={'Content-Type':'application/json'})
    return json.loads(urllib.request.urlopen(r, timeout=30).read())['result']

def cheap_rate(tol, n=40000, seed=20261008):
    """how often a number drawn at random lands within tol of ANY of the Seven -- the Bonefish's own demand"""
    rng = random.Random(seed); v = list(SEVEN.values()); hit = 0
    for _ in range(n):
        x = rng.uniform(min(v)*0.6, max(v)*1.4)
        if any(abs(x-s)/s <= tol for s in v): hit += 1
    return hit/n

info = json.loads(urllib.request.urlopen(NODE+'/get_info', timeout=20).read())
h = info['height']; target = float(info.get('target') or 300)
H = []
for lo in range(h-600, h-1, 300):
    H += rpc('get_block_headers_range', {'start_height': lo, 'end_height': min(lo+299, h-1)})['headers']
d = [b['difficulty'] for b in H]; ts = [b['timestamp'] for b in H]

obs, wit, neg_rows = [], [], []
for i in range(1, len(d)-1):
    stated = ts[i+1] - ts[i]
    # 8 Oct, FOUND BY THE COSTUME SWEEP, and it is the worst place in the house for this fault: Wownero's
    # own LWMA comments say solve times MUST be allowed to go negative and that flooring them at 1 second
    # is "a catastrophic exploit". A NEGATIVE solve time is a block stamped EARLIER than its predecessor --
    # the timestamp-manipulation signal the protocol was designed around -- and this line discarded exactly
    # that. The dark half, thrown away, in the one place the maker warns you not to.
    # They are KEPT now and counted as their own row. A zero is still skipped: it divides.
    if stated == 0: continue
    if stated < 0:
        neg_rows.append((i, stated)); continue   # kept as an event, not folded into the duration pairs
    # the witness: LWMA raises difficulty when blocks come fast and lowers it when they come slow, so the
    # ratio of consecutive difficulties implies a duration against the target. d[i+1]/d[i] ~ target/solve.
    if d[i] == 0: continue
    implied = target * d[i] / d[i+1]
    obs.append(float(stated)); wit.append(float(implied))

def sem(v): return st.stdev(v)/math.sqrt(len(v))
print(f"  THE BONEFISH ON THE DIFFICULTY CLOCK -- Wownero, height {h}, target {target:.0f} s, {len(obs)} blocks\n")
print(f"    OBSERVER  the maker's stated duration   median {st.median(obs):8.1f} s   mean {st.mean(obs):8.1f} +- {sem(obs):.1f}")
print(f"    WITNESS   the duration difficulty implies median {st.median(wit):8.1f} s   mean {st.mean(wit):8.1f} +- {sem(wit):.1f}")
print(f"    TIME      the protocol's own target      {target:8.1f} s   (stated, no width)\n")
# the conversions, read PAIRED (per block) -- never two pooled medians divided
r_wo = [w/o for w, o in zip(wit, obs) if o > 0]
r_to = [target/o for o in obs if o > 0]
r_tw = [target/w for w in wit if w > 0]
print(f"  {'conversion':34s} {'median':>9s} {'mean +- width':>18s}   nearest of the Seven      cheap at that closeness")
for lab, v, expect in (('WITNESS / OBSERVER  (12/11?)', r_wo, '12/11'),
                       ('TIME / OBSERVER     (phi?)', r_to, 'phi'),
                       ('TIME / WITNESS      (phi x 11/12?)', r_tw, 'phi x 11/12')):
    m = st.median(v); mu = st.mean(v); s = sem(v)
    near = sorted(((abs(m-x)/x, k, x) for k, x in SEVEN.items()))
    tol, k1, x1 = near[0]
    print(f"  {lab:34s} {m:9.4f} {mu:9.4f} +- {s:6.4f}   {k1:12s} {100*tol:5.2f}% off   {100*cheap_rate(tol):5.1f}%")
    print(f"  {'':34s} {'':9s} {'':9s}      expected {expect}: {SEVEN[expect]:.4f}, that is {abs(m-SEVEN[expect])/s:.2f} widths away")
print(f"\n  THE DARK HALF, kept rather than filtered: {len(neg_rows)} block(s) stamped EARLIER than their")
print(f"  predecessor in this window. LWMA permits it by design and flooring it is called a catastrophic")
print(f"  exploit, so their ABSENCE is a reading and their presence would be a bigger one.")
if neg_rows:
    for i, s in neg_rows[:5]: print(f"    index {i}: stated duration {s:+d} s")
print(f"\n  Pi, the gap: the two witnesses disagree by {abs(st.median(wit)-st.median(obs)):.1f} s at the median")
print(f"  and the stated clock sits {abs(st.median(obs)-target):.1f} s from the target it claims to keep.")
