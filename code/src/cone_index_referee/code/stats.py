import sys, json, re, collections
sys.path.insert(0,'/Users/heuremen/bones-forge/cone_index_referee/code')
import numpy as np
OUT='/Users/heuremen/bones-forge/cone_index_referee/out/'
DESK='/Users/heuremen/bones-forge/cone_index/'
LEADS=[12,24,36,48,72,96,120]
rows=json.load(open(OUT+'rows.json')); paths=json.load(open(OUT+'paths.json'))
rng=np.random.default_rng(777)
def boot(items, B=2000):
    """items: list of (storm, inside(0/1)) -> share, lo, hi, nstorms"""
    d=collections.defaultdict(lambda:[0,0])
    for s,i in items: d[s][0]+=i; d[s][1]+=1
    ins=np.array([v[0] for v in d.values()]); n=np.array([v[1] for v in d.values()])
    k=len(ins)
    if k==0: return None
    idx=rng.integers(0,k,size=(B,k))
    sh=ins[idx].sum(1)/n[idx].sum(1)
    return ins.sum()/n.sum(), float(np.percentile(sh,2.5)), float(np.percentile(sh,97.5)), k
def classify(res,nrows,band):
    if res is None: return 'CANNOT_TELL'
    sh,lo,hi,k=res
    if k<10 or nrows<30: return 'CANNOT_TELL'
    if lo>=band[0] and hi<=band[1]: return 'CONSISTENT'
    if lo>band[1]: return 'ABOVE'
    if hi<band[0]: return 'BELOW'
    return 'CANNOT_TELL'
WP=(0.60,0.70); CB=(0.6167,0.7167)
def cell_rows(sel):
    sc=[r for r in sel if r['outcome'] in('INSIDE','OUTSIDE')]
    nr=[r for r in sel if r['outcome']=='NR']
    return sc,nr
res={}
fin=lambda r:r['grp']=='final'
for b in('AL','EP'):
    sel=[p for p in paths if p['basin']==b and fin(p)]
    sc,nr=cell_rows(sel)
    items=[(p['storm'],p['outcome']=='INSIDE') for p in sc]
    bt=boot(items)
    res['WP_%s'%b]=dict(inside=sum(i for _,i in items),scored=len(items),storms=bt[3],share=bt[0],lo=bt[1],hi=bt[2],out=classify(bt,len(items),WP),nr=len(nr),nr_why=dict(collections.Counter(p['why'] for p in nr)))
    for L in LEADS:
        sel=[r for r in rows if r['basin']==b and r['lead']==L and fin(r) and r['rad'] is not None]
        sc,nr=cell_rows(sel)
        items=[(r['storm'],r['outcome']=='INSIDE') for r in sc]
        bt=boot(items)
        res['C_%s_%d'%(b,L)]=dict(inside=sum(i for _,i in items),scored=len(items),storms=bt[3],share=bt[0],lo=bt[1],hi=bt[2],out=classify(bt,len(items),CB),nr=len(nr),nr_why=dict(collections.Counter(r['why'] for r in nr)))
# 2026
for b in('AL','EP'):
    sel=[p for p in paths if p['basin']==b and p['grp']=='current']
    sc,nr=cell_rows(sel); items=[(p['storm'],p['outcome']=='INSIDE') for p in sc]
    bt=boot(items); res['WP26_%s'%b]=dict(inside=sum(i for _,i in items),scored=len(items),share=None if bt is None else bt[0],out=classify(bt,len(items),WP),nr=len(nr))
    for L in LEADS:
        sel=[r for r in rows if r['basin']==b and r['lead']==L and r['grp']=='current' and r['rad'] is not None]
        sc,nr=cell_rows(sel); items=[(r['storm'],r['outcome']=='INSIDE') for r in sc]
        bt=boot(items); res['C26_%s_%d'%(b,L)]=dict(inside=sum(i for _,i in items),scored=len(items),share=None if bt is None else bt[0],lo=None if bt is None else bt[1],hi=None if bt is None else bt[2],out=classify(bt,len(items),CB),nr=len(nr))
# by season whole path
bys={}
for b in('AL','EP'):
    for y in range(2010,2027):
        sel=[p for p in paths if p['basin']==b and p['season']==y]
        sc,nr=cell_rows(sel)
        if not sel and y!=2012: pass
        items=[(p['storm'],p['outcome']=='INSIDE') for p in sc]
        bt=boot(items)
        bys['%s%d'%(b,y)]=dict(inside=sum(i for _,i in items),scored=len(items),out=classify(bt,len(items),WP) if bt else 'CANNOT_TELL',nr=len(nr))
res['by_season_wp']=bys
json.dump(res,open(OUT+'cells_ref.json','w'),indent=1)
print('cell | inside/scored | storms | share | lo-hi | outcome | nr')
for k,v in res.items():
    if k=='by_season_wp': continue
    print(k,v['inside'],v['scored'],v.get('storms'),None if v['share'] is None else round(100*v['share'],2),None if v.get('lo') is None else (round(100*v['lo'],2),round(100*v['hi'],2)),v['out'],v['nr'])
