import json,re,subprocess,hashlib,html,os,io,sys
O='/Users/heuremen/bones-forge/oy_index/'
S=json.load(open(O+'schools.json'))
ids=[l.strip().split('/')[-1] for l in open('../lane_G_urls.txt') if '/school/' in l]
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
def fetch(u):
    f='src/'+hashlib.md5(u.encode()).hexdigest()
    if not os.path.exists(f):
        subprocess.run(['curl','-sL','-m','60','-A',UA,'--max-filesize','40000000','-o',f,u],capture_output=True)
    return open(f,'rb').read() if os.path.exists(f) else b''
def text(b):
    if b[:4]==b'%PDF':
        import pypdf
        try: return ' '.join((p.extract_text() or '') for p in pypdf.PdfReader(io.BytesIO(b)).pages)
        except Exception as e: return ''
    s=b.decode('utf-8','ignore')
    s=re.sub(r'(?is)<(script|style)\b.*?</\1>','',s)
    return html.unescape(re.sub(r'<[^>]+>',' ',s))
def norm(t):
    t=t.replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"').replace('–','-').replace('—','-').replace('\xa0',' ')
    t=re.sub(r'\s+',' ',t)
    return t.strip().lower()
res=[]
for s in S:
    if s['unitid'] not in ids: continue
    for kind in ('sentences','courses'):
        for h in s[kind]:
            key='sentence' if kind=='sentences' else 'line'
            src=h['url']
            b=fetch(src); t=norm(text(b)) if b else ''
            q=norm(h[key])
            full=q in t if t else None
            # compact compare ignoring spaces
            tc=re.sub(r'\s','',t); qc=re.sub(r'\s','',q)
            comp=qc in tc if t else None
            res.append(dict(unitid=s['unitid'],school=s['school'],kind=kind,text=h[key],url=src,fetched=bool(t),size=len(b),verbatim=full,nospace=comp))
json.dump(res,open('verbatim_results.json','w'))
import collections
for kind in ('sentences','courses'):
    r=[x for x in res if x['kind']==kind]
    print(kind,len(r),'fetched',sum(x['fetched'] for x in r),'verbatim',sum(1 for x in r if x['verbatim']),'nospace-only',sum(1 for x in r if x['nospace'] and not x['verbatim']),'not found',sum(1 for x in r if x['fetched'] and not x['nospace']),'unreachable',sum(1 for x in r if not x['fetched']))
