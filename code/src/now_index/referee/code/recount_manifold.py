#!/usr/bin/env python3
"""Independent recount of PLAN.md source 3 resolved set from raw files only."""
import json,glob,os,math,random,collections,datetime as D
B='/Users/heuremen/bones-forge/now_index/'
def utc(y,m,d,h=0,mi=0,s=0): return int(D.datetime(y,m,d,h,mi,s,tzinfo=D.timezone.utc).timestamp()*1000)
LO=utc(2025,1,1); HI=utc(2026,10,31,23,59,59); DAY=86400000
mk={}
for f in sorted(glob.glob(B+'data/raw/manifold/search_resolved_*.json')):
    for m in json.load(open(f)): mk.setdefault(m['id'],m)
print('unique resolved markets in raw:',len(mk))
cnt=collections.Counter(); rows={}
for m in mk.values():
    if m.get('outcomeType')!='BINARY': cnt['not binary']+=1; continue
    if m.get('uniqueBettorCount',0)<50: cnt['<50 bettors']+=1; continue
    ts=[t for t in (m.get('closeTime'),m.get('resolutionTime')) if t]
    ref=min(ts)
    if not(LO<=ref<=HI): cnt['outside window']+=1; continue
    if m.get('resolution') not in('YES','NO'): cnt['resolution '+str(m.get('resolution'))]+=1; continue
    if m['createdTime']>ref-30*DAY: cnt['created <30d']+=1; continue
    t=ref-30*DAY
    fn=B+'data/raw/manifold/bets_%s_%d.json'%(m['id'],t)
    if not os.path.exists(fn): cnt['NO BETS FILE']+=1; print('nofile',m['id']); continue
    bets=json.load(open(fn))
    c=[b for b in bets if not b.get('isCancelled') and b.get('probAfter') is not None and b['createdTime']<t]
    if not c: cnt['no bet before']+=1; continue
    b=max(c,key=lambda b:b['createdTime'])
    rows[m['id']]=(b['probAfter'],1 if m['resolution']=='YES' else 0,len(bets))
    cnt['read']+=1
print(dict(cnt))
rs=json.load(open(B+'data/research/manifold_resolved.json'))
print('researcher counts',rs['counts'])
theirs={r['id']:r for r in rs['rows']}
print('same ids:',set(theirs)==set(rows),len(theirs),len(rows),'only theirs',set(theirs)-set(rows),'only mine',set(rows)-set(theirs))
dp=[(i,abs(theirs[i]['probability']-rows[i][0])) for i in rows if i in theirs]
print('max prob diff',max(d for _,d in dp)); print('n diff>1e-6',sum(d>1e-6 for _,d in dp))
print('resolution mismatches',[i for i in rows if i in theirs and theirs[i]['resolution']!=('YES' if rows[i][1] else 'NO')])
print('bets files hitting limit(20) full:',sum(1 for v in rows.values() if v[2]>=20))
def wilson(k,n,z=1.959964):
    p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return c-h,c+h
bins=[[] for _ in range(10)]
for p,y,_ in rows.values():
    i=min(int(math.floor(p*10+1e-9)),9)
    bins[i].append((p,y))
N=[];H=[]
for i,b in enumerate(bins):
    n=len(b);k=sum(y for _,y in b);N.append(n);H.append(k)
    if n:
        mp=sum(p for p,_ in b)/n;lo,hi=wilson(k,n)
        out='CANNOT_TELL' if n<30 else('ABOVE' if lo>mp else 'BELOW' if hi<mp else 'CONSISTENT')
        print(i,'n=%d happened=%d mean_p=%.4f share=%.4f wilson=(%.4f,%.4f) %s'%(n,k,mp,k/n,lo,hi,out))
print('N',N);print('H',H)
allr=list(rows.values());n=len(allr)
br=sum((p-y)**2 for p,y,_ in allr)/n; base=sum(y for _,y,_ in allr)/n; bb=sum((base-y)**2 for _,y,_ in allr)/n
print('n',n,'brier %.4f base_rate %.4f base_brier %.4f skill %.4f'%(br,base,bb,1-br/bb))
# boundary check: how many probs within 1e-9 of a tenth
print('boundary probs:',[round(p,6) for p,_,_ in allr if abs(p*10-round(p*10))<1e-6])
print('p==1 or 0:',sum(p>=0.999999 for p,_,_ in allr),sum(p<=1e-6 for p,_,_ in allr))
