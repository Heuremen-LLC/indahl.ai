import gzip, json, sys, collections, numpy as np
G=collections.defaultdict(dict)   # (phase,exp,model,variant) -> {(qid,cond,pos): score}
for l in gzip.open(sys.argv[1],'rt'):
    r=json.loads(l)
    if r['task']!='multidoc_qa': continue
    k=(r['phase'],r['experiment'],r['model_key'],r['prompt_variant'])
    G[k][(r['question_id'],r['condition'],str(r['gold_position']))]=float(r['score'])
rng=np.random.default_rng(20261025)
def mat(k):
    d=G[k]; qs=sorted({q for q,c,p in d}); pos=sorted({p for q,c,p in d if p!='None'},key=int)
    M=np.full((len(qs),10),np.nan); qi={q:i for i,q in enumerate(qs)}
    for (q,c,p),s in d.items():
        if p!='None': M[qi[q],int(p)]=s
    fl=np.mean([s for (q,c,p),s in d.items() if c=='closed_book']) if any(c=='closed_book' for q,c,p in d) else np.nan
    ce=np.mean([s for (q,c,p),s in d.items() if c=='oracle']) if any(c=='oracle' for q,c,p in d) else np.nan
    return qs,M,fl,ce,pos
def edges(M): return M[:,[0,1]].mean(1)-M[:,[4,5]].mean(1), M[:,[8,9]].mean(1)-M[:,[4,5]].mean(1)
def ci(v,B=20000):
    v=v[~np.isnan(v)]; i=rng.integers(0,len(v),(B,len(v))); m=v[i].mean(1); lo,hi=np.percentile(m,[2.5,97.5])
    return v.mean(),lo,hi,('ABOVE' if lo>0 else 'BELOW' if hi<0 else 'CONSISTENT')
def paired(ka,kb,which=0):
    qa,Ma,*_=mat(ka); qb,Mb,*_=mat(kb); com=sorted(set(qa)&set(qb)); A=Ma[[qa.index(q) for q in com]]; B=Mb[[qb.index(q) for q in com]]
    return ci(edges(A)[which]-edges(B)[which]), len(com), A, B
fmt=lambda t:'%+.4f [%+.4f, %+.4f] %s'%t
P2=lambda m:('phase2','matched-2.8b-architecture',m,'liu_baseline'); P3=lambda m:('phase3','matched-8b-pure-vs-hybrid',m,'liu_baseline')
print('--- A. Table 1')
for k in (P2('pythia-2.8b'),P2('mamba-2.8b'),P2('mamba2-2.7b'),P3('mamba2-8b'),P3('mamba2-hybrid-8b')):
    qs,M,fl,ce,pos=mat(k); p,r=edges(M); print(k[2],'n',len(qs),'primacy',fmt(ci(p)),'recency',fmt(ci(r)),'floor %.3f ceiling %.3f'%(fl,ce))
for a,b in ((P2('mamba-2.8b'),P2('pythia-2.8b')),(P2('mamba2-2.7b'),P2('pythia-2.8b')),(P2('mamba2-2.7b'),P2('mamba-2.8b')),(P3('mamba2-hybrid-8b'),P3('mamba2-8b'))):
    (t,n,_,_)=paired(a,b,0); (t2,_,_,_)=paired(a,b,1); print('paired',a[2],'-',b[2],'n',n,'primacy',fmt(t),'recency',fmt(t2))
print('--- B1 copy carrier')
copies={'pythia-2.8b':[P2('pythia-2.8b'),('phase4','scale-pair-2.8b-2.8b','pythia-2.8b','liu_baseline')],
        'mamba-2.8b':[P2('mamba-2.8b'),('phase4','scale-pair-2.8b-2.8b','mamba-2.8b','liu_baseline'),('phase5','pretraining-corpus','mamba-2.8b','liu_baseline')]}
for m,ks in copies.items():
    for i in range(len(ks)):
        for j in range(i+1,len(ks)):
            (t,n,A,B)=paired(ks[i],ks[j],0); agree=np.nanmean(A==B); print(m,ks[i][0],'vs',ks[j][0],'n',n,'item agreement %.4f'%agree,'primacy copy gap',fmt(t))
print('--- B2 prompt carrier')
for k in sorted(G):
    if k[0]=='phase7' and k[2]=='pythia-2.8b':
        km=(k[0],k[1],'mamba-2.8b',k[3]); qs,M,fl,ce,pos=mat(k)
        if not all(str(p) in pos for p in (0,1,4,5)): print(k[1],k[3],'positions',pos,'-> CANNOT_TELL'); continue
        (t,n,_,_)=paired(k,km,0); print(k[1],k[3],'positions',pos,'pythia-mamba primacy',fmt(t))
