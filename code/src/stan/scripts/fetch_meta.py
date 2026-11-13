"""Metadata v2 with authors and DOI family for gold and every eligible pool candidate. Cached, gentle."""
import json,re,os,time,hashlib,urllib.request,urllib.parse,html,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
S='/Users/heuremen/bones-forge/stan'; C=S+'/data/meta_cache'; os.makedirs(C,exist_ok=True)
UA={'User-Agent':'heuremen-stan-research/1.0 (mailto:research@heuremen.org)'}
def get(u,t=30): return json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t).read())
def aid(l):
    m=re.search(r'arxiv\.org/abs/([\d.]+?)(v\d+)?$',l or ''); return m.group(1) if m else None
def doi_of(l):
    m=re.search(r'doi\.org/(10\..+)$',l or ''); return m.group(1).lower() if m else None
def inv(ai):
    pos={}
    for w,ps in ai.items():
        for p in ps: pos[p]=w
    return ' '.join(pos[i] for i in sorted(pos))
def family(d):
    s=set(); txt=json.dumps([d.get('doi'),d.get('ids'),d.get('locations'),d.get('primary_location')])
    for m in re.finditer(r'10\.\d{4,9}/[^\s"\\<>?#]+',txt): s.add(m.group(0).lower().rstrip('.,;)'))
    for m in re.finditer(r'arxiv\.org/(?:abs|pdf)/([\d.]+?)(?:v\d+)?(?:\.pdf)?["\\]',txt): s.add('arxiv:'+m.group(1))
    for m in re.finditer(r'10\.48550/arxiv\.([\d.]+)',txt.lower()): s.add('arxiv:'+m.group(1))
    return sorted(s)
def meta(link):
    a=aid(link); d=doi_of(link); key=('10.48550/arxiv.'+a) if a else d
    f=C+'/'+hashlib.sha1(key.encode()).hexdigest()[:16]+'.json'
    if os.path.exists(f): return json.load(open(f))
    try:
        w=get('https://api.openalex.org/works/doi:'+urllib.parse.quote(key,safe='/:.')); time.sleep(0.25)
        r={'title':w.get('title'),'abstract':inv(w['abstract_inverted_index']) if w.get('abstract_inverted_index') else None,
           'authors':[(x.get('author') or {}).get('display_name') for x in w.get('authorships',[])],'family':family(w),'year':w.get('publication_year')}
    except Exception as e: r={'title':None,'abstract':None,'authors':[],'family':[],'err':type(e).__name__}
    if a: r['family']=sorted(set(r['family'])|{'arxiv:'+a})
    if d: r['family']=sorted(set(r['family'])|{d})
    json.dump(r,open(f,'w')); return r
if __name__=='__main__':
    B='/Users/heuremen/bones-forge'
    gold=json.load(open(S+'/data/gold_items.json'))
    L=json.load(open(B+'/qia_leads/matrix_page/list.json'))['studies']
    dirs=['sweep_20261101/texts_read','sweep_20261101/texts','backfill_20261101/texts','list_fixes_20261101/rundate_sample/texts','sweep_20261101/old_cut_fix/texts']
    held=set()
    for d in dirs:
        for f in os.listdir(B+'/qia_leads/'+d): held.add(re.sub(r'^arxiv_','',f).rsplit('.',1)[0].lower())
    links=[g['link'] for g in gold if g['link']]
    for s in L:
        a=aid(s['link']); d=doi_of(s['link'])
        if (a and a in held) or (d and d.replace('/','_') in held): links.append(s['link'])
    links=list(dict.fromkeys(links)); print(len(links),'links',flush=True)
    out={}
    for k,l in enumerate(links):
        out[l]=meta(l)
        if k%100==0: print(k,flush=True)
    json.dump(out,open(S+'/data/meta_v2.json','w'))
    print('ok',sum(1 for v in out.values() if v.get('title')),'with title',sum(1 for v in out.values() if v.get('authors')),'with authors',flush=True)
