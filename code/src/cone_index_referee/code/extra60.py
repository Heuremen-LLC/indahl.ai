import sys, json, collections
sys.path.insert(0,'/Users/heuremen/bones-forge/cone_index_referee/code')
from refcore import *
import numpy as np
OUT='/Users/heuremen/bones-forge/cone_index_referee/out/'
AD=read_adecks({})
HA=read_hurdat(ROOT+'hurdat/hurdat2-1851-2025-092326.txt',{'AL'}); HA.pop('_dups')
HE=read_hurdat(ROOT+'hurdat/hurdat2-nepac-1949-2025-092926.txt',{'EP'}); HE.pop('_dups')
def mean_lead(basin,season,L,ep_rule='tau0'):
    v=[];west=0
    for (b,s,n),fcs in AD.items():
        if b!=basin or s!=season: continue
        bt=(HA if b=='AL' else HE).get('%s%02d%d'%(b,n,s))
        if bt is None: continue
        for dtg,fc in fcs.items():
            if dtg[8:] not in('00','06','12','18') or 0 not in fc or L not in fc: continue
            if b=='EP' and not(-140<fc[0][1]<0): continue
            b0=bt.get(dtg)
            if b0 is None or b0[2] not in TC: continue
            bv=bt.get(addh(dtg,L))
            if bv is None or bv[2] not in TC: continue
            if ep_rule=='both_east' and b=='EP' and not(-140<fc[L][1]<0 and -140<bv[1]<0): west+=1; continue
            v.append(gc(fc[L],(bv[0],bv[1])))
    return round(float(np.mean(v)),2),len(v),west
out={}
for L in (48,60,72,96):
    out['AL2020_%d'%L]=mean_lead('AL',2020,L)
for L in (72,96,120):
    out['EP2015_%d_tau0rule'%L]=mean_lead('EP',2015,L)
    out['EP2015_%d_both_east'%L]=mean_lead('EP',2015,L,'both_east')
# other AL seasons 60h
for y in (2019,2021,2022): out['AL%d_60'%y]=mean_lead('AL',y,60)
# 2012 frame forecast count
print(json.dumps(out,indent=1))
json.dump(out,open(OUT+'extra60.json','w'),indent=1)
