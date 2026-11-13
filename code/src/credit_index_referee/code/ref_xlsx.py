"""Minimal xlsx reader (zipfile + ElementTree). Returns rows of the first sheet as lists of strings."""
import zipfile, re
import xml.etree.ElementTree as ET

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

def col_idx(ref):
    letters = re.match(r'[A-Z]+', ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1

def sheets(path):
    with zipfile.ZipFile(path) as z:
        wb = ET.fromstring(z.read('xl/workbook.xml'))
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rmap = {r.get('Id'): r.get('Target') for r in rels}
        out = []
        for s in wb.find('m:sheets', NS):
            rid = s.get('{%s}id' % NS['r'])
            t = rmap[rid]
            t = t.lstrip('/')
            if not t.startswith('xl/'):
                t = 'xl/' + t
            out.append((s.get('name'), t))
        return out

def read(path, sheet_index=0):
    with zipfile.ZipFile(path) as z:
        ss = []
        if 'xl/sharedStrings.xml' in z.namelist():
            root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in root.findall('m:si', NS):
                ss.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
        name, target = sheets(path)[sheet_index]
        root = ET.fromstring(z.read(target))
        rows = []
        for row in root.iter('{%s}row' % NS['m']):
            vals = {}
            for c in row.findall('m:c', NS):
                t = c.get('t')
                v = c.find('m:v', NS)
                if t == 's':
                    val = ss[int(v.text)] if v is not None else ''
                elif t == 'inlineStr':
                    val = ''.join(x.text or '' for x in c.iter('{%s}t' % NS['m']))
                elif t == 'b':
                    val = ('TRUE' if v is not None and v.text == '1' else 'FALSE')
                else:
                    val = v.text if v is not None else ''
                vals[col_idx(c.get('r'))] = val
            if vals:
                mx = max(vals)
                rows.append([vals.get(i, '') for i in range(mx + 1)])
        return name, rows
