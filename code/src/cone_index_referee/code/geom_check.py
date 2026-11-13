import sys, json, math, collections
sys.path.insert(0,'/Users/heuremen/bones-forge/cone_index_referee/code')
from refcore import *
import numpy as np
from scipy.spatial import ConvexHull
OUT='/Users/heuremen/bones-forge/cone_index_referee/out/'
paths=json.load(open(OUT+'paths.json'))
sc=[p for p in paths if p['outcome'] in('INSIDE','OUTSIDE')]
# 1. exact quadratic vs margin sign
dis=[p for p in sc if (p['outcome']=='INSIDE')!=(p['M']<=1e-9)]
print('quad vs ternary-margin sign disagreements',len(dis),'of',len(sc))
Ms=np.array([p['M'] for p in sc])
for t in (0.5,1,2,4,6,10,20): print('|M|<%g n mi:'%t,int((abs(Ms)<t).sum()),'of',len(sc))
# 2. rows to test with method B and C: all with |M|<25 plus 300 random others
rng=np.random.default_rng(5)
near=[p for p in sc if abs(p['M'])<25]; far=[p for p in sc if abs(p['M'])>=25]
test=near+[far[i] for i in rng.choice(len(far),300,replace=False)]
# need forecasts and best tracks again
AD=read_adecks({})
HA=read_hurdat(ROOT+'hurdat/hurdat2-1851-2025-092326.txt',{'AL'}); HA.pop('_dups')
HE=read_hurdat(ROOT+'hurdat/hurdat2-nepac-1949-2025-092926.txt',{'EP'}); HE.pop('_dups')
BD=read_bdecks({})
RAD={int(y):v for y,v in json.load(open(OUT+'radii_ref.json'))['radii'].items()}
def circ(c,r,n=720):
    a=np.linspace(0,2*np.pi,n,endpoint=False); return np.c_[c[0]+r*np.cos(a),c[1]+r*np.sin(a)]
def in_hull(h,pt): return np.all(h.equations[:,:2]@pt+h.equations[:,2]<=1e-9)
def methodB(P,centers,radii):
    pr=[proj(P,c) for c in centers]
    for i in range(len(pr)-1):
        if radii[i]==0: pts=np.vstack([pr[i][None,:],circ(pr[i+1],radii[i+1])])
        else: pts=np.vstack([circ(pr[i],radii[i]),circ(pr[i+1],radii[i+1])])
        if in_hull(ConvexHull(pts),np.zeros(2)): return True
    return False
def slerp(a,b,t):
    def v(p): la,lo=math.radians(p[0]),math.radians(p[1]); return np.array([math.cos(la)*math.cos(lo),math.cos(la)*math.sin(lo),math.sin(la)])
    A,Bv=v(a),v(b); w=math.acos(max(-1,min(1,A@Bv)))
    if w<1e-12: X=A
    else: X=(math.sin((1-t)*w)*A+math.sin(t*w)*Bv)/math.sin(w)
    return (math.degrees(math.asin(max(-1,min(1,X[2])))),math.degrees(math.atan2(X[1],X[0])))
def methodC(P,centers,radii):
    ts=np.linspace(0,1,201)
    for i in range(len(centers)-1):
        best=1e9
        for t in ts:
            c=slerp(centers[i],centers[i+1],t); r=radii[i]+t*(radii[i+1]-radii[i])
            best=min(best,gc(P,c)-r)
        if best<=0: return True
    return False
res=collections.Counter(); ex=[]
for p in test:
    basin,season,num=p['basin'],p['season'],int(p['storm'][2:4])
    R={int(k):v for k,v in RAD[season][basin].items()}
    fc=AD[(basin,season,num)][p['dtg']]
    bt=HA.get(p['storm']) if basin=='AL' and season<2026 else (HE.get(p['storm']) if season<2026 else BD[p['storm']])
    centers=[fc[0]]+[fc[L] for L in LEADS]; radii=[0]+[R[L] for L in LEADS]
    ins_b=True; ins_c=True
    for h in range(12,121,6):
        b=bt[addh(p['dtg'],h)]; P=(b[0],b[1])
        ins_b&=methodB(P,centers,radii)
        ins_c&=methodC(P,centers,radii)
        if not ins_b and not ins_c: break
    A=p['outcome']=='INSIDE'
    res['B agrees' if ins_b==A else 'B differs']+=1
    res['C agrees' if ins_c==A else 'C differs']+=1
    if ins_b!=A: ex.append(('B',p['storm'],p['dtg'],p['M'],A))
    if ins_c!=A: ex.append(('C',p['storm'],p['dtg'],p['M'],A))
print(len(test),'tested',dict(res))
for e in ex[:25]: print(e)
json.dump(dict(tested=len(test),near=len(near),res=res,examples=ex),open(OUT+'geom_check.json','w'),indent=1,default=str)
