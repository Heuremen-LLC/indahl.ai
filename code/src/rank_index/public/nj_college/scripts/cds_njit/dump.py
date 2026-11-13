import sys,zipfile,re
z=zipfile.ZipFile(sys.argv[1])
ss=re.findall(r'<si>(.*?)</si>',z.read('xl/sharedStrings.xml').decode('utf8'),re.S)
ss=[re.sub(r'<[^>]+>','',s) for s in ss]
wb=z.read('xl/workbook.xml').decode()
print(re.findall(r'<sheet [^>]*name="([^"]+)"',wb))
names=[n for n in z.namelist() if n.startswith('xl/worksheets/sheet')]
out=open(sys.argv[2],'w')
for n in sorted(names):
    x=z.read(n).decode('utf8')
    out.write(f"\n#### {n}\n")
    for m in re.finditer(r'<c r="([A-Z]+\d+)"([^>]*?)(?:/>|>(.*?)</c>)',x,re.S):
        ref,attr,body=m.groups()
        if not body: continue
        v=re.search(r'<v>(.*?)</v>',body,re.S)
        if not v: 
            t=re.search(r'<t[^>]*>(.*?)</t>',body,re.S)
            if t: out.write(f"{ref}\t{t.group(1)}\n")
            continue
        val=v.group(1)
        if 't="s"' in attr: val=ss[int(val)]
        out.write(f"{ref}\t{val}\n")
