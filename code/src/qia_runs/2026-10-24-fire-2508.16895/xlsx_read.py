"""xlsx_read.py -- stdlib-only reader for .xlsx sheets (zip + XML). Reads data only; executes nothing from the file."""
import zipfile, re, sys, xml.etree.ElementTree as ET
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main', 'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def col_idx(ref):
    s = re.match(r'[A-Z]+', ref).group(); n = 0
    for ch in s: n = n * 26 + ord(ch) - 64
    return n - 1
def read(path):
    z = zipfile.ZipFile(path); names = z.namelist()
    ss = []
    if 'xl/sharedStrings.xml' in names:
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS):
            ss.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    wb = ET.fromstring(z.read('xl/workbook.xml')); rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rmap = {r.get('Id'): r.get('Target') for r in rels}
    out = {}
    for sh in wb.find('m:sheets', NS):
        tgt = rmap[sh.get('{%s}id' % NS['r'])]; tgt = tgt.lstrip('/'); tgt = tgt if tgt.startswith('xl/') else 'xl/' + tgt
        rows = []
        for row in ET.fromstring(z.read(tgt)).iter('{%s}row' % NS['m']):
            r = {}
            for c in row.findall('m:c', NS):
                v = c.find('m:v', NS); t = c.get('t'); val = None
                if t == 's' and v is not None: val = ss[int(v.text)]
                elif t == 'inlineStr': val = ''.join(x.text or '' for x in c.iter('{%s}t' % NS['m']))
                elif v is not None:
                    try: val = float(v.text)
                    except ValueError: val = v.text
                r[col_idx(c.get('r'))] = val
            rows.append([r.get(i) for i in range(max(r) + 1)] if r else [])
        out[sh.get('name')] = rows
    return out
if __name__ == '__main__':
    d = read(sys.argv[1])
    for k, rows in d.items():
        print('SHEET', k, len(rows), 'rows')
        for r in rows[:int(sys.argv[2]) if len(sys.argv) > 2 else 4]: print('  ', [str(x)[:60] for x in r[:12]])
