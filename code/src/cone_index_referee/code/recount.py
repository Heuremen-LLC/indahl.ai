import sys, json, math, collections, datetime as dt
sys.path.insert(0,'/Users/heuremen/bones-forge/cone_index_referee/code')
from refcore import *
OUT='/Users/heuremen/bones-forge/cone_index_referee/out/'
st={}
AD=read_adecks(st)
HA=read_hurdat(ROOT+'hurdat/hurdat2-1851-2025-092326.txt',{'AL'})
HE=read_hurdat(ROOT+'hurdat/hurdat2-nepac-1949-2025-092926.txt',{'EP'})
st['hurdat_dups']=(HA.pop('_dups'),HE.pop('_dups'))
BD=read_bdecks(st)
rr=json.load(open(OUT+'radii_ref.json'))['radii']
RAD={int(y):v for y,v in rr.items()}
def radii_for(season,basin):
    v=RAD.get(season)
    return None if v is None else {int(k):x for k,x in v[basin].items()}
def bt_lookup(basin,season,num):
    sid='%s%02d%d'%(basin,num,season)
    if season==2026: return BD.get(sid)
    src=HA if basin=='AL' else HE
    return src.get(sid)
rows=[]; paths=[]; frame_out=collections.Counter(); short=collections.Counter(); nolead=collections.Counter()
tau0=[]; nst=set()
for (basin,season,num),fcs in sorted(AD.items()):
    bt=bt_lookup(basin,season,num)
    R=radii_for(season,basin)
    sid='%s%02d%d'%(basin,num,season)
    for dtg,fc in sorted(fcs.items()):
        if dtg[8:] not in ('00','06','12','18'): frame_out['odd hour']+=1; continue
        if 0 not in fc: frame_out['no tau0']+=1; continue
        if basin=='EP' and not (-140.0<fc[0][1]<0): frame_out['EP west of 140W']+=1; continue
        if bt is None: frame_out['no best track for storm']+=1; continue
        b0=bt.get(dtg)
        if b0 is None: frame_out['no bt at init']+=1; continue
        if b0[2] not in TC: frame_out['not TC at init']+=1; continue
        tau0.append(gc(fc[0],(b0[0],b0[1])))
        grp='current' if season==2026 else 'final'
        # circle rows (also for no-radii seasons, second ruler only)
        for L in LEADS:
            if L not in fc: nolead[L]+=1; continue
            vt=addh(dtg,L); b=bt.get(vt)
            if b is None: oc,why,d,tcb='NR','no bt',None,False
            elif b[2] not in TC: oc,why,d,tcb='NR','not tropical',None,False
            else:
                d=gc(fc[L],(b[0],b[1])); tcb=True
                oc=None if R is None else ('INSIDE' if d<=R[L] else 'OUTSIDE'); why=None
            rows.append(dict(storm=sid,basin=basin,season=season,grp=grp,dtg=dtg,lead=L,dist=d,tc=tcb,outcome=oc,why=why,rad=None if R is None else R[L]))
        if R is None: continue
        if not all(L in fc for L in LEADS): short[basin]+=1; continue
        pts=[bt.get(addh(dtg,h)) for h in range(12,121,6)]
        if any(p is None for p in pts): paths.append(dict(storm=sid,basin=basin,season=season,grp=grp,dtg=dtg,outcome='NR',why='no bt')); continue
        if any(p[2] not in TC for p in pts): paths.append(dict(storm=sid,basin=basin,season=season,grp=grp,dtg=dtg,outcome='NR',why='not tropical')); continue
        centers=[fc[0]]+[fc[L] for L in LEADS]; radii=[0]+[R[L] for L in LEADS]
        P=[(p[0],p[1]) for p in pts]
        margins=[cone_margin(q,centers,radii) for q in P]
        # exact membership
        ins=True
        for q in P:
            pr=[proj(q,c) for c in centers]
            if not any(seg_inside_exact(pr[i],radii[i],pr[i+1],radii[i+1]) for i in range(7)): ins=False;break
        paths.append(dict(storm=sid,basin=basin,season=season,grp=grp,dtg=dtg,outcome='INSIDE' if ins else 'OUTSIDE',why=None,M=max(margins),
                          first_out=None if ins else next(12+6*i for i,q in enumerate(P) if not any(seg_inside_exact(*(lambda pr:(pr[i2],radii[i2],pr[i2+1],radii[i2+1]))([proj(q,c) for c in centers])) for i2 in range(7)))))
json.dump(dict(stats=st,frame_out=frame_out,short=short,nolead=nolead,tau0_median=float(np.median(tau0)),tau0_n=len(tau0)),open(OUT+'frame.json','w'),indent=1)
json.dump(rows,open(OUT+'rows.json','w')); json.dump(paths,open(OUT+'paths.json','w'))
print(st); print(dict(frame_out),dict(short),dict(nolead),np.median(tau0),len(tau0),len(rows),len(paths))
