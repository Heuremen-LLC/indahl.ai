import numpy as np, json, sys
sys.path.insert(0,'.')
from boot import *
def hf(f):
    L=[l.split() for l in open(D+f).read().split('\n')[1:] if l.strip()];return {l[0]:[float(x) for x in l[1:]] for l in L}
desk=json.load(open('/Users/heuremen/bones-forge/seasonal_index/summary_seasonal.json'))['heidke']
res={}
for v in ['temp','prec']:
    ct=rd(f'{v}01_forecast.bi');O=rd(f'{v}_seas_verif.bi');S=len(O);H=hf(f'{v}01.heidke.txt')
    d1=[];d2=[];d3=[];none=[]
    rows=[]
    for i in range(S):
        key='%04d%02d01'%(1995+i//12,i%12+1);o=O[i];f=ct[i];m=o!=-9999
        ok=m&np.isin(f,[1,2,3]);T=ok.sum()
        cov=100*T/m.sum()
        cp=H[key]
        if T==0 or T==0:
            none.append((key,cp,int(m.sum()),int((f[m]==0).sum()),int((~np.isin(f[m],[0,1,2,3])).sum())));d1.append(np.nan);d2.append(np.nan);continue
        Hc=((f[ok]-2)==o[ok]).sum();E=T/3;ne=100*(Hc-E)/(T-E);al=ne*cov/100
        d1.append(ne-cp[0]);d2.append(al-cp[1]);d3.append(cov-cp[2]);rows.append((key,ne,cp[0],al,cp[1],cov,cp[2]))
    d1=np.array(d1);d2=np.array(d2);ok=~np.isnan(d1)
    print(v,'scored seasons',ok.sum(),'mean diff ne',d1[ok].mean(),'all',d2[ok].mean(),'max|d| ne',np.abs(d1[ok]).max(),'max|d| all',np.abs(d2[ok]).max(),'cov max|d|',np.abs(d3).max())
    print(' within1 ne',(np.abs(d1[ok])<1).sum())
    S_=len(O);M=mult(S_,12)
    for nm,dd in(('ne',d1),('all',d2)):
        o=~np.isnan(dd);lo,hi=ci(np.where(o,dd,0),o.astype(float),M);print(' boot',nm,round(lo,4),round(hi,4))
    print(' seasons with no ours score:',none)
    # CPC rows for those: what does CPC list
    # worst diffs
    w=sorted(rows,key=lambda r:-abs(r[1]-r[2]))[:3];print(' worst ne',w)
    # CPC stated all vs ne*cov
    # CPC EC seasons non-EC values
    # 6 prec seasons: look at cpc rows
    # also all-EC detection: coverage 0
    res[v]=dict(none=none)
    # E/T difference if CPC rounds
    print(' cpc: seasons with coverage 0:',[k for k,x in H.items() if x[2]==0])
json.dump(res,open('../out/heidke_none.json','w'),indent=1,default=str)
