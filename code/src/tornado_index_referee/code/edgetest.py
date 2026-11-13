"""Do on-boundary points explain the 0.003 FY2026 POD gap and the +-2 verified counts? Count tornado segments (prelim, FY2026) exactly on a warning polygon edge/vertex."""
import sys, os, calendar, numpy as np, bisect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rwarn, rgeo, recount as RC
T, _ = RC.load_db(); P, _ = RC.load_prelim(); W = rwarn.load_warn(range(2008, 2028))
iss = [w['iss'] for w in W]
def on_edge(x, y, ring, eps=1e-9):
    a = ring[:-1]; b = ring[1:]; d = b - a; L = (d ** 2).sum(1); L[L == 0] = 1
    t = np.clip(((x - a[:, 0]) * d[:, 0] + (y - a[:, 1]) * d[:, 1]) / L, 0, 1)
    return (np.hypot(a[:, 0] + t * d[:, 0] - x, a[:, 1] + t * d[:, 1] - y) < eps).any()
cnt = 0; tot = 0; changed = 0
for (t0, t1, lo, la, _a, _b, m, yr) in P:
    if t0 >= calendar.timegm((2026, 10, 1, 0, 0, 0)): continue
    tot += 1; hit_in = False; hit_edge = False
    for i in range(bisect.bisect_left(iss, t0 - 95 * 60), bisect.bisect_right(iss, t0)):
        w = W[i]
        if not (w['iss'] <= t0 < w['exp']): continue
        x0, y0, x1, y1 = w['bb']
        if not (x0 <= lo <= x1 and y0 <= la <= y1): continue
        if rgeo.inside_even_odd(np.array([lo]), np.array([la]), w['rings'])[0]: hit_in = True
        elif any(on_edge(lo, la, r) for r in w['rings']): hit_edge = True
    if hit_edge and not hit_in: changed += 1
print('prelim reports', tot, 'unwarned by strict test but exactly on an edge of an active warning:', changed)
