#!/usr/bin/env python3
"""cone_tick.py: CONE rider (see PLAN.md). Rerunnable. Installs no timer. Reads public NOAA/NHC files with no key, one request at a time, paced:
ATCF a-decks (OFCL official forecasts), HURDAT2 (post-season best track), ATCF b-decks (current-season operational best track), the NHC cone page
(radii) and its Internet Archive copies, NHC's yearly average track error tables. Sets each official forecast position beside the best-track
position and asks whether it fell inside that year's cone circle, and whether the whole five-day path stayed inside the forecast's cone.
Writes data/radii.json, data/stated_errors.json, data/cone.json, summary_cone.json, data/cone_live.json and data/cone_history.jsonl.
--offline: cached files only. --publish: also put data/cone_live.json in the site KV as cone_live, served at /cone/live.json.
--radii: (re)build data/radii.json and data/stated_errors.json from the stated documents only, then stop. --selftest: rule checks only."""
import os, sys, json, time, math, re, gzip, glob, hashlib, random, statistics, subprocess, urllib.request, collections as C
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
OFF = '--offline' in sys.argv; PUB = '--publish' in sys.argv; RADII_ONLY = '--radii' in sys.argv
UA = 'heuremen-cone/0.1 (+https://indahl.ai/cone)'
NHC = 'https://www.nhc.noaa.gov'; FTP = 'https://ftp.nhc.noaa.gov/atcf'
LEADS = (12, 24, 36, 48, 72, 96, 120); TC = {'TD', 'TS', 'HU', 'SD', 'SS'}
R_EARTH_NMI = 3440.065
SEASON_FIRST = 2010
WP_BAND = (0.60, 0.70)                              # NHC: "about 60-70% of the time" (whole 5-day path)
CIRCLE_CLAIM = 2.0 / 3.0; CIRCLE_BAND = (CIRCLE_CLAIM - 0.05, CIRCLE_CLAIM + 0.05)   # our reading of "two-thirds"
B_RESAMPLES = 2000; SEED = 20261110; MIN_STORMS = 10; MIN_ROWS = 30
EP_EAST_OF = -140.0
VER_TOL_NMI = 1.0; VER_TOL_FRAC = 0.02; VER_N_ABS = 2; VER_N_FRAC = 0.05
EDGE_NMI = 4.0
PACE = 0.8; CURRENT_HOURS = 6
INSIDE, OUTSIDE = 'INSIDE', 'OUTSIDE'
for d in ('data', 'data/raw', 'data/raw/adeck', 'data/raw/hurdat', 'data/raw/current', 'data/raw/docs', 'data/raw/docs/aboutcone_wb'): os.makedirs(d, exist_ok=True)
NOW = time.time(); STAMP = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(NOW)); THIS_YEAR = int(time.strftime('%Y', time.gmtime(NOW)))
def log(*a): print('cone:', *a, file=sys.stderr)
_last = [0.0]; STALE = []
def get(url, tries=3, timeout=180):
    err = None
    for a in range(tries):
        w = PACE - (time.time() - _last[0])
        if w > 0: time.sleep(w)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=timeout) as r: b = r.read()
            _last[0] = time.time(); return b
        except Exception as e:
            _last[0] = time.time(); err = e
            if getattr(e, 'code', 0) in (400, 403, 404): break
            time.sleep(5 * (a + 1) ** 2)
    raise RuntimeError('fetch failed %s: %r' % (url[:120], err))
def age_h(f): return 1e9 if not os.path.exists(f) else (NOW - os.path.getmtime(f)) / 3600
def fetch_to(url, f, max_age_h=None):
    """Keep a copy at f. Refetch only when missing or older than max_age_h (None: never refetch)."""
    if OFF or (os.path.exists(f) and (max_age_h is None or age_h(f) < max_age_h)): return os.path.exists(f)
    try: b = get(url); open(f + '.tmp', 'wb').write(b); os.replace(f + '.tmp', f); return True
    except Exception as e: log('fetch FAILED', url, repr(e)[:120]); STALE.append(url.rsplit('/', 1)[-1]); return os.path.exists(f)
def visible(t):
    import html as _h
    t = re.sub(r'(?is)<script.*?</script>|<style.*?</style>', ' ', t); t = re.sub(r'<[^>]+>', ' ', t); return _h.unescape(re.sub(r'\s+', ' ', t))

# ---------------- geometry ----------------
def gc_nmi(la1, lo1, la2, lo2):
    p1, p2 = math.radians(la1), math.radians(la2); dl = math.radians(lo2 - lo1); dp = p2 - p1
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH_NMI * math.asin(min(1.0, math.sqrt(a)))
def bearing(la1, lo1, la2, lo2):
    p1, p2 = math.radians(la1), math.radians(la2); dl = math.radians(lo2 - lo1)
    return math.atan2(math.sin(dl) * math.cos(p2), math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl))
def in_hull_of_two(c1, r1, c2, r2):
    """Origin inside the convex hull of disks (c1, r1) and (c2, r2) in the plane. The hull is the union over t in [0, 1] of the disk with centre
    c1 + t(c2 - c1) and radius r1 + t(r2 - r1). f(t) = |c(t)| - r(t) is convex, so a ternary search finds its minimum."""
    def f(t): return math.hypot(c1[0] + t * (c2[0] - c1[0]), c1[1] + t * (c2[1] - c1[1])) - (r1 + t * (r2 - r1))
    a, b = 0.0, 1.0
    for _ in range(80):
        m1, m2 = a + (b - a) / 3, b - (b - a) / 3
        if f(m1) <= f(m2): b = m2
        else: a = m1
    return min(f(0.0), f(1.0), f((a + b) / 2)) <= 0
def in_cone(pt, circles):
    """pt (lat, lon). circles: list of (lat, lon, radius n mi) along the track. Azimuthal equidistant projection centred on pt."""
    xy = []
    for la, lo, r in circles:
        d = gc_nmi(pt[0], pt[1], la, lo); th = bearing(pt[0], pt[1], la, lo); xy.append(((d * math.sin(th), d * math.cos(th)), r))
    if any(math.hypot(*c) <= r for c, r in xy): return True
    return any(in_hull_of_two(xy[i][0], xy[i][1], xy[i + 1][0], xy[i + 1][1]) for i in range(len(xy) - 1))

# ---------------- readers ----------------
def latlon(s):
    s = s.strip(); m = re.match(r'^(\d+)([NSEW])$', s)
    if not m: return None
    v = int(m.group(1)) / 10.0; return -v if m.group(2) in 'SW' else v
def hlat(s):
    s = s.strip(); m = re.match(r'^(\d+(?:\.\d+)?)([NSEW])$', s)
    if not m: return None
    v = float(m.group(1)); return -v if m.group(2) in 'SW' else v
def wrap(lo): return ((lo + 180.0) % 360.0) - 180.0
def read_adeck(path, tech='OFCL'):
    """-> {dtg: {tau: (lat, lon)}}, duplicates with a different position, unreadable count, lines used."""
    out = C.defaultdict(dict); dup = 0; bad = 0; used = 0
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt', errors='replace') as fh:
        for ln in fh:
            f = [x.strip() for x in ln.split(',')]
            if len(f) < 8 or f[4] != tech: continue
            try: tau = int(f[5])
            except ValueError: bad += 1; continue
            la, lo = latlon(f[6]), latlon(f[7])
            if la is None or lo is None: bad += 1; continue
            used += 1; dtg = f[2]
            if tau in out[dtg]:
                if out[dtg][tau] != (la, wrap(lo)): dup += 1
                continue
            out[dtg][tau] = (la, wrap(lo))
    return out, dup, bad, used
def read_hurdat(path):
    """-> {storm_id: {yyyymmddhh: (lat, lon, status)}} synoptic records only, plus storm names."""
    bt = {}; names = {}; cur = None
    for ln in open(path, errors='replace'):
        f = [x.strip() for x in ln.split(',')]
        if len(f) >= 3 and re.match(r'^[A-Z]{2}\d{6}$', f[0]): cur = f[0]; bt[cur] = {}; names[cur] = f[1]; continue
        if cur is None or len(f) < 6 or not re.match(r'^\d{8}$', f[0]): continue
        if f[1] not in ('0000', '0600', '1200', '1800'): continue
        la, lo = hlat(f[4]), hlat(f[5])
        if la is None or lo is None: continue
        bt[cur][f[0] + f[1][:2]] = (la, wrap(lo), f[3])
    return bt, names
def read_bdeck(path):
    bt = {}
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt', errors='replace') as fh:
        for ln in fh:
            f = [x.strip() for x in ln.split(',')]
            if len(f) < 11 or f[4] != 'BEST' or f[2][-2:] not in ('00', '06', '12', '18') or f[5] not in ('0', '00', '000'): continue
            la, lo = latlon(f[6]), latlon(f[7])
            if la is None or lo is None or f[2] in bt: continue
            bt[f[2]] = (la, wrap(lo), f[10])
    return bt
def add_h(dtg, h):
    t = time.strptime(dtg, '%Y%m%d%H'); import calendar
    return time.strftime('%Y%m%d%H', time.gmtime(calendar.timegm(t) + h * 3600))

# ---------------- stated documents: radii and NHC's yearly error tables ----------------
def parse_radii(text):
    t = visible(text); m = re.search(r'cones? (?:in|for) (\d{4})', t); i = t.find('Forecast Period')
    if not m or i < 0: return None
    seg = t[i:i + 700].replace('2/3', ' '); seg = seg[:seg.find('Example')] if 'Example' in seg else seg
    ncol = seg.count('(nautical miles)'); seg = seg.split('(nautical miles)')[-1]   # 2 columns to 2018 (Atlantic, Eastern North Pacific), 3 in 2019 to 2025 (+ Central), 2 from 2026 (Eastern and Central together)
    nums = [int(x) for x in re.findall(r'\b\d+\b', seg)]
    tab = {}; w = ncol + 1
    for j in range(0, len(nums) - ncol, w):
        lead, a, e = nums[j], nums[j + 1], nums[j + 2]
        if lead in (3, 12, 24, 36, 48, 60, 72, 96, 120) and lead not in tab: tab[lead] = (a, e)
        else: break
    stats = re.search(r'based on error statistics from (\d{4})\s*[-–]\s*(\d{4})', t)
    return dict(year=int(m.group(1)), AL={str(k): v[0] for k, v in tab.items()}, EP={str(k): v[1] for k, v in tab.items()}, stats=(stats.group(1) + '-' + stats.group(2)) if stats else None)
def build_radii():
    out = {}
    live = 'data/raw/docs/aboutcone.shtml'; fetch_to(NHC + '/aboutcone.shtml', live, 24)
    srcs = [(os.path.basename(f)[:14], f, 'https://web.archive.org/web/%s/https://www.nhc.noaa.gov/aboutcone.shtml' % os.path.basename(f)[:14]) for f in sorted(glob.glob('data/raw/docs/aboutcone_wb/*.html'))]
    srcs.append((STAMP, live, NHC + '/aboutcone.shtml'))
    for ts, f, url in srcs:
        r = parse_radii(open(f, errors='replace').read())
        if not r: continue
        y = str(r['year'])
        if all(str(L) in r['AL'] and str(L) in r['EP'] for L in LEADS):
            prev = out.get(y)
            if prev and (prev['AL'], prev['EP']) != (r['AL'], r['EP']): out[y].setdefault('conflicts', []).append(dict(copy=ts, AL=r['AL'], EP=r['EP']))
            if not prev: out[y] = dict(AL=r['AL'], EP=r['EP'], stats=r['stats'], first_copy=ts, url=url)
            out[y]['last_copy'] = ts
    json.dump(out, open('data/radii.json', 'w'), indent=1, sort_keys=True); return out
def build_stated_errors():
    import pypdf
    out = {}
    for basin, name in (('AL', '1989-present_OFCL_ATL_annual_trk_errors.pdf'), ('EP', '1989-present_OFCL_EPAC_annual_trk_errors.pdf')):
        f = 'data/raw/docs/' + name; fetch_to(NHC + '/verification/pdfs/' + name, f, 24 * 7)
        if not os.path.exists(f): continue
        text = '\n'.join(p.extract_text() for p in pypdf.PdfReader(f).pages)
        rows = {}
        for ln in text.splitlines():
            t = ln.split()
            if len(t) == 17 and re.match(r'^(19|20)\d\d$', t[0]):
                v = [float(x) for x in t[1:]]
                rows[t[0]] = {str(L): dict(err=v[2 * i], n=int(v[2 * i + 1])) for i, L in enumerate((0, 12, 24, 36, 48, 72, 96, 120))}
        out[basin] = dict(file=name, url=NHC + '/verification/pdfs/' + name, sha256=hashlib.sha256(open(f, 'rb').read()).hexdigest()[:16],
                          title=' '.join(text.split('\n')[0:3]).strip()[:200], notes=[l.strip() for l in text.splitlines() if re.match(r'^\s*\d\s+[A-Z]', l)][:6], years=rows)
    json.dump(out, open('data/stated_errors.json', 'w'), indent=1, sort_keys=True); return out

# ---------------- the rules (PLAN.md, Rules) ----------------
def circle_outcome(fpos, bpt, radius):
    """fpos (lat, lon) or None. bpt (lat, lon, status) or None. -> (outcome, why, distance)."""
    if fpos is None or radius is None: return K.CANNOT_TELL, 'unreadable', None
    if bpt is None: return None, 'no best-track point', None   # a failed read, no outcome: the row carries read_status NOTHING_RETURNED (PLAN_ADDENDUM_std2.md)
    if bpt[2] not in TC: return None, 'not a tropical cyclone', None
    d = gc_nmi(fpos[0], fpos[1], bpt[0], bpt[1])
    return (INSIDE if d <= radius else OUTSIDE), None, d
def path_outcome(fc, bt, dtg, radii):
    """fc: {tau: (lat, lon)} with tau 0 and all seven leads. -> (outcome, why, first time outside or None)."""
    circles = [(fc[0][0], fc[0][1], 0.0)] + [(fc[L][0], fc[L][1], float(radii[str(L)])) for L in LEADS]
    pts = []
    for h in range(12, 121, 6):
        p = bt.get(add_h(dtg, h))
        if p is None: return None, 'no best-track point', None
        if p[2] not in TC: return None, 'not a tropical cyclone', None
        pts.append((h, p))
    for h, p in pts:
        if not in_cone((p[0], p[1]), circles): return OUTSIDE, None, h
    return INSIDE, None, None
def boot(groups, stat='share', seed=SEED, B=B_RESAMPLES):
    """groups: list of per-storm (k, n) for share, or (sum, n) for mean. Storm-level block bootstrap, percentile 95% interval."""
    g = [x for x in groups if x[1] > 0]
    if not g: return None, None
    rng = random.Random(seed); m = len(g); vals = []
    for _ in range(B):
        k = n = 0
        for _i in range(m):
            a, b = g[rng.randrange(m)]; k += a; n += b
        vals.append(k / n)
    vals.sort(); return vals[int(0.025 * B)], vals[min(B - 1, int(math.ceil(0.975 * B)) - 1)]
def cell_read(rows, band):
    by = C.defaultdict(lambda: [0, 0]); cnt = C.Counter(); why = C.Counter()
    for r in rows:
        cnt[r['outcome']] += 1
        if r.get('why'): why[r['why']] += 1
        if r['outcome'] in (INSIDE, OUTSIDE): by[r['storm']][1] += 1; by[r['storm']][0] += (r['outcome'] == INSIDE)
    k, n = cnt[INSIDE], cnt[INSIDE] + cnt[OUTSIDE]; storms = len(by)
    lo, hi = boot(list(by.values())) if n else (None, None)
    # PLAN_ADDENDUM_std2.md: no rows is NO_INTERVAL_FORMABLE, under 10 storms or 30 rows is TOO_WIDE_TO_RESOLVE (owner decision O3), otherwise K.read on the band with closed edges.
    if n == 0 or lo is None: o, why_ct = K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE
    elif storms < MIN_STORMS or n < MIN_ROWS: o, why_ct = K.CANNOT_TELL, K.TOO_WIDE_TO_RESOLVE
    else: o, why_ct = K.read(lo, hi, band=band, edge='closed')
    nret = sum(1 for r in rows if r.get('read_status') == K.NOTHING_RETURNED)
    return dict(scored=n, inside=k, outside=cnt[OUTSIDE], storms=storms, share=round(k / n, 4) if n else None, lo=None if lo is None else round(lo, 4), hi=None if hi is None else round(hi, 4),
                band=list(band), outcome=o, reason=why_ct, nothing_returned=nret, nothing_returned_why=dict(why), cannot_tell=cnt[K.CANNOT_TELL],
                req13=K.req13([dict(outcome=r['outcome'], reason=r.get('reason')) for r in rows if r['outcome'] in (INSIDE, OUTSIDE, K.CANNOT_TELL)], nothing_returned=nret))
def ver_outcome(ours, n_ours, stated, n_stated):
    if stated is None or n_stated is None or ours is None: return K.CANNOT_TELL, 'missing'
    if abs(n_ours - n_stated) > max(VER_N_ABS, VER_N_FRAC * n_stated): return K.CANNOT_TELL, 'case counts differ'
    tol = max(VER_TOL_NMI, VER_TOL_FRAC * stated)
    o, r, _ = K.read_exact(ours, band=(stated - tol, stated + tol), edge='closed')   # a published mean against a published mean with the plan's tolerance: an interval of zero width (owner decision O1)
    return o, r
def rule_selftest():
    ok = True
    def check(name, c):
        nonlocal ok; ok &= bool(c); print(('OK   ' if c else 'FAIL ') + name)
    check('inside at 20 n mi with radius 30', circle_outcome((20.0, -60.0), (20.0 + 20 / 60, -60.0, 'HU'), 30)[0] == INSIDE)
    check('outside at 40 n mi with radius 30', circle_outcome((20.0, -60.0), (20.0 + 40 / 60, -60.0, 'HU'), 30)[0] == OUTSIDE)
    check('no best-track point is a failed read with no outcome', circle_outcome((20.0, -60.0), None, 30)[:2] == (None, 'no best-track point'))
    check('remnant low is a failed read with no outcome', circle_outcome((20.0, -60.0), (20.0, -60.0, 'LO'), 30)[:2] == (None, 'not a tropical cyclone'))
    check('unreadable is cannot tell', circle_outcome(None, (20.0, -60.0, 'HU'), 30)[0] == K.CANNOT_TELL)
    check('distance one degree of latitude is 60 n mi', abs(gc_nmi(10, -50, 11, -50) - 60.04) < 0.1)
    circ = [(20.0, -60.0, 0.0), (20.0, -62.0, 30.0), (20.0, -64.0, 60.0)]
    check('point on the track between circles is in the cone', in_cone((20.0, -61.0), circ))
    check('point 50 n mi off the track at 63 W is outside the cone (hull half-width about 47 there)', not in_cone((20.0 + 50 / 60, -63.0), circ))
    check('point 40 n mi off the track at 63 W is in the cone (hull half-width about 47)', in_cone((20.0 + 40 / 60, -63.0), circ))
    check('point far away is not in the cone', not in_cone((25.0, -61.0), circ))
    dtg = '2020080100'; fc = {0: (20.0, -60.0)}; bt = {}
    for i, L in enumerate(LEADS): fc[L] = (20.0, -60.0 - L / 12.0)
    for h in range(0, 121, 6): bt[add_h(dtg, h)] = (20.0, -60.0 - h / 12.0, 'HU')
    rad = {str(L): 20 + L for L in LEADS}
    check('a path on the forecast track is inside', path_outcome(fc, bt, dtg, rad)[0] == INSIDE)
    bt2 = dict(bt); bt2[add_h(dtg, 66)] = (24.0, -65.5, 'HU')
    check('a path that leaves at 66 h is outside at 66', path_outcome(fc, bt2, dtg, rad)[0::2] == (OUTSIDE, 66))
    bt3 = dict(bt); del bt3[add_h(dtg, 114)]
    check('a path whose track ends is a failed read with no outcome', path_outcome(fc, bt3, dtg, rad)[0] is None)
    check('cell reads: under 10 storms is TOO_WIDE_TO_RESOLVE, empty is NO_INTERVAL_FORMABLE, straddling is STRADDLES_EDGE', cell_read([], WP_BAND)['reason'] == K.NO_INTERVAL_FORMABLE and cell_read([dict(storm='A', outcome=INSIDE)] * 40, WP_BAND)['reason'] == K.TOO_WIDE_TO_RESOLVE and cell_read([dict(storm='S%d' % (i % 20), outcome=INSIDE if i % 20 < 13 else OUTSIDE) for i in range(400)], WP_BAND)['reason'] == K.STRADDLES_EDGE)
    rng = random.Random(1); g = [(1 if rng.random() < 0.67 else 0, 1) for _ in range(800)]; k = sum(a for a, b in g)
    lo, hi = boot(g); wl, wh = K.wilson(k, 800)
    check('bootstrap with one row per storm is close to Wilson (%.3f %.3f vs %.3f %.3f)' % (lo, hi, wl, wh), abs(lo - wl) < 0.012 and abs(hi - wh) < 0.012)
    check('verification rule: 1 n mi off on 40 is consistent', ver_outcome(41.0, 100, 40.0, 100)[0] == K.CONSISTENT)
    check('verification rule: 5 n mi off on 40 is above', ver_outcome(45.0, 100, 40.0, 100)[0] == K.ABOVE)
    check('verification rule: ours on the band edge is consistent, closed', ver_outcome(41.0, 100, 40.0, 100)[0] == K.CONSISTENT and ver_outcome(40.0 + 1.0, 100, 40.0, 100)[0] == K.CONSISTENT)
    check('verification rule: case counts 10 percent apart is cannot tell', ver_outcome(40.0, 90, 40.0, 100) == (K.CANNOT_TELL, 'case counts differ'))
    check('heuremen_kit self-test', K.selftest())
    return ok
if '--selftest' in sys.argv: sys.exit(0 if rule_selftest() else 1)

if RADII_ONLY:
    r = build_radii(); s = build_stated_errors()
    for y in sorted(r): log(y, r[y]['stats'], 'AL', [r[y]['AL'][str(L)] for L in LEADS], 'EP', [r[y]['EP'][str(L)] for L in LEADS], 'conflicts' if r[y].get('conflicts') else '')
    for b in s: log(b, 'stated years', min(s[b]['years']), 'to', max(s[b]['years']))
    sys.exit(0)

# ---------------- 1. stated side ----------------
RADII = build_radii() if not OFF else json.load(open('data/radii.json'))
STATED_ERR = build_stated_errors() if not OFF else json.load(open('data/stated_errors.json'))
# a-decks: archived seasons once, the current season from aid_public (refreshed at most every CURRENT_HOURS)
def season_files(y):
    d = 'data/raw/adeck/%d' % y; os.makedirs(d, exist_ok=True)
    if y < THIS_YEAR:
        if not OFF and not glob.glob(d + '/a*.dat.gz'):
            try:
                idx = get('%s/archive/%d/' % (FTP, y)).decode()
                for n in sorted(set(re.findall(r'href="(a(?:al|ep)[0-8]\d%d\.dat\.gz)"' % y, idx))): fetch_to('%s/archive/%d/%s' % (FTP, y, n), d + '/' + n)
            except Exception as e: log('archive index FAILED', y, repr(e)[:100]); STALE.append('archive %d' % y)
        return sorted(glob.glob(d + '/a*.dat.gz'))
    d = 'data/raw/current'
    idx_f = d + '/aid_public_index.html'; fetch_to(FTP + '/aid_public/', idx_f, CURRENT_HOURS)
    names = sorted(set(re.findall(r'href="(a(?:al|ep)[0-8]\d%d\.dat\.gz)"' % y, open(idx_f, errors='replace').read()))) if os.path.exists(idx_f) else []
    for n in names: fetch_to('%s/aid_public/%s' % (FTP, n), d + '/' + n, CURRENT_HOURS)
    return sorted(glob.glob(d + '/a*%d.dat.gz' % y))

# ---------------- 2. delivered side ----------------
def newest_hurdat():
    f_idx = 'data/raw/hurdat/index.html'; fetch_to(NHC + '/data/hurdat/', f_idx, 24)
    names = re.findall(r'href="(hurdat2-(?:nepac-)?\d{4}-(\d{4})-(\d{6,8})\.txt)"', open(f_idx, errors='replace').read()) if os.path.exists(f_idx) else []
    best = {}
    for n, last, stamp in names:
        basin = 'EP' if 'nepac' in n else 'AL'
        dt = (int(stamp[4:]) if len(stamp) == 8 else 2000 + int(stamp[4:]), int(stamp[:2]), int(stamp[2:4]))
        if basin not in best or (int(last), dt) > best[basin][0]: best[basin] = ((int(last), dt), n, int(last))
    out = {}
    for basin, (_, n, last) in best.items():
        if fetch_to(NHC + '/data/hurdat/' + n, 'data/raw/hurdat/' + n): out[basin] = dict(file=n, last_season=last)
    if not out:   # offline fallback: newest file on disk
        for f in sorted(glob.glob('data/raw/hurdat/hurdat2-*.txt')):
            n = os.path.basename(f); out['EP' if 'nepac' in n else 'AL'] = dict(file=n, last_season=int(re.search(r'-(\d{4})-\d{6,8}\.txt', n).group(1)))
    return out
HURDAT = newest_hurdat()
BT = {}; NAMES = {}; BT_SRC = {}
for basin, h in HURDAT.items():
    bt, nm = read_hurdat('data/raw/hurdat/' + h['file'])
    for sid, v in bt.items():
        if sid[:2] == basin: BT[sid] = v; NAMES[sid] = nm[sid]; BT_SRC[sid] = 'HURDAT2'
FINAL_LAST = {b: h['last_season'] for b, h in HURDAT.items()}
SEASONS = list(range(SEASON_FIRST, THIS_YEAR + 1))
def bdeck_for(sid):
    """Operational best track for a season HURDAT2 does not yet hold."""
    y = int(sid[4:]); n = 'b%s%s%d.dat' % (sid[:2].lower(), sid[2:4], y); f = 'data/raw/current/' + n
    url = ('%s/btk/%s' % (FTP, n)) if y == THIS_YEAR else ('%s/archive/%d/%s.gz' % (FTP, y, n))
    fetch_to(url, f, CURRENT_HOURS if y == THIS_YEAR else None)
    return read_bdeck(f) if os.path.exists(f) else None

# ---------------- 3. rows ----------------
rows = []; paths = []; frame_out = C.Counter(); dups = 0; bad_lines = 0; short = C.Counter(); missing_lead = C.Counter(); files_read = 0; tau0 = []
radius_missing = set(); d60 = C.defaultdict(list)
for y in SEASONS:
    for f in season_files(y):
        sid = os.path.basename(f)[1:9].upper(); basin = sid[:2]
        final = y <= FINAL_LAST.get(basin, 0)
        bt = BT.get(sid) if final else bdeck_for(sid)
        if not final and bt is not None: BT_SRC[sid] = 'b-deck'
        fc_all, dup, bad, used = read_adeck(f); dups += dup; bad_lines += bad; files_read += 1
        rad = (RADII.get(str(y)) or {}).get(basin)
        for dtg in sorted(fc_all):
            fc = fc_all[dtg]
            if 0 not in fc: frame_out['no tau 0 position'] += 1; continue
            if not bt: frame_out['no best track for this storm'] += 1; continue
            b0 = bt.get(dtg)
            if b0 is None: frame_out['no best-track point at the initial time'] += 1; continue
            if b0[2] not in TC: frame_out['not a tropical cyclone at the initial time'] += 1; continue
            if basin == 'EP' and not (EP_EAST_OF < fc[0][1] <= 0): frame_out['East Pacific forecast west of 140 W'] += 1; continue
            tau0.append(gc_nmi(fc[0][0], fc[0][1], b0[0], b0[1]))
            grp = 'final' if final else 'current'
            if rad is None: radius_missing.add(y); frame_out['forecasts in a season without cone radii (second ruler only)'] += 1
            for L in LEADS:
                if L not in fc: missing_lead[L] += 1; continue
                vt = add_h(dtg, L); bv = bt.get(vt)
                o, why, d = circle_outcome(fc[L], bv, rad[str(L)] if rad else 1e9)
                if rad is None: o, why = 'NO_RADII', 'no cone radii for the season'
                rows.append(dict(storm=sid, basin=basin, season=y, grp=grp, dtg=dtg, lead=L, fc=fc[L], bt=bv, radius=rad[str(L)] if rad else None, dist=None if d is None else round(d, 2),
                                 tc_both=bool(bv and bv[2] in TC and d is not None), outcome=o, why=why, reason=(K.NO_INTERVAL_FORMABLE if o == K.CANNOT_TELL else None), read_status=(K.NOTHING_RETURNED if o is None else None)))
            if 60 in fc:   # display only, added after the data (10 Nov 2026): the 60 h recount, set beside second-ruler rows whose case counts differ
                v60 = bt.get(add_h(dtg, 60))
                if v60 and v60[2] in TC: d60[(basin, y)].append(gc_nmi(fc[60][0], fc[60][1], v60[0], v60[1]))
            if rad is None: continue
            if all(L in fc for L in LEADS):
                o, why, h = path_outcome(fc, bt, dtg, rad)
                paths.append(dict(storm=sid, basin=basin, season=y, grp=grp, dtg=dtg, outcome=o, why=why, first_outside_h=h, read_status=(K.NOTHING_RETURNED if o is None else None)))
            else: short[basin] += 1
log('files', files_read, 'rows', len(rows), 'paths', len(paths), 'frame out', dict(frame_out))

# ---------------- 4. gates ----------------
kg = {}
kg['format'] = files_read > 0 and bad_lines == 0 and bool(BT) and all(all(str(L) in RADII[y][b] for L in LEADS for b in ('AL', 'EP')) for y in RADII)
def reader_gate():
    """Three OFCL and three HURDAT2 positions read from raw text with a separate expression, against the parsed values. Rows picked once, stored."""
    kf = 'data/known_good_rows.json'
    if not os.path.exists(kf):
        pick = []; rng = random.Random(7)
        for f in rng.sample(sorted(glob.glob('data/raw/adeck/20*/a*.dat.gz')), 3):
            ls = [l for l in gzip.open(f, 'rt', errors='replace') if re.search(r',\s*OFCL,\s*24,', l)]
            pick.append(dict(kind='adeck', file=f, line=rng.choice(ls).rstrip('\n')))
        hf = sorted(glob.glob('data/raw/hurdat/hurdat2-1851-*.txt'))[-1]
        ls = [l for l in open(hf) if re.match(r'^20(1\d|2[0-5])\d{4}, (00|06|12|18)00,', l)]
        for l in rng.sample(ls, 3): pick.append(dict(kind='hurdat', file=hf, line=l.rstrip('\n')))
        json.dump(pick, open(kf, 'w'), indent=1)
    ok = True
    for p in json.load(open(kf)):
        if p['kind'] == 'adeck':
            m = re.match(r'^\s*(\w\w),\s*(\d+),\s*(\d{10}),\s*\d+,\s*OFCL,\s*24,\s*(\d+)N,\s*(\d+)W', p['line'])
            sid = (m.group(1) + m.group(2) + m.group(3)[:4]).upper(); want = (int(m.group(4)) / 10, -int(m.group(5)) / 10)
            got = read_adeck(p['file'])[0].get(m.group(3), {}).get(24)
            ok &= got is not None and abs(got[0] - want[0]) < 1e-9 and abs(got[1] - want[1]) < 1e-9
        else:
            m = re.match(r'^(\d{8}), (\d\d)00,\s*\w?,\s*(\w\w),\s*([\d.]+)N,\s*([\d.]+)W', p['line'])
            key = m.group(1) + m.group(2); want = (float(m.group(4)), -float(m.group(5)), m.group(3))
            got = [v[key] for sid, v in BT.items() if key in v and abs(v[key][0] - want[0]) < 1e-9 and abs(v[key][1] - want[1]) < 1e-9]
            ok &= len(got) >= 1 and got[0][2] == want[2]
    return ok
kg['reader'] = reader_gate()
kg['join'] = bool(tau0) and statistics.median(tau0) < 15.0
kg['rule'] = rule_selftest() if '--quiet-rule' not in sys.argv else True
GATE = all(kg.values())
if not GATE:
    log('GATE FAILED', kg)
    for r in rows + paths:
        if r['outcome'] in (INSIDE, OUTSIDE): r['outcome_before_gate'] = r['outcome']; r['outcome'] = K.CANNOT_TELL; r['why'] = 'gate failed'; r['reason'] = K.NO_INTERVAL_FORMABLE

# ---------------- 5. cells ----------------
BN = {'AL': 'Atlantic', 'EP': 'East Pacific'}
def sel(rs, **kw): return [r for r in rs if r['outcome'] != 'NO_RADII' and all(r[k] == v for k, v in kw.items())]
cells = []
for b in ('AL', 'EP'):
    c = cell_read(sel(paths, basin=b, grp='final'), WP_BAND); c.update(cell='%s, whole path' % BN[b], basin=b, kind='whole path', lead=None); cells.append(c)
for b in ('AL', 'EP'):
    for L in LEADS:
        rs = sel(rows, basin=b, grp='final', lead=L); c = cell_read(rs, CIRCLE_BAND)
        ds = sorted(r['dist'] for r in rs if r['outcome'] in (INSIDE, OUTSIDE))
        c.update(cell='%s, %d h' % (BN[b], L), basin=b, kind='circle', lead=L, median_nmi=round(statistics.median(ds), 1) if ds else None,
                 near_edge=round(sum(1 for r in rs if r['dist'] is not None and r['outcome'] in (INSIDE, OUTSIDE) and abs(r['dist'] - r['radius']) <= EDGE_NMI) / len(ds), 4) if ds else None,
                 forecasts_without_lead=None)
        cells.append(c)
by_season = []
for y in SEASONS:
    for b in ('AL', 'EP'):
        grp = 'final' if y <= FINAL_LAST.get(b, 0) else 'current'
        e = dict(season=y, basin=b, best_track='HURDAT2' if grp == 'final' else 'operational b-deck', radii=RADII.get(str(y), {}).get(b), radii_stats=RADII.get(str(y), {}).get('stats'))
        e['whole_path'] = cell_read(sel(paths, basin=b, season=y), WP_BAND)
        e['circles'] = {str(L): cell_read(sel(rows, basin=b, season=y, lead=L), CIRCLE_BAND) for L in LEADS}
        by_season.append(e)
current = [e for e in by_season if e['best_track'] != 'HURDAT2']

# ---------------- 6. second ruler: NHC's stated average track errors ----------------
ver = []
for b in ('AL', 'EP'):
    yrs = (STATED_ERR.get(b) or {}).get('years', {})
    for y in range(SEASON_FIRST, FINAL_LAST.get(b, 0) + 1):
        for L in LEADS:
            rs = [r for r in rows if r['basin'] == b and r['season'] == y and r['lead'] == L and r['tc_both']]   # every season, with or without radii
            by = C.defaultdict(lambda: [0.0, 0])
            for r in rs: by[r['storm']][0] += r['dist']; by[r['storm']][1] += 1
            ours = round(sum(r['dist'] for r in rs) / len(rs), 1) if rs else None
            st = (yrs.get(str(y)) or {}).get(str(L)) or {}
            o, why = ver_outcome(ours, len(rs), st.get('err'), st.get('n'))
            vreason = K.NO_INTERVAL_FORMABLE if o == K.CANNOT_TELL else None   # missing value or case counts that differ: the planned comparison cannot be formed
            lo, hi = boot(list(by.values())) if rs else (None, None)
            tol = None if st.get('err') is None else round(max(VER_TOL_NMI, VER_TOL_FRAC * st['err']), 2)
            ver.append(dict(basin=b, season=y, lead=L, ours=ours, n_ours=len(rs), stated=st.get('err'), n_stated=st.get('n'), band=None if tol is None else [round(st['err'] - tol, 2), round(st['err'] + tol, 2)],
                            ours_lo=None if lo is None else round(lo, 1), ours_hi=None if hi is None else round(hi, 1), outcome=o, reason=vreason, why=why))
ver_tally = {b: dict(C.Counter(v['outcome'] for v in ver if v['basin'] == b)) for b in ('AL', 'EP')}
for v in ver:   # display only, after the data: our 60 h recount beside each row whose case counts differ. Decides nothing.
    if v['why'] == 'case counts differ':
        x = d60.get((v['basin'], v['season'])) or []
        v['ours_60h'] = dict(mean=round(sum(x) / len(x), 1) if x else None, n=len(x))

# ---------------- 7. plan seal and output ----------------
seal_f = 'data/plan_seal.json'
def git(*a): return subprocess.run(['git'] + list(a), cwd=H, capture_output=True, text=True).stdout.strip()
if not os.path.exists(seal_f) and K.plan_committed('PLAN.md', NOW):
    json.dump(dict(plan_commit=git('log', '-1', '--format=%H', '--', 'PLAN.md'), plan_commit_time=git('log', '-1', '--format=%cI', '--', 'PLAN.md'),
                   plan_sha256=hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest(), first_comparison=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW))), open(seal_f, 'w'), indent=1)
seal = json.load(open(seal_f)) if os.path.exists(seal_f) else None
outside_paths = sorted([p for p in paths if p['grp'] == 'final' and p['outcome'] == OUTSIDE], key=lambda p: p['dtg'])
summary = dict(
    desk='CONE', publisher='Heuremen LLC', generated=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW)), plan='PLAN.md', plan_seal=seal, plan_unchanged_since_commit=K.plan_committed('PLAN.md'),
    claim=dict(source='NOAA National Hurricane Center', whole_path='Historical data indicate that the entire 5-day path of the center of the tropical cyclone will remain within the cone about 60-70% of the time.',
               circle='The size of each circle is set so that two-thirds of historical official forecast errors over a 5-year sample fall within the circle.',
               whole_path_band=list(WP_BAND), circle_claim=round(CIRCLE_CLAIM, 4), circle_band_our_reading=[round(x, 4) for x in CIRCLE_BAND]),
    frame=dict(seasons_first=SEASON_FIRST, final_last=FINAL_LAST, leads=list(LEADS), ep_east_of=EP_EAST_OF, b_resamples=B_RESAMPLES, seed=SEED, min_storms=MIN_STORMS, min_rows=MIN_ROWS),
    gates=dict(kg, passed=GATE, tau0_median_nmi=round(statistics.median(tau0), 1) if tau0 else None, tau0_n=len(tau0)),
    sources=dict(hurdat=HURDAT, adeck_files=files_read, radii_years=sorted(RADII), radii_missing=sorted(radius_missing), stated_errors={b: dict(file=v['file'], sha256=v['sha256'], years=[min(v['years']), max(v['years'])]) for b, v in STATED_ERR.items()},
                 duplicate_ofcl_positions=dups, unreadable_lines=bad_lines, stale=STALE, frame_out=dict(frame_out), forecasts_shorter_than_five_days=dict(short), forecasts_without_lead={str(k): v for k, v in missing_lead.items()}),
    rows=dict(circle=sum(1 for r in rows if r['outcome'] != 'NO_RADII'), second_ruler_only=sum(1 for r in rows if r['outcome'] == 'NO_RADII'), paths=len(paths), storms=len(set(r['storm'] for r in rows)), circle_outcomes=dict(C.Counter(r['outcome'] for r in rows if r['grp'] == 'final' and r['outcome'] not in (None, 'NO_RADII'))), circle_failed_reads=sum(1 for r in rows if r['grp'] == 'final' and r.get('read_status')),
              path_outcomes=dict(C.Counter(p['outcome'] for p in paths if p['grp'] == 'final' and p['outcome'])), path_failed_reads=sum(1 for p in paths if p['grp'] == 'final' and p.get('read_status')), first_forecast=min((r['dtg'] for r in rows), default=None), last_forecast=max((r['dtg'] for r in rows), default=None)),
    radii=RADII, cells=cells, by_season=by_season, current=current, verification=ver, verification_tally=ver_tally,
    after_data_note='ours_60h on second-ruler rows whose case counts differ was added after the data on 10 Nov 2026 (first read). Display only. No outcome uses it.',
    outside_paths_first_hour=dict(C.Counter(str(p['first_outside_h']) for p in outside_paths)), storm_names={s: NAMES.get(s) for s in sorted(set(r['storm'] for r in rows))})
# the block indahl.ai/forecasters reads (indahl-ai/forecasters.py, rows 'feed'). Display only, the cells above decide. Each row carries the band its
# outcome rule reads against: NHC's own 60 to 70 percent for the whole path, our reading of two-thirds for the circles. The point is drawn from the band's middle.
def _fc_row(c):
    wp = c['kind'] == 'whole path'
    return dict(kind='coverage', item=c['cell'] if wp else '%s circle' % c['cell'],
                counts=('share of official forecasts whose best-track positions stayed inside the cone for the whole path' if wp else 'share of official forecasts whose best-track position at that lead fell inside the lead circle'),
                stated=round((WP_BAND[0] + WP_BAND[1]) / 2, 4) if wp else round(CIRCLE_CLAIM, 4),
                band=list(WP_BAND) if wp else [round(x, 4) for x in CIRCLE_BAND], band_kind='stated' if wp else 'rule', band_by=None if wp else 'ours',
                n=c['inside'], of=c['scored'], delivered=c['share'], lo=c['lo'], hi=c['hi'], outcome=c['outcome'],
                interval='storm-level block bootstrap, as the desk gives it')
summary['forecasters'] = dict(rows=[_fc_row(c) for c in cells if c['lo'] is not None],
                              note='The whole path is read against the band NHC states and the circles against two-thirds read as a band, our reading. Each point is drawn from the middle of its band.')
json.dump(dict(generated=summary['generated'], rows=rows, paths=paths), open('data/cone.json.tmp', 'w')); os.replace('data/cone.json.tmp', 'data/cone.json')
json.dump(summary, open('summary_cone.json.tmp', 'w'), indent=1); os.replace('summary_cone.json.tmp', 'summary_cone.json')
live = dict({k: v for k, v in summary.items() if k not in ('storm_names', 'by_season')}, updated=summary['generated'])
json.dump(live, open('data/cone_live.json.tmp', 'w'), separators=(',', ':')); os.replace('data/cone_live.json.tmp', 'data/cone_live.json')
if PUB:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'cone_live', '--path', os.path.join(H, 'data', 'cone_live.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                       cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
    log('cone_live', 'published' if p.returncode == 0 else 'publish FAILED ' + (p.stderr or '')[-200:])
    if p.returncode: STALE.append('publish')
with open('data/cone_history.jsonl', 'a') as f: f.write(json.dumps(dict(t=summary['generated'], gate=GATE, rows=len(rows), paths=len(paths), cells=[(c['cell'], c['scored'], c['inside'], c['outcome']) for c in cells], stale=STALE)) + '\n')
log('gates', kg)
for c in cells: log('%-24s storms %4d scored %6d inside %6d  share %s [%s, %s]  NR %5d  %s' % (c['cell'], c['storms'], c['scored'], c['inside'], c['share'], c['lo'], c['hi'], c['nothing_returned'], c['outcome']))
log('verification', ver_tally)
for e in current: log('current', e['season'], e['basin'], e['whole_path']['scored'], e['whole_path']['inside'], e['whole_path']['outcome'])
