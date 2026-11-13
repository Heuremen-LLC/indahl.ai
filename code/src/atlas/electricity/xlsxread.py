"""Minimal .xlsx reader (zip + xml, standard library only). rows(path, sheet_index) -> list of lists of str/float/None."""
import zipfile,re
import xml.etree.ElementTree as ET
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def col(ref):
    n=0
    for ch in re.match(r'[A-Z]+',ref).group(0): n=n*26+ord(ch)-64
    return n-1
def sheets(path):
    z=zipfile.ZipFile(path); wb=ET.fromstring(z.read('xl/workbook.xml')); rel=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rid={r.get('Id'):r.get('Target') for r in rel}
    return [(s.get('name'),'xl/'+rid[s.get('{%s}id'%NS['r'])].lstrip('/').replace('xl/','')) for s in wb.find('m:sheets',NS)]
def rows(path,idx=0):
    z=zipfile.ZipFile(path); name,target=sheets(path)[idx]
    ss=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS): ss.append(''.join(t.text or '' for t in si.iter('{%s}t'%NS['m'])))
    out=[]
    for row in ET.fromstring(z.read(target)).find('m:sheetData',NS):
        cells={}
        for c in row:
            v=c.find('m:v',NS); t=c.get('t')
            if t=='inlineStr': val=''.join(x.text or '' for x in c.iter('{%s}t'%NS['m']))
            elif v is None: val=None
            elif t=='s': val=ss[int(v.text)]
            elif t in('str','e','b'): val=v.text
            else:
                try: val=float(v.text)
                except: val=v.text
            cells[col(c.get('r'))]=val
        out.append([cells.get(i) for i in range(max(cells)+1)] if cells else [])
    return out

def hyperlinks(path,idx=0):
    """{cell ref: target} for external hyperlinks on a sheet (regex over the sheet and its rels, standard library only)."""
    z=zipfile.ZipFile(path); name,target=sheets(path)[idx]
    rels_name=target.replace('worksheets/','worksheets/_rels/')+'.rels'
    rel={}
    for m in re.finditer(r'<Relationship [^>]*?Id="([^"]+)"[^>]*?Target="([^"]+)"',z.read(rels_name).decode('utf-8','ignore')): rel[m.group(1)]=m.group(2)
    out={}
    for m in re.finditer(r'<hyperlink ref="([A-Z]+\d+)" r:id="([^"]+)"',z.read(target).decode('utf-8','ignore')):
        if m.group(2) in rel: out[m.group(1)]=rel[m.group(2)]
    return out
