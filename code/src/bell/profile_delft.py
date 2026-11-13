import numpy as np
from scipy.stats import chi2_contingency
d=np.loadtxt('/Users/heuremen/bones-forge/bell/raw/delft/bell_open_data.txt',delimiter=',',usecols=np.arange(1,17),dtype=np.int64)
c1t,c1c,c2t,c2c=d[:,2],d[:,3],d[:,4],d[:,5]
a,b=d[:,6],d[:,7]
exA,exB,invA,invB=d[:,12],d[:,13],d[:,14],d[:,15]
s0,s1,L,sep=5426350,5425700,55000-2550,250000
w1=((c1c==0)&(s0<=c1t)&(c1t<s0+L))|((c1c==1)&(s1<=c1t)&(c1t<s1+L))
w2=((c2c==0)&(s0+sep<=c2t)&(c2t<s0+sep+L))|((c2c==1)&(s1+sep<=c2t)&(c2t<s1+sep+L))
psi=c1c!=c2c
win=w1&w2&psi
inv=((invA==0)|(invA>250))&((invB==0)|(invB>250))
noex=(exA==0)&(exB==0)
keep=win&inv&noex
print("total candidate rows",len(d),"kept",keep.sum(),"discarded",(~keep).sum())
print("discard reasons (non-exclusive): outside herald window/psi-",(~win).sum()," invalid marker",(~inv).sum()," excitation click",(~noex).sum())
def test(mask,label):
    tab=[]
    print(f"\n[{label}] setting(a,b): kept / discarded / discard-rate")
    for aa in (0,1):
        for bb in (0,1):
            m=(a==aa)&(b==bb)
            k=(m&mask).sum(); dd=(m&~mask).sum()
            tab.append([k,dd]); print(f"  ({aa},{bb}): {k} / {dd} / {dd/(k+dd):.4f}")
    chi,p,dof,_=chi2_contingency(np.array(tab))
    print(f"  chi2={chi:.3f} dof={dof} p={p:.4g}  setting-dependent at p<0.01: {'YES' if p<0.01 else 'NO'}")
    for nm,s in (("A setting",a),("B setting",b)):
        t=[[(mask&(s==v)).sum(),(~mask&(s==v)).sum()] for v in (0,1)]
        c,pp,_,_=chi2_contingency(np.array(t)); print(f"  marginal {nm}: {t} chi2={c:.3f} p={pp:.4g}")
test(keep,"overall kept vs discarded")
test(win,"herald-window filter only")
test(noex,"excitation-click filter only")
test(inv,"invalid-marker filter only")
# readout no-click (outcome, not discard) among kept, by setting
print("\nkept trials: readout no-click rate by setting (A,B)")
roA=(d[:,10]>10620)&(d[:,10]<=10620+3700); roB=(d[:,11]>10620)&(d[:,11]<=10620+3700)
for aa in (0,1):
    for bb in (0,1):
        m=keep&(a==aa)&(b==bb); print(f"  ({aa},{bb}) n={m.sum()} A-noclick={(~roA[m]).mean():.3f} B-noclick={(~roB[m]).mean():.3f}")
# replicate paper
x=roA*2-1;y=roB*2-1
k=(keep*(((-1)**(a*b))*(x*y)+1)//2).sum(); print("\nreplication k/n =",k,"/",keep.sum())
