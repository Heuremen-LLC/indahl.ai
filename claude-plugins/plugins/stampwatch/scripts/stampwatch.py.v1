#!/usr/bin/env python3
"""stampwatch.py -- Heuremen LLC (https://indahl.ai). Standard library only. Plan: plans/stampwatch/PLAN.md, PLAN_v2.md, PLAN_v3.md
(and v4) in github.com/Heuremen-LLC/claude-plugins. Detects a label that stops being bound to the content it attests, in two directions:
A, the label moves while the content is frozen; B, the content moves while the label is carried. It names no cause.

  python3 stampwatch.py selftest                         planted cases, one per axis; exits non-zero if any comes out wrong
  python3 stampwatch.py ibm-index RECORDS_DIR            parse IBM BackendProperties records once into a compact index (no reading)
  python3 stampwatch.py ibm-counts INDEX                 floor-window counts and pair classes per field (dates only, no value compared)
  python3 stampwatch.py ibm-floor INDEX                  floors per backend and field, and the leave-one-backend-out check
  python3 stampwatch.py ibm-read INDEX [--from DATE]     FROZEN_RECORD / FROZEN_DATE counts and rule 4 readings on pairs after the window
  python3 stampwatch.py generic SPEC.json SNAP_DIR       direction A and B counts on any JSON feed (labels, content, evidence paths)

Observations (FROZEN_RECORD, FROZEN_DATE, CARRIED, value-changed-date-unchanged, RESTAMPED_IDENTICAL events) are counts. Outcomes
(ABOVE, CONSISTENT, CANNOT_TELL with a reason, NOTHING_RETURNED) come only from rule 4 (and rule 5 when a reference is given)."""
import json, gzip, os, sys, glob, math, hashlib, datetime as dt, random

WINDOW = ('2026-05-04', '2026-09-14')      # floor window (PLAN_v2)
MIN_FLOOR = 500; SIZE = 0.05; Q = 0.05     # PLAN_v3
FIELDS = ('T1', 'T2'); QUANT = ('readout_error', 'prob_meas0_prep1', 'prob_meas1_prep0')

# ---------- exact binomial machinery (stdlib) ----------
def _lpmf(k, n, p):
    if p <= 0: return 0.0 if k == 0 else -math.inf
    if p >= 1: return 0.0 if k == n else -math.inf
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log1p(-p)
def sf(k, n, p):
    """P(X >= k), X ~ Bin(n, p)"""
    if k <= 0: return 1.0
    if k > n: return 0.0
    m = [_lpmf(i, n, p) for i in range(k, n + 1)]; mx = max(m)
    if mx == -math.inf: return 0.0
    return min(1.0, math.exp(mx) * sum(math.exp(x - mx) for x in m))
def cdf(k, n, p): return 1.0 - sf(k + 1, n, p)
def cp(k, n, a=0.05):
    """exact (Clopper-Pearson) two-sided interval for k of n, by bisection"""
    if n == 0: return (0.0, 1.0)
    def bis(f, lo=0.0, hi=1.0):
        for _ in range(80):
            mid = (lo + hi) / 2
            if f(mid): hi = mid
            else: lo = mid
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else bis(lambda p: sf(k, n, p) >= a / 2)
    hi = 1.0 if k == n else bis(lambda p: cdf(k, n, p) <= a / 2)
    return (lo, hi)
def bh(ps, q=Q):
    """Benjamini-Hochberg: returns a list of booleans, flagged"""
    m = len(ps); order = sorted(range(m), key=lambda i: ps[i]); cut = -1
    for r, i in enumerate(order, 1):
        if ps[i] <= q * r / m: cut = r
    flag = [False] * m
    for r, i in enumerate(order, 1): flag[i] = r <= cut
    return flag

# ---------- IBM adapter ----------
def load_ibm(p):
    with (gzip.open(p, 'rt', encoding='utf-8') if p.endswith('.gz') else open(p, encoding='utf-8')) as f: d = json.load(f)
    Q_ = {}
    for i, qs in enumerate(d.get('qubits', [])):
        Q_[i] = {x['name']: [x.get('value'), x.get('date')] for x in qs if x.get('name') in FIELDS + QUANT}
    rest = {k: v for k, v in d.items() if k != 'last_update_date'}   # everything the stamp attests: qubits, gates, general
    return d.get('backend_name'), d.get('last_update_date'), Q_, hashlib.sha256(json.dumps(rest, sort_keys=True, default=str).encode()).hexdigest()
def read_time(p):
    b = os.path.basename(p)
    if '__' in b:
        t = b.split('__')[1][:15]
        try: return dt.datetime.strptime(t, '%Y%m%dT%H%M%S').replace(tzinfo=dt.timezone.utc).isoformat()
        except ValueError: pass
    return None
def ibm_index(rdir, out):
    n = bad = 0
    with gzip.open(out, 'wt') as o:
        for p in sorted(glob.glob(os.path.join(rdir, '*.json*'))):
            rt = read_time(p)
            if not rt: bad += 1; continue   # no read time: refused (PLAN)
            try: b, stamp, Qd, csha = load_ibm(p)
            except Exception: bad += 1; continue
            o.write(json.dumps({'file': os.path.basename(p), 'read': rt, 'backend': b, 'stamp': stamp, 'content_sha': csha, 'q': Qd}) + '\n'); n += 1
    print(f'indexed {n} records, refused or unreadable {bad}')
def norm(s):
    try: return dt.datetime.fromisoformat(str(s).replace('Z', '+00:00')).astimezone(dt.timezone.utc)
    except Exception: return None
def pairs(index):
    recs = {}
    for l in gzip.open(index, 'rt'):
        r = json.loads(l); recs.setdefault(r['backend'], []).append(r)
    out, dup = [], 0
    for b, L in recs.items():
        L.sort(key=lambda r: (norm(r['stamp']) or dt.datetime.min.replace(tzinfo=dt.timezone.utc), r['read']))
        prev = None
        for r in L:
            if prev is not None:
                if r['stamp'] == prev['stamp']: dup += 1; continue   # duplicate snapshots of one stamp: one observation, never a pair
                out.append((b, prev, r))
            prev = r
    return out, dup
def in_window(r): return WINDOW[0] <= (norm(r['stamp']) or norm(r['read'])).strftime('%Y-%m-%d') <= WINDOW[1]
def field_moves(a, b, f):
    """per qubit present in both: (date_moved, value_identical)"""
    res = []
    for q, e in b['q'].items():
        x = a['q'].get(q, {}).get(f); y = e.get(f)
        if not x or not y or x[1] is None or y[1] is None: continue
        res.append((x[1] != y[1], x[0] == y[0] and type(x[0]) == type(y[0])))
    return res
def pair_class(a, b, f):
    gap = (norm(b['stamp']) - norm(a['stamp'])).total_seconds() / 3600 if norm(a['stamp']) and norm(b['stamp']) else 0
    mv = field_moves(a, b, f)
    if not mv or gap <= 24: return 'unclassed', mv
    moved = sum(1 for m, _ in mv if m) / len(mv)
    if 1 - moved >= 0.95: return 'positive', mv
    if moved >= 0.50: return 'negative', mv
    return 'between', mv

def floors(index):
    P, _ = pairs(index); acc = {}
    for b, a, c in P:
        if not (in_window(a) and in_window(c)): continue
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
            lobo = 'ABOVE' if lo > ohi else ('CONSISTENT' if hi <= ohi else 'CANNOT_TELL')
            rows.append(dict(backend=b, field=f, identical=k, moves=n, share=k / n if n else None, interval=[lo, hi], others=[ok, on], others_interval=[olo, ohi], leave_one_backend_out=lobo))
    return rows

def read_pair(k, n, u):
    p = sf(k, n, u); hi = cp(k, n)[1] if n else 1.0
    return p, hi
def outcome(flag, hi, u, n):
    if n == 0: return 'CANNOT_TELL', 'NO_INTERVAL_FORMABLE'
    if flag: return 'ABOVE', None
    if hi <= u + SIZE: return 'CONSISTENT', None
    return 'CANNOT_TELL', 'TOO_WIDE_TO_RESOLVE'

def ibm_read(index, since=None, classes=('negative', 'between', 'positive', 'unclassed')):
    acc = floors(index); ft = floor_table(acc); fu = {}
    for r in ft:
        if r['moves'] >= MIN_FLOOR: fu[(r['backend'], r['field'])] = r['interval'][1]
    cross = {}
    for f in FIELDS:
        k = sum(r['identical'] for r in ft if r['field'] == f); n = sum(r['moves'] for r in ft if r['field'] == f)
        cross[f] = cp(k, n)[1] if n >= MIN_FLOOR else None
    P, dup = pairs(index); reads, obs = [], dict(FROZEN_RECORD=0, FROZEN_DATE={}, VALUE_CHANGED_DATE_UNCHANGED={}, RESTAMPED_IDENTICAL_events=0, duplicate_snapshots=dup)
    for b, a, c in P:
        if in_window(a) or in_window(c): continue
        if since and (norm(c['stamp']) or norm(c['read'])).strftime('%Y-%m-%d') < since: continue
        if a['stamp'] != c['stamp']:
            if a.get('content_sha') and a.get('content_sha') == c.get('content_sha'): obs['FROZEN_RECORD'] += 1   # every field under the stamp unchanged (qubits, gates, general)
            elif a['q'] == c['q']: obs['FROZEN_QUBITS_ONLY'] = obs.get('FROZEN_QUBITS_ONLY', 0) + 1   # T1, T2 and readout figures unchanged, other fields (gates, general) moved
        for f in FIELDS + QUANT:
            fd = vc = 0
            for q, e in c['q'].items():
                x = a['q'].get(q, {}).get(f); y = e.get(f)
                if not x or not y: continue
                if x[1] == y[1] and x[0] == y[0] and a['stamp'] != c['stamp']: fd += 1
                if x[1] == y[1] and x[0] != y[0]: vc += 1
            obs['FROZEN_DATE'][f] = obs['FROZEN_DATE'].get(f, 0) + fd; obs['VALUE_CHANGED_DATE_UNCHANGED'][f] = obs['VALUE_CHANGED_DATE_UNCHANGED'].get(f, 0) + vc
        for f in FIELDS:
            cl, mv = pair_class(a, c, f)
            if cl not in classes: continue
            n = sum(1 for m, _ in mv if m); k = sum(1 for m, s in mv if m and s); obs['RESTAMPED_IDENTICAL_events'] += k
            u = fu.get((b, f)) or cross.get(f)
            reads.append(dict(backend=b, field=f, cls=cl, a=a['file'], b=c['file'], k=k, n=n, u=u, floor='backend' if (b, f) in fu else 'cross'))
    ps = [sf(r['k'], r['n'], r['u']) if r['u'] is not None and r['n'] else 1.0 for r in reads]; fl = bh(ps)
    for r, p, g in zip(reads, ps, fl):
        r['p'] = p; hi = cp(r['k'], r['n'])[1] if r['n'] else 1.0; r['hi'] = hi
        r['outcome'], r['reason'] = outcome(g, hi, r['u'] or 0, r['n']) if r['u'] is not None else ('CANNOT_TELL', 'NO_INTERVAL_FORMABLE')
        r['chance_expected'] = (r['n'] * r['u']) if r['u'] is not None else None
    return dict(floor_table=ft, cross_floor=cross, observations=obs, readings=reads)

def ibm_counts(index):
    P, dup = pairs(index); acc = floors(index); win = sum(1 for b, a, c in P if in_window(a) and in_window(c))
    cls = {}; exp = {}
    fu = {(b, f): cp(k, n)[1] for (b, f), (k, n) in acc.items() if n >= MIN_FLOOR}
    for b, a, c in P:
        if in_window(a) or in_window(c): continue
        for f in FIELDS:
            cl, mv = pair_class(a, c, f); cls[(cl, f)] = cls.get((cl, f), 0) + 1
            if cl == 'negative':
                n = sum(1 for m, _ in mv if m); u = fu.get((b, f))
                if u is not None and n:   # chance that this reading's raw p falls at or under 0.05 under the floor (an upper bound on BH flags)
                    kc = next((k for k in range(n + 1) if sf(k, n, u) <= 0.05), None)
                    exp[f] = exp.get(f, 0) + (sf(kc, n, u) if kc is not None else 0)
    return dict(window_pairs=win, duplicate_snapshots=dup, floor_moves={f'{b} {f}': n for (b, f), (k, n) in sorted(acc.items())},
                classes={f'{c} {f}': v for (c, f), v in sorted(cls.items())}, negative_expected_false_flags_upper=exp)

# ---------- generic adapter (direction A and B on any JSON feed) ----------
def get(d, path):
    for k in path.split('.'):
        if isinstance(d, dict): d = d.get(k)
        elif isinstance(d, list) and k.isdigit() and int(k) < len(d): d = d[int(k)]
        else: return None
    return d
def h(o): return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()
def generic(spec, snaps):
    """spec: {label: path, content: [paths], evidence: [paths] (optional), static: [paths]}; snaps: [(read_time, dict)] in time order"""
    out = dict(FROZEN_RECORD=0, CARRIED=0, evidence_stamp_only=0, pairs=0, missing_read_time=0, duplicate=0); prev = None
    for rt, d in snaps:
        if not rt: out['missing_read_time'] += 1; continue
        if prev is not None:
            pl, cl = get(prev, spec['label']), get(d, spec['label'])
            pc, cc = h([get(prev, p) for p in spec['content']]), h([get(d, p) for p in spec['content']])
            ev = spec.get('evidence', []); pe = h([get(prev, p) for p in ev]); ce = h([get(d, p) for p in ev])
            evc = h([get(prev, p) for p in spec.get('evidence_content', [])]) != h([get(d, p) for p in spec.get('evidence_content', [])])
            if pl == cl and pc == cc: out['duplicate'] += 1
            else:
                out['pairs'] += 1
                if pl != cl and pc == cc: out['FROZEN_RECORD'] += 1
                if pc != cc and pl == cl:
                    if not ev or pe == ce: out['CARRIED'] += 1
                    elif not evc: out['CARRIED'] += 1; out['evidence_stamp_only'] += 1   # PLAN_v2 rule 6: a touched evidence stamp without new content
        prev = d
    return out
def quantized(series, step, ref):
    """rule 5: series [(t, value)], ref {t: value}. A repeat the reference contradicts is ABOVE; a repeat it agrees with is CONSISTENT;
    no reference is CANNOT_TELL."""
    res = []
    for (t0, v0), (t1, v1) in zip(series, series[1:]):
        if v0 != v1: continue
        if t1 not in ref: res.append((t1, 'CANNOT_TELL', 'NO_INTERVAL_FORMABLE'))
        elif abs(ref[t1] - v1) >= step - 1e-12: res.append((t1, 'ABOVE', None))
        else: res.append((t1, 'CONSISTENT', None))
    return res

# ---------- planted cases ----------
def selftest():
    ok = True
    def check(name, got, want):
        nonlocal ok
        good = got == want; ok &= good; print(('ok  ' if good else 'FAIL'), name, '->', got, '' if good else f'(want {want})')
    R = random.Random(20261113)
    # synthetic IBM-like records: 156 qubits, noisy T1/T2 that change on remeasure
    def rec(stamp, prev=None, frozen=(), identical=(), all_frozen=False):
        q = {}
        for i in range(156):
            if prev and (all_frozen or i in frozen): q[i] = json.loads(json.dumps(prev['q'][i])); continue
            e = {}
            for f in FIELDS:
                if prev and i in identical and f == 'T1': e[f] = [prev['q'][i][f][0], stamp]          # date moves, value bitwise identical
                else: e[f] = [round(R.uniform(80, 300), 4) * 1e-6, stamp]
            e['readout_error'] = [R.randint(1, 60) / 4000, stamp]; q[i] = e
        return {'file': f'syn__{stamp}', 'read': stamp, 'backend': 'syn', 'stamp': stamp, 'q': q}
    t = lambda d: f'2026-10-{d:02d}T12:00:00+00:00'
    r0 = rec(t(1)); r1 = rec(t(3), r0); r2 = rec(t(5), r1, all_frozen=True); r2['stamp'] = t(5)
    r3 = rec(t(7), r2, frozen=set(range(100))); r4 = rec(t(9), r3, identical=set(range(20))); r5 = rec(t(11), r4, identical={3})
    # 1 whole record frozen
    check('whole record frozen: FROZEN_RECORD', all(r1['q'][q] == e for q, e in r2['q'].items()) and r1['stamp'] != r2['stamp'], True)
    # 2 some fields frozen under a moved label
    cl, mv = pair_class(r2, r3, 'T1'); check('some fields frozen: class with 100 of 156 dates unchanged', cl, 'between')
    # 3 restamp with identical value, 20 of 156, against a realistic floor
    u = cp(5, 85000)[1]; mv = field_moves(r3, r4, 'T1'); n = sum(1 for m, _ in mv if m); k = sum(1 for m, s in mv if m and s)
    ps = [sf(k, n, u)] + [sf(0, 156, u)] * 30; fl = bh(ps); check('20 of 156 identical restamps reads ABOVE', outcome(fl[0], cp(k, n)[1], u, n)[0], 'ABOVE')
    # 3b single identical restamp at a planted floor chosen so p > 0.05 by construction (u = 0.001, n = 156, 31 readings: p = 1-(1-u)^156 ~ 0.145)
    mv = field_moves(r4, r5, 'T1'); n = sum(1 for m, _ in mv if m); k = sum(1 for m, s in mv if m and s); u1 = 0.001
    p1 = sf(k, n, u1); fl = bh([p1] + [1.0] * 30); check(f'single identical restamp (k={k}, n={n}, u=0.001, p={p1:.3f}) is a count, not flagged', fl[0], False)
    # 4 quantized repeat contradicted by the reference, and 5 agreed by the reference
    s = [(0, 0.33), (1, 0.33), (2, 0.33)]
    check('quantized repeat contradicted by reference', quantized(s, 1 / 3, {1: 0.33, 2: 1.00})[-1][1], 'ABOVE')
    check('quantized repeat agreed by reference', quantized(s, 1 / 3, {1: 0.33, 2: 0.33})[-1][1], 'CONSISTENT')
    check('quantized repeat with no reference', quantized(s, 1 / 3, {})[0][1], 'CANNOT_TELL')
    # 6 direction B with no evidence change, 7 with only the evidence stamp touched, and a fresh-evidence negative
    spec = {'label': 'verified', 'content': ['quote'], 'evidence': ['verified_at'], 'evidence_content': ['source_sha']}
    snaps = [('t0', {'verified': True, 'quote': 'a', 'verified_at': 1, 'source_sha': 'x'}), ('t1', {'verified': True, 'quote': 'b', 'verified_at': 1, 'source_sha': 'x'})]
    check('direction B, no evidence change: CARRIED', generic(spec, snaps)['CARRIED'], 1)
    snaps = [('t0', {'verified': True, 'quote': 'a', 'verified_at': 1, 'source_sha': 'x'}), ('t1', {'verified': True, 'quote': 'b', 'verified_at': 2, 'source_sha': 'x'})]
    g = generic(spec, snaps); check('direction B, evidence stamp only: CARRIED', (g['CARRIED'], g['evidence_stamp_only']), (1, 1))
    snaps = [('t0', {'verified': True, 'quote': 'a', 'verified_at': 1, 'source_sha': 'x'}), ('t1', {'verified': True, 'quote': 'b', 'verified_at': 2, 'source_sha': 'y'})]
    check('direction B with fresh evidence: not flagged', generic(spec, snaps)['CARRIED'], 0)
    # 8 duplicate snapshots with one stamp, 9 a missing read time
    snaps = [('t0', {'verified': 1, 'quote': 'a'}), ('t1', {'verified': 1, 'quote': 'a'}), (None, {'verified': 2, 'quote': 'a'})]
    g = generic({'label': 'verified', 'content': ['quote']}, snaps); check('duplicate snapshot and missing read time', (g['duplicate'], g['missing_read_time']), (1, 1))
    # binomial machinery against known values
    check('cp(0, 10) upper = 0.3085', round(cp(0, 10)[1], 4), 0.3085)
    check('sf(1, 156, 0.001) = 0.1445', round(sf(1, 156, 0.001), 4), 0.1445)
    print('SELFTEST', 'PASSED' if ok else 'FAILED'); return ok

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == 'selftest': sys.exit(0 if selftest() else 1)
    if a[0] == 'ibm-index': ibm_index(a[1], a[2] if len(a) > 2 else 'ibm_index.jsonl.gz')
    elif a[0] == 'ibm-counts': print(json.dumps(ibm_counts(a[1]), indent=1))
    elif a[0] == 'ibm-floor': print(json.dumps(floor_table(floors(a[1])), indent=1))
    elif a[0] == 'ibm-read':
        since = a[a.index('--from') + 1] if '--from' in a else None
        print(json.dumps(ibm_read(a[1], since), indent=1, default=str))
    elif a[0] == 'generic':
        spec = json.load(open(a[1])); snaps = []
        for p in sorted(glob.glob(os.path.join(a[2], '*.json*'))):
            d = json.load(gzip.open(p, 'rt') if p.endswith('.gz') else open(p)); snaps.append((d.get('read_at'), d))
        print(json.dumps(generic(spec, snaps), indent=1))
