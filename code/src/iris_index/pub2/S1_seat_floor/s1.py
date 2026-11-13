import sys, json, random, importlib.util, numpy as np
TD='/Users/heuremen/bones-forge/triangulation/triangle/'; sys.path.insert(0,TD)
def load(path,name):
    from importlib.machinery import SourceFileLoader; return SourceFileLoader(name,path).load_module()
cur=load(TD+'triangle.py','tri_cur'); old=load(TD+'triangle.py.bak-preFalsePositive','tri_old')
P=[json.loads(l)['prompt'] for l in open('/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/dl_iris_yorke/x/llm-judge-release-main/data/preprocessed_pairs.jsonl')]
W=np.array([len(t.split()) for t in P]); rng=np.random.default_rng(20261025); idx=rng.integers(0,len(P),(20000,len(P)))
res={}
for nm,m in (('current',cur),('pre-fix',old)):
    F=np.array([sum(1 for h in m.exor_scan(t) if h[3]) for t in P]); r=1000*F[idx].sum(1)/W[idx].sum(1); lo,hi=np.percentile(r,[2.5,97.5])
    res[nm]=(1000*F.sum()/W.sum(),lo,hi); print(f'S1a floor {nm}: {res[nm][0]:.2f} [{lo:.2f}, {hi:.2f}] per 1k words on {len(P)} human prompts ({W.sum()} words)')
json.dump(res,open('s1a_floor.json','w'))
import ast
fr=[]
for l in open(TD+'runs/hook_fires.jsonl'):
    r=json.loads(l)
    if r['session']!='1fecc2b7': continue
    for f in (ast.literal_eval(r['frames']) if isinstance(r['frames'],str) else r['frames']):
        if f.get('used',True): fr.append((r['t'],f['kind'],f['hit'],f['ctx']))
pick=random.Random(20261025).sample(fr,min(20,len(fr))); json.dump(pick,open('s1b_sample.json','w'),indent=1)
print('S1b pool',len(fr),'frames; sample drawn (shares not computed):')
for i,(t,k,h,c) in enumerate(pick): print(i,k,'|',c[:200].replace('\n',' '))
