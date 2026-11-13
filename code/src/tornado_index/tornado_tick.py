#!/usr/bin/env python3
"""tornado_tick.py: TORNADO rider (see PLAN.md). Rerunnable. Installs no timer. Reads public sources with no key, one request at a time, paced:
IEM archive of SPC Day 1 Convective Outlooks (shapefiles by year), IEM archive of NWS storm-based tornado warnings, the SPC tornado database file,
SPC preliminary storm reports, the Census state boundary file. Sets the stated tornado probability bands and the stated GPRA warning goals beside
the tornadoes that happened. Writes data/tornado.json, summary_tornado.json, data/tornado_live.json and data/tornado_history.jsonl.
--offline: cached files only. --publish: also put data/tornado_live.json in the site KV as tornado_live, served at /tornado/live.json.
--selftest: rule, distance and warning checks only, no network. --no-pointcheck: skip gate 2 network reads (gate 2 then reads its cached answers)."""
import os, sys, json, time, math, re, csv, io, gzip, glob, hashlib, random, subprocess, calendar, urllib.request, urllib.parse, collections as C
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import numpy as np
from matplotlib.path import Path
import heuremen_kit as K, shpread
OFF = '--offline' in sys.argv; PUB = '--publish' in sys.argv; NOPC = '--no-pointcheck' in sys.argv
UA = 'heuremen-tornado/0.1 (+https://indahl.ai/tornado)'
IEM_OTL = 'https://mesonet.agron.iastate.edu/cgi-bin/request/gis/outlooks.py?d=1&type=C&sts=%d-01-01T00:00Z&ets=%d-01-01T00:00Z&geom=geom_layers'
IEM_SBW = 'https://mesonet.agron.iastate.edu/api/1/vtec/sbw_interval.geojson?begints=%s&endts=%s&ph=TO'
IEM_PT = 'https://mesonet.agron.iastate.edu/api/1/nws/outlook_by_point.json?lat=%.4f&lon=%.4f&valid=%s'
DB_URL = 'https://www.spc.noaa.gov/wcm/data/1950-2025_actual_tornadoes.csv'
PRELIM = 'https://www.spc.noaa.gov/climo/reports/%s_rpts_filtered_torn.csv'
STATES_URL = 'https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_20m.zip'
FIRST_YEAR, LAST_CLOSED = 2007, 2025; FY_FIRST, FY_LAST_CLOSED = 2008, 2025
LEVELS = (0.02, 0.05, 0.10, 0.15, 0.30, 0.45, 0.60)
BANDS = [(0.0, 0.02)] + [(LEVELS[i], LEVELS[i + 1]) for i in range(len(LEVELS) - 1)] + [(0.60, 1.0)]
BAND_NAMES = ['under 2', '2 to 5', '5 to 10', '10 to 15', '15 to 30', '30 to 45', '45 to 60', '60 and over']
RADIUS_KM = 25 * 1.609344; GRID_KM = 80.0; MIN_DAYS = 30; NBOOT = 2000; SEED = 20261110
GOALS = dict(pod=0.72, lead=13.0, far=0.71)
ALLEY = ('TX', 'OK', 'KS', 'NE', 'SD', 'IA')
NOT48 = ('AK', 'HI', 'PR')
PACE = 1.5
for d in ('data', 'data/raw', 'data/raw/outlooks', 'data/raw/warnings', 'data/raw/db', 'data/raw/prelim', 'data/raw/boundaries', 'data/cache'): os.makedirs(d, exist_ok=True)
NOW = time.time(); STAMP = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(NOW))
def log(*a): print('tornado:', *a, file=sys.stderr, flush=True)
_last = [0.0]; STALE = []
def get(url, tries=3, timeout=900):
    err = None
    for a in range(tries):
        w = PACE - (time.time() - _last[0])
        if w > 0: time.sleep(w)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=timeout) as r: b = r.read()
            _last[0] = time.time(); return b
        except Exception as e:
            _last[0] = time.time(); err = e
            if getattr(e, 'code', 0) in (400, 404, 422): break
            time.sleep(5 * (a + 1) ** 2)
    raise RuntimeError('fetch failed %s: %r' % (url[:140], err))
def fetch_to(path, url, max_age_h=None, must=None):
    """Fetch url into path unless a copy exists (and is younger than max_age_h when given). Returns True if a copy is on disk."""
    fresh = os.path.exists(path) and (max_age_h is None or (NOW - os.path.getmtime(path)) / 3600 < max_age_h)
    if fresh or OFF: return os.path.exists(path)
    try:
        b = get(url)
        if must and not must(b): raise RuntimeError('unexpected content')
        open(path + '.part', 'wb').write(b); os.replace(path + '.part', path); return True
    except Exception as e:
        log('fetch FAILED', url[:120], repr(e)[:120]); STALE.append(os.path.basename(path)); return os.path.exists(path)
def ep(s):
    """'YYYYmmddHHMM' or 'YYYY-mm-ddTHH:MM(:SS)Z' -> epoch seconds UTC."""
    s = s.strip().replace('Z', '')
    if 'T' in s: return calendar.timegm(time.strptime(s[:16], '%Y-%m-%dT%H:%M'))
    return calendar.timegm(time.strptime(s[:12], '%Y%m%d%H%M'))
def day_of(t, hour):
    """The date (YYYYmmdd) of the window that starts at `hour` UTC and holds epoch t."""
    return time.strftime('%Y%m%d', time.gmtime(t - hour * 3600))

# ---------------- projection and grid ----------------
R = 6371.0088; P1, P2, P0, L0 = map(math.radians, (29.5, 45.5, 23.0, -96.0))
NN = (math.sin(P1) + math.sin(P2)) / 2; CC = math.cos(P1) ** 2 + 2 * NN * math.sin(P1); RHO0 = R * math.sqrt(CC - 2 * NN * math.sin(P0)) / NN
def proj(lon, lat):
    lon = np.radians(np.asarray(lon, float)); lat = np.radians(np.asarray(lat, float))
    rho = R * np.sqrt(CC - 2 * NN * np.sin(lat)) / NN; th = NN * (lon - L0)
    return rho * np.sin(th), RHO0 - rho * np.cos(th)
def unproj(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    rho = np.hypot(x, RHO0 - y); th = np.arctan2(x, RHO0 - y)
    lat = np.arcsin((CC - (rho * NN / R) ** 2) / (2 * NN)); lon = L0 + th / NN
    return np.degrees(lon), np.degrees(lat)
def seg_dist(px, py, ax, ay, bx, by):
    """Distance from points (px, py) to the segment a-b, all in km on the projection."""
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    if L2 <= 0: return np.hypot(px - ax, py - ay)
    t = np.clip(((px - ax) * dx + (py - ay) * dy) / L2, 0, 1)
    return np.hypot(px - (ax + t * dx), py - (ay + t * dy))
def ring_paths(rings): return [Path(np.asarray(r)) for r in rings if len(r) >= 3]
def inside(paths, xy):
    """Even-odd over all rings: a point inside an odd number of rings is inside (a hole is outside)."""
    c = np.zeros(len(xy), int)
    for p in paths: c += p.contains_points(xy)
    return (c % 2) == 1

# ---------------- the rules (PLAN.md, Rules) ----------------
# 12 Nov 2026: Faults and Guards 2.0 outcome rule (PLAN_ADDENDUM_std2.md). Every rule returns (outcome, reason). The warning goals are one-sided bounds and never print CONSISTENT.
def band_outcome(lo, hi, band, days, edge='[)'):
    if days <= 0: return K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE
    if days < MIN_DAYS: return K.CANNOT_TELL, K.TOO_WIDE_TO_RESOLVE
    return K.read(lo, hi, band=band, edge=edge)
def goal_outcome(lo, hi, goal, kind):
    """kind 'atleast' (POD, lead): the goal itself counts as met, ABOVE means the interval is at or above it. 'atmost' (FAR): the goal itself counts as met, BELOW means the interval is at or under it."""
    return K.read(lo, hi, bound=goal, edge='[)' if kind == 'atleast' else '(]')
def bss_outcome(lo, hi):
    return K.read(lo, hi, bound=0.0, edge='closed')
def boot_ratio(num, den, seed=SEED, n=NBOOT):
    """num, den: per-day sums. Day-level block bootstrap of sum(num)/sum(den). Returns (value, lo, hi)."""
    num = np.asarray(num, float); den = np.asarray(den, float); D = len(num)
    if D == 0 or den.sum() <= 0: return None, None, None
    rng = np.random.default_rng(seed); w = rng.multinomial(D, np.full(D, 1.0 / D), size=n).astype(float)
    sn = w @ num; sd = w @ den; ok = sd > 0; r = sn[ok] / sd[ok]
    return float(num.sum() / den.sum()), float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))
def boot_bss(bs, bc, seed=SEED, n=NBOOT):
    bs = np.asarray(bs, float); bc = np.asarray(bc, float); D = len(bs)
    if D == 0 or bc.sum() <= 0: return None, None, None
    rng = np.random.default_rng(seed); w = rng.multinomial(D, np.full(D, 1.0 / D), size=n).astype(float)
    a = w @ bs; b = w @ bc; ok = b > 0; r = 1 - a[ok] / b[ok]
    return float(1 - bs.sum() / bc.sum()), float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))
def segments(t0, t1):
    """1-minute segments from the start up to the end. No end, or end before start: one segment at the start. Returns (times, fractions along the track)."""
    if t1 is None or t1 <= t0: return np.array([t0], float), np.array([0.0])
    ts = np.arange(t0, t1 + 1e-6, 60.0); return ts, (ts - t0) / (t1 - t0)
def warn_tornado(tor, warns):
    """tor: dict(t0, t1, ax, ay, bx, by) in epoch s and lon/lat. warns: list of dicts (issue, expire, paths, bbox). Returns (pew, lead, initial lead, verified warning indexes)."""
    ts, fr = segments(tor['t0'], tor['t1'])
    lon = tor['ax'] + fr * (tor['bx'] - tor['ax']); lat = tor['ay'] + fr * (tor['by'] - tor['ay']); xy = np.column_stack([lon, lat])
    best = np.full(len(ts), np.nan); ver = set()
    for i, w in enumerate(warns):
        act = (w['issue'] <= ts) & (ts < w['expire'])
        if not act.any(): continue
        x0, y0, x1, y1 = w['bbox']; bb = act & (lon >= x0) & (lon <= x1) & (lat >= y0) & (lat <= y1)
        if not bb.any(): continue
        hit = np.zeros(len(ts), bool); hit[bb] = inside(w['paths'], xy[bb])
        if hit.any():
            ver.add(i); lead = (ts - w['issue']) / 60.0
            best = np.where(hit & (np.isnan(best) | (lead > best)), lead, best)    # earliest issued warning = largest lead
    warned = ~np.isnan(best); lead = np.where(warned, best, 0.0)
    return float(warned.mean()), float(lead.mean()), float(lead[0]), ver
def rule_selftest():
    t = []
    t.append(band_outcome(0.20, 0.25, (0.10, 0.15), 40) == (K.ABOVE, None)); t.append(band_outcome(0.01, 0.04, (0.05, 0.10), 40) == (K.BELOW, None))
    t.append(band_outcome(0.11, 0.14, (0.10, 0.15), 40) == (K.CONSISTENT, None)); t.append(band_outcome(0.09, 0.12, (0.10, 0.15), 40) == (K.CANNOT_TELL, K.STRADDLES_EDGE))
    t.append(band_outcome(0.11, 0.14, (0.10, 0.15), 29) == (K.CANNOT_TELL, K.TOO_WIDE_TO_RESOLVE)); t.append(band_outcome(0.003, 0.008, (0.0, 0.02), 400) == (K.CONSISTENT, None))
    t.append(band_outcome(None, None, (0.10, 0.15), 0) == (K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE)); t.append(band_outcome(0.12, 0.15, (0.10, 0.15), 40) == (K.CANNOT_TELL, K.STRADDLES_EDGE))   # open upper edge
    t.append(goal_outcome(0.60, 0.66, 0.72, 'atleast') == (K.BELOW, None)); t.append(goal_outcome(0.73, 0.80, 0.72, 'atleast') == (K.ABOVE, None)); t.append(goal_outcome(0.70, 0.74, 0.72, 'atleast') == (K.CANNOT_TELL, K.STRADDLES_EDGE))
    t.append(goal_outcome(0.72, 0.78, 0.71, 'atmost') == (K.ABOVE, None)); t.append(goal_outcome(0.60, 0.70, 0.71, 'atmost') == (K.BELOW, None)); t.append(goal_outcome(0.69, 0.73, 0.71, 'atmost') == (K.CANNOT_TELL, K.STRADDLES_EDGE))
    t.append(goal_outcome(0.72, 0.80, 0.72, 'atleast') == (K.ABOVE, None) and goal_outcome(0.60, 0.71, 0.71, 'atmost') == (K.BELOW, None))   # the goal itself counts as met
    t.append(all(goal_outcome(a, b, g, k)[0] != K.CONSISTENT for a, b, g, k in ((0.7, 0.8, 0.72, 'atleast'), (0.6, 0.7, 0.71, 'atmost'), (0.1, 0.2, 0.15, 'atleast'))))   # a one-sided bound never prints CONSISTENT
    t.append(bss_outcome(0.05, 0.2) == (K.ABOVE, None) and bss_outcome(-0.3, -0.1) == (K.BELOW, None) and bss_outcome(-0.1, 0.1) == (K.CANNOT_TELL, K.STRADDLES_EDGE) and bss_outcome(None, None) == (K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE))
    # distance: a point at the origin of the projection, a track 39.9 km and 40.6 km away (gate 3)
    t.append(bool(seg_dist(np.array([0.0]), np.array([0.0]), -50, 39.9, 50, 39.9)[0] <= RADIUS_KM)); t.append(bool(seg_dist(np.array([0.0]), np.array([0.0]), -50, 40.6, 50, 40.6)[0] > RADIUS_KM))
    t.append(day_of(ep('202605011259'), 13) == '20260430' and day_of(ep('202605011300'), 13) == '20260501')
    # warnings (gate 4): a square warning from lon -98..-97, lat 35..36, issued at 1000 s, expiring at 1000 + 3600 s
    sq = [[(-98, 35), (-97, 35), (-97, 36), (-98, 36), (-98, 35)]]; W = [dict(issue=1000.0, expire=4600.0, paths=ring_paths(sq), bbox=(-98, 35, -97, 36))]
    p, l, l0, v = warn_tornado(dict(t0=1600.0, t1=1600.0 + 600, ax=-97.6, ay=35.4, bx=-97.4, by=35.6), W); t.append(p == 1.0 and abs(l - 15.0) < 1e-9 and abs(l0 - 10.0) < 1e-9 and v == {0})
    p, l, l0, v = warn_tornado(dict(t0=1600.0, t1=2200.0, ax=-90.0, ay=35.4, bx=-89.9, by=35.5), W); t.append(p == 0.0 and l == 0.0 and v == set())
    p, l, l0, v = warn_tornado(dict(t0=1600.0, t1=1600.0 + 9 * 60, ax=-97.45, ay=35.5, bx=-96.55, by=35.5), W); t.append(abs(p - 0.5) < 1e-9 and v == {0})
    p, l, l0, v = warn_tornado(dict(t0=500.0, t1=500.0 + 60, ax=-97.5, ay=35.5, bx=-97.5, by=35.5), W); t.append(p == 0.0)   # before issue: unwarned
    xy = np.array([[-97.5, 35.5], [-97.95, 35.05]]); hole = sq + [[(-97.9, 35.1), (-97.1, 35.1), (-97.1, 35.9), (-97.9, 35.9), (-97.9, 35.1)]]
    t.append(list(inside(ring_paths(hole), xy)) == [False, True])
    lo, hi = None, None; v, lo, hi = boot_ratio([1, 1, 0, 0], [2, 2, 2, 2]); t.append(abs(v - 0.25) < 1e-12 and lo <= 0.25 <= hi)
    x, y = proj([-96.0, -80.0], [23.0, 40.0]); lo2, la2 = unproj(x, y); t.append(abs(x[0]) < 1e-6 and abs(y[0]) < 1e-6 and np.allclose(lo2, [-96, -80]) and np.allclose(la2, [23, 40]))
    return all(t), t
if '--selftest' in sys.argv:
    ok, t = rule_selftest(); print('rule selftest', 'PASSED' if ok else 'FAILED', t); sys.exit(0 if ok and K.selftest() else 1)

# ---------------- 1. boundaries and grid ----------------
st_zip = 'data/raw/boundaries/cb_2024_us_state_20m.zip'
fetch_to(st_zip, STATES_URL)
_, states = shpread.read_zip(st_zip)
SP = {s['STUSPS']: ring_paths(s['rings']) for s in states}
# 10 Nov 2026, referee R1: a rectangle that covers the 48 states with margin (the corner projections clipped south Texas, south Florida and the Washington coast)
xs = np.arange(-3200.0, 3200.0 + 1, GRID_KM); ys = np.arange(-800.0, 3600.0 + 1, GRID_KM)
XX, YY = np.meshgrid(xs, ys); LON, LAT = unproj(XX.ravel(), YY.ravel()); LL = np.column_stack([LON, LAT])
pst = np.array([''] * len(LL), dtype=object)
for k, paths in SP.items():
    if k in NOT48: continue
    m = inside(paths, LL) & (pst == '')
    pst[m] = k
keep = pst != ''
PX, PY = XX.ravel()[keep], YY.ravel()[keep]; PLON, PLAT = LON[keep], LAT[keep]; PST = pst[keep]; NP = len(PX); PLL = np.column_stack([PLON, PLAT])
CELLS = {'United States': np.ones(NP, bool), 'Kansas': PST == 'KS', 'Tornado Alley': np.isin(PST, ALLEY)}
log('grid points', NP, {k: int(v.sum()) for k, v in CELLS.items()})

# ---------------- 2. stated side: outlooks ----------------
this_year = int(time.strftime('%Y', time.gmtime(NOW)))
fmt_ok = True; other1300 = set(); late13 = set(); issued = {}; layers = C.defaultdict(lambda: C.defaultdict(list)); prodiss = {}; odd_threshold = C.Counter(); unreadable_days = set()
for y in range(FIRST_YEAR, this_year + 1):
    f = 'data/raw/outlooks/day1_%d.zip' % y
    fetch_to(f, IEM_OTL % (y, y + 1), max_age_h=(20 if y == this_year else None), must=lambda b: b[:2] == b'PK')
    if not os.path.exists(f): continue
    try: fn, recs = shpread.read_zip(f)
    except Exception as e: log('outlook file unreadable', f, repr(e)[:100]); STALE.append(f); continue
    if not all(k in fn for k in ('ISSUE', 'EXPIRE', 'THRESHOLD', 'CATEGORY', 'CYCLE', 'PRODISS')): fmt_ok = False; continue
    for r in recs:
        if r['CYCLE'] != '13' and r.get('DAY', '1') == '1' and r['ISSUE'][8:12] == '1300' and r['ISSUE'][:4] == str(y): other1300.add(r['ISSUE'][:8])
        if r['CYCLE'] == '13' and r.get('DAY', '1') == '1' and r['ISSUE'][8:12] > '1300' and r['ISSUE'][:4] == str(y): late13.add(r['ISSUE'][:8])
        if r['CYCLE'] != '13' or r.get('DAY', '1') != '1' or r.get('TYPE', 'C') != 'C': continue
        d = r['ISSUE'][:8]
        if not d.startswith(str(y)): continue
        issued[d] = r['EXPIRE']; prodiss.setdefault(d, r['PRODISS'])
        if r['CATEGORY'] != 'TORNADO': continue
        th = r['THRESHOLD']
        if th != 'SIGN' and th not in ('%.2f' % L for L in LEVELS): odd_threshold[th] += 1; continue
        layers[d][th].append(r['rings'])
# per day: band index per grid point (0 = under 2 percent) and hatched flag
BAND = {}; SIGN = {}
for d in sorted(issued):
    b = np.zeros(NP, np.int8); s = np.zeros(NP, bool)
    try:
        for i, L in enumerate(LEVELS):
            for rings in layers[d].get('%.2f' % L, []): b[inside(ring_paths(rings), PLL)] = i + 1
        for rings in layers[d].get('SIGN', []): s |= inside(ring_paths(rings), PLL)
    except Exception as e: unreadable_days.add(d); continue
    BAND[d] = b; SIGN[d] = s
log('outlook days issued', len(issued), 'read', len(BAND))

# ---------------- 3. delivered side ----------------
db_f = 'data/raw/db/1950-2025_actual_tornadoes.csv'
fetch_to(db_f, DB_URL, max_age_h=24 * 7)
NEEDDB = ('slat', 'slon', 'elat', 'elon', 'date', 'time', 'tz', 'edat', 'etime', 'mag')
tors = []; dbc = C.Counter(); tz_other = 0; db_fields = []
with open(db_f, newline='') as fh:
    rd = csv.DictReader(fh); db_fields = rd.fieldnames or []
    for r in rd:
        try: yr = int(r['yr'])
        except Exception: continue
        if yr < FIRST_YEAR - 1: continue
        if r['tz'] != '3': tz_other += 1; continue
        try:
            t0 = calendar.timegm(time.strptime(r['date'] + ' ' + r['time'], '%Y-%m-%d %H:%M:%S')) + 6 * 3600
            slat, slon = float(r['slat']), float(r['slon'])
        except Exception: dbc['no start position or time'] += 1; continue
        if slat == 0 or slon == 0: dbc['no start position or time'] += 1; continue
        try: elat, elon = float(r['elat']), float(r['elon'])
        except Exception: elat = elon = 0.0
        if elat == 0 or elon == 0: elat, elon = slat, slon; dbc['no end position, start point used'] += 1
        try: t1 = calendar.timegm(time.strptime(r['edat'] + ' ' + r['etime'], '%Y-%m-%d %H:%M:%S')) + 6 * 3600
        except Exception: t1 = None; dbc['no end time, one segment'] += 1
        try: mag = int(r['mag'])
        except Exception: mag = -9
        tors.append(dict(src='db', om=r['om'], st=r['st'], t0=float(t0), t1=float(t1) if t1 else None, ax=slon, ay=slat, bx=elon, by=elat, mag=mag))
log('database tornadoes read', len(tors), dict(dbc), 'other time zone', tz_other)
# preliminary reports, 1 January 2026 onward, one file per convective day (1200 UTC to 1159 UTC)
pre_days = []; pre_missing = []; t_last = NOW - 36 * 3600
d = calendar.timegm((LAST_CLOSED + 1, 1, 1, 0, 0, 0))
while d + 86400 + 12 * 3600 <= t_last:
    ds = time.strftime('%Y%m%d', time.gmtime(d)); f = 'data/raw/prelim/%s.csv' % ds
    ok = fetch_to(f, PRELIM % ds[2:], max_age_h=(None if NOW - d > 21 * 86400 else 20), must=lambda b: b.startswith(b'Time'))
    if not ok: pre_missing.append(ds)
    else:
        pre_days.append(ds)
        for r in csv.DictReader(open(f, newline='', encoding='latin-1')):
            try:
                hhmm = int(r['Time']); lat = float(r['Lat']); lon = float(r['Lon'])
            except Exception: dbc['preliminary report unreadable'] += 1; continue
            t = d + (hhmm // 100) * 3600 + (hhmm % 100) * 60 + (0 if hhmm >= 1200 else 86400)
            try: mag = int(re.sub(r'\D', '', r.get('F_Scale', '')) or -9)
            except Exception: mag = -9
            tors.append(dict(src='prelim', om=ds + '-' + r['Time'], st=r.get('State', ''), t0=float(t), t1=None, ax=lon, ay=lat, bx=lon, by=lat, mag=mag))
    d += 86400
log('preliminary days', len(pre_days), 'missing', len(pre_missing))

# ---------------- 4. outlook rows: events per point-day ----------------
EV = {}; EV2 = {}; EV2U = {}
for d in BAND: EV[d] = np.zeros(NP, bool); EV2[d] = np.zeros(NP, bool); EV2U[d] = np.zeros(NP, bool)
placed = C.Counter()
for t in tors:
    dd = day_of(t['t0'], 13)
    yr = int(dd[:4])
    if yr < FIRST_YEAR: continue                                    # read only so a warning in early FY2008 can find its tornado
    if (t['src'] == 'db') != (yr <= LAST_CLOSED): continue
    if t['t0'] - ep(dd + '1300') >= 23 * 3600: placed['start between 1200 and 1300 UTC, in no outlook day'] += 1; continue          # closed years read the database, the recent window the preliminary reports
    if dd not in EV: placed['no outlook day'] += 1; continue
    ax, ay = proj(t['ax'], t['ay']); bx, by = proj(t['bx'], t['by'])
    near = seg_dist(PX, PY, float(ax), float(ay), float(bx), float(by)) <= RADIUS_KM
    EV[dd] |= near
    if t['mag'] >= 2: EV2[dd] |= near
    if t['mag'] >= 2 or t['mag'] < 0: EV2U[dd] |= near            # referee R5, display only: unrated tornadoes read as EF2 or stronger, an upper bound
    placed['placed'] += 1
days_closed = [d for d in sorted(BAND) if FIRST_YEAR <= int(d[:4]) <= LAST_CLOSED]
days_pre = [d for d in sorted(BAND) if int(d[:4]) > LAST_CLOSED and d in set(pre_days)]
frame_days = []
t = calendar.timegm((FIRST_YEAR, 1, 1, 0, 0, 0))
while t + 86400 + 12 * 3600 <= t_last: frame_days.append(time.strftime('%Y%m%d', time.gmtime(t))); t += 86400
nothing = dict(no_outlook=[d for d in frame_days if d not in issued], outlook_unreadable=sorted(unreadable_days),
               no_outlook_other_cycle_1300=[d for d in frame_days if d not in issued and d in other1300], late_cycle13_scored=sorted(d for d in late13 if d in set(frame_days)),
               prelim_missing=pre_missing)
# climatology per grid point and calendar month over closed years, leave the scored year out
ym = C.defaultdict(lambda: [np.zeros(NP), 0])
for d in days_closed: k = (int(d[:4]), int(d[4:6])); ym[k][0] += EV[d]; ym[k][1] += 1
mon_tot = {m: [sum(v[0] for k, v in ym.items() if k[1] == m), sum(v[1] for k, v in ym.items() if k[1] == m)] for m in range(1, 13)}
def clim(d):
    y, m = int(d[:4]), int(d[4:6]); e, n = mon_tot[m]
    if y <= LAST_CLOSED and (y, m) in ym: e = e - ym[(y, m)][0]; n = n - ym[(y, m)][1]
    return e / n if n else np.zeros(NP)
STATED_P = np.array([0.0] + list(LEVELS))
def cell_read(name, days, mask, prelim=False):
    nb = len(BANDS); rows = np.zeros((len(days), nb)); ev = np.zeros((len(days), nb)); s_rows = np.zeros(len(days)); s_ev = np.zeros(len(days)); s_evu = np.zeros(len(days)); yr_of = [d[:4] for d in days]
    bs = np.zeros(len(days)); bc = np.zeros(len(days)); n_rows = 0
    for i, d in enumerate(days):
        b = BAND[d][mask]; e = EV[d][mask]
        rows[i] = np.bincount(b, minlength=nb); ev[i] = np.bincount(b, weights=e, minlength=nb)
        s = SIGN[d][mask]; s_rows[i] = s.sum(); s_ev[i] = (s & EV2[d][mask]).sum(); s_evu[i] = (s & EV2U[d][mask]).sum()
        p = STATED_P[b]; c = clim(d)[mask]; o = e.astype(float); bs[i] = ((p - o) ** 2).sum(); bc[i] = ((c - o) ** 2).sum(); n_rows += len(b)
    bands = []
    for j, (a, b) in enumerate(BANDS):
        dj = rows[:, j] > 0; v, lo, hi = boot_ratio(ev[dj, j], rows[dj, j], seed=SEED + j)
        o, o_why = band_outcome(lo, hi, (a, b), int(dj.sum()), edge='closed' if j == nb - 1 else '[)')
        # referee R4, display only: the observed share read against the contour level itself (ABOVE if the interval is above it, BELOW if under it)
        lab, lab_why = (None, None) if j == 0 or lo is None or int(dj.sum()) < MIN_DAYS else K.read(lo, hi, bound=a, edge='closed')   # a point figure with no tolerance: never CONSISTENT
        # referee bootstrap note, display only: whole calendar years resampled instead of days
        yv = None
        if j in (3,) and int(dj.sum()) >= MIN_DAYS:
            ys_ = sorted(set(yr_of)); yn = np.array([ev[[k for k in range(len(days)) if yr_of[k] == y_], j].sum() for y_ in ys_]); yd = np.array([rows[[k for k in range(len(days)) if yr_of[k] == y_], j].sum() for y_ in ys_])
            if len(ys_) >= 5: _, ylo, yhi = boot_ratio(yn, yd, seed=SEED + 50 + j); yv = dict(lo=round(ylo, 5), hi=round(yhi, 5), **dict(zip(('outcome', 'reason'), band_outcome(ylo, yhi, (a, b), int(dj.sum()), edge='closed' if j == nb - 1 else '[)'))))
        bands.append(dict(label_reading=lab, label_reason=lab_why, year_blocks=yv, band=BAND_NAMES[j], lo_stated=a, hi_stated=b, rows=int(rows[:, j].sum()), days=int(dj.sum()), events=int(ev[:, j].sum()),
                          freq=None if v is None else round(v, 5), lo=None if lo is None else round(lo, 5), hi=None if hi is None else round(hi, 5), outcome=o, reason=o_why))
    dj = s_rows > 0; v, lo, hi = boot_ratio(s_ev[dj], s_rows[dj], seed=SEED + 99)
    hatched = dict(rows=int(s_rows.sum()), days=int(dj.sum()), events=int(s_ev.sum()), freq=None if v is None else round(v, 5), lo=None if lo is None else round(lo, 5), hi=None if hi is None else round(hi, 5),
                   **dict(zip(('outcome', 'reason'), band_outcome(lo, hi, (0.10, 1.0), int(dj.sum()), edge='closed'))))
    hatched['unrated_as_ef2_upper'] = round(float(s_evu.sum() / s_rows.sum()), 5) if s_rows.sum() else None
    if prelim and not any(t['mag'] >= 0 for t in tors if t['src'] == 'prelim'):
        hatched.update(outcome=K.CANNOT_TELL, reason=K.NO_INTERVAL_FORMABLE, why='no preliminary report carries a rating, so an EF2 or stronger tornado cannot be told apart')
    v, lo, hi = boot_bss(bs, bc, seed=SEED + 7)
    brier = dict(bs=round(float(bs.sum() / n_rows), 6) if n_rows else None, bs_clim=round(float(bc.sum() / n_rows), 6) if n_rows else None,
                 bss=None if v is None else round(v, 4), lo=None if lo is None else round(lo, 4), hi=None if hi is None else round(hi, 4), **dict(zip(('outcome', 'reason'), bss_outcome(lo, hi))))
    cnt = C.Counter(x['outcome'] for x in bands)
    return dict(cell=name, preliminary=prelim, days=len(days), points=int(mask.sum()), rows=n_rows, bands=bands, hatched=hatched, brier=brier,
                band_outcomes={k: cnt.get(k, 0) for k in K.OUTCOMES}, first_day=days[0] if days else None, last_day=days[-1] if days else None)

# ---------------- 5. warnings ----------------
def fy_bounds(fy): return calendar.timegm((fy - 1, 10, 1, 0, 0, 0)), calendar.timegm((fy, 10, 1, 0, 0, 0))
fy_now = this_year + (1 if int(time.strftime('%m', time.gmtime(NOW))) >= 10 else 0)
WARN = {}; warn_bad = 0; warn_all = 0; warn_missing = []
for fy in range(FY_FIRST, fy_now + 1):
    a, b = fy_bounds(fy); f = 'data/raw/warnings/to_fy%d.geojson' % fy
    ok = fetch_to(f, IEM_SBW % (time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime(a)), time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime(b))), max_age_h=(20 if fy == fy_now else None), must=lambda x: x[:1] == b'{')
    if not ok: warn_missing.append(fy); continue
    try: fs = json.load(open(f))['features']
    except Exception: warn_missing.append(fy); continue
    ws = []
    for ft in fs:
        p = ft.get('properties', {}); g = ft.get('geometry') or {}; warn_all += 1
        if 'utc_issue' not in p or 'utc_expire' not in p or g.get('type') not in ('Polygon', 'MultiPolygon'): warn_bad += 1; continue
        if p.get('status', 'NEW') != 'NEW': continue
        polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        rings = [r for poly in polys for r in poly]; allp = np.array([pt[:2] for r in rings for pt in r])
        _pe = p.get('utc_polygon_end') or p['utc_expire']
        ws.append(dict(pend=min(float(ep(_pe)), float(ep(p['utc_expire']))), issue=float(ep(p['utc_issue'])), expire=float(ep(p['utc_expire'])), paths=ring_paths([[tuple(pt[:2]) for pt in r] for r in rings]),
                       bbox=(allp[:, 0].min(), allp[:, 1].min(), allp[:, 0].max(), allp[:, 1].max()), wfo=p.get('wfo'), pid=p.get('product_id'), eventid=p.get('eventid')))
    ws.sort(key=lambda w: w['issue']); WARN[fy] = ws
def fy_read(fy, W_=None):
    WARN = W_ or globals()['WARN']
    a, b = fy_bounds(fy); ws = WARN.get(fy)
    if ws is None: return None
    pre = fy > FY_LAST_CLOSED
    ts = [t for t in tors if a <= t['t0'] < b and ((t['src'] == 'db' and t['t0'] < calendar.timegm((LAST_CLOSED + 1, 1, 1, 0, 0, 0))) or (t['src'] == 'prelim' and pre))]
    iss = np.array([w['issue'] for w in ws]); verified = set(); per = []
    # warnings issued before the fiscal year can still cover its first tornadoes: take the neighbouring year's last warnings too
    prev = [w for w in WARN.get(fy - 1, []) if w['expire'] > a]; pool = prev + ws; off = len(prev)
    piss = np.array([w['issue'] for w in pool]); pexp = np.array([w['expire'] for w in pool])
    for t in ts:
        t1 = t['t1'] or t['t0']; idx = np.nonzero((piss <= t1) & (pexp > t['t0']))[0]
        cand = [pool[i] for i in idx]; pew, lead, l0, ver = warn_tornado(t, cand)
        for j in ver:
            k = idx[j] - off
            if k >= 0: verified.add(int(k))
        per.append((day_of(t['t0'], 12), pew, lead, l0))
    # tornadoes after the year's end can verify a warning issued inside it
    nxt = [t for t in tors if b <= t['t0'] < b + 6 * 3600 and ((t['src'] == 'db') == (t['t0'] < calendar.timegm((LAST_CLOSED + 1, 1, 1, 0, 0, 0))))]
    for t in nxt:
        t1 = t['t1'] or t['t0']; idx = np.nonzero((iss <= t1) & (np.array([w['expire'] for w in ws]) > t['t0']))[0]
        if len(idx): _, _, _, ver = warn_tornado(t, [ws[i] for i in idx]); verified |= {int(idx[j]) for j in ver}
    dpod = C.defaultdict(lambda: [0.0, 0.0, 0.0, 0]); dfar = C.defaultdict(lambda: [0, 0])
    for dd, pew, lead, l0 in per: x = dpod[dd]; x[0] += pew; x[1] += lead; x[2] += l0; x[3] += 1
    for i, w in enumerate(ws): x = dfar[day_of(w['issue'], 12)]; x[0] += (i not in verified); x[1] += 1
    return dict(fy=fy, preliminary=pre, tornadoes=len(per), warnings=len(ws), verified=len(verified), dpod=dict(dpod), dfar=dict(dfar))
def goals_from(parts, label, pre):
    dpod = C.defaultdict(lambda: [0.0, 0.0, 0.0, 0]); dfar = C.defaultdict(lambda: [0, 0])
    for p in parts:
        for k, v in p['dpod'].items():
            x = dpod[k]; x[0] += v[0]; x[1] += v[1]; x[2] += v[2]; x[3] += v[3]
        for k, v in p['dfar'].items(): x = dfar[k]; x[0] += v[0]; x[1] += v[1]
    ks = sorted(dpod); n = [dpod[k][3] for k in ks]
    pod = boot_ratio([dpod[k][0] for k in ks], n, seed=SEED + 11); lead = boot_ratio([dpod[k][1] for k in ks], n, seed=SEED + 12); l0 = boot_ratio([dpod[k][2] for k in ks], n, seed=SEED + 13)
    kf = sorted(dfar); far = boot_ratio([dfar[k][0] for k in kf], [dfar[k][1] for k in kf], seed=SEED + 14)
    def pack(v, kind, goal, nd=4):
        return dict(value=None if v[0] is None else round(v[0], nd), lo=None if v[1] is None else round(v[1], nd), hi=None if v[2] is None else round(v[2], nd), goal=goal, **dict(zip(('outcome', 'reason'), goal_outcome(v[1], v[2], goal, kind) if goal is not None else (None, None))))
    return dict(label=label, preliminary=pre, tornadoes=sum(p['tornadoes'] for p in parts), warnings=sum(p['warnings'] for p in parts), verified=sum(p['verified'] for p in parts),
                tornado_days=len(ks), warning_days=len(kf), pod=pack(pod, 'atleast', GOALS['pod']), lead_min=pack(lead, 'atleast', GOALS['lead'], 2), far=pack(far, 'atmost', GOALS['far']),
                initial_lead_min=pack(l0, None, None, 2))

# ---------------- 6. known-good gates ----------------
kg = {}
kg['format'] = fmt_ok and all(k in db_fields for k in NEEDDB) and warn_all > 0 and warn_bad <= 0.01 * warn_all and bool(BAND)
# gate 2: 30 point-days from the stated side, our band against IEM's outlook-by-point answer at one minute after the product issue time
pc_f = 'data/cache/pointcheck.json'; pc = json.load(open(pc_f)) if os.path.exists(pc_f) else {}
rng = random.Random(SEED); cand = [d for d in days_closed if BAND[d].max() > 0]; picks = []
for _ in range(30):
    d = rng.choice(cand); idx = np.nonzero(BAND[d] > 0)[0] if rng.random() < 0.6 else np.arange(NP); i = int(rng.choice(list(idx))); picks.append((d, i))
agree = 0; pc_rows = []
for d, i in picks:
    key = '%s_%.4f_%.4f' % (d, PLAT[i], PLON[i])
    if key not in pc and not OFF and not NOPC:
        v = time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime(ep(prodiss[d]) + 60))
        try: pc[key] = json.loads(get(IEM_PT % (PLAT[i], PLON[i], v)))
        except Exception as e: log('point check failed', key, repr(e)[:80])
    ans = pc.get(key)
    if ans is None: pc_rows.append(dict(day=d, lat=round(float(PLAT[i]), 4), lon=round(float(PLON[i]), 4), ours=float(STATED_P[BAND[d][i]]), iem=None)); continue
    ths = [float(x['threshold']) for x in ans.get('data', []) if x.get('day') == 1 and x.get('outlook_type') == 'C' and x.get('category') == 'TORNADO' and re.match(r'^0\.\d+$', str(x.get('threshold', ''))) and x.get('issue', '').startswith(time.strftime('%Y-%m-%dT13:00', time.strptime(d, '%Y%m%d')))]
    iem = max(ths) if ths else 0.0; ours = float(STATED_P[BAND[d][i]]); agree += abs(iem - ours) < 1e-9
    pc_rows.append(dict(day=d, lat=round(float(PLAT[i]), 4), lon=round(float(PLON[i]), 4), ours=ours, iem=iem))
json.dump(pc, open(pc_f, 'w'))
kg['stated_reader'] = sum(r['iem'] is not None for r in pc_rows) == 30 and agree >= 29
import contextlib
with contextlib.redirect_stdout(io.StringIO()): _kit_ok = K.selftest()
kg['rule'] = rule_selftest()[0] and _kit_ok
GATE = all(kg.values())

# ---------------- 7. readings ----------------
cells = [cell_read(n, days_closed, m) for n, m in CELLS.items()] + [cell_read(n, days_pre, m, prelim=True) for n, m in CELLS.items()]
years = []
for y in range(FIRST_YEAR, LAST_CLOSED + 1):
    c = cell_read('United States %d' % y, [d for d in days_closed if d.startswith(str(y))], CELLS['United States']); c['year'] = y; years.append(c)
fys = [fy_read(fy) for fy in range(FY_FIRST, fy_now + 1)]
warn_years = [goals_from([p], 'FY%d' % p['fy'], p['preliminary']) for p in fys if p]
warn_pooled = goals_from([p for p in fys if p and not p['preliminary']], 'FY%d to FY%d' % (FY_FIRST, FY_LAST_CLOSED), False)
# referee R6, display only: the issuance polygon counted only until its own polygon end (the replacement polygons are not in the file), a floor
WARN_FLOOR = {fy: [dict(w, expire=w['pend']) for w in ws] for fy, ws in WARN.items()}
warn_floor = goals_from([p for p in (fy_read(fy, WARN_FLOOR) for fy in range(FY_FIRST, FY_LAST_CLOSED + 1)) if p], 'FY%d to FY%d, polygon until its polygon end' % (FY_FIRST, FY_LAST_CLOSED), False)
for k in ('pod', 'lead_min', 'far', 'initial_lead_min'): warn_floor[k]['outcome'] = None
def gate_all(obj):
    if GATE: return obj
    if isinstance(obj, dict):
        o = {k: gate_all(v) for k, v in obj.items()}
        if 'outcome' in o and o['outcome'] in K.OUTCOMES: o['outcome_before_gate'] = o['outcome']; o['outcome'] = K.CANNOT_TELL; o['reason'] = K.NO_INTERVAL_FORMABLE   # a failed gate: no reading can be formed (Addendum std2)
        return o
    if isinstance(obj, list): return [gate_all(x) for x in obj]
    return obj
cells, years, warn_years, warn_pooled = gate_all(cells), gate_all(years), gate_all(warn_years), gate_all(warn_pooled)
for c in cells + years: cnt = C.Counter(x['outcome'] for x in c['bands']); c['band_outcomes'] = {k: cnt.get(k, 0) for k in K.OUTCOMES}   # counted after the gate

# REQ-13 (standard 6.7, PLAN_ADDENDUM_std2.md). Failed reads are listed apart and are outside the counts: days with no outlook, unreadable outlook layers, preliminary days not fetched, fiscal years whose warning file was not fetched.
def _rd(x): return (x['outcome'], x.get('reason'))
NR_BANDS = list(nothing['no_outlook']) + list(nothing['outlook_unreadable']) + list(nothing['prelim_missing']); NR_WARN = list(warn_missing)
_us_closed = next(c for c in cells if c['cell'] == 'United States' and not c['preliminary'])
REQ13_HEAD = K.req13([_rd(b) for b in _us_closed['bands']], nothing_returned=NR_BANDS)
_wr = [_rd(w[k]) for w in [warn_pooled] + warn_years for k in ('pod', 'lead_min', 'far')]
REQ13_WARN = K.req13(_wr, nothing_returned=NR_WARN)
REQ13_ALL = K.req13([_rd(b) for c in cells + years for b in c['bands']] + [_rd(c['hatched']) for c in cells] + [_rd(c['brier']) for c in cells] + _wr, nothing_returned=NR_BANDS + NR_WARN)

# ---------------- 8. plan seal and output ----------------
seal_f = 'data/plan_seal.json'
def git(*a): return subprocess.run(['git'] + list(a), cwd=H, capture_output=True, text=True).stdout.strip()
if not os.path.exists(seal_f) and K.plan_committed('PLAN.md', NOW):
    json.dump(dict(plan_commit=git('log', '-1', '--format=%H', '--', 'PLAN.md'), plan_commit_time=git('log', '-1', '--format=%cI', '--', 'PLAN.md'),
                   plan_sha256=hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest(), first_comparison=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW))), open(seal_f, 'w'), indent=1)
seal = json.load(open(seal_f)) if os.path.exists(seal_f) else None
summary = dict(
    desk='TORNADO', publisher='Heuremen LLC', generated=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW)), plan='PLAN.md', plan_seal=seal, plan_unchanged_since_commit=K.plan_committed('PLAN.md'),
    claim=dict(outlook='SPC Day 1 Convective Outlook, 1300 UTC: probability of one or more tornadoes within 25 miles of a point during the outlook period, contours 2, 5, 10, 15, 30, 45, 60 percent, hatched 10 percent or more for EF2 or stronger',
               warnings='NWS GPRA goals as stated in OIG-25-026-I Box 1: POD at least 72 percent, lead time at least 13 minutes, FAR at most 71 percent'),
    frame=dict(issuance='1300 UTC Day 1', closed_years=[FIRST_YEAR, LAST_CLOSED], recent_from='%d-01-01' % (LAST_CLOSED + 1), grid_km=GRID_KM, radius_km=round(RADIUS_KM, 3), grid_points=NP,
               cell_points={k: int(v.sum()) for k, v in CELLS.items()}, alley_states=list(ALLEY), min_days=MIN_DAYS, bootstrap=dict(resamples=NBOOT, seed=SEED, block='day'),
               fiscal_years_closed=[FY_FIRST, FY_LAST_CLOSED]),
    gates=dict(kg, passed=GATE, point_check=dict(agree=agree, of=len(pc_rows), rows=pc_rows)),
    sources=dict(outlook_days_issued=len(issued), outlook_days_read=len(BAND), threshold_outside_set=dict(odd_threshold), database_rows_read=sum(t['src'] == 'db' for t in tors),
                 database_counts=dict(dbc), database_unrated_by_year={str(y): sum(1 for t in tors if t['src'] == 'db' and t['mag'] < 0 and int(day_of(t['t0'], 13)[:4]) == y) for y in range(FIRST_YEAR, LAST_CLOSED + 1)}, database_rows_by_year={str(y): sum(1 for t in tors if t['src'] == 'db' and int(day_of(t['t0'], 13)[:4]) == y) for y in range(FIRST_YEAR, LAST_CLOSED + 1)}, database_unrated_closed=sum(1 for t in tors if t['src'] == 'db' and t['mag'] < 0 and FIRST_YEAR <= int(day_of(t['t0'], 13)[:4]) <= LAST_CLOSED), database_other_time_zone=tz_other, preliminary_days=len(pre_days), preliminary_reports=sum(t['src'] == 'prelim' for t in tors),
                 tornado_placement=dict(placed), warnings_by_fy={str(fy): len(w) for fy, w in WARN.items()}, warnings_missing_fy=warn_missing, warnings_unreadable=warn_bad, stale=STALE),
    nothing_returned=dict(no_outlook_days=len(nothing['no_outlook']), no_outlook_list=nothing['no_outlook'], outlook_unreadable=nothing['outlook_unreadable'], prelim_missing=nothing['prelim_missing'], warnings_missing_fy=warn_missing,
                          no_outlook_other_cycle_1300=nothing['no_outlook_other_cycle_1300'], late_cycle13_scored=nothing['late_cycle13_scored']),
    cells=cells, years=years, warnings=dict(pooled=warn_pooled, years=warn_years, polygon_end_floor=warn_floor, req13=REQ13_WARN), req13=REQ13_HEAD, req13_all=REQ13_ALL,
    after_data_note='label_reading and year_blocks on bands, hatched unrated_as_ef2_upper, warnings polygon_end_floor and nothing_returned no_outlook_other_cycle_1300 and late_cycle13_scored were added after the data on 10 Nov 2026 at the outside referee (tornado_index_referee/REFEREE.md R2, R2b, R4, R5, R6 and the bootstrap note). Display only. No outcome uses them. The grid rectangle was widened at the referee (R1) to keep every point inside the 48 states, as the plan says.')
# the block indahl.ai/forecasters reads (indahl-ai/forecasters.py, rows 'feed'). Display only, the cells above decide. The ten to fifteen percent band of the
# closed years, the headline band, read against the band SPC states. The point is drawn from the band's middle, the outcome is the band rule's.
def _fc_row(c, b):
    return dict(kind='probability', item='%s, stated band %s percent, %d to %d' % (c['cell'], b['band'], FIRST_YEAR, LAST_CLOSED),
                counts='share of point-days in the band with a tornado within twenty-five miles',
                stated=round((b['lo_stated'] + b['hi_stated']) / 2, 4), band=[b['lo_stated'], b['hi_stated']], band_kind='stated',
                n=b['events'], of=b['rows'], delivered=b['freq'], lo=b['lo'], hi=b['hi'], outcome=b['outcome'], reason=b['reason'], req13=REQ13_HEAD,
                interval='day-level block bootstrap, as the desk gives it')
summary['forecasters'] = dict(rows=[_fc_row(c, b) for c in cells if not c['preliminary'] for b in c['bands'] if b['band'] == '10 to 15' and b['lo'] is not None],
                              note='Each row is read against the band SPC states, and its point is drawn from the middle of the band.')
json.dump(summary, open('summary_tornado.json.tmp', 'w'), indent=1); os.replace('summary_tornado.json.tmp', 'summary_tornado.json')
live = dict(summary, updated=summary['generated']); live.pop('years', None)
json.dump(live, open('data/tornado_live.json.tmp', 'w'), separators=(',', ':')); os.replace('data/tornado_live.json.tmp', 'data/tornado_live.json')
if PUB:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'tornado_live', '--path', os.path.join(H, 'data', 'tornado_live.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                       cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
    log('tornado_live', 'published' if p.returncode == 0 else 'publish FAILED ' + (p.stderr or '')[-200:])
    if p.returncode: STALE.append('publish')
with open('data/tornado_history.jsonl', 'a') as f:
    f.write(json.dumps(dict(t=summary['generated'], gate=GATE, cells=[(c['cell'], c['preliminary'], c['band_outcomes'], c['hatched']['outcome'], c['brier']['bss']) for c in cells],
                            warnings=(warn_pooled['pod']['value'], warn_pooled['lead_min']['value'], warn_pooled['far']['value']), stale=STALE)) + '\n')
log('gates', kg)
for c in cells:
    log('%-14s %s days %5d  bands %s  hatched %s  bss %s [%s, %s]' % (c['cell'], 'PRELIM' if c['preliminary'] else 'closed', c['days'], c['band_outcomes'], c['hatched']['outcome'], c['brier']['bss'], c['brier']['lo'], c['brier']['hi']))
    for b in c['bands']: log('    %-12s rows %8d days %5d ev %7d  freq %s [%s, %s] %s' % (b['band'], b['rows'], b['days'], b['events'], b['freq'], b['lo'], b['hi'], b['outcome']))
for w in [warn_pooled] + warn_years: log('%-16s tor %5d warn %5d  POD %s [%s,%s] %s  lead %s %s  FAR %s [%s,%s] %s' % (w['label'], w['tornadoes'], w['warnings'], w['pod']['value'], w['pod']['lo'], w['pod']['hi'], w['pod']['outcome'], w['lead_min']['value'], w['lead_min']['outcome'], w['far']['value'], w['far']['lo'], w['far']['hi'], w['far']['outcome']))
