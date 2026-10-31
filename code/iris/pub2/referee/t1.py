import json,numpy as np,sys
D=sys.argv[1]
L={r['id']:r for r in map(json.loads,open(f'{D}/labels.jsonl'))}; C={r['id']:r for r in map(json.loads,open(f'{D}/chat_judges.jsonl'))}
ids=sorted(L); cell=np.array([L[i]['cell'] for i in ids]); cells=sorted(set(cell))
print(L[ids[0]], {k:(v if k!='x' else '') for k,v in C[ids[0]].items()})
def fav(name):
    out=[]
    for i in ids:
        s=sum(C[i][name]); p=0.5 if s==8 else float(s>8)  # i picked if >8 of 16
        out.append(np.mean([p if ch==L[i]['i'] else 1-p for ch in L[i]['choice']]))
    return np.array(out)
def share(name):
    return np.array([np.mean([sum(C[i][name])/16 if ch==L[i]['i'] else 1-sum(C[i][name])/16 for ch in L[i]['choice']]) for i in ids])
rng=np.random.default_rng(1); idx={c:np.where(cell==c)[0] for c in cells}
def boot(x):
    out=[]
    for _ in range(20000):
        pick=rng.choice(len(cells),len(cells)); s=np.concatenate([idx[cells[k]] for k in pick]); out.append(x[s].mean())
    return '%+.2f [%+.2f,%+.2f]'%(100*x.mean(),*(100*np.percentile(out,[2.5,97.5])))
F={n:fav(n) for n in ('gpt-5.6-sol','claude-opus-5')}; P={n:share(n) for n in F}
print('fav sol',100*F['gpt-5.6-sol'].mean(),'opus',100*F['claude-opus-5'].mean()); print('fav sol-opus',boot(F['gpt-5.6-sol']-F['claude-opus-5']))
print('share sol-opus',boot(P['gpt-5.6-sol']-P['claude-opus-5']))
aa=np.array([float(L[i]['choice'][0]==L[i]['choice'][1]) for i in ids])
for n in F: print(n,'fav minus aa',boot(F[n]-aa))
# ties count
for n in F: print(n,'ties(8/16)',sum(sum(C[i][n])==8 for i in ids),'of',len(ids))
