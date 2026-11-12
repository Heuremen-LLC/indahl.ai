#!/usr/bin/env python3
"""census_tick.py: rows and cells for the CENSUS desk, from PLAN.md (sealed, data/plan_seal.json). First prints and later values come from the cached ALFRED vintages (data/cache/alfred), widths from our own dated EITS copies (data/snapshots). Network: only with --pull (runs census_snap.py and alfred_pull.py first). Default and --offline read files only.
--selftest: rule checks only. One run at a time (lock). Writes data/census.json, summary_census.json, data/known_good_rows.json, data/census_history.jsonl.
This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."""
import os, sys, json, gzip, glob, csv, time, fcntl, subprocess, statistics, datetime
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
ABOVE, BELOW, CONSISTENT, CANNOT_TELL = K.ABOVE, K.BELOW, K.CONSISTENT, K.CANNOT_TELL
_LK = open('.census_tick.lock', 'a')
try: fcntl.flock(_LK, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: sys.exit(0)
CACHE = 'data/cache/alfred'
# series: (name, geography label, alfred id, EITS dataset, EITS category, EITS data type, EITS geo, multiplier)
SPEC = []
for g, suf, eg in (('US', '', 'US'), ('Northeast', 'NE', 'NO'), ('Midwest', 'MW', 'MW'), ('South', 'S', 'SO'), ('West', 'W', 'WE')):
    SPEC.append(('SALES', g, 'HSN1F' + suf, 'ressales', 'ASOLD', 'E_TOTAL', eg, 1.645))
    SPEC.append(('STARTS', g, 'HOUST' + suf, 'resconst', 'ASTARTS', 'E_TOTAL', eg, 1.645))
SPEC += [('COMPLETIONS', 'US', 'COMPUTSA', 'resconst', 'ACOMPLETIONS', 'E_TOTAL', 'US', 1.645), ('PERMITS', 'US', 'PERMIT', 'resconst', 'APERMITS', 'E_TOTAL', 'US', 1.645), ('RETAIL', 'US', 'RSAFS', 'marts', '44X72', 'E_SM', 'US', 1.753)]
STEPS = ('S1', 'S2', 'S3')
def mshift(m, k):
    y, mo = int(m[:4]), int(m[5:7]); t = y * 12 + mo - 1 + k; return '%04d-%02d' % (t // 12, t % 12 + 1)
def outcome(p1, later, half):
    """pure rule: p1 first print, later value, half-width (None = no width). 12 Nov 2026, Faults and Guards 2.0 (PLAN_ADDENDUM_std2.md): an exact read of one published value
    against one stated interval is an interval of zero width (owner decision O1), read with K.read_exact against the band, edges included. Same result as before, now with a reason code."""
    if half is None: return CANNOT_TELL, K.NO_INTERVAL_FORMABLE
    o, r, _d = K.read_exact(later, band=(p1 - half, p1 + half))
    return o, r
NIF = K.NO_INTERVAL_FORMABLE
def annual_vintages(vs, data, thresh=0.0):
    """vintages where any month at least 14 months older than the vintage's newest month changed against the previous vintage (return dict vintage -> max relative change)"""
    out = {}
    for i in range(1, len(vs)):
        a, b = data[vs[i - 1]], data[vs[i]]; n = max(b); mx = 0.0; ch = False
        for m, v in b.items():
            if m <= mshift(n, -14) and m in a and a[m] != v:
                ch = True; mx = max(mx, abs(v - a[m]) / abs(a[m]) if a[m] else 1)
        if ch: out[vs[i]] = mx
    return out
def revision_detail(vs, data, v):
    """how far the months at least 14 months older than the vintage's newest month moved against the previous vintage: number of months, median and max absolute relative change (all such months, changed or not)"""
    i = vs.index(v); a, b = data[vs[i - 1]], data[v]; n = max(b); ch = []
    for m, x in b.items():
        if m <= mshift(n, -14) and m in a and a[m]: ch.append(abs(x - a[m]) / abs(a[m]))
    al = [abs(x - a[m]) / abs(a[m]) for m, x in b.items() if m in a and a[m] and x != a[m]]
    return dict(all_changed=len(al), all_median_changed_pct=100 * statistics.median(al) if al else None, all_max_pct=100 * max(al) if al else None, months=len(ch), changed=sum(1 for c in ch if c > 0), median_pct=100 * statistics.median(ch) if ch else None, median_changed_pct=100 * statistics.median([c for c in ch if c > 0]) if any(c > 0 for c in ch) else None, max_pct=100 * max(ch) if ch else None)
def load_alfred(sid):
    vs = []; data = {}
    for f in sorted(glob.glob('%s/%s_20*.csv' % (CACHE, sid)) + glob.glob('%s/%s_19*.csv' % (CACHE, sid))):
        v = os.path.basename(f)[len(sid) + 1:-4]
        rows = list(csv.reader(open(f)))
        if not rows or rows[0][0] != 'observation_date' or len(rows[0]) != 2 or rows[0][1] != '%s_%s' % (sid, v.replace('-', '')): return None, None, 'format'
        d = {}
        for r in rows[1:]:
            try: d[r[0][:7]] = float(r[1])
            except ValueError: pass
        if d: vs.append(v); data[v] = d
    return vs, data, None
def load_widths():
    """first copy wins: key (dataset, cat, dtype, geo, month) -> (value, fetched date)"""
    W = {}
    for ds in ('ressales', 'resconst', 'marts'):
        for f in sorted(glob.glob('data/snapshots/*_%s_errors.json.gz' % ds)):
            doc = json.load(gzip.open(f)); rows = doc['rows']; h = rows[0]; fd = doc['fetched_utc'][:10]
            ix = {k: h.index(k) for k in ('cell_value', 'data_type_code', 'category_code', 'geo_level_code', 'seasonally_adj', 'time')}
            for r in rows[1:]:
                if r[ix['seasonally_adj']] != 'yes': continue
                try: val = float(r[ix['cell_value']])
                except ValueError: continue
                W.setdefault((ds, r[ix['category_code']], r[ix['data_type_code']], r[ix['geo_level_code']], r[ix['time']]), (val, fd))
    return W
def eits_current():
    out = {}
    for ds in ('ressales', 'resconst', 'marts'):
        fs = sorted(glob.glob('data/snapshots/*_%s_values.json.gz' % ds))
        if not fs: continue
        rows = json.load(gzip.open(fs[-1]))['rows']; h = rows[0]
        for r in rows[1:]:
            if r[h.index('seasonally_adj')] == 'yes' and r[h.index('geo_level_code')] == 'US':
                try: out[(ds, r[h.index('category_code')], r[h.index('data_type_code')], r[h.index('time')])] = float(r[h.index('cell_value')])
                except ValueError: pass
    return out
def day(s): return datetime.date.fromisoformat(s)
def build():
    W = load_widths(); rows = []; meta = {}; fmt_ok = True
    for (name, geo, sid, ds, cat, dt, eg, mult) in SPEC:
        vs, data, err = load_alfred(sid)
        if err or not vs: fmt_ok = False if err else fmt_ok; meta[sid] = dict(error=err or 'no vintages'); continue
        first_v = vs[0]; last_v = vs[-1]
        firstseen = {}
        for v in vs:
            for m in data[v]: firstseen.setdefault(m, v)
        av = annual_vintages(vs, data)
        brk = None
        if name == 'RETAIL':
            big = [v for v, c in av.items() if c > 0.03]; brk = big[0] if big else None
        meta[sid] = dict(vintages=len(vs), first_vintage=first_v, last_vintage=last_v, annual_revision_vintages=sorted(av), retail_break_vintage=brk)
        if name == 'RETAIL': meta[sid]['annual_revision_detail'] = {v: revision_detail(vs, data, v) for v in sorted(av)}
        for m in sorted(firstseen):
            if m in data[first_v]: continue   # first print unknown
            v1 = firstseen[m]; p1 = data[v1][m]
            wv = W.get((ds, cat, dt, eg, m)); basis = None; half = None; rse = None
            if wv:
                rse = wv[0]; half = mult * rse / 100.0 * p1
                basis = 'as printed' if 0 <= (day(wv[1]) - day(v1)).days <= 3 else 'as served 2026'
            for step in STEPS:
                row = dict(series=name, geo=geo, alfred=sid, month=m, step=step, first_vintage=v1, first=p1, rse=rse, half=half, width_basis=basis, outcome=None, reason=None)
                tv = last_v if step == 'S3' else firstseen.get(mshift(m, 1 if step == 'S1' else 2))
                if tv is None or m not in data.get(tv, {}) or (step == 'S3' and tv <= v1):
                    row.update(outcome=CANNOT_TELL, reason=NIF, reason_detail='missing vintage'); rows.append(row); continue
                later = data[tv][m]; row.update(target_vintage=tv, later=later)
                if half is not None:
                    # 11 Nov, after the data, after the outside referee (CHECKS.md R-1 to R-5): extra readings computed here, none changes a rule or an outcome
                    row['out_all'] = outcome(p1, later, half)[0]            # the outcome if no exclusion applied (annual revision or break rows counted in)
                    row['same_release'] = step != 'S3' and tv == v1          # the later print came in the same release as the first print
                if half is None: row.update(outcome=CANNOT_TELL, reason=NIF, reason_detail='no width')
                elif brk and v1 < brk <= tv: row.update(outcome=CANNOT_TELL, reason=NIF, reason_detail='universe break')
                elif step != 'S3' and any(v1 < a <= tv for a in av): row.update(outcome=CANNOT_TELL, reason=NIF, reason_detail='annual revision in window')
                else:
                    o, r = outcome(p1, later, half); row.update(outcome=o, reason=r)
                    row['miss_in_half_widths'] = (later - p1) / half if half else None
                    for tag, d in (('dn', -0.5), ('up', 0.5)):
                        h2 = mult * max(rse + d * (0.1 if mult == 1.753 else 1), 0) / 100.0 * p1; row['out_' + tag] = outcome(p1, later, h2)[0]
                row['rel_rev'] = (later - p1) / p1 if p1 else None
                rows.append(row)
    return rows, meta, fmt_ok
def cells(rows):
    out = []; keys = sorted(set((r['series'], r['geo'], r['step'], r['width_basis'] or 'none') for r in rows), key=lambda k: (['SALES', 'STARTS', 'COMPLETIONS', 'RETAIL', 'PERMITS'].index(k[0]), ['US', 'Northeast', 'Midwest', 'South', 'West'].index(k[1]), k[2], k[3]))
    for (s, g, st, b) in keys:
        rs = [r for r in rows if (r['series'], r['geo'], r['step'], r['width_basis'] or 'none') == (s, g, st, b)]
        c = {o: sum(1 for r in rs if r['outcome'] == o) for o in (CONSISTENT, ABOVE, BELOW)}
        n = sum(c.values()); lo, hi = K.wilson(c[CONSISTENT], n)
        why = {}
        for r in rs:
            if r['outcome'] == CANNOT_TELL: why[r.get('reason_detail') or r['reason']] = why.get(r.get('reason_detail') or r['reason'], 0) + 1
        # 12 Nov 2026, PLAN_ADDENDUM_std2.md: 0.90 is a point figure with no tolerance, so only ABOVE, BELOW or CANNOT_TELL. Under ten scored rows is TOO_WIDE_TO_RESOLVE (owner decision O3), no scored row is NO_INTERVAL_FORMABLE.
        if n == 0: oc, ocr = CANNOT_TELL, K.NO_INTERVAL_FORMABLE
        elif n < 10: oc, ocr = CANNOT_TELL, K.TOO_WIDE_TO_RESOLVE
        else: oc, ocr = K.read(lo, hi, bound=0.90)
        r13 = K.req13([(r['outcome'], r.get('reason')) for r in rs], nothing_returned=0)
        sc = [r for r in rs if r['outcome'] in (CONSISTENT, ABOVE, BELOW)]
        rv = [abs(r['rel_rev']) for r in sc if r.get('rel_rev') is not None]; mh = [abs(r['miss_in_half_widths']) for r in sc if r.get('miss_in_half_widths') is not None]
        sens = {}
        for tag in ('dn', 'up'):
            k2 = sum(1 for r in sc if r.get('out_' + tag) == CONSISTENT); n2 = sum(1 for r in sc if r.get('out_' + tag) in (CONSISTENT, ABOVE, BELOW)); sens[tag] = (k2 / n2) if n2 else None
        ai = [r for r in rs if r.get('out_all')]; ni = len(ai); ki = sum(1 for r in ai if r['out_all'] == CONSISTENT); li, hi_ = K.wilson(ki, ni)
        sr = [r for r in sc if r.get('same_release')]; ssr = [r for r in sc if not r.get('same_release')]; ks = sum(1 for r in ssr if r['outcome'] == CONSISTENT); ls, hs_ = K.wilson(ks, len(ssr))
        sc_half = sum(1 for x in mh if x <= 0.5); sc_23 = sum(1 for x in mh if x <= 2 / 3)   # share inside if every stated half-width were cut to half, or to two thirds (display only)
        p90 = statistics.quantiles(mh, n=10, method='inclusive')[8] if len(mh) >= 10 else None
        out.append(dict(series=s, geo=g, step=st, width_basis=b, rows=len(rs), scored=n, inside=c[CONSISTENT], above=c[ABOVE], below=c[BELOW], share=(c[CONSISTENT] / n) if n else None, lo=lo, hi=hi,
                        outcome=oc, reason=ocr, req13=r13, cannot_tell=sum(why.values()), cannot_tell_why=why, median_abs_rev_pct=(100 * statistics.median(rv)) if rv else None, median_abs_miss_half_widths=statistics.median(mh) if mh else None,
                        share_rse_minus_half=sens['dn'], share_rse_plus_half=sens['up'],
                        p90_abs_miss_half_widths=p90, max_abs_miss_half_widths=max(mh) if mh else None, at_half_width=dict(inside=sc_half, scored=len(mh)), at_two_thirds_width=dict(inside=sc_23, scored=len(mh)),
                        counted_in=dict(scored=ni, inside=ki, share=(ki / ni) if ni else None, lo=li, hi=hi_), same_release_rows=len(sr), without_same_release=dict(scored=len(ssr), inside=ks, lo=ls, hi=hs_) , first_month=min(r['month'] for r in rs), last_month=max(r['month'] for r in rs)))
    return out
def rule_selftest():
    ok = True; t = []
    def chk(n, c):
        nonlocal ok; ok &= bool(c); t.append(('ok ' if c else 'FAIL ') + n)
    chk('inside', outcome(100, 105, 10)[0] == CONSISTENT); chk('edge inside', outcome(100, 110, 10)[0] == CONSISTENT)
    chk('above', outcome(100, 111, 10)[0] == ABOVE); chk('below', outcome(100, 89, 10)[0] == BELOW); chk('no width', outcome(100, 101, None) == (CANNOT_TELL, K.NO_INTERVAL_FORMABLE))
    chk('mshift', mshift('2025-12', 1) == '2026-01' and mshift('2026-01', -14) == '2024-11')
    d = {'a': {'2020-01': 1.0, '2021-06': 2.0}, 'b': {'2020-01': 1.5, '2021-06': 2.0, '2021-07': 3.0}}
    chk('annual vintage found', list(annual_vintages(['a', 'b'], d)) == ['b'])
    d = {'a': {'2020-01': 1.0, '2021-06': 2.0}, 'b': {'2020-01': 1.0, '2021-06': 2.5, '2021-07': 3.0}}
    chk('recent revision is not annual', annual_vintages(['a', 'b'], d) == {})
    return ok, ' '.join(t)
if '--selftest' in sys.argv:
    ok, t = rule_selftest(); print(t); print('rule selftest', 'PASSED' if ok else 'FAILED'); sys.exit(0 if ok and K.selftest() else 1)
PUB = '--publish' in sys.argv
if '--pull' in sys.argv:
    subprocess.run([sys.executable, 'census_snap.py']); subprocess.run([sys.executable, 'alfred_pull.py', '--refresh-vintages'])
# plan seal must exist and match
seal = json.load(open('data/plan_seal.json'))
plan_ok = (K.plan_committed('PLAN.md') if hasattr(K, 'plan_committed') else True) and seal['plan_sha256'] == __import__('hashlib').sha256(open('PLAN.md', 'rb').read()).hexdigest()
now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
DRY = '--dry' in sys.argv
if not seal.get('first_comparison') and plan_ok and not DRY:
    seal['first_comparison'] = now; json.dump(seal, open('data/plan_seal.json', 'w'), indent=1)
rows, meta, fmt_ok = build()
# gates
kg = {}
kg['format'] = fmt_ok and bool(rows)
cur = eits_current(); hits = tot = 0; detail = []
for (name, geo, sid, ds, cat, dt, eg, mult) in SPEC:
    if geo != 'US': continue
    vs, data, err = load_alfred(sid)
    if not vs: continue
    dt_ = dt.replace('E_', ''); newest = data[vs[-1]]
    for m in sorted(newest)[-12:]:
        e = cur.get((ds, cat, 'SM' if ds == 'marts' else dt_, m))
        if e is None: continue
        tot += 1; ok = abs(e - newest[m]) <= 0.005 * abs(e) + 0.5; hits += ok
        if not ok: detail.append('%s %s alfred %s eits %s' % (sid, m, newest[m], e))
kg['join'] = tot >= 10 and hits / tot >= 0.90; kg['join_detail'] = dict(compared=tot, equal=hits, mismatches=detail[:12])
# reader: values read by hand from the Census release texts (CHECKS.md)
HAND = [('HSN1F', '2026-10-27', '2026-09', 676), ('HSN1F', '2026-10-27', '2026-08', 680), ('HSN1F', '2026-10-27', '2025-09', 714),
        ('HOUST', '2026-10-20', '2026-09', 1221), ('HOUST', '2026-10-20', '2026-08', 1288), ('HOUST', '2026-10-20', '2025-09', 1319), ('COMPUTSA', '2026-10-20', '2026-09', 1192), ('COMPUTSA', '2026-10-20', '2026-08', 1166),
        ('PERMIT', '2026-10-20', '2026-09', 1400), ('PERMIT', '2026-10-20', '2026-08', 1403)]
hand_res = []
for sid, v, m, want in HAND:
    vs, data, err = load_alfred(sid); got = (data or {}).get(v, {}).get(m) if vs else None
    hand_res.append(dict(series=sid, vintage=v, month=m, release_text=want, parsed=got, equal=got is not None and abs(got - want) < 0.5))
kg['reader'] = all(h['equal'] for h in hand_res); kg['reader_detail'] = hand_res
kg['rule'] = rule_selftest()[0] and K.selftest()
passed = kg['format'] and kg['join'] and kg['reader'] and kg['rule'] and plan_ok
if not passed:
    for r in rows:
        if r['outcome'] in (CONSISTENT, ABOVE, BELOW): r['outcome_before_gate'] = r['outcome']; r['outcome'] = CANNOT_TELL; r['reason'] = NIF; r['reason_detail'] = 'gate failed'
C = cells(rows)
S = dict(generated=now, plan_seal=seal, plan_matches_file=plan_ok, gates=dict(passed=passed, **kg), series_meta=meta, cells=C,
         rows=dict(total=len(rows), first_month=min(r['month'] for r in rows), last_month=max(r['month'] for r in rows), first_vintage=min(r['first_vintage'] for r in rows)),
         snapshots=dict(files=len(glob.glob('data/snapshots/*.json.gz')), earliest=min(os.path.basename(f)[:16] for f in glob.glob('data/snapshots/*.json.gz')), as_printed_rows=sum(1 for r in rows if r['width_basis'] == 'as printed')),
         same_release_months={sid: sorted({r['month'] for r in rows if r['alfred'] == sid and r['step'] == 'S1' and r.get('same_release')}) for sid in ('HSN1F', 'HOUST', 'COMPUTSA', 'RSAFS')},
         after_data_note='12 Nov 2026: outcome rule moved to Faults and Guards 2.0 (PLAN_ADDENDUM_std2.md), cell CONSISTENT removed for the point figure 0.90, reason codes and REQ-13 added, no data or row rule changed. 11 Nov 2026 after the outside referee: p90 miss, shares at half and two thirds of the width, rows counted in with annual revisions, same-release rows, revision detail for the retail vintages. See CHECKS.md R-1 to R-5. No rule, cell or outcome changed on 11 Nov.', headline_req13=K.req13([(r['outcome'], r.get('reason')) for r in rows if r['series'] in ('SALES', 'STARTS', 'COMPLETIONS', 'RETAIL') and r['geo'] == 'US' and r['step'] == 'S1'], nothing_returned=0))
json.dump(rows, open('data/census.json', 'w'), separators=(',', ':'))
json.dump(S, open('summary_census.json', 'w'), indent=1)
json.dump([r for r in rows if r['alfred'] in ('HOUST', 'HSN1F') and r['step'] == 'S1' and r['month'] in ('2024-12', '2025-03', '2025-06', '2026-06')], open('data/known_good_rows.json', 'w'), indent=1)
live = dict(S, updated=now)
if not DRY:
    json.dump(live, open('data/census_live.json.tmp', 'w'), separators=(',', ':')); os.replace('data/census_live.json.tmp', 'data/census_live.json')
if PUB and not DRY:
    # 11 Nov: the feed /census/live.json (KV census_live, the same namespace as the other desk feeds). Only the schedulers and --publish put it.
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'census_live', '--path', os.path.join(H, 'data', 'census_live.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                       cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
    print('census_live', 'published' if p.returncode == 0 else 'publish FAILED ' + (p.stderr or '')[-200:])
if not DRY: open('data/census_history.jsonl', 'a').write(json.dumps(dict(t=now, rows=len(rows), gate=passed)) + '\n')
print('gates', passed, {k: v for k, v in kg.items() if not k.endswith('detail')}); print('rows', len(rows), 'cells', len(C))
