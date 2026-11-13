import sys, re
from pypdf import PdfReader
path=sys.argv[1]; pats=sys.argv[2:]
r=PdfReader(path)
txt="\n".join((p.extract_text() or "") for p in r.pages)
open(path.rsplit('.',1)[0]+'.txt','w').write(txt)
for pat in pats:
    for m in re.finditer(pat, txt, flags=re.I):
        s=max(0,m.start()-400); e=min(len(txt), m.end()+600)
        print('=== ',pat,' @',m.start()); print(txt[s:e].replace('\n',' ')); print()
