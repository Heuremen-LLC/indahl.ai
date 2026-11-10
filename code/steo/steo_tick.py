#!/usr/bin/env python3
"""steo_tick.py: STEO rider (see PLAN.md). Rerunnable. Installs no timer. Reads the Internet Archive copies of the EIA STEO chart gallery workbook
(data/raw/wayback, fetched by fetch_wayback.py, refreshed at most once in 7 days), the STEO release table (data/releases.json, fetch_archive.py) and
EIA's monthly spot prices for WTI and Henry Hub (refreshed at most once in 24 hours), and sets each stated 95 percent interval beside the monthly
average spot price. Writes data/steo.json, summary_steo.json, data/steo_live.json, data/steo_history.jsonl.
--offline: no network. --publish: also put data/steo_live.json in the site KV as steo_live, served at /steo/live.json. --selftest: rule checks only.
Run with venv/bin/python (xlrd for the .xls copies and the spot files)."""
import os, sys, json, time, math, re, glob, zipfile, html, hashlib, subprocess, datetime as DT, urllib.request, collections as C
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
OFF = '--offline' in sys.argv; PUB = '--publish' in sys.argv
UA = 'heuremen-steo/0.1 (+https://indahl.ai/steo)'; WB = 'data/raw/wayback'; SPOT = 'data/raw/spot'
SPOT_URL = {'WTI': ('RWTCm.xls', 'https://www.eia.gov/dnav/pet/hist_xls/RWTCm.xls'), 'HH': ('RNGWHHDm.xls', 'https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDm.xls')}
SERIES = ('WTI', 'HH'); SNAME = {'WTI': 'WTI crude oil', 'HH': 'Henry Hub natural gas'}
LEVEL = 0.95; MIN_ROWS = 30; MIN_MONTHS = 24; MAX_W = 0.15; BLOCK = 12; REPS = 2000; SEED = 20261110
LEADS = (('all leads', 1, 999), ('1 to 2 months', 1, 2), ('3 to 6 months', 3, 6), ('7 to 12 months', 7, 12), ('13 months or more', 13, 999))
NOW = time.time(); STAMP = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW)); STALE = []
os.makedirs(SPOT, exist_ok=True)
def log(*a): print('steo:', *a, file=sys.stderr)
def fnum(x):
    try:
        v = float(x); return v if math.isfinite(v) else None
    except Exception: return None
def ym_of_serial(s):
    v = fnum(s)
    if v is None or v < 20000 or v > 80000: return None
    d = DT.date(1899, 12, 30) + DT.timedelta(days=int(v)); return '%04d-%02d' % (d.year, d.month)
def mdiff(a, b): return (int(a[:4]) - int(b[:4])) * 12 + int(a[5:7]) - int(b[5:7])

# ---------------- the rule (PLAN.md, Rules) ----------------
def row_outcome(lo, hi, y, why=None):
    if why: return K.CANNOT_TELL, why
    if lo is None or hi is None or lo > hi: return K.CANNOT_TELL, 'unreadable'
    if y is None: return K.NOTHING_RETURNED, None
    if y > hi: return K.ABOVE, None
    if y < lo: return K.BELOW, None
    return K.CONSISTENT, None
def cell_outcome(lo, hi, n, months):
    if n < MIN_ROWS or months < MIN_MONTHS or lo is None: return K.CANNOT_TELL
    if hi < LEVEL: return K.BELOW
    if lo > LEVEL: return K.ABOVE
    if hi - lo <= MAX_W: return K.CONSISTENT
    return K.CANNOT_TELL
def draws(W, reps=REPS, seed=SEED, block=BLOCK):
    rng = np.random.default_rng(seed); M = np.zeros((reps, W))
    if W < block: return M
    nb = math.ceil(W / block); st = rng.integers(0, W - block + 1, size=(reps, nb))
    for j in range(block): np.add.at(M, (np.repeat(np.arange(reps), nb), (st + j).ravel()), 1)
    return M
def boot(num, den, M):
    a = M @ num; b = M @ den; ok = b > 0
    if ok.sum() < 100: return None, None
    r = a[ok] / b[ok]; return float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))
def rule_selftest():
    t = [row_outcome(10, 20, 25) == (K.ABOVE, None), row_outcome(10, 20, 5) == (K.BELOW, None), row_outcome(10, 20, 10) == (K.CONSISTENT, None),
         row_outcome(20, 10, 15) == (K.CANNOT_TELL, 'unreadable'), row_outcome(None, 10, 5) == (K.CANNOT_TELL, 'unreadable'), row_outcome(10, 20, None) == (K.NOTHING_RETURNED, None),
         row_outcome(10, 20, 15, 'issue unknown') == (K.CANNOT_TELL, 'issue unknown'), ym_of_serial('42186') == '2015-07', mdiff('2016-01', '2015-11') == 2]
    rng = np.random.default_rng(5); W = 150; M = draws(W, 500, 3); y = rng.standard_normal((W, 20))
    for half, want in ((1.0, K.CONSISTENT), (0.5, K.BELOW)):
        ins = (np.abs(y) <= 1.959964 * half).sum(1).astype(float); lo, hi = boot(ins, np.full(W, 20.0), M); t.append(cell_outcome(lo, hi, W * 20, W) == want)
    t += [cell_outcome(0.9, 0.99, 20, 50) == K.CANNOT_TELL, cell_outcome(0.9, 0.99, 100, 10) == K.CANNOT_TELL, cell_outcome(0.7, 0.99, 100, 50) == K.CANNOT_TELL, cell_outcome(0.96, 0.99, 100, 50) == K.ABOVE]
    return all(t), t
if '--selftest' in sys.argv:
    ok, t = rule_selftest(); print('rule selftest', 'PASSED' if ok else 'FAILED', t); sys.exit(0 if ok and K.selftest() else 1)

# ---------------- 0. refresh (spot once in 24 h, archive copies once in 7 days) ----------------
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=120) as r: return r.read()
def age_h(f): return 1e9 if not os.path.exists(f) else (NOW - os.path.getmtime(f)) / 3600
if not OFF:
    for s, (n, u) in SPOT_URL.items():
        f = os.path.join(SPOT, n)
        if age_h(f) >= 24:
            try: b = get(u); open(f + '.part', 'wb').write(b); os.replace(f + '.part', f); time.sleep(1.5)
            except Exception as e: log('spot fetch FAILED', s, repr(e)[:120]); STALE.append('spot ' + s)
    if age_h(os.path.join(WB, 'cdx_chart_gallery.json')) >= 24 * 7:
        for scr in ('fetch_archive.py', 'fetch_wayback.py'):
            p = subprocess.run([sys.executable, '-I', scr], capture_output=True, text=True, timeout=3600)
            if p.returncode: log(scr, 'FAILED', p.stderr[-200:]); STALE.append(scr)

# ---------------- 1. readers ----------------
def xlsx_sheets(path):
    """-> {sheet name: {(row, col letter): value text}} from the raw sheet XML (cached values)."""
    z = zipfile.ZipFile(path); names = z.namelist(); ss = []
    if 'xl/sharedStrings.xml' in names:
        x = z.read('xl/sharedStrings.xml').decode('utf8')
        for si in re.findall(r'(?s)<si>(.*?)</si>', x): ss.append(html.unescape(''.join(re.findall(r'(?s)<t[^>]*>(.*?)</t>', si))))
    wb = z.read('xl/workbook.xml').decode('utf8'); rels = z.read('xl/_rels/workbook.xml.rels').decode('utf8'); rid = {}
    for m in re.finditer(r'<Relationship [^>]*>', rels):
        a = m.group(0); rid[re.search(r'Id="([^"]+)"', a).group(1)] = re.search(r'Target="([^"]+)"', a).group(1)
    out = {}
    for m in re.finditer(r'<sheet [^>]*>', wb):
        a = m.group(0); nm = html.unescape(re.search(r'name="([^"]+)"', a).group(1)); tg = rid[re.search(r'r:id="([^"]+)"', a).group(1)].lstrip('/')
        tg = tg if tg.startswith('xl/') else 'xl/' + tg; x = z.read(tg).decode('utf8'); c = {}
        for mm in re.finditer(r'(?s)<c r="([A-Z]+)(\d+)"([^>]*?)(?:/>|>(.*?)</c>)', x):
            col, row, attr, inner = mm.groups(); v = re.search(r'<v>(.*?)</v>', inner or '')
            if not v:
                t = re.search(r'(?s)<t[^>]*>(.*?)</t>', inner or '')
                if t: c[(int(row), col)] = html.unescape(t.group(1))
                continue
            c[(int(row), col)] = ss[int(v.group(1))] if 't="s"' in attr else html.unescape(v.group(1))
        out[nm] = c
    return out
def col_letter(i):
    s = ''
    i += 1
    while i: i, r = divmod(i - 1, 26); s = chr(65 + r) + s
    return s
def xls_sheets(path):
    import xlrd
    b = xlrd.open_workbook(path); out = {}
    for sh in b.sheets():
        c = {}
        for r in range(sh.nrows):
            for k in range(sh.ncols):
                if sh.cell_type(r, k) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK, xlrd.XL_CELL_ERROR): continue   # 10 Nov 2026, referee R1: an Excel error cell (#N/A) is no value, xlrd gives it as code 42
                v = sh.cell_value(r, k)
                if v == '' or v is None: continue
                c[(r + 1, col_letter(k))] = repr(v) if isinstance(v, float) else str(v)
        out[sh.name] = c
    return out
def ci_sheet(c):
    """-> dict(level, note, title, series label, rows) or None if the sheet has no interval table."""
    hdr = [(r, k) for (r, k), v in c.items() if str(v).strip() == 'Lower']
    if not hdr: return None
    r0, klo = hdr[0]; kup = next((k for (r, k), v in c.items() if r == r0 and str(v).strip() == 'Upper'), None)
    if not kup or not any('onfidence' in str(v) for (r, k), v in c.items() if r in (r0 - 1, r0)): return None
    kmon = next((k for (r, k), v in c.items() if r == r0 and str(v).strip() == 'Month'), None)
    khist = next((k for (r, k), v in c.items() if r == r0 - 1 and str(v).strip() == 'Historical'), None)
    kset = next((k for (r, k), v in c.items() if r == r0 - 1 and str(v).strip() == 'Settle'), None)
    texts = [str(v) for v in c.values()]
    lv_row = next((r for (r, k), v in c.items() if 'percentage between' in str(v)), None)
    level = None
    if lv_row:
        nums = [fnum(v) for (r, k), v in sorted(c.items(), key=lambda kv: (kv[0][0], len(kv[0][1]), kv[0][1])) if r == lv_row and fnum(v) is not None]
        level = nums[0] if nums else None
    note = next((t for t in texts if 'trading days ending' in t), None)
    title = next((t for t in texts if re.match(r'\s*Short-Term Energy Outlook,\s+\w+\s+\d{4}', t)), None)
    lab = next((t for t in texts if re.search(r'Henry Hub|WTI|West Texas', t)), None)
    rows = []
    for (r, k), v in c.items():
        if k != kmon or r <= r0: continue
        ym = ym_of_serial(v)
        if not ym: continue
        g = lambda kk: fnum(c.get((r, kk))) if kk else None
        rows.append(dict(month=ym, row=r, hist=g(khist), settle=g(kset), lower=g(klo), upper=g(kup), lower_txt=c.get((r, klo)), upper_txt=c.get((r, kup))))
    return dict(level=level, note=note, title=title, label=lab, rows=sorted(rows, key=lambda x: x['month']), cols=dict(month=kmon, lower=klo, upper=kup, hist=khist))
MON = {m: i + 1 for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])}
def note_date(note):
    m = re.search(r'trading days ending\s+([A-Za-z]+)\.?\s+(\d{1,2}),\s+(\d{4})', note or '')
    if not m or m.group(1)[:3].lower() not in MON: return None
    return '%s-%02d-%02d' % (m.group(3), MON[m.group(1)[:3].lower()], int(m.group(2)))
releases = json.load(open('data/releases.json')) if os.path.exists('data/releases.json') else []
REL = sorted(r['released'] for r in releases); ISSUE = {r['released']: r['issue'] for r in releases}

# ---------------- 2. stated side ----------------
cdx = json.load(open(os.path.join(WB, 'cdx_chart_gallery.json'))) if os.path.exists(os.path.join(WB, 'cdx_chart_gallery.json')) else []
files = sorted(glob.glob(os.path.join(WB, 'cg_*.xls*')))
copies = []; cnt_copy = C.Counter(); fmt_ok = True
for f in files:
    ts = re.search(r'cg_(\d{14})_', f).group(1); cap = '%s-%s-%s' % (ts[:4], ts[4:6], ts[6:8])
    try: sh = xlsx_sheets(f) if f.endswith('.xlsx') else xls_sheets(f)
    except Exception as e: cnt_copy['does not open'] += 1; continue
    found = {}
    for nm, c in sh.items():
        s = ci_sheet(c)
        if not s: continue
        lab = s['label'] or ''
        ser = 'HH' if 'Henry Hub' in lab else ('WTI' if re.search(r'WTI|West Texas', lab) else {'Fig1': 'WTI', '1': 'WTI', 'Fig4': 'HH', '4': 'HH'}.get(nm))
        if ser and ser not in found: found[ser] = dict(s, sheet=nm)
    if not found: cnt_copy['no interval table'] += 1; continue
    if set(found) != set(SERIES): fmt_ok = False
    nd = None
    for s in found.values(): nd = nd or note_date(s['note'])
    rel = next((r for r in REL if nd and r > nd), None)
    why = None
    if not nd or not rel: why = 'issue unknown'
    elif rel > cap: why = 'issue unknown'   # the copy was made before the release it maps to
    cnt_copy['used' if not why else 'issue unknown'] += 1
    copies.append(dict(file=os.path.basename(f), captured=cap, ts=ts, note_date=nd, released=rel, issue=ISSUE.get(rel), why=why, sheets=found,
                       url=next(('https://web.archive.org/web/%s/%s' % (u['ts'], u['url']) for u in cdx if u['ts'] == ts), None)))
# one statement per issue: the earliest copy; later copies that differ are counted
by_issue = C.defaultdict(list)
for cp in copies:
    if not cp['why']: by_issue[cp['released']].append(cp)
differ = 0
for rel, cps in by_issue.items():
    cps.sort(key=lambda x: x['ts'])
    for later in cps[1:]:
        for s in SERIES:
            a = {r['month']: (r['lower'], r['upper']) for r in cps[0]['sheets'].get(s, {}).get('rows', [])}
            b = {r['month']: (r['lower'], r['upper']) for r in later['sheets'].get(s, {}).get('rows', [])}
            differ += sum(1 for m in a if m in b and a[m] != b[m] and a[m][0] is not None)

# ---------------- 3. delivered side ----------------
def read_spot(s):
    f = os.path.join(SPOT, SPOT_URL[s][0])
    if not os.path.exists(f): return {}, None
    import xlrd
    b = xlrd.open_workbook(f); sh = b.sheet_by_name('Data 1'); out = {}
    for r in range(sh.nrows):
        ym = ym_of_serial(sh.cell_value(r, 0)); v = fnum(sh.cell_value(r, 1))
        if ym and v is not None: out[ym] = v
    return out, time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(f)))
spot = {}; spot_read = {}
for s in SERIES: spot[s], spot_read[s] = read_spot(s)

# Addendum 1 (PLAN.md, after the data): a sheet with no level cell takes 0.95 when the issue's PDF labels the series' bounds "95% NYMEX".
PDFL_F = 'data/pdf_levels.json'; PDFL = json.load(open(PDFL_F)) if os.path.exists(PDFL_F) else {}
def pdf_level(issue, s):
    k = '%s/%s' % (issue, s)
    if k in PDFL: return PDFL[k]
    f = 'data/raw/archives/%s.pdf' % issue; ok = None
    if os.path.exists(f):
        try:
            import pypdf
            ok = False
            for pg in pypdf.PdfReader(f).pages:
                tx = pg.extract_text() or ''
                if re.search(r'95%\s*NYMEX', tx) and re.search(r'confidence', tx, re.I) and re.search(r'West Texas|WTI' if s == 'WTI' else r'Henry Hub', tx): ok = True; break
        except Exception: ok = None
    if ok is not None: PDFL[k] = ok
    return ok

# ---------------- 4. rows ----------------
rows = []; begun = 0; bad_issue_rows = 0
for rel in sorted(by_issue):
    cp = by_issue[rel][0]; relm = rel[:7]
    for s in SERIES:
        sh = cp['sheets'].get(s)
        if not sh: continue
        lv_ok = sh['level'] is not None and abs(sh['level'] - LEVEL) < 1e-9
        for r in sh['rows']:
            if r['lower'] is None and r['upper'] is None and (r['lower_txt'] in (None, '#N/A', '') and r['upper_txt'] in (None, '#N/A', '')): continue   # no interval stated for this month
            if r['month'] <= relm:
                if r['lower'] is not None or r['upper'] is not None: begun += 1   # referee R2: count only months with a stated value
                continue
            y = spot[s].get(r['month'])
            # a month counts as delivered only once it has ended and EIA lists it
            o, why = row_outcome(r['lower'], r['upper'], y, None if lv_ok else 'unreadable')
            lv2 = lv_ok or (sh['level'] is None and pdf_level(cp['issue'], s) is True)
            o2, why2 = row_outcome(r['lower'], r['upper'], y, None if lv2 else 'unreadable')
            rows.append(dict(issue=cp['issue'], released=rel, series=s, month=r['month'], lead=mdiff(r['month'], relm), lower=r['lower'], upper=r['upper'], settle=r['settle'],
                             spot=y, outcome=o, why=why, outcome_add1=o2, why_add1=why2, level_from='workbook' if lv_ok else ('pdf legend' if lv2 else None), copy=cp['file'], copy_url=cp['url'], level=sh['level']))
json.dump(PDFL, open(PDFL_F, 'w'), indent=0)
for cp in copies:
    if cp['why']: bad_issue_rows += sum(1 for s in cp['sheets'].values() for r in s['rows'] if r['lower'] is not None)

# ---------------- 5. known-good gates ----------------
kg = {'format': fmt_ok and bool(copies)}
ok2 = []
for want in (json.load(open('data/known_good_rows.json')) if os.path.exists('data/known_good_rows.json') else []):
    f = os.path.join(WB, want['file']); raw = None
    if f.endswith('.xls'):
        try:
            import xlrd
            sh_ = xlrd.open_workbook(f).sheet_by_name(want['sheet']); ci = ord(want['col']) - 65
            raw = repr(sh_.cell_value(want['row'] - 1, ci)) if sh_.cell_type(want['row'] - 1, ci) == xlrd.XL_CELL_NUMBER else None
        except Exception: raw = None
        cp = next((c for c in copies if c['file'] == want['file']), None); parsed = None
        for s in (cp['sheets'].values() if cp else []):
            if s['sheet'] == want['sheet']: parsed = next((r['upper'] for r in s['rows'] if r['row'] == want['row']), None)
        ok2.append(raw == want['value'] and parsed == float(want['value'])); continue
    try:
        z = zipfile.ZipFile(f); wb = z.read('xl/workbook.xml').decode(); rels = z.read('xl/_rels/workbook.xml.rels').decode()
        rid = re.search(r'<sheet [^>]*name="%s"[^>]*r:id="([^"]+)"' % re.escape(want['sheet']), wb).group(1)
        tg = (re.search(r'Id="%s"[^>]*Target="([^"]+)"' % rid, rels) or re.search(r'Target="([^"]+)"[^>]*Id="%s"' % rid, rels)).group(1).lstrip('/'); tg = tg if tg.startswith('xl/') else 'xl/' + tg
        m = re.search(r'(?s)<c r="%s%d"[^>]*>.*?<v>([^<]*)</v>' % (want['col'], want['row']), z.read(tg).decode()); raw = m.group(1) if m else None
    except Exception: raw = None
    cp = next((c for c in copies if c['file'] == want['file']), None)
    parsed = None
    if cp:
        for s in cp['sheets'].values():
            if s['sheet'] == want['sheet']:
                parsed = next((r['upper'] for r in s['rows'] if r['row'] == want['row']), None)
    ok2.append(raw == want['value'] and parsed == float(want['value']))
kg['reader'] = len(ok2) >= 3 and all(ok2)
kg['issue_map'] = all(cp['why'] is None for cp in copies if cp['note_date']) and any(not cp['why'] for cp in copies)
same = {}
for s in SERIES:
    n = k = 0
    for rel, cps in by_issue.items():
        sh = cps[0]['sheets'].get(s)
        if not sh: continue
        for r in sh['rows']:
            if r['month'] < rel[:7] and r['hist'] is not None and r['month'] in spot[s]:
                n += 1; k += abs(r['hist'] - spot[s][r['month']]) <= 0.02 * abs(spot[s][r['month']])
    same[s] = dict(months=n, within_2pct=k)
kg['same_quantity'] = all(v['months'] >= 20 and v['within_2pct'] / v['months'] >= 0.90 for v in same.values())
# 10 Nov 2026, referee R1: a stated interval of zero width is a reader fault (the #N/A cells of the .xls copies were read as 42). Added at the referee.
kg['no_zero_width'] = not any(r['lower'] is not None and r['lower'] == r['upper'] for r in rows)
kg['rule'] = rule_selftest()[0]
GATE = all(kg.values())
if not GATE:
    for r in rows:
        if r['outcome'] in K.OUTCOMES: r['outcome_before_gate'] = r['outcome']; r['outcome'] = K.CANNOT_TELL
        if r['outcome_add1'] in K.OUTCOMES: r['outcome_add1_before_gate'] = r['outcome_add1']; r['outcome_add1'] = K.CANNOT_TELL

# ---------------- 6. cells ----------------
def make_cells(OK, WK):
  out = []
  for s in SERIES:
    rs_s = [r for r in rows if r['series'] == s]; sc_s = [r for r in rs_s if r[OK] in (K.CONSISTENT, K.ABOVE, K.BELOW)]
    months = sorted({r['month'] for r in sc_s}); MI = {m: i for i, m in enumerate(months)}; M = draws(len(months))
    for nm, a, b in LEADS:
        rs = [r for r in rs_s if a <= r['lead'] <= b]; cnt = C.Counter(r[OK] for r in rs)
        sc = [r for r in rs if r[OK] in (K.CONSISTENT, K.ABOVE, K.BELOW)]; n = len(sc); k = cnt[K.CONSISTENT]; mo = len({r['month'] for r in sc})
        lo = hi = None
        if n:
            num = np.zeros(len(months)); den = np.zeros(len(months))
            for r in sc: num[MI[r['month']]] += r[OK] == K.CONSISTENT; den[MI[r['month']]] += 1
            lo, hi = boot(num, den, M)
        why = C.Counter(r[WK] for r in rs if r[OK] == K.CANNOT_TELL)
        out.append(dict(series=s, cell=nm, stated=LEVEL, rows=len(rs), scored=n, inside=k, above=cnt[K.ABOVE], below=cnt[K.BELOW], cannot_tell=cnt[K.CANNOT_TELL], cannot_tell_why={str(x): y for x, y in why.items()},
                          nothing_returned=cnt[K.NOTHING_RETURNED], months=mo, issues=len({r['issue'] for r in sc}), share=round(k / n, 4) if n else None,
                          share_above=round(cnt[K.ABOVE] / n, 4) if n else None, share_below=round(cnt[K.BELOW] / n, 4) if n else None,
                          lo=None if lo is None else round(lo, 4), hi=None if hi is None else round(hi, 4), outcome=cell_outcome(lo, hi, n, mo) if GATE else K.CANNOT_TELL))
  return out
cells = make_cells('outcome', 'why'); cells_add1 = make_cells('outcome_add1', 'why_add1')
def med(xs): return round(float(np.median(xs)), 4) if xs else None
width = [dict(series=s, cell=nm, rows=len(xs), median_width_over_settle=med(xs)) for s in SERIES for nm, a, b in LEADS[1:]
         for xs in [[(r['upper'] - r['lower']) / r['settle'] for r in rows if r['series'] == s and a <= r['lead'] <= b and r['settle'] and r['lower'] is not None and r['upper'] is not None]]]
issues_used = sorted({r['issue'] for r in rows}, key=lambda i: next(x['released'] for x in releases if x['issue'] == i))

# ---------------- 7. plan seal and output ----------------
seal_f = 'data/plan_seal.json'
def g(*a): return subprocess.run(['git'] + list(a), cwd=H, capture_output=True, text=True).stdout.strip()
if not os.path.exists(seal_f) and K.plan_committed('PLAN.md', NOW):
    json.dump(dict(plan_commit=g('log', '-1', '--format=%H', '--', 'PLAN.md'), plan_commit_time=g('log', '-1', '--format=%cI', '--', 'PLAN.md'),
                   plan_sha256=hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest(), first_comparison=STAMP), open(seal_f, 'w'), indent=1)
seal = json.load(open(seal_f)) if os.path.exists(seal_f) else None
def fc_row(c):
    return dict(kind='coverage', item='%s, stated %s ahead' % (SNAME[c['series']], c['cell'].replace(' months', ' months').replace('all leads', 'any number of months')),
                counts='share of monthly average spot prices inside the stated interval', stated=LEVEL, n=c['inside'], of=c['scored'], delivered=c['share'], lo=c['lo'], hi=c['hi'],
                outcome=c['outcome'], interval='moving-block bootstrap over outcome months, as the desk gives it')
# 10 Nov 2026, outside referee (steo_index_referee/REFEREE.md R4 to R7): display only, added after the data, never used for an outcome.
def _after():
    out = dict(note='Added on 10 Nov 2026 at the outside referee. Display only. No outcome uses them.')
    sens = []
    for OK in ('outcome', 'outcome_add1'):
        for s in SERIES:
            sc = [r for r in rows if r['series'] == s and r[OK] in (K.CONSISTENT, K.ABOVE, K.BELOW)]
            months = sorted({r['month'] for r in sc}); MI = {m: i for i, m in enumerate(months)}
            num = np.zeros(len(months)); den = np.zeros(len(months))
            for r in sc: num[MI[r['month']]] += r[OK] == K.CONSISTENT; den[MI[r['month']]] += 1
            for bl in (6, 12, 24):
                lo, hi = boot(num, den, draws(len(months), block=bl)) if sc else (None, None)
                sens.append(dict(reading='plan' if OK == 'outcome' else 'addendum1', series=s, block_months=bl, lo=None if lo is None else round(lo, 4), hi=None if hi is None else round(hi, 4),
                                 outcome=cell_outcome(lo, hi, len(sc), len(months)) if GATE else K.CANNOT_TELL))
    out['block_sensitivity'] = sens
    wb = [r for r in rows if r['series'] == 'WTI' and r['outcome'] == K.BELOW]
    out['wti_plan_below_by_year'] = dict(C.Counter(r['month'][:4] for r in wb))
    out['wti_plan_below_nov2014_feb2016'] = sum(1 for r in wb if '2014-11' <= r['month'] <= '2016-02')
    out['issues_released_in_span'] = sum(1 for x in releases if issues_used and next(y['released'] for y in releases if y['issue'] == issues_used[0]) <= x['released'] <= next(y['released'] for y in releases if y['issue'] == issues_used[-1]))
    out['issues_with_workbook'] = len(by_issue)
    lvl = C.defaultdict(list)
    for r in rows:
        if r['level'] is None: lvl[r['series']].append(r['issue'])
    out['issues_without_level_cell'] = {s: sorted(set(v), key=lambda i: next(x['released'] for x in releases if x['issue'] == i)) for s, v in lvl.items()}
    out['plan_addendum_commit'] = g('log', '-1', '--format=%h %cI', '--', 'PLAN.md'); out['plan_sha256_now'] = hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest()
    return out
summary = dict(desk='STEO', publisher='Heuremen LLC', generated=STAMP, plan='PLAN.md', plan_seal=seal, plan_unchanged_since_commit=K.plan_committed('PLAN.md'),
    claim=dict(source='EIA Short-Term Energy Outlook chart gallery, 95% NYMEX futures price confidence interval', stated='Lower and Upper by month at level 0.95', delivered='EIA monthly average spot price, WTI Cushing (RWTC) and Henry Hub (RNGWHHD)'),
    frame=dict(level=LEVEL, min_rows=MIN_ROWS, min_months=MIN_MONTHS, max_width=MAX_W, block_months=BLOCK, replicates=REPS, seed=SEED),
    gates=dict(kg, passed=GATE, same_quantity_detail=same),
    sources=dict(copies_held=len(files), copies=dict(cnt_copy), issues=len(by_issue), first_issue=issues_used[0] if issues_used else None, last_issue=issues_used[-1] if issues_used else None,
                 copies_differing_values=differ, spot_read=spot_read, spot_last_month={s: max(spot[s]) if spot[s] else None for s in SERIES}, releases_listed=len(releases), stale=STALE),
    rows=dict(total=len(rows), outcomes=dict(C.Counter(r['outcome'] for r in rows)), months_begun_at_release=begun, rows_in_copies_with_unknown_issue=bad_issue_rows),
    cells=cells, cells_addendum1=cells_add1, addendum1=dict(note='PLAN.md Addendum 1, decided after the data: a sheet with no level cell takes 0.95 when the issue PDF labels the bounds 95% NYMEX. Shown beside the primary reading.',
        rows_level_from_pdf=sum(1 for r in rows if r['level_from'] == 'pdf legend'), issues_level_from_pdf=len({r['issue'] for r in rows if r['level_from'] == 'pdf legend'}),
        pdf_missing_or_unlabelled=sorted({r['issue'] for r in rows if r['level'] is None and r['level_from'] is None})),
    described=dict(width=width),
    after_data=_after())
summary['forecasters'] = dict(rows=[fc_row(c) for c in cells if c['lo'] is not None])
json.dump(dict(generated=STAMP, rows=rows, copies=[{k: v for k, v in cp.items() if k != 'sheets'} for cp in copies]), open('data/steo.json.tmp', 'w')); os.replace('data/steo.json.tmp', 'data/steo.json')
json.dump(summary, open('summary_steo.json.tmp', 'w'), indent=1); os.replace('summary_steo.json.tmp', 'summary_steo.json')
json.dump(dict(summary, updated=STAMP), open('data/steo_live.json.tmp', 'w'), separators=(',', ':')); os.replace('data/steo_live.json.tmp', 'data/steo_live.json')
if PUB:
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    p = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'steo_live', '--path', os.path.join(H, 'data', 'steo_live.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'],
                       cwd=os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door'), env=env, capture_output=True, text=True)
    log('steo_live', 'published' if p.returncode == 0 else 'publish FAILED ' + (p.stderr or '')[-200:])
    if p.returncode: STALE.append('publish')
with open('data/steo_history.jsonl', 'a') as f: f.write(json.dumps(dict(t=STAMP, gate=GATE, rows=len(rows), cells=[(c['series'], c['cell'], c['scored'], c['inside'], c['outcome']) for c in cells], stale=STALE)) + '\n')
log('gates', kg, same, 'copies', dict(cnt_copy), 'issues', len(by_issue), 'rows', len(rows), 'differ', differ)
for c in cells + cells_add1: log('%-3s %-18s scored %4d inside %4d above %3d below %3d ct %3d nr %3d months %3d [%s, %s] %s' % (c['series'], c['cell'], c['scored'], c['inside'], c['above'], c['below'], c['cannot_tell'], c['nothing_returned'], c['months'], c['lo'], c['hi'], c['outcome']))
