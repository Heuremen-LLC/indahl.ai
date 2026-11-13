import h5py,numpy as np,sys
from scipy.stats import chi2_contingency
fn=sys.argv[1]
f=h5py.File(fn,'r')
sa=f['alice/settings'][:];sb=f['bob/settings'][:];ca=f['alice/clicks'][:];cb=f['bob/clicks'][:]
ok=((sa==1)|(sa==2))&((sb==1)|(sb==2))
print(fn,"trials",len(sa),"valid-setting trials",ok.sum(),"dropped (bad setting code)",(~ok).sum())
a=(sa[ok]==2).astype(int);b=(sb[ok]==2).astype(int)
for label,mask in (("all 16 slots",0xFFFF),("slots 4-6 (3-pulse grouping, tab '456')",0b111<<4)):
    A=(ca[ok]&mask)!=0;B=(cb[ok]&mask)!=0
    print(f"\n== {label}")
    print(" (a,b): trials | A-click | B-click | coinc | P(A) | P(B) | P(neither)")
    for aa in (0,1):
        for bb in (0,1):
            m=(a==aa)&(b==bb);n=m.sum()
            print(f"  ({aa},{bb}): {n} | {A[m].sum()} | {B[m].sum()} | {(A&B)[m].sum()} | {A[m].mean():.6f} | {B[m].mean():.6f} | {(~A&~B)[m].mean():.6f}")
    # holes = trials with no coincidence (neither or single) vs setting pair
    tab=[[((A&B)&(a==aa)&(b==bb)).sum(),((~(A&B))&(a==aa)&(b==bb)).sum()] for aa in (0,1) for bb in (0,1)]
    c,p,d,_=chi2_contingency(tab);print(f"  non-coincidence ('hole') rate vs (a,b): chi2={c:.2f} dof={d} p={p:.3g} -> setting-dependent p<0.01: {'YES' if p<0.01 else 'NO'} (NB: coincidence rate is the Bell signal itself)")
    tab=[[((~A&~B)&(a==aa)&(b==bb)).sum(),((A|B)&(a==aa)&(b==bb)).sum()] for aa in (0,1) for bb in (0,1)]
    c,p,d,_=chi2_contingency(tab);print(f"  both-silent rate vs (a,b): chi2={c:.2f} dof={d} p={p:.3g} -> p<0.01: {'YES' if p<0.01 else 'NO'}")
    # own-setting dependence
    for nm,X,s in (("A no-click vs a",A,a),("B no-click vs b",B,b)):
        t=[[(~X&(s==v)).sum(),(X&(s==v)).sum()] for v in (0,1)];c,p,_,_=chi2_contingency(t)
        print(f"  {nm} (local setting): rate0={t[0][0]/sum(t[0]):.6f} rate1={t[1][0]/sum(t[1]):.6f} chi2={c:.2f} p={p:.3g}")
    # no-signaling: A no-click vs REMOTE b, within each a
    for nm,X,own,rem in (("A no-click vs remote b",A,a,b),("B no-click vs remote a",B,b,a)):
        for v in (0,1):
            m=own==v;t=[[(~X&m&(rem==r)).sum(),(X&m&(rem==r)).sum()] for r in (0,1)];c,p,_,_=chi2_contingency(t)
            print(f"  {nm} | own={v}: rate(rem0)={t[0][0]/sum(t[0]):.6f} rate(rem1)={t[1][0]/sum(t[1]):.6f} chi2={c:.2f} p={p:.3g}")
