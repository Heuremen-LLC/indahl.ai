import json,random,collections
from common import *
cfg=json.load(open(S+'/teachers/config.json'))['teachers']; names=list(cfg)
pool={g['id']:g for g in all_pool()}
R1={n:{r['id']:r for r in jl_read(S+'/teachers/%s_round1.jsonl'%n) if r['set']=='pool'} for n in names}
R2={n:{r['id']:r for r in jl_read(S+'/teachers/%s_round2.jsonl'%n)} for n in names}
cnt=collections.Counter(); silver=[]; review=[]; dis3=[]; per_item_all=collections.Counter(); r1tab=collections.defaultdict(collections.Counter)
for i,g in pool.items():
    if not all(i in R1[n] for n in names): cnt['item_not_yet_labelled_by_all_three']+=1; continue
    allun=True
    for c in CODES:
        l1={n:R1[n][i]['labels'][c] for n in names}
        for n in names: r1tab[c][(n,)+key(l1[n])]+=1
        k1={key(l) for l in l1.values()}
        if len(k1)==1 and 'PARSE_FAILED' not in {x[0] for x in k1}: via='round1'; fin=l1
        else:
            fin=dict(l1)
            for n in names:
                if i in R2[n] and c in R2[n][i]['labels']: fin[n]=R2[n][i]['labels'][c]
            kf=[key(l) for l in fin.values()]
            if len(set(kf))==1 and kf[0][0]!='PARSE_FAILED': via='crosstalk'
            else: via=None
        rec={'id':i,'code':c,'round1':{n:l1[n] for n in names},'final':{n:fin[n] for n in names}}
        if via:
            qs=[l['quote'] for l in fin.values() if l['quote']]
            lab=dict(next(iter(fin.values()))); lab['quote']=min(qs,key=len) if qs else ''
            rec.update(via=via,label=lab); silver.append(rec); cnt[('unanimous_'+via,)+key(lab)]+=1
        else:
            allun=False
            kc=collections.Counter(key(l) for l in fin.values() if l['status']!='PARSE_FAILED'); top=kc.most_common(1)[0] if kc else (None,0)
            if top[1]==2: rec['majority']=list(top[0]); review.append(rec); cnt[('two_of_three',)+tuple(top[0])]+=1
            else: dis3.append(rec); cnt['all_differ_or_parse_failed']+=1
    per_item_all[allun]+=1
# cap
rng=random.Random(1); byc=collections.defaultdict(list)
for r in silver: byc[r['code']].append(r)
kept=[];capped=[]
for c,rs in byc.items():
    cl=collections.defaultdict(list)
    for r in rs: cl[key(r['label'])].append(r)
    lim=len(rs)//2
    # iterate: cap largest class to the size of all others combined (half of total)
    big=max(cl,key=lambda k:len(cl[k])); others=len(rs)-len(cl[big])
    for k,v in cl.items():
        rng.shuffle(v)
        if k==big and len(v)>max(others,1): kept+=v[:max(others,1)]; capped+=v[max(others,1):]
        else: kept+=v
ids=sorted({r['id'] for r in kept}); rng=random.Random(2); rng.shuffle(ids); valid=set(ids[:max(4,len(ids)//20)])
for r in kept: r['split']='valid' if r['id'] in valid else 'train'
def row(r):
    l=r['label']; tgt={'status':l['status'],'reason':l['reason'],'quote':l['quote']}
    return {'messages':[{'role':'user','content':code_prompt(r['code'],pool[r['id']]['text'])},{'role':'assistant','content':json.dumps(tgt)}]}
import os; os.makedirs(S+'/data/silver',exist_ok=True); os.makedirs(S+'/review_queue',exist_ok=True)
w=lambda p,rs:open(p,'w').write('\n'.join(json.dumps(x) for x in rs)+('\n' if rs else ''))
w(S+'/data/silver/silver_all.jsonl',silver); w(S+'/data/silver/unused_cap.jsonl',capped)
w(S+'/data/silver/train.jsonl',[row(r) for r in kept if r['split']=='train']); w(S+'/data/silver/valid.jsonl',[row(r) for r in kept if r['split']=='valid'])
w(S+'/review_queue/two_of_three.jsonl',review); w(S+'/review_queue/all_differ.jsonl',dis3)
summ={'items':len(pool),'items_all_seven_codes_unanimous':per_item_all[True],'silver_pairs':len(silver),'silver_by_via':dict(collections.Counter(r['via'] for r in silver)),
 'silver_by_code':dict(collections.Counter(r['code'] for r in silver)),'train_rows':sum(r['split']=='train' for r in kept),'valid_rows':sum(r['split']=='valid' for r in kept),'unused_cap':len(capped),
 'review_queue_two_of_three':len(review),'all_differ_or_parse_failed':len(dis3),
 'outcomes':{'|'.join(map(str,k)) if isinstance(k,tuple) else k:v for k,v in sorted(cnt.items(),key=str)},
 'kept_by_code_class':{c+'|'+'/'.join(k):sum(1 for r in kept if r['code']==c and key(r['label'])==k) for c in CODES for k in {key(r['label']) for r in kept if r['code']==c}},
 'unanimous_round1_by_code':dict(collections.Counter(r['code'] for r in silver if r['via']=='round1')),'unanimous_after_crosstalk_by_code':dict(collections.Counter(r['code'] for r in silver if r['via']=='crosstalk'))}
json.dump(summ,open(S+'/results/silver_summary.json','w'),indent=1); print(json.dumps(summ,indent=1))
