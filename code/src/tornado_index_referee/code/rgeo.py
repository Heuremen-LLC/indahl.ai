"""Referee geometry (own code): spherical Albers, even-odd ray casting, segment distance."""
import math
import numpy as np
R = 6371.0088
_p1, _p2, _p0, _l0 = [math.radians(v) for v in (29.5, 45.5, 23.0, -96.0)]
_n = 0.5 * (math.sin(_p1) + math.sin(_p2))
_C = math.cos(_p1) ** 2 + 2 * _n * math.sin(_p1)
_r0 = R / _n * math.sqrt(_C - 2 * _n * math.sin(_p0))
def fwd(lon, lat):
    lam = np.radians(np.asarray(lon, float)); phi = np.radians(np.asarray(lat, float))
    r = R / _n * np.sqrt(_C - 2 * _n * np.sin(phi)); t = _n * (lam - _l0)
    return r * np.sin(t), _r0 - r * np.cos(t)
def inv(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    r = np.sqrt(x * x + (_r0 - y) ** 2); t = np.arctan2(x, _r0 - y)
    phi = np.arcsin((_C - (r * _n / R) ** 2) / (2 * _n))
    return np.degrees(_l0 + t / _n), np.degrees(phi)
def ring_cross(px, py, ring):
    """Boolean array: crossing-number parity of points (px,py) against one closed ring (Nx2)."""
    x0 = ring[:-1, 0]; y0 = ring[:-1, 1]; x1 = ring[1:, 0]; y1 = ring[1:, 1]
    m = (px >= ring[:, 0].min()) & (px <= ring[:, 0].max()) & (py >= ring[:, 1].min()) & (py <= ring[:, 1].max())
    out = np.zeros(len(px), bool)
    if not m.any(): return out
    qx = px[m][:, None]; qy = py[m][:, None]
    straddle = (y0[None, :] > qy) != (y1[None, :] > qy)
    with np.errstate(divide='ignore', invalid='ignore'):
        xi = x0[None, :] + (qy - y0[None, :]) * (x1 - x0)[None, :] / (y1 - y0)[None, :]
    out[m] = ((straddle & (qx < xi)).sum(axis=1) % 2) == 1
    return out
def inside_even_odd(px, py, rings):
    c = np.zeros(len(px), int)
    for r in rings:
        if len(r) >= 3: c += ring_cross(px, py, r)
    return c % 2 == 1
def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy
    if L == 0: return np.sqrt((px - ax) ** 2 + (py - ay) ** 2)
    t = np.clip(((px - ax) * dx + (py - ay) * dy) / L, 0.0, 1.0)
    return np.sqrt((px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2)
