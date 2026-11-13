import csv,glob
from scipy.stats import chi2_contingency
for fn in sorted(glob.glob('/Users/heuremen/bones-forge/bell/raw/munich/*_lab_*.csv')):
    rows=list(csv.reader(open(fn,encoding='utf-8',errors='replace'),delimiter=';'))[1:]
    t={0:[0,0],1:[0,0]}
    for r in rows:
        try: s=int(r[1]); ex=r[5].strip()=='yes'
        except: continue
        t[s][1 if ex else 0]+=1
    if min(t[0][1]+t[1][1],1)==0: print(fn.split("/")[-1],"setting0",t[0],"setting1",t[1],"no exclusions"); continue
    c,p,_,_=chi2_contingency([t[0],t[1]])
    print(fn.split('/')[-1],"setting0 kept/excl",t[0],"setting1 kept/excl",t[1],f"chi2={c:.2f} p={p:.3g}")
