from common import *
from scipy.stats import spearmanr
rng=np.random.default_rng(3)
for chip in ['ibm_fez','ibm_kingston','ibm_marrakesh','ibm_phoenix']:
    J=json.load(open(R+f'deciding_runs/job_gates_{chip}.json')); z=np.load(R+f'deciding_runs/raw_gates_{chip}.npz'); P=json.load(open(R+f'deciding_runs/props_gates_{chip}.json')); Q=qprops(P)
    n=len(Q); meta=J['meta']; sub=D.datetime.strptime(J['submitted'],'%Y-%m-%dT%H:%M:%S%z')
    def p(w,cp=(0,1)):
        ii=[i for i,m in enumerate(meta) if m.get('arm')=='G' and m.get('ref_wait_us')==w and m['copy'] in cp]
        x=np.concatenate([bits(z['c_%d'%i],n) for i in ii]); return x.mean(0),x.shape[0]
    T1=np.array([q['T1'][0] if 'T1' in q else np.nan for q in Q]); age=np.array([(sub-pt(q['T1'][1])).total_seconds()/3600 if 'T1' in q else np.nan for q in Q])
    e01=np.array([q['prob_meas1_prep0'][0] for q in Q]); e10=np.array([q['prob_meas0_prep1'][0] for q in Q])
    def tauc(P30,P300):
        s30=(P30-e01)/(1-e10-e01); s300=(P300-e01)/(1-e10-e01)
        with np.errstate(all='ignore'): return 270/np.log(s30/s300)
    P30,n30=p(30); P300,n300=p(300)
    t=tauc(P30,P300); ok=np.isfinite(t)&np.isfinite(T1)&(t>0)
    ratio=(t/T1)[ok]
    # copy-to-copy: tau from copy0 vs copy1
    t0=tauc(p(30,(0,))[0],p(300,(0,))[0]); t1_=tauc(p(30,(1,))[0],p(300,(1,))[0]); ok2=np.isfinite(t0)&np.isfinite(t1_)&(t0>0)&(t1_>0)
    rc=np.log(t0[ok2]/t1_[ok2])
    # shot-noise null: log-ratio sd across qubits between independent halves
    print('%-14s n=%d | per-qubit ratio (our tau[30->300] / IBM T1): median %.2f, 10th-90th pct %.2f-%.2f, rank corr %.2f | our own copy0 vs copy1 ln-ratio: sd %.2f (so IBM-vs-ours spread beyond our own repeat noise: %.2f vs %.2f in ln units) | IBM T1 age median %.1f h'%(chip,ok.sum(),np.median(ratio),*np.percentile(ratio,[10,90]),spearmanr(t[ok],T1[ok])[0],np.std(rc),np.std(np.log(ratio)),np.std(rc)/np.sqrt(2),np.nanmedian(age)))
