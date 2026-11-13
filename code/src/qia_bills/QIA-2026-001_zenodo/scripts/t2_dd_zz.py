from common import *
print('DD run (22 Oct): 117 spectators on the equator, 39 others idle in 0, all idle for N steps of length L (DD off = plain idle; DD on = symmetric X-X echo on every spectator).')
print('Prediction from published numbers only: exp(-t/T2_IBM) x product over spectator-neighbours of |cos(pi * zz_IBM * t)|  (zz scale 1 = as published)')
for chip in ['ibm_fez','ibm_kingston','ibm_marrakesh']:
    J=json.load(open(R+f'dd_run/job_dd_{chip}.json')); z=np.load(R+f'dd_run/raw_dd_{chip}.npz'); P=json.load(open(R+f'dd_run/props_dd_{chip}.json')); Q=qprops(P)
    I=J['info']; S=np.array(I['S']); Sset=set(S.tolist()); n=J['n_qubits']; meta=J['meta']; L=I['L_dt']*4e-3
    zzm,_,_,_=zz_map(P)
    nb={q:[] for q in range(n)}
    for (a,b),v in zzm.items(): nb[a].append((b,v)); nb[b].append((a,v))
    T2=np.array([Q[q]['T2'][0] if 'T2' in Q[q] else np.nan for q in S])
    def ex(dd,N,st):
        ii=[i for i,m in enumerate(meta) if m['dd']==dd and m['mode']=='D' and m['N']==N and m['setting']==st]
        x=np.concatenate([bits(z['fin_%d'%i],n) for i in ii]); return (1-2*x.mean(0))[S]
    def coh(dd,N): return np.hypot(ex(dd,N,'XX'),ex(dd,N,'YY'))
    c0=coh('off',0)
    print('\n==',chip,'L=%.2f us'%L)
    for dd in ('off','on'):
        for N in (4,8,16):
            t=N*L; r=coh(dd,N)/c0
            for scale in (1.0,):
                beat=np.array([np.prod([abs(np.cos(np.pi*scale*v*1e-3*t)) for (b,v) in nb[q] if b in Sset]) for q in S])  # kHz*1e-3 = MHz ; MHz*us = cycles
                pred=np.exp(-t/T2)*beat
                ok=np.isfinite(pred)&(c0>0.3)
                d=(r-pred)[ok]; m,ci,k=boot_median(d)
                pred_noZZ=np.exp(-t/T2)
                d2=(r-pred_noZZ)[ok]; m2,ci2,k2=boot_median(d2)
                print('  DD %-3s N=%2d t=%5.1f us: measured c(N)/c(0) median %.3f | published T2 only %.3f (diff %+.3f [%+.3f,%+.3f] %s) | published T2 x zz beat %.3f (diff %+.3f [%+.3f,%+.3f] n=%d -> %s)'%(dd,N,t,np.median(r[ok]),np.median(pred_noZZ[ok]),m2,ci2[0],ci2[1],outcome(ci2),np.median(pred[ok]),m,ci[0],ci[1],k,outcome(ci)))
