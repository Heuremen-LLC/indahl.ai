"""Contamination wall: compare every pool candidate with every gold record, report the matcher's recall on twins (real) and on a synthetic
paraphrase control, then rebuild the pool without flagged items. Pool order: seeded shuffle of the eligible list, first 100 with an abstract."""
import json,re,os,random,hashlib,collections
from fetch_meta import *; import matcher as M
B='/Users/heuremen/bones-forge'
gold=json.load(open(S+'/data/gold_items.json')); gm={g['id']:meta(g['link']) for g in gold if g['link']}
tw=json.load(open(S+'/data/twins.json')); ck=lambda k:S+'/data/abstracts_cache/'+hashlib.sha1(k.encode()).hexdigest()[:16]+'.json'
def absf(link,m):
    if m.get('abstract') and len(m['abstract'])>=300: return m['abstract']
    a=aid(link)
    if a and os.path.exists(ck('ax:'+a)):
        r=json.load(open(ck('ax:'+a))); 
        if r.get('abstract') and len(r['abstract'])>=300: return r['abstract']
    return None
# eligible list as in build_data (same seed, same order), recomputed here from the List
L=json.load(open(B+'/qia_leads/matrix_page/list.json'))['studies']
dirs=['sweep_20261101/texts_read','sweep_20261101/texts','backfill_20261101/texts','list_fixes_20261101/rundate_sample/texts','sweep_20261101/old_cut_fix/texts']
held=set()
for d in dirs:
    for f in os.listdir(B+'/qia_leads/'+d): held.add(re.sub(r'^arxiv_','',f).rsplit('.',1)[0].lower())
rem=set()
for p in (B+'/ledger/removed_at_request.json',B+'/qia_leads/REMOVED_ON_REQUEST.json'):
    d=json.load(open(p)); rem|={x.lower() for x in (d['ids'] if isinstance(d,dict) else [y.get('doi') or y.get('id') or '' for y in d]) if x}
gl={g['link'] for g in gold}; gids={aid(g['link']) for g in gold if aid(g['link'])}; gdoi={doi_of(g['link']) for g in gold if doi_of(g['link'])}
nm=lambda t:re.sub(r'[^a-z0-9]+',' ',t.lower()).strip(); gt={nm(g['study']) for g in gold}
elig=[]
for s in L:
    a=aid(s['link']); d=doi_of(s['link'])
    if s['link'] in gl or (a and a in gids) or (d and d in gdoi) or nm(s['study']) in gt: continue
    if any(k and k in rem for k in ((s.get('anchor') or '').lower(),d or '','arxiv-'+(a or '#'))): continue
    if (a and a in held) or (d and d.replace('/','_') in held): elig.append(s)
random.Random(20261112).shuffle(elig)
cand=[]
for s in elig:
    m=meta(s['link']); cand.append((s,m,absf(s['link'],m)))
docs=[m.get('abstract') or '' for m in gm.values()]+[c[2] or '' for c in cand]+[t['record']['abstract'] or '' for t in tw]
idf=M.Idf(docs)
# controls
hit=collections.Counter(); miss=[]
for t in tw:
    f,why,sc=M.compare(t['record'],gm[t['gold_id']],idf,use_family=False); k=t['kind']; hit[(k,'n')]+=1; hit[(k,'flagged')]+=f
    if not f: miss.append({'twin_doi':t['twin_doi'],'kind':k,'scores':sc})
rng=random.Random(5); syn=collections.Counter()
for gid,m in gm.items():
    if not m.get('abstract') or len(m['abstract'])<300: continue
    sents=re.split(r'(?<=[.!?]) ',m['abstract']); rng.shuffle(sents); sents=sents[:max(2,int(len(sents)*0.6))]
    rec={'title':' '.join((m['title'] or '').split()[1:]),'abstract':' '.join(sents),'authors':[],'family':[]}
    f,_,_=M.compare(rec,m,idf,False); syn['n']+=1; syn['flagged']+=f
# false-flag rate on non-twin pairs, gold vs gold
ids=list(gm); ff=0;tot=0
for a in range(len(ids)):
    for b in range(a+1,len(ids)): ff+=M.compare(gm[ids[a]],gm[ids[b]],idf,False)[0]; tot+=1
# apply
flagged=[];kept=[]
for s,m,ab in cand:
    best=None
    for gid,gmeta in gm.items():
        f,why,sc=M.compare(dict(m,abstract=ab),gmeta,idf,True)
        if f: best=(gid,why,sc); break
    if best: flagged.append({'link':s['link'],'gold_id':best[0],'why':best[1],'scores':best[2]})
    else: kept.append((s,m,ab))
old=json.load(open(S+'/data/pool.json'))[:100]
bad={hashlib.sha1(f['link'].encode()).hexdigest()[:12] for f in flagged}
for o in old:
    o['wall_flagged']=o['id'] in bad
json.dump(old,open(S+'/data/pool_with_wall_flags.json','w'),indent=1)
pool=[o for o in old if not o['wall_flagged']]; noabs=0
rep={'matcher_thresholds':M.TH,'positive_control_real_twins':{k:{'n':hit[(k,'n')],'flagged':hit[(k,'flagged')],'recall':round(hit[(k,'flagged')]/hit[(k,'n')],3)} for k in ('journal_or_proceedings','zenodo_version') if hit[(k,'n')]},
 'positive_control_total':{'n':sum(v for (k,w),v in hit.items() if w=='n'),'flagged':sum(v for (k,w),v in hit.items() if w=='flagged')},
 'missed_twins':miss,'synthetic_paraphrase_control(60pct of sentences shuffled, first title word dropped, no authors)':{'n':syn['n'],'flagged':syn['flagged']},
 'translation_control':'none available, recall on translations is untested','gold_vs_gold_nontwin_pairs_flagged':{'flagged':ff,'pairs':tot},
 'candidates':len(cand),'flagged_as_gold_duplicates':len(flagged),'flagged_detail':flagged,'kept_after_wall':len(kept),'skipped_no_abstract':noabs,'pool_first_slice_before_wall':len(old),'pool_size_after_wall':len(pool)}
json.dump(rep,open(S+'/results/contamination_wall.json','w'),indent=1); print(json.dumps({k:v for k,v in rep.items() if k!='flagged_detail' and k!='missed_twins'},indent=1))
