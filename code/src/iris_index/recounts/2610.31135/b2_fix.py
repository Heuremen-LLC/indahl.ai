# B2 rerun with the template in the key (first pass merged 'concise' and 'instructional'). Baseline-on-same-200 is DEFINED AFTER THE DATA.
import gzip, json, sys, collections, numpy as np
G=collections.defaultdict(dict); RID=collections.defaultdict(set)
for l in gzip.open(sys.argv[1],'rt'):
    r=json.loads(l)
    if r['task']!='multidoc_qa' or r['model_key'] not in ('pythia-2.8b','mamba-2.8b'): continue
    k=(r['phase'],r['experiment'],r['model_key'],r['prompt_variant'],r['prompt_template'])
    G[k][(r['question_id'],str(r['gold_position']))]=float(r['score']); RID[k].add(r['run_id'])
rng=np.random.default_rng(20261025)
def prim(k,qs): return np.array([np.mean([G[k][(q,p)] for p in ('0','1')])-np.mean([G[k][(q,p)] for p in ('4','5')]) for q in qs])
def ci(v):
    i=rng.integers(0,len(v),(20000,len(v))); m=v[i].mean(1); lo,hi=np.percentile(m,[2.5,97.5]); return '%+.4f [%+.4f, %+.4f] %s'%(v.mean(),lo,hi,'ABOVE' if lo>0 else 'BELOW' if hi<0 else 'CONSISTENT')
b=lambda m:('phase2','matched-2.8b-architecture',m,'liu_baseline','liu_baseline')
print('run ids phase2 vs phase4 pythia same:', RID[b('pythia-2.8b')]==RID[('phase4','scale-pair-2.8b-2.8b','pythia-2.8b','liu_baseline','liu_baseline')])
for k in sorted(G):
    if k[0]!='phase7' or k[2]!='pythia-2.8b': continue
    km=k[:2]+('mamba-2.8b',)+k[3:]; qs=sorted({q for q,p in G[k]} & {q for q,p in G[km]})
    print(k[1],k[3],k[4],'n',len(qs),'pythia-mamba primacy',ci(prim(k,qs)-prim(km,qs)),'| same 200 q, baseline prompt (phase2):',ci(prim(b('pythia-2.8b'),qs)-prim(b('mamba-2.8b'),qs)))
