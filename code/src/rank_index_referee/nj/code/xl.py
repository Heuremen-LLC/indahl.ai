"""Referee's own minimal xlsx reader (zipfile + iterparse). Shares nothing with the desk code."""
import re, sys, zipfile
import xml.etree.ElementTree as ET

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RNS = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'


def _col(ref):
    m = re.match(r'([A-Z]+)', ref)
    n = 0
    for ch in m.group(1):
        n = n * 26 + ord(ch) - 64
    return n - 1


def sheets(path):
    z = zipfile.ZipFile(path)
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rmap = {r.get('Id'): r.get('Target') for r in rels}
    out = []
    for s in wb.iter(NS + 'sheet'):
        t = rmap[s.get(RNS + 'id')]
        t = t.lstrip('/')
        if not t.startswith('xl/'):
            t = 'xl/' + t
        out.append((s.get('name'), t))
    return z, out


def shared(z):
    try:
        data = z.open('xl/sharedStrings.xml')
    except KeyError:
        return []
    ss = []
    for ev, el in ET.iterparse(data):
        if el.tag == NS + 'si':
            ss.append(''.join(t.text or '' for t in el.iter(NS + 't')))
            el.clear()
    return ss


def rows(path, sheet=None, keep=None):
    """Yield (sheet_name, row_number, [values]). keep(values)->bool filters early."""
    z, sh = sheets(path)
    ss = shared(z)
    for name, target in sh:
        if sheet and name != sheet:
            continue
        for ev, el in ET.iterparse(z.open(target)):
            if el.tag == NS + 'row':
                r = int(el.get('r'))
                vals = {}
                for c in el.iter(NS + 'c'):
                    t = c.get('t')
                    v = c.find(NS + 'v')
                    if t == 'inlineStr':
                        x = ''.join(tt.text or '' for tt in c.iter(NS + 't'))
                    elif v is None:
                        x = ''
                    elif t == 's':
                        x = ss[int(v.text)]
                    else:
                        x = v.text
                    vals[_col(c.get('r'))] = x
                el.clear()
                if vals:
                    arr = [''] * (max(vals) + 1)
                    for k, x in vals.items():
                        arr[k] = x
                    if keep is None or keep(arr) or r <= 6:
                        yield name, r, arr


if __name__ == '__main__':
    for name, r, a in rows(sys.argv[1]):
        if r <= int(sys.argv[2] if len(sys.argv) > 2 else 5):
            print(name, r, a)
