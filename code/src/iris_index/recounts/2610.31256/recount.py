import json, re, string, sys, glob, os, numpy as np
from collections import Counter
D=sys.argv[1]
def norm(s):
    s=''.join(ch for ch in s.lower() if ch not in set(string.punctuation)); s=re.sub(r'\b(a|an|the)\b',' ',s); return ' '.join(s.split())
def f1(p,t):
    p,t=norm(p).split(),norm(t).split()
    if not p or not t: return float(p==t)
    c=sum((Counter(p)&Counter(t)).values())
    if c==0: return 0.0
    pr,rc=c/len(p),c/len(t); return 2*pr*rc/(pr+rc)
ref={r['name']:r for r in json.load(open(f'{D}/data/13-statistical_robustness/bootstrap_ci.json'))['results']}
S={}
for f in sorted(glob.glob(f'{D}/data/13-statistical_robustness/predictions/*.json')):
    d=json.load(open(f)); name=os.path.basename(f)[:-5]
    s=np.array([f1(p,t) for p,t in zip(d['predictions'],d['ground_truths'])]); em=np.mean([norm(p)==norm(t) for p,t in zip(d['predictions'],d['ground_truths'])])
    S[name]=s; r=ref.get(name,{}).get('metrics',{})
    print(f"{name:40s} n {len(s)} F1 {100*s.mean():6.2f} (theirs {r.get('f1_score',{}).get('point',float('nan')):6.2f})  EM {100*em:5.2f} (theirs {r.get('exact_match',{}).get('point',float('nan')):5.2f})")
rng=np.random.default_rng(20261025); idx=rng.integers(0,137,(20000,137))
def paired(a,b):
    d=a-b; m=d[idx].mean(1); lo,hi=np.percentile(m,[2.5,97.5]); oc='ABOVE' if lo>0 else 'BELOW' if hi<0 else 'CONSISTENT'; return 100*d.mean(),100*lo,100*hi,oc
print('--- B1 paired 5-shot minus 0-shot')
for m in sorted({k.split('__')[1] for k in S if k.startswith('llm__')}):
    a,b=S.get(f'llm__{m}__5shot'),S.get(f'llm__{m}__0shot')
    if a is None or b is None: print(m,'CANNOT_TELL'); continue
    print(f'{m:28s} %+6.2f [%+6.2f, %+6.2f] %s'%paired(a,b))
print('known-good', paired(S['llm__gpt-4o__5shot'],S['llm__gpt-4o__5shot']))
print('--- B2 llama-3.1-8b 5shot minus gpt-4o 5shot: %+.2f [%+.2f, %+.2f] %s'%paired(S['llm__llama-3.1-8b-instruct__5shot'],S['llm__gpt-4o__5shot']))
