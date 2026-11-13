import csv, sys, collections, numpy as np
from math import sqrt
T95={1:12.706,2:4.303,3:3.182,4:2.776,5:2.571,6:2.447,7:2.365,8:2.306}
R=list(csv.DictReader(open(sys.argv[1]))); A=collections.defaultdict(list)
for r in R: A[(r['student'],r['benchmark'],r['method'])].append(float(r['accuracy']))
settings=sorted({(s,b) for s,b,m in A if b not in ('CyberMacro','Medical3')}); counts=collections.Counter(); wins=0
for s,b in settings:
    st={m:(np.mean(A[(s,b,m)]),np.std(A[(s,b,m)],ddof=1) if len(A[(s,b,m)])>1 else 0.0,len(A[(s,b,m)])) for m in ('Pristine','EvoKD-Adapted','QEDKS-Adapted','MapSteal (Ours)') if (s,b,m) in A}
    ms=[k for k in st if k.startswith('MapSteal')][0]; others={k:v for k,v in st.items() if k!=ms}
    best=max(others,key=lambda k:others[k][0]); (m1,s1,n1),(m2,s2,n2)=st[ms],others[best]
    if n2>1:
        se=sqrt(s1**2/n1+s2**2/n2); df=se**4/((s1**2/n1)**2/(n1-1)+(s2**2/n2)**2/(n2-1)) if se>0 else 4
        t=T95[max(1,min(8,int(df)))]
    else:
        se=s1/sqrt(n1); t=T95[n1-1]
    d=m1-m2; lo,hi=d-t*se,d+t*se; oc='ABOVE' if lo>0 else 'BELOW' if hi<0 else 'CONSISTENT'; counts[oc]+=1; wins+=d>0
    print(f'{s:11s} {b:18s} MapSteal {m1:6.2f}+-{s1:4.2f} vs best other {best:9s} {m2:6.2f}+-{s2:4.2f}: {d:+5.2f} [{lo:+6.2f}, {hi:+6.2f}] {oc}')
print('settings',len(settings),'| MapSteal mean highest in',wins,'|',dict(counts))
