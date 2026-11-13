"""Referee: independent stated-side recount for every report the pipeline read (file choice taken from sources.json,
values parsed with the referee's own readers). Output: out/stated_all.json"""
import sys, os, json, re, io, csv, zipfile, xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rep, myxls
DSA = '/Users/heuremen/bones-forge/social_index/dsa'

def xlsx_rows(data, sheetname):
    z = zipfile.ZipFile(io.BytesIO(data)); ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', ns):
            ss.append(''.join(t.text or '' for t in si.iter('{%s}t' % ns['m'])))
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rm = {r.get('Id'): r.get('Target') for r in rels}
    for sh in wb.find('m:sheets', ns):
        if sh.get('name') != sheetname: continue
        tgt = rm[sh.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/')
        tgt = tgt if tgt.startswith('xl/') else 'xl/' + tgt
        out = []
        for row in ET.fromstring(z.read(tgt)).iter('{%s}row' % ns['m']):
            cells = {}
            for c in row.findall('m:c', ns):
                ref = c.get('r'); col = 0
                for ch in re.match(r'[A-Z]+', ref).group(0): col = col * 26 + ord(ch) - 64
                v = c.find('m:v', ns); t = c.get('t')
                if t == 's' and v is not None: val = ss[int(v.text)]
                elif t == 'inlineStr': val = ''.join(x.text or '' for x in c.iter('{%s}t' % ns['m']))
                else: val = v.text if v is not None else ''
                cells[col - 1] = val or ''
            out.append([cells.get(i, '') for i in range(max(cells) + 1)] if cells else [])
        return out
    raise KeyError(sheetname)

def num(s):
    if isinstance(s, float): return int(s) if s == int(s) else s
    t = (s or '').strip().replace(',', '').replace('\xa0', '').replace(' ', '')
    if re.fullmatch(r'-?\d+(\.0+)?', t): return int(float(t))
    return None

def load_sheet(svc_dir, container, member):
    base = os.path.join(DSA, svc_dir)
    parts = container.split('!')
    path = os.path.join(base, parts[0])
    if len(parts) == 1:
        low = path.lower()
        if low.endswith('.csv'): return rep.rows(open(path, 'rb').read())
        if low.endswith('.xlsx'): return xlsx_rows(open(path, 'rb').read(), member)
        if low.endswith('.xls'):
            wbk = myxls.read_xls(path); return myxls.rows_of(wbk[member])
    data = open(path, 'rb').read()
    for p in parts[1:]:
        z = zipfile.ZipFile(io.BytesIO(data)); data = z.read(p)
    if parts[-1].lower().endswith('.csv'): return rep.rows(data)
    if parts[-1].lower().endswith('.xlsx'): return xlsx_rows(data, member)
    raise ValueError(container)

def norm(s): return re.sub(r'\s+', ' ', str(s or '')).strip().lower()

def hdr_idx(rows, word):
    for i, r in enumerate(rows[:15]):
        if any(norm(c).startswith(word) for c in r): return i
    return 0

def col(hdr, name):
    h = [norm(c) for c in hdr]
    for j, c in enumerate(h):
        if c == name: return j
    for j, c in enumerate(h):
        if c.startswith(name): return j
    return None

def total_row(rows, catcol, svc_words, svccol):
    for r in rows:
        if len(r) > catcol and norm(r[catcol]) == 'total':
            if svccol is not None and len(r) > svccol and r[svccol].strip() and svc_words and not any(w in norm(r[svccol]) or norm(r[svccol]) in w for w in svc_words): continue
            return r
    return None

if __name__ == '__main__':
    srcs = json.load(open(os.path.join(DSA, 'data', 'sources.json')))
    out = {}
    for s in srcs:
        if s.get('status') != 'read': continue
        svc, per = s['service'], s['period']; sh = s['sheets']; res = {}
        words = [norm(svc), norm(svc).split()[0]]
        try:
            # sheet 8
            rows = load_sheet(s['dir'], sh['8']['container'], sh['8']['member'])
            hi = hdr_idx(rows, 'indicator'); hdr = rows[hi]
            ii, sc, vi, si = col(hdr, 'indicator'), col(hdr, 'scope'), col(hdr, 'value'), col(hdr, 'service')
            for r in rows[hi + 1:]:
                if len(r) <= max(ii, sc, vi): continue
                if si is not None and r[si].strip() and not any(w in norm(r[si]) or norm(r[si]) in w for w in words + ['snap', 'xvideos', 'xnxx', 'app store']): continue
                if norm(r[sc]) not in ('total number', 'total'): continue
                ind = norm(r[ii])
                if ind.startswith('number of measures solely taken by automated means') and 'solely' not in res: res['solely'] = num(r[vi])
                if ind.startswith('number of measures not taken by automated means') and 'not' not in res: res['not'] = num(r[vi])
            for k, key in (('5', 'own_illegal'), ('6', 'own_tc')):
                rows = load_sheet(s['dir'], sh[k]['container'], sh[k]['member'])
                hi = hdr_idx(rows, 'applicability'); hdr = rows[hi]
                ci = col(hdr, 'category'); fi = col(hdr, "number of measures taken at the provider's own initiative"); gi = col(hdr, 'number of measures taken after detection')
                si = col(hdr, 'service')
                r = total_row(rows[hi + 1:], ci, words + ['snap', 'xvideos', 'xnxx', 'app store'], si)
                cols = {}
                for j, h in enumerate(hdr):
                    hn = norm(h)
                    if hn.startswith(('visibility restriction', 'monetary restriction', 'provision of the service', 'account restriction')):
                        cols[h.strip()] = num(r[j]) if r is not None and j < len(r) else None
                res[key] = num(r[fi]) if r is not None and len(r) > fi else None
                res[key.replace('own', 'own_auto')] = num(r[gi]) if r is not None and gi is not None and len(r) > gi else None
                res['cols_' + k] = cols
            rows = load_sheet(s['dir'], sh['4']['container'], sh['4']['member'])
            hi = hdr_idx(rows, 'applicability'); hdr = rows[hi]
            ci = col(hdr, 'category'); si = col(hdr, 'service')
            r = total_row(rows[hi + 1:], ci, words + ['snap', 'xvideos', 'xnxx', 'app store'], si)
            for key, name in (('notices', 'number of notices received'), ('tf_notices', 'number of notices received from trusted flaggers'),
                              ('items', 'number of specific items of information included in the total number of notices'),
                              ('L', 'number of actions taken on the basis of the law'), ('M', 'number of actions taken on the basis of the law (trusted flagger notices)'),
                              ('N', 'number of actions taken on the basis of the terms and conditions of the service'), ('O', 'number of actions taken on the basis of the terms and conditions of the service (trusted flagger notices)')):
                j = col(hdr, name)
                if key == 'notices': j = next((jj for jj, h in enumerate(hdr) if norm(h) == 'number of notices received'), j)
                if key == 'items': j = next((jj for jj, h in enumerate(hdr) if norm(h) == 'number of specific items of information included in the total number of notices'), j)
                if key == 'L': j = next((jj for jj, h in enumerate(hdr) if norm(h) == 'number of actions taken on the basis of the law'), j)
                if key == 'N': j = next((jj for jj, h in enumerate(hdr) if norm(h) == 'number of actions taken on the basis of the terms and conditions of the service'), j)
                res[key] = num(r[j]) if r is not None and j is not None and len(r) > j else None
        except Exception as e:
            res['error'] = '%s: %s' % (type(e).__name__, e)
        out['%s|%s' % (svc, per)] = res
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'stated_all.json'), 'w'), indent=1)
    print(len(out), 'reports')
