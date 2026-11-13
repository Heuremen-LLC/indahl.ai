# stdlib xlsx reader: returns {sheet_name: [rows]} with shared strings resolved
import zipfile,re,sys,xml.etree.ElementTree as ET
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def col(ref):
    s=re.match(r'[A-Z]+',ref).group(0); n=0
    for ch in s: n=n*26+ord(ch)-64
    return n-1
def read(p):
    z=zipfile.ZipFile(p); ss=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS): ss.append(''.join(t.text or '' for t in si.iter('{%s}t'%NS['m'])))
    wb=ET.fromstring(z.read('xl/workbook.xml')); rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rid={r.get('Id'):r.get('Target') for r in rels}
    out={}
    for sh in wb.find('m:sheets',NS):
        tgt=rid[sh.get('{%s}id'%NS['r'])]; tgt=tgt if tgt.startswith('xl/') else 'xl/'+tgt.lstrip('/')
        rows=[]
        for r in ET.fromstring(z.read(tgt)).iter('{%s}row'%NS['m']):
            vals={}
            for c in r.findall('m:c',NS):
                v=c.find('m:v',NS); t=c.get('t'); x=v.text if v is not None else (''.join(i.text or '' for i in c.iter('{%s}t'%NS['m'])) if t=='inlineStr' else None)
                if t=='s' and x is not None: x=ss[int(x)]
                vals[col(c.get('r'))]=x
            rows.append([vals.get(i) for i in range(max(vals)+1)] if vals else [])
        out[sh.get('name')]=rows
    return out
if __name__=='__main__':
    d=read(sys.argv[1])
    for k,v in d.items(): print('SHEET',k,len(v),'rows'); [print('  ',r[:16]) for r in v[:3]]
