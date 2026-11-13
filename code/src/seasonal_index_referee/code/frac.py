import numpy as np,sys
sys.path.insert(0,'.')
from boot import rd,D
def hf(f):
    L=[l.split() for l in open(D+f).read().split('\n')[1:] if l.strip()];return {l[0]:[float(x) for x in l[1:]] for l in L}
for v in ['temp','prec']:
    ct=rd(f'{v}01_forecast.bi');O=rd(f'{v}_seas_verif.bi');H=hf(f'{v}01.heidke.txt')
    for mode in ['leave','round','floor','ceil']:
        e=[]
        for i in range(len(O)):
            key='%04d%02d01'%(1995+i//12,i%12+1);m=O[i]!=-9999;f=ct[i].copy()
            if mode=='round':f=np.where(np.isin(f,[0,1,2,3]),f,np.round(f))
            if mode=='floor':f=np.where(np.isin(f,[0,1,2,3]),f,np.floor(f))
            if mode=='ceil':f=np.where(np.isin(f,[0,1,2,3]),f,np.ceil(f))
            ok=m&np.isin(f,[1,2,3]);T=ok.sum()
            if T==0:continue
            Hc=((f[ok]-2)==O[i][ok]).sum();ne=100*(Hc-T/3)/(T-T/3*1) if False else 100*(Hc-T/3)/(T-T/3)
            ne=100*(Hc-T/3)/(T-T/3)
            e.append((abs(ne-H[key][0]),abs(100*T/m.sum()-H[key][2])))
        e=np.array(e);print(v,mode,'mean|d|ne',e[:,0].mean().round(4),'max',e[:,0].max().round(3),'n>0.05',(e[:,0]>0.05).sum(),'cov max',e[:,1].max().round(3))
    fr=~np.isin(ct[:len(O)],[0,1,2,3])&(O!=-9999);print(v,'fractional cat cells',fr.sum(),'seasons',fr.any(1).sum(),np.unique(ct[:len(O)][fr]).round(3)[:10])
