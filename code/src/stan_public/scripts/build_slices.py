"""Grow the pool from the whole QIA List and the IRIS List. Slices of 100 kept items, numbered from 2 (slice 1 is the first 100 of data/pool.json).
Seeded shuffle, abstracts from OpenAlex then arXiv, contamination wall against gold (matcher.py, thresholds fixed in PLAN_ADDENDUM_1), removed ids skipped,
duplicates of earlier pool items skipped by title. Cached and gentle (3 workers, 0.25 s between calls each)."""
import json,re,os,random,hashlib,collections,concurrent.futures as cf,urllib.request,time
import xml.etree.ElementTree as ET
from fetch_meta import *; import matcher as M
B='/Users/heuremen/bones-forge'; os.makedirs(S+'/data/slices',exist_ok=True)
gold=json.load(open(S+'/data/gold_items.json')); tw=json.load(open(S+'/data/twins.json'))
gm={g['id']:meta(g['link']) for g in gold if g['link']}
idf=M.Idf([m.get('abstract') or '' for m in gm.values()]+[t['record']['abstract'] or '' for t in tw])
slice1=json.load(open(S+'/data/pool.json'))[:100]; s1=({p['link'] for p in slice1},{M.norm and ' '.join(M.norm(p['title'])) for p in slice1})
L=json.load(open(B+'/qia_leads/matrix_page/list.json'))['studies']
try: L+= [dict(x,anchor='') for x in json.load(open(B+'/iris_index/matrix_page/iris_list.json'))['studies']]
except Exception: pass
rem=set()
for p in (B+'/ledger/removed_at_request.json',B+'/qia_leads/REMOVED_ON_REQUEST.json'):
    d=json.load(open(p)); rem|={x.lower() for x in (d['ids'] if isinstance(d,dict) else [y.get('doi') or y.get('id') or '' for y in d]) if x}
gl={g['link'] for g in gold}; gids={aid(g['link']) for g in gold if aid(g['link'])}; gdoi={doi_of(g['link']) for g in gold if doi_of(g['link'])}
nm=lambda t:re.sub(r'[^a-z0-9]+',' ',t.lower()).strip(); gt={nm(g['study']) for g in gold}
elig=[];seen_l=set();ex=collections.Counter()
for s in L:
    l=s.get('link'); a=aid(l); d=doi_of(l)
    if not l or not (a or d): ex['no_arxiv_or_doi']+=1; continue
    if l in seen_l: ex['duplicate_link']+=1; continue
    seen_l.add(l)
    if l in gl or (a and a in gids) or (d and d in gdoi) or nm(s['study']) in gt: ex['gold']+=1; continue
    if any(k and k in rem for k in ((s.get('anchor') or '').lower(),d or '','arxiv-'+(a or '#'))): ex['removed']+=1; continue
    if l in s1[0]: ex['in_slice1']+=1; continue
    elig.append(s)
random.Random(20261112).shuffle(elig)
def arxiv_abs(a):
    f=S+'/data/abstracts_cache/'+hashlib.sha1(('ax:'+a).encode()).hexdigest()[:16]+'.json'
    if os.path.exists(f): return json.load(open(f)).get('abstract')
    r={'abstract':None}
    try:
        x=urllib.request.urlopen(urllib.request.Request('http://export.arxiv.org/api/query?max_results=1&id_list='+a,headers=UA),timeout=60).read(); time.sleep(3.2)
        e=ET.fromstring(x).find('{http://www.w3.org/2005/Atom}entry'); r={'abstract':' '.join((e.find('{http://www.w3.org/2005/Atom}summary').text or '').split())}
    except Exception: pass
    json.dump(r,open(f,'w')); return r['abstract']
def prep(s):
    m=meta(s['link']); ab=m.get('abstract')
    if not (ab and len(ab)>=300) and aid(s['link']): ab=arxiv_abs(aid(s['link']))
    return s,m,(ab if ab and len(ab)>=300 else None)
kept=[];n_slice=1;log=collections.Counter(ex);titles=set(s1[1]);log['eligible']=len(elig)
def flush():
    global kept,n_slice
    while len(kept)>=100:
        n_slice+=1; json.dump(kept[:100],open(S+'/data/slices/slice_%02d.json'%n_slice,'w'),indent=1); kept=kept[100:]
        json.dump(dict(log,slices_written=n_slice-1),open(S+'/results/slice_log.json','w'),indent=1); print('wrote slice',n_slice,dict(log),flush=True)
with cf.ThreadPoolExecutor(3) as ex_:
    for k in range(0,len(elig),30):
        for s,m,ab in ex_.map(prep,elig[k:k+30]):
            log['processed']+=1
            if not ab: log['no_abstract']+=1; continue
            t=(m.get('title') or s['study']).strip()
            if ' '.join(M.norm(t)) in titles: log['duplicate_title']+=1; continue
            hit=None
            for gid,gmeta in gm.items():
                f,why,sc=M.compare(dict(m,abstract=ab),gmeta,idf,True)
                if f: hit=(gid,why,sc); break
            if hit: log['wall_flagged']+=1; open(S+'/results/slice_wall_flagged.jsonl','a').write(json.dumps({'link':s['link'],'gold_id':hit[0],'why':hit[1],'scores':hit[2]})+'\n'); continue
            titles.add(' '.join(M.norm(t))); log['kept']+=1
            kept.append({'id':hashlib.sha1(s['link'].encode()).hexdigest()[:12],'link':s['link'],'title':t,'text':t+'\n\n'+ab,'authors':m.get('authors')})
        flush()
json.dump(dict(log,slices_written=n_slice-1,leftover_unfilled=len(kept)),open(S+'/results/slice_log.json','w'),indent=1); print('done',dict(log),flush=True)
