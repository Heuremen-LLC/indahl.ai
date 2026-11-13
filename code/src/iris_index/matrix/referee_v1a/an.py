import json,os,csv,collections,re,sys
import numpy as np
H='/Users/heuremen/bones-forge/iris_index/matrix'
sys.path.insert(0,H)
import score_matrix as S
GOLD=S.GNP; MCQ=S.MCQ
rng=np.random.default_rng(1)
def ci(x):
    x=np.array(x,float);i=rng.integers(0,len(x),(2000,len(x)));m=x[i].mean(1);return round(x.mean(),3),round(np.percentile(m,2.5),3),round(np.percentile(m,97.5),3),len(x)
for m in ['gemma3_4b','mistral_7b','phi4-mini','qwen3_4b']:
    d=f'{H}/results/{m}'; R={a:S.rows(d,a) for a in ('nep_abstain','nep_abstain_copy','mcq_A','mcq_A_copy','mcq_A_rev','mcq_B','mcq_batch8')}
    print('=====',m)
    # NEP key / pattern audit
    pat=collections.Counter(); 
    keys=collections.Counter()
    for k,r in R['nep_abstain'].items():
        o,st=S.outcome(r)
        if not isinstance(o,dict): pat[('unp',st)]+=1;continue
        keys[tuple(sorted(o))]+=1
        nl=sum(o.get(f) is None for f in ('intent','primary_driver','value_orientation','affect'))
        pat[(GOLD[k],'np=%r'%o.get('no_persona'),'nulls=%d'%nl)]+=1
    print(keys.most_common(3))
    for k,v in sorted(pat.items(),key=str): print('  ',k,v)
    # strict labeling variants
    def lab_strict(o):  # no_persona flag only
        return o.get('no_persona') is True
    def lab_alt(o): # complete = persona only if flag False and all 4 non-null
        return o.get('no_persona') is True or any(o.get(f) is None for f in ('intent','primary_driver','value_orientation','affect'))
    gp=[k for k in GOLD if GOLD[k]]; gq=[k for k in GOLD if not GOLD[k]]
    for nm,f in (('scorer',lambda o:S.nep_label(o)==('NP',)),('flag-only',lab_strict),('flag-or-any-null',lab_alt)):
        oa=[];fa=[]
        for k in gp: oa.append(float(not f(S.outcome(R['nep_abstain'][k])[0])))
        for k in gq: fa.append(float(f(S.outcome(R['nep_abstain'][k])[0])))
        print(nm,'overattr',ci(oa),'false none',ci(fa))
    # NEP copy
    lab={k:S.nep_label(S.outcome(r)[0]) for k,r in R['nep_abstain'].items()}
    c1={k:S.nep_label(S.outcome(r)[0]) for k,r in R['nep_abstain_copy'].items()}
    print('nep copy disagree',np.mean([lab[k]!=c1[k] for k in lab]),'raw-identical',np.mean([R['nep_abstain'][k]['raw']==R['nep_abstain_copy'][k]['raw'] for k in lab]))
    if m=='qwen3_4b': 
        print('qwen mcq stats'); 
    # MCQ
    A={k:S.content(r)[0] for k,r in R['mcq_A'].items()};Ac={k:S.content(r)[0] for k,r in R['mcq_A_copy'].items()}
    Rv={k:S.content(r)[0] for k,r in R['mcq_A_rev'].items()};B={k:S.content(r)[0] for k,r in R['mcq_B'].items()}
    print('mcq_A raw-identical to copy',np.mean([R['mcq_A'][k]['raw']==R['mcq_A_copy'][k]['raw'] for k in R['mcq_A']]))
    print('terms',{a:collections.Counter((S.content(r)[1] if a.startswith('mcq') and a!='mcq_batch8' else S.outcome(r)[1]) for r in v.values()) for a,v in R.items()})
    if m=='qwen3_4b': continue
    ks=list(A)
    d3=[float(A[k]!=Rv[k])-float(A[k]!=Ac[k]) for k in ks]; print('M3',ci(d3),'raw flip',np.mean([A[k]!=Rv[k] for k in ks]),'copy',np.mean([A[k]!=Ac[k] for k in ks]))
    d5=[float(A[k]!=B[k])-float(A[k]!=Ac[k]) for k in ks]; print('M5',ci(d5),'raw',np.mean([A[k]!=B[k] for k in ks]))
    # letters
    def letter(r):
        o,_=S.outcome(r); return str(o['answer']).strip().upper()[:1]
    lA=collections.Counter(letter(r) for r in R['mcq_A'].values());lR=collections.Counter(letter(r) for r in R['mcq_A_rev'].values());lB=collections.Counter(letter(r) for r in R['mcq_B'].values())
    print('letters A-order',lA,'rev',lR,'B',lB)
    # letter-preserving fraction: same letter both orders => content flips
    same=np.mean([letter(R['mcq_A'][k])==letter(R['mcq_A_rev'][k]) for k in ks]); print('same letter A vs rev',same,'content flips',np.mean([A[k]!=Rv[k] for k in ks]))
    # expected flip under pure letter bias independent: p(A)pA' + p(B)pB'
    pA=lA['A']/200;pR=lR['A']/200
    # pure letter model: content flips iff same letter. P(same)= pA*pR+(1-pA)(1-pR) if independent; if deterministic same letter -> 1 
    print('indep expected flip',pA*pR+(1-pA)*(1-pR))
    # decompose: items where same letter; accuracy
    acc=lambda M:np.mean([M[k]==MCQ[k]['gold'] for k in ks]); print('acc A',acc(A),'rev',acc(Rv),'B',acc(B),'copy',acc(Ac))
    # by source
    for src in ('tomi','bigtom'):
        kk=[k for k in ks if k.startswith(src)]; print(src,len(kk),'flipA-rev',np.mean([A[k]!=Rv[k] for k in kk]),'acc A',np.mean([A[k]==MCQ[k]['gold'] for k in kk]),'acc rev',np.mean([Rv[k]==MCQ[k]['gold'] for k in kk]))
    # batch
    dr=collections.Counter(); lens=collections.Counter()
    for b in R['mcq_batch8'].values():
        o,st=S.outcome(b);ans=o.get('answers') if isinstance(o,dict) else None
        lens[(len(b['items']),len(ans) if isinstance(ans,list) else st)]+=1
    print('batch lens',lens)
