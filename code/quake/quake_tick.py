#!/usr/bin/env python3
"""quake_tick.py: QUAKE rider (see PLAN.md). Rerunnable. Installs no timer. Reads public USGS sources with no key, one request at a time, paced:
the ComCat event service (earthquake.usgs.gov/fdsnws/event/1) for every event that carries an aftershock forecast product (product type oaf),
every archived version of that product (includesuperseded=true), each version's forecast.json, and the ComCat catalog around each mainshock.
Sets each stated probability and each stated 95% range beside what the catalog shows for the same zone, window and magnitude.
Writes data/quake_rows.json.gz, summary_quake.json, data/quake_live.json and data/quake_history.jsonl.
--offline: cached files only. --publish: also put data/quake_live.json in the site KV as quake_live, served at /quake/live.json.
--selftest: rule checks only, no network. --stated-only: fetch and parse the stated side only, no catalog, no comparison (used before the plan seal)."""
import os, sys, json, time, math, re, gzip, glob, hashlib, subprocess, urllib.request, urllib.parse, random, statistics, collections as C
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
from us_place import is_us   # display only (referee R2)
OFF = '--offline' in sys.argv; PUB = '--publish' in sys.argv; STATED_ONLY = '--stated-only' in sys.argv
UA = 'heuremen-quake/0.1 (+https://indahl.ai/quake)'
FDSN = 'https://earthquake.usgs.gov/fdsnws/event/1/query'
PACE = 1.0; LIST_HOURS = 6; SETTLE_DAYS = 7.0; DAY = 86400000
BOOT = 2000; SEED = 20261110; BLOCK_KM = 100.0; BLOCK_DAYS = 365.0
COVER_CLAIM = 0.95; COVER_BAND = (0.925, 0.975); MIN_ROWS = 30; MIN_BLOCKS = 10
PBINS = (0.0, 0.01, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80, 0.90, 0.99, 1.0)
GATE3_TOL_ABS = 2; GATE3_TOL_REL = 0.2; GATE3_SHARE = 0.8; GATE3_MIN = 20
WINDOWS = ('1 Day', '1 Week', '1 Month', '1 Year')
for d in ('data', 'data/raw', 'data/raw/detail', 'data/raw/forecast', 'data/raw/catalog'): os.makedirs(d, exist_ok=True)
NOW = time.time(); NOW_MS = int(NOW * 1000); STAMP = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(NOW))
def log(*a): print('quake:', *a, file=sys.stderr)
_last = [0.0]; STALE = []
def get(url, tries=3, timeout=300):
    """One request at a time, at least PACE seconds apart, backing off on errors."""
    err = None
    for a in range(tries):
        w = PACE - (time.time() - _last[0])
        if w > 0: time.sleep(w)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=timeout) as r: b = r.read()
            _last[0] = time.time(); return b
        except Exception as e:
            _last[0] = time.time(); err = e
            if getattr(e, 'code', 0) in (400, 404, 204): break
            time.sleep(5 * (a + 1) ** 2)
    raise RuntimeError('fetch failed %s: %r' % (url[:140], err))
def fnum(x):
    try:
        v = float(x); return v if math.isfinite(v) else None
    except Exception: return None
def inum(x):
    v = fnum(x); return int(v) if v is not None and v == int(v) else None
def iso(ms): return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(ms / 1000))
def km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km on a sphere of radius 6371 km (haversine)."""
    p1, p2 = math.radians(lat1), math.radians(lat2); dp = p2 - p1; dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(min(1.0, math.sqrt(a)))

# ---------------- the rules (PLAN.md, Rules) ----------------
def row_cover(count, nmin, nmax):
    """Stated 95% range [nmin, nmax] against the count. CONSISTENT inside, ABOVE more than nmax, BELOW fewer than nmin."""
    if count is None or nmin is None or nmax is None or nmin > nmax: return K.CANNOT_TELL
    if count > nmax: return K.ABOVE
    if count < nmin: return K.BELOW
    return K.CONSISTENT
def cover_outcome(lo, hi, n, nb):
    if n < MIN_ROWS or nb < MIN_BLOCKS: return K.CANNOT_TELL
    if hi < COVER_CLAIM: return K.BELOW
    if lo > COVER_CLAIM: return K.ABOVE
    if lo >= COVER_BAND[0] and hi <= COVER_BAND[1]: return K.CONSISTENT
    return K.CANNOT_TELL
def rel_tol(p): return max(0.01, min(0.05, p / 2, (1 - p) / 2))
def rel_outcome(lo, hi, claim, n, nb):
    if n < MIN_ROWS or nb < MIN_BLOCKS or claim is None: return K.CANNOT_TELL
    if lo > claim: return K.ABOVE
    if hi < claim: return K.BELOW
    t = rel_tol(claim)
    if lo >= claim - t and hi <= claim + t: return K.CONSISTENT
    return K.CANNOT_TELL
def pbin(p):
    for i in range(len(PBINS) - 1):
        if PBINS[i] <= p < PBINS[i + 1] or (i == len(PBINS) - 2 and p == 1.0): return i
    return None
def pbin_name(i):
    a, b = PBINS[i], PBINS[i + 1]
    return '%g to %g percent' % (100 * a, 100 * b) + ('' if i == len(PBINS) - 2 else ', not including %g' % (100 * b))
def rule_selftest():
    t = [row_cover(5, 2, 8) == K.CONSISTENT, row_cover(9, 2, 8) == K.ABOVE, row_cover(1, 2, 8) == K.BELOW, row_cover(0, 0, 0) == K.CONSISTENT,
         row_cover(None, 0, 1) == K.CANNOT_TELL, row_cover(1, 3, 2) == K.CANNOT_TELL,
         cover_outcome(0.80, 0.90, 500, 50) == K.BELOW, cover_outcome(0.96, 0.99, 500, 50) == K.ABOVE, cover_outcome(0.93, 0.97, 500, 50) == K.CONSISTENT,
         cover_outcome(0.90, 0.97, 500, 50) == K.CANNOT_TELL, cover_outcome(0.93, 0.97, 20, 50) == K.CANNOT_TELL, cover_outcome(0.93, 0.97, 500, 5) == K.CANNOT_TELL,
         rel_outcome(0.30, 0.40, 0.20, 500, 50) == K.ABOVE, rel_outcome(0.05, 0.10, 0.20, 500, 50) == K.BELOW, rel_outcome(0.17, 0.23, 0.20, 500, 50) == K.CONSISTENT,
         rel_outcome(0.10, 0.26, 0.20, 500, 50) == K.CANNOT_TELL, abs(rel_tol(0.003) - 0.01) < 1e-12, abs(rel_tol(0.5) - 0.05) < 1e-12,
         pbin(0.0) == 0, pbin(0.0099) == 0, pbin(0.01) == 1, pbin(0.995) == 9, pbin(1.0) == 9, pbin(0.5) == 5,
         abs(km(0, 0, 0, 1) - 111.195) < 0.01]
    return all(t), t

if '--selftest' in sys.argv:
    ok, t = rule_selftest(); print('RULE SELFTEST', 'PASSED' if ok else 'FAILED', t); sys.exit(0 if ok and K.selftest() else 1)

# ---------------- 1. the stated side: events with an aftershock forecast, every archived version ----------------
def newest(prefix):
    fs = sorted(glob.glob('data/raw/%s_*.json.gz' % prefix)); return fs[-1] if fs else None
def age_h(f): return 1e9 if not f else (NOW - os.path.getmtime(f)) / 3600
def jload(f): return json.load(gzip.open(f) if f.endswith('.gz') else open(f))
lst_f = newest('oaf_events')
if not OFF and age_h(lst_f) > LIST_HOURS:
    try:
        b = get(FDSN + '?' + urllib.parse.urlencode(dict(format='geojson', producttype='oaf', starttime='2000-01-01', orderby='time-asc', limit=20000)))
        json.loads(b); lst_f = 'data/raw/oaf_events_%s.json.gz' % STAMP; gzip.open(lst_f, 'wb').write(b)
    except Exception as e: log('event list failed', repr(e)[:120]); STALE.append('event list')
if not lst_f: log('no event list'); sys.exit(2)
EVENTS = jload(lst_f)['features']
def detail(ev):
    f = 'data/raw/detail/%s.json' % ev['id']
    have = json.load(open(f)) if os.path.exists(f) else None
    if have and (OFF or have['properties'].get('updated', 0) >= ev['properties'].get('updated', 0)): return have
    if OFF: return have
    try:
        b = get(FDSN + '?' + urllib.parse.urlencode(dict(format='geojson', eventid=ev['id'], includesuperseded='true')))
        d = json.loads(b); open(f + '.tmp', 'wb').write(b); os.replace(f + '.tmp', f); return d
    except Exception as e:
        log('detail failed', ev['id'], repr(e)[:100]); STALE.append('detail ' + ev['id']); return have
def forecast_doc(code, src, ut, contents):
    """forecast.json of one version: inline bytes when the event service carries them, else fetched once from its address (versions never change)."""
    f = 'data/raw/forecast/%s_%s_%d.json' % (code, src, ut)
    if os.path.exists(f): return json.load(open(f)), f
    c = contents.get('forecast.json') or contents.get('')
    if not c: return None, None
    if c.get('bytes') is not None: raw = c['bytes'].encode()
    elif c.get('url') and not OFF:
        try: raw = get(c['url'])
        except Exception as e: log('forecast failed', code, ut, repr(e)[:80]); return None, None
    else: return None, None
    try: d = json.loads(raw)
    except Exception: return None, None
    open(f + '.tmp', 'wb').write(raw); os.replace(f + '.tmp', f); return d, f
def zone_of(doc):
    p = ((doc.get('model') or {}).get('parameters') or {})
    rt = p.get('regionType')
    if rt is None: return None, 'zone not stated'
    if rt == 'circle':
        lat, lon, r = fnum(p.get('regionCenterLat')), fnum(p.get('regionCenterLon')), fnum(p.get('regionRadius'))
        if None in (lat, lon, r): return None, 'zone not readable'
        return dict(type='circle', lat=lat, lon=lon, r_km=r), None
    if rt == 'rectangle':
        a = [fnum(p.get(k)) for k in ('regionMinLat', 'regionMaxLat', 'regionMinLon', 'regionMaxLon')]
        if None in a: return None, 'zone not readable'
        return dict(type='rectangle', min_lat=a[0], max_lat=a[1], min_lon=a[2], max_lon=a[3]), None
    return None, 'zone not readable'
def zone_of_data(code, src, ut, contents, why):
    """When forecast.json states no zone, the same version's forecast_data.json may: parameters.aftershock_search_region (a circle, km) and min_depth/max_depth (km)."""
    c = contents.get('forecast_data.json')
    if not c: return None, why
    f = 'data/raw/forecast/%s_%s_%d_data.json' % (code, src, ut)
    if os.path.exists(f): d = json.load(open(f))
    elif OFF or not c.get('url'): return None, why
    else:
        try: raw = get(c['url']); d = json.loads(raw); open(f + '.tmp', 'wb').write(raw); os.replace(f + '.tmp', f)
        except Exception as e: log('forecast_data failed', code, ut, repr(e)[:80]); return None, why
    P = d.get('parameters') or {}; R = P.get('aftershock_search_region') or {}
    if not R: return None, 'zone not stated'
    if 'SphRegionCircle' not in R or not isinstance(R.get('center'), dict): return None, 'zone not readable'
    lat, lon, r = fnum(R['center'].get('lat')), fnum(R['center'].get('lon')), fnum(R.get('radius'))
    if None in (lat, lon, r): return None, 'zone not readable'
    return dict(type='circle', lat=lat, lon=lon, r_km=r, min_depth=fnum(P.get('min_depth')), max_depth=fnum(P.get('max_depth')), from_file='forecast_data.json'), None
def in_zone(z, lat, lon, depth=None):
    if depth is not None and z.get('min_depth') is not None and z.get('max_depth') is not None and not (z['min_depth'] <= depth <= z['max_depth']): return False
    if z['type'] == 'circle': return km(z['lat'], z['lon'], lat, lon) <= z['r_km']
    lo = ((lon - z['min_lon']) % 360.0); w = ((z['max_lon'] - z['min_lon']) % 360.0) or 360.0
    return z['min_lat'] <= lat <= z['max_lat'] and lo <= w
def zone_reach(z, lat, lon):
    """km from the mainshock to the far edge of the zone (for the catalog query circle)."""
    if z['type'] == 'circle': return km(lat, lon, z['lat'], z['lon']) + z['r_km']
    return max(km(lat, lon, a, b) for a in (z['min_lat'], z['max_lat']) for b in (z['min_lon'], z['max_lon']))

SEQ = []; VERS = []; MISSING = C.Counter(); FIRST_SEEN = {}
for ev in EVENTS:
    d = detail(ev)
    if not d: MISSING['detail not read'] += 1; continue
    pr = d['properties']; g = d['geometry']['coordinates']
    ids = set(x for x in (pr.get('ids') or '').split(',') if x)
    s = dict(id=d['id'], time=pr['time'], mag=fnum(pr.get('mag')), lat=g[1], lon=g[0], depth=g[2], net=pr.get('net'), place=pr.get('place'), ids=sorted(ids), title=pr.get('title'), us=is_us(pr.get('place'), pr.get('title')))
    SEQ.append(s)
    for v in pr['products'].get('oaf', []):
        ut = v['updateTime']; base = dict(seq=s['id'], source=v.get('source'), code=v.get('code'), issued=ut, indexed=v.get('indexTime'), status=v.get('status'))
        if v.get('status') == 'DELETE': VERS.append(dict(base, missing='deleted')); continue
        doc, f = forecast_doc(v.get('code'), v.get('source'), ut, v.get('contents') or {})
        if doc is None: VERS.append(dict(base, missing='forecast not read')); continue
        z, zwhy = zone_of(doc)
        if z is None: z, zwhy = zone_of_data(v.get('code'), v.get('source'), ut, v.get('contents') or {}, zwhy)
        VERS.append(dict(base, file=f, created=inum(doc.get('creationTime')), model=(doc.get('model') or {}).get('name'), zone=z, zone_why=zwhy, doc=doc,
                         advisory=doc.get('advisoryTimeFrame'), template=doc.get('template')))
log('events', len(SEQ), 'versions', len(VERS))

# ---------------- 2. blocks for the bootstrap (PLAN.md: epicentres within 100 km and times within 365 days are one block) ----------------
par = list(range(len(SEQ)))
def find(i):
    while par[i] != i: par[i] = par[par[i]]; i = par[i]
    return i
for i in range(len(SEQ)):
    for j in range(i + 1, len(SEQ)):
        a, b = SEQ[i], SEQ[j]
        if abs(a['time'] - b['time']) <= BLOCK_DAYS * DAY and km(a['lat'], a['lon'], b['lat'], b['lon']) <= BLOCK_KM: par[find(i)] = find(j)
BLOCK = {SEQ[i]['id']: SEQ[find(i)]['id'] for i in range(len(SEQ))}
SEQD = {s['id']: s for s in SEQ}

# ---------------- 3. rows: one per version, window and magnitude ----------------
rows = []; frame = C.Counter()
for v in VERS:
    if v.get('missing'): continue
    doc = v['doc']; fc = doc.get('forecast')
    if not isinstance(fc, list) or not fc: v['missing'] = 'no forecast windows'; continue
    for w in fc:
        t0, t1, lab = inum(w.get('timeStart')), inum(w.get('timeEnd')), w.get('label')
        items = [(fnum(b.get('magnitude')), fnum(b.get('probability')), inum(b.get('p95minimum')), inum(b.get('p95maximum')), 'bin') for b in (w.get('bins') or [])]
        am = w.get('aboveMainshockMag')
        if isinstance(am, dict): items.append((fnum(am.get('magnitude')), fnum(am.get('probability')), None, None, 'above mainshock'))
        for mag, p, nmin, nmax, kind in items:
            r = dict(seq=v['seq'], block=BLOCK[v['seq']], issued=v['issued'], indexed=v.get('indexed'), us=SEQD[v['seq']]['us'], created=v['created'], window=lab, t0=t0, t1=t1, mag=mag, p=p, nmin=nmin, nmax=nmax, kind=kind,
                     model=v['model'], zone=v['zone'], net=SEQD[v['seq']]['net'], file=v['file'])
            if t0 is None or t1 is None or mag is None or p is None or not (0 <= p <= 1) or (kind == 'bin' and (nmin is None or nmax is None or nmin > nmax)):
                r.update(status='scored_no', outcome=K.CANNOT_TELL, why='unreadable')
            elif v['issued'] > t0: r.update(status='outside', why='issued after the window opened')
            elif v['zone'] is None: r.update(status='scored_no', outcome=K.CANNOT_TELL, why=v['zone_why'])
            elif t1 + SETTLE_DAYS * DAY > NOW_MS: r.update(status='scored_no', outcome=K.NOTHING_RETURNED, why='window not closed')
            else: r.update(status='pending')
            rows.append(r)
outside = [r for r in rows if r['status'] == 'outside']; rows = [r for r in rows if r['status'] != 'outside']
# display only (added 10 Nov 2026 after the stated-side read, before any comparison): how late after its windows opened a version went public
_lv = sorted(set((r['seq'], r['issued'], r['t0']) for r in outside)); _lag = sorted((i - t) / 60000 for s_, i, t in _lv)
LATE = dict(versions=len(set((s_, i) for s_, i, t in _lv)), versions_parsed=sum(1 for v in VERS if not v.get('missing')), median_minutes=round(statistics.median(_lag), 1) if _lag else None,
            within_15_minutes=sum(1 for x in _lag if x <= 15), over_one_day=sum(1 for x in _lag if x > 1440))
log('rows', len(rows), 'issued after the window opened', len(outside))
if STATED_ONLY:
    zc = C.Counter((v.get('zone') or {}).get('type') or v.get('zone_why') or v.get('missing') for v in VERS)
    print(json.dumps(dict(events=len(SEQ), versions=len(VERS), zones=dict(zc), blocks=len(set(BLOCK.values())), rows=len(rows), outside=len(outside),
                          status={'%s|%s' % k: v for k, v in C.Counter((r['status'], r.get('why')) for r in rows).most_common()}), default=str, indent=1)); sys.exit(0)

# ---------------- 4. the delivered side: the ComCat catalog around each mainshock ----------------
CIDX_F = 'data/raw/catalog/index.json'; CIDX = json.load(open(CIDX_F)) if os.path.exists(CIDX_F) else {}
def catalog(s, vs, rs):
    """Every ComCat earthquake around the mainshock from its time on, out to the far edge of every stated zone, down to 0.05 below the lowest stated magnitude."""
    zs = [v['zone'] for v in vs if v.get('zone')]
    if not zs: return None, None
    reach = min(20000.0, max(zone_reach(z, s['lat'], s['lon']) for z in zs) + 1.0)
    mags = [r['mag'] for r in rs if r['kind'] == 'bin' and r['mag'] is not None]
    minmag = round((min(mags) if mags else 3.0) - 0.05, 2)
    t_end = max([r['t1'] for r in rs if r['t1']] + [s['time']]) + DAY
    q = dict(format='geojson', latitude=s['lat'], longitude=s['lon'], maxradiuskm=round(reach, 1), starttime=iso(s['time'] - 1000), endtime=iso(min(t_end, NOW_MS)),
             minmagnitude=minmag, eventtype='earthquake', orderby='time-asc')
    f = 'data/raw/catalog/%s.json.gz' % s['id']; meta = CIDX.get(s['id'])
    need = [r['t1'] + SETTLE_DAYS * DAY for r in rs if r['status'] == 'pending']
    fresh = meta and os.path.exists(f) and meta.get('query') == q_key(q) and all(meta['fetched'] >= x for x in need)
    if not fresh and not OFF:
        feats = []; off = 1
        try:
            while True:
                b = get(FDSN + '?' + urllib.parse.urlencode(dict(q, limit=20000, offset=off)))
                page = json.loads(b)['features'] if b.strip() else []
                feats += page
                if len(page) < 20000: break
                off += 20000
            gzip.open(f + '.tmp', 'wt').write(json.dumps(dict(query=q, fetched=NOW_MS, features=feats))); os.replace(f + '.tmp', f)
            CIDX[s['id']] = dict(fetched=NOW_MS, query=q_key(q), n=len(feats)); meta = CIDX[s['id']]
        except Exception as e: log('catalog failed', s['id'], repr(e)[:100]); STALE.append('catalog ' + s['id'])
    if not (meta and os.path.exists(f)): return None, None
    doc = json.load(gzip.open(f))
    ev = []
    for x in doc['features']:
        p = x['properties']; c = x['geometry']['coordinates']
        ev.append((p['time'], c[1], c[0], fnum(p.get('mag')), set(i for i in (p.get('ids') or '').split(',') if i), p.get('type'), x['id'], fnum(c[2]) if len(c) > 2 else None))
    return ev, doc['fetched']
def q_key(q): return hashlib.sha256(json.dumps({k: q[k] for k in sorted(q) if k not in ('endtime',)}, sort_keys=True).encode()).hexdigest()[:16]
def count(ev, z, t0, t1, mag, main_ids):
    return sum(1 for (t, la, lo, m, ids, ty, i, dp) in ev if t0 <= t < t1 and m is not None and m >= mag and ty == 'earthquake' and not (ids & main_ids) and in_zone(z, la, lo, dp))
by_seq_v = C.defaultdict(list); by_seq_r = C.defaultdict(list)
for v in VERS: by_seq_v[v['seq']].append(v)
for r in rows: by_seq_r[r['seq']].append(r)
CAT = {}
for s in SEQ:
    ev, fetched = catalog(s, by_seq_v[s['id']], by_seq_r[s['id']])
    CAT[s['id']] = (ev, fetched)
json.dump(CIDX, open(CIDX_F + '.tmp', 'w')); os.replace(CIDX_F + '.tmp', CIDX_F)
for r in rows:
    if r['status'] != 'pending': continue
    ev, fetched = CAT.get(r['seq'], (None, None))
    if ev is None or fetched is None or fetched < r['t1'] + SETTLE_DAYS * DAY: r.update(status='scored_no', outcome=K.NOTHING_RETURNED, why='catalog not read'); continue
    n = count(ev, r['zone'], r['t0'], r['t1'], r['mag'], set(SEQD[r['seq']]['ids']))
    r['count'] = n; r['occurred'] = n >= 1; r['status'] = 'scored'
    r['outcome'] = row_cover(n, r['nmin'], r['nmax']) if r['kind'] == 'bin' else K.CONSISTENT
    r['count_mag_rounded'] = sum(1 for (t, la, lo, m, ids, ty, i, dp) in ev if r['t0'] <= t < r['t1'] and m is not None and round(m + 1e-9, 1) >= r['mag'] and ty == 'earthquake' and not (ids & set(SEQD[r['seq']]['ids'])) and in_zone(r['zone'], la, lo, dp))

# ---------------- 5. known-good gates (PLAN.md) ----------------
kg = {}
parsed = [v for v in VERS if not v.get('missing')]
fmt_ok = sum(1 for v in parsed if isinstance(v['doc'].get('forecast'), list) and v['doc']['forecast'] and all(isinstance(w.get('bins'), list) for w in v['doc']['forecast']))
cat_ok = all(all(isinstance(e[0], int) and e[3] is not None for e in ev[:50]) for ev, f in CAT.values() if ev)
kg['format'] = bool(parsed) and fmt_ok >= 0.95 * len(VERS) and cat_ok
KG_F = 'data/known_good_rows.json'
def reader_gate():
    fs = sorted(v['file'] for v in parsed if v.get('file'))
    if len(fs) < 3: return False, []
    pick = [fs[0], fs[len(fs) // 2], fs[-1]]; out = []
    for f in pick:
        raw = open(f).read()
        m = re.search(r'"forecast"\s*:\s*\[\s*\{.*?"bins"\s*:\s*\[\s*\{(.*?)\}', raw, re.S)
        txt = m.group(1) if m else ''
        def grab(k):
            mm = re.search(r'"%s"\s*:\s*([-0-9.eE]+)' % k, txt); return float(mm.group(1)) if mm else None
        doc = json.load(open(f)); b = doc['forecast'][0]['bins'][0]
        same = all(grab(k) == fnum(b.get(k)) for k in ('magnitude', 'probability', 'p95minimum', 'p95maximum'))
        out.append(dict(file=f, raw={k: grab(k) for k in ('magnitude', 'probability', 'p95minimum', 'p95maximum')}, parsed={k: b.get(k) for k in ('magnitude', 'probability', 'p95minimum', 'p95maximum')}, same=same))
    return all(o['same'] for o in out), out
kg['reader'], kg_rows = reader_gate(); json.dump(kg_rows, open(KG_F, 'w'), indent=1)
g3 = []
for v in parsed:
    obs = {fnum(o.get('magnitude')): inum(o.get('count')) for o in (v['doc'].get('observations') or []) if isinstance(o, dict)}
    if not v.get('zone') or 'Sequence Specific' not in (v.get('model') or '') or not obs.get(3.0) or v.get('created') is None: continue
    ev, fetched = CAT.get(v['seq'], (None, None))
    if not ev or fetched < v['created']: continue
    s = SEQD[v['seq']]; ours = count(ev, v['zone'], s['time'] + 1, v['created'], 3.0, set(s['ids']))
    g3.append(dict(seq=v['seq'], issued=v['issued'], theirs=obs[3.0], ours=ours, agree=abs(ours - obs[3.0]) <= max(GATE3_TOL_ABS, GATE3_TOL_REL * obs[3.0])))
kg['counter'] = len(g3) >= GATE3_MIN and sum(x['agree'] for x in g3) >= GATE3_SHARE * len(g3)
ok, _ = rule_selftest()
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()): kg['rule'] = ok and K.selftest()
GATE = all(kg.values())
if not GATE:
    for r in rows:
        if r['status'] == 'scored': r['outcome_before_gate'] = r['outcome']; r['outcome'] = K.CANNOT_TELL

# ---------------- 6. cells with a sequence-level block bootstrap ----------------
SC = [r for r in rows if r['status'] == 'scored']
BLOCKS = sorted(set(BLOCK.values())); BI = {b: i for i, b in enumerate(BLOCKS)}; NB = len(BLOCKS)
rng = random.Random(SEED); DRAWS = [[rng.randrange(NB) for _ in range(NB)] for _ in range(BOOT)]
def boot(kb, nb):
    sh = []
    for d in DRAWS:
        k = sum(kb[i] for i in d); n = sum(nb[i] for i in d)
        if n: sh.append(k / n)
    if len(sh) < 0.9 * BOOT: return None, None
    sh.sort(); return sh[int(math.floor(0.025 * (len(sh) - 1)))], sh[int(math.ceil(0.975 * (len(sh) - 1)))]
def cover_cell(name, rs):
    rs = [r for r in rs if r['kind'] == 'bin']; kb = [0] * NB; nb = [0] * NB; cnt = C.Counter(r['outcome'] for r in rs)
    for r in rs:
        i = BI[r['block']]; nb[i] += 1; kb[i] += r['outcome'] == K.CONSISTENT
    n = sum(nb); k = sum(kb); wl, wh = K.wilson(k, n); bl, bh = boot(kb, nb) if n else (None, None)
    lo = min(wl, bl) if bl is not None else wl; hi = max(wh, bh) if bh is not None else wh
    nblk = sum(1 for x in nb if x); nseq = len(set(r['seq'] for r in rs))
    o = cover_outcome(lo, hi, n, nblk) if GATE and bl is not None else K.CANNOT_TELL
    return dict(cell=name, scored=n, inside=k, above=cnt[K.ABOVE], below=cnt[K.BELOW], share=round(k / n, 4) if n else None, wilson=[round(wl, 4), round(wh, 4)],
                boot=[round(bl, 4), round(bh, 4)] if bl is not None else None, lo=round(lo, 4), hi=round(hi, 4), claim=COVER_CLAIM, outcome=o, sequences=nseq, blocks=nblk,
                versions=len(set((r['seq'], r['issued']) for r in rs)), range_zero_zero=sum(1 for r in rs if r['nmax'] == 0))
def rel_cell(name, rs):
    kb = [0] * NB; nb = [0] * NB
    for r in rs:
        i = BI[r['block']]; nb[i] += 1; kb[i] += bool(r['occurred'])
    n = sum(nb); k = sum(kb); claim = round(sum(r['p'] for r in rs) / n, 4) if n else None
    wl, wh = K.wilson(k, n); bl, bh = boot(kb, nb) if n else (None, None)
    lo = min(wl, bl) if bl is not None else wl; hi = max(wh, bh) if bh is not None else wh; nblk = sum(1 for x in nb if x)
    o = rel_outcome(lo, hi, claim, n, nblk) if GATE and bl is not None else K.CANNOT_TELL
    return dict(cell=name, scored=n, occurred=k, stated_mean=claim, share=round(k / n, 4) if n else None, wilson=[round(wl, 4), round(wh, 4)],
                boot=[round(bl, 4), round(bh, 4)] if bl is not None else None, lo=round(lo, 4), hi=round(hi, 4), tol=round(rel_tol(claim), 4) if claim is not None else None,
                outcome=o, sequences=len(set(r['seq'] for r in rs)), blocks=nblk)
BIN = [r for r in SC if r['kind'] == 'bin']
headline_cell = cover_cell('M3 and above, every window', [r for r in BIN if r['mag'] == 3.0])
cover_mag = [cover_cell('M%g and above' % m, [r for r in BIN if r['mag'] == m]) for m in (3.0, 4.0, 5.0, 6.0, 7.0)]   # PLAN.md: each magnitude 3 to 7 (a few versions also state M8, counted in the every-magnitude cell)
cover_win = [cover_cell('M3 and above, %s' % w.lower(), [r for r in BIN if r['mag'] == 3.0 and r['window'] == w]) for w in WINDOWS]
cover_all = cover_cell('every magnitude, every window', BIN)
rel_bins = [dict(rel_cell(pbin_name(i), [r for r in BIN if pbin(r['p']) == i]), bin=[PBINS[i], PBINS[i + 1]]) for i in range(len(PBINS) - 1)]
rel_above = rel_cell('at least one as large as the mainshock', [r for r in SC if r['kind'] == 'above mainshock'])
# described, not scored (PLAN.md): the first forecast of each sequence, and the split by the network that located the mainshock
firsts = {}
for r in BIN:
    if r['seq'] not in firsts or r['issued'] < firsts[r['seq']]: firsts[r['seq']] = r['issued']
FIRST = [r for r in BIN if r['issued'] == firsts[r['seq']]]
first_cover = cover_cell('first forecast of each sequence, M3 and above', [r for r in FIRST if r['mag'] == 3.0])
first_rel = [dict(rel_cell(pbin_name(i), [r for r in FIRST if pbin(r['p']) == i]), bin=[PBINS[i], PBINS[i + 1]]) for i in range(len(PBINS) - 1)]
net_cover = [cover_cell('M3 and above, mainshock located by the %s network' % ('USGS national' if nt == 'us' else 'regional'), [r for r in BIN if r['mag'] == 3.0 and ((r['net'] == 'us') == (nt == 'us'))]) for nt in ('us', 'regional')]
# 10 Nov 2026, outside referee (quake_index_referee/REFEREE.md R1, R2, R5, R7): display only, added after the data, never used for an outcome.
# (a) rows stated at 10 percent or more, pooled, split by magnitude and by window. (b) M3 range cell and the 10-percent cell, US and territories against
# elsewhere (us_place.py). (c) each magnitude without rows whose range is 0 to 0. (d) scored rows from versions indexed after their window opened.
HI = [r for r in BIN if r['p'] >= 0.10]
rel10 = [rel_cell(nm, rs) for nm, rs in (('M3 and above', [r for r in HI if r['mag'] == 3.0]), ('M4 and above, M5 and above, M6 and above and M7 and above', [r for r in HI if r['mag'] >= 4.0]))]
rel10 += [rel_cell('every magnitude, %s' % w.lower(), [r for r in HI if r['window'] == w]) for w in WINDOWS]
rel10_all = rel_cell('every magnitude, every window', HI)
region = [dict(region=nm, cover=cover_cell('M3 and above, %s' % nm, [r for r in BIN if r['mag'] == 3.0 and r['us'] == u]), rel10=rel_cell('stated 10 percent or more, %s' % nm, [r for r in HI if r['us'] == u]),
               sequences=sum(1 for x in SEQ if x['us'] == u)) for nm, u in (('United States and territories', True), ('elsewhere', False))]
nonzero = [cover_cell('M%g and above, range not 0 to 0' % m, [r for r in BIN if r['mag'] == m and r['nmax'] > 0]) for m in (3.0, 4.0, 5.0, 6.0, 7.0)]
late_index = dict(rows=sum(1 for r in BIN if r.get('indexed') and r['indexed'] > r['t0']), m3_rows=sum(1 for r in BIN if r['mag'] == 3.0 and r.get('indexed') and r['indexed'] > r['t0']))
brier = round(sum((r['p'] - r['occurred']) ** 2 for r in BIN) / len(BIN), 5) if BIN else None
rounded = dict(rows=len(BIN), same_cover=sum(1 for r in BIN if row_cover(r['count_mag_rounded'], r['nmin'], r['nmax']) == row_cover(r['count'], r['nmin'], r['nmax'])))

# ---------------- 7. plan seal and output ----------------
def _misses():
    best = {}
    for r in BIN:
        if r['outcome'] not in (K.ABOVE, K.BELOW) or r['mag'] != 3.0: continue
        d = abs(r['count'] - (r['nmax'] if r['outcome'] == K.ABOVE else r['nmin']))
        if r['seq'] not in best or d > best[r['seq']][0]: best[r['seq']] = (d, r)
    return [dict({k: r.get(k) for k in ('seq', 'issued', 'window', 't0', 't1', 'mag', 'p', 'nmin', 'nmax', 'count', 'outcome')}, beyond=d) for d, r in sorted(best.values(), key=lambda x: -x[0])[:25]]
seal_f = 'data/plan_seal.json'
def git(*a): return subprocess.run(['git'] + list(a), cwd=H, capture_output=True, text=True).stdout.strip()
if not os.path.exists(seal_f) and K.plan_committed('PLAN.md', NOW):
    json.dump(dict(plan_commit=git('log', '-1', '--format=%H', '--', 'PLAN.md'), plan_commit_time=git('log', '-1', '--format=%cI', '--', 'PLAN.md'),
                   plan_sha256=hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest(), first_comparison=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW))), open(seal_f, 'w'), indent=1)
seal = json.load(open(seal_f)) if os.path.exists(seal_f) else None
nr = C.Counter(r['why'] for r in rows if r.get('outcome') == K.NOTHING_RETURNED)
ct = C.Counter(r['why'] for r in rows if r['status'] == 'scored_no' and r.get('outcome') == K.CANNOT_TELL)
vm = C.Counter(v['missing'] for v in VERS if v.get('missing'))
summary = dict(
    desk='QUAKE', publisher='Heuremen LLC', generated=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW)), plan='PLAN.md', plan_seal=seal, plan_unchanged_since_commit=K.plan_committed('PLAN.md'),
    claim=dict(source='USGS Operational Aftershock Forecasting, ComCat product type oaf', stated_probability='probability of at least one earthquake at or above the magnitude in the window',
               stated_range='the 95% confidence range of the number, prob(N <= Nmin) about 0.025 and prob(N <= Nmax) about 0.975 (USGS scientific background)', cover_claim=COVER_CLAIM),
    frame=dict(settle_days=SETTLE_DAYS, min_rows=MIN_ROWS, min_blocks=MIN_BLOCKS, cover_band=list(COVER_BAND), pbins=list(PBINS), bootstrap=dict(resamples=BOOT, seed=SEED, block_km=BLOCK_KM, block_days=BLOCK_DAYS)),
    gates=dict(kg, passed=GATE, counter_checked=len(g3), counter_agree=sum(x['agree'] for x in g3)),
    sources=dict(events=len(SEQ), versions=len(VERS), versions_parsed=len(parsed), versions_missing=dict(vm), zones=dict(C.Counter((v.get('zone') or {}).get('type') or v.get('zone_why') for v in parsed)),
                 blocks=NB, catalogs=sum(1 for ev, f in CAT.values() if ev is not None), catalog_events=sum(len(ev) for ev, f in CAT.values() if ev), stale=STALE,
                 first_event=iso(min(s['time'] for s in SEQ)) if SEQ else None, last_event=iso(max(s['time'] for s in SEQ)) if SEQ else None),
    rows=dict(total=len(rows), scored=len(SC), scored_bins=len(BIN), issued_after_window_opened=len(outside), late_versions=LATE, nothing_returned=dict(nr), cannot_tell=dict(ct),
              outcomes=dict(C.Counter(r.get('outcome') for r in rows))),
    headline_cell=headline_cell, cover_by_magnitude=cover_mag, cover_by_window=cover_win, cover_all=cover_all, reliability=rel_bins, reliability_above_mainshock=rel_above,
    described=dict(stated_10_percent_or_more=rel10, stated_10_percent_or_more_all=rel10_all, by_region=region, cover_without_zero_ranges=nonzero, indexed_after_window_opened=late_index,
                   after_data_note='stated_10_percent_or_more, by_region, cover_without_zero_ranges and indexed_after_window_opened were added after the data on 10 Nov 2026 at the outside referee (quake_index_referee/REFEREE.md R1, R2, R5, R7). Display only. No outcome uses them.',
                   first_forecast_cover=first_cover, first_forecast_reliability=first_rel, cover_by_network=net_cover, brier_score=brier, magnitude_rounded_check=rounded,
                   counter_gate_rows=g3[:2000]),
    biggest_misses=_misses(),   # display only: the M3 row farthest outside its range, one per sequence
    sequences=[dict(id=s['id'], title=s['title'], time=iso(s['time']), mag=s['mag'], net=s['net'], block=BLOCK[s['id']], versions=len(by_seq_v[s['id']]),
                    scored=sum(1 for r in by_seq_r[s['id']] if r['status'] == 'scored' and r['kind'] == 'bin'),
                    m3_inside=sum(1 for r in by_seq_r[s['id']] if r['status'] == 'scored' and r['kind'] == 'bin' and r['mag'] == 3.0 and r['outcome'] == K.CONSISTENT),
                    m3_scored=sum(1 for r in by_seq_r[s['id']] if r['status'] == 'scored' and r['kind'] == 'bin' and r['mag'] == 3.0)) for s in SEQ])
# the block indahl.ai/forecasters reads (indahl-ai/forecasters.py, rows 'feed'). Display only, the cells above decide. Range coverage against the stated 95 percent.
def _fc_row(c):
    return dict(kind='coverage', item=c['cell'], counts='share of stated ranges that held the aftershock count', stated=c['claim'], consistent_within=list(COVER_BAND),
                n=c['inside'], of=c['scored'], delivered=c['share'], lo=c['lo'], hi=c['hi'], outcome=c['outcome'],
                interval='union of the Wilson and block bootstrap intervals, as the desk gives it')
summary['forecasters'] = dict(rows=[_fc_row(c) for c in [cover_all] + cover_win + cover_mag if c['lo'] is not None],
                              note='CONSISTENT also needs the whole interval within two and a half points of the stated share. The interval is the union of a Wilson interval and a block bootstrap.')
slim = [{k: r.get(k) for k in ('seq', 'block', 'issued', 'window', 't0', 't1', 'mag', 'kind', 'p', 'nmin', 'nmax', 'count', 'count_mag_rounded', 'occurred', 'outcome', 'why', 'status', 'zone', 'model', 'file')} for r in rows + outside]
gzip.open('data/quake_rows.json.gz.tmp', 'wt').write(json.dumps(dict(generated=summary['generated'], rows=slim))); os.replace('data/quake_rows.json.gz.tmp', 'data/quake_rows.json.gz')
json.dump(summary, open('summary_quake.json.tmp', 'w'), indent=1); os.replace('summary_quake.json.tmp', 'summary_quake.json')
live = dict(summary, updated=summary['generated']); live['described'] = {k: v for k, v in summary['described'].items() if k != 'counter_gate_rows'}
json.dump(live, open('data/quake_live.json.tmp', 'w'), separators=(',', ':')); os.replace('data/quake_live.json.tmp', 'data/quake_live.json')
if PUB:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'quake_live', '--path', os.path.join(H, 'data', 'quake_live.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                       cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
    log('quake_live', 'published' if p.returncode == 0 else 'publish FAILED ' + (p.stderr or '')[-200:])
    if p.returncode: STALE.append('publish')
with open('data/quake_history.jsonl', 'a') as f: f.write(json.dumps(dict(t=summary['generated'], gate=GATE, rows=len(rows), scored=len(SC), headline=[headline_cell['inside'], headline_cell['scored'], headline_cell['outcome']], stale=STALE[:20])) + '\n')
log('gates', kg, 'counter', summary['gates']['counter_agree'], 'of', len(g3))
for c in [headline_cell] + cover_mag + cover_win: log('%-40s scored %6d inside %6d above %5d below %5d share %s wilson %s boot %s  %s' % (c['cell'], c['scored'], c['inside'], c['above'], c['below'], c['share'], c['wilson'], c['boot'], c['outcome']))
for c in rel_bins + [rel_above]: log('%-40s n %6d occurred %6d stated %s share %s [%s, %s] %s' % (c['cell'], c['scored'], c['occurred'], c['stated_mean'], c['share'], c['lo'], c['hi'], c['outcome']))
