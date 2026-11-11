#!/usr/bin/env python3
"""neo_tick.py: NEO rider (see PLAN.md). Rerunnable. Installs no timer. Reads public sources with no key, one request at a time, paced:
JPL SBDB Close-Approach Data API (current record and our own dated copies), JPL SBDB API (latest solution facts), JPL Sentry API (stored, not scored),
Internet Archive Wayback Machine (archived copies of Close-Approach responses). Sets each close-approach distance range stated from an earlier
orbit solution beside the latest solution's distance. Writes data/neo.json, summary_neo.json, data/snapshots/*.json.gz and data/neo_history.jsonl.
--offline: cached files only, no new copy. --publish: also put data/neo_live.json in the site KV as neo_live, served at /neo/live.json. --no-sbdb: skip the latest-solution facts (no SBDB read and no kept SBDB answer, a display field only). The designation lookups kept in data/cache/des_*.json are Close-Approach answers for renamed or numbered objects that the matching needs, so --offline reads them and no flag skips them. --selftest: rule checks only, no network."""
import os, sys, json, time, math, re, gzip, glob, hashlib, statistics, subprocess, urllib.request, urllib.parse, collections as C
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
OFF = '--offline' in sys.argv; NOSBDB = '--no-sbdb' in sys.argv; PUB = '--publish' in sys.argv   # --publish: also put neo_live into the site KV (10 Nov 2026, ship)
UA = 'heuremen-neo/0.1 (+https://indahl.ai/neo)'
CAD = 'https://ssd-api.jpl.nasa.gov/cad.api'; SBDB = 'https://ssd-api.jpl.nasa.gov/sbdb.api'; SENTRY = 'https://ssd-api.jpl.nasa.gov/sentry.api'
CDX = 'https://web.archive.org/cdx/search/cdx?url=ssd-api.jpl.nasa.gov/cad.api*&from=2024&output=json&fl=timestamp,original,statuscode,length&filter=statuscode:200&limit=100000'
CAD_VERSION = '1.5'; NEED = ('des', 'orbit_id', 'jd', 'dist', 'dist_min', 'dist_max')
FRAME_DIST = 0.05; FRAME_JD = 2460310.5          # 2024-01-01 00:00
MATCH_DAYS = 10.0; WIDE = 0.05; CLAIM = 0.9973; CONSISTENT_FLOOR = 0.98; MIN_ROWS = 10
PACE = 1.5; SNAP_HOURS = 6; SENTRY_HOURS = 24; SBDB_CAP = 150
for d in ('data', 'data/raw', 'data/raw/wayback', 'data/cache', 'data/cache/sbdb', 'data/snapshots'): os.makedirs(d, exist_ok=True)
NOW = time.time(); NOW_JD = NOW / 86400 + 2440587.5; STAMP = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(NOW))
def log(*a): print('neo:', *a, file=sys.stderr)
_last = [0.0]; STALE = []
def get(url, tries=3, timeout=180):
    """One request at a time, at least PACE seconds apart, backing off on errors (JPL fair use policy)."""
    err = None
    for a in range(tries):
        w = PACE - (time.time() - _last[0])
        if w > 0: time.sleep(w)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=timeout) as r: b = r.read()
            _last[0] = time.time(); return b
        except Exception as e:
            _last[0] = time.time(); err = e
            if getattr(e, 'code', 0) in (400, 404): break          # a refused request is not retried
            time.sleep(5 * (a + 1) ** 2)
    raise RuntimeError('fetch failed %s: %r' % (url[:120], err))
def fnum(x):
    try:
        v = float(x); return v if math.isfinite(v) else None
    except Exception: return None
def _cal(ts):
    import calendar
    return calendar.timegm(time.strptime(ts[:14], '%Y%m%d%H%M%S')) / 86400 + 2440587.5
def iso_of_jd(jd): return time.strftime('%Y-%m-%d %H:%M', time.gmtime((jd - 2440587.5) * 86400))
def tsig_minutes(s):
    """'13:02' -> 782, '2_09:08' -> 3428, '< 00:01' -> None (a bound, not a value)."""
    if not s or '<' in s: return None
    m = re.match(r'^\s*(?:(\d+)_)?(\d+):(\d+)\s*$', s)
    return (int(m.group(1) or 0) * 1440 + int(m.group(2)) * 60 + int(m.group(3))) if m else None

# ---------------- the rule (PLAN.md, Rules) ----------------
def row_outcome(s, d, now_jd):
    """s: stated dict (orbit_id, jd, dist, dist_min, dist_max). d: delivered dict or None. Returns (outcome, why)."""
    lo, hi = s.get('dist_min'), s.get('dist_max')
    if s.get('dist') is None or lo is None or hi is None or lo > hi or s.get('jd') is None: return K.CANNOT_TELL, 'unreadable'
    if s['jd'] > now_jd: return K.NOTHING_RETURNED, 'approach not yet passed'
    if d is None: return K.CANNOT_TELL, 'no record'
    a, b = d.get('dist_min'), d.get('dist_max')
    if d.get('dist') is None or a is None or b is None or a > b: return K.CANNOT_TELL, 'unreadable'
    if str(d.get('orbit_id')) == str(s.get('orbit_id')): return K.CANNOT_TELL, 'same solution'
    if hi - lo > WIDE: return K.CANNOT_TELL, 'wide range'
    if a > hi: return K.ABOVE, None
    if b < lo: return K.BELOW, None
    if a >= lo and b <= hi: return K.CONSISTENT, None
    return K.CANNOT_TELL, 'edge'
def cell_outcome(k, n):
    lo, hi = K.wilson(k, n)
    if n < MIN_ROWS: o = K.CANNOT_TELL
    elif hi < CLAIM: o = K.BELOW
    elif lo > CLAIM: o = K.ABOVE
    elif lo >= CONSISTENT_FLOOR: o = K.CONSISTENT
    else: o = K.CANNOT_TELL
    return o, lo, hi
def rule_selftest():
    S = dict(orbit_id='3', jd=100.0, dist=0.015, dist_min=0.010, dist_max=0.020)
    def D(lo, hi, oid='7'): return dict(orbit_id=oid, jd=100.0, dist=(lo + hi) / 2, dist_min=lo, dist_max=hi)
    t = [(row_outcome(S, D(0.030, 0.031), 200) == (K.ABOVE, None)), (row_outcome(S, D(0.004, 0.005), 200) == (K.BELOW, None)),
         (row_outcome(S, D(0.012, 0.013), 200) == (K.CONSISTENT, None)), (row_outcome(S, D(0.019, 0.021), 200) == (K.CANNOT_TELL, 'edge')),
         (row_outcome(S, D(0.012, 0.013, '3'), 200) == (K.CANNOT_TELL, 'same solution')), (row_outcome(S, None, 200) == (K.CANNOT_TELL, 'no record')),
         (row_outcome(dict(S, dist_min=0.001, dist_max=0.060), D(0.012, 0.013), 200) == (K.CANNOT_TELL, 'wide range')),
         (row_outcome(dict(S, dist_min=None), D(0.012, 0.013), 200) == (K.CANNOT_TELL, 'unreadable')),
         (row_outcome(dict(S, dist_min=0.03), D(0.012, 0.013), 200) == (K.CANNOT_TELL, 'unreadable')),
         (row_outcome(S, D(0.012, 0.013), 50) == (K.NOTHING_RETURNED, 'approach not yet passed')),
         cell_outcome(200, 200)[0] == K.CONSISTENT, cell_outcome(150, 200)[0] == K.BELOW, cell_outcome(40, 40)[0] == K.CANNOT_TELL, cell_outcome(5, 5)[0] == K.CANNOT_TELL,
         tsig_minutes('2_09:08') == 3428, tsig_minutes('13:02') == 782, tsig_minutes('< 00:01') is None]
    return all(t), t
if '--selftest' in sys.argv:
    ok, t = rule_selftest(); print('rule selftest', 'PASSED' if ok else 'FAILED', t); sys.exit(0 if ok and K.selftest() else 1)

def parse_cad(doc):
    """A Close-Approach response -> list of dict rows, or None if it is not a data response in the known format."""
    if not isinstance(doc, dict) or 'Close Approach' not in str(doc.get('signature', {}).get('source', '')): return None
    f = doc.get('fields'); data = doc.get('data')
    if not f or data is None or any(n not in f for n in NEED): return None
    if 'body' in f: data = [r for r in data if r[f.index('body')] == 'Earth']
    out = []
    for r in data:
        x = dict(zip(f, r))
        out.append(dict(des=str(x['des']).split('|')[-1].strip(),   # the www form prints 'packed|designation'
                         orbit_id=str(x['orbit_id']), jd=fnum(x['jd']), cd=x.get('cd'), dist=fnum(x['dist']), dist_min=fnum(x['dist_min']),
                        dist_max=fnum(x['dist_max']), t_sigma_f=x.get('t_sigma_f'), h=fnum(x.get('h')), fullname=(x.get('fullname') or '').strip() or None))
    return out

# ---------------- 1. stated side, part one: archived copies ----------------
cdx_f = 'data/raw/wayback/cdx_cad_api.json'
if not OFF:
    try: b = get(CDX, timeout=240); json.loads(b); open(cdx_f + '.tmp', 'wb').write(b); os.replace(cdx_f + '.tmp', cdx_f)
    except Exception as e: log('wayback index fetch FAILED, using last copy', repr(e)[:140]); STALE.append('wayback index')
cdx = json.load(open(cdx_f))[1:] if os.path.exists(cdx_f) else []
copies = []; wb = C.Counter()
for ts, orig, sc, ln in cdx:
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(orig).query); body = (q.get('body') or ['Earth'])[0]
    f = 'data/raw/wayback/cad_%s_%s.json' % (ts, hashlib.sha1(orig.encode()).hexdigest()[:8])
    if not os.path.exists(f) and not OFF:
        try: b = get('https://web.archive.org/web/%sid_/%s' % (ts, orig), tries=2, timeout=90); json.loads(b); open(f, 'wb').write(b)
        except Exception as e: log('archived copy not fetched', ts, repr(e)[:100])
    if not os.path.exists(f): wb['not fetched'] += 1; continue
    try: doc = json.load(open(f))
    except Exception: wb['does not parse'] += 1; continue
    if body != 'Earth': wb['other body'] += 1; continue
    rows = parse_cad(doc)
    if rows is None: wb['count only or other format'] += 1; continue
    wb['used'] += 1; copies.append(dict(src='wayback', ts=ts, jd=_cal(ts), url='https://web.archive.org/web/%s/%s' % (ts, orig), file=f, version=doc['signature'].get('version'), rows=rows))

# ---------------- 2. stated side, part two: our own copies; and the Sentry lists (stored, not scored) ----------------
def newest(prefix):
    fs = sorted(glob.glob('data/snapshots/%s_2*.json.gz' % prefix)); return fs[-1] if fs else None
def age_h(f): return 1e9 if not f else (NOW_JD - _cal(re.search(r'_(\d{8}T\d{6})Z', f).group(1).replace('T', ''))) * 24
def store(prefix, url):
    b = get(url); doc = json.loads(b); doc['_fetched'] = STAMP; doc['_url'] = url
    f = 'data/snapshots/%s_%s.json.gz' % (prefix, STAMP)
    with gzip.open(f + '.tmp', 'wt') as g: json.dump(doc, g)
    os.replace(f + '.tmp', f); return f
if not OFF:
    if age_h(newest('cad')) >= SNAP_HOURS:
        try:
            d0 = time.strftime('%Y-%m-%d', time.gmtime(NOW - 60 * 86400)); log('own copy stored', store('cad', CAD + '?date-min=%s&date-max=%%2B60&dist-max=0.2&fullname=true' % d0))
        except Exception as e: log('own copy FAILED', repr(e)[:140]); STALE.append('own close-approach copy')
    if age_h(newest('sentry')) >= SENTRY_HOURS:
        try: store('sentry', SENTRY); store('sentry_removed', SENTRY + '?removed=1')
        except Exception as e: log('sentry copy FAILED', repr(e)[:140]); STALE.append('sentry copy')
own = 0
for f in sorted(glob.glob('data/snapshots/cad_*.json.gz')):
    try: doc = json.load(gzip.open(f, 'rt'))
    except Exception: continue
    rows = parse_cad(doc)
    if rows is None: continue
    ts = re.search(r'_(\d{8}T\d{6})Z', f).group(1).replace('T', ''); own += 1
    copies.append(dict(src='own', ts=ts, jd=_cal(ts), url=None, file=f, version=doc['signature'].get('version'), rows=rows))
sentry_now = None
for p in ('sentry', 'sentry_removed'):
    f = newest(p)
    if f:
        try: sentry_now = dict(sentry_now or {}, **{p: dict(file=f, count=int(json.load(gzip.open(f, 'rt')).get('count')))})
        except Exception: pass

# ---------------- 3. delivered side: the current record ----------------
def cached(name, fn):
    f = os.path.join('data/raw', name)
    if not OFF:
        try: v = fn(); json.dump(v, open(f + '.tmp', 'w')); os.replace(f + '.tmp', f); return v
        except Exception as e: log('fetch FAILED, using last copy', name, repr(e)[:140]); STALE.append(name)
    return json.load(open(f)) if os.path.exists(f) else None
cur_doc = cached('cad_current.json', lambda: json.loads(get(CAD + '?date-min=2024-01-01&date-max=now&dist-max=0.5&fullname=true', timeout=300)))
cur_rows = parse_cad(cur_doc) if cur_doc else None
cur_version = (cur_doc or {}).get('signature', {}).get('version')
by_des = C.defaultdict(list)
for r in cur_rows or []: by_des[r['des']].append(r)
def nearest(des, jd, pool=None):
    best = None
    for r in (pool if pool is not None else by_des.get(des, [])):
        if r['jd'] is not None and abs(r['jd'] - jd) <= MATCH_DAYS and (best is None or abs(r['jd'] - jd) < abs(best['jd'] - jd)): best = r
    return best
def by_designation(des, jd):
    """An object that has since been numbered or renamed is listed under its new designation. The API resolves the old one."""
    f = 'data/cache/des_%s_%d.json' % (re.sub(r'\W+', '_', des), round(jd))
    if os.path.exists(f) and (OFF or NOW - os.path.getmtime(f) < 7 * 86400): doc = json.load(open(f))
    elif OFF: return None
    else:
        a = time.strftime('%Y-%m-%d', time.gmtime((jd - MATCH_DAYS - 1 - 2440587.5) * 86400)); b = time.strftime('%Y-%m-%d', time.gmtime((jd + MATCH_DAYS + 1 - 2440587.5) * 86400))
        try: doc = json.loads(get(CAD + '?des=%s&date-min=%s&date-max=%s&dist-max=0.5' % (urllib.parse.quote(des), a, b)))
        except Exception as e:
            log('designation lookup failed', des, repr(e)[:100])
            if 'HTTP Error 400' not in repr(e): return None
            doc = {'_not_found': True}                      # JPL answers 400 'specified object was not found'. Kept so it is not asked again for a week.
        json.dump(doc, open(f, 'w'))
    return nearest(des, jd, parse_cad(doc) or [])

# ---------------- 4. rows ----------------
first = {}                                   # (des, approach group, orbit_id) -> earliest statement
groups = C.defaultdict(list)                 # des -> [group anchor jd]
def group_of(des, jd):
    for g in groups[des]:
        if abs(g - jd) <= MATCH_DAYS: return g
    groups[des].append(jd); return jd
after = 0; outside = 0
for c in sorted(copies, key=lambda c: c['jd']):
    for r in c['rows']:
        if r['jd'] is None or r['dist'] is None: continue
        if r['dist'] > FRAME_DIST or r['jd'] < FRAME_JD: outside += 1; continue
        k = (r['des'], group_of(r['des'], r['jd']), r['orbit_id'])
        if c['jd'] >= r['jd']:
            if k not in first: after += 1
            continue
        if k not in first: first[k] = dict(r, copy_ts=c['ts'], copy_src=c['src'], copy_url=c['url'], copy_jd=c['jd'])
rows = []
for (des, g, oid), s in sorted(first.items(), key=lambda kv: (kv[1]['jd'], kv[0][0], kv[1]['copy_jd'])):
    d = None
    if s['jd'] <= NOW_JD:
        d = nearest(des, s['jd'])
        if d is None: d = by_designation(des, s['jd'])
    o, why = row_outcome(s, d, NOW_JD)
    row = dict(des=des, fullname=s['fullname'], approach=iso_of_jd(s['jd']), group=round(g, 3), lead_days=round(s['jd'] - s['copy_jd'], 2), stated_copy=s['copy_ts'], stated_src=s['copy_src'], stated_url=s['copy_url'],
               stated_orbit=oid, stated_jd=s['jd'], stated=s['dist'], stated_min=s['dist_min'], stated_max=s['dist_max'], stated_tsig=s['t_sigma_f'], h=s['h'], outcome=o, why=why)
    if d:
        row.update(latest_orbit=d['orbit_id'], latest_des=d['des'], latest_jd=d['jd'], latest=d['dist'], latest_min=d['dist_min'], latest_max=d['dist_max'])
        if s['dist_min'] is not None and s['dist_max'] is not None and s['dist_max'] > s['dist_min'] and d['dist'] is not None and s['dist'] is not None:
            row['z'] = round((d['dist'] - s['dist']) / ((s['dist_max'] - s['dist_min']) / 6), 3)
        if d['dist'] is not None and s['dist'] is not None: row['move_km'] = round((d['dist'] - s['dist']) * 149597870.7, 1)   # CHECKS.md addition 1: the same move in kilometres, display only
        if d['jd'] is not None:
            row['dt_min'] = round((d['jd'] - s['jd']) * 1440, 2); tm = tsig_minutes(s['t_sigma_f'])
            if tm is not None: row['tsig_min'] = tm
    rows.append(row)
# headline row per approach: the longest lead
best = {}
for r in rows:
    k = (r['des'], r['group'])
    if k not in best or r['lead_days'] > best[k]['lead_days']: best[k] = r
for r in rows: r['headline'] = best[(r['des'], r['group'])] is r

# ---------------- 5. known-good gates ----------------
kg = {}
kg['format'] = bool(cur_rows) and cur_version == CAD_VERSION and all(c['version'] == CAD_VERSION for c in copies)
# three stated rows read directly from the raw text of three archived copies (CHECKS.md). des, orbit_id, dist, dist_min, dist_max.
KG2 = json.load(open('data/known_good_rows.json')) if os.path.exists('data/known_good_rows.json') else []
ok2 = []
for want in KG2:
    c = next((c for c in copies if c['file'].endswith(want['file'])), None)
    r = next((r for r in (c['rows'] if c else []) if r['des'] == want['des']), None)
    ok2.append(bool(r) and r['orbit_id'] == want['orbit_id'] and all(repr(r[k]) == repr(float(want[k])) for k in ('dist', 'dist_min', 'dist_max')))
kg['reader'] = len(ok2) >= 3 and all(ok2)
same = [r for r in rows if r.get('latest_orbit') is not None and str(r['latest_orbit']) == str(r['stated_orbit']) and r.get('latest') is not None and r['stated']]
agree = [r for r in same if abs(r['latest'] - r['stated']) <= 1e-5 * r['stated']]
kg['join'] = len(same) >= 5 and len(agree) / len(same) >= 0.95
kg['rule'] = rule_selftest()[0]
GATE = all(kg.values())
rows = [r for r in rows if r['outcome'] == K.NOTHING_RETURNED] + K.apply_gate(GATE, [r for r in rows if r['outcome'] != K.NOTHING_RETURNED])   # a row with no approach yet has no outcome to gate
rows.sort(key=lambda r: (r['stated_jd'], r['des'], -r['lead_days']))
def oc(r): return r['outcome']

# ---------------- 6. cells ----------------
LEADS = (('all leads', 0, 1e9), ('0 to 7 days', 0, 7), ('8 to 30 days', 7, 30), ('more than 30 days', 30, 1e9))
def med(xs): return round(statistics.median(xs), 3) if xs else None
def cell(name, rs):
    seen = set(); once = []
    for r in sorted(rs, key=lambda r: r['stated_jd']):          # an object is counted once in a cell, by its earliest approach
        if r['des'] in seen: continue
        seen.add(r['des']); once.append(r)
    cnt = C.Counter(oc(r) for r in once); why = C.Counter(r['why'] for r in once if oc(r) == K.CANNOT_TELL and r.get('why'))
    n = cnt[K.CONSISTENT] + cnt[K.ABOVE] + cnt[K.BELOW]; k = cnt[K.CONSISTENT]; o, lo, hi = cell_outcome(k, n)
    km = [abs(r['move_km']) for r in once if oc(r) in (K.CONSISTENT, K.ABOVE, K.BELOW) and r.get('move_km') is not None]
    zs = [abs(r['z']) for r in once if oc(r) in (K.CONSISTENT, K.ABOVE, K.BELOW) and r.get('z') is not None]
    ts = [r for r in once if oc(r) in (K.CONSISTENT, K.ABOVE, K.BELOW) and r.get('tsig_min') and r.get('dt_min') is not None]
    return dict(cell=name, rows=len(once), scored=n, inside=k, above=cnt[K.ABOVE], below=cnt[K.BELOW], cannot_tell=cnt[K.CANNOT_TELL], cannot_tell_why=dict(why),
                not_yet=cnt[K.NOTHING_RETURNED], share=round(k / n, 4) if n else None, lo=round(lo, 4), hi=round(hi, 4), claim=CLAIM, outcome=o if GATE else K.CANNOT_TELL,
                median_abs_move_km=med(km), median_abs_shift_sigma=med(zs), share_beyond_1_sigma=round(sum(z > 1 for z in zs) / len(zs), 3) if zs else None, shift_rows=len(zs),
                time_rows=len(ts), time_inside_3_sigma=sum(abs(r['dt_min']) <= r['tsig_min'] for r in ts))
head = [r for r in rows if r['headline']]
cells = [cell(nm, [r for r in head if (a < r['lead_days'] <= b if a else r['lead_days'] <= b)]) for nm, a, b in LEADS]
aug = cell('approaches in August 2026', [r for r in head if r['approach'].startswith('2026-08')])
def once_all(rs):
    seen = set(); out = []
    for r in sorted(rs, key=lambda r: r['stated_jd']):
        if r['des'] not in seen: seen.add(r['des']); out.append(r)
    return out
_sc = [r for r in once_all(head) if oc(r) in (K.CONSISTENT, K.ABOVE, K.BELOW)]
by_copy = dict(scored=dict(C.Counter(r['stated_copy'][:8] for r in _sc)), outside=dict(C.Counter(r['stated_copy'][:8] for r in _sc if oc(r) != K.CONSISTENT)))   # display only: which copy each scored row was stated in
later = [r for r in rows if not r['headline']]
later_cnt = C.Counter(oc(r) for r in later)
# 10 Nov 2026, referee (neo_index_referee/REFEREE.md R1, R4, R5): display only, added after the data, never used for an outcome.
# (a) the copy that supplies the most scored rows, and every cell read again without it. (b) every cell read against 98.9 percent, the share of a
# two-dimensional normal inside its 3-sigma ellipse (1 - exp(-4.5)), the floor the CNEOS target-plane wording gives. (c) lopsided stated ranges.
CLAIM_2D = 1 - math.exp(-4.5)
def _dep():
    sc = [r for r in once_all(head) if oc(r) in (K.CONSISTENT, K.ABOVE, K.BELOW)]
    if not sc: return None
    big = C.Counter(r['stated_copy'] for r in sc).most_common(1)[0][0]
    def lead_rs(a, b, rs): return [r for r in rs if (a < r['lead_days'] <= b if a else r['lead_days'] <= b)]
    out = dict(copy=big, copy_day=big[:8], copy_url=next((r['stated_url'] for r in sc if r['stated_copy'] == big), None), cells=[])
    for nm, a, b in LEADS:
        c_all = cell(nm, lead_rs(a, b, head)); rs = lead_rs(a, b, [r for r in head if r['stated_copy'] != big])
        c_wo = cell(nm, rs); o2, lo2, hi2 = cell_outcome(c_all['inside'], c_all['scored'])
        o2 = (K.BELOW if hi2 < CLAIM_2D else o2) if c_all['scored'] >= MIN_ROWS else K.CANNOT_TELL
        sc_c = [r for r in once_all(lead_rs(a, b, head)) if oc(r) in (K.CONSISTENT, K.ABOVE, K.BELOW)]
        one_miss = cell_outcome(c_all['inside'] - 1, c_all['scored'])[0] if c_all['scored'] and c_all['inside'] == c_all['scored'] else None
        out['cells'].append(dict(cell=nm, from_copy_scored=sum(r['stated_copy'] == big for r in sc_c), from_copy_outside=sum(r['stated_copy'] == big and oc(r) != K.CONSISTENT for r in sc_c),
                                 without=dict(scored=c_wo['scored'], inside=c_wo['inside'], lo=c_wo['lo'], hi=c_wo['hi'], outcome=c_wo['outcome']),
                                 against_2d=dict(claim=round(CLAIM_2D, 4), outcome=o2 if GATE else K.CANNOT_TELL), outcome_if_one_outside=one_miss))
    return out
dependence = _dep()
for r in rows:
    if r['stated_max'] is not None and r['stated_min'] is not None and r['stated'] is not None and r['stated_max'] > r['stated_min']:
        f = (r['stated'] - r['stated_min']) / (r['stated_max'] - r['stated_min']); r['nominal_position'] = round(f, 4); r['lopsided'] = f < 0.25 or f > 0.75

# ---------------- 7. latest-solution facts for scored headline rows (display only) ----------------
def sbdb(des, oid):
    if NOSBDB: return None   # 10 Nov 2026: --no-sbdb skips the SBDB answers entirely, kept ones too. They fill latest_solution, a display field the scoring never reads
    f = 'data/cache/sbdb/%s.json' % re.sub(r'\W+', '_', des)
    if os.path.exists(f):
        v = json.load(open(f))
        if v.get('orbit_id') == str(oid) or OFF or NOSBDB: return v
    if OFF or NOSBDB: return None
    try: o = json.loads(get(SBDB + '?sstr=%s' % urllib.parse.quote(des)))['orbit']
    except Exception as e: log('sbdb failed', des, repr(e)[:80]); return None
    v = {k: o.get(k) for k in ('orbit_id', 'soln_date', 'condition_code', 'data_arc', 'first_obs', 'last_obs', 'n_obs_used')}; json.dump(v, open(f, 'w')); return v
todo = [r for r in head if oc(r) in (K.ABOVE, K.BELOW)] + [r for r in head if oc(r) == K.CONSISTENT]
n_new = 0
for r in todo:
    f = 'data/cache/sbdb/%s.json' % re.sub(r'\W+', '_', r.get('latest_des') or r['des'])
    if not os.path.exists(f):
        if n_new >= SBDB_CAP: continue
        n_new += 1
    v = sbdb(r.get('latest_des') or r['des'], r.get('latest_orbit'))
    if v: r['latest_solution'] = v

# ---------------- 8. plan seal and output ----------------
seal_f = 'data/plan_seal.json'
def git(*a): return subprocess.run(['git'] + list(a), cwd=H, capture_output=True, text=True).stdout.strip()
if not os.path.exists(seal_f) and K.plan_committed('PLAN.md', NOW):
    json.dump(dict(plan_commit=git('log', '-1', '--format=%H', '--', 'PLAN.md'), plan_commit_time=git('log', '-1', '--format=%cI', '--', 'PLAN.md'),
                   plan_sha256=hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest(), first_comparison=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW))), open(seal_f, 'w'), indent=1)
seal = json.load(open(seal_f)) if os.path.exists(seal_f) else None
cnt_all = C.Counter(oc(r) for r in rows)
summary = dict(
    desk='NEO', publisher='Heuremen LLC', generated=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW)), plan='PLAN.md', plan_seal=seal, plan_unchanged_since_commit=K.plan_committed('PLAN.md'),
    claim=dict(source='NASA/JPL CNEOS, SBDB Close-Approach Data API ' + str(cur_version), stated='dist_min and dist_max: minimum and maximum (3-sigma) approach distance (au)',
               our_reading='a 3-sigma range holds about 99.7 percent of later values under a normal error model', claim_share=CLAIM),
    frame=dict(dist_au_max=FRAME_DIST, approach_from='2024-01-01', match_days=MATCH_DAYS, wide_range_au=WIDE, min_rows=MIN_ROWS, consistent_floor=CONSISTENT_FLOOR),
    gates=dict(kg, passed=GATE, same_solution_rows=len(same), same_solution_agree=len(agree)),
    sources=dict(wayback_index_copies=len(cdx), wayback=dict(wb), own_copies=own, own_first_copy=min((c['ts'] for c in copies if c['src'] == 'own'), default=None), current_record_rows=len(cur_rows or []), sentry_stored=sentry_now, stale=STALE,
                 statements_outside_frame=outside, statements_copied_after_approach=after),
    rows=dict(total=len(rows), headline=len(head), later_statements=len(later), objects=len(set(r['des'] for r in rows)), outcomes=dict(cnt_all),
              later_statement_outcomes=dict(later_cnt), first_stated_copy=min((r['stated_copy'] for r in rows), default=None), last_stated_copy=max((r['stated_copy'] for r in rows), default=None)),
    cells=cells, august_2026=aug, by_copy_day=by_copy, dependence=dependence,
    after_data_note='dependence (each cell read without the copy that supplies the most scored rows, each cell read against 98.9 percent, and the outcome a cell at its floor would take with one row outside) and nominal_position and lopsided on rows were added after the data on 10 Nov 2026 at the outside referee (neo_index_referee/REFEREE.md). Display only. No outcome uses them.',
    outside_range=[{k: r.get(k) for k in ('des', 'approach', 'lead_days', 'stated_copy', 'stated_url', 'stated_orbit', 'stated', 'stated_min', 'stated_max', 'latest_orbit', 'latest', 'latest_min', 'latest_max', 'z', 'move_km', 'outcome', 'headline', 'latest_solution', 'nominal_position', 'lopsided')}
                   for r in rows if oc(r) in (K.ABOVE, K.BELOW)],
    august_rows=[{k: r.get(k) for k in ('des', 'approach', 'lead_days', 'stated_copy', 'stated_orbit', 'stated', 'stated_min', 'stated_max', 'latest_orbit', 'latest', 'latest_min', 'latest_max', 'z', 'move_km', 'outcome', 'why', 'stated_url', 'nominal_position', 'lopsided')}
                 for r in head if r['approach'].startswith('2026-08')])
json.dump(dict(generated=summary['generated'], rows=rows), open('data/neo.json.tmp', 'w')); os.replace('data/neo.json.tmp', 'data/neo.json')
json.dump(summary, open('summary_neo.json.tmp', 'w'), indent=1); os.replace('summary_neo.json.tmp', 'summary_neo.json')
# the live feed: the summary as served at /neo/live.json (every row stays in data/neo.json, which is kept here)
json.dump(dict(summary, updated=summary['generated']), open('data/neo_live.json.tmp', 'w'), separators=(',', ':')); os.replace('data/neo_live.json.tmp', 'data/neo_live.json')
if PUB:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'neo_live', '--path', os.path.join(H, 'data', 'neo_live.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                       cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
    log('neo_live', 'published' if p.returncode == 0 else 'publish FAILED ' + (p.stderr or '')[-200:])
    if p.returncode: STALE.append('publish')
with open('data/neo_history.jsonl', 'a') as f: f.write(json.dumps(dict(t=summary['generated'], gate=GATE, rows=len(rows), cells=[(c['cell'], c['scored'], c['inside'], c['outcome']) for c in cells], stale=STALE)) + '\n')
log('gates', kg, 'rows', len(rows), 'headline', len(head))
for c in cells + [aug]: log('%-26s scored %4d inside %4d above %3d below %3d cannot tell %4d not yet %3d  [%.4f, %.4f]  %s' % (c['cell'], c['scored'], c['inside'], c['above'], c['below'], c['cannot_tell'], c['not_yet'], c['lo'], c['hi'], c['outcome']))
