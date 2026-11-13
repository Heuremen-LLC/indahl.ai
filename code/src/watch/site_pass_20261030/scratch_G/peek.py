import sys,re,hashlib,io,html,json
sys.path.insert(0,'.')
def load(u):
    f='src/'+hashlib.md5(u.encode()).hexdigest()
    b=open(f,'rb').read()
    if b[:4]==b'%PDF':
        import pypdf,logging
        logging.disable(logging.CRITICAL)
        return ' '.join((p.extract_text() or '') for p in pypdf.PdfReader(io.BytesIO(b)).pages)
    s=b.decode('utf-8','ignore')
    s=re.sub(r'(?is)<(script|style)\b.*?</\1>','',s)
    return html.unescape(re.sub(r'<[^>]+>',' ',s))
def peek(u,pat,w=160,n=3):
    t=re.sub(r'\s+',' ',load(u))
    out=[]
    for m in list(re.finditer(pat,t,re.I))[:n]:
        out.append(t[max(0,m.start()-w):m.end()+w])
    return out
if __name__=='__main__':
    u=sys.argv[1]; pat=sys.argv[2]
    for o in peek(u,pat): print('>>',o)
