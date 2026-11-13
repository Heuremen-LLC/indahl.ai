import json, gzip, glob, sys, os, numpy as np
R=sys.argv[1]; m=json.load(open(f'{R}/manifest.json')); order=m['benchmark_order']; bm=m['collections']['primary']['benchmarks']
Q={}; G={}; CTRL={}
for s in order:
    for l in gzip.open(f"{R}/{bm[s]['questions']}",'rt'):
        r=json.loads(l); Q[r['id']]=s; CTRL[r['id']]='control' in json.dumps({k:v for k,v in r.items() if k not in ('state','question','options')}).lower()
    for l in gzip.open(f"{R}/{bm[s]['ground_truth']}",'rt'):
        r=json.loads(l); G[r['id']]=r['gold_option_index']
ids=sorted(Q); S=np.array([order.index(Q[i]) for i in ids]); C=np.array([CTRL[i] for i in ids])
corr={}
for f in sorted(glob.glob(f'{R}/results/primary_predictions/*.jsonl.gz')):
    P={}
    for l in gzip.open(f,'rt'):
        r=json.loads(l); P[r['id']]=r
    corr[os.path.basename(f)[:-9]]=np.array([P[i]['status']=='ok' and P[i]['predicted_index']==G[i] for i in ids],float)
def overall(c,mask=None):
    mask=np.ones(len(ids),bool) if mask is None else mask
    return 100*np.mean([c[(S==b)&mask].mean() for b in range(len(order)) if ((S==b)&mask).any()])
for k,c in corr.items(): print(f'{k:20s} overall {overall(c):.2f}   excl. controls {overall(c,~C):.2f}')
rng=np.random.default_rng(20261025); groups=[np.where(S==b)[0] for b in range(len(order))]
def boot(a,b,mask=None,B=20000):
    mask=np.ones(len(ids),bool) if mask is None else mask; out=[]
    gs=[g[mask[g]] for g in groups]; gs=[g for g in gs if len(g)]
    da=a-b
    for _ in range(B): out.append(100*np.mean([da[rng.choice(g,len(g))].mean() for g in gs]))
    lo,hi=np.percentile(out,[2.5,97.5]); pt=overall(a,mask)-overall(b,mask); return '%+.2f [%+.2f, %+.2f] %s'%(pt,lo,hi,'ABOVE' if lo>0 else 'BELOW' if hi<0 else 'CONSISTENT')
print('B1 jev - gpt35  all:', boot(corr['jev'],corr['gpt35-1106'],B=5000)); print('B1 jev - luna   all:', boot(corr['jev'],corr['luna'],B=5000))
print('B2 jev - gpt35 excl. controls:', boot(corr['jev'],corr['gpt35-1106'],~C,B=5000))
