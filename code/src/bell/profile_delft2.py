import numpy as np
from scipy.stats import chi2_contingency
base='/Users/heuremen/bones-forge/bell/raw/delft2/'
K=[];A=[];B=[]
for s0,f in ((5426000,'bell_open_data_2_old_detector.txt'),(5426000-700,'bell_open_data_2_new_detector.txt')):
    d=np.loadtxt(base+f,delimiter=',',usecols=np.arange(1,17),dtype=np.int64)
    c1t,c1c,c2t,c2c=d[:,2],d[:,3],d[:,4],d[:,5]
    s1,L,sep,pp0,pp1=5425100,50000,250000,4000,2500
    w1=((c1c==0)&(s0<=c1t)&(c1t<s0+L))|((c1c==1)&(s1<=c1t)&(c1t<s1+L))
    w2m=((c2c==0)&(s0+sep<=c2t)&(c2t<s0+sep+L))|((c2c==1)&(s1+sep<=c2t)&(c2t<s1+sep+L))
    w2p=((c2c==0)&(s0+sep<=c2t)&(c2t<s0+sep+pp0))|((c2c==1)&(s1+sep<=c2t)&(c2t<s1+sep+pp1))
    psim=c1c!=c2c
    win=(w1&w2m&psim)|(w1&w2p&~psim)
    inv=((d[:,14]==0)|(d[:,14]>250))&((d[:,15]==0)|(d[:,15]>250))
    noex=(d[:,12]==0)&(d[:,13]==0)
    K.append(win&inv&noex);A.append(d[:,6]);B.append(d[:,7])
keep=np.concatenate(K);a=np.concatenate(A);b=np.concatenate(B)
print("run2 total",len(keep),"kept",keep.sum(),"discarded",(~keep).sum())
tab=[]
for aa in (0,1):
    for bb in (0,1):
        m=(a==aa)&(b==bb);k=(m&keep).sum();dd=(m&~keep).sum();tab.append([k,dd])
        print(f"  ({aa},{bb}): {k} / {dd} / {dd/(k+dd):.4f}")
chi,p,dof,_=chi2_contingency(np.array(tab));print(f"  chi2={chi:.3f} dof={dof} p={p:.4g}")
