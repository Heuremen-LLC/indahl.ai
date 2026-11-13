import sys,pypdf,json
r=pypdf.PdfReader(sys.argv[1]);f=r.get_fields() or {}
print(len(f),file=sys.stderr)
out=[]
for i,p in enumerate(r.pages):
    for a in p.get('/Annots') or []:
        a=a.get_object()
        if a.get('/Subtype')=='/Widget':
            n=a.get('/T');par=a.get('/Parent')
            nm=n if n else (par.get_object().get('/T') if par else None)
            v=a.get('/V') if a.get('/V') is not None else (par.get_object().get('/V') if par else None)
            rect=[round(float(x)) for x in a['/Rect']]
            out.append((i+1,rect[1],rect[0],nm,v))
for o in out: print(*o,sep='\t')
