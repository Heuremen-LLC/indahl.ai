import zipfile,re,sys
from xml.etree import ElementTree as ET
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
z=zipfile.ZipFile(sys.argv[1])
ss=[ ''.join(t.text or '' for t in si.iter('{%s}t'%ns['m'])) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)] if 'xl/sharedStrings.xml' in z.namelist() else []
sh=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
for row in sh.iter('{%s}row'%ns['m']):
    vals=[]
    for c in row.findall('m:c',ns):
        v=c.find('m:v',ns)
        if v is None: 
            is_=c.find('m:is',ns); vals.append(''.join(t.text or '' for t in is_.iter('{%s}t'%ns['m'])) if is_ is not None else ''); continue
        vals.append(ss[int(v.text)] if c.get('t')=='s' else v.text)
    print(' | '.join(vals))
