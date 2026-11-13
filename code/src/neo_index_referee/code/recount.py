#!/usr/bin/env python3
"""Referee recount of the NEO desk, written without importing neo_tick.py or heuremen_kit.py.
Reads the raw files under neo_index/data (Wayback copies, own snapshots, current record, designation cache) and rebuilds
every row outcome and every cell. Writes neo_index_referee/out/*.json. Usage: python3 -I recount.py"""
import json, gzip, glob, os, re, math, hashlib, calendar, time, urllib.parse, collections as C
D = '/Users/heuremen/bones-forge/neo_index/data'
OUT = '/Users/heuremen/bones-forge/neo_index_referee/out'; os.makedirs(OUT, exist_ok=True)
NEED = ('des', 'orbit_id', 'jd', 'dist', 'dist_min', 'dist_max')
JD2024 = 2460310.5
AU_KM = 149597870.7
# run time of the desk's last run (so "passed" means the same thing)
SUMMARY = json.load(open('/Users/heuremen/bones-forge/neo_index/summary_neo.json'))
RUN_JD = calendar.timegm(time.strptime(SUMMARY['generated'], '%Y-%m-%dT%H:%M:%SZ')) / 86400 + 2440587.5

def ts_jd(ts): return calendar.timegm(time.strptime(ts[:14], '%Y%m%d%H%M%S')) / 86400 + 2440587.5
def num(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError): return None

def rows_of(doc):
    sig = (doc or {}).get('signature') or {}
    if 'Close Approach' not in str(sig.get('source', '')): return None, None
    f = doc.get('fields'); data = doc.get('data')
    if not f or data is None or not all(n in f for n in NEED): return None, sig.get('version')
    out = []
    for r in data:
        x = dict(zip(f, r))
        if 'body' in x and x['body'] != 'Earth': continue
        des = str(x['des']); des = des.split('|')[1].strip() if '|' in des else des.strip()
        out.append(dict(des=des, oid=str(x['orbit_id']), jd=num(x['jd']), d=num(x['dist']), lo=num(x['dist_min']), hi=num(x['dist_max']),
                        fullname=(x.get('fullname') or '').strip(), tsig=x.get('t_sigma_f')))
    return out, sig.get('version')

# ---- stated copies ----
cdx = json.load(open(D + '/raw/wayback/cdx_cad_api.json'))[1:]
copies = []; skip = C.Counter()
for ts, orig, sc, ln in cdx:
    fn = D + '/raw/wayback/cad_%s_%s.json' % (ts, hashlib.sha1(orig.encode()).hexdigest()[:8])
    if not os.path.exists(fn): skip['missing file'] += 1; continue
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(orig).query)
    if q.get('body', ['Earth'])[0] != 'Earth': skip['other body'] += 1; continue
    try: doc = json.load(open(fn))
    except Exception: skip['unparsed'] += 1; continue
    rs, ver = rows_of(doc)
    if rs is None: skip['no data rows'] += 1; continue
    copies.append(dict(src='wayback', ts=ts, jd=ts_jd(ts), url=orig, ver=ver, rows=rs))
for fn in sorted(glob.glob(D + '/snapshots/cad_*.json.gz')):
    doc = json.load(gzip.open(fn, 'rt')); rs, ver = rows_of(doc)
    ts = re.search(r'cad_(\d{8})T(\d{6})Z', fn); ts = ts.group(1) + ts.group(2)
    if rs is not None: copies.append(dict(src='own', ts=ts, jd=ts_jd(ts), url=fn, ver=ver, rows=rs))

# ---- current record, with aliases from fullname ("462959 (2005 xx)") ----
cur, cur_ver = rows_of(json.load(open(D + '/raw/cad_current.json')))
alias = C.defaultdict(set)
for r in cur:
    m = re.match(r'^(\d+)\s*(?:[A-Za-z\'\- ]+)?\s*(?:\(([^)]+)\))?$', r['fullname'])
    alias[r['des']].add(r['des'])
    if m and m.group(2): alias[m.group(2).strip()].add(r['des'])
    m2 = re.search(r'\(([^)]+)\)', r['fullname'])
    if m2: alias[m2.group(1).strip()].add(r['des'])
by = C.defaultdict(list)
for r in cur: by[r['des']].append(r)
def cache_rows(des, jd):
    fn = D + '/cache/des_%s_%d.json' % (re.sub(r'\W+', '_', des), round(jd))
    if not os.path.exists(fn): return None
    doc = json.load(open(fn))
    if doc.get('_not_found'): return []
    return rows_of(doc)[0] or []
def match(des, jd):
    pool = []
    for k in alias.get(des, {des}): pool += by.get(k, [])
    how = 'current'
    if not any(abs(r['jd'] - jd) <= 10 for r in pool):
        cr = cache_rows(des, jd)
        if cr is None: return None, 'no cache'
        pool = cr; how = 'designation lookup'
    c = sorted([r for r in pool if r['jd'] is not None and abs(r['jd'] - jd) <= 10], key=lambda r: abs(r['jd'] - jd))
    if not c: return None, how
    return c[0], how + (' (2+ within 10 d)' if len(c) > 1 else '')

# ---- statements -> rows: identity (des, approach cluster, orbit_id), earliest pre-approach copy ----
first = {}; post = 0; out_frame = 0; anchors = C.defaultdict(list)
def anchor(des, jd):
    for a in anchors[des]:
        if abs(a - jd) <= 10: return a
    anchors[des].append(jd); return jd
for c in sorted(copies, key=lambda c: (c['jd'], c['ts'])):
    for r in c['rows']:
        if r['jd'] is None or r['d'] is None: continue
        if r['d'] > 0.05 or r['jd'] < JD2024: out_frame += 1; continue
        k = (r['des'], anchor(r['des'], r['jd']), r['oid'])
        if c['jd'] >= r['jd']:
            if k not in first: post += 1
            continue
        if k not in first: first[k] = dict(r, cts=c['ts'], cjd=c['jd'], csrc=c['src'], curl=c['url'])

def outcome(s, d):
    if s['lo'] is None or s['hi'] is None or s['lo'] > s['hi']: return 'CANNOT_TELL', 'unreadable'
    if s['jd'] > RUN_JD: return 'NOTHING_RETURNED', 'not yet'
    if d is None: return 'CANNOT_TELL', 'no record'
    if d['lo'] is None or d['hi'] is None or d['lo'] > d['hi']: return 'CANNOT_TELL', 'unreadable'
    if d['oid'] == s['oid']: return 'CANNOT_TELL', 'same solution'
    if s['hi'] - s['lo'] > 0.05: return 'CANNOT_TELL', 'wide range'
    if d['lo'] > s['hi']: return 'ABOVE', None
    if d['hi'] < s['lo']: return 'BELOW', None
    if d['lo'] >= s['lo'] and d['hi'] <= s['hi']: return 'CONSISTENT', None
    return 'CANNOT_TELL', 'edge'

rows = []
for (des, a, oid), s in first.items():
    d, how = (None, 'not yet') if s['jd'] > RUN_JD else match(des, s['jd'])
    o, why = outcome(s, d)
    rows.append(dict(des=des, anchor=a, oid=oid, jd=s['jd'], lead=s['jd'] - s['cjd'], cts=s['cts'], csrc=s['csrc'], curl=s['curl'], d=s['d'], lo=s['lo'], hi=s['hi'],
                     o=o, why=why, how=how, l_oid=d and d['oid'], l_des=d and d['des'], l_jd=d and d['jd'], l_d=d and d['d'], l_lo=d and d['lo'], l_hi=d and d['hi']))
best = {}
for r in rows:
    k = (r['des'], r['anchor'])
    if k not in best or r['lead'] > best[k]['lead']: best[k] = r
for r in rows: r['head'] = best[(r['des'], r['anchor'])] is r

def wilson(k, n, z=1.96):
    if n == 0: return 0.0, 1.0
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0, c - h), min(1, c + h)
def cell_rule(k, n, claim=0.9973, floor=0.98):
    lo, hi = wilson(k, n)
    if n < 10: return 'CANNOT_TELL', lo, hi
    if hi < claim: return 'BELOW', lo, hi
    if lo > claim: return 'ABOVE', lo, hi
    if lo >= floor: return 'CONSISTENT', lo, hi
    return 'CANNOT_TELL', lo, hi
SC = ('CONSISTENT', 'ABOVE', 'BELOW')
def once(rs):
    seen = set(); o = []
    for r in sorted(rs, key=lambda r: r['jd']):
        if r['des'] not in seen: seen.add(r['des']); o.append(r)
    return o
def cell(rs, claim=0.9973):
    rs = once(rs); cnt = C.Counter(r['o'] for r in rs); n = sum(cnt[x] for x in SC); k = cnt['CONSISTENT']
    o, lo, hi = cell_rule(k, n, claim)
    return dict(rows=len(rs), scored=n, inside=k, above=cnt['ABOVE'], below=cnt['BELOW'], cannot_tell=cnt['CANNOT_TELL'], not_yet=cnt['NOTHING_RETURNED'],
                why=dict(C.Counter(r['why'] for r in rs if r['o'] == 'CANNOT_TELL')), lo=round(lo, 4), hi=round(hi, 4), outcome=o)
LEADS = [('all leads', lambda L: True), ('0 to 7 days', lambda L: L <= 7), ('8 to 30 days', lambda L: 7 < L <= 30), ('more than 30 days', lambda L: L > 30)]
head = [r for r in rows if r['head']]
res = dict(run_jd=RUN_JD, copies_used=sum(c['src'] == 'wayback' for c in copies), own=sum(c['src'] == 'own' for c in copies), skip=dict(skip),
           versions=dict(C.Counter(c['ver'] for c in copies)), cur_ver=cur_ver, cur_rows=len(cur), out_frame=out_frame, post=post,
           rows=len(rows), head=len(head), outcomes=dict(C.Counter(r['o'] for r in rows)))
res['cells'] = {nm: cell([r for r in head if f(r['lead'])]) for nm, f in LEADS}
res['august'] = cell([r for r in head if time.strftime('%Y-%m', time.gmtime((r['jd'] - 2440587.5) * 86400)) == '2026-08'])
# --- sensitivity, after the data, referee only ---
FEB = '20240209054243'
res['without_feb9'] = {nm: cell([r for r in head if f(r['lead']) and r['cts'] != FEB]) for nm, f in LEADS}
# drop the Feb copy entirely (so its approaches fall to the next-longest statement)
res['claim_98_89'] = {nm: cell([r for r in head if f(r['lead'])], claim=1 - math.exp(-4.5)) for nm, f in LEADS}
gt30 = once([r for r in head if r['lead'] > 30])
res['gt30_scored_by_copy'] = dict(C.Counter(r['cts'][:8] for r in gt30 if r['o'] in SC))
res['gt30_outside_by_copy'] = dict(C.Counter(r['cts'][:8] for r in gt30 if r['o'] in ('ABOVE', 'BELOW')))
res['lead_min_pre'] = min(r['lead'] for r in rows)
res['rows_lead_under_0.01d'] = sum(r['lead'] < 0.01 for r in rows)
res['match_how'] = dict(C.Counter(r['how'] for r in rows if r['o'] != 'NOTHING_RETURNED'))
res['same_oid_rows'] = sum(1 for r in rows if r['l_oid'] is not None and r['l_oid'] == r['oid'])
res['same_oid_agree'] = sum(1 for r in rows if r['l_oid'] is not None and r['l_oid'] == r['oid'] and abs(r['l_d'] - r['d']) <= 1e-5 * r['d'])
res['latest_oid_lower'] = [(r['des'], r['oid'], r['l_oid']) for r in rows if r['l_oid'] and r['l_oid'].isdigit() and r['oid'].isdigit() and int(r['l_oid']) < int(r['oid'])]
res['match_dt_hours_scored_max'] = max(abs(r['l_jd'] - r['jd']) * 24 for r in rows if r['o'] in SC)
res['outside'] = [dict(des=r['des'], approach=time.strftime('%Y-%m-%d %H:%M', time.gmtime((r['jd'] - 2440587.5) * 86400)), lead=round(r['lead'], 2), copy=r['cts'], oid=r['oid'], l_oid=r['l_oid'],
                       l_des=r['l_des'], how=r['how'], o=r['o'], head=r['head'], move_km=round((r['l_d'] - r['d']) * AU_KM, 1), stated_range_km=round((r['hi'] - r['lo']) * AU_KM, 1),
                       asym=round((r['d'] - r['lo']) / (r['hi'] - r['d']), 3) if r['hi'] > r['d'] else None, dt_h=round((r['l_jd'] - r['jd']) * 24, 3)) for r in rows if r['o'] in ('ABOVE', 'BELOW')]
json.dump(res, open(OUT + '/recount.json', 'w'), indent=1)
json.dump(rows, open(OUT + '/rows.json', 'w'))
# --- diff against the desk's rows ---
desk = json.load(open(D + '/neo.json'))['rows']
dk = {(r['des'], r['stated_orbit'], r['stated_copy'], round(r['stated_jd'], 6)): r for r in desk}
mk = {(r['des'], r['oid'], r['cts'], round(r['jd'], 6)): r for r in rows}
diff = dict(only_desk=len(set(dk) - set(mk)), only_ref=len(set(mk) - set(dk)), outcome_diff=[], head_diff=0)
for k in set(dk) & set(mk):
    if dk[k]['outcome'] != mk[k]['o']: diff['outcome_diff'].append((k, dk[k]['outcome'], mk[k]['o'], mk[k]['how']))
    if dk[k]['headline'] != mk[k]['head']: diff['head_diff'] += 1
json.dump(diff, open(OUT + '/diff_vs_desk.json', 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in res.items() if k not in ('outside',)}, indent=1)); print('DIFF', json.dumps(diff, default=str)[:2000])
for o in res['outside']: print(o)
