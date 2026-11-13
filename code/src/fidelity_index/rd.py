import zipfile,re,sys
def rd(f):
    z=zipfile.ZipFile(f)
    ss=[re.sub('<[^>]+>','',m) for m in re.findall(r'<si>(.*?)</si>',z.read('xl/sharedStrings.xml').decode(),re.S)]
    x=z.read('xl/worksheets/sheet1.xml').decode()
    for row in re.findall(r'<row.*?</row>',x,re.S):
        out=[]
        for c in re.findall(r'<c ([^>]*?)(?:/>|>(.*?)</c>)',row,re.S):
            a,b=c; v=re.search(r'<v>(.*?)</v>',b or '')
            if not v: out.append('');continue
            v=v.group(1); out.append(ss[int(v)] if 't="s"' in a else v)
        print(out)
rd(sys.argv[1])
