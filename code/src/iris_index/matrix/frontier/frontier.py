import json, csv, re, numpy as np
rng=np.random.default_rng(20261025)
def ci(x,B=2000):
    x=np.asarray(x,float); i=rng.integers(0,len(x),(B,len(x))); m=x[i].mean(1); lo,hi=np.percentile(m,[2.5,97.5]); return (x.mean(),lo,hi,len(x))
S='/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/'
out={}
# F-M1 NepPlural
N=S+'dl_iris_nep/x/NepPlural-main/'; gold={r['comment_id']:r['is_no_persona_gold'].strip().lower()=='true' for r in csv.DictReader(open(N+'data/pools/sample/step3/gold_final.csv'))}
for m in ('gpt','gemini','claude'):
    lab={}
    for l in open(N+f'results/abstention_baseline/{m}.jsonl'):
        r=json.loads(l); lab[r['id']]=bool((r.get('labels') or {}).get('no_persona'))
    out[f'F-M1 over-attribution {m}']=ci([float(not lab[k]) for k in gold if gold[k] and k in lab])
    out[f'F-M1 false abstention {m}']=ci([float(lab[k]) for k in gold if not gold[k] and k in lab])
# UCL judge files
Y=S+'dl_iris_yorke/x/llm-judge-release-main/data/'
P=re.compile(r'\[\[([AB<>=]+)\]\]'); F2=re.compile(r'\[([AB<>=]+)\]'); SC={'A>>B':-2,'A>B':-1,'A=B':0,'B>A':1,'B>>A':2}
def parse(t):
    u=(t or '').upper(); m=P.findall(u) or F2.findall(u); return SC.get(m[-1]) if m else None
def load(f):
    R={}
    for l in open(Y+f):
        r=json.loads(l); a=parse(r['round1'].get('raw')); b=parse(r['round2'].get('raw'))
        R[r['uid']]=(a, -b if b is not None else None)   # both candidate-relative
    return R
# F-M2 copy floor GPT-4.1 October run1 vs run2 (order-averaged sign, their boundary change)
r1,r2=load('october_rerun/run1/C1F1D1.jsonl'),load('october_rerun/run2/C1F1D1.jsonl')
avg=lambda t: None if None in t else (t[0]+t[1])/2
cp=[float(np.sign(avg(r1[u]))!=np.sign(avg(r2[u]))) for u in r1 if u in r2 and avg(r1[u]) is not None and avg(r2[u]) is not None]
out['F-M2 copy floor gpt-4.1 (Oct run1 vs run2, outcome sign)']=ci(cp)
# per-round copy floor (single verdict, same order): the like-for-like floor for F-M3
cp1=[float(np.sign(r1[u][0])!=np.sign(r2[u][0])) for u in r1 if u in r2 and r1[u][0] is not None and r2[u][0] is not None]
out['F-M2 copy floor gpt-4.1 (single round1 verdict sign)']=ci(cp1)
# F-M3 order: round1 vs swapped round2, candidate-relative sign, per judge
for name,f in (('gpt-4.1 (May)','full_factorial/C1F1D1.jsonl'),('gpt-4.1 (Oct run1)','october_rerun/run1/C1F1D1.jsonl'),('claude-sonnet-4.5','L1_swap/C1F1D1.jsonl'),('gemini-2.5-flash','L1_swap_v2_flash_16k/C1F1D1.jsonl'),('gemini-2.5-pro','L1_swap_v2/C1F1D1.jsonl')):
    R=load(f); fl=[float(np.sign(a)!=np.sign(b)) for a,b in R.values() if a is not None and b is not None]
    out[f'F-M3 order flip {name}']=ci(fl)
# GPT-4.1 order flip minus its own single-verdict copy floor, paired on October run1 prompts
o1=[float(np.sign(r1[u][0])!=np.sign(r1[u][1]))-float(np.sign(r1[u][0])!=np.sign(r2[u][0])) for u in r1 if u in r2 and None not in (r1[u][0],r1[u][1],r2[u][0])]
out['F-M3 gpt-4.1 order flip minus copy floor (Oct)']=ci(o1)
# paired judge differences in order flip (shared prompts)
def flips(f): R=load(f); return {u:float(np.sign(a)!=np.sign(b)) for u,(a,b) in R.items() if a is not None and b is not None}
G,C,Fl=flips('full_factorial/C1F1D1.jsonl'),flips('L1_swap/C1F1D1.jsonl'),flips('L1_swap_v2_flash_16k/C1F1D1.jsonl')
for n,(X,Z) in {'claude-sonnet-4.5 minus gpt-4.1':(C,G),'gemini-2.5-flash minus gpt-4.1':(Fl,G),'claude-sonnet-4.5 minus gemini-2.5-flash':(C,Fl)}.items():
    out['F-M3 paired '+n]=ci([X[u]-Z[u] for u in X if u in Z])
for k,(m,lo,hi,n) in out.items():
    oc='ABOVE' if lo>0 else 'BELOW' if hi<0 else 'CONSISTENT'
    print(f'{k:62s} {m:.3f} [{lo:.3f}, {hi:.3f}] n{n}  {oc if ("minus" in k) else ""}')
json.dump({k:list(v) for k,v in out.items()},open('frontier_out.json','w'),indent=1)
