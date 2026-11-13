import sys,pypdf
r=pypdf.PdfReader(sys.argv[1]);o=open(sys.argv[2],'w')
for i,p in enumerate(r.pages): o.write(f'\n=====PAGE {i+1}\n'+(p.extract_text() or ''))
