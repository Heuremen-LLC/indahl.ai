"""Fetch abstracts (OpenAlex, then arXiv API), cache, build gold and pool item files."""
import json,re,os,sys,time,random,hashlib,urllib.request,urllib.parse,html
import xml.etree.ElementTree as ET
B='/Users/heuremen/bones-forge'; S=B+'/stan'; C=S+'/data/abstracts_cache'; os.makedirs(C,exist_ok=True)
UA={'User-Agent':'heuremen-stan-research/1.0 (mailto:research@heuremen.org)'}
def get(u,t=30):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t).read()
def aid(link):
    m=re.search(r'arxiv\.org/abs/([\d.]+?)(v\d+)?$',link or ''); return m.group(1) if m else None
def doi_of(link):
    m=re.search(r'doi\.org/(10\..+)$',link or ''); return m.group(1).lower() if m else None
def norm(t): return re.sub(r'[^a-z0-9]+',' ',t.lower()).strip()
def ck(key): return C+'/'+hashlib.sha1(key.encode()).hexdigest()[:16]+'.json'
def inv(ai):
    pos={}
    for w,ps in ai.items():
        for p in ps: pos[p]=w
    return ' '.join(pos[i] for i in sorted(pos))
def openalex(key):
    f=ck('oa:'+key)
    if os.path.exists(f): return json.load(open(f))
    try:
        d=json.loads(get('https://api.openalex.org/works/doi:'+urllib.parse.quote(key,safe='/:.'))); time.sleep(0.25)
        r={'title':d.get('title'),'abstract':inv(d['abstract_inverted_index']) if d.get('abstract_inverted_index') else None,'src':'openalex'}
    except Exception as e: r={'title':None,'abstract':None,'src':'openalex','err':type(e).__name__}
    json.dump(r,open(f,'w')); return r
def arxiv_batch(ids):
    ids=[i for i in ids if not os.path.exists(ck('ax:'+i))]
    for k in range(0,len(ids),40):
        ch=ids[k:k+40]
        try:
            x=get('http://export.arxiv.org/api/query?max_results=%d&id_list=%s'%(len(ch),','.join(ch)),60); time.sleep(3.2)
            ns={'a':'http://www.w3.org/2005/Atom'}; got={}
            for e in ET.fromstring(x).findall('a:entry',ns):
                i=re.sub(r'v\d+$','',e.find('a:id',ns).text.rsplit('/abs/',1)[-1])
                got[i]={'title':' '.join((e.find('a:title',ns).text or '').split()),'abstract':' '.join((e.find('a:summary',ns).text or '').split()),'src':'arxiv'}
        except Exception as e: got={}; print('arxiv err',type(e).__name__)
        for i in ch: json.dump(got.get(i,{'title':None,'abstract':None,'src':'arxiv','err':'none'}),open(ck('ax:'+i),'w'))
def abstract_for(link):
    a=aid(link); d=doi_of(link); r=None
    if a: r=openalex('10.48550/arxiv.'+a)
    elif d: r=openalex(d)
    if r and r.get('abstract') and len(r['abstract'])>=300: return r
    if a:
        arxiv_batch([a]); r2=json.load(open(ck('ax:'+a)))
        if r2.get('abstract') and len(r2['abstract'])>=300: return r2
    return None
def clean(t): return html.unescape(re.sub(r'<[^>]+>',' ',t or '')).strip()
gold=json.load(open(S+'/data/gold_split.json'))['items']
L=json.load(open(B+'/qia_leads/matrix_page/list.json'))['studies']
rem=set()
for p in (B+'/ledger/removed_at_request.json',B+'/qia_leads/REMOVED_ON_REQUEST.json'):
    d=json.load(open(p)); rem|={x.lower() for x in (d['ids'] if isinstance(d,dict) else [y.get('doi') or y.get('id') or '' for y in d]) if x}
def removed(s):
    k=[s['anchor'].lower() if s.get('anchor') else '', (doi_of(s['link']) or ''), 'arxiv-'+(aid(s['link']) or '#')]
    return any(x and (x in rem or any(x in r for r in rem if '/' in r and len(x)>8)) for x in k)
# phase 1: pool eligibility
dirs=['sweep_20261101/texts_read','sweep_20261101/texts','backfill_20261101/texts','list_fixes_20261101/rundate_sample/texts','sweep_20261101/old_cut_fix/texts']
held=set()
for d in dirs:
    for f in os.listdir(B+'/qia_leads/'+d):
        held.add(re.sub(r'^arxiv_','',f).rsplit('.',1)[0].lower())
def has_text(s):
    a=aid(s['link']); d=doi_of(s['link'])
    return (a and a in held) or (d and d.replace('/','_') in held)
gids={aid(g['link']) for g in gold if aid(g['link'])}; gdoi={doi_of(g['link']) for g in gold if doi_of(g['link'])}; gl={g['link'] for g in gold}
gold_titles={norm(g['study']) for g in gold}
elig=[]; ex={'no_link':0,'not_held':0,'gold':0,'removed':0}
for s in L:
    if not s['link']: ex['no_link']+=1; continue
    a=aid(s['link']); d=doi_of(s['link'])
    if s['link'] in gl or (a and a in gids) or (d and d in gdoi) or norm(s['study']) in gold_titles: ex['gold']+=1; continue
    if removed(s): ex['removed']+=1; continue
    if not has_text(s): ex['not_held']+=1; continue
    elig.append(s)
print('eligible',len(elig),ex)
random.Random(20261112).shuffle(elig)
# phase 2: fetch abstracts, gold first
out_gold=[];miss_g=0
arxiv_batch([aid(g['link']) for g in gold if aid(g['link'])][:0])
for g in gold:
    r=abstract_for(g['link']) if g['link'] else None
    if not r: miss_g+=1; g=dict(g,text=None)
    else: g=dict(g,title=clean(r['title']),text=clean(r['title'])+'\n\n'+clean(r['abstract']),abs_src=r['src'])
    out_gold.append(g)
json.dump(out_gold,open(S+'/data/gold_items.json','w'),indent=1)
print('gold items',len(out_gold),'missing abstract',miss_g)
pool=[];miss_p=0;seen=set()
for s in elig:
    if len(pool)>=240: break
    r=abstract_for(s['link'])
    if not r: miss_p+=1; continue
    t=norm(r['title'] or '')
    if t in seen or t in gold_titles: continue
    seen.add(t)
    pool.append({'id':hashlib.sha1(s['link'].encode()).hexdigest()[:12],'link':s['link'],'title':clean(r['title']),'text':clean(r['title'])+'\n\n'+clean(r['abstract']),'abs_src':r['src']})
json.dump(pool,open(S+'/data/pool.json','w'),indent=1)
json.dump({'eligible':len(elig),'excluded':ex,'pool_abstract_unavailable_before_240':miss_p,'pool_size':len(pool),'gold_missing_abstract':miss_g},open(S+'/data/data_counts.json','w'),indent=1)
print('pool',len(pool),'skipped no abstract',miss_p)
