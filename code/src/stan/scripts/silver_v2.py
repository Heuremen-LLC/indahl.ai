"""STAN v2 silver labels (written 12 Nov 2026). Does not touch v1 files. See results/v2_prep.md for the rules."""
import json,random,collections,math,os
from common import *
SEED=1112
QUOTABLE={('F1','PRESENT'),('F1','ABSENT'),('F2','PRESENT'),('F2','ABSENT'),('F3','PRESENT')}   # QUOTABLE.md, frozen
cfg=json.load(open(S+'/teachers/config.json'))['teachers']; names=list(cfg)
pool={g['id']:g for g in all_pool()}
gs=json.load(open(S+'/data/gold_split.json'))['items']; gold_test={g['id'] for g in gs if g['split']=='test'}
PAR=os.environ.get('PARITY')  # PARITY=1: only the 165 papers v1 used, outputs under silver_v2_parity
V1IDS={json.loads(l)['id'] for l in open(S+'/data/silver_v1/silver_all.jsonl')} if PAR else None
SUF='_parity' if PAR else ''
R1={n:{r['id']:r for r in jl_read(S+'/teachers/%s_round1.jsonl'%n) if r['set']=='pool'} for n in names}
R2={n:{r['id']:r for r in jl_read(S+'/teachers/%s_round2.jsonl'%n)} for n in names}
def native(code,o,text):
    """Original status/reason/quote, no conversion. vote is the status counted toward agreement, or None."""
    if not isinstance(o,dict) or str(o.get('status','')).upper() not in ('PRESENT','ABSENT','CANNOT_TELL','NOT_APPLICABLE'):
        return {'status':'PARSE_FAILED','reason':'','quote':'','flag':'parse_failed','vote':None}
    st=str(o['status']).upper(); rs=str(o.get('reason') or '').upper().strip(); q=str(o.get('quote') or '')
    if st=='CANNOT_TELL':
        if rs not in ALL_REASONS: return {'status':'PARSE_FAILED','reason':'','quote':'','flag':'parse_failed','vote':None}
        return {'status':st,'reason':rs,'quote':'','flag':'ok','vote':st}
    if st=='NOT_APPLICABLE': return {'status':st,'reason':'','quote':'','flag':'ok','vote':st}
    if ws(q) and ws(q) in ws(text): return {'status':st,'reason':'','quote':q,'flag':'grounded','vote':st}
    return {'status':st,'reason':'','quote':q,'flag':'unquoted' if not ws(q) else 'not_found','vote':None}
def r1lab(n,i,c): return native(c,(parse_obj(R1[n][i]['raw']) or {}).get(c),pool[i]['text'])
def r2lab(n,i,c):
    if i in R2[n] and c in R2[n][i]['codes']: return native(c,(parse_obj(R2[n][i]['raw']) or {}).get(c),pool[i]['text'])
    return None
log=collections.Counter(); silver=[]; dropped=[]; calls=collections.Counter()
for i,g in pool.items():
    if V1IDS is not None and i not in V1IDS: continue
    if i in gold_test: log['pool_id_in_gold_test_skipped']+=1; continue
    if not all(i in R1[n] for n in names): log['item_not_labelled_by_all_three']+=1; continue
    log['items_used']+=1
    for c in CODES:
        l1={n:r1lab(n,i,c) for n in names}
        for n in names: calls[(l1[n]['status'],l1[n]['flag'])]+=1
        def unan(L):
            v={x['vote'] for x in L.values()}
            return None not in v and len(v)==1
        fin=l1; via='round1'
        if not unan(l1):
            fin={n:(r2lab(n,i,c) or l1[n]) for n in names}; via='crosstalk'
        rec={'id':i,'code':c,'round1':l1,'final':fin}
        if not unan(fin):
            v=[x['vote'] for x in fin.values()]
            if any(x['flag'] in('unquoted','not_found') for x in fin.values()): log['no_silver_some_unquoted_or_unfound_PA']+=1
            elif any(x['flag']=='parse_failed' for x in fin.values()): log['no_silver_parse_failed']+=1
            else: log['no_silver_teachers_disagree']+=1
            continue
        st=next(iter(fin.values()))['vote']
        if st in ('PRESENT','ABSENT') and (c,st) not in QUOTABLE:
            rec['drop']='non_quotable_cell'; rec['status']=st; dropped.append(rec); log['dropped_non_quotable_%s_%s'%(c,st)]+=1; continue
        if st=='CANNOT_TELL':
            rc=collections.Counter(x['reason'] for x in fin.values()); rs=rc.most_common(1)[0][0]; q=''
        elif st=='NOT_APPLICABLE': rs=''; q=''
        else: rs=''; q=min((x['quote'] for x in fin.values()),key=len)
        rec.update(via=via,label={'status':st,'reason':rs,'quote':q}); silver.append(rec)
# cap by status per code
def counts(rows):
    t={c:collections.Counter() for c in CODES}
    for r in rows: t[r['code']][r['label']['status']]+=1
    return {c:dict(t[c]) for c in CODES}
before=counts(silver)
rng=random.Random(SEED); kept=[]; capped=[]
for c in CODES:
    rs=[r for r in silver if r['code']==c]; cl=collections.defaultdict(list)
    for r in rs: cl[r['label']['status']].append(r)
    if not cl: continue
    big=max(cl,key=lambda k:len(cl[k])); others=len(rs)-len(cl[big])
    for k in sorted(cl):
        v=sorted(cl[k],key=lambda r:r['id']); rng.shuffle(v)
        lim=others   # single-status codes are cut to 0: untrainable
        if k==big and len(v)>lim: kept+=v[:lim]; capped+=v[lim:]
        else: kept+=v
after=counts(kept)
# paper-level split
ids=sorted({r['id'] for r in kept}); rs_=random.Random(SEED); rs_.shuffle(ids); nv=math.ceil(0.2*len(ids)); valid=set(ids[:nv])
for r in kept: r['split']='valid' if r['id'] in valid else 'train'
def code_prompt_v2(code,text):
    fmt='{"quote": "verbatim quote or empty", "status": "PRESENT|ABSENT|CANNOT_TELL|NOT_APPLICABLE", "reason": "reason or empty"}'
    return RULES+'\n\nCODE\n\n'+code_block(code)+'\n\nTEXT\n'+text+'\n\nAnswer with one JSON object only, in this form: '+fmt
def row(r):
    l=r['label']; tgt={'quote':l['quote'],'status':l['status'],'reason':l['reason']}
    return {'messages':[{'role':'user','content':code_prompt_v2(r['code'],pool[r['id']]['text'])},{'role':'assistant','content':json.dumps(tgt)}]}
w=lambda p,rs:open(p,'w').write('\n'.join(json.dumps(x) for x in rs)+('\n' if rs else ''))
D=S+'/data/silver_v2%s/'%SUF; os.makedirs(D,exist_ok=True)
w(D+'silver_all.jsonl',silver); w(D+'unused_cap.jsonl',capped); w(D+'dropped_non_quotable.jsonl',dropped)
w(D+'train.jsonl',[row(r) for r in kept if r['split']=='train']); w(D+'valid.jsonl',[row(r) for r in kept if r['split']=='valid'])
w(D+'train_meta.jsonl',[{'id':r['id'],'code':r['code'],'status':r['label']['status']} for r in kept if r['split']=='train'])
w(D+'valid_meta.jsonl',[{'id':r['id'],'code':r['code'],'status':r['label']['status']} for r in kept if r['split']=='valid'])
# classes
STS=['PRESENT','ABSENT','CANNOT_TELL','NOT_APPLICABLE']
cls={'seed':SEED,'papers_with_kept_rows':len(ids),'valid_papers':nv,'valid_paper_share':round(nv/len(ids),3),'codes':{}}
for c in CODES:
    tr=collections.Counter(r['label']['status'] for r in kept if r['code']==c and r['split']=='train')
    va=collections.Counter(r['label']['status'] for r in kept if r['code']==c and r['split']=='valid')
    nt=sum(tr.values()); nvv=sum(va.values())
    pl=max(STS,key=lambda s:(tr[s],-STS.index(s))) if nt else None
    d={'before_cap':before[c],'after_cap':after[c],'train':dict(tr),'valid':dict(va),'train_rows':nt,'valid_rows':nvv,'under_15_train':nt<15,
       'plurality_status_train':pl,'plurality_rate_valid':round(va[pl]/nvv,3) if nvv and pl else None,
       'constant_CT_rate_valid':round(va['CANNOT_TELL']/nvv,3) if nvv else None,
       'train_largest_share':round(max(tr.values())/nt,3) if nt else None}
    cls['codes'][c]=d
tv=collections.Counter(); 
for c in CODES: tv.update(cls['codes'][c]['valid'])
cls['pooled_valid']=dict(tv); cls['train_rows']=sum(cls['codes'][c]['train_rows'] for c in CODES); cls['valid_rows']=sum(cls['codes'][c]['valid_rows'] for c in CODES)
cls['pooled_constant_CT_rate_valid']=round(tv['CANNOT_TELL']/max(1,sum(tv.values())),3)
cls['pooled_plurality_rate_valid']=round(max(tv.values())/max(1,sum(tv.values())),3)
cls['per_code_plurality_pooled_rate_valid']=round(sum(cls['codes'][c]['valid'].get(cls['codes'][c]['plurality_status_train'],0) for c in CODES if cls['codes'][c]['plurality_status_train'])/max(1,cls['valid_rows']),3)
cls['capped_rows']=dict(collections.Counter('%s %s'%(r['code'],r['label']['status']) for r in capped))
cls['silver_by_via']=dict(collections.Counter(r['via'] for r in silver))
cls['ct_by_via_code']=dict(collections.Counter('%s %s'%(r['code'],r['via']) for r in silver if r['label']['status']=='CANNOT_TELL'))
json.dump(cls,open(S+'/results/silver_v2_classes%s.json'%SUF+'','w'),indent=1)
json.dump({'rule_counts':dict(log),'teacher_calls_round1_by_status_flag':{'|'.join(k):v for k,v in calls.items()},'silver_rows':len(silver),'kept_after_cap':len(kept),'capped_out':len(capped),'dropped_non_quotable':len(dropped)},open(S+'/results/silver_v2_log%s.json'%SUF+'','w'),indent=1)
print(json.dumps({c:(cls['codes'][c]['before_cap'],cls['codes'][c]['after_cap'],cls['codes'][c]['train'],cls['codes'][c]['valid']) for c in CODES})); print(dict(log)); print(cls['train_rows'],cls['valid_rows'],cls['pooled_constant_CT_rate_valid'],cls['valid_papers'],cls['papers_with_kept_rows'])
