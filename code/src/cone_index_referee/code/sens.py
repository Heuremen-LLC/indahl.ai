import sys, json, math, collections
sys.path.insert(0,'/Users/heuremen/bones-forge/cone_index_referee/code')
from refcore import *
import numpy as np
OUT='/Users/heuremen/bones-forge/cone_index_referee/out/'
st={}
AD=read_adecks(st)
HA=read_hurdat(ROOT+'hurdat/hurdat2-1851-2025-092326.txt',{'AL'}); HA.pop('_dups')
HE=read_hurdat(ROOT+'hurdat/hurdat2-nepac-1949-2025-092926.txt',{'EP'}); HE.pop('_dups')
BD=read_bdecks(st)
RAD={int(y):v for y,v in json.load(open(OUT+'radii_ref.json'))['radii'].items()}
def radii_for(season,basin):
    v=RAD.get(season); return None if v is None else {int(k):x for k,x in v[basin].items()}
def bt_lookup(basin,season,num):
    sid='%s%02d%d'%(basin,num,season)
    if season==2026: return BD.get(sid)
    return (HA if basin=='AL' else HE).get(sid)
def inside_cone(q,centers,radii,skip_first=False):
    pr=[proj(q,c) for c in centers]
    s0=1 if skip_first else 0
    return any(seg_inside_exact(pr[i],radii[i],pr[i+1],radii[i+1]) for i in range(s0,len(pr)-1))
F=[]  # frame forecasts
for (basin,season,num),fcs in sorted(AD.items()):
    bt=bt_lookup(basin,season,num); R=radii_for(season,basin)
    if bt is None or R is None or season==2026: continue
    sid='%s%02d%d'%(basin,num,season)
    for dtg,fc in sorted(fcs.items()):
        if dtg[8:] not in('00','06','12','18') or 0 not in fc: continue
        if basin=='EP' and not(-140.0<fc[0][1]<0): continue
        b0=bt.get(dtg)
        if b0 is None or b0[2] not in TC: continue
        F.append((basin,season,sid,dtg,fc,bt,R))
print('frame forecasts',len(F))
def pts_for(dtg,bt):
    return [bt.get(addh(dtg,h)) for h in range(12,121,6)]
# 1. path variants on scored set
out=[]
for (basin,season,sid,dtg,fc,bt,R) in F:
    if not all(L in fc for L in LEADS): continue
    pts=pts_for(dtg,bt)
    avail=[p for p in pts if p is not None and p[2] in TC]
    full=len(avail)==19
    centers=[fc[0]]+[fc[L] for L in LEADS]; radii=[0]+[R[L] for L in LEADS]
    Pall=[(p[0],p[1]) for p in avail]
    base=all(inside_cone(q,centers,radii) for q in Pall)
    no0=all(inside_cone(q,centers,radii,True) for q in Pall)
    # with 60h circle where carried and radius exists
    v60=None
    if 60 in fc and 60 in R:
        c2=[fc[0],fc[12],fc[24],fc[36],fc[48],fc[60],fc[72],fc[96],fc[120]]; r2=[0,R[12],R[24],R[36],R[48],R[60],R[72],R[96],R[120]]
        v60=all(inside_cone(q,c2,r2) for q in Pall)
    # first-bad index along prefix of consecutive TC points
    pref=[]
    for p in pts:
        if p is None or p[2] not in TC: break
        pref.append((p[0],p[1]))
    prefix_in=all(inside_cone(q,centers,radii) for q in pref)
    out.append(dict(basin=basin,season=season,storm=sid,dtg=dtg,full=full,navail=len(avail),base=base,no0=no0,v60=v60,prefix_in=prefix_in,nprefix=len(pref),
                    c12=gc(fc[12],(bt[addh(dtg,12)][0],bt[addh(dtg,12)][1])) if bt.get(addh(dtg,12)) and bt[addh(dtg,12)][2] in TC else None, R12=R[12]))
json.dump(out,open(OUT+'sens_paths.json','w'))
print(len(out))
