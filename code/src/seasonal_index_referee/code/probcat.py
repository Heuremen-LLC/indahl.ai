import numpy as np,sys
sys.path.insert(0,'.')
from boot import rd
for v in ['temp','prec']:
    A=rd(f'{v}01_forecast_above.bi');B=rd(f'{v}01_forecast_below.bi');C=rd(f'{v}01_forecast.bi');O=rd(f'{v}_seas_verif.bi');m=O[0]!=-9999
    for sh in (-1,0,1):
        n=len(O);ok=0;tot=0
        for i in range(max(0,-sh),min(n,n-sh)):
            a=A[i+sh][m];b=B[i+sh][m];c=C[i][m];ii=np.isin(c,[1,2,3])
            pred=np.where(a>b,3,np.where(b>a,1,2))
            # compare: category 3 <-> above is max & >=? 
            ok+=(pred[ii]==c[ii]).sum();tot+=ii.sum()
        print(v,'prob-vs-category agreement, prob record shift',sh,round(ok/tot,4))
    # rows where cat=3 but above<=below etc at shift 0
    a=A[:len(O)][:,m];b=B[:len(O)][:,m];c=C[:len(O)][:,m]
    print(v,'cat3 mean above',a[c==3].mean(),'min',a[c==3].min(),'cat1 mean below',b[c==1].mean(),'min',b[c==1].min(),'cat2 near mean above/below',a[c==2].mean(),b[c==2].mean(), 'EC above range',a[c==0].min(),a[c==0].max())
