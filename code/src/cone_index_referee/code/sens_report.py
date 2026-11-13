import json, collections, sys
import numpy as np
OUT='/Users/heuremen/bones-forge/cone_index_referee/out/'
S=json.load(open(OUT+'sens_paths.json'))
rng=np.random.default_rng(99)
def boot(items,B=2000):
    d=collections.defaultdict(lambda:[0,0])
    for s,i in items: d[s][0]+=i; d[s][1]+=1
    ins=np.array([v[0] for v in d.values()]);n=np.array([v[1] for v in d.values()]);k=len(ins)
    idx=rng.integers(0,k,size=(B,k)); sh=ins[idx].sum(1)/n[idx].sum(1)
    return round(100*ins.sum()/n.sum(),1),round(100*np.percentile(sh,2.5),1),round(100*np.percentile(sh,97.5),1),k
rep={}
for b in('AL','EP'):
    full=[r for r in S if r['basin']==b and r['full']]
    rep[b+'_base']=(sum(r['base'] for r in full),len(full),boot([(r['storm'],r['base']) for r in full]))
    rep[b+'_no_tau0_piece']=(sum(r['no0'] for r in full),len(full),boot([(r['storm'],r['no0']) for r in full]))
    f60=[r for r in full if r['v60'] is not None]
    rep[b+'_with60h_2019+_base']=(sum(r['base'] for r in f60),len(f60))
    rep[b+'_with60h_2019+_v60']=(sum(r['v60'] for r in f60),len(f60))
    # 2020+ only
    # partial-path: all forecasts with all leads, use prefix of TC points; require >=1 point
    allr=[r for r in S if r['basin']==b and r['nprefix']>=1]
    rep[b+'_partial_prefix(all forecasts with 7 leads)']=(sum(r['prefix_in'] for r in allr),len(allr),boot([(r['storm'],r['prefix_in']) for r in allr]))
    # NR bounds
    nr=[r for r in S if r['basin']==b and not r['full']]
    rep[b+'_NR_forecasts']=len(nr)
    rep[b+'_NR_prefix_inside']=sum(r['prefix_in'] for r in nr)
    # path outside when 12h circle... first 12h
    # LOSO
    sc=[]
    for y in range(2010,2026):
        if y==2012: continue
        rest=[r for r in full if r['season']!=y]
        sc.append((y,boot([(r['storm'],r['base']) for r in rest])))
    rep[b+'_LOSO']=sc
    # season-level bootstrap
    byy=collections.defaultdict(lambda:[0,0])
    for r in full: byy[r['season']][0]+=r['base']; byy[r['season']][1]+=1
    ys=list(byy); ins=np.array([byy[y][0] for y in ys]);n=np.array([byy[y][1] for y in ys])
    idx=rng.integers(0,len(ys),size=(2000,len(ys))); sh=ins[idx].sum(1)/n[idx].sum(1)
    rep[b+'_season_level_boot']=(round(100*np.percentile(sh,2.5),1),round(100*np.percentile(sh,97.5),1),len(ys))
    # mean of season shares (unweighted)
    rep[b+'_season_shares']={y:round(100*byy[y][0]/byy[y][1],1) for y in sorted(byy)}
    # selection: 12h inside-circle share, scored paths vs NR forecasts
    a=[r['c12']<=r['R12'] for r in full if r['c12'] is not None]
    c=[r['c12']<=r['R12'] for r in nr if r['c12'] is not None]
    rep[b+'_12h_circle_share_in_scored_paths']=(round(100*np.mean(a),1),len(a))
    rep[b+'_12h_circle_share_in_NR_paths']=(round(100*np.mean(c),1),len(c))
# per-storm distribution of AL
for k,v in rep.items(): print(k,v)
json.dump(rep,open(OUT+'sens_report.json','w'),indent=1,default=str)
