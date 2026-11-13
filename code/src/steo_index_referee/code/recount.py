# Referee recount. Shares nothing with desk code. Run with steo_index/venv/bin/python -I (xlrd only for .xls files).
import re, json, glob, os, zipfile, datetime as DT, math, collections as C
import xml.etree.ElementTree as ET
D = '/Users/heuremen/bones-forge/steo_index/data/'
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def col2n(s):
    n = 0
    for ch in s: n = n*26 + ord(ch)-64
    return n
def read_xlsx(p):
    z = zipfile.ZipFile(p)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).iter(NS+'si'):
            ss.append(''.join(t.text or '' for t in si.iter(NS+'t')))
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rid = {r.get('Id'): r.get('Target') for r in rels}
    out = {}
    for sh in wb.iter(NS+'sheet'):
        t = rid[sh.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/')
        t = t if t.startswith('xl/') else 'xl/'+t
        cells = {}
        for c in ET.fromstring(z.read(t)).iter(NS+'c'):
            m = re.match(r'([A-Z]+)(\d+)', c.get('r')); ty = c.get('t')
            v = c.find(NS+'v')
            if ty == 'inlineStr':
                val = ''.join(x.text or '' for x in c.iter(NS+'t'))
            elif v is None: continue
            elif ty == 's': val = ss[int(v.text)]
            elif ty in ('str', 'e', 'b'): val = v.text
            else:
                try: val = float(v.text)
                except: val = v.text
            cells[(int(m.group(2)), col2n(m.group(1)))] = val
        out[sh.get('name')] = cells
    return out
def read_xls(p):
    import xlrd
    b = xlrd.open_workbook(p); out = {}
    for sh in b.sheets():
        cells = {}
        for r in range(sh.nrows):
            for c in range(sh.ncols):
                ty = sh.cell_type(r, c)
                if ty in (0, 6): continue
                cells[(r+1, c+1)] = '#ERR%s' % sh.cell_value(r, c) if ty == 5 else sh.cell_value(r, c)
        out[sh.name] = cells
    return out
def serial_ym(v):
    if not isinstance(v, (int, float)) or v < 30000 or v > 70000: return None
    d = DT.date(1899, 12, 30) + DT.timedelta(days=int(v)); return (d.year, d.month)
MONTHS = ['january','february','march','april','may','june','july','august','september','october','november','december']
def note_date(txt):
    m = re.search(r'trading days ending\s+([A-Za-z]+)\.?\s*(\d{1,2}),?\s*(\d{4})', txt)
    if not m: return None
    mo = [i for i, n in enumerate(MONTHS) if n.startswith(m.group(1).lower()[:3])]
    return DT.date(int(m.group(3)), mo[0]+1, int(m.group(2))) if mo else None
def parse_sheet(cells):
    """Find interval table. Returns None if none."""
    hdr = [k for k, v in cells.items() if isinstance(v, str) and v.strip() == 'Lower']
    if not hdr: return None
    r0, cl = sorted(hdr)[0]
    up = [k for k, v in cells.items() if k[0] == r0 and isinstance(v, str) and v.strip() == 'Upper']
    mo = [k for k, v in cells.items() if k[0] == r0 and isinstance(v, str) and v.strip() == 'Month']
    if not up or not mo: return None
    cu, cm = up[0][1], mo[0][1]
    txt = [str(v) for v in cells.values() if isinstance(v, str)]
    if not any('Confidence' in t or 'confidence' in t for t in txt): return None
    rows = {}
    for (r, c), v in cells.items():
        if c == cm and r > r0:
            ym = serial_ym(v)
            if ym: rows[ym] = (cells.get((r, cl)), cells.get((r, cu)), r)
    note = next((t for t in txt if 'trading days ending' in t), None)
    title = next((t for t in txt if re.match(r'\s*Short-Term Energy Outlook,', t)), None)
    lab = ' | '.join(t for t in txt if re.search(r'WTI|West Texas|Henry Hub', t))[:200]
    lvl = [v for (r, c), v in cells.items() if isinstance(v, float) and abs(v-0.95) < 1e-12 and r < r0+3]
    lvlcells = [(k, v) for k, v in cells.items() if isinstance(v, float) and v == 0.95]
    lv=[v for (r, c), v in cells.items() if r0-8 <= r < r0 and isinstance(v, float) and 0 < v <= 1]
    return dict(level=(lv[0] if lv else None), rows=rows, note=note, title=title, lab=lab, has_level=bool(lvlcells), nlvl=len(lvlcells), r0=r0)
def series_of(name, s):
    L = s['lab']
    if 'Henry Hub' in L: return 'HH'
    if re.search(r'WTI|West Texas', L): return 'WTI'
    return None
# release table: own parser, all <tr>
def releases():
    h = open(D+'raw/terms/archive_index_outlook.html', encoding='utf8', errors='replace').read()
    out = []
    for tr in re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', h):
        tds = re.findall(r'(?is)<td[^>]*>(.*?)</td>', tr)
        if len(tds) < 2: continue
        t0 = re.sub(r'<[^>]+>', '', tds[0]).strip(); t1 = re.sub(r'<[^>]+>', '', tds[1]).strip()
        m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})$', t1)
        mm = re.match(r'([A-Za-z]+)\s+(\d{4})$', t0)
        if m and mm:
            pdf = re.search(r'archives/([a-z]{3}\d\d)\.pdf', tr)
            out.append((DT.date(int(m.group(3)), int(m.group(1)), int(m.group(2))), t0, pdf.group(1) if pdf else None))
    return sorted(out)
def spot(fn):
    import xlrd
    b = xlrd.open_workbook(D+'raw/spot/'+fn); sh = b.sheet_by_name('Data 1'); o = {}
    for r in range(sh.nrows):
        ym = serial_ym(sh.cell_value(r, 0)); v = sh.cell_value(r, 1)
        if ym and isinstance(v, float): o[ym] = v
    return o
def main():
    REL = releases()
    relmap = {}
    for d, name, pdf in REL: relmap[d] = (name, pdf)
    dates = [d for d, _, _ in REL]
    SP = {'WTI': spot('RWTCm.xls'), 'HH': spot('RNGWHHDm.xls')}
    copies = []
    for f in sorted(glob.glob(D+'raw/wayback/cg_*.xls*')):
        ts = re.search(r'cg_(\d{14})_', f).group(1)
        cap = DT.date(int(ts[:4]), int(ts[4:6]), int(ts[6:8]))
        try: sh = read_xlsx(f) if f.endswith('x') else read_xls(f)
        except Exception as e: copies.append(dict(file=os.path.basename(f), err=repr(e))); continue
        found = {}; nd = None; tit = None
        for nm, cells in sh.items():
            s = parse_sheet(cells)
            if not s: continue
            ser = series_of(nm, s)
            if ser is None: ser = {'Fig1': 'WTI', '1': 'WTI', 'Fig4': 'HH', '4': 'HH'}.get(nm)
            if ser and ser not in found: found[ser] = dict(s, sheet=nm)
            nd = nd or note_date(s['note'] or ''); tit = tit or s['title']
        rel = next((d for d in dates if nd and d > nd), None)
        copies.append(dict(file=os.path.basename(f), ts=ts, cap=cap, nd=nd, rel=rel, title=tit, sheets=found))
    return REL, SP, copies
if __name__ == '__main__':
    REL, SP, copies = main()
    print(len(REL), 'releases', REL[0], REL[-1])
    for c in copies:
        if 'err' in c: print('ERR', c); continue
        print(c['file'][:24], c['cap'], c['nd'], c['rel'], sorted(c['sheets']), (c['title'] or '')[:45], [(k, v['has_level'], v['nlvl']) for k, v in c['sheets'].items()])
