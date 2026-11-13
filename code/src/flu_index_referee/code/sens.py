import json,math,collections,numpy as np
exec(open('boot.py').read().split("Ms={L")[0])
sel=rows; k='o95_final'
sc=[r for r in sel if r[k] in 'CAB']; n,d=agg(sc,lambda r:r[k]=='C',lambda r:1)
print('headline',n.sum(),d.sum(),n.sum()/d.sum(),'W',W)
for L in (1,2,4,6,8,13,26):
    his=[];los=[]
    for seed in range(1,21):
        M=draws(L,2000,seed*7919); lo,hi=interval(n,d,M); his.append(hi);los.append(lo)
    print('L',L,'hi mean %.4f min %.4f max %.4f; frac seeds hi<0.95: %.2f; lo mean %.4f'%(np.mean(his),min(his),max(his),np.mean(np.array(his)<0.95),np.mean(los)))
# season-cluster by season-week of year? cluster by season (4 clusters): per-season shares
for s in ('2023-24','2024-25','2025-26','2026-27'):
    ss=[r for r in sc if r['season']==s]; print(s,len(ss),sum(r[k]=='C' for r in ss)/len(ss))
# multiplicity profile L=4
prof=np.array([min(i+1,4,W-i,W-3) for i in range(W)]); print('cover first/last weeks',prof[:5],prof[-5:])
# Per-cell checks of every outcome across 20 seeds at L=4
Ms=[draws(4,2000,s*104729) for s in range(1,11)]
S=json.load(open('/Users/heuremen/bones-forge/flu_index/summary_flu.json'))
allc=list(S['cells'])
for loc in S['by_location']:
    for c in loc['cells']: allc.append(dict(c,cell=loc['loc']))
flip=collections.Counter(); ex=[]
for c in allc:
    sel=cellsel(c['cell']); kk='o%s_%s'%(c['level'],c['side']); sc=[r for r in sel if r[kk] in 'CAB']
    n,d=agg(sc,lambda r:r[kk]=='C',lambda r:1); nw=len({r['week'] for r in sc}); p=c['stated']
    outs=set()
    for M in Ms:
        lo,hi=interval(n,d,M) if len(sc) else (0,1); outs.add(rule(p,lo,hi,len(sc),nw,0.10) if len(sc) else 'CANNOT_TELL')
    if outs!={c['outcome']}: ex.append((c['cell'],c['level'],c['side'],c['outcome'],outs,c['lo'],c['hi']))
print('cells whose outcome varies across 10 other seeds:',len(ex)); [print(' ',e) for e in ex]
# edge: 2026-27 cells
for c in S['cells']:
    if c['cell']=='season 2026-27': print(c['level'],c['side'],c['share'],c['lo'],c['hi'],c['weeks'],c['scored'])
