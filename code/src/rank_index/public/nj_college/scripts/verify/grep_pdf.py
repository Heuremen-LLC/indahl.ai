import sys,re
from pypdf import PdfReader
r=PdfReader(sys.argv[1]); pats=sys.argv[2:]
for i,p in enumerate(r.pages):
    t=p.extract_text() or ''
    for line in t.splitlines():
        if any(re.search(x,line,re.I) for x in pats): print(i+1,'|',line[:160])
