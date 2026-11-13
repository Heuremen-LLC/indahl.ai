#!/usr/bin/python3 -I
"""Referee recount for QUAKE. Own reader, zone test, counter, Wilson, block bootstrap, cell rules. Written from PLAN.md text.
Imports nothing from quake_index. Reads raw files only."""
import json, gzip, glob, os, math, random, bisect, sys, collections as C
R = '/Users/heuremen/bones-forge/quake_index/data/raw/'
OUT = '/Users/heuremen/bones-forge/quake_index_referee/out/'
DAY = 86400000
RUN_MS = int(sys.argv[1]) if len(sys.argv) > 1 else None   # run time; default = catalog fetch time
ER = 6371.0
def hav(la1, lo1, la2, lo2):
    p1, p2 = math.radians(la1), math.radians(la2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 2 * ER * math.asin(min(1.0, math.sqrt(a)))

# ---- events and versions
events = {}; versions = []; vmiss = C.Counter()
for f in sorted(glob.glob(R + 'detail/*.json')):
    d = json.load(open(f)); pr = d['properties']; eid = d['id']
    g = d['geometry']['coordinates']
    events[eid] = dict(id=eid, time=pr['time'], mag=pr['mag'], net=pr['net'], lat=g[1], lon=g[0], ids=set(x for x in pr['ids'].split(',') if x), title=pr['title'])
    for p in pr['products'].get('oaf', []):
        versions.append((eid, p))
print('events', len(events), 'versions', len(versions))

def load_forecast(p):
    c = p['contents']
    if not isinstance(c, dict): return None, 'deleted'
    ut = p['updateTime']; base = R + 'forecast/%s_%s_%d' % (p['code'], p['source'], ut)
    doc = None
    if os.path.exists(base + '.json'):
        try: doc = json.load(open(base + '.json'))
        except Exception: return None, 'unreadable'
    elif '' in c and 'bytes' in c['']:
        try: doc = json.loads(c['']['bytes'])
        except Exception: return None, 'unreadable'
    else:
        return None, 'forecast not read'
    return doc, None

# ---- blocks: union-find on events within 100 km and 365 days
ids = sorted(events)
par = {i: i for i in ids}
def find(x):
    while par[x] != x: par[x] = par[par[x]]; x = par[x]
    return x
for i in range(len(ids)):
    for j in range(i + 1, len(ids)):
        a, b = events[ids[i]], events[ids[j]]
        if abs(a['time'] - b['time']) <= 365 * DAY and hav(a['lat'], a['lon'], b['lat'], b['lon']) <= 100.0:
            par[find(ids[i])] = find(ids[j])
block = {i: find(i) for i in ids}
print('blocks', len(set(block.values())))

# ---- catalogs
cat = {}; fetched = {}
for eid in ids:
    c = json.load(gzip.open(R + 'catalog/%s.json.gz' % eid))
    fetched[eid] = c['fetched']
    ev = []
    for ft in c['features']:
        pp = ft['properties']; co = ft['geometry']['coordinates']
        if pp.get('type') != 'earthquake' or pp.get('mag') is None: continue
        ev.append((pp['time'], co[1], co[0], co[2] if len(co) > 2 else None, pp['mag'], set(x for x in (pp.get('ids') or '').split(',') if x), ft['id']))
    cat[eid] = ev

zcache = {}
def zone_events(eid, zone):
    key = (eid, zone)
    if key in zcache: return zcache[key]
    lat, lon, rad, dmin, dmax = zone
    main = events[eid]['ids']
    sel = []
    for (t, la, lo, dp, m, ii, i) in cat[eid]:
        if ii & main: continue
        if dmin is not None and dp is not None and not (dmin <= dp <= dmax): continue
        if hav(lat, lon, la, lo) <= rad: sel.append((t, m))
    sel.sort()
    ts = [x[0] for x in sel]
    zcache[key] = (ts, [x[1] for x in sel])
    return zcache[key]
def count(eid, zone, t0, t1, mag):
    ts, ms = zone_events(eid, zone)
    a = bisect.bisect_left(ts, t0); b = bisect.bisect_left(ts, t1)   # [t0, t1)
    return sum(1 for m in ms[a:b] if m >= mag)
def count_round(eid, zone, t0, t1, mag):
    ts, ms = zone_events(eid, zone)
    a = bisect.bisect_left(ts, t0); b = bisect.bisect_left(ts, t1)
    return sum(1 for m in ms[a:b] if round(m + 1e-9, 1) >= mag)

# ---- rows
rows = []; vstat = C.Counter(); zc = C.Counter(); late_lags = []; late_vers = set(); parsed_n = 0
for eid, p in versions:
    doc, why = load_forecast(p)
    if doc is None: vstat[why] += 1; continue
    parsed_n += 1
    ut = p['updateTime']
    mp = (doc.get('model') or {}).get('parameters') or {}
    zone = None; zwhy = 'zone not stated'
    if mp.get('regionType') == 'circle':
        zone = (float(mp['regionCenterLat']), float(mp['regionCenterLon']), float(mp['regionRadius']), None, None); zc['circle'] += 1
    elif mp.get('regionType') is None:
        fd = R + 'forecast/%s_%s_%d_data.json' % (p['code'], p['source'], ut)
        if os.path.exists(fd):
            P = json.load(open(fd))['parameters']; r_ = P.get('aftershock_search_region') or {}
            if r_ and 'center' in r_:
                zone = (r_['center']['lat'], r_['center']['lon'], r_['radius'], P.get('min_depth'), P.get('max_depth')); zc['circle'] += 1
    if zone is None: zc['zone not stated'] += 1
    run = RUN_MS or fetched[eid]
    for w in doc['forecast']:
        t0, t1, lab = w['timeStart'], w['timeEnd'], w['label']
        items = [('bin', b['magnitude'], b['probability'], b['p95minimum'], b['p95maximum']) for b in w['bins']]
        if isinstance(w.get('aboveMainshockMag'), dict): a = w['aboveMainshockMag']; items.append(('above mainshock', a['magnitude'], a['probability'], None, None))
        for kind, mag, pr_, nmin, nmax in items:
            r = dict(seq=eid, block=block[eid], issued=ut, window=lab, t0=t0, t1=t1, mag=mag, kind=kind, p=pr_, nmin=nmin, nmax=nmax, net=events[eid]['net'], zone=zone)
            if not (0 <= pr_ <= 1) or (kind == 'bin' and nmin > nmax): r.update(status='unscored', outcome='CANNOT_TELL'); rows.append(r); continue
            if ut > t0:
                r.update(status='outside'); late_lags.append((ut - t0) / 60000.0); late_vers.add((eid, ut)); rows.append(r); continue
            if zone is None: r.update(status='unscored', outcome='CANNOT_TELL'); rows.append(r); continue
            if t1 + 7 * DAY > run: r.update(status='unscored', outcome='NOTHING_RETURNED', why='window not closed'); rows.append(r); continue
            if fetched[eid] < t1 + 7 * DAY: r.update(status='unscored', outcome='NOTHING_RETURNED', why='catalog not read'); rows.append(r); continue
            n = count(eid, zone, t0, t1, mag); r['count'] = n; r['occurred'] = n >= 1; r['count_r'] = count_round(eid, zone, t0, t1, mag)
            r['status'] = 'scored'
            if kind == 'bin': r['outcome'] = 'CONSISTENT' if nmin <= n <= nmax else ('ABOVE' if n > nmax else 'BELOW')
            else: r['outcome'] = 'CONSISTENT'
            rows.append(r)
print('versions parsed', parsed_n, dict(vstat), 'zones', dict(zc))
late_lags.sort()
print('late versions', len(late_vers), 'median min', late_lags[len(late_lags) // 2] if late_lags else None)
inframe = [r for r in rows if r['status'] != 'outside']
print('rows total', len(rows), 'outside', len(rows) - len(inframe), 'inframe', len(inframe))
print('outcomes', dict(C.Counter(r.get('outcome') for r in inframe)))
sc = [r for r in rows if r['status'] == 'scored']
print('scored', len(sc), 'unscored why', dict(C.Counter(r.get('why') for r in rows if r['status'] == 'unscored')))

# ---- intervals
def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)
def boot(rs, f, seed=20261110, B=2000):
    g = C.defaultdict(lambda: [0, 0])
    for r in rs: x = g[r['block']]; x[0] += f(r); x[1] += 1
    bl = list(g.values()); nb = len(bl); rng = random.Random(seed); vals = []
    for _ in range(B):
        k = n = 0
        for _ in range(nb): a = bl[rng.randrange(nb)]; k += a[0]; n += a[1]
        vals.append(k / n)
    vals.sort()
    def q(u):
        pos = u * (B - 1); i = int(pos); fr = pos - i
        return vals[i] * (1 - fr) + vals[min(i + 1, B - 1)] * fr
    return q(0.025), q(0.975), nb
def cover_cell(name, rs, seed=20261110):
    n = len(rs); k = sum(1 for r in rs if r['outcome'] == 'CONSISTENT')
    ab = sum(1 for r in rs if r['outcome'] == 'ABOVE'); be = sum(1 for r in rs if r['outcome'] == 'BELOW')
    if n == 0: return dict(cell=name, scored=0)
    w = wilson(k, n); bl, bh, nb = boot(rs, lambda r: 1 if r['outcome'] == 'CONSISTENT' else 0, seed)
    lo, hi = min(w[0], bl), max(w[1], bh)
    if n < 30 or nb < 10: o = 'CANNOT_TELL'
    elif hi < 0.95: o = 'BELOW'
    elif lo > 0.95: o = 'ABOVE'
    elif lo >= 0.925 and hi <= 0.975: o = 'CONSISTENT'
    else: o = 'CANNOT_TELL'
    return dict(cell=name, scored=n, inside=k, above=ab, below=be, share=k / n, wilson=w, boot=(bl, bh), lo=lo, hi=hi, blocks=nb, outcome=o)
PB = (0.0, 0.01, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80, 0.90, 0.99, 1.0)
def pbin(p):
    for i in range(len(PB) - 1):
        if PB[i] <= p < PB[i + 1]: return i
    return len(PB) - 2   # p == 1.0
def rel_cell(name, rs, seed=20261110):
    n = len(rs)
    if n == 0: return dict(cell=name, scored=0)
    k = sum(1 for r in rs if r['occurred']); s = sum(r['p'] for r in rs) / n
    w = wilson(k, n); bl, bh, nb = boot(rs, lambda r: 1 if r['occurred'] else 0, seed)
    lo, hi = min(w[0], bl), max(w[1], bh)
    tol = max(0.01, min(0.05, s / 2, (1 - s) / 2))
    if n < 30 or nb < 10: o = 'CANNOT_TELL'
    elif lo > s: o = 'ABOVE'
    elif hi < s: o = 'BELOW'
    elif lo >= s - tol and hi <= s + tol: o = 'CONSISTENT'
    else: o = 'CANNOT_TELL'
    return dict(cell=name, scored=n, occurred=k, stated=s, share=k / n, wilson=w, boot=(bl, bh), lo=lo, hi=hi, tol=tol, blocks=nb, outcome=o)

BIN = [r for r in sc if r['kind'] == 'bin']; AB = [r for r in sc if r['kind'] != 'bin']
res = {}
res['headline'] = cover_cell('M3 and above, every window', [r for r in BIN if r['mag'] == 3.0])
res['by_mag'] = [cover_cell('M%g' % m, [r for r in BIN if r['mag'] == m]) for m in (3.0, 4.0, 5.0, 6.0, 7.0, 8.0)]
res['by_window'] = [cover_cell(w, [r for r in BIN if r['mag'] == 3.0 and r['window'] == w]) for w in ('1 Day', '1 Week', '1 Month', '1 Year')]
res['all'] = cover_cell('every magnitude, every window', BIN)
res['rel'] = [rel_cell('%g-%g' % (PB[i] * 100, PB[i + 1] * 100), [r for r in BIN if pbin(r['p']) == i]) for i in range(10)]
res['rel_above'] = rel_cell('above mainshock', AB)
# splits
def split_rel(rs): return [rel_cell('%g-%g' % (PB[i] * 100, PB[i + 1] * 100), [r for r in rs if pbin(r['p']) == i], seed=1) for i in range(10)]
res['split_rel'] = {}
res['split_rel']['M3'] = split_rel([r for r in BIN if r['mag'] == 3.0])
res['split_rel']['M4up'] = split_rel([r for r in BIN if r['mag'] >= 4.0])
for w in ('1 Day', '1 Week', '1 Month', '1 Year'): res['split_rel'][w] = split_rel([r for r in BIN if r['window'] == w])
for m in (3.0, 4.0, 5.0): res['split_rel']['M%g' % m] = split_rel([r for r in BIN if r['mag'] == m])
# 10 percent and over combined
res['rel10up'] = {}
for nm, rs in (('all', BIN), ('M3', [r for r in BIN if r['mag'] == 3.0]), ('M4up', [r for r in BIN if r['mag'] >= 4.0]),
               ('1 Day', [r for r in BIN if r['window'] == '1 Day']), ('1 Week', [r for r in BIN if r['window'] == '1 Week']),
               ('1 Month', [r for r in BIN if r['window'] == '1 Month']), ('1 Year', [r for r in BIN if r['window'] == '1 Year'])):
    x = [r for r in rs if r['p'] >= 0.10]
    res['rel10up'][nm] = rel_cell('p>=10 ' + nm, x, seed=1)
# seed variation on headline
res['seed_var'] = []
for sd in (1, 2, 3, 4, 5, 20261110):
    c = cover_cell('h', [r for r in BIN if r['mag'] == 3.0], sd); res['seed_var'].append((sd, c['boot'][0], c['boot'][1]))
# network split
res['by_net'] = {}
for nm, f in (('us', lambda r: r['net'] == 'us'), ('regional', lambda r: r['net'] != 'us')):
    res['by_net'][nm] = cover_cell('M3 ' + nm, [r for r in BIN if r['mag'] == 3.0 and f(r)])
res['by_net_rel10'] = {}
for nm, f in (('us', lambda r: r['net'] == 'us'), ('regional', lambda r: r['net'] != 'us')):
    res['by_net_rel10'][nm] = rel_cell('p>=10 ' + nm, [r for r in BIN if r['p'] >= 0.1 and f(r)], seed=1)
# rounding check
res['round_same'] = sum(1 for r in BIN if (r['nmin'] <= r['count_r'] <= r['nmax']) == (r['outcome'] == 'CONSISTENT'))
res['round_n'] = len(BIN)
res['brier'] = sum((r['p'] - (1 if r['occurred'] else 0)) ** 2 for r in BIN) / len(BIN)
# first version of each event
firsts = {}
for r in rows:
    pass
json.dump(res, open(OUT + 'recount.json', 'w'), indent=1, default=list)
def slim(r): return {k: r.get(k) for k in ('seq', 'issued', 'window', 'mag', 'kind', 'count', 'outcome', 'status', 'p', 'nmin', 'nmax', 't0', 't1', 'net', 'block')}
json.dump([slim(r) for r in rows], open(OUT + 'rows.json', 'w'))
print(json.dumps(res['headline'], default=list)); 
