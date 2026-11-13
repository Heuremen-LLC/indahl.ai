import sys, pandas as pd, numpy as np
d=pd.read_parquet(sys.argv[1]); m=pd.read_csv(sys.argv[2]); g=d.gold_guidance.astype(bool).values
silver=np.where(d.guidance_agrees_with_llm.astype(bool).values, g, ~g)
S={'TF-IDF + LogReg':d.tf_idf_logreg_guidance_prediction,'ModernBERT-base':d.modernbert_base_guidance_prediction,'ModernBERT-large':d.modernbert_large_guidance_prediction}
def met(p):
    tp=(p&g).sum(); fp=(p&~g).sum(); fn=(~p&g).sum(); tn=(~p&~g).sum(); pr=tp/(tp+fp); rc=tp/(tp+fn)
    f1p=2*pr*rc/(pr+rc); prn=tn/(tn+fn); rcn=tn/(tn+fp); f1n=2*prn*rcn/(prn+rcn); return (tp+tn)/len(g),(f1p+f1n)/2,pr,rc
print(m[m.evaluation=='guidance'][['system','accuracy','macro_f1','precision','recall']].to_string(index=False))
rng=np.random.default_rng(20261025); idx=rng.integers(0,len(g),(20000,len(g)))
for k,v in S.items():
    p=v.astype(bool).values; a,f,pr,rc=met(p); print(f'{k:18s} ours: acc {a:.4f} macroF1 {f:.4f} P {pr:.4f} R {rc:.4f}')
a,f,pr,rc=met(silver); print(f'SILVER labeller   acc {a:.4f} macroF1 {f:.4f} P {pr:.4f} R {rc:.4f}')
print('--- B1 silver minus system, accuracy (paired)')
for k,v in S.items():
    p=v.astype(bool).values; dd=((silver==g).astype(float)-(p==g).astype(float)); b=dd[idx].mean(1); lo,hi=np.percentile(b,[2.5,97.5])
    print(f'  {k:18s} {dd.mean():+.3f} [{lo:+.3f}, {hi:+.3f}] {"ABOVE" if lo>0 else "BELOW" if hi<0 else "CONSISTENT"}')
c=silver!=g; print('--- B2 corrected items:',int(c.sum()))
for k,v in S.items():
    p=v.astype(bool).values; print(f'  {k:18s} matches the wrong silver label on {int((p[c]==silver[c]).sum())}/{int(c.sum())}; error rate where silver==gold {np.mean(p[~c]!=g[~c]):.3f}')
