import sys,re,pypdf
r=pypdf.PdfReader(sys.argv[1]); pat=re.compile(sys.argv[2],re.I)
for i,p in enumerate(r.pages):
    t=p.extract_text() or ''
    for ln in t.splitlines():
        if pat.search(ln): print(i+1,'|',ln[:200])
