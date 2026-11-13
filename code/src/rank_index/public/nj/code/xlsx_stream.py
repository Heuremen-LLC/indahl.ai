"""Stream sheets out of a large .xlsx without openpyxl.
usage: python3 -I xlsx_stream.py <xlsx> <outdir> <keysfile|-> sheet1 [sheet2 ...]
Writes <outdir>/<sheet>.csv with an extra first column 'xlsx_row' (1-based row number in the sheet).
If keysfile given (lines 'CC|DDDD|SSS'), keeps non-data rows (titles, notes, header) and data rows whose
cells A, C, E (County Code, District Code, School Code) match a key.
"""
import sys, zipfile, re, csv, os
import xml.etree.ElementTree as ET

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RNS = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'


def col_index(ref):
    letters = re.match(r'[A-Z]+', ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def shared_strings(z):
    out = []
    try:
        f = z.open('xl/sharedStrings.xml')
    except KeyError:
        return out
    for ev, el in ET.iterparse(f, events=('end',)):
        if el.tag == NS + 'si':
            out.append(''.join(t.text or '' for t in el.iter(NS + 't')))
            el.clear()
    return out


def sheet_paths(z):
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rmap = {r.get('Id'): r.get('Target') for r in rels}
    out = {}
    for s in wb.iter(NS + 'sheet'):
        t = rmap[s.get(RNS + 'id')]
        t = t.lstrip('/')
        if not t.startswith('xl/'):
            t = 'xl/' + t
        out[s.get('name')] = t
    return out


def norm(v, width):
    v = (v or '').strip()
    if v.endswith('.0'):
        v = v[:-2]
    return v.zfill(width) if v.isdigit() else v


def main():
    xlsx, outdir, keysfile = sys.argv[1:4]
    sheets = sys.argv[4:]
    keys = None
    if keysfile != '-':
        keys = set(l.strip() for l in open(keysfile) if l.strip())
    z = zipfile.ZipFile(xlsx)
    ss = shared_strings(z)
    paths = sheet_paths(z)
    if sheets == ['*']:
        sheets = list(paths)
    os.makedirs(outdir, exist_ok=True)
    for sh in sheets:
        p = paths[sh]
        w = csv.writer(open(os.path.join(outdir, sh + '.csv'), 'w', newline=''))
        kept = 0
        for ev, el in ET.iterparse(z.open(p), events=('end',)):
            if el.tag != NS + 'row':
                continue
            rnum = int(el.get('r'))
            vals = {}
            for c in el.iter(NS + 'c'):
                t = c.get('t')
                v = c.find(NS + 'v')
                if t == 's' and v is not None:
                    val = ss[int(v.text)]
                elif t == 'inlineStr':
                    val = ''.join(x.text or '' for x in c.iter(NS + 't'))
                else:
                    val = v.text if v is not None else ''
                vals[col_index(c.get('r'))] = val
            el.clear()
            row = [vals.get(i, '') for i in range(max(vals) + 1)] if vals else []
            if keys is not None:
                c0 = norm(row[0], 2) if row else ''
                is_data = len(row) >= 5 and len(c0) == 2 and c0.isdigit()
                if is_data:
                    k = '|'.join([c0, norm(row[2], 4), norm(row[4], 3)])
                    if k not in keys:
                        continue
            w.writerow([rnum] + row)
            kept += 1
        print(sh, kept, flush=True)


if __name__ == '__main__':
    main()
