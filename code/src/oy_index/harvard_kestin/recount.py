import sys,collections,random,statistics as st
sys.path.insert(0,'/Users/heuremen/bones-forge/oy_index/harvard_kestin'); import dta118
n,l,R,_,_=dta118.read(sys.argv[1]); I={k:i for i,k in enumerate(n)}
rows=[dict(zip(n,r)) for r in R]
by=collections.defaultdict(list); [by[r['rid']].append(r) for r in rows]
c=collections.Counter(len(v) for v in by.values()); print('rows',len(rows),'students',len(by),'rows per student',dict(c))
arms=collections.Counter(tuple(sorted(int(x['lect_AI']) for x in v)) for v in by.values()); print('arm pattern per student',dict(arms))
A=[r for r in rows if r['lect_AI']==1]; B=[r for r in rows if r['lect_AI']==0]
mean=lambda xs:sum(xs)/len(xs)
print('H1 post means AI %.2f (N=%d) vs AL %.2f (N=%d); pre combined %.2f (N=%d)'%(mean([r['post_score'] for r in A]),len(A),mean([r['post_score'] for r in B]),len(B),mean([r['pre_score'] for r in rows]),len(rows)))
print('pre by arm AI %.2f AL %.2f'%(mean([r['pre_score'] for r in A]),mean([r['pre_score'] for r in B])))
mx=max(r['post_score'] for r in rows); print('max post',mx,'ceiling share AI %.2f AL %.2f'%(mean([r['post_score']==mx for r in A]),mean([r['post_score']==mx for r in B])))
t=[r['new_total_total_time2'] for r in A if r['new_total_total_time2'] is not None]; tb=[r['new_total_total_time2'] for r in B if r['new_total_total_time2'] is not None]
print('time AI median %.1f n%d share<60 %.2f; AL time values'%(st.median(t),len(t),mean([x<60 for x in t])),collections.Counter(tb).most_common(4))
for k in ['engaged_score','enjoyed_score','effort_learn_score','feel_difficult_score']:
    a=[r[k] for r in A if r[k] is not None]; b=[r[k] for r in B if r[k] is not None]
    print(k,'AI %.2f (%.2f) n%d AL %.2f (%.2f) n%d'%(mean(a),st.stdev(a),len(a),mean(b),st.stdev(b),len(b)))
# P1 paired within-student
pairs=[(next(x for x in v if x['lect_AI']==1),next(x for x in v if x['lect_AI']==0)) for v in by.values() if len(v)==2 and {x['lect_AI'] for x in v}=={0,1}]
d=[a['post_score']-b['post_score'] for a,b in pairs]; random.seed(20261025)
bs=sorted(mean(random.choices(d,k=len(d))) for _ in range(5000))
print('P1 paired students %d: AI minus AL post %.2f [%.2f, %.2f]'%(len(d),mean(d),bs[124],bs[4874]))
# gain version: post - pre within lesson, paired
g=[(a['post_score']-a['pre_score'])-(b['post_score']-b['pre_score']) for a,b in pairs]
bs=sorted(mean(random.choices(g,k=len(g))) for _ in range(5000)); print('P1b paired gain difference %.2f [%.2f, %.2f]'%(mean(g),bs[124],bs[4874]))
print('medians post AI',st.median([r['post_score'] for r in A]),'AL',st.median([r['post_score'] for r in B]),'pre all',st.median([r['pre_score'] for r in rows]))
# paired students only, unpaired-style means
PA=[a for a,b in pairs]; PB=[b for a,b in pairs]
print('paired-only means post AI %.2f AL %.2f pre AI %.2f AL %.2f'%(mean([x['post_score'] for x in PA]),mean([x['post_score'] for x in PB]),mean([x['pre_score'] for x in PA]),mean([x['pre_score'] for x in PB])))
import math
def welch_pooled(a,b):
    na,nb=len(a),len(b); ma,mb=mean(a),mean(b); va,vb=st.variance(a),st.variance(b)
    sp=((na-1)*va+(nb-1)*vb)/(na+nb-2); return (mb-ma)/math.sqrt(sp*(1/na+1/nb)), na+nb-2
for k in ['engaged_score','feel_difficult_score','enjoyed_score','effort_learn_score']:
    a=[r[k] for r in A if r[k] is not None]; b=[r[k] for r in B if r[k] is not None]
    t,df=welch_pooled(a,b)
    dd=[pa[k]-pb[k] for pa,pb in pairs if pa[k] is not None and pb[k] is not None]
    tdep=mean(dd)/(st.stdev(dd)/math.sqrt(len(dd)))
    print(f'{k}: independent t({df})={t:.2f} | dependent t({len(dd)-1})={-tdep:.2f}  (sign: AL minus AI)')
def mwz(a,b):
    allv=sorted([(x,0) for x in a]+[(x,1) for x in b]); ranks={}; i=0
    vals=[v for v,_ in allv]
    while i<len(vals):
        j=i
        while j<len(vals) and vals[j]==vals[i]: j+=1
        for k in range(i,j): ranks.setdefault(vals[i],(i+j+1)/2)
        i=j
    na,nb=len(a),len(b); Ra=sum(ranks[x] for x in a); U=Ra-na*(na+1)/2
    from collections import Counter
    T=sum(c**3-c for c in Counter(vals).values()); N=na+nb
    sd=math.sqrt(na*nb/12*((N+1)-T/(N*(N-1)))); return (U-na*nb/2)/sd
print('Mann-Whitney z (AL vs AI post, 316 obs): %.2f'%mwz([r['post_score'] for r in B],[r['post_score'] for r in A]))
pa=[a['post_score'] for a,b in pairs]; pb=[b['post_score'] for a,b in pairs]
print('Mann-Whitney z on the 122 paired students only: %.2f'%mwz(pb,pa))
