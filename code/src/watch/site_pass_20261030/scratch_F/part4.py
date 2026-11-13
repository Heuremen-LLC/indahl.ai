import json,re,html,io,os,hashlib,collections,sys
B='/Users/heuremen/bones-forge/'
ids=[l.strip().rsplit('/',1)[1] for l in open(B+'watch/site_pass_20261030/lane_F_urls.txt')]
S={s['unitid']:s for s in json.load(open(B+'oy_index/schools.json'))}
L=json.load(open('part3_links.json'))
CACHE='/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/dl_smallpass/'
def text_of(b):
    if not b or len(b)<300: return None
    if b[:4]==b'%PDF':
        try:
            import pypdf; return ' '.join((p.extract_text() or '') for p in pypdf.PdfReader(io.BytesIO(b)).pages[:60])
        except Exception as e: return None
    s=b.decode('utf-8','ignore')
    s2=re.sub(r'(?s)<(script|style|nav|footer|header).*?</\1>','',s)
    return html.unescape(re.sub(r'<[^>]+>',' ',s2)), html.unescape(re.sub(r'<[^>]+>',' ',s))
def norm(t): return re.sub(r'\s+',' ',t).strip()
def loose(t): return re.sub(r'[^0-9a-z]+','',t.lower().replace('’',"'").replace('‘',"'"))
tcache={}
def get_text(u):
    if u in tcache: return tcache[u]
    r=L.get(u); out={}
    srcs=[]
    if r and os.path.exists(r['file']): srcs.append(('live',open(r['file'],'rb').read()))
    cf=CACHE+hashlib.md5(u.encode()).hexdigest()
    if os.path.exists(cf): srcs.append(('crawl',open(cf,'rb').read()))
    for name,b in srcs:
        t=text_of(b)
        if isinstance(t,tuple): out[name]=(norm(t[0]),norm(t[1]))
        elif t: out[name]=(norm(t),norm(t))
        else: out[name]=None
    tcache[u]=out; return out
res=collections.defaultdict(list)
def chk(kind,i,piece,u):
    p=norm(piece)
    t=get_text(u)
    status={}
    for name in ('live','crawl'):
        if name not in t: status[name]='nofile'; continue
        if t[name] is None: status[name]='unreadable'; continue
        a,b=t[name]
        if p in a or p in b: status[name]='exact'
        elif loose(p) in loose(a) or loose(p) in loose(b): status[name]='loose'
        else: status[name]='absent'
    res[kind].append((i,u,p[:100],status))
for i in ids:
    s=S[i]
    for h in s['sentences']: chk('sent',i,h['sentence'],h['url'])
    for h in s['courses']: chk('course',i,h['line'],h['url'])
import pickle
json.dump(res,open('part4.json','w'),indent=0)
for kind in ('sent','course'):
    c=collections.Counter((x[3].get('live'),x[3].get('crawl')) for x in res[kind])
    print(kind,len(res[kind]),c.most_common())
