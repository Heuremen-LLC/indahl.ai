import sys, json, collections, numpy as np, pandas as pd
from sklearn.metrics import f1_score
X=sys.argv[1]; AX=['intent','primary_driver','value_orientation','affect']; NP='No-Persona'; TIE='__tie__'
gold=pd.read_csv(f'{X}/data/pools/sample/step3/gold_final.csv',dtype={'comment_id':str}).set_index('comment_id'); ids=list(gold.index)
def load(cond):
    M={}
    for m in ('gpt','gemini','claude'):
        R={}
        for l in open(f'{X}/results/{cond}/{m}.jsonl'):
            r=json.loads(l); lab=r.get('labels') or {}
            R[r['id']]={a:(NP if lab.get('no_persona') else (lab.get(a) or TIE)) for a in AX}
        M[m]=pd.DataFrame([R.get(i,{a:TIE for a in AX}) for i in ids],index=ids)
    maj={}
    for i in ids:
        maj[i]={}
        for a in AX:
            c=collections.Counter(M[m].loc[i,a] for m in M).most_common(1)[0]; maj[i][a]=c[0] if c[1]>=2 else TIE
    M['majority']=pd.DataFrame([maj[i] for i in ids],index=ids); return M
def mf1(y,p):
    labs=sorted(set(y)); return float(f1_score(y,p,labels=labs,average='macro',zero_division=0))
def score(P,idx): return np.mean([mf1(gold[a].values[idx],P[a].values[idx]) for a in AX])
rng=np.random.default_rng(20261025); B=[rng.integers(0,300,300) for _ in range(2000)]   # 2,000 draws: sklearn per draw is slow
F,A=load('forced_single'),load('abstention_baseline'); full=np.arange(300); res={}
for cond,M in (('forced',F),('abstain',A)):
    for m,P in M.items():
        pt=score(P,full); bs=[score(P,b) for b in B]; lo,hi=np.percentile(bs,[2.5,97.5]); res[(cond,m)]=(pt,bs); print(f'{cond:8s} {m:9s} gold macro-F1 {pt:.2f} [{lo:.2f}, {hi:.2f}]')
gnp=gold.is_no_persona_gold.astype(str).str.lower().eq('true').values
for m in ('gpt','gemini','claude'):
    pred=(A[m]['intent']==NP).values; tp=(pred&gnp).sum(); p=tp/pred.sum(); r=tp/gnp.sum(); fa=pred[~gnp].mean()
    print(f'abstain {m}: NP F1 {2*p*r/(p+r):.2f}  false abstention {100*fa:.1f}% of {(~gnp).sum()}')
print('--- B2 abstain minus forced (paired, same draws)')
for m in ('gpt','gemini','claude','majority'):
    d=np.array(res[('abstain',m)][1])-np.array(res[('forced',m)][1]); pt=res[('abstain',m)][0]-res[('forced',m)][0]; lo,hi=np.percentile(d,[2.5,97.5])
    print(f'  {m:9s} {pt:+.2f} [{lo:+.2f}, {hi:+.2f}] {"ABOVE" if lo>0 else "BELOW" if hi<0 else "CONSISTENT"}')
print('--- B3 abstain ranking (paired)')
for a,b in (('gemini','gpt'),('gpt','claude'),('gemini','claude')):
    d=np.array(res[('abstain',a)][1])-np.array(res[('abstain',b)][1]); pt=res[('abstain',a)][0]-res[('abstain',b)][0]; lo,hi=np.percentile(d,[2.5,97.5])
    print(f'  {a}-{b} {pt:+.3f} [{lo:+.3f}, {hi:+.3f}] {"ABOVE" if lo>0 else "BELOW" if hi<0 else "CONSISTENT"}')
