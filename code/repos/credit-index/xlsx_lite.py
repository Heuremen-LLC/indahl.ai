"""xlsx_lite.py: read the sheets of an .xlsx file with the standard library only (zipfile + xml). Returns rows of cell text (strings) by sheet name."""
import zipfile, re, xml.etree.ElementTree as ET
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main', 'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def _col(ref):
    n = 0
    for ch in re.match(r'[A-Z]+', ref).group(0): n = n * 26 + ord(ch) - 64
    return n - 1
def sheets(path):
    z = zipfile.ZipFile(path); ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS): ss.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    wb = ET.fromstring(z.read('xl/workbook.xml')); rel = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    tgt = {r.get('Id'): r.get('Target') for r in rel}
    out = {}
    for s in wb.find('m:sheets', NS):
        t = tgt[s.get('{%s}id' % NS['r'])].lstrip('/'); t = t if t.startswith('xl/') else 'xl/' + t
        rows = []
        for row in ET.fromstring(z.read(t)).iter('{%s}row' % NS['m']):
            cells = {}
            for c in row.findall('m:c', NS):
                v = c.find('m:v', NS); typ = c.get('t')
                if typ == 'inlineStr': val = ''.join(x.text or '' for x in c.iter('{%s}t' % NS['m']))
                elif v is None: val = ''
                elif typ == 's': val = ss[int(v.text)]
                else: val = v.text
                cells[_col(c.get('r'))] = val
            rows.append([cells.get(i, '') for i in range(max(cells) + 1)] if cells else [])
        out[s.get('name')] = rows
    return out
