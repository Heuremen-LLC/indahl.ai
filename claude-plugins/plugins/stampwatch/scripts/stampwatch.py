#!/usr/bin/env python3
"""stampwatch.py -- Heuremen LLC (https://indahl.ai). Standard library only. Plan: plans/stampwatch/PLAN.md and amendments v2 to v5 in
github.com/Heuremen-LLC/claude-plugins. Detects a label that stops being bound to the content it attests, in two directions:
A, the label moves while the content is frozen; B, the content moves while the label is carried. It names no cause.

  python3 stampwatch.py selftest                       planted cases, end to end through the same code paths as real data
  python3 stampwatch.py ibm-index RECORDS_DIR [OUT]    parse IBM BackendProperties records once (refuses files with no read time)
  python3 stampwatch.py ibm-counts INDEX               floor-window counts, pair classes per field, k-thresholds per BH family
  python3 stampwatch.py ibm-floor INDEX                floors per backend and field, and the leave-one-backend-out check
  python3 stampwatch.py ibm-read INDEX                 observations by stamp-gap bin and rule 4 readings, one BH family per class
  python3 stampwatch.py feed SPEC.json SNAP_DIR        direction A and B counts per unit on a snapshotted JSON feed (HF, CKAN, any)

Observations (FROZEN_RECORD, FROZEN_DATE, FROZEN_QUBITS_ONLY, CARRIED, VALUE_CHANGED_DATE_UNCHANGED, RESTAMPED_IDENTICAL events, stamp
regressions, duplicates) are counts. Outcomes (ABOVE, CONSISTENT, CANNOT_TELL with a reason, NOTHING_RETURNED) come only from rule 4
(and rule 5 when a reference is given). When the floor holds no identical values at all, u is the 95 % upper bound of a rate never
observed: it measures how much history we hold, not a noise rate."""
import json, gzip, os, sys, glob, math, hashlib, datetime as dt, random, re, tempfile, csv, io

WINDOW = ('2026-05-04', '2026-09-14'); MIN_FLOOR = 500; SIZE = 0.05; Q = 0.05
FIELDS = ('T1', 'T2'); QUANT = ('readout_error', 'prob_meas0_prep1', 'prob_meas1_prep0'); CLASSES = ('negative', 'positive', 'between', 'unclassed')
BINS = (('<=1h', 0, 1), ('1-24h', 1, 24), ('>24h', 24, 1e12))

# ---------- exact binomial machinery ----------
def _lpmf(k, n, p):
    if p <= 0: return 0.0 if k == 0 else -math.inf
    if p >= 1: return 0.0 if k == n else -math.inf
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log1p(-p)
def sf(k, n, p):
    if k <= 0: return 1.0
    if k > n: return 0.0
    m = [_lpmf(i, n, p) for i in range(k, n + 1)]; mx = max(m)
    return 0.0 if mx == -math.inf else min(1.0, math.exp(mx) * sum(math.exp(x - mx) for x in m))
def cdf(k, n, p): return 1.0 - sf(k + 1, n, p)
def cp(k, n, a=0.05):
    if n == 0: return (0.0, 1.0)
    def bis(f):
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if f(mid): hi = mid
            else: lo = mid
        return (lo + hi) / 2
    return (0.0 if k == 0 else bis(lambda p: sf(k, n, p) >= a / 2), 1.0 if k == n else bis(lambda p: cdf(k, n, p) <= a / 2))
def bh(ps, q=Q):
    m = len(ps); order = sorted(range(m), key=lambda i: ps[i]); cut = -1
    for r, i in enumerate(order, 1):
        if ps[i] <= q * r / m: cut = r
    flag = [False] * m
    for r, i in enumerate(order, 1): flag[i] = r <= cut
    return flag
def k_threshold(n, u, m, q=Q):
    """smallest k that could be flagged as the smallest p in a BH family of m (p <= q/m)"""
    if not n or u is None: return None
    return next((k for k in range(n + 1) if sf(k, n, u) <= q / max(m, 1)), None)

# ---------- IBM adapter ----------
def load_ibm(p):
    with (gzip.open(p, 'rt', encoding='utf-8') if p.endswith('.gz') else open(p, encoding='utf-8')) as f: d = json.load(f)
    Q_ = {}
    for i, qs in enumerate(d.get('qubits', [])):
        Q_[i] = {x['name']: [x.get('value'), x.get('date')] for x in qs if x.get('name') in FIELDS + QUANT}
    rest = {k: v for k, v in d.items() if k != 'last_update_date'}
    return d.get('backend_name'), d.get('last_update_date'), Q_, hashlib.sha256(json.dumps(rest, sort_keys=True, default=str).encode()).hexdigest()
def read_time(p):
    """read time from the file name: backend__YYYYmmddTHHMMSS, or backend_YYYY-MM-DD[_HHMM] (day precision when no time is given)"""
    b = os.path.basename(p)
    if '__' in b:
        try: return dt.datetime.strptime(b.split('__')[1][:15], '%Y%m%dT%H%M%S').replace(tzinfo=dt.timezone.utc).isoformat()
        except ValueError: pass
    m = re.search(r'_(\d{4}-\d{2}-\d{2})(?:_(\d{4}))?\.json', b)
    if m:
        t = dt.datetime.strptime(m.group(1) + (m.group(2) or '0000'), '%Y-%m-%d%H%M').replace(tzinfo=dt.timezone.utc)
        return t.isoformat() + ('' if m.group(2) else '#day')
    return None
def ibm_index(rdir, out):
    n = 0; refused = []
    with gzip.open(out, 'wt') as o:
        for p in sorted(glob.glob(os.path.join(rdir, '*.json*'))):
            rt = read_time(p)
            if not rt: refused.append([os.path.basename(p), 'no read time']); continue
            try: b, stamp, Qd, csha = load_ibm(p)
            except Exception as e: refused.append([os.path.basename(p), 'unreadable ' + type(e).__name__]); continue
            o.write(json.dumps({'file': os.path.basename(p), 'read': rt, 'backend': b, 'stamp': stamp, 'content_sha': csha, 'q': Qd}) + '\n'); n += 1
    return dict(indexed=n, refused=refused)
def norm(s):
    """an instant in UTC; a time with no offset is refused (None), never read as this machine's local time"""
    try:
        d = dt.datetime.fromisoformat(str(s).split('#')[0].replace('Z', '+00:00'))
        return None if d.tzinfo is None else d.astimezone(dt.timezone.utc)
    except Exception: return None
def gap_h(a, b):
    x, y = norm(a['stamp']), norm(b['stamp']); return (y - x).total_seconds() / 3600 if x and y else None
def gap_bin(g):
    if g is None: return 'unknown'
    for name, lo, hi in BINS:
        if lo < g <= hi or (lo == 0 and g <= hi): return name
    return 'unknown'
def pairs(index):
    """consecutive records per backend in read-time order. Same stamp + same content: a true duplicate. Same stamp + different content:
    CARRIED (direction B), kept as a pair. A later read with an earlier stamp: a stamp regression, counted, not paired."""
    recs = {}
    for l in gzip.open(index, 'rt'):
        r = json.loads(l); recs.setdefault(r['backend'], []).append(r)
    out = []; obs = dict(duplicates=0, carried_same_stamp=0, stamp_regressions=0, order_by_stamp_tiebreak=0)
    far = dt.datetime.max.replace(tzinfo=dt.timezone.utc)
    for b, L in recs.items():
        L.sort(key=lambda r: (r['read'].split('#')[0], norm(r['stamp']) or far)); prev = None   # day-precision ties broken by stamp
        for r in L:
            if prev is not None:
                if r['read'].split('#')[0] == prev['read'].split('#')[0] and ('#day' in r['read'] or '#day' in prev['read']): obs['order_by_stamp_tiebreak'] += 1
                if r['stamp'] == prev['stamp'] or (norm(r['stamp']) and norm(r['stamp']) == norm(prev['stamp'])):
                    if r.get('content_sha') == prev.get('content_sha'): obs['duplicates'] += 1; continue
                    obs['carried_same_stamp'] += 1; out.append((b, prev, r, 'same_stamp')); prev = r; continue
                if norm(r['stamp']) and norm(prev['stamp']) and norm(r['stamp']) < norm(prev['stamp']): obs['stamp_regressions'] += 1; continue
                out.append((b, prev, r, 'moved'))
            prev = r
    return out, obs
def in_window(r): t = norm(r['stamp']) or norm(r['read']); return WINDOW[0] <= t.strftime('%Y-%m-%d') <= WINDOW[1]
def field_moves(a, b, f):
    res = []
    for q, e in b['q'].items():
        x = a['q'].get(q, {}).get(f); y = e.get(f)
        if not x or not y or x[1] is None or y[1] is None: continue
        res.append((x[1] != y[1], x[0] == y[0] and type(x[0]) == type(y[0])))
    return res
def pair_class(a, b, f):
    g = gap_h(a, b) or 0; mv = field_moves(a, b, f)
    if not mv or g <= 24: return 'unclassed', mv
    moved = sum(1 for m, _ in mv if m) / len(mv)
    if 1 - moved >= 0.95: return 'positive', mv
    if moved >= 0.50: return 'negative', mv
    return 'between', mv
def floors(index):
    P, _ = pairs(index); acc = {}
    for b, a, c, kind in P:
        if kind != 'moved' or not (in_window(a) and in_window(c)): continue
        for f in FIELDS:
            for m, same in field_moves(a, c, f):
                if m: s = acc.setdefault((b, f), [0, 0]); s[0] += same; s[1] += 1
    return acc
def floor_table(acc):
    rows = []; bks = sorted({b for b, f in acc})
    for f in FIELDS:
        for b in bks:
            k, n = acc.get((b, f), [0, 0]); ok = sum(acc.get((x, f), [0, 0])[0] for x in bks if x != b); on = sum(acc.get((x, f), [0, 0])[1] for x in bks if x != b)
            lo, hi = cp(k, n); olo, ohi = cp(ok, on)
            rows.append(dict(backend=b, field=f, identical=k, moves=n, interval=[lo, hi], others=[ok, on], others_interval=[olo, ohi],
                             leave_one_backend_out='ABOVE' if lo > ohi else ('CONSISTENT' if hi <= ohi else 'CANNOT_TELL'),
                             note=('u is the 95 %% upper bound of a rate never observed (0 identical in %d date moves); it measures history size' % n) if k == 0 else ''))
    return rows
def outcome(flag, hi, u, n):
    if n == 0 or u is None: return 'CANNOT_TELL', 'NO_INTERVAL_FORMABLE'
    if flag: return 'ABOVE', None
    if hi <= u + SIZE: return 'CONSISTENT', None   # worded in output as "bounded below u + 5 %", never "matches the floor"
    return 'CANNOT_TELL', 'TOO_WIDE_TO_RESOLVE'
def observe(P, skip_window=True):
    obs = {'FROZEN_RECORD': {}, 'FROZEN_QUBITS_ONLY': {}, 'FROZEN_DATE': {}, 'VALUE_CHANGED_DATE_UNCHANGED': {}, 'unmoved_date_identical_value': {}}
    for b, a, c, kind in P:
        if skip_window and (in_window(a) or in_window(c)): continue
        g = gap_bin(gap_h(a, c))
        if kind == 'moved':
            if a.get('content_sha') == c.get('content_sha'): obs['FROZEN_RECORD'][g] = obs['FROZEN_RECORD'].get(g, 0) + 1
            elif a['q'] == c['q']: obs['FROZEN_QUBITS_ONLY'][g] = obs['FROZEN_QUBITS_ONLY'].get(g, 0) + 1
        for f in FIELDS + QUANT:
            fd = vc = 0
            for q, e in c['q'].items():
                x = a['q'].get(q, {}).get(f); y = e.get(f)
                if not x or not y: continue
                if x[1] == y[1] and x[0] == y[0] and type(x[0]) == type(y[0]): obs['unmoved_date_identical_value'][f] = obs['unmoved_date_identical_value'].get(f, 0) + 1
                # FROZEN_DATE per plan: label moved, this field's date and value unchanged, and other fields under the label moved
                if kind == 'moved' and x[1] == y[1] and x[0] == y[0] and a.get('content_sha') != c.get('content_sha'): fd += 1
                if x[1] == y[1] and x[0] != y[0]: vc += 1
            if fd: obs['FROZEN_DATE'].setdefault(f, {})[g] = obs['FROZEN_DATE'].get(f, {}).get(g, 0) + fd
            if vc: obs['VALUE_CHANGED_DATE_UNCHANGED'].setdefault(f, {})[g] = obs['VALUE_CHANGED_DATE_UNCHANGED'].get(f, {}).get(g, 0) + vc
    return obs
def ibm_read(index, P=None, pobs=None, acc=None, u_fixed=None):
    if P is None: P, pobs = pairs(index)
    acc = acc if acc is not None else floors(index); ft = floor_table(acc)
    fu = {(r['backend'], r['field']): r['interval'][1] for r in ft if r['moves'] >= MIN_FLOOR}
    cross = {}
    for f in FIELDS:
        k = sum(r['identical'] for r in ft if r['field'] == f); n = sum(r['moves'] for r in ft if r['field'] == f)
        cross[f] = cp(k, n)[1] if n >= MIN_FLOOR else None
    reads = []; events = 0
    for b, a, c, kind in P:
        if in_window(a) or in_window(c) or kind != 'moved': continue
        for f in FIELDS:
            cl, mv = pair_class(a, c, f); n = sum(1 for m, _ in mv if m); k = sum(1 for m, s in mv if m and s); events += k
            u = u_fixed if u_fixed is not None else (fu.get((b, f)) or cross.get(f))
            reads.append(dict(backend=b, field=f, cls=cl, a=a['file'], b=c['file'], k=k, n=n, u=u, floor='fixed' if u_fixed is not None else ('backend' if (b, f) in fu else 'cross')))
    fam = {}
    for cl in CLASSES:
        R = [r for r in reads if r['cls'] == cl]; m = len(R); fam[cl] = m
        ps = [sf(r['k'], r['n'], r['u']) if r['u'] is not None and r['n'] else 1.0 for r in R]; fl = bh(ps)
        for r, p, g in zip(R, ps, fl):
            r['p'] = p; r['hi'] = cp(r['k'], r['n'])[1] if r['n'] else 1.0; r['family_m'] = m
            r['outcome'], r['reason'] = outcome(g, r['hi'], r['u'], r['n']); r['chance_expected'] = r['n'] * r['u'] if r['u'] is not None else None
    obs = observe(P); obs.update(pobs or {}); obs['RESTAMPED_IDENTICAL_events'] = events
    return dict(floor_table=ft, cross_floor=cross, bh_families=fam, observations=obs, readings=reads,
                consistent_means='the pair\'s identical share is bounded below u + 0.05 (95 % exact upper bound); it does not mean it matches the floor')
def ibm_counts(index):
    P, pobs = pairs(index); acc = floors(index); ft = floor_table(acc)
    fu = {(r['backend'], r['field']): r['interval'][1] for r in ft if r['moves'] >= MIN_FLOOR}
    cls = {}; ns = {}
    for b, a, c, kind in P:
        if in_window(a) or in_window(c) or kind != 'moved': continue
        for f in FIELDS:
            cl, mv = pair_class(a, c, f); cls[(cl, f)] = cls.get((cl, f), 0) + 1; ns.setdefault(cl, []).append((b, f, sum(1 for m, _ in mv if m)))
    fam = {cl: len(v) for cl, v in ns.items()}; thr = {}
    for cl, v in ns.items():
        for b, f, n in v:
            t = k_threshold(n, fu.get((b, f)), fam[cl])
            if n: thr.setdefault(f'{cl} {b} {f}', set()).add(t)
    return dict(pair_observations=pobs, window_pairs=sum(1 for b, a, c, k in P if in_window(a) and in_window(c)),
                classes={f'{c} {f}': v for (c, f), v in sorted(cls.items())}, bh_family_sizes=fam,
                k_threshold_smallest_p={k: sorted(x for x in v if x is not None) for k, v in sorted(thr.items())})

# ---------- snapshotted feeds (HF, CKAN, any JSON) ----------
DT = re.compile(r'^\s*\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?)?\s*$|^\s*\d{1,2}/\d{1,2}/\d{2,4}( \d{1,2}:\d{2}(:\d{2})?)?\s*$')
def getp(d, path):
    for k in path.split('.'):
        if isinstance(d, dict): d = d.get(k)
        else: return None
    return d
def units_of(s, path):
    """a units path may hold one '*' to flatten nested dicts, e.g. datasets.*.resources"""
    if '*' not in path: return getp(s, path) or {}
    head, tail = path.split('.*.', 1); out = {}
    for k, v in (getp(s, head) or {}).items():
        for u, obj in (getp(v, tail) or {}).items(): out[u] = obj
    return out
def h(o): return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()
def parse_read(x):
    """read time in the collectors' format (20261113T172813Z) or ISO; anything else is refused"""
    if not x: return None
    try: return dt.datetime.strptime(str(x), '%Y%m%dT%H%M%SZ').replace(tzinfo=dt.timezone.utc)
    except ValueError: return norm(x)
def check_spec(spec):
    if 'units' not in spec or 'label' not in spec or 'content' not in spec: raise ValueError('spec needs units, label and content')
    if bool(spec.get('evidence')) != bool(spec.get('evidence_content')): raise ValueError('evidence and evidence_content go together, or neither')
def csv_diff(old, new):
    """rows added, removed, changed, columns touched; and whether every changed cell is datetime-shaped"""
    o = list(csv.reader(io.StringIO(old.decode('utf-8', 'replace')))); n = list(csv.reader(io.StringIO(new.decode('utf-8', 'replace'))))
    hdr = n[0] if n else []; so = {tuple(r) for r in o[1:]}; sn = {tuple(r) for r in n[1:]}
    from collections import Counter
    if o[:1] == n[:1] and Counter(map(tuple, o[1:])) == Counter(map(tuple, n[1:])):
        return dict(rows_changed=0, rows_added=0, rows_removed=0, columns_touched=[], datetime_only=False, reorder_only=True)
    rem = so - sn; add = sn - so; changed = 0; cols = set(); only_dt = True
    if len(o) == len(n):
        for a, b in zip(o[1:], n[1:]):
            if a != b:
                changed += 1
                for i, (x, y) in enumerate(zip(a, b)):
                    if x != y:
                        cols.add(hdr[i] if i < len(hdr) else str(i))
                        if not (DT.match(x) and DT.match(y)): only_dt = False
        return dict(rows_changed=changed, rows_added=0, rows_removed=0, columns_touched=sorted(cols), datetime_only=only_dt and changed > 0, reorder_only=False)
    return dict(rows_changed=0, rows_added=len(add), rows_removed=len(rem), columns_touched=[], datetime_only=False, reorder_only=False)
def feed(spec, snaps, store=None):
    """spec: {units: path to a dict of unit -> object, label: path in the unit, content: [paths], evidence: [paths], evidence_content: [paths],
    repeat_floor: true for the first two snapshots as a repeat floor}. snaps: list of dicts with read_at; refused without it."""
    check_spec(spec)
    out = dict(snapshots=0, refused_no_read_time=0, units=0, pairs=0, duplicate=0, FROZEN_LABEL_CONTENT=0, CARRIED=0, CARRIED_datetime_only=0,
               evidence_stamp_frozen_content=0, nondeterministic_units=0, dropped=0, nothing_returned=0, carried_list=[])
    good = []
    for s in snaps:
        t = parse_read(s.get('read_at')) if isinstance(s, dict) else None
        if t is None: out['refused_no_read_time'] += 1; continue
        s['_t'] = t; good.append(s)
    good.sort(key=lambda s: s['_t']); out['snapshots'] = len(good)
    seq = {}
    for s in good:
        for u, obj in units_of(s, spec['units']).items(): seq.setdefault(u, []).append((s['read_at'], obj))
    out['units'] = len(seq); nondet = set()
    nondet = set(); floored = None
    if spec.get('repeat_floor'):
        t0 = good[0] if good else None
        rf = next((g for g in good[1:] if (g['_t'] - t0['_t']).total_seconds() >= 300), None) if t0 else None
        out['repeat_floor_pair'] = [t0['read_at'] if t0 else None, rf['read_at'] if rf else None]
        floored = set()
        if rf:
            for u, L in seq.items():
                a_ = [o for t, o in L if t == t0['read_at']]; b_ = [o for t, o in L if t == rf['read_at']]
                if a_ and b_:
                    floored.add(u)
                    if h([getp(a_[0], p) for p in spec['content']]) != h([getp(b_[0], p) for p in spec['content']]): nondet.add(u)
        out['no_repeat_floor'] = len([u for u in seq if u not in floored])   # FIX 2: a unit with no floor pair is excluded from direction B
    out['nondeterministic_units'] = len(nondet)
    for u, L in seq.items():
        for (ta, a), (tb, b) in zip(L, L[1:]):
            if any(getp(x, 'dropped') for x in (a, b)): out['dropped'] += 1; continue
            if any(getp(x, 'nothing_returned') for x in (a, b)): out['nothing_returned'] += 1; continue
            la, lb = getp(a, spec['label']), getp(b, spec['label'])
            ca, cb = h([getp(a, p) for p in spec['content']]), h([getp(b, p) for p in spec['content']])
            ev = spec.get('evidence', []); ea, eb = h([getp(a, p) for p in ev]), h([getp(b, p) for p in ev])
            ec = spec.get('evidence_content', []); eca, ecb = h([getp(a, p) for p in ec]), h([getp(b, p) for p in ec])
            if ev and ea != eb and eca == ecb: out['evidence_stamp_frozen_content'] += 1   # rule 6, second half, direction A on the evidence
            if la == lb and ca == cb: out['duplicate'] += 1; continue
            out['pairs'] += 1
            if la != lb and ca == cb: out['FROZEN_LABEL_CONTENT'] += 1
            if ca != cb and la == lb and (not ev or eca == ecb):
                if floored is not None and u not in floored: out['excluded_no_floor'] = out.get('excluded_no_floor', 0) + 1; continue
                if u in nondet: out['excluded_nondeterministic'] = out.get('excluded_nondeterministic', 0) + 1; continue
                item = dict(unit=u, a=ta, b=tb)
                if store:   # FIX 3: diff a's own bytes against b's own bytes, stored by sha
                    pa = os.path.join(store, f"{u}__{str(getp(a, 'sha256'))[:12]}.csv.gz"); pb = os.path.join(store, f"{u}__{str(getp(b, 'sha256'))[:12]}.csv.gz")
                    if os.path.exists(pa) and os.path.exists(pb):
                        item['diff'] = csv_diff(gzip.decompress(open(pa, 'rb').read()), gzip.decompress(open(pb, 'rb').read()))
                d = item.get('diff')
                if spec.get('requires_diff') and d is None: out['CARRIED_no_diff'] = out.get('CARRIED_no_diff', 0) + 1; item['outcome'] = 'CANNOT_TELL'; item['reason'] = 'NOT_RELEASED'
                elif d and d.get('reorder_only'): out['CARRIED_reorder_only'] = out.get('CARRIED_reorder_only', 0) + 1; item['outcome'] = 'CANNOT_TELL'; item['reason'] = 'METHOD_UNSTATED'
                elif d and d.get('datetime_only'): out['CARRIED_datetime_only'] += 1; item['outcome'] = 'CANNOT_TELL'; item['reason'] = 'METHOD_UNSTATED'
                else: out['CARRIED'] += 1
                out['carried_list'].append(item)
    return out
def quantized(series, step, ref):
    res = []
    for (t0, v0), (t1, v1) in zip(series, series[1:]):
        if v0 != v1: continue
        if t1 not in ref: res.append((t1, 'CANNOT_TELL', 'NO_INTERVAL_FORMABLE'))
        elif abs(ref[t1] - v1) >= step - 1e-12: res.append((t1, 'ABOVE', None))
        else: res.append((t1, 'CONSISTENT', None))
    return res

# ---------- planted cases, end to end ----------
def selftest():
    ok = True
    def check(name, got, want):
        nonlocal ok
        good = got == want; ok &= good; print(('ok  ' if good else 'FAIL'), name, '->', got, '' if good else f'(want {want})')
    R = random.Random(20261113); td = tempfile.mkdtemp(prefix='sw_selftest_')
    def rec(stamp, prev=None, frozen=(), identical=(), all_frozen=False, gates=None):
        q = []
        for i in range(156):
            row = []
            for f in FIELDS:
                if prev and (all_frozen or i in frozen): v, d = prev['_q'][i][f]
                elif prev and i in identical and f == 'T1': v, d = prev['_q'][i][f][0], stamp
                else: v, d = round(R.uniform(80, 300), 4) * 1e-6, stamp
                row.append({'name': f, 'value': v, 'date': d, 'unit': 's'})
            if prev and (all_frozen or i in frozen): rv = prev['_q'][i]['readout_error']
            else: rv = [R.randint(1, 60) / 4000, stamp]
            row.append({'name': 'readout_error', 'value': rv[0], 'date': rv[1], 'unit': ''}); q.append(row)
        d = {'backend_name': 'syn_backend', 'last_update_date': stamp, 'qubits': q, 'gates': gates if gates is not None else [{'gate': 'cz', 'value': R.random()}], 'general': []}
        d['_q'] = {i: {x['name']: [x['value'], x['date']] for x in r} for i, r in enumerate(q)}
        return d
    def save(d, read):
        dd = {k: v for k, v in d.items() if k != '_q'}; p = os.path.join(td, f'syn_backend__{read}.json.gz'); open(p, 'wb').write(gzip.compress(json.dumps(dd).encode())); return d
    T = lambda day, hr=12: f'2026-10-{day:02d}T{hr:02d}:00:00+00:00'; RT = lambda day, hr=12: f'202610{day:02d}T{hr:02d}0000'
    r0 = save(rec(T(1)), RT(1)); r1 = save(rec(T(3), r0), RT(3))
    r2 = rec(T(5), r1, all_frozen=True, gates=None); r2['gates'] = json.loads(json.dumps({k: v for k, v in r1.items() if k == 'gates'}['gates'])); save(r2, RT(5))   # whole record frozen, stamp moved
    r3 = save(rec(T(7), r2, frozen=set(range(100))), RT(7))                                   # some fields frozen under a moved label
    r4 = save(rec(T(9), r3, identical=set(range(20))), RT(9))                                 # 20 of 156 identical restamps
    r5 = save(rec(T(11), r4, identical={3}), RT(11))                                          # one identical restamp at the planted floor
    r6 = rec(T(11), r5); save(r6, RT(11, 18))                                                 # same stamp, different content: CARRIED
    save(r6, RT(11, 19))                                                                      # true duplicate
    open(os.path.join(td, 'syn_backend_no_read_time.json'), 'w').write('{}')                  # refused: no read time
    ix = os.path.join(td, 'ix.jsonl.gz'); res = ibm_index(td, ix)
    check('refused file with no read time', res['refused'][0][1] if res['refused'] else None, 'no read time')
    P, pobs = pairs(ix)
    check('same stamp, different content: CARRIED', pobs['carried_same_stamp'], 1)
    check('same stamp, same content: duplicate', pobs['duplicates'], 1)
    obs = observe(P, skip_window=False)
    check('whole record frozen: FROZEN_RECORD (content_sha)', sum(obs['FROZEN_RECORD'].values()), 1)
    check('FROZEN_DATE needs other fields moved', obs['FROZEN_DATE'].get('T1', {}).get('>24h'), 100)
    global WINDOW
    w0 = WINDOW; WINDOW = ('2000-01-01', '2000-01-02')
    try:
        acc_u = {('syn_backend', 'T1'): [5, 85000], ('syn_backend', 'T2'): [5, 85000]}
        out = ibm_read(ix, P, pobs, acc=acc_u)
        above = [r for r in out['readings'] if r['field'] == 'T1' and r['k'] == 20]
        check('20 of 156 identical restamps reads ABOVE (end to end)', above[0]['outcome'] if above else None, 'ABOVE')
        # single identical restamp in its OWN run at u = 0.001: exact p, family size and outcome (FIX 5)
        td2 = tempfile.mkdtemp(prefix='sw_single_'); 
        for d, rt in ((r4, RT(9)), (r5, RT(11))):
            dd = {k: v for k, v in d.items() if k != '_q'}; open(os.path.join(td2, f'syn_backend__{rt}.json.gz'), 'wb').write(gzip.compress(json.dumps(dd).encode()))
        ix2 = os.path.join(td2, 'ix.jsonl.gz'); ibm_index(td2, ix2); P2, po2 = pairs(ix2)
        out2 = ibm_read(ix2, P2, po2, acc={}, u_fixed=0.001)
        one = [r for r in out2['readings'] if r['field'] == 'T1']
        check('single restamp, own run, u=0.001: k, n, p, family m, outcome', (one[0]['k'], one[0]['n'], round(one[0]['p'], 4), one[0]['family_m'], one[0]['outcome']) if one else None, (1, 156, 0.1445, 2, 'CONSISTENT'))
    finally:
        WINDOW = w0
    # real-floor single event: BH arithmetic on hand-built families (not end to end): u ~ 0.00025, n = 156
    u = cp(0, 14800)[1]; p1 = sf(1, 156, u)
    check(f'BH arithmetic: real floor k=1 (p={p1:.3f}) unflagged with m=12', bh([p1] + [1.0] * 11)[0], False)
    check('BH arithmetic: real floor k=1 unflagged with m=5550', bh([p1] + [1.0] * 5549)[0], False)
    check('BH arithmetic: real floor k=2 flagged with m=12', bh([sf(2, 156, u)] + [1.0] * 11)[0], True)
    check('BH arithmetic: real floor k=2 not flagged with m=5550', bh([sf(2, 156, u)] + [1.0] * 5549)[0], False)
    # rule 5
    s = [(0, 0.33), (1, 0.33), (2, 0.33)]
    check('quantized repeat contradicted by reference', quantized(s, 1 / 3, {1: 0.33, 2: 1.00})[-1][1], 'ABOVE')
    check('quantized repeat agreed by reference', quantized(s, 1 / 3, {1: 0.33, 2: 0.33})[-1][1], 'CONSISTENT')
    check('quantized repeat with no reference', quantized(s, 1 / 3, {})[0][1], 'CANNOT_TELL')
    # feeds, real read-time format (FIX 1): floor is the first snapshot at least 300 s after the first one
    T0, T2m, T6m, TL, TL2 = '20261113T180000Z', '20261113T180200Z', '20261113T180600Z', '20261114T000000Z', '20261114T040000Z'
    it = lambda v, q, va=1, s_='s': {'verified': v, 'quote': q, 'verified_at': va, 'source_sha': s_}
    spec = {'units': 'items', 'label': 'verified', 'content': ['quote'], 'evidence': ['verified_at'], 'evidence_content': ['source_sha'], 'repeat_floor': True}
    snaps = [{'read_at': T2m, 'items': {'x': it(1, 'a'), 'y': it(1, 'p'), 'n': it(1, 'CHANGED_AT_2MIN')}},
             {'read_at': T0, 'items': {'x': it(1, 'a'), 'y': it(1, 'p'), 'n': it(1, 'r0')}},
             {'read_at': T6m, 'items': {'x': it(1, 'a'), 'y': it(1, 'p'), 'n': it(1, 'r6')}},
             {'read_at': TL, 'items': {'x': it(1, 'b'), 'y': it(2, 'p', 2), 'n': it(1, 'r9'), 'z': it(1, 'new')}},
             {'read_at': TL2, 'items': {'x': it(1, 'b'), 'y': it(2, 'p', 2), 'n': it(1, 'r9'), 'z': it(1, 'newer')}},
             {'read_at': 'yesterday', 'items': {}}, {'items': {}}, {'read_at': '2026-11-13T18:00:00', 'items': {}}]
    g = feed(spec, snaps)
    check('feed: unparseable, missing or naive (no offset) read times are refused', g['refused_no_read_time'], 3)
    check('feed: the 2-minute snapshot is not the floor pair, the 6-minute one is', g['repeat_floor_pair'], [T0, T6m])
    check('feed: unit that changed across the floor pair is non-deterministic', g['nondeterministic_units'], 1)
    check('feed: direction B per unit (x)', g['CARRIED'], 1)
    check('feed: unit that appeared after the floor is excluded from B (z)', (g['no_repeat_floor'], g.get('excluded_no_floor')), (1, 1))
    check('feed: direction A per unit (y label moved, content same)', g['FROZEN_LABEL_CONTENT'], 1)
    check('feed: evidence stamp moved with unchanged evidence content (y)', g['evidence_stamp_frozen_content'], 1)
    try: feed({'units': 'items', 'label': 'v', 'content': ['q'], 'evidence': ['e']}, []); bad = False
    except ValueError: bad = True
    check('feed: spec with evidence but no evidence_content is refused', bad, True)
    g = feed({'units': 'ds.*.res', 'label': 'lm', 'content': ['sha256']}, [{'read_at': T0, 'ds': {'d1': {'res': {'a': {'lm': 1, 'sha256': 'x'}}}}}, {'read_at': T6m, 'ds': {'d1': {'res': {'a': {'lm': 2, 'sha256': 'x'}}}}}])
    check('feed: wildcard units flatten nested resources, label moved with content frozen', g['FROZEN_LABEL_CONTENT'], 1)
    g = feed({'units': 'r', 'label': 'lm', 'content': ['sha256']}, [{'read_at': T0, 'r': {'a': {'lm': 1, 'sha256': 'x'}}}, {'read_at': T6m, 'r': {'a': {'lm': 1, 'dropped': 'too_large'}}}])
    check('feed: too_large is dropped, not compared', g['dropped'], 1)
    # CKAN-shaped: stored bytes by sha; missing bytes -> CARRIED_no_diff; reordered rows -> reorder_only; datetime-only -> CANNOT_TELL
    st = tempfile.mkdtemp(prefix='sw_store_')
    def put(u, b): sh = hashlib.sha256(b).hexdigest(); open(os.path.join(st, f'{u}__{sh[:12]}.csv.gz'), 'wb').write(gzip.compress(b)); return sh
    A1 = b'id,updated,val\n1,2026-11-12T03:00:00Z,5\n2,2026-11-12T03:00:00Z,6\n'; A2 = b'id,updated,val\n1,2026-11-13T03:00:00Z,5\n2,2026-11-13T03:00:00Z,6\n'
    B1 = b'id,val\n1,5\n2,6\n'; B2 = b'id,val\n2,6\n1,5\n'; C1 = b'id,val\n1,5\n'; C2 = b'id,val\n1,7\n'
    sa1, sa2, sb1, sb2, sc1, sc2 = put('dt', A1), put('dt', A2), put('ro', B1), put('ro', B2), put('rv', C1), put('rv', C2)
    cspec = {'units': 'r', 'label': 'lm', 'content': ['sha256'], 'repeat_floor': True, 'requires_diff': True}
    rr = lambda dtsha, rosha, rvsha, nsha: {'dt': {'lm': 1, 'sha256': dtsha}, 'ro': {'lm': 1, 'sha256': rosha}, 'rv': {'lm': 1, 'sha256': rvsha}, 'nd': {'lm': 1, 'sha256': nsha}}
    snaps = [{'read_at': T0, 'r': rr(sa1, sb1, sc1, 'n1')}, {'read_at': T6m, 'r': rr(sa1, sb1, sc1, 'n1')}, {'read_at': TL, 'r': rr(sa2, sb2, sc2, 'n2')}]
    g = feed(cspec, snaps, st)
    reasons = sorted((c['unit'], c.get('outcome', 'CARRIED'), c.get('reason')) for c in g['carried_list'])
    check('ckan: datetime-only diff and reorder-only read CANNOT_TELL (METHOD_UNSTATED); a real value change is CARRIED; no stored bytes is NOT_RELEASED',
          reasons, [('dt', 'CANNOT_TELL', 'METHOD_UNSTATED'), ('nd', 'CANNOT_TELL', 'NOT_RELEASED'), ('ro', 'CANNOT_TELL', 'METHOD_UNSTATED'), ('rv', 'CARRIED', None)])
    d = csv_diff(B1, B2); check('csv diff: two rows swapped is reorder_only', d['reorder_only'], True)
    d = csv_diff(b'id,updated,val\n1,2026-11-12,5\n', b'id,updated,val\n1,2026-11-12,6\n')
    check('csv diff: a real value change is not datetime-only', d['datetime_only'], False)
    check('cp(0, 10) upper = 0.3085', round(cp(0, 10)[1], 4), 0.3085)
    print('SELFTEST', 'PASSED' if ok else 'FAILED'); return ok

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == 'selftest': sys.exit(0 if selftest() else 1)
    if a[0] == 'ibm-index': print(json.dumps(ibm_index(a[1], a[2] if len(a) > 2 else 'ibm_index.jsonl.gz'), indent=1))
    elif a[0] == 'ibm-counts': print(json.dumps(ibm_counts(a[1]), indent=1))
    elif a[0] == 'ibm-floor': print(json.dumps(floor_table(floors(a[1])), indent=1))
    elif a[0] == 'ibm-read': print(json.dumps(ibm_read(a[1]), indent=1, default=str))
    elif a[0] == 'feed':
        spec = json.load(open(a[1])); snaps = []; bad = 0
        for p in glob.glob(os.path.join(a[2], '*.json*')):
            try: snaps.append(json.load(gzip.open(p, 'rt') if p.endswith('.gz') else open(p)))
            except Exception: bad += 1
        res = feed(spec, snaps, spec.get('store_dir')); res['snapshots_nothing_returned'] = bad
        print(json.dumps(res, indent=1, default=str))
