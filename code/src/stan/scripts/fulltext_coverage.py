import json,re,time,os,urllib.request,urllib.parse,collections
R='/Users/heuremen/bones-forge/stan/'
UA={'User-Agent':'stan-coverage/1.0'}
last={}
def get(url,maxb=30*2**20):
    h=urllib.parse.urlparse(url).netloc
    w=1.05-(time.time()-last.get(h,0))
    if w>0: time.sleep(w)
    last[h]=time.time()
    try:
        r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60)
        b=r.read(maxb+1)
        if len(b)>maxb: return None,'too_big'
        return b,r.headers.get('content-type','')
    except Exception as e: return None,str(e)[:80]
def js(url):
    b,e=get(url)
    try: return json.loads(b)
    except: return None
def host(u): return urllib.parse.urlparse(u).netloc
g=json.load(open(R+'data/gold_items.json'))
split={i['id']:i['split'] for i in json.load(open(R+'data/gold_split.json'))['items']}
out={}
def save(i,b,url,src,ext):
    p=R+'data/fulltext_cache/%s.%s'%(i,ext); open(p,'wb').write(b)
    return dict(source=src,result='FETCHED',host=host(url),file=p,bytes=len(b),url=url)
def oa(i,doi):
    tried=[]
    d=js('https://api.openalex.org/works/doi:'+doi)
    urls=[]
    if d:
        for l in [d.get('best_oa_location')]+(d.get('locations') or []):
            if l and l.get('pdf_url') and l['pdf_url'] not in urls: urls.append(l['pdf_url'])
    u=js('https://api.unpaywall.org/v2/%s?email=stan-coverage@example.com'%doi)
    if u:
        for l in [u.get('best_oa_location')]+(u.get('oa_locations') or []):
            if l and l.get('url_for_pdf') and l['url_for_pdf'] not in urls: urls.append(l['url_for_pdf'])
    if not urls: return 'NO_OA',None
    for x in urls[:3]:
        b,ct=get(x)
        if b and b[:4]==b'%PDF': return 'OK',save(i,b,x,'openalex/unpaywall','pdf')
    return 'FAIL',None
for it in g:
    i=it['id'];l=it['link'] or '';rec=dict(split=split.get(i,it['split']),link=l)
    m=re.search(r'arxiv\.org/abs/([^\s?#]+)',l)
    z=re.search(r'10\.5281/zenodo\.(\d+)',l)
    if not l: rec.update(source=None,result='NO_IDENTIFIER',host=None,file=None,bytes=0)
    elif m:
        aid=m.group(1); got=None
        b,ct=get('https://export.arxiv.org/pdf/'+aid)
        if b and b[:4]==b'%PDF': got=save(i,b,'https://export.arxiv.org/pdf/'+aid,'arxiv_pdf','pdf')
        else:
            b,ct=get('https://export.arxiv.org/e-print/'+aid)
            if b and len(b)>100: got=save(i,b,'https://export.arxiv.org/e-print/'+aid,'arxiv_eprint','tar.gz')
        if got: rec.update(got)
        else:
            doi='10.48550/arxiv.'+re.sub(r'v\d+$','',aid)
            s,got=oa(i,doi)
            if got: rec.update(got)
            else: rec.update(source='arxiv,openalex,unpaywall',result='OA_LINK_FAILED' if s=='FAIL' else 'OA_LINK_FAILED',host='arxiv.org',file=None,bytes=0,note='arxiv pdf/eprint fetch failed')
    elif z:
        got=None
        d=js('https://zenodo.org/api/records/'+z.group(1))
        files=(d or {}).get('files') or []
        pf=[f for f in files if f.get('key','').lower().endswith('.pdf')]
        if pf:
            u=pf[0]['links']['self']
            b,ct=get(u)
            if b and b[:4]==b'%PDF': got=save(i,b,u,'zenodo','pdf')
        if got: rec.update(got)
        else:
            s,got=oa(i,'10.5281/zenodo.'+z.group(1))
            if got: rec.update(got)
            else: rec.update(source='zenodo,openalex,unpaywall',result='OA_LINK_FAILED' if pf else 'NO_OA',host='zenodo.org',file=None,bytes=0,note='record has pdf=%s'%bool(pf))
    else: rec.update(source=None,result='NO_IDENTIFIER',host=None,file=None,bytes=0)
    out[i]=rec; print(i,rec['result'],rec.get('host'),flush=True)
json.dump(out,open('/tmp/x.json','w')) if False else None
# extraction
for i,r in out.items():
    if r['result']!='FETCHED': continue
    if r['file'].endswith('.pdf'):
        try:
            import pypdf
            pr=pypdf.PdfReader(r['file']); r['pages']=len(pr.pages)
            r['chars']=sum(len(p.extract_text() or '') for p in pr.pages)
        except Exception as e: r['pages']=None;r['chars']=0;r['extract_error']=str(e)[:80]
        r['extract_flag']=r['chars']<2000
    else: r['pages']=None;r['chars']=None;r['extract_flag']=False
cnt=lambda f:dict(collections.Counter(r['result'] for r in out.values() if f(r)))
res=dict(per_id=out,counts_overall=cnt(lambda r:True),counts_dev=cnt(lambda r:r['split']=='dev'),counts_test=cnt(lambda r:r['split']=='test'),
 counts_per_host=dict(collections.Counter(r['host'] for r in out.values() if r['result']=='FETCHED')),
 extraction_failures=[i for i,r in out.items() if r.get('extract_flag')],
 missing=[i for i,r in out.items() if r['result']!='FETCHED'])
json.dump(res,open(R+'data/fulltext_coverage.json','w'),indent=1)
print({k:v for k,v in res.items() if k!='per_id'})
