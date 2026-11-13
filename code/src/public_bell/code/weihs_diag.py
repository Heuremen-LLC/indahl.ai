import weihs_tables as w, numpy as np, sys
sys.path.insert(0,'.')
import bellsort as bs
names=['longdist%d'%k for k in [0,1,2,3,4,5,10,11,12,13,20,22,23,30,31,32,33,34,35,36,37]]
rows=[]
for n in names:
    tA,a,x=w.load('Alice','longdist',n); tB,b,y=w.load('Bob','longdist',n)
    peak,_,_=w.find_peak(tA,tB); ia,ib=w.coincidences(tA,tB,peak,1.5e-9)
    o=np.argsort(tA[ia]); ia,ib=ia[o],ib[o]
    t=tA[ia]; rows.append(np.stack([t, a[ia], b[ib], x[ia], y[ib], np.full(ia.size, len(rows))],1))
D=np.concatenate(rows)
t,ca,cb,cx,cy,f=D.T; ca,cb,cx,cy,f=[v.astype(int) for v in (ca,cb,cx,cy,f)]
m=np.arange(1,len(t)-1); m=m[(f[m-1]==f[m])&(f[m+1]==f[m])]
gap_next=t[m+1]-t[m]; gap_prev=t[m]-t[m-1]
print('coincidence gaps quantiles (us)', np.quantile(gap_next,[.01,.05,.1,.5])*1e6)
s0=ca[m]*2+cb[m]; out=cx[m]*2+cy[m]
for tag,j,g in (('later',m+1,gap_next),('earlier',m-1,gap_prev)):
    key=ca[j]*2+cb[j]
    for lo,hi in [(0,2e-6),(2e-6,10e-6),(10e-6,50e-6),(50e-6,200e-6),(200e-6,1)]:
        sel=(g>=lo)&(g<hi)
        T=np.zeros((4,4,4),int); np.add.at(T,(s0[sel],key[sel],out[sel]),1)
        r,_=bs.test_table(T,R=0)
        print(tag, f'gap {lo*1e6:6.0f}-{hi*1e6:8.0f} us n={sel.sum():7d} G={r["G"]:9.1f} df={r["df"]} p={r["p_analytic"]:.2g}')
# what drives it at long gaps: correlation E(xy) given current settings, split by next settings
sel=gap_next>200e-6; j=m+1
for s in range(4):
    Es=[]
    for k in range(4):
        mm=sel&(s0==s)&((ca[j]*2+cb[j])==k)
        xy=(2*cx[m][mm]-1)*(2*cy[m][mm]-1); Es.append(f'{xy.mean():+.3f}(n={mm.sum()})')
    print('current (a,b)=',divmod(s,2),' E(xy) by next (a,b)=00,01,10,11:',' '.join(Es))
