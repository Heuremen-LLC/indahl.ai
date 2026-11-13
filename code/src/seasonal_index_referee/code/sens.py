import numpy as np, json
from boot import *
base={v:cells(v,(12,)) for v in ['temp','prec']}
seeds=[1,2,3,4,5,6,7,8,9,10]
chg={}
for v in ['temp','prec']:
    P,O=load(v);S=len(O)
    # recompute numerators once
    keys=list(base[v].keys())
    for sd in seeds:
        M=mult(S,12,seed=sd)
        # leaning and bins
        def one(sel):
            num=np.zeros(S);den=np.zeros(S);ss=0;n=0
            for c,(X,code) in P.items():
                s=sel(c,X);num+=(s&(O==code)).sum(1);den+=s.sum(1);ss+=X[s].sum();n+=s.sum()
            if not n: return None
            lo,hi=ci(num,den,M);return outcome(lo,hi,ss/n/100,n,int((den>0).sum())),lo,hi
        r={'leaning':one(lambda c,X:X>=40)}
        for c in P:
            for bn,a,b in BINS: r[f'{c}|{bn}']=one(lambda cc,X,c=c,a=a,b=b:(X>=a)&(X<b) if cc==c else np.zeros(X.shape,bool))
        for k,x in r.items():
            if x is None: continue
            if x[0]!=base[v][k][12]['outcome']: chg.setdefault((v,k),[]).append((sd,x[0],round(x[1],4),round(x[2],4)))
print('cells changing outcome under other seeds:',len(chg))
for k,x in chg.items(): print(k,'base',base[k[0]][k[1]][12]['outcome'],base[k[0]][k[1]][12]['lo'],base[k[0]][k[1]][12]['hi'],x)
