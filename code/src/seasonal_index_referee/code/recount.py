import numpy as np, json, re, sys
D='/Users/heuremen/bones-forge/seasonal_index/data/raw/cpc_verif_grid/'
def rd(f): 
    a=np.fromfile(D+f,dtype='<f4'); assert a.size%684==0; return a.reshape(-1,684)
def heid(f):
    L=open(D+f).read().split('\n')[1:]
    return np.array([[float(x) for x in l.split()[1:]] for l in L if l.strip()]),[l.split()[0] for l in L if l.strip()]
out={}
for v in ['temp','prec']:
    ab=rd(f'{v}01_forecast_above.bi');be=rd(f'{v}01_forecast_below.bi');ct=rd(f'{v}01_forecast.bi');ob=rd(f'{v}_seas_verif.bi')
    print(v,ab.shape,ob.shape,np.unique(ob),np.unique(ct)[:6])
    H,dates=heid(f'{v}01.heidke.txt'); print(len(H),dates[0],dates[-1])
    # orientation alternatives on 36x19 grid, record layout (lat=19 rows, lon=36 cols) C-order vs other
    def score(fc,obs,shiftf,shifto,perm):
        res=[]
        for i in range(len(H)):
            fi=i+shiftf; oi=i+shifto
            if fi<0 or oi<0 or fi>=len(fc) or oi>=len(obs): res.append(np.nan);continue
            f=fc[fi]; o=obs[oi]
            if perm=='T': f=f.reshape(19,36).T.ravel() ; # wrong orientation applied to fc only
            if perm=='flip': f=f[::-1]
            m=(o!=-9999)&np.isin(f,[1,2,3])
            T=m.sum(); 
            if T<=0: res.append(np.nan);continue
            Hc=(f[m]-2==o[m]).sum(); E=T/3; res.append(100*(Hc-E)/(T-E))
        return np.array(res)
    for sf in [-2,-1,0,1,2]:
        for perm in ['id','flip','T']:
            r=score(ct,ob,sf,0,perm); ok=~np.isnan(r)&~np.isnan(H[:,0])
            d=np.abs(r[ok]-H[ok,0]); print(v,'fc shift',sf,perm,'n',ok.sum(),'mean|d|',round(d.mean(),3) if ok.sum() else None, 'within0.05',(d<0.05).mean() if ok.sum() else None)
    # obs shift via mapping: shift obs vs heidke rows
    for so in [-1,1]:
        r=score(ct,ob,0,so,'id'); ok=~np.isnan(r)&~np.isnan(H[:,0]); d=np.abs(r[ok]-H[ok,0]); print(v,'obs shift',so,'mean|d|',round(d.mean(),3))
