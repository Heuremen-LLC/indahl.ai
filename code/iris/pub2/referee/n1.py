import json,sys,re,string,numpy as np
from collections import Counter
D=sys.argv[1]
exec(open('recounts/2610.31256/recount.py').read().split("ref={")[0].replace("D=sys.argv[1]","D=sys.argv[1]"))
def load(n):
    d=json.load(open(f'{D}/data/13-statistical_robustness/predictions/{n}.json')); return d
a=load('llm__llama-3.1-8b-instruct__5shot'); b=load('llm__gpt-4o__5shot')
print(a['ground_truths']==b['ground_truths'], [k for k in a.keys()])
fa=np.array([f1(p,t) for p,t in zip(a['predictions'],a['ground_truths'])]); fb=np.array([f1(p,t) for p,t in zip(b['predictions'],b['ground_truths'])])
la=np.array([len(norm(p).split()) for p in a['predictions']]);lb=np.array([len(norm(p).split()) for p in b['predictions']]);lt=np.array([len(norm(t).split()) for t in a['ground_truths']])
print('mean len pred llama %.1f gpt4o %.1f gold %.1f'%(la.mean(),lb.mean(),lt.mean()))
d=fa-fb; print('wins',(d>0).sum(),'losses',(d<0).sum(),'ties',(d==0).sum())
pa=[]; 
# precision/recall decomposition
def pr(p,t):
    p,t=norm(p).split(),norm(t).split(); c=sum((Counter(p)&Counter(t)).values()); return (c/len(p) if p else 0, c/len(t) if t else 0)
for nm,x in (('llama',a),('gpt4o',b)):
    v=np.array([pr(p,t) for p,t in zip(x['predictions'],x['ground_truths'])]); print(nm,'prec %.3f recall %.3f'%tuple(v.mean(0)))
