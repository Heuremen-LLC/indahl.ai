# Referee-directed rebuild (25 Oct): control set from the released `category` field; resampling unit family_id.
import json, gzip, glob, os, sys, re, numpy as np
R=sys.argv[1]; m=json.load(open(f'{R}/manifest.json')); order=m['benchmark_order']; bm=m['collections']['primary']['benchmarks']
def is_ctrl(src,cat):
    c=cat.lower()
    if src=='bigtom': return 'control' in c
    if src=='tomi': return c.startswith('memory') or c.startswith('reality') or '_no_tom' in c
    if src.startswith('fantom'): return c=='tom:belief:accessible:choice'
    if src=='hitom': return c.startswith('order-0')
    return False
Q={};G={};C={};FAM={}
for s in order:
    for l in gzip.open(f"{R}/{bm[s]['questions']}",'rt'):
        r=json.loads(l); Q[r['id']]=s; C[r['id']]=is_ctrl(s,r.get('category','')); FAM[r['id']]=r.get('family_id',r['id'])
    for l in gzip.open(f"{R}/{bm[s]['ground_truth']}",'rt'):
        r=json.loads(l); G[r['id']]=r['gold_option_index']
ids=sorted(Q); S=np.array([order.index(Q[i]) for i in ids]); Cm=np.array([C[i] for i in ids]); print('controls:',int(Cm.sum()))
def corr(name):
    P={json.loads(l)['id']:json.loads(l) for l in gzip.open(f'{R}/results/primary_predictions/{name}.jsonl.gz','rt')}
    return np.array([P[i]['status']=='ok' and P[i]['predicted_index']==G[i] for i in ids],float)
j,g=corr('jev'),corr('gpt35-1106')
def ov(c,mask): return 100*np.mean([c[(S==b)&mask].mean() for b in range(len(order)) if ((S==b)&mask).any()])
nm=~Cm; print('excl. controls: jev %.2f gpt35 %.2f'%(ov(j,nm),ov(g,nm)))
fam=np.array([FAM[i] for i in ids]); rng=np.random.default_rng(20261025)
def boot(mask,B=2000):
    out=[]
    for _ in range(B):
        idx=[]
        for b in range(len(order)):
            sel=np.where((S==b)&mask)[0]
            if not len(sel): continue
            fs=np.unique(fam[sel]); pick=rng.choice(fs,len(fs)); 
            byf={}; [byf.setdefault(fam[k],[]).append(k) for k in sel]
            idx.append(np.concatenate([byf[f] for f in pick]))
        out.append(100*np.mean([ (j[x].mean()-g[x].mean()) for x in idx]))
    return np.percentile(out,[2.5,97.5])
lo,hi=boot(nm); print('jev-gpt35 excl. controls %+.2f [%+.2f, %+.2f] (family_id)'%(ov(j,nm)-ov(g,nm),lo,hi))
lo,hi=boot(np.ones(len(ids),bool)); print('jev-gpt35 all %+.2f [%+.2f, %+.2f] (family_id)'%(ov(j,np.ones(len(ids),bool))-ov(g,np.ones(len(ids),bool)),lo,hi))
