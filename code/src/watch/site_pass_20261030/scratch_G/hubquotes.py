import re,html,json,subprocess,hashlib,os,io,logging
logging.disable(logging.CRITICAL)
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
def fetch(u):
    f='src/'+hashlib.md5(u.encode()).hexdigest()
    if not os.path.exists(f) or os.path.getsize(f)==0:
        subprocess.run(['curl','-sL','-m','60','-A',UA,'-c','src/cj.txt','-b','src/cj.txt','--max-filesize','60000000','-o',f,u],capture_output=True)
    return open(f,'rb').read() if os.path.exists(f) else b''
def text(b):
    if b[:4]==b'%PDF':
        import pypdf
        try: return ' '.join((p.extract_text() or '') for p in pypdf.PdfReader(io.BytesIO(b)).pages)
        except Exception: return ''
    s=b.decode('utf-8','ignore')
    s=re.sub(r'(?is)<(script|style)\b.*?</\1>','',s)
    return html.unescape(re.sub(r'<[^>]+>',' ',s))
def norm(t):
    t=t.replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"').replace('–','-').replace('—','-').replace('\xa0',' ').replace('−','-')
    return re.sub(r'\s+',' ',t).strip().lower()
H=json.load(open('hub_rows.json'))
def plain(c): return html.unescape(re.sub(r'<[^>]+>','',c)).strip()
def link(c):
    m=re.search(r'href="([^"]+)"',c); return html.unescape(m.group(1)) if m else None
out=[]
# chatbot table
for r in H['findings']:
    inst,doc,quote,src=plain(r[0]),plain(r[1]),plain(r[2]),link(r[3])
    b=fetch(src); t=norm(text(b))
    q=quote.strip('“”"')
    frags=[f.strip(' ….') for f in re.split(r'…|\.\.\.',q) if len(f.strip(' ….'))>8]
    res=[(f[:60],norm(f) in t, re.sub(r'\s','',norm(f)) in re.sub(r'\s','',t)) for f in frags]
    out.append(dict(inst=inst,quote=quote,src=src,size=len(b),frags=res))
    print(inst,'| size',len(b),'|',[(a,b_,c_) for a,b_,c_ in res])
json.dump(out,open('chatbot_verify.json','w'))
