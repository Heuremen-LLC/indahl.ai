"""water_24ms.py: reads Reclamation's 24-Month Study reports for WATER (see PLAN.md).
Catalog from RISE record 6331, values from the report text (Lake Powell and Hoover Dam - Lake Mead operations tables)
and from Reclamation's HDB model table by the Model Run ID the report prints. Public sources, no key. Read-only on the network."""
import os, re, json, time, urllib.request, urllib.parse
H = os.path.dirname(os.path.abspath(__file__))
UA = 'heuremen-water/0.1 (+https://indahl.ai/water)'
RISE = 'https://data.usbr.gov/rise/api/'
HDB = 'https://www.usbr.gov/pn-bin/hdb/hdb.pl'
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
RES = {'mead': dict(name='Lake Mead', sdi=1930, svr='lchdb', lo=895.0, hi=1229.0, step=30.0),
       'powell': dict(name='Lake Powell', sdi=1928, svr='uchdb2', lo=3370.0, hi=3711.0, step=40.0)}
TITLE = re.compile(r'^\s*(' + '|'.join(MONTHS) + r')\s+(\d{4})\s+(Most Probable|Probable Minimum|Probable Maximum)\s+24-Month Study\s*(?:-\s*(\S+))?\s*$')
SCEN = {'Most Probable': 'MP', 'Probable Minimum': 'MIN', 'Probable Maximum': 'MAX'}

def http_json(url, accept='application/json', tries=3):
    err = None
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': accept}), timeout=120) as r: return json.loads(r.read())
        except Exception as e:
            err = e; time.sleep(3 * (a + 1))
    raise RuntimeError('fetch failed %s: %r' % (url, err))

def catalog(cache=os.path.join(H, 'data', 'raw', 'rise_24ms_catalog_items.jsonl'), refresh=True):
    """Every report in RISE record 6331 as dicts. Refresh reads the record and its items again and rewrites the cache."""
    if refresh:
        rec = http_json(RISE + 'catalog-record/6331', 'application/vnd.api+json')
        ids = [e['id'].split('/')[-1] for e in rec['data']['relationships']['catalogItems']['data']]
        rows = []
        for i in range(0, len(ids), 100):
            q = '&'.join('id%5B%5D=' + x for x in ids[i:i + 100])
            d = http_json(RISE + 'catalog-item?' + q + '&itemsPerPage=100', 'application/vnd.api+json'); rows += d['data']; time.sleep(1)
        if len(rows) >= 0.95 * len(ids):
            with open(cache + '.tmp', 'w') as f:
                for r in rows: f.write(json.dumps(r) + '\n')
            os.replace(cache + '.tmp', cache)
    out = []
    for l in open(cache):
        a = json.loads(l)['attributes']; m = TITLE.match(a['itemTitle'])
        if not m: out.append(dict(id=a['_id'], title=a['itemTitle'].strip(), parsed=False)); continue
        mon = MONTHS.index(m.group(1)) + 1
        out.append(dict(id=a['_id'], title=a['itemTitle'].strip(), parsed=True, issue='%s-%02d' % (m.group(2), mon), scenario=SCEN[m.group(3)],
                        variant=(m.group(4) or '').lower() or None, published=a.get('publicationFirstPublicationDate'), url=a['binaryFilePath'],
                        file=os.path.basename(a['binaryFilePath'])))
    return out

# ---------- report text ----------
MON3 = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
FIXMON = {'0ct': 'oct', 'ju1': 'jul', 'jui': 'jul', 'jun.': 'jun', 'sept': 'sep', 'n0v': 'nov', '0ec': 'dec', 'au9': 'aug', 'apt': 'apr', 'rnay': 'may', 'rnar': 'mar'}
DIG = str.maketrans({'O': '0', 'o': '0', 'D': '0', 'Q': '0', 'l': '1', 'I': '1', '|': '1', 'i': '1', 'B': '8', 'S': '5', 's': '5', 'Z': '2', 'z': '2', 'g': '9', ',': '.'})
ELEV = re.compile(r'^\d{3,4}\.\d{2}$')
MRID = re.compile(r'model\s*run\s*id\s*[:=]?\s*([0-9OoIl]{3,5})', re.I)

def _month_token(t):
    t = t.strip('.*:').lower(); t = FIXMON.get(t, t)
    return MON3.get(t[:3]) if len(t) >= 3 and t[:3] in MON3 and (len(t) == 3 or t in ('june', 'july', 'sept')) else None

def _year_token(t):
    t = t.strip('.*:').translate(DIG)
    return int(t) if re.fullmatch(r'(19|20)\d\d', t) else None

def _numeric(t):
    """Clean a token that is mostly digits. Returns the cleaned text or None."""
    if not t: return None
    d = sum(c.isdigit() for c in t)
    if d < max(1, 0.5 * len(t.replace('.', ''))): return None
    return t.translate(DIG)

def _words(page):
    """Words as (x0, y0, x1, y1, text) in the page's visual orientation, with scan skew taken out of y."""
    import pymupdf, statistics
    M = page.rotation_matrix; out = []; lines = {}
    for w in page.get_text('words'):
        if not w[4].strip(): continue
        r = pymupdf.Rect(w[:4]) * M if page.rotation else pymupdf.Rect(w[:4])
        out.append([r.x0, r.y0, r.x1, r.y1, w[4]]); lines.setdefault((w[5], w[6]), []).append(len(out) - 1)
    sl = []
    for ix in lines.values():
        if len(ix) < 2: continue
        a, b = out[ix[0]], out[ix[-1]]; dx = (b[0] + b[2]) / 2 - (a[0] + a[2]) / 2
        if dx > 40: sl.append(((b[1] + b[3]) / 2 - (a[1] + a[3]) / 2) / dx)
    k = statistics.median(sl) if sl else 0.0
    if abs(k) > 0.0015:
        for w in out:
            xc = (w[0] + w[2]) / 2; w[1] -= k * xc; w[3] -= k * xc
    return [tuple(w) for w in out]

def _candidates(doc):
    """Pages that may hold each operations table, in page order."""
    c = {'powell': [], 'mead': []}
    for i, p in enumerate(doc):
        t = p.get_text(); L = [l.strip() for l in t.split('\n') if l.strip()]
        head = ' '.join(L[:60])
        if re.search(r'(^|\n)\s*(Lake\s*)?Pow\s*e\s*l\s*l\s*(\n|$)', t) and not re.search(r'Upper Basin Power|Flood Control', head): c['powell'].append(i)   # Addendum 2: scans drop or split the heading ("Powell", "Lake Powe ll")
        if (re.search(r'Hoov\w*[:.]?\s*Da[rm]n?\b', t) or re.search(r'Lake\s*Mead', t)) and not re.search(r'Change.?In|Static|Generator', head): c['mead'].append(i)
    return c

def _pages(doc):
    """Index of the Lake Powell and Hoover Dam - Lake Mead operations pages: the first candidate page with at least 12 dated rows carrying an elevation in the reservoir's range."""
    found = {}; c = _candidates(doc)
    for key, pages in c.items():
        R = RES[key]
        for i in pages:
            rows = _rows(doc[i])
            good = sum(1 for _, vals in rows if any(R['lo'] <= float(v) <= R['hi'] for v in vals))
            if good >= 12: found[key] = i; break
    return found

def _rows(page):
    """(target 'YYYY-MM', [elevation-shaped values]) for every dated row of an operations table page."""
    W = _words(page)
    dates = []
    for i, w in enumerate(W):
        m = _month_token(w[4]); y = None
        if m is None:
            mm = re.fullmatch(r'([A-Za-z0-9]{3})\.?((?:19|20|l9|2O|1 9)[0-9OIl]{2})', w[4].strip('*'))   # merged "Apr2010"
            if mm and _month_token(mm.group(1)) and _year_token(mm.group(2)): dates.append((w, _month_token(mm.group(1)), _year_token(mm.group(2))))
            continue
        cands = [v for v in W if v is not w and abs((v[1] + v[3]) / 2 - (w[1] + w[3]) / 2) < 0.6 * (w[3] - w[1]) and 0 <= v[0] - w[2] < 25]
        cands.sort(key=lambda v: v[0])
        for v in cands:
            y = _year_token(v[4])
            if y: break
        if y: dates.append((w, m, y))
    if not dates: return []
    hs = sorted(d[0][3] - d[0][1] for d in dates); h = hs[len(hs) // 2]
    out = []
    for w, m, y in dates:
        yc = (w[1] + w[3]) / 2
        row = sorted([v for v in W if abs((v[1] + v[3]) / 2 - yc) < 0.55 * h and v[0] > w[2]], key=lambda v: v[0])
        toks = []   # join split numbers: "1140" ".39", "1140." "39", "1140" "." "39", and touching pieces such as "1" "083.57"
        k = 0
        numish = lambda s: s in ('.', ',') or _numeric(s) is not None
        while k < len(row):
            t = row[k][4]; x1 = row[k][2]
            while k + 1 < len(row):
                nx = row[k + 1]; gap = nx[0] - x1
                dec = gap < 7 and (re.fullmatch(r'[.,][0-9OoIlBS]{1,2}', nx[4]) or t.endswith('.') or t.endswith(',') or nx[4] in ('.', ','))
                touch = gap < 2.5 and numish(t) and numish(nx[4])
                if not (dec or touch): break
                k += 1; t += nx[4]; x1 = nx[2]
            toks.append(t); k += 1
        vals = [c for c in (_numeric(t) for t in toks) if c and ELEV.fullmatch(c)]
        out.append(('%04d-%02d' % (y, m), vals))
    return out

def read_text(pdf_path):
    """Values a report prints: {'mrids': [...], 'mead': {month: [candidates]}, 'powell': {...}, 'pages': {...}}."""
    import pymupdf
    doc = pymupdf.open(pdf_path); res = {'mrids': [], 'pages': {}}
    ids = []
    for p in doc:
        for m in MRID.finditer(p.get_text()): ids.append(m.group(1).translate(DIG))
    res['mrids'] = sorted(set(ids), key=ids.count, reverse=True)
    pg = _pages(doc); res['pages'] = pg
    for key in RES:
        res[key] = {}
        if key not in pg: continue
        for month, vals in _rows(doc[pg[key]]):
            res[key].setdefault(month, []).extend(vals)
    return res

def pick(res, key):
    """One value per printed month: the single candidate inside the reservoir range, else None. Then the neighbour rule of PLAN.md."""
    R = RES[key]; months = sorted(res.get(key, {})); val = {}
    for mo in months:
        c = [float(v) for v in res[key][mo] if R['lo'] <= float(v) <= R['hi']]
        val[mo] = c[0] if len(set(c)) == 1 else None
    def nb(mo, d):
        y, m = int(mo[:4]), int(mo[5:]); m += d; y += (m - 1) // 12; m = (m - 1) % 12 + 1; return '%04d-%02d' % (y, m)
    kept = {}
    for mo in months:
        v = val[mo]
        if v is None: kept[mo] = None; continue
        ok = True
        for d in (-1, 1):
            w = val.get(nb(mo, d))
            if w is not None and abs(v - w) >= R['step']: ok = False
        kept[mo] = v if ok else None
    return kept

# ---------- HDB ----------
def hdb_series(key, table='R', tstp='MN', t1='1935-01-01T00:00', t2=None, mrid=0):
    R = RES[key]; t2 = t2 or time.strftime('%Y-%m-%dT00:00', time.gmtime(time.time() + 40 * 86400))
    q = urllib.parse.urlencode(dict(svr=R['svr'], sdi=R['sdi'], tstp=tstp, t1=t1, t2=t2, table=table, mrid=mrid, format='json'))
    d = http_json(HDB + '?' + q)
    out = {}
    for x in d['Series'][0]['Data']:
        if x['v'] == '': continue
        mo, dd, yy = x['t'].split(' ')[0].split('/')
        k = '%s-%02d' % (yy, int(mo)) if tstp == 'MN' else '%s-%02d-%02d' % (yy, int(mo), int(dd))
        if tstp == 'HR':
            hh = x['t'].split(' ')[1]; ap = x['t'].split(' ')[2]; hr = int(hh.split(':')[0]) % 12 + (12 if ap == 'PM' else 0); k += 'T%02d' % hr
        out[k] = float(x['v'])
    return out

def hdb_model(key, mrid, t1, t2):
    return hdb_series(key, table='M', tstp='MN', t1=t1, t2=t2, mrid=mrid)
