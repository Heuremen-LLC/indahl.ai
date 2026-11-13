import numpy as np,sys,json
sys.path.insert(0,'.')
from boot import *
out={}
for v in ['temp','prec']:
    P,O=load(v);S=len(O)
    num=np.zeros(S);den=np.zeros(S);ss=np.zeros(S);bycat={}
    for c,(X,code) in P.items():
        s=X>=40;num+=(s&(O==code)).sum(1);den+=s.sum(1);ss+=np.where(s,X,0).sum(1)
        bycat[c]=(int(s.sum()),int((s&(O==code)).sum()),float(X[s].mean()/100) if s.any() else None)
    print(v,'leaning rows by cat (n,hits,mean stated)',bycat)
    print(' seasons with zero leaning rows',(den==0).sum(),' top5 seasons share of rows',np.sort(den)[::-1][:5].sum()/den.sum(),' top20 share',np.sort(den)[::-1][:20].sum()/den.sum(),' top 10% seasons (38) share',np.sort(den)[::-1][:38].sum()/den.sum())
    # leave-top-k-out
    order=np.argsort(-den)
    for k in (10,38):
        keep=np.ones(S,bool);keep[order[:k]]=False;print(' without top',k,'rows share kept',den[keep].sum()/den.sum(),'obs',round(num[keep].sum()/den[keep].sum(),4),'stated',round(ss[keep].sum()/den[keep].sum()/100,4))
    # by era (seasons per 5 years)
    for a,b in [(0,120),(120,240),(240,380)]:
        d=den[a:b].sum();print(' era seasons',a,b,'rows',int(d),'stated',round(ss[a:b].sum()/d/100,4),'obs',round(num[a:b].sum()/d,4))
    # per-season observed-vs-stated: fraction of seasons with obs>stated
    ok=den>0;print(' share of seasons obs>stated',((num[ok]/den[ok])>(ss[ok]/den[ok]/100)).mean())
    # whole-grid observed frequency each category all rows (climatology check)
    for c,(X,code) in P.items(): pass
    allobs={k:float((O==k).mean()) for k in(-1,0,1)};print(' observed tercile freq all rows (below,near,above)',allobs)
    # by decade overall obs freq of above
    for a,b in [(0,60),(60,120),(120,180),(180,240),(240,300),(300,380)]:
        print('  seasons',a,b,'obs above',round(float((O[a:b]==1).mean()),3),'below',round(float((O[a:b]==-1).mean()),3),'near',round(float((O[a:b]==0).mean()),3))
    # share of all rows that are equal chances (stated above=below≈33.33)
    A=P['above'][0];B=P['below'][0];print(' share rows near-EC (all within 31-36)',float(((A>=31)&(A<36)&(B>=31)&(B<36)).mean()),' share rows with any category>=40',float(((A>=40)|(B>=40)|(P['near'][0]>=40)).mean()))
    # bin definition: stated values straddling bin labels 
    for c in P:
        X=P[c][0];print(' ',c,'rows with 30<=x<31',int(((X>=30)&(X<31)).sum()),'35<=x<36',int(((X>=35)&(X<36)).sum()),'39<=x<40',int(((X>=39)&(X<40)).sum()),'49<=x<50',int(((X>=49)&(X<50)).sum()))
    # seasons: lowest seasons forecasts include leaning pattern by year
    yr=np.array([1995+i//12 for i in range(S)])
    print(' leaning rows by year', {int(y):int(den[yr==y].sum()) for y in sorted(set(yr))[::4]})
    # equal-chances bin rows: near observed freq for EC (31-36)
    # permutation sense: fraction of EC rows where observed above
    ec=(A>=31)&(A<36)&(B>=31)&(B<36);print(' EC rows obs freq (above,near,below)',[round(float((O[ec]==k).mean()),4) for k in(1,0,-1)])
