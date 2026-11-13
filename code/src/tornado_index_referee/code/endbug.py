"""Test: does the desk's candidate-warning window (issue <= recorded end time even when end < start) explain the small POD differences?"""
import sys, os, calendar, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rwarn, recount as RC
T, _ = RC.load_db(); P, _ = RC.load_prelim()
W = rwarn.load_warn(range(2008, 2028)); cl = [t for t in T if t[0] < calendar.timegm((2026, 1, 1, 0, 0, 0))]
# tornadoes whose recorded end precedes start
bad = [t for t in cl + P if t[1] is not None and t[1] <= t[0]]
print('end<=start tornadoes', len(bad), 'of which end<start', sum(1 for t in bad if t[1] < t[0]))
per_ok, _ = rwarn.process(bad, W, 'expire')
# desk-like: truncate window by shifting the tornado end into t0 candidate selection -> emulate by temporarily setting issue filter at t1
import bisect
def process_bug(Tl):
    iss = [w['iss'] for w in W]; out = []
    for (t0, t1, lo0, la0, lo1, la1, m, yr) in Tl:
        ts = np.array([float(t0)]); lon = np.array([lo0]); lat = np.array([la0]); cutoff = t1 if t1 is not None else t0
        pew = 0.0; lead = 0.0
        for i in range(bisect.bisect_left(iss, t0 - 95 * 60), bisect.bisect_right(iss, cutoff)):
            w = W[i]
            if not (w['iss'] <= t0 < w['exp']): continue
            x0, y0, x1, y1 = w['bb']
            if x0 <= lo0 <= x1 and y0 <= la0 <= y1 and rwarn.rgeo.inside_even_odd(lon, lat, w['rings'])[0]:
                pew = 1.0; lead = max(lead, (t0 - w['iss']) / 60)
        out.append((pew, lead))
    return out
bug = process_bug(bad)
d_pew = [b[0] - a[1] for a, b in zip(per_ok, bug)]
print('mean PEW  ok %.4f  desk-like %.4f ; tornadoes where they differ: %d' % (np.mean([a[1] for a in per_ok]), np.mean([b[0] for b in bug]), sum(1 for x in d_pew if abs(x) > 1e-9)))
