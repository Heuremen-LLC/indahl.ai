#!/usr/bin/env python3
"""water_tick.py: WATER rider (see PLAN.md). Rerunnable. Installs no timer. Reads public sources with no key:
Reclamation HDB (observed and 24-Month Study model runs), RISE (24-Month Study catalog and report files), Reclamation Lower Colorado daily report,
USGS Water Services, California CDEC. Scores every 24-Month Study projection of Lake Mead and Lake Powell against the measured end-of-month
elevation, keeps a live panel, snapshots USGS provisional values. Writes data/water.json, summary_water.json and data/water_live.json.
--offline: use cached files only. --publish: also put water_live into the site KV (off by default)."""
import os, sys, json, time, math, re, html, calendar, hashlib, statistics, subprocess, urllib.request, urllib.parse, datetime as D, collections as C
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import water_24ms as W, heuremen_kit as K
OFF = '--offline' in sys.argv; PUB = '--publish' in sys.argv
for d in ('data', 'data/raw', 'data/raw/24ms', 'data/cache', 'data/cache/parsed', 'data/cache/hdb_model'): os.makedirs(d, exist_ok=True)
NOW = time.time(); TODAY = time.strftime('%Y-%m-%d', time.gmtime(NOW)); UA = W.UA
def log(*a): print('water:', *a, file=sys.stderr)
def get_text(url, tries=3):
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=120) as r: return r.read().decode('utf-8', 'replace')
        except Exception as e:
            err = e; time.sleep(3 * (a + 1))
    raise RuntimeError('fetch failed %s: %r' % (url, err))
STALE = []
def cached(name, fn):
    """Fetch with fn() and keep a copy in data/raw, or read the copy when offline or when the fetch fails. A failed fetch is named in the feed."""
    f = os.path.join('data/raw', name)
    if not OFF:
        try:
            v = fn(); json.dump(v, open(f + '.tmp', 'w')); os.replace(f + '.tmp', f); return v, True
        except Exception as e: log('fetch FAILED, using last copy', name, repr(e)[:160]); STALE.append(name)
    return (json.load(open(f)), False) if os.path.exists(f) else (None, False)
def mshift(mo, k):
    y, m = int(mo[:4]), int(mo[5:]) + k; y += (m - 1) // 12; m = (m - 1) % 12 + 1; return '%04d-%02d' % (y, m)
def mdiff(a, b): return (int(a[:4]) - int(b[:4])) * 12 + int(a[5:]) - int(b[5:])
def wyear(mo): return int(mo[:4]) + (1 if int(mo[5:]) >= 10 else 0)
def r2(x): return None if x is None else round(x, 2)
def pct(xs, q):
    if not xs: return None
    s = sorted(xs); i = (len(s) - 1) * q; lo = math.floor(i); hi = math.ceil(i); return s[lo] + (s[hi] - s[lo]) * (i - lo)

# ---------------- 1. stated side: 24-Month Study reports ----------------
reports = W.catalog(refresh=not OFF)
reports = [r for r in reports if r.get('parsed')]
for r in reports:
    f = os.path.join('data/raw/24ms', r['file'])
    if not os.path.exists(f) and not OFF:
        try:
            with urllib.request.urlopen(urllib.request.Request(r['url'], headers={'User-Agent': UA}), timeout=300) as x: b = x.read()
            open(f + '.part', 'wb').write(b); os.replace(f + '.part', f); log('new report', r['file'])
        except Exception as e: log('report download failed', r['file'], repr(e)[:120])
def parsed(r):
    f = os.path.join('data/raw/24ms', r['file']); c = os.path.join('data/cache/parsed', r['file'] + '.json')
    if not os.path.exists(f): return None
    sz = os.path.getsize(f)
    if os.path.exists(c):
        v = json.load(open(c))
        if v.get('size') == sz and v.get('parser') == PARSER: return v
    try: v = W.read_text(f)
    except Exception as e: v = {'error': repr(e)[:200], 'mrids': [], 'pages': {}, 'mead': {}, 'powell': {}}
    v['size'] = sz; v['parser'] = PARSER; v['sha256'] = hashlib.sha256(open(f, 'rb').read()).hexdigest(); json.dump(v, open(c, 'w')); return v
PARSER = hashlib.sha256(open(os.path.join(H, 'water_24ms.py'), 'rb').read()).hexdigest()[:12]
def model(key, mrid, t1, t2):
    c = os.path.join('data/cache/hdb_model', '%s_%s.json' % (key, mrid))
    if os.path.exists(c): return json.load(open(c))
    if OFF: return {'_error': 'offline'}
    try: v = W.hdb_model(key, mrid, t1 + '-01T00:00', t2 + '-01T00:00')
    except Exception as e: return {'_error': repr(e)[:160]}
    json.dump(v, open(c, 'w')); return v
stated = {}   # (report id, reservoir) -> {target: value or None}
meta = {}     # report id -> facts about how it was read
for r in reports:
    p = parsed(r); m = dict(file=r['file'], title=r['title'], mrid=None, read={}, hdb_check={})
    if p is None: meta[r['id']] = dict(m, missing=True); continue
    m['mrid'] = p['mrids'][0] if p.get('mrids') else None
    for key in ('mead', 'powell'):
        tv = W.pick(p, key)
        if not tv: stated[(r['id'], key)] = {}; m['read'][key] = 'no table'; continue
        src = 'text'; vals = dict(tv)
        if m['mrid']:
            ms = sorted(tv); hv = model(key, m['mrid'], ms[0], ms[-1])
            if '_error' not in hv:
                both = [mo for mo in ms if tv[mo] is not None and mo in hv]
                agree = [mo for mo in both if abs(tv[mo] - hv[mo]) <= 0.0151]   # Addendum 1: print rounds to 0.01 ft, HDB stores unrounded values
                share = len(agree) / len(both) if both else 0.0
                m['hdb_check'][key] = dict(both=len(both), agree=len(agree), share=round(share, 3), differ=len(both) - len(agree),
                                           first_disagree=[(mo, tv[mo], r2(hv[mo])) for mo in both if mo not in agree][:4])
                if both and share >= 0.60:   # Addendum 1: a run that agrees on at least 60 percent of months is the printed run, read clean from HDB
                    src = 'hdb'; vals = {mo: (round(hv[mo], 2) if mo in hv else tv[mo]) for mo in ms}
            else: m['hdb_check'][key] = dict(error=hv['_error'])
        stated[(r['id'], key)] = vals; m['read'][key] = src
    meta[r['id']] = m

# ---------------- 2. measured side ----------------
obs, fresh_obs = cached('hdb_observed_monthly.json', lambda: {k: W.hdb_series(k, table='R', tstp='MN', t1='1935-01-01T00:00') for k in ('mead', 'powell')})
daily, _ = cached('hdb_observed_daily.json', lambda: {k: W.hdb_series(k, table='R', tstp='DY', t1='1999-12-01T00:00') for k in ('mead', 'powell')})
hourly, _ = cached('hdb_observed_hourly.json', lambda: {k: W.hdb_series(k, table='R', tstp='HR', t1=time.strftime('%Y-%m-%dT00:00', time.gmtime(NOW - 40 * 86400))) for k in ('mead', 'powell')})
# the last month is complete only once its last day has a daily reading
def complete(key, mo):
    y, m = int(mo[:4]), int(mo[5:]); ld = '%04d-%02d-%02d' % (y, m, calendar.monthrange(y, m)[1]); return ld in (daily or {}).get(key, {})
measured = {k: {mo: v for mo, v in (obs or {}).get(k, {}).items() if mo < TODAY[:7] or complete(k, mo)} for k in ('mead', 'powell')}

# ---------------- 3. known-good gates (PLAN.md) ----------------
KG1 = ['SEP26_7_508.pdf', 'APR11_508.pdf', 'JUL04_508.pdf']
KG2 = {'JAN05_508.pdf': {'mead': {'2005-01': 1134.83, '2005-02': 1137.47, '2005-03': 1135.76}, 'powell': {'2005-01': 3559.61, '2005-02': 3555.45, '2005-03': 3552.15}},
       'JAN15_MIN_508.pdf': {'mead': {'2014-11': 1083.57, '2015-01': 1088.93, '2016-04': 1068.35}, 'powell': {}},
       'AUG09_MIN_508.pdf': {'mead': {'2009-08': 1094.73, '2009-12': 1097.51, '2010-06': 1080.05}, 'powell': {'2009-08': 3639.93, '2009-12': 3632.17, '2010-06': 3626.60}}}   # read directly from the page text, 9-10 Nov 2026
KG3 = ['2010-06', '2018-12', '2025-09']
kg = {}
byfile = {r['file']: r for r in reports}
ok1 = []
for f in KG1:
    r = byfile.get(f); m = meta.get(r['id']) if r else None
    ok1.append(bool(m and all(m['hdb_check'].get(k, {}).get('both', 0) > 0 and m['hdb_check'][k].get('differ', 1) == 0 for k in ('mead', 'powell'))))   # strict: every month agrees
kg['hdb_model_read'] = all(ok1)
ok2 = []
for f, want in KG2.items():
    r = byfile.get(f); p = parsed(r) if r else None
    for key, mv in want.items():
        tv = W.pick(p, key) if p else {}
        for mo, v in mv.items(): ok2.append(tv.get(mo) is not None and abs(tv[mo] - v) <= 0.0051)
kg['text_read'] = bool(ok2) and all(ok2)
ok3 = []
lc_eom = json.load(open('data/raw/lc_mead_eom_table.json')) if os.path.exists('data/raw/lc_mead_eom_table.json') else {}
for mo in KG3:
    y, m = int(mo[:4]), int(mo[5:]); ld = '%04d-%02d-%02d' % (y, m, calendar.monthrange(y, m)[1])
    for key in ('mead', 'powell'):
        a = (obs or {}).get(key, {}).get(mo); b = (daily or {}).get(key, {}).get(ld); ok3.append(a is not None and b is not None and abs(a - b) <= 0.0051)
    if lc_eom: ok3.append(abs(lc_eom.get(mo, -1e9) - (obs or {}).get('mead', {}).get(mo, 1e9)) <= 0.0051)
kg['measured_read'] = bool(ok3) and all(ok3)
GATE = all(kg.values())

# ---------------- 4. rows ----------------
by_issue = C.defaultdict(dict)   # issue -> scenario/variant -> report
dups = []
for r in reports:
    k = r['scenario'] + ('_' + r['variant'] if r['variant'] else '')
    if k in by_issue[r['issue']]:
        a = by_issue[r['issue']][k]; keep, drop = (r, a) if (r['published'] or '') > (a['published'] or '') else (a, r); by_issue[r['issue']][k] = keep; dups.append(drop['title'])
    else: by_issue[r['issue']][k] = r
def mp_for_cells(sc):
    if 'MP' in sc: return sc['MP']
    return sc.get('MP_7maf') or sc.get('MP_6maf')
rows = []; vrows = []
for issue, sc in sorted(by_issue.items()):
    mp = mp_for_cells(sc); mn = sc.get('MIN'); mx = sc.get('MAX')
    for key in ('mead', 'powell'):
        mpv = stated.get((mp['id'], key), {}) if mp else {}
        mnv = stated.get((mn['id'], key), {}) if mn else {}
        mxv = stated.get((mx['id'], key), {}) if mx else {}
        targets = sorted(set(mpv) | set(mnv) | set(mxv))
        for t in targets:
            L = mdiff(t, issue)
            if L < 0: continue
            o = measured[key].get(t); a = mnv.get(t); b = mxv.get(t); v = mpv.get(t)
            row = dict(issue=issue, res=key, target=t, lead=L, wy=wyear(t), mp=r2(v), mp_src=(meta[mp['id']]['read'].get(key) if mp else None),
                       mp_report=(mp['title'] if mp else None), pmin=r2(a), pmax=r2(b), measured=r2(o))
            if mn and mx and a is not None and b is not None:
                lo, hi = min(a, b), max(a, b); row.update(band_lo=r2(lo), band_hi=r2(hi), inverted=a > b, mp_outside=(v is not None and not (lo - 0.005 <= v <= hi + 0.005)))
            if o is None: row['outcome'] = None; row['read_status'] = K.NOTHING_RETURNED; row['why'] = 'no measured value for this month yet'   # a failed read, no outcome (PLAN_ADDENDUM_std2.md)
            elif 'band_lo' not in row:
                row['outcome'] = K.CANNOT_TELL; row['reason'] = K.NO_INTERVAL_FORMABLE
                row['why'] = 'no Probable Minimum and Maximum issued this month' if not (mn and mx) else 'band edge unreadable for this month'
            else:   # a measured value against the stated band with the plan's 0.005 ft tolerance: an exact read, an interval of zero width (owner decision O1), closed edges
                row['outcome'], row['reason'], _ = K.read_exact(o, band=(row['band_lo'] - 0.005, row['band_hi'] + 0.005), edge='closed')
            if v is not None and o is not None:
                e = o - v; row['mp_error'] = r2(e); row['mp_sign'] = 'above' if e > 0.005 else ('below' if e < -0.005 else 'equal')
            elif v is None and mp and t in mpv: row['mp_why'] = 'Most Probable value unreadable'
            rows.append(row)
    for vk in ('MP_6maf',) if ('MP_6maf' in sc and 'MP_7maf' in sc) else ():
        r = sc[vk]
        for key in ('mead', 'powell'):
            for t, v in sorted(stated.get((r['id'], key), {}).items()):
                L = mdiff(t, issue)
                if L < 0: continue
                o = measured[key].get(t); vr = dict(issue=issue, res=key, target=t, lead=L, variant='6 maf Lake Powell release', mp=r2(v), measured=r2(o), report=r['title'])
                if v is not None and o is not None: vr['mp_error'] = r2(o - v); vr['mp_sign'] = 'above' if o - v > 0.005 else ('below' if o - v < -0.005 else 'equal')
                vrows.append(vr)
_gated = iter(K.apply_gate(GATE, [r for r in rows if not r.get('read_status')]))
rows = [r if r.get('read_status') else dict(next(_gated), **({} if GATE else {'reason': K.NO_INTERVAL_FORMABLE})) for r in rows]   # a row with no measurement yet has no outcome to gate. A gate failure is NO_INTERVAL_FORMABLE

# ---------------- 5. cells ----------------
def verdict_r(lo, hi, claim, band, neff):
    """Returns (outcome, reason). PLAN.md names two rules for a cell: ABOVE and BELOW against the claim (0.80 or 0.50), CONSISTENT if the whole interval is inside the band.
    PLAN_ADDENDUM_std2.md reads them as two K.read steps with closed edges. No water years is NO_INTERVAL_FORMABLE, under 10 water years is TOO_WIDE_TO_RESOLVE (owner decision O3).
    No size that matters is named, so no both-alternatives test."""
    if neff == 0: return K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE
    if neff < 10: return K.CANNOT_TELL, K.TOO_WIDE_TO_RESOLVE
    o, r = K.read(lo, hi, bound=claim, edge='closed')
    if o in (K.ABOVE, K.BELOW): return o, None
    return K.read(lo, hi, band=band, edge='closed')
def verdict(lo, hi, claim, band, neff): return verdict_r(lo, hi, claim, band, neff)[0]
GATED = (K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE)
def oc(r): return r.get('outcome_before_gate') or r['outcome']
def rulers(rs, k, claim, band):
    """Addendum 2, checks added after the data and never used for the outcome: the same count read on three other rulers.
    rows_as_independent: Wilson on rows. kish_weighted_water_years: water years weighted by their row count, n = (sum m)^2 / sum m^2.
    two_water_year_blocks: neighbouring water years paired (2000-2001, 2002-2003, ...)."""
    n = len(rs)
    if not n: return {}
    out = {}; sh = k / n
    by = C.Counter(r['wy'] for r in rs); nk = sum(by.values()) ** 2 / sum(m * m for m in by.values()); nb = len(set(r['wy'] // 2 for r in rs))
    for name, ne in (('rows_as_independent', n), ('kish_weighted_water_years', nk), ('two_water_year_blocks', nb)):
        ke = k if name == 'rows_as_independent' else round(ne * sh)   # the plan's convention: the effective count of successes is rounded
        lo, hi = K.wilson(ke, ne); lo2, hi2 = K.wilson(ne * sh, ne)   # and the same ruler without rounding, since cells near a bound can flip on it
        v1 = verdict_r(lo, hi, claim, band, ne) if GATE else GATED; v2 = verdict_r(lo2, hi2, claim, band, ne) if GATE else GATED
        out[name] = dict(n=round(ne, 1), k=round(ke, 1), lo=round(lo, 3), hi=round(hi, 3), outcome=v1[0], reason=v1[1],
                         lo_unrounded=round(lo2, 3), hi_unrounded=round(hi2, 3), outcome_unrounded=v2[0], reason_unrounded=v2[1])
    return out
def lag1(rs, ok):
    """Addendum 2, after the data: correlation of the per-water-year share between neighbouring water years."""
    by = C.defaultdict(list)
    for r in rs: by[r['wy']].append(1.0 if ok(r) else 0.0)
    sh = {w: sum(v) / len(v) for w, v in by.items()}; pairs = [(sh[w], sh[w + 1]) for w in sh if w + 1 in sh]
    if len(pairs) < 5: return None
    xs, ys = zip(*pairs); mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return None if sx == 0 or sy == 0 else round(sum((x - mx) * (y - my) for x, y in pairs) / (sx * sy), 2)
s80 = json.load(open('data/scan80.json')) if os.path.exists('data/scan80.json') else {}
SENT = {}   # issue month -> both band reports carry the 80 percent sentence (Addendum 2)
for f, v in s80.items():
    if v['scenario'] in ('MIN', 'MAX'): SENT.setdefault(v['issue'], {})[v['scenario']] = bool(v['hit'])
SENT = {k for k, d in SENT.items() if d.get('MIN') and d.get('MAX')}
cells = []; sent_cells = []
for key in ('mead', 'powell'):
    for L in range(24):
        rs = [r for r in rows if r['res'] == key and r['lead'] == L]
        b = [r for r in rs if r.get('band_lo') is not None and r['measured'] is not None]
        k = sum(1 for r in b if oc(r) == K.CONSISTENT)
        ab = sum(1 for r in b if oc(r) == K.ABOVE); be = sum(1 for r in b if oc(r) == K.BELOW)
        neff = len(set(r['wy'] for r in b)); keff = round(neff * k / len(b)) if b else 0; lo, hi = K.wilson(keff, neff)
        bo, bor = verdict_r(lo, hi, 0.80, (0.70, 0.90), neff) if GATE else GATED
        m = [r for r in rs if r.get('mp_error') is not None]
        s = [r for r in m if r['mp_sign'] != 'equal']; km = sum(1 for r in s if r['mp_sign'] == 'above')
        neff2 = len(set(r['wy'] for r in s)); keff2 = round(neff2 * km / len(s)) if s else 0; lo2, hi2 = K.wilson(keff2, neff2)
        mo_, mor = verdict_r(lo2, hi2, 0.50, (0.40, 0.60), neff2) if GATE else GATED
        errs = [r['mp_error'] for r in m]
        widths = [r['band_hi'] - r['band_lo'] for r in b]   # defined after the data: how wide the stated band was, as context for the share inside
        cells.append(dict(res=key, lead=L, band=dict(n=len(b), inside=k, above=ab, below=be, share=r2(k / len(b)) if b else None, n_wy=neff, k_wy=keff, lo=round(lo, 3), hi=round(hi, 3), outcome=bo, reason=bor,
  req13=K.req13([dict(outcome=r['outcome'], reason=r.get('reason')) for r in rs if r.get('outcome')], nothing_returned=sum(1 for r in rs if r.get('read_status'))),
                                                     median_width_ft=r2(statistics.median(widths)) if widths else None, zero_width=sum(1 for w in widths if w <= 0.005),
                                                     inverted=sum(1 for r in b if r.get('inverted')), wy_lag1_corr=lag1(b, lambda r: oc(r) == K.CONSISTENT),
                                                     checks_after_data=rulers(b, k, 0.80, (0.70, 0.90))),
                          mp=dict(n=len(s), above=km, below=len(s) - km, ties=len(m) - len(s), share_above=r2(km / len(s)) if s else None, n_wy=neff2, k_wy=keff2, lo=round(lo2, 3), hi=round(hi2, 3), outcome=mo_, reason=mor,
                                  req13=K.req13([dict(outcome=K.ABOVE if r['mp_sign'] == 'above' else K.BELOW) for r in s], nothing_returned=sum(1 for r in rs if r.get('read_status') and r.get('mp') is not None)),
                                  median_error=r2(statistics.median(errs)) if errs else None, median_abs_error=r2(statistics.median([abs(e) for e in errs])) if errs else None,
                                  p10=r2(pct(errs, 0.10)), p90=r2(pct(errs, 0.90)), checks_after_data=rulers(s, km, 0.50, (0.40, 0.60)))))
        bs = [r for r in b if r['issue'] in SENT]; ks = sum(1 for r in bs if oc(r) == K.CONSISTENT)   # Addendum 2, after the data: only months whose two band reports print the 80 percent sentence
        ns = len(set(r['wy'] for r in bs)); kse = round(ns * ks / len(bs)) if bs else 0; los, his = K.wilson(kse, ns)
        sent_cells.append(dict(res=key, lead=L, n=len(bs), inside=ks, above=sum(1 for r in bs if oc(r) == K.ABOVE), below=sum(1 for r in bs if oc(r) == K.BELOW), n_wy=ns, lo=round(los, 3), hi=round(his, 3),
                               outcome=(verdict_r(los, his, 0.80, (0.70, 0.90), ns) if GATE else GATED)[0], reason=(verdict_r(los, his, 0.80, (0.70, 0.90), ns) if GATE else GATED)[1]))
def runs(leads):
    out = []; st = None
    for x in sorted(leads):
        if st is None: st = pv = x
        elif x == pv + 1: pv = x
        else: out.append((st, pv)); st = pv = x
    if st is not None: out.append((st, pv))
    return ', '.join(str(a) if a == b2 else '%d to %d' % (a, b2) for a, b2 in out)
flagged = []
for key in ('mead', 'powell'):
    for t in ('band', 'mp'):
        for o in (K.ABOVE, K.BELOW):
            ls = [c['lead'] for c in cells if c['res'] == key and c[t]['outcome'] == o]
            if ls: flagged.append(dict(res=key, test=t, outcome=o, n=len(ls), leads=runs(ls)))
flags = sum(f['n'] for f in flagged)

# ---------------- 6. live panel ----------------
def lastn(d, n): ks = sorted(d); return [(k, d[k]) for k in ks[-n:]]
def change(dd, days):
    ks = sorted(dd)
    if not ks: return None
    last = ks[-1]; t0 = (D.date.fromisoformat(last) - D.timedelta(days=days)).isoformat()
    return r2(dd[last] - dd[t0]) if t0 in dd else None
def rises(dd, window=60):
    ks = sorted(dd); end = D.date.fromisoformat(ks[-1]); st = (end - D.timedelta(days=window)).isoformat(); out = {}
    for k in (1, 2, 7):
        best = None
        for d0 in ks:
            if d0 < st: continue
            d1 = (D.date.fromisoformat(d0) + D.timedelta(days=k)).isoformat()
            if d1 in dd:
                r = dd[d1] - dd[d0]
                if best is None or r > best[0]: best = (r, d0, d1)
        out['%d' % k] = None if best is None else dict(rise_ft=r2(best[0]), start=best[1], end=best[2])
    return out
live = {}
for key in ('mead', 'powell'):
    dd = (daily or {}).get(key, {}); hh = (hourly or {}).get(key, {})
    if not dd: live[key] = None; continue
    lk = sorted(dd)[-1]; hk = sorted(hh)[-1] if hh else None
    lowk = min(dd, key=lambda k: dd[k]); low_since = dict(date=lowk, ft=r2(dd[lowk]))
    live[key] = dict(name=W.RES[key]['name'], daily_date=lk, daily_ft=r2(dd[lk]), hourly_time=hk, hourly_ft=r2(hh[hk]) if hk else None,
                     change_1d=change(dd, 1), change_7d=change(dd, 7), change_30d=change(dd, 30), largest_rise_60d=rises(dd), lowest_daily_since_dec_1999=low_since,
                     source='Reclamation HDB, sdi %d (%s), daily end-of-day and hourly readings, Mountain Standard Time' % (W.RES[key]['sdi'], W.RES[key]['svr']))
usgs_p, _ = cached('usgs_09379900_iv_latest.json', lambda: json.loads(get_text('https://waterservices.usgs.gov/nwis/iv/?format=json&sites=09379900&parameterCd=62614&period=P2D')))
try:
    v = usgs_p['value']['timeSeries'][0]['values'][0]['value'][-1]; live['powell_usgs'] = dict(time=v['dateTime'], ft=float(v['value']), qualifiers=v['qualifiers'], datum='NGVD 1929', site='USGS 09379900 Lake Powell at Glen Canyon Dam, AZ')
except Exception: live['powell_usgs'] = None
# other reservoirs: storage against the capacity the operating agency states
others = []
def lc_report():
    t = get_text('https://www.usbr.gov/lc/region/g4000/hourly/levels.html'); txt = html.unescape(re.sub('<[^>]+>', ' ', re.sub(r'<script.*?</script>', '', t, flags=re.S)))
    cap = {}
    m = re.search(r'AVAILABLE CAPACITY IN A\.F\.\s+\*?(\d+)\s+(\d+)\s+(\d+)', txt)
    if m: cap.update({'Lake Mead': int(m.group(1)), 'Lake Mohave': int(m.group(2)), 'Lake Havasu': int(m.group(3))})
    m = re.search(r'MAX\. STORAGE (\d+) AF\s*\|\s*MAX\. STORAGE (\d+) AF\s*\|\s*MAX\. STORAGE (\d+) AF\s*\|\s*MAX\. STORAGE (\d+) AF', txt)
    if m: cap.update({'Lake Powell': int(m.group(1)), 'Flaming Gorge': int(m.group(2)), 'Navajo': int(m.group(3)), 'Blue Mesa': int(m.group(4))})
    return dict(capacity=cap, mead_note='Lake Mead figure is the content at the bottom of exclusive flood control space, as the report labels it')
lcr, _ = cached('usbr_lc_levels_capacity.json', lc_report)
acc, _ = cached('usbr_lc_accumweb.json', lambda: json.loads(get_text('https://www.usbr.gov/lc/region/g4000/riverops/webreports/accumweb.json')))
NAMES = {'Lake Mohave': 'Lake Mohave', 'Lake Havasu': 'Lake Havasu', 'FLAMING GORGE RESERVOIR': 'Flaming Gorge', 'NAVAJO RESERVOIR': 'Navajo', 'BLUE MESA RESERVOIR': 'Blue Mesa', 'LAKE POWELL': 'Lake Powell', 'Lake Mead': 'Lake Mead'}
if acc and lcr:
    for s in acc['Series']:
        if not s['DataTypeName'].startswith('storage, end of period') or s['SiteName'] not in NAMES: continue
        nm = NAMES[s['SiteName']]; cap = lcr['capacity'].get(nm)
        pts = [(x['t'], float(x['v'])) for x in s['Data'] if x['v'] != '']
        if not pts or not cap: continue
        t, v = pts[-1]; mo, dd_, yy = t.split(' ')[0].split('/')
        others.append(dict(name=nm, agency='Reclamation', date='%s-%02d-%02d' % (yy, int(mo), int(dd_)), storage_af=round(v), stated_capacity_af=cap, share=round(v / cap, 3),
                           capacity_label='content at the bottom of exclusive flood control space' if nm == 'Lake Mead' else ('available capacity' if nm in ('Lake Mohave', 'Lake Havasu') else 'maximum storage'),
                           source='Reclamation Lower Colorado daily report and its JSON feed'))
def cdec():
    t = get_text('https://cdec.water.ca.gov/reportapp/javareports?name=RES'); txt = html.unescape(re.sub('<[^>]+>', ' | ', t)); txt = re.sub(r'(\s*\|\s*)+', ' | ', txt)
    out = {}
    for sid in ('SHA', 'ORO'):
        m = re.search(r'\|\s*([A-Z ()]+?)\s*\|\s*%s\s*\|\s*([\d,]+)\s*\|\s*([\d,.]+)\s*\|\s*([\d,]+)\s*\|' % sid, txt)
        if m: out[sid] = dict(name=m.group(1).title(), capacity=int(m.group(2).replace(',', '')), elevation=float(m.group(3).replace(',', '')), storage=int(m.group(4).replace(',', '')))
    d = re.search(r'Ending at midnight - (\d\d)/(\d\d)/(\d{4})', txt); out['as_of'] = '%s-%s-%s' % (d.group(3), d.group(1), d.group(2)) if d else None
    return out
cd, _ = cached('cdec_res.json', cdec)
if cd:
    for sid in ('SHA', 'ORO'):
        if sid in cd: others.append(dict(name=cd[sid]['name'], agency='California CDEC', date=cd.get('as_of'), storage_af=cd[sid]['storage'], stated_capacity_af=cd[sid]['capacity'], share=round(cd[sid]['storage'] / cd[sid]['capacity'], 3), capacity_label='capacity', source='CDEC daily reservoir storage summary (RES)'))
live['others'] = others
# Addendum 2: quotes are whole sentences or carry "..." where cut, labels say which rule governed 2026, the shortage provision sits apart from the elevations
G07 = dict(doc='2007 Interim Guidelines Record of Decision', url='https://www.usbr.gov/lc/region/programs/strategies/RecordofDecision.pdf')
G27 = dict(doc='2027-2028 Operating Guidelines (August 2026)', url='https://www.usbr.gov/ColoradoRiverBasin/post2026/decision-doc/2027-2028OperatingGuidelines_Final.pdf')
THRESH = [
 dict(G07, res='mead', ft=1075, section='2.D.1.a', governs='governed calendar year 2026',
      quote='In years when Lake Mead content is projected to be at or below elevation 1,075 feet and at or above 1,050 feet on January 1, a quantity of 7.167 maf shall be apportioned for consumptive use in the Lower Division States ...'),
 dict(G07, res='mead', ft=1050, section='2.D.1.b', governs='in force through 2026, not the tier that governed 2026',
      quote='In years when Lake Mead content is projected to be below elevation 1,050 feet and at or above 1,025 feet on January 1, a quantity of 7.083 maf shall be apportioned ...'),
 dict(G07, res='mead', ft=1025, section='2.D.1.c', governs='in force through 2026, not the tier that governed 2026',
      quote='In years when Lake Mead content is projected to be below elevation 1,025 feet on January 1, a quantity of 7.0 maf shall be apportioned ...'),
 dict(G27, res='mead', ft=1125, section='5.3.A.5', governs='2027 and 2028',
      quote='Should the Most Probable projection indicate a likelihood of achieving Lake Mead elevation 1,125 feet or above during 2027 or 2028, the Secretary will consult with the Lower Division States regarding the potential to increase apportionments.'),
 dict(G27, res='mead', ft=1010, section='5.3.A.4', governs='2027 and 2028',
      quote='Should the Most Probable projection of any 24-Month Study show Lake Mead falling below 1,010 feet at any time in the subsequent 12-month period, the Secretary shall consult and coordinate with the Basin States and Basin Tribes, and other affected parties as appropriate, to consider potential actions throughout the Basin to respond to and address hydrologic and operational conditions.'),
 dict(G27, res='mead', ft=950, section='5.3', governs='2027 and 2028',
      quote='Below elevation 950 feet, Lake Mead releases are restricted to only the upper penstock outlet works, which would reduce operational flexibility and severely constrain releases, and below this elevation hydropower can no longer be produced.'),
 dict(G27, res='powell', ft=3565, section='5.1.A.1', governs='water years 2027 and 2028',
      quote='In Water Years when the projected October 1 Lake Powell elevation is at or above 3,565 feet, the initial Water Year release will be determined by performing an incremental modeling approach using Exhibit Runs. Reclamation shall first evaluate a Water Year release of 8.23 maf and, if necessary, successively evaluate releases of 8.0 maf and 7.5 maf. The initial Water Year release shall be the first release evaluated that is projected to maintain a minimum Lake Powell elevation of 3,510 feet throughout the Water Year.'),
 dict(G27, res='powell', ft=3540, section='5.1.C.1', governs='water years 2027 and 2028',
      quote='In Water Years when the projected October 1 Lake Powell elevation is below 3,540 feet, the initial Water Year release will be determined by performing a modeling approach using an Exhibit Run.'),
 dict(G27, res='powell', ft=3510, section='5.1', governs='water years 2027 and 2028',
      quote='These operations are designed to protect a minimum Lake Powell elevation of 3,500 feet by initially seeking to maintain a minimum elevation of 3,510 feet.'),
 dict(G27, res='powell', ft=3490, section='5.1', governs='water years 2027 and 2028',
      quote='There are additional impacts to hydropower associated with operating below 3,490 feet, as this is the minimum power pool.'),
]
for t in THRESH:
    lv = (live.get(t['res']) or {}).get('daily_ft')
    t['current_minus_threshold_ft'] = r2(lv - t['ft']) if lv is not None else None
live['thresholds'] = THRESH
live['threshold_notes'] = [
 dict(G27, section='5.3.A.1', what='a shortage provision for 2027 and 2028 that names no elevation',
      quote='The Secretary will determine that a Shortage Condition exists for the applicable Year for purposes of the apportionment of Colorado River water among the Lower Division States and will apportion 6.25 maf for consumptive use in the Lower Division States.'),
 dict(doc='October 2026 Most Probable 24-Month Study (7 maf)', url='https://data.usbr.gov/rise/content-rise-public/rise/catalog-item/binary/OCT26_7_508.pdf', section='page 2',
      what='which 2007 tier governed 2026, and other documents that also governed Lake Mead in 2026 and are not listed in the table',
      quote='Consistent with Section 2.D.1 of the 2007 Interim Guidelines, a Shortage Condition consistent with Section 2.D.1.a governs the operation of Lake Mead for CY 2026. In addition, Section III.B of Exhibit 1 to the Lower Basin Drought Contingency Plan (DCP) Agreement and provisions in IBWC Minutes No. 323 and 330 also governs the operation of Lake Mead for CY 2026.'),
]
live['added_after_plan'] = ['largest_rise_60d', 'lowest_daily_since_dec_1999', 'datum notes', 'measured-side cross-checks']
live['datum'] = dict(mead='RISE names the USGS 1912 datum, "Locally known at Hoover Dam as \u201cPower House Datum.\u201d Add 0.55 foot to convert to National Geodetic Vertical Datum of 1929 (NVGD 1929), leveling of 1935."',
                     powell='RISE lists EGM96 for the Lake Powell site and gives no definition.')

# ---------------- 7. USGS provisional against approved (snapshot) ----------------
GAUGES = [('09379900', '62614'), ('09380000', '00060'), ('09402500', '00060'), ('09404200', '00060'), ('09415000', '00060'), ('09180500', '00060'), ('09315000', '00060'), ('09379500', '00060')]
snapf = 'data/usgs_snapshots.json'; snap = json.load(open(snapf)) if os.path.exists(snapf) else {'first_read': None, 'prov': {}, 'revised': {}}
if not OFF:
    try:
        st = time.strftime('%Y-%m-%d', time.gmtime(NOW - 540 * 86400))
        u = 'https://waterservices.usgs.gov/nwis/dv/?format=json&sites=%s&parameterCd=00060,62614&statCd=00003&startDT=%s&endDT=%s' % (','.join(g for g, _ in GAUGES), st, TODAY)
        d = json.loads(get_text(u)); want = set('%s:%s' % g for g in GAUGES)
        for ts in d['value']['timeSeries']:
            site = ts['sourceInfo']['siteCode'][0]['value']; par = ts['variable']['variableCode'][0]['value']; gk = '%s:%s' % (site, par)
            if gk not in want: continue
            for x in ts['values'][0]['value']:
                v = float(x['value']); day = x['dateTime'][:10]; q = x['qualifiers']; kk = gk + ':' + day
                if v == -999999.0: continue
                if 'P' in q and kk not in snap['prov']: snap['prov'][kk] = dict(v=v, read=TODAY)
                elif 'A' in q and kk in snap['prov'] and kk not in snap['revised']: snap['revised'][kk] = dict(p=snap['prov'][kk]['v'], a=v, approved_seen=TODAY)
        snap['first_read'] = snap['first_read'] or TODAY
        json.dump(snap, open(snapf + '.tmp', 'w')); os.replace(snapf + '.tmp', snapf)
    except Exception as e: log('usgs snapshot failed', repr(e)[:160])
rev = []
for g, par in GAUGES:
    gk = '%s:%s' % (g, par); rr = [v for k, v in snap['revised'].items() if k.startswith(gk + ':')]
    held = sum(1 for k in snap['prov'] if k.startswith(gk + ':'))
    big = [x for x in rr if (abs(x['a'] - x['p']) > 0.1 if par == '62614' else (abs(x['a'] - x['p']) > 0.01 * max(abs(x['p']), 1e-9)))]
    lo, hi = K.wilson(len(big), len(rr))
    rev.append(dict(site=g, parameter=par, provisional_days_stored=held, approved_since=len(rr), revised_beyond_threshold=len(big), lo=round(lo, 3), hi=round(hi, 3), outcome=K.CANNOT_TELL, reason=(K.TOO_WIDE_TO_RESOLVE if len(rr) < 30 else K.NO_INTERVAL_FORMABLE),   # under 30 revised days (PLAN.md), or no stated figure to read against (the plan states none)
                    
                    threshold='0.1 ft' if par == '62614' else '1 percent'))

# ---------------- 7a. measured-side cross-checks (in the plan as reported, not scored, Addendum 2 puts them on the page) ----------------
def lc_eom_table():
    t = get_text('https://www.usbr.gov/lc/region/g4000/hourly/mead-elv.html'); txt = html.unescape(re.sub('<[^>]+>', ' ', re.sub(r'<script.*?</script>', '', t, flags=re.S)))
    out = {}
    for m in re.finditer(r'\n\s*((?:19|20)\d\d)((?:\s+(?:-{3}|\d{3,4}\.\d{1,2}))+)', txt):
        y = int(m.group(1)); vals = m.group(2).split()
        if len(vals) != 12: continue
        for i, v in enumerate(vals):
            if v != '---': out['%d-%02d' % (y, i + 1)] = float(v)
    return out
lct, _ = cached('lc_mead_eom_table.json', lc_eom_table)
xc = {}
if lct:
    om = (obs or {}).get('mead', {})
    d90 = [(mo, om[mo], v) for mo, v in lct.items() if mo >= '1990-01' and mo in om and abs(om[mo] - v) > 0.0051]
    d00 = [x for x in d90 if x[0] >= '2000-01']; big = max(d00, key=lambda x: abs(x[1] - x[2])) if d00 else None
    xc['mead_hdb_vs_lc_table'] = dict(months_compared_since_1990=sum(1 for mo in lct if mo >= '1990-01' and mo in om), differ_since_1990=len(d90), differ_since_2000=len(d00),
                                      largest_since_2000=dict(month=big[0], hdb=r2(big[1]), lc_table=r2(big[2]), gap=r2(big[1] - big[2])) if big else None,
                                      months_since_2000=[dict(month=mo, hdb=r2(a_), lc_table=r2(b_)) for mo, a_, b_ in d00])
ud, _ = cached('usgs_09379900_dv_since_2019.json', lambda: json.loads(get_text('https://waterservices.usgs.gov/nwis/dv/?format=json&sites=09379900&parameterCd=62614&statCd=00003&startDT=2019-04-01&endDT=' + TODAY)))
if ud:
    uv = {}
    for ts in ud['value']['timeSeries']:
        for x in ts['values'][0]['value']:
            if float(x['value']) != -999999.0: uv[x['dateTime'][:10]] = float(x['value'])
    pd_ = (daily or {}).get('powell', {}); diffs = sorted(uv[d] - pd_[d] for d in uv if d in pd_)
    if diffs: xc['powell_usgs_daily_mean_minus_hdb_end_of_day'] = dict(days=len(diffs), median=r2(statistics.median(diffs)), p10=r2(pct(diffs, 0.1)), p90=r2(pct(diffs, 0.9)))
# Addendum 2: misread rate of our print reading, by era, measured where an HDB run agrees with the print
ERAS = [('2000 to 2005', '2000', '2005'), ('2006 to 2011', '2006', '2011'), ('2012 to 2017', '2012', '2017'), ('2018 to 2026', '2018', '2026')]
byid = {r['id']: r for r in reports}; era_rate = []
for name, y0, y1 in ERAS:
    both = dif = 0; po = 0
    for rid, m in meta.items():
        y = byid[rid]['issue'][:4]
        if not (y0 <= y <= y1): continue
        for k2, v in m.get('hdb_check', {}).items():
            if m['read'].get(k2) == 'hdb': both += v.get('both', 0); dif += v.get('differ', 0)
        for k2 in ('mead', 'powell'):
            if m['read'].get(k2) == 'text': po += sum(1 for x in stated.get((rid, k2), {}).values() if x is not None)
    era_rate.append(dict(era=name, months_compared=both, misread=dif, rate=round(dif / both, 4) if both else None, print_only_values=po))

# ---------------- 8. outputs ----------------
cnt = C.Counter((r['res'], r.get('outcome_before_gate') or r['outcome']) for r in rows if not r.get('read_status'))
failed_reads = dict(C.Counter(r['res'] for r in rows if r.get('read_status')))
reads = C.Counter((k, v) for m in meta.values() for k, v in m.get('read', {}).items())
hdbdiff = sum(1 for m in meta.values() for k, v in m.get('hdb_check', {}).items() if v.get('differ'))
unread = sum(1 for (rid, key), vals in stated.items() for t, v in vals.items() if v is None)
cov = dict(reports=len(reports), by_scenario=dict(C.Counter(r['scenario'] for r in reports)), first_issue=min(r['issue'] for r in reports), last_issue=max(r['issue'] for r in reports),
           band_months=sum(1 for sc in by_issue.values() if 'MIN' in sc and 'MAX' in sc), missing_files=sum(1 for m in meta.values() if m.get('missing')),
           read_from={'%s %s' % k: v for k, v in reads.items()}, hdb_runs_that_differ_from_print=hdbdiff, unreadable_values=unread, duplicates_set_aside=dups,
           rows=len(rows), rows_by_outcome={'%s %s' % k: v for k, v in sorted(cnt.items())}, failed_reads=failed_reads, variant_rows=len(vrows),
           inverted_band_rows=sum(1 for r in rows if r.get('inverted')), mp_outside_own_band_rows=sum(1 for r in rows if r.get('mp_outside')),
           inverted_detail=dict(mead=sum(1 for r in rows if r.get('inverted') and r['res'] == 'mead'), powell=sum(1 for r in rows if r.get('inverted') and r['res'] == 'powell'),
                                powell_leads_0_to_5=sum(1 for r in rows if r.get('inverted') and r['res'] == 'powell' and r['lead'] <= 5)),
           zero_width_band_rows=sum(1 for r in rows if r.get('band_lo') is not None and r['band_hi'] - r['band_lo'] <= 0.005),
           zero_width_lead0={k: [sum(1 for r in rows if r['res'] == k and r['lead'] == 0 and r.get('band_lo') is not None and r['measured'] is not None and r['band_hi'] - r['band_lo'] <= 0.005),
                                 sum(1 for r in rows if r['res'] == k and r['lead'] == 0 and r.get('band_lo') is not None and r['measured'] is not None)] for k in ('mead', 'powell')},
           print_vs_hdb=dict(months_compared=sum(v.get('both', 0) for m in meta.values() for v in m.get('hdb_check', {}).values()),
                             months_agree=sum(v.get('agree', 0) for m in meta.values() for v in m.get('hdb_check', {}).values()),
                             runs_used=sum(1 for m in meta.values() for k, v in m.get('read', {}).items() if v == 'hdb'),
                             runs_below_60=sum(1 for m in meta.values() for v in m.get('hdb_check', {}).values() if v.get('both') and v.get('share', 1) < 0.60),
                             misread_rate_in_used_runs=round(sum(v['differ'] for m in meta.values() for k, v in m.get('hdb_check', {}).items() if m['read'].get(k) == 'hdb') / max(1, sum(v['both'] for m in meta.values() for k, v in m.get('hdb_check', {}).items() if m['read'].get(k) == 'hdb')), 4)),
           measured_last={k: max(measured[k]) if measured[k] else None for k in measured})
def notable():
    out = []
    for key in ('mead', 'powell'):
        sc = [r for r in rows if r['res'] == key and r.get('mp_error') is not None and 1 <= r['lead'] <= 12]
        for r in sorted(sc, key=lambda r: -abs(r['mp_error']))[:5]: out.append(dict(kind='largest Most Probable miss, leads 1 to 12', **{k: r.get(k) for k in ('res', 'issue', 'target', 'lead', 'mp', 'pmin', 'pmax', 'measured', 'mp_error', 'outcome', 'reason')}))
        rec = [r for r in rows if r['res'] == key and r['measured'] is not None]
        last_t = max((r['target'] for r in rec), default=None)
        for r in sorted([r for r in rec if r['target'] == last_t], key=lambda r: r['lead'])[:13]: out.append(dict(kind='latest measured month', **{k: r.get(k) for k in ('res', 'issue', 'target', 'lead', 'mp', 'pmin', 'pmax', 'measured', 'mp_error', 'outcome', 'reason')}))
    return out
head = {key: dict(band=next(c['band'] for c in cells if c['res'] == key and c['lead'] == 6), mp=next(c['mp'] for c in cells if c['res'] == key and c['lead'] == 6)) for key in ('mead', 'powell')}
with open('data/water_history.jsonl', 'a') as hf:   # one line per run, so later readings can be traced
    hf.write(json.dumps(dict(run=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW)), plan_sha256=hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest()[:16], lead6={k: dict(band=[v['band']['inside'], v['band']['n'], v['band']['outcome']], mp=[v['mp']['above'], v['mp']['n'], v['mp']['outcome']]) for k, v in head.items()}, mead_ft=(live.get('mead') or {}).get('daily_ft'), powell_ft=(live.get('powell') or {}).get('daily_ft'), measured_last=cov['measured_last'])) + '\n')
summary = dict(updated=time.strftime('%Y-%m-%d %H:%M', time.gmtime(NOW)),stale_sources=STALE + (['offline run'] if OFF else []), plan_sha256=hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest(), known_good=kg, gate='passed' if GATE else 'FAILED',
               coverage=cov, headline_lead6=head, cells=cells, flagged=dict(cells=len(cells) * 2, flagged=flags, groups=flagged, note='Neighbouring cells share reports and target months, so these are not separate results.'),
               band_sentence_months=dict(note='Added after the data: band cells restricted to the issue months whose Probable Minimum and Probable Maximum reports both print the 80 percent sentence.', months=sorted(SENT), cells=sent_cells),
               misread_by_era=era_rate, measured_cross_checks=xc,
               checks_after_data_note='Added after the data and never used for any outcome. Each cell carries the same count read on three other rulers: rows_as_independent (Wilson on rows), kish_weighted_water_years (water years weighted by row count, n = (sum m) squared over sum of m squared), two_water_year_blocks (water years paired 2000-2001, 2002-2003 and so on). The effective count of successes is rounded as the plan rounds it, and the unrounded reading is given beside it. wy_lag1_corr is the correlation of the per-water-year share between neighbouring water years.',
               variants=vrows, notable=notable(), live=live, usgs_revisions=dict(first_read=snap.get('first_read'), gauges=rev))
json.dump(rows, open('data/water.json', 'w'), separators=(',', ':'))
json.dump(summary, open('summary_water.json', 'w'), indent=1)
pub = {k: summary[k] for k in ('updated', 'gate', 'stale_sources', 'coverage', 'headline_lead6', 'cells', 'checks_after_data_note', 'flagged', 'band_sentence_months', 'misread_by_era', 'measured_cross_checks', 'variants', 'notable', 'live', 'usgs_revisions')}
json.dump(pub, open('data/water_live.json', 'w'), separators=(',', ':'))
msg = 'water: %d reports, %d rows, gate %s, lead-6 band Mead %s/%s Powell %s/%s' % (len(reports), len(rows), 'passed' if GATE else 'FAILED', head['mead']['band']['inside'], head['mead']['band']['n'], head['powell']['band']['inside'], head['powell']['band']['n'])
if PUB:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'water_live', '--path', os.path.join(H, 'data', 'water_live.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                       cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
    msg += '; published' if p.returncode == 0 else '; publish FAILED'
print(msg)
