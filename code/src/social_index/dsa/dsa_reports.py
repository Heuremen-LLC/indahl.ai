"""dsa_reports.py: stated side of SOCIAL section 1 (see PLAN.md). Reads harmonised DSA transparency reports (Implementing Regulation
(EU) 2024/2835 template) from zip/CSV/XLSX files and returns the stated values the plan names, each with its verbatim row.
Standard library only. Run with python3 -I. Reads untrusted files; never executes anything from them."""
import os, re, io, csv, json, zipfile, hashlib, xml.etree.ElementTree as ET

SHEETS = {'1': r'(?:^|[^0-9])1[ _.\-]*report[ _]*identification', '3': r'(?:^|[^0-9])3[ _.\-]*member[ _]*states?(?:[ _]*orders?)?(?![a-z])',
          '4': r'(?:^|[^0-9])4[ _.\-]*(?:article[ _]*16[ _]*)?notices', '5': r'(?:^|[^0-9])5[ _.\-]*own[ _\-]*initiative[ _]*il',
          '6': r'(?:^|[^0-9])6[ _.\-]*own[ _\-]*initiative[ _]*t(?:&|and)?c(?![a-z])', '8': r'(?:^|[^0-9])8[ _.\-]*automated[ _]*means(?![ _]*ads)'}
ADS = re.compile(r'ads?(?:\.csv)?$', re.I)
SHEETS_ADS = {'8a': r'(?:^|[^0-9])8[ _.\-]*automated[ _]*means[ _]*ads$', '6a': r'(?:^|[^0-9])6[ _.\-]*own[ _\-]*initiative[ _]*t(?:&|and)?c[ _]*ads$'}   # PLAN.md Addendum 6.1

def iso_date(v, mdy=False, pick=min):
    """Report dates as ISO: 2026-08-28, 2026/8/28, 2026-02-27 00:00:00, Excel serial 46081, '2026/2/28 [see Note 1]', 6/30/2026 (mdy).
    A cell holding several dates on several lines gives pick(dates)."""
    import datetime as D
    t = (v or '').strip()
    if '\n' in t:
        ds = [x for x in (iso_date(l, mdy) for l in t.splitlines()) if x]
        return pick(ds) if ds else None
    m = re.match(r'(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})', t)
    if m: return '%04d-%02d-%02d' % tuple(int(x) for x in m.groups())
    m = re.fullmatch(r'(\d{5})(?:\.0+)?', t)
    if m and 30000 < int(m.group(1)) < 60000: return (D.date(1899, 12, 30) + D.timedelta(days=int(m.group(1)))).isoformat()
    m = re.match(r'(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})', t)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        mo, d = (a, b) if mdy else (b, a)
        if mo > 12: mo, d = d, mo
        return '%04d-%02d-%02d' % (y, mo, d)
    return None

def norm(s):
    s = (s or '').replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip().lower()

def to_int(s):
    t = (s or '').strip().replace('\xa0', '').replace(' ', '').replace(',', '').replace("'", '')
    if re.fullmatch(r'-?\d+', t): return int(t)
    if re.fullmatch(r'-?\d+\.0+', t): return int(float(t))
    if re.fullmatch(r'-?\d+(\.\d+)?[eE]\+?\d+', t):   # XLSX numeric cells written as 3.8746603E7
        f = float(t)
        if f == int(f): return int(f)
    return None

# ---------- XLSX (stdlib) ----------
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main', 'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'pr': 'http://schemas.openxmlformats.org/package/2006/relationships'}
def col_index(ref):
    m = re.match(r'([A-Z]+)', ref); n = 0
    for ch in m.group(1): n = n * 26 + ord(ch) - 64
    return n - 1
def xlsx_sheets(data):
    z = zipfile.ZipFile(io.BytesIO(data)); names = z.namelist()
    ss = []
    if 'xl/sharedStrings.xml' in names:
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS):
            ss.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    wb = ET.fromstring(z.read('xl/workbook.xml')); rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rmap = {r.get('Id'): r.get('Target') for r in rels.findall('pr:Relationship', NS)}
    out = {}
    for sh in wb.find('m:sheets', NS).findall('m:sheet', NS):
        tgt = rmap[sh.get('{%s}id' % NS['r'])].lstrip('/'); tgt = tgt if tgt.startswith('xl/') else 'xl/' + tgt
        rows = []
        for row in ET.fromstring(z.read(tgt)).iter('{%s}row' % NS['m']):
            cells = {}
            for c in row.findall('m:c', NS):
                t = c.get('t'); v = c.find('m:v', NS); val = ''
                if t == 's' and v is not None: val = ss[int(v.text)]
                elif t == 'inlineStr': val = ''.join(x.text or '' for x in c.iter('{%s}t' % NS['m']))
                elif v is not None: val = v.text or ''
                if re.fullmatch(r'-?\d+\.0', val): val = val[:-2]
                cells[col_index(c.get('r'))] = val
            rows.append([cells.get(i, '') for i in range(max(cells) + 1)] if cells else [])
        out[sh.get('name')] = rows
    return out

# ---------- reading a report directory ----------
def decode(b):
    for enc in ('utf-8-sig', 'cp1252', 'latin-1'):
        try: return b.decode(enc)
        except UnicodeDecodeError: pass
def csv_rows(text):
    """Rows plus, for each row, its exact source text (records can span several physical lines)."""
    first = text.split('\n', 1)[0]
    delim = ';' if first.count(';') > first.count(',') else ','
    phys = text.split('\n'); rdr = csv.reader(io.StringIO(text, newline=''), delimiter=delim); rows, raws, prev = [], [], 0
    for row in rdr:
        rows.append(row); raws.append('\n'.join(l.rstrip('\r') for l in phys[prev:rdr.line_num])); prev = rdr.line_num
    return rows, raws

def collect(path):
    """Returns {sheet_key: dict(rows, raw_lines or None, member, container)} from a directory, zip, csv or xlsx files."""
    found = {}
    def vscore(name):
        m = re.search(r'version[ _]*(\d+)|[ _]v(\d+)(?:[ _.]|$)', name.lower())
        v = int(m.group(1) or m.group(2)) if m else 1
        return v + (0.5 if re.search(r'updated|corrected|revised', name.lower()) else 0)
    def better(k, name, when=None):
        if k not in found: return True
        a, b = vscore(name), vscore(found[k]['member'])
        if a != b: return a > b
        return (when or '') > (found[k].get('when') or '')   # tie: the later file (zip member time or file time) wins
    def consider(name, data, container, when=None):
        base = os.path.basename(name); low = base.lower()
        if '__macosx' in name.lower() or base.startswith('._'): return
        if low.endswith('.zip'):
            try:
                z = zipfile.ZipFile(io.BytesIO(data))
                for zi in z.infolist():
                    if not zi.filename.endswith('/'): consider(zi.filename, z.read(zi.filename), container + '!' + zi.filename, '%04d-%02d-%02d %02d:%02d:%02d' % zi.date_time)
            except zipfile.BadZipFile: pass
            return
        if low.endswith(('.xlsx', '.xls')):
            try:
                if low.endswith('.xlsx'): sheets = xlsx_sheets(data)
                else:
                    import xls_biff; sheets = xls_biff.xls_sheets(data)
            except Exception: return
            for sn, rows in sheets.items():
                for k, pat in SHEETS_ADS.items():
                    if re.search(pat, sn.lower().replace('.csv', '')) and (k not in found or (found[k]['kind'] != 'csv' and better(k, sn, when))): found[k] = dict(rows=rows, raw=None, member=sn, container=container, kind='xlsx' if low.endswith('.xlsx') else 'xls', when=when)
                for k, pat in SHEETS.items():
                    if re.search(pat, sn.lower()) and not ADS.search(sn.lower().replace('.csv', '')) and (k not in found or (found[k]['kind'] != 'csv' and better(k, sn, when))):
                        found[k] = dict(rows=rows, raw=None, member=sn, container=container, kind='xlsx' if low.endswith('.xlsx') else 'xls', when=when)
            return
        if low.endswith('.csv'):
            stem = low[:-4]
            for k, pat in SHEETS_ADS.items():
                if re.search(pat, stem):
                    t = decode(data); rows, lines = csv_rows(t)
                    if found.get(k, {}).get('kind') not in (None, 'csv') or better(k, name, when): found[k] = dict(rows=rows, raw=lines, member=name, container=container, kind='csv', when=when)
            for k, pat in SHEETS.items():
                if re.search(pat, stem) and not re.search(r'[_ ]ads$', stem):
                    t = decode(data); rows, lines = csv_rows(t)
                    if found.get(k, {}).get('kind') not in (None, 'csv') or better(k, name, when): found[k] = dict(rows=rows, raw=lines, member=name, container=container, kind='csv', when=when)
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith(('superseded', 'companion', 'unzipped', 'earlier'))]   # latest version only (PLAN.md)
            for f in sorted(files):
                fp = os.path.join(root, f)
                if f.lower().endswith(('.zip', '.csv', '.xlsx', '.xls')): consider(f, open(fp, 'rb').read(), os.path.relpath(fp, path), __import__('time').strftime('%Y-%m-%d %H:%M:%S', __import__('time').localtime(os.path.getmtime(fp))))
    else:
        consider(path, open(path, 'rb').read(), os.path.basename(path))
    return found

def raw_line(sheet, i):
    """Verbatim source text of data row i (CSV: the file line; XLSX: cells joined)."""
    r = sheet['rows'][i]
    if sheet['raw'] is not None and i < len(sheet['raw']):
        return sheet['raw'][i]   # verbatim source text of this CSV record
    return '%s sheet "%s" row %d: %s' % (sheet['kind'].upper(), sheet['member'], i + 1, ' | '.join(c for c in r))

def header_index(rows, must):
    for i, r in enumerate(rows[:15]):
        if any(norm(c).startswith(must) for c in r): return i
    return None

def find_col(hdr, *names):
    h = [norm(c) for c in hdr]
    for n in names:
        if n in h: return h.index(n)
    for n in names:
        for j, c in enumerate(h):
            if c.startswith(n): return j
    return None

def svc_ok(cell, want):
    c = norm(cell)
    return any(c == norm(w) or (len(c) > 2 and (norm(w) in c or c in norm(w))) for w in want if w)

def pick_service(rows, si, want):
    svcs = sorted({r[si].strip() for r in rows if len(r) > si and r[si].strip()})
    if len(svcs) <= 1: return svcs[0] if svcs else None, svcs
    m = [s for s in svcs if svc_ok(s, want)]
    return (m[0] if len(m) == 1 else None), svcs

def read_report(path, want):
    """want: names the service may appear under. Returns dict of stated values with quotes, plus identification and problems."""
    sh = collect(path); out = dict(sheets={k: dict(member=v['member'], container=v['container'], kind=v['kind'], when=v.get('when')) for k, v in sh.items()}, problems=[], values={})
    def put(key, val, sheet, i, field, note=None):
        out['values'][key] = dict(value=val, quote=raw_line(sheet, i), member=sheet['member'], container=sheet['container'], field=field, note=note)
    # 1 identification
    if '1' in sh:
        rows = sh['1']['rows']; ident = {}
        for i, r in enumerate(rows):
            for j, c in enumerate(r):
                n = norm(c)
                for key, lab in (('provider', 'name of the service provider'), ('published', 'date of the publication of the report'), ('previous', 'date of the publication of the latest previous report'),
                                 ('start', 'starting date of reporting period'), ('end', 'ending date of reporting period')):
                    if n == lab and j + 1 < len(r):
                        val = r[-1].strip() if r[-1].strip() else (r[j + 1].strip() if j + 1 < len(r) else '')
                        ident[key] = dict(value=val, iso=iso_date(val), quote=raw_line(sh['1'], i)); ident.setdefault('service', r[1].strip() if len(r) > 1 else '')
        vals_ = [x['value'] for x in ident.values() if isinstance(x, dict)]
        mdy = any(re.match(r'\d{1,2}/(1[3-9]|2\d|3[01])/\d{4}', l.strip()) for v in vals_ for l in v.splitlines())
        for key, x in ident.items():
            if isinstance(x, dict): x['iso'] = iso_date(x['value'], mdy, pick=max if key == 'end' else min)
            if isinstance(x, dict) and ('\n' in x['value'] or mdy): x['note'] = ('month/day/year dates' if mdy else '') + ('; several dates in one cell, earliest start and latest end read' if '\n' in x['value'] else '')
        out['identification'] = ident
    else: out['problems'].append('no 1_report_identification sheet')
    # 8 automated means (and the Ads template, Addendum 6.1)
    for s8, pre in (('8', ''), ('8a', 'ads_')):
      if s8 not in sh:
        if s8 == '8': out['problems'].append('no 8_automated_means sheet')
        continue
      if True:
        rows = sh[s8]['rows']; hi = header_index(rows, 'indicator') or header_index(rows, 'applicability') or 0; hdr = rows[hi]
        si, ii, sc, vi = find_col(hdr, 'service'), find_col(hdr, 'indicator'), find_col(hdr, 'scope'), find_col(hdr, 'value')
        if None in (ii, sc, vi): out['problems'].append('%s: header not read %r' % (s8, hdr[:8]))
        else:
            body = list(range(hi + 1, len(rows)))
            svc, svcs = pick_service([rows[i] for i in body], si, want) if si is not None else (None, [])
            if si is not None and len(svcs) > 1 and svc is None: out['problems'].append('%s: service not matched among %r' % (s8, svcs))
            for i in body:
                r = rows[i]
                if len(r) <= max(ii, sc, vi): continue
                if si is not None and svc and r[si].strip() != svc: continue
                ind, scope = norm(r[ii]), norm(r[sc])
                if scope not in ('total number', 'total'): continue
                snote = None if scope == 'total number' else 'scope written as %r, read as Total number' % r[sc].strip()
                for key0, lab in (('solely', 'number of measures solely taken by automated means'), ('not', 'number of measures not taken by automated means')):
                    if not ind.startswith(lab): continue
                    key = pre + key0; v = to_int(r[vi])
                    if key in out['values']:
                        if out['values'][key]['value'] != v: out['problems'].append('%s: two Total rows for %s with different values (%r, %r); the first is read' % (s8, key, out['values'][key]['value'], v))
                        continue
                    note = '; '.join(x for x in (snote, None if v is not None else 'blank or not an integer: %r' % r[vi]) if x) or None
                    put(key, v, sh[s8], i, ('Number of measures solely taken by automated means' if key0 == 'solely' else 'Number of measures not taken by automated means') + ' / Total number', note)
    # 5 and 6 own initiative
    for k, key in (('5', 'own_illegal'), ('6', 'own_tc'), ('6a', 'ads_own_tc')):
        if k not in sh:
            if k != '6a': out['problems'].append('no sheet %s' % k)
            continue
        rows = sh[k]['rows']; hi = header_index(rows, 'applicability') or 0; hdr = rows[hi]
        si = find_col(hdr, 'service'); ci = find_col(hdr, 'category of illegal content', 'category of incompatibility with the provider\'s terms and conditions', 'category')
        di = find_col(hdr, 'description of the sub-category "other"', 'description of the sub-category'); fi = find_col(hdr, "number of measures taken at the provider's own initiative")
        gi = find_col(hdr, 'number of measures taken after detection with solely automated means')
        if None in (ci, fi): out['problems'].append('%s: header not read' % k); continue
        body = list(range(hi + 1, len(rows))); svc, svcs = pick_service([rows[i] for i in body], si, want) if si is not None else (None, [])
        if si is not None and len(svcs) > 1 and svc is None: out['problems'].append('%s: service not matched among %r' % (k, svcs)); continue
        tot_i = None; cat_sum_f = 0; cat_sum_g = 0; cat_n = 0; cat_n_g = 0; spam = 0; spam_rows = []
        for i in body:
            r = rows[i]
            if len(r) <= ci or (si is not None and svc and len(r) > si and r[si].strip() != svc): continue
            cat = r[ci].strip().upper()
            fv = to_int(r[fi]) if len(r) > fi else None; gv = to_int(r[gi]) if gi is not None and len(r) > gi else None
            if cat == 'TOTAL' and tot_i is None: tot_i = i
            elif cat.startswith('STATEMENT_CATEGORY_'):
                if fv is not None: cat_sum_f += fv; cat_n += 1
                if gv is not None: cat_sum_g += gv; cat_n_g += 1
            if di is not None and len(r) > di and re.search(r'spam|high.?volume', r[di], re.I) and fv is not None:
                spam += fv; spam_rows.append(raw_line(sh[k], i))
        if tot_i is not None:
            r = rows[tot_i]; fv = to_int(r[fi]) if len(r) > fi else None; gv = to_int(r[gi]) if gi is not None and len(r) > gi else None
            rc = {}
            for j, h in enumerate(hdr):   # restriction columns H to U of the TOTAL row (PLAN.md Addendum 5)
                hn = norm(h)
                if hn.startswith(('visibility restriction', 'monetary restriction', 'provision of the service', 'account restriction')) and not hn.startswith('contextual'):
                    rc[h.strip()] = to_int(r[j]) if j < len(r) else None
            out['values']['cols_' + k] = dict(value=rc, quote=raw_line(sh[k], tot_i))
            if fv is None and cat_n: put(key, cat_sum_f, sh[k], tot_i, 'sum of STATEMENT_CATEGORY_ rows, column F', 'summed by us: TOTAL cell blank')
            else: put(key, fv, sh[k], tot_i, "TOTAL / Number of measures taken at the provider's own initiative", None if fv is not None else 'blank')
            if fv is not None and cat_n and cat_sum_f != fv: out['values'][key]['category_sum'] = cat_sum_f
            if gv is None and cat_n_g and gi is not None: put(key.replace('own', 'own_auto', 1), cat_sum_g, sh[k], tot_i, 'sum of STATEMENT_CATEGORY_ rows, column G', 'summed by us: TOTAL cell blank')
            else: put(key.replace('own', 'own_auto', 1), gv, sh[k], tot_i, 'TOTAL / Number of measures taken after detection with solely automated means', None if gv is not None else 'blank')
        else: out['problems'].append('%s: no TOTAL row' % k)
        out['values']['spam_' + k] = dict(value=spam, rows=spam_rows)
        if fv_total_check := (out['values'].get(key) or {}).get('value'):
            rcs = [v for v in ((out['values'].get('cols_' + k) or {}).get('value') or {}).values() if isinstance(v, int)]
            out['values']['colsum_equal_' + k] = bool(rcs) and sum(rcs) == fv_total_check   # Addendum 6.4: TOTAL equals the sum of columns H to U
    # 4 notices
    if '4' in sh:
        rows = sh['4']['rows']; hi = header_index(rows, 'applicability') or 0; hdr = rows[hi]
        si = find_col(hdr, 'service'); ci = find_col(hdr, 'category of illegal content', 'category')
        cols = {'notice_items': find_col(hdr, 'number of specific items of information included in the total number of notices'),
                'notice_tf_items': find_col(hdr, 'number of specific items of information included in the total number of notices by trusted flaggers (trusted flagger notices)'),
                'notice_law': find_col(hdr, 'number of actions taken on the basis of the law'), 'notice_tc': find_col(hdr, 'number of actions taken on the basis of the terms and conditions of the service'),
                'notice_tf_law': find_col(hdr, 'number of actions taken on the basis of the law (trusted flagger notices)'), 'notice_tf_tc': find_col(hdr, 'number of actions taken on the basis of the terms and conditions of the service (trusted flagger notices)')}
        body = list(range(hi + 1, len(rows))); svc, svcs = pick_service([rows[i] for i in body], si, want) if si is not None else (None, [])
        for i in body:
            r = rows[i]
            if ci is None or len(r) <= ci or (si is not None and svc and len(r) > si and r[si].strip() != svc): continue
            if r[ci].strip().upper() == 'TOTAL':
                for key, j in cols.items():
                    if j is not None and key not in out['values']: put(key, to_int(r[j]) if len(r) > j else None, sh['4'], i, 'TOTAL / ' + hdr[j].strip())
                break
    else: out['problems'].append('no 4_notices sheet')
    # 3 orders
    if '3' in sh:
        rows = sh['3']['rows']; hi = header_index(rows, 'applicability') or 0; hdr = rows[hi]
        si = find_col(hdr, 'service'); ci = find_col(hdr, 'category of illegal content', 'category'); sc = find_col(hdr, 'scope')
        j = find_col(hdr, 'number of specific items of information included in the total number of orders to act against illegal content')
        body = list(range(hi + 1, len(rows))); svc, svcs = pick_service([rows[i] for i in body], si, want) if si is not None else (None, [])
        for i in body:
            r = rows[i]
            if ci is None or j is None or len(r) <= max(ci, j): continue
            if si is not None and svc and len(r) > si and r[si].strip() != svc: continue
            if r[ci].strip().upper() == 'TOTAL' and (sc is None or norm(r[sc]) == 'total'):
                put('orders_items', to_int(r[j]), sh['3'], i, 'TOTAL / TOTAL / Number of specific items of information included in the total number of orders to act against illegal content'); break
    else: out['problems'].append('no 3_member_states_orders sheet')
    return out

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

if __name__ == '__main__':
    import sys
    print(json.dumps(read_report(sys.argv[1], sys.argv[2:]), indent=1)[:6000])
