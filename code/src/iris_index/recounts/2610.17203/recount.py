import json, sys, numpy as np, collections
D=sys.argv[1]
L={r['id']:r for r in map(json.loads,open(f'{D}/labels.jsonl'))}; C={r['id']:r for r in map(json.loads,open(f'{D}/chat_judges.jsonl'))}
ids=sorted(L); cell=np.array([L[i]['cell'] for i in ids]); cells=sorted(set(cell))
def agree(name):
    out=[]
    for i in ids:
        p=sum(C[i][name])/16; a=[p if ch==L[i]['i'] else 1-p for ch in L[i]['choice']]; out.append(np.mean(a))
    return np.array(out)
aa=np.array([float(L[i]['choice'][0]==L[i]['choice'][1]) for i in ids])
A={n:agree(n) for n in ('gpt-5.6-sol','claude-opus-5')}
for n,v in A.items(): print(f'{n}: agreement with authors {100*v.mean():.1f}%')
print(f'author-author {100*aa.mean():.1f}%')
rng=np.random.default_rng(20261025); idx={c:np.where(cell==c)[0] for c in cells}
def boot(x):
    out=[]
    for _ in range(20000):
        pick=rng.choice(len(cells),len(cells)); s=np.concatenate([idx[cells[k]] for k in pick]); out.append(x[s].mean())
    lo,hi=np.percentile(out,[2.5,97.5]); return '%+.1f pp [%+.1f, %+.1f] %s'%(100*x.mean(),100*lo,100*hi,'ABOVE' if lo>0 else 'BELOW' if hi<0 else 'CONSISTENT')
for n,v in A.items(): print('B1',n,'minus author-author:',boot(v-aa))
print('B2 sol minus opus:',boot(A['gpt-5.6-sol']-A['claude-opus-5']))
