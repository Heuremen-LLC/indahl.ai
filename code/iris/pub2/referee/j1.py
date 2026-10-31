import json,gzip,glob,os,sys,collections,numpy as np,itertools
R=sys.argv[1]; m=json.load(open(f'{R}/manifest.json')); order=m['benchmark_order']; bm=m['collections']['primary']['benchmarks']
Q={};G={};META={}
for s in order:
    for l in gzip.open(f"{R}/{bm[s]['questions']}",'rt'):
        r=json.loads(l); Q[r['id']]=s; META[r['id']]=r
    for l in gzip.open(f"{R}/{bm[s]['ground_truth']}",'rt'): r=json.loads(l); G[r['id']]=r['gold_option_index']
ids=sorted(Q); S=np.array([order.index(Q[i]) for i in ids])
# ToMi category summary
C=collections.Counter(META[i]['category'] for i in ids if Q[i]=='tomi')
for k,v in sorted(C.items()): print(k,v)
def isctrl(i):
    r=META[i]; s=Q[i]; c=r['category']
    if s=='bigtom': return 'control' in c
    if s=='tomi': return c.startswith('memory') or c.startswith('reality') or '_no_tom' in c
    if s=='hitom': return c.startswith('order-0')
    if s=='fantom-short': return c=='tom:belief:accessible:choice'
    return False
C=np.array([isctrl(i) for i in ids]); print('controls by source',{o:int(C[S==k].sum()) for k,o in enumerate(order)},C.sum())
corr={}
for f in sorted(glob.glob(f'{R}/results/primary_predictions/*.jsonl.gz')):
    P={}
    for l in gzip.open(f,'rt'):
        r=json.loads(l); P[r['id']]=r
    corr[os.path.basename(f)[:-9]]=np.array([P[i]['status']=='ok' and P[i]['predicted_index']==G[i] for i in ids],float)
def overall(c,mask):
    return 100*np.mean([c[(S==b)&mask].mean() for b in range(len(order)) if ((S==b)&mask).any()])
allm=np.ones(len(ids),bool)
for k in ('jev','gpt35-1106','luna'): print(k,'all %.2f ctrlfree %.2f'%(overall(corr[k],allm),overall(corr[k],~C)))
# family-clustered bootstrap
fam=np.array([META[i]['family_id'] for i in ids]); 
def boot(a,b,mask,B=5000,seed=1):
    rng=np.random.default_rng(seed); d=a-b; per=[]
    for bi in range(len(order)):
        idx=np.where((S==bi)&mask)[0]
        if len(idx)==0: continue
        fs=fam[idx]; u,inv=np.unique(fs,return_inverse=True)
        sums=np.bincount(inv,weights=d[idx]); cnt=np.bincount(inv).astype(float); per.append((sums,cnt))
    out=[]
    for _ in range(B):
        t=0
        for sums,cnt in per:
            j=rng.integers(0,len(sums),len(sums)); t+=sums[j].sum()/cnt[j].sum()
        out.append(100*t/len(per))
    lo,hi=np.percentile(out,[2.5,97.5]); return overall(a,mask)-overall(b,mask),lo,hi
print('family-boot jev-gpt35 all',boot(corr['jev'],corr['gpt35-1106'],allm))
print('family-boot jev-luna all',boot(corr['jev'],corr['luna'],allm))
print('family-boot jev-gpt35 ctrlfree',boot(corr['jev'],corr['gpt35-1106'],~C))
print('n families per source',{o:len(set(fam[S==k])) for k,o in enumerate(order)})
