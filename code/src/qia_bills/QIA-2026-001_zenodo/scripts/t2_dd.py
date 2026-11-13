from common import *
for chip in ['ibm_fez','ibm_kingston','ibm_marrakesh']:
    J=json.load(open(R+f'dd_run/job_dd_{chip}.json')); z=np.load(R+f'dd_run/raw_dd_{chip}.npz'); P=json.load(open(R+f'dd_run/props_dd_{chip}.json')); Q=qprops(P)
    I=J['info']; S=np.array(I['S']); n=J['n_qubits']; meta=J['meta']; L=I['L_dt']*4e-3  # us
    sub=D.datetime.strptime(J['submitted'],'%Y-%m-%dT%H:%M:%S%z')
    T2=np.array([Q[q]['T2'][0] if 'T2' in Q[q] else np.nan for q in S]); T1=np.array([Q[q]['T1'][0] if 'T1' in Q[q] else np.nan for q in S])
    age=np.array([(sub-pt(Q[q]['T2'][1])).total_seconds()/3600 if 'T2' in Q[q] else np.nan for q in S])
    def ex(dd,N,st):
        ii=[i for i,m in enumerate(meta) if m['dd']==dd and m['mode']=='D' and m['N']==N and m['setting']==st]
        x=np.concatenate([bits(z['fin_%d'%i],n) for i in ii]); return (1-2*x.mean(0))[S], x.shape[0]
    def coh(dd,N):
        a,ns=ex(dd,N,'XX'); b,_=ex(dd,N,'YY'); return np.hypot(a,b),ns
    c0,ns=coh('off',0)
    print('\n==',chip,'L=%.2f us, job %s, IBM T2 median over spectators %.1f us (age median %.1f h, max %.1f h); shots per setting %d'%(L,str(sub)[5:16],np.nanmedian(T2),np.nanmedian(age),np.nanmax(age),ns))
    for dd in ('off','on'):
        for N in (8,16):
            c,_=coh(dd,N); t=N*L
            with np.errstate(all='ignore'):
                r=c/c0
                imp=-t/np.log(r)
            ok=np.isfinite(imp)&(imp>0)&np.isfinite(T2)&(c0>0.3)
            pred=np.exp(-t/T2)
            d=(r-pred)[np.isfinite(T2)&(c0>0.3)]
            m,ci,k=boot_median(d)
            ratio=(imp/T2)[ok]; mr,cir,kr=boot_median(ratio)
            print('  DD %-3s N=%2d (t=%5.1f us): median coherence ratio c(N)/c(0) %.4f vs exp(-t/T2_IBM) %.4f | median diff %+.4f [%+.4f,%+.4f] n=%d -> %-10s | implied T2 / IBM T2 median %.2f [%.2f,%.2f]'%(dd,N,t,np.nanmedian(r[ok]),np.nanmedian(pred[ok]),m,ci[0],ci[1],k,outcome(ci),mr,cir[0],cir[1]))
