import numpy as np
D='/Users/heuremen/bones-forge/seasonal_index/data/raw/cpc_verif_grid/'
rd=lambda f:np.fromfile(D+f,dtype='<f4').reshape(-1,684)
ob=rd('temp_seas_verif.bi'); m=(ob!=-9999)
print('mask same all seasons',(m==m[0]).all(), m[0].sum(), 'seasons w/ different mask',(~(m==m[0]).all(1)).sum(), 'cells ever',m.any(0).sum())
g=m[0].reshape(19,36)
for r in range(19): print(''.join('#' if x else '.' for x in g[r]))
# lon index j->130W+2j ; lat row r ->20N+2r
r,c=np.where(g); print('lat rows',r.min(),r.max(),'cols',c.min(),c.max())
def at(lon,lat): return g[(lat-20)//2,(130-lon)//2]
print('Florida 82W 28N',at(82,28),' Pacific',at(128,22),' Atlantic',at(62,54))
# row0 = south? Florida should be near bottom; check north row has land (Canada border 49N)
print('rows with land: south(20N)=',g[0].sum(),' north end',g[18].sum(), 'mid',g[14].sum())
for v in ['temp','prec']:
    a=rd(f'{v}01_forecast_above.bi');b=rd(f'{v}01_forecast_below.bi');o=rd(f'{v}_seas_verif.bi')
    n=len(o); mm=o!=-9999
    A=a[:n][mm];B=b[:n][mm]
    print(v,'above range',A.min(),A.max(),'below',B.min(),B.max(),'near range',(100-A-B).min(),(100-A-B).max(),'nan',np.isnan(A).sum(),np.isnan(B).sum())
    print(' share A==33.33ish',np.mean(np.abs(A-33.33)<0.01), 'unique count',len(np.unique(np.round(A,2))))
    ct=rd(f'{v}01_forecast.bi')[:n][mm]; print(' ct integer share',np.isin(ct,[0,1,2,3]).mean(), 'EC share',(ct==0).mean(), ' ct nonint share',(~np.isin(ct,[0,1,2,3])).mean())
    # does EC category coincide with A=B=33.33?
    ec=ct==0; print(' EC rows: mean|A-33.3|',np.abs(A[ec]-33.33).mean(), ' non-EC & A==33.33 share', np.mean(np.abs(A[~ec]-33.33)<0.02))
    # forecasts beyond obs
    print(' last 3 fc records land mask? nonzero stated', [(np.abs(a[n+k]-0)>0).sum() for k in range(3)], 'values',np.unique(np.round(a[n],0))[:8])
