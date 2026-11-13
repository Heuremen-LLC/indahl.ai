from common import *
rng=np.random.default_rng(5)
W=(30,90,300)
print('Per chip: X on all qubits then idle w us then read (deciding_runs gates job, 2 copies x 1000 shots = 2000 shots/point). Compared with IBM T1, prob_meas1_prep0, prob_meas0_prep1 in the props saved at firing.')
for chip in ['ibm_fez','ibm_kingston','ibm_marrakesh','ibm_phoenix']:
    J=json.load(open(R+f'deciding_runs/job_gates_{chip}.json')); z=np.load(R+f'deciding_runs/raw_gates_{chip}.npz'); P=json.load(open(R+f'deciding_runs/props_gates_{chip}.json')); Q=qprops(P)
    n=J['n_qubits'] if 'n_qubits' in J else len(Q); meta=J['meta']
    sub=D.datetime.strptime(J['submitted'],'%Y-%m-%dT%H:%M:%S%z')
    Pm={}; Ns={}
    for w in W:
        ii=[i for i,m in enumerate(meta) if m.get('arm')=='G' and m.get('ref_wait_us')==w]
        x=np.concatenate([bits(z['c_%d'%i],n) for i in ii]); Pm[w]=x.mean(0); Ns[w]=x.shape[0]
    T1=np.array([q['T1'][0] if 'T1' in q else np.nan for q in Q]); t1age=np.array([(sub-pt(q['T1'][1])).total_seconds()/3600 if 'T1' in q else np.nan for q in Q])
    e01=np.array([q['prob_meas1_prep0'][0] for q in Q]); e10=np.array([q['prob_meas0_prep1'][0] for q in Q])
    ok=np.isfinite(T1)&np.isfinite(e01)&np.isfinite(e10)
    print('\n==',chip,'job',str(sub)[:16],'props',P['last_update_date'][:16],'n qubits with T1',ok.sum(),'median IBM T1 %.1f us (qubit-wise age median %.1f h, max %.1f h)'%(np.nanmedian(T1),np.nanmedian(t1age),np.nanmax(t1age)))
    # A: prediction from published numbers only, measured minus predicted, per delay
    s=lambda w: np.exp(-w/T1)
    for w in W:
        pred=(1-e10)*s(w)+e01*(1-s(w)); d=(Pm[w]-pred)[ok]
        m,ci,k=boot_median(d)
        print('  delay %3d us: median measured P(1) %.4f, predicted from IBM numbers %.4f | median(measured-predicted) %+.4f [%+.4f,%+.4f] n=%d -> %s'%(w,np.median(Pm[w][ok]),np.median(pred[ok]),m,ci[0],ci[1],k,outcome(ci)))
    # implied T1 from our points, corrected with IBM readout probs
    def sc(w): return (Pm[w]-e01)/(1-e10-e01)
    def tau(a,b):
        with np.errstate(all='ignore'): return (b-a)/np.log(sc(a)/sc(b))
    for a,b in ((30,90),(90,300),(30,300)):
        t=tau(a,b); m,ci,k=boot_median(t[ok]); 
        r=t/T1; mr,cir,kr=boot_median(np.where(np.isfinite(r),r,np.nan)[ok])
        print('  our decay time from points %d->%d us: median %.1f us; ratio to the same qubit\'s IBM T1: median %.3f [%.3f,%.3f] n=%d'%(a,b,m,mr,cir[0],cir[1],kr))
    # B: shape. per qubit tau(90->300) vs tau(30->90): if single exponential, equal (up to shot noise)
    ta=tau(30,90); tb=tau(90,300)
    # shot-noise null: simulate pure exponential with tau_c per qubit, same readout probs, same shots
    tc=tau(30,300)
    okk=ok&np.isfinite(ta)&np.isfinite(tb)&np.isfinite(tc)&(tc>0)
    obs=np.median(np.log(tb[okk]/ta[okk]))
    nulls=[]
    for rep in range(200):
        Ps={}
        for w in W:
            sw=np.exp(-w/tc); p=(1-e10)*sw+e01*(1-sw); Ps[w]=rng.binomial(Ns[w],np.clip(np.nan_to_num(p,nan=0.5),0,1))/Ns[w]
        def scs(w): return (Ps[w]-e01)/(1-e10-e01)
        with np.errstate(all='ignore'):
            ta_=(90-30)/np.log(scs(30)/scs(90)); tb_=(300-90)/np.log(scs(90)/scs(300))
        g=okk&np.isfinite(ta_)&np.isfinite(tb_)&(ta_>0)&(tb_>0)
        nulls.append(np.median(np.log(tb_[g]/ta_[g])))
    print('  SHAPE: median over qubits of ln(tau[90->300]/tau[30->90]) = %+.3f (n=%d); pure-exponential same-noise null: mean %+.3f, 95%% range [%+.3f,%+.3f]; share of qubits with tau[90->300] > tau[30->90]: %.0f%%'%(obs,okk.sum(),np.mean(nulls),*np.percentile(nulls,[2.5,97.5]),100*np.mean(tb[okk]>ta[okk])))
    # claim-style test: P(30) below P(300)^0.1 (raw levels, readout error NOT removed) observed vs pure-exp null with IBM readout probs and shot noise
    obsb=np.mean((Pm[30]<Pm[300]**0.1)[ok])
    nb=[]
    for rep in range(200):
        Ps={}
        for w in (30,300):
            sw=np.exp(-w/tc); p=(1-e10)*sw+e01*(1-sw); Ps[w]=rng.binomial(Ns[w],np.clip(np.nan_to_num(p,nan=0.5),0,1))/Ns[w]
        nb.append(np.mean((Ps[30]<Ps[300]**0.1)[okk]))
    nb0=[]
    for rep in range(200):
        Ps={}
        for w in (30,300):
            sw=np.exp(-w/tc); Ps[w]=rng.binomial(Ns[w],np.clip(np.nan_to_num(sw,nan=0.5),0,1))/Ns[w]
        nb0.append(np.mean((Ps[30]<Ps[300]**0.1)[okk]))
    print('  BELOW-THE-LINE share (site definition P30 < P300^0.1, raw levels): observed %.0f%%; pure exponential, no readout error, shot noise only: %.0f%%; pure exponential WITH IBM readout error + shot noise: %.0f%% [%.0f-%.0f]'%(100*obsb,100*np.mean(nb0),100*np.mean(nb),*[100*v for v in np.percentile(nb,[2.5,97.5])]))
    # readout-corrected version of the same test
    obsc=np.mean((sc(30)<sc(300)**0.1)[okk]); 
    print('  same test AFTER removing readout error with IBM probs: observed %.0f%%'%(100*obsc))
    # per-delay medians for the table
    print('  levels (median over qubits): P30 %.3f P90 %.3f P300 %.3f'%(np.median(Pm[30][ok]),np.median(Pm[90][ok]),np.median(Pm[300][ok])))
