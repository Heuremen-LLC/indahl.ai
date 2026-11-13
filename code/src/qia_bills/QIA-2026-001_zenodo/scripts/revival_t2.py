from common import *
for chip in ['ibm_fez','ibm_phoenix']:
    J=json.load(open(R+f'deciding_runs/job_revival_{chip}.json')); z=np.load(R+f'deciding_runs/raw_revival_{chip}.npz'); P=json.load(open(R+f'deciding_runs/props_revival_{chip}.json')); Q=qprops(P)
    A=J['info']['A']; nA=len(A); meta=J['meta']; sub=D.datetime.strptime(J['submitted'],'%Y-%m-%dT%H:%M:%S%z')
    T2=np.array([Q[q]['T2'][0] if 'T2' in Q[q] else np.nan for q in A]); T1=np.array([Q[q]['T1'][0] if 'T1' in Q[q] else np.nan for q in A])
    age=np.array([(sub-pt(Q[q]['T2'][1])).total_seconds()/3600 if 'T2' in Q[q] else np.nan for q in A])
    def C(arm,tau):
        o=[]
        for st in 'XY':
            ii=[i for i,m in enumerate(meta) if m['arm']==arm and m['tau']==tau and m['setting']==st]
            x=np.concatenate([bits(z['a_%d'%i],nA) for i in ii]); o.append(1-2*x.mean(0))
        return np.hypot(*o)
    taus=sorted({m['tau'] for m in meta})
    print('\n==',chip,'job',str(sub)[5:16],'A qubits',nA,'IBM T2 median %.1f us, T1 median %.1f us, T2 age median %.1f h'%(np.nanmedian(T2),np.nanmedian(T1),np.nanmedian(age)),'shots/point',2*500)
    c2={a:C(a,2) for a in '01+'}
    for t in (26,58,90):
        pred=np.exp(-(t-2)/T2)
        for a in '0+':
            r=C(a,t)/c2[a]; m,ci,k=boot_median(r-pred)
            imp=-(t-2)/np.log(np.clip(r,1e-3,0.999)); mi,cii,ki=boot_median((imp/T2)[np.isfinite(T2)&(r>0.1)])
            print('  neighbours in %s, tau 2->%2d us: median C ratio %.3f vs exp(-dt/T2_IBM) %.3f | diff %+.3f [%+.3f,%+.3f] -> %-10s | implied/IBM T2 median %.2f [%.2f,%.2f] (n=%d)'%(a,t,np.nanmedian(r),np.nanmedian(pred),m,ci[0],ci[1],outcome(ci),mi,cii[0],cii[1],ki))
