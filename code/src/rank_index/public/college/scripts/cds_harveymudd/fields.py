import pypdf,sys
r=pypdf.PdfReader(sys.argv[1]); out=[]
for i,p in enumerate(r.pages):
    for a in p.get('/Annots',[]) or []:
        a=a.get_object()
        if a.get('/FT')=='/Tx' or (a.get('/Parent') and a['/Parent'].get_object().get('/FT')=='/Tx'):
            v=a.get('/V') or (a['/Parent'].get_object().get('/V') if a.get('/Parent') else None)
            if v not in (None,''):
                x,y=[round(float(t)) for t in a['/Rect'][:2]]
                out.append((i+1,-y,x,str(a.get('/T') or a['/Parent'].get_object().get('/T')),str(v)))
out.sort()
open(sys.argv[2],'w').write("\n".join(f"p{p} y{-y} x{x} {t} = {v}" for p,y,x,t,v in out))
