import re,collections
L=open('/Users/heuremen/bones-forge/triangulation/triangle/runs/hook_fires.log').read().split('\n')[:374]
rows=[]
for i,l in enumerate(L):
    m=re.match(r'(\S+) session (\S+) mode (\S+) words (\d+) (.*)',l)
    if not m: print('nomatch',i,l[:100]);continue
    rows.append((i+1,m.group(1),m.group(2),m.group(3),int(m.group(4)),m.group(5)))
print(len(rows))
c=collections.Counter((r[2],r[3]) for r in rows); print(c.most_common(20))
c=collections.Counter((r[1][:10]) for r in rows); print(c)
import statistics as st
def cat(r): return 'seated' if r[2]=='1fecc2b7' else ('test' if r[2]=='testtest' else 'cold')
G=collections.defaultdict(list)
for r in rows: G[cat(r)].append(r)
for k,v in G.items():
    pb=[r for r in v if 'PUSHED BACK' in r[5]]
    fr=[r for r in pb if 'Two-lane' in r[5]]
    # other triggers
    print(k,len(v),'pushed',len(pb),'twolane',len(fr),'words med',st.median(r[4] for r in v),'zero-words',sum(r[4]==0 for r in v), 'sum words',sum(r[4] for r in v))
# cold word thresholds
cold=G['cold']
print(sorted(r[4] for r in cold)[:10], sum(r[4]>=300 for r in cold))
for th in (0,200,300,500,800):
    c=[r for r in cold if r[4]>=th]; s=[r for r in G['seated'] if r[4]>=th]
    f=lambda v:(sum('Two-lane' in r[5] for r in v),len(v))
    print(th,'cold',f(c),'seated',f(s))
# pushed-back reasons
print(collections.Counter(re.sub(r'".*?"','',x)[:40] for r in G['seated'] for x in r[5].split('; ')[:1]).most_common(8))
# per day seated
for d in ('2026-10-06','2026-10-07','2026-10-08'):
    s=[r for r in G['seated'] if r[1].startswith(d)]
    pb=sum('PUSHED BACK' in r[5] for r in s); fr=sum('Two-lane' in r[5] for r in s)
    print(d,len(s),pb,fr,sum(r[4] for r in s))
print('=====')
import math, numpy as np
S=G['seated']; C=G['cold']
print('seated words min',min(r[4] for r in S),'n<300',sum(r[4]<300 for r in S),'pushed among <300',sum('PUSHED' in r[5] for r in S if r[4]<300), 'twolane among <300',sum('Two-lane' in r[5] for r in S if r[4]<300))
# day tables
days={}
for d in ('2026-10-06','2026-10-07','2026-10-08'):
    s=[r for r in S if r[1].startswith(d)]
    days[d]=dict(n=len(s),pb=sum('PUSHED' in r[5] for r in s),fr=sum('Two-lane' in r[5] for r in s),w=sum(r[4] for r in s),med=st.median(r[4] for r in s))
print(days)
# widths: day3 vs days1+2 pooled, per reply
def z2(a,n,b,m):
    p=(a+b)/(n+m); return (a/n-b/m)/math.sqrt(p*(1-p)*(1/n+1/m))
d=days;
for key in ('pb','fr'):
    a=d['2026-10-08'][key]; n=d['2026-10-08']['n']
    b=d['2026-10-06'][key]+d['2026-10-07'][key]; m=d['2026-10-06']['n']+d['2026-10-07']['n']
    print(key,'day3 vs 1+2 z',z2(a,n,b,m), 'day3 vs 2', z2(a,n,d['2026-10-07'][key],d['2026-10-07']['n']))
# Poisson rate per 1k words, day3 vs 1+2
def zp(a,w,b,v):
    r1=a/w;r2=b/v; return (r1-r2)/math.sqrt(a/w**2+b/v**2)
a=d['2026-10-08']['fr'];w=d['2026-10-08']['w']/1000; b=d['2026-10-06']['fr']+d['2026-10-07']['fr']; v=(d['2026-10-06']['w']+d['2026-10-07']['w'])/1000
print('rate z day3 vs 1+2',zp(a,w,b,v), 'day3 vs 2', zp(a,w,d['2026-10-07']['fr'],d['2026-10-07']['w']/1000))
# frame-count (quoted strings) per reply
def nfr(t):
    m=re.search(r'Two-lane frame\(s\):(.*?)(?:\. Give|$)',t)
    return len(re.findall(r'"[^"]*"',t.split('. Give')[0])) if 'Two-lane' in t else 0
print('quoted frame strings seated',sum(nfr(r[5]) for r in S),'cold',sum(nfr(r[5]) for r in C))
# logistic
print('#####')
from datetime import datetime
S=sorted(S,key=lambda r:r[1])
T=[datetime.fromisoformat(r[1]) for r in S]
after=[(i) for i in range(1,len(S)) if 'PUSHED' in S[i-1][5] and (T[i]-T[i-1]).total_seconds()<180]
print('rows following a pushback within 3 min',len(after),'of which pushed again',sum('PUSHED' in S[i][5] for i in after))
nonafter=[i for i in range(1,len(S)) if i not in set(after)]
print('others', len(nonafter), sum('Two-lane' in S[i][5] for i in nonafter), sum('PUSHED' in S[i][5] for i in nonafter))
# retries: pushed -> next row
import itertools
print('pushed rows',sum('PUSHED' in r[5] for r in S))
gaps=[(T[i]-T[i-1]).total_seconds() for i in range(1,len(S))]
print(np.percentile(gaps,[10,25,50,75,90]))
# logistic by hand via sklearn?
try:
    from sklearn.linear_model import LogisticRegression
    X=[];y=[]
    for r in S+C:
        X.append([math.log(r[4]), 1 if r in S else 0]); y.append(1 if 'Two-lane' in r[5] else 0)
    m=LogisticRegression(C=1e6).fit(X,y); print('logit coef logw, seated',m.coef_)
    # bootstrap seated coef
    import random
    co=[]
    for _ in range(500):
        idx=[random.randrange(len(X)) for _ in X]
        mm=LogisticRegression(C=1e6).fit([X[i] for i in idx],[y[i] for i in idx]); co.append(mm.coef_[0][1])
    print(np.percentile(co,[2.5,50,97.5]))
except Exception as e: print(e)
# seated, length bins
for lo,hi in ((150,300),(300,500),(500,5000)):
    s=[r for r in S if lo<=r[4]<hi]; c=[r for r in C if lo<=r[4]<hi]
    print(lo,hi,'seated',sum('Two-lane' in r[5] for r in s),len(s),'cold',sum('Two-lane' in r[5] for r in c),len(c))
print('@@@@@')
s=[r for r in S if r[4]>=500]; c=[r for r in C if r[4]>=500]
print('>=500 medians seated',st.median(r[4] for r in s),'cold',st.median(r[4] for r in c))
for lo,hi in ((500,700),(700,1000),(1000,9999)):
    a=[r for r in s if lo<=r[4]<hi]; b=[r for r in c if lo<=r[4]<hi]
    print(lo,hi,'seated',sum('Two-lane' in r[5] for r in a),len(a),'cold',sum('Two-lane' in r[5] for r in b),len(b))
# per-reply within-session cold: sessions
print(len(set(r[2] for r in C)), 'cold sessions; rows',len(C))
# cold date
print(collections.Counter(r[1][:10] for r in C))
# cold first-words
print([r[4] for r in C][:20])
print('$$$$$')
rng=np.random.default_rng(1)
Sf=np.array([('Two-lane' in r[5]) for r in S],float);Sw=np.array([r[4] for r in S],float)
Cf=np.array([('Two-lane' in r[5]) for r in C],float);Cw=np.array([r[4] for r in C],float)
rat=[]
for _ in range(20000):
    i=rng.integers(0,len(Sf),len(Sf));j=rng.integers(0,len(Cf),len(Cf))
    rat.append((Sf[i].sum()/Sw[i].sum())/(Cf[j].sum()/Cw[j].sum()))
print('bootstrap ratio',np.percentile(rat,[2.5,50,97.5]))
# block bootstrap seated by 10 consecutive rows
blocks=[(k,k+10) for k in range(0,len(Sf),10)]
rat=[]
for _ in range(20000):
    ch=rng.integers(0,len(blocks),len(blocks)); idx=np.concatenate([np.arange(*blocks[b]) for b in ch]); idx=idx[idx<len(Sf)]
    j=rng.integers(0,len(Cf),len(Cf))
    rat.append((Sf[idx].sum()/Sw[idx].sum())/(Cf[j].sum()/Cw[j].sum()))
print('block bootstrap ratio',np.percentile(rat,[2.5,50,97.5]))
# per-reply 'at least a frame' saturating: probability of frame vs words in cold: slope?
# prob per 1k words implied: if frames Poisson with rate r per 1k, P(>=1)=1-exp(-r*w)
r_c=Cf.sum()/Cw.sum()*1000
print('cold pred P(>=1) at 1.1k words using seated rate',1-math.exp(-0.763*1.1),'cold observed',Cf.mean())
print('seated pred using cold rate at 0.36k',1-math.exp(-0.595*0.36),'obs',Sf.mean())
