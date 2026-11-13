import sys,pypdf,re
r=pypdf.PdfReader(sys.argv[1])
keys=sys.argv[2:]
for i,p in enumerate(r.pages):
    t=p.extract_text() or ''
    for k in keys:
        if k in t: print(k,'-> page',i+1)
