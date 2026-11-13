import json,math,random
from math import comb
d=json.load(open('/Users/heuremen/bones-forge/census_coverage/summary_coverage.json'))
p=0.10;n=51
print('P(X>=14) independent null =',sum(comb(n,k)*p**k*(1-p)**(n-k) for k in range(14,52)))
z=[a['nce']/a['se'] for a in d['areas']]
print('mean z^2',sum(x*x for x in z)/51,'(1 under all-zero null)')
# equicorrelated simulation: shared factor, rho
for rho in (0,.2,.4,.6):
    random.seed(1);c=[]
    for _ in range(20000):
        g=random.gauss(0,1);k=sum(abs(math.sqrt(rho)*g+math.sqrt(1-rho)*random.gauss(0,1))>1.645 for _ in range(n));c.append(k)
    c.sort();print('rho',rho,'mean',sum(c)/len(c),'95th pct',c[int(.95*len(c))],'P(>=14)',sum(x>=14 for x in c)/len(c))
# multiplier sensitivity
zs=sorted(abs(x) for x in z);flag=[x for x in zs if x>1.645]
print('lowest flagged |z|',min(flag),'highest unflagged',max(x for x in zs if x<=1.645))
# component fragility: states' SE and est rounded to 0.1; flip under +-0.05 in est, SE, national
f=lambda e,s,p:(('BELOW' if e+1.645*s<p else 'ABOVE' if e-1.645*s>p else 'C'))
for c,pn in (('omissions',5.8),('duplication',1.6),('other_erroneous',0.6)):
    fr=[];
    for r in d['component_rows']:
        x=r[c];base=f(x['est'],x['se'],pn);flips=set()
        for de in(-.05,0,.05):
            for ds in(-.05,0,.05):
                for dp in(-.05,0,.05):
                    flips.add(f(x['est']+de,max(x['se']+ds,0.001),pn+dp))
        if len(flips)>1: fr.append((r['area'],base))
    print(c,'readings that flip under rounding (+-0.05 on est, SE, national):',len(fr))
