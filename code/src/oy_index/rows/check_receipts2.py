"""Looser receipt check: each "quote" is tested against every URL within 3 lines above/below. Prints PASS (first URL that holds it) or FAIL."""
import re,sys,random,subprocess,os,io,html,hashlib
K=int(sys.argv[2]) if len(sys.argv)>2 else 3; random.seed(sys.argv[1]+'v2')
L=open(sys.argv[1]).read().split('\n')
D='/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/dl_oy_check'; os.makedirs(D,exist_ok=True)
norm=lambda s: re.sub(r'[^a-z0-9]+',' ',html.unescape(s).lower().replace('’',"'")).strip()
def text(u):
    f=os.path.join(D,hashlib.md5(u.encode()).hexdigest())
    if not os.path.exists(f): subprocess.run(['curl','-sL','-m','60','-A','Mozilla/5.0','-o',f,u],capture_output=True)
    if not os.path.exists(f): return ''
    b=open(f,'rb').read()
    if b[:4]==b'%PDF':
        try:
            import pypdf; return ' '.join((p.extract_text() or '') for p in pypdf.PdfReader(io.BytesIO(b)).pages)
        except Exception: return ''
    s=b.decode('utf-8','ignore'); s=re.sub(r'(?s)<(script|style).*?</\1>','',s); return re.sub(r'<[^>]+>',' ',s)
items=[]
for i,l in enumerate(L):
    for q in re.findall(r'"([^"]{30,300})"',l):
        us=[u.rstrip('.,;:') for j in range(max(0,i-3),min(len(L),i+4)) for u in re.findall(r'https?://[^\s)|>"\]]+',L[j])]
        if us: items.append((q,list(dict.fromkeys(us))))
print(os.path.basename(sys.argv[1]),'quotes',len(items))
for q,us in random.sample(items,min(K,len(items))):
    nq=norm(q)[:70]; hit=None
    for u in us[:6]:
        if nq and nq in norm(text(u)): hit=u; break
    print('  ','PASS' if hit else 'FAIL',(hit or us[0])[:85],'|',q[:70])
