from common import *
import glob
from scipy.stats import spearmanr
files=[f for f in glob.glob(R+'**/*prop*.json',recursive=True) if 'synth' not in f and 'dd_coherence' not in f]
for chip in ['ibm_fez','ibm_kingston','ibm_marrakesh']:
    cyc={}  # readout stamp -> q props
    t1c={}
    for f in files:
        try: P=json.load(open(f))
        except: continue
        if not isinstance(P,dict) or P.get('backend_name')!=chip or 'qubits' not in P: continue
        Q=qprops(P)
        rs=Q[0]['readout_error'][1]; cyc.setdefault(rs,Q)
    ks=sorted(cyc)
    print(chip,'distinct readout-calibration cycles in saved records:',len(ks))
    prev=None
    for k in ks:
        Q=cyc[k]
        e01=np.array([q['prob_meas1_prep0'][0] for q in Q]); e10=np.array([q['prob_meas0_prep1'][0] for q in Q]); re=np.array([q['readout_error'][0] for q in Q])
        s='  %s  median prob_meas1_prep0 %.4f  prob_meas0_prep1 %.4f  readout_error %.4f'%(k[5:16],np.median(e01),np.median(e10),np.median(re))
        if prev is not None:
            pe=np.array([q['readout_error'][0] for q in prev]); d=re-pe
            rho=spearmanr(re,pe)[0]
            s+=' | vs previous cycle: median per-qubit |change| %.4f (%.0f%% of median), median change %+.4f, rank corr %.2f'%(np.median(abs(d)),100*np.median(abs(d))/np.median(pe),np.median(d),rho)
        print(s); prev=Q
    # T1 distinct stamps: use per-qubit T1 value changes between records
    recs=[]
    for f in files:
        try: P=json.load(open(f))
        except: continue
        if not isinstance(P,dict) or P.get('backend_name')!=chip or 'qubits' not in P: continue
        recs.append((P['last_update_date'],qprops(P)))
    recs.sort(key=lambda x:x[0]); seen=set(); last=None
    for lu,Q in recs:
        t1=tuple(round(q['T1'][0],6) if 'T1' in q else None for q in Q)
        if t1 in seen: continue
        seen.add(t1)
        a=np.array([x if x else np.nan for x in t1])
        s='  T1 set (record %s): median T1 %.1f us'%(lu[5:16],np.nanmedian(a))
        if last is not None:
            ok=np.isfinite(a)&np.isfinite(last); r=a[ok]/last[ok]
            s+=' | vs previous distinct T1 set: median per-qubit ratio %.2f, 10th-90th pct of ratio %.2f-%.2f, rank corr %.2f, n=%d'%(np.median(r),*np.percentile(r,[10,90]),spearmanr(a[ok],last[ok])[0],ok.sum())
        print(s); last=a
