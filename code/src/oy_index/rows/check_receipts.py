# Spot-check receipts in a Wall row: pick K random (URL, "quote") pairs, fetch the URL, test the quote is present (normalized).
import re,sys,random,subprocess,os,io,html,hashlib
K=int(sys.argv[2]) if len(sys.argv)>2 else 2; random.seed(sys.argv[1])
row=open(sys.argv[1]).read()
D='/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/dl_oy_check'; os.makedirs(D,exist_ok=True)
pairs=[]
for line in row.split('\n'):
    urls=re.findall(r'https?://[^\s)|>"]+',line); qs=re.findall(r'"([^"]{25,400})"',line)
    for q in qs:
        if urls: pairs.append((urls[0].rstrip('.,;'),q))
norm=lambda s: re.sub(r'[^a-z0-9]+',' ',html.unescape(s).lower().replace('’',"'").replace('“','"').replace('”','"')).strip()
def text(u):
    f=os.path.join(D,hashlib.md5(u.encode()).hexdigest())
    if not os.path.exists(f): subprocess.run(['curl','-sL','-m','90','-A','Mozilla/5.0','-o',f,u])
    b=open(f,'rb').read()
    if b[:4]==b'%PDF':
        import pypdf; return ' '.join((p.extract_text() or '') for p in pypdf.PdfReader(io.BytesIO(b)).pages)
    s=b.decode('utf-8','ignore'); s=re.sub(r'(?s)<(script|style).*?</\1>','',s); return re.sub(r'<[^>]+>',' ',s)
print(os.path.basename(sys.argv[1]),'pairs',len(pairs))
for u,q in random.sample(pairs,min(K,len(pairs))):
    try: t=norm(text(u))
    except Exception as e: print('  ERROR',u,e); continue
    nq=norm(q); ok=nq in t or nq[:60] in t
    print('  ','PASS' if ok else 'FAIL',u[:90],'|',q[:80])
