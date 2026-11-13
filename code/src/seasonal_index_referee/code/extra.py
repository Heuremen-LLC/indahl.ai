import numpy as np,sys,math
sys.path.insert(0,'.')
from boot import *
L=[l.split() for l in open(D+'prec01.heidke.txt').read().split('\n')[1:] if l.strip()]
print('prec non-EC around 1997-98 El Nino:',[(l[0],l[1]) for l in L if '19970901'<=l[0]<='19980501'])
# edge weights
S=380;B=12;nb=math.ceil(S/B);w=np.array([sum(1 for s in range(S-B+1) if s<=i<s+B) for i in range(S)])*nb/(S-B+1)
print('expected multiplicity first,6th,12th,interior,last',w[0].round(3),w[5].round(3),w[11].round(3),w[100].round(3),w[-1].round(3),'total',w.sum().round(1))
# circular block bootstrap headline
P,O=load('temp');num=np.zeros(S);den=np.zeros(S)
for c,(X,code) in P.items():
    s=X>=40;num+=(s&(O==code)).sum(1);den+=s.sum(1)
for B in (6,12,24):
    nb=math.ceil(S/B);rng=np.random.default_rng(SEED);st=rng.integers(0,S,size=(REPS,nb));M=np.zeros((REPS,S))
    for r in range(REPS): M[r]=np.bincount(((st[r][:,None]+np.arange(B)[None,:])%S).ravel(),minlength=S)
    print('circular block',B,[round(x,4) for x in ci(num,den,M)])
# iid-by-season (block 1) and cell-iid width for comparison
M=mult(S,1);print('block 1',[round(x,4) for x in ci(num,den,M)])
