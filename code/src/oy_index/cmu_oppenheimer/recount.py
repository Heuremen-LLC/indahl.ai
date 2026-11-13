import sys,math,random,statistics as st
sys.path.insert(0,'/Users/heuremen/bones-forge/oy_index/cmu_oppenheimer'); import xlsx
d=xlsx.read(sys.argv[1]); G=d['Assignment grades'][2:]
num=lambda x: float(x) if x not in (None,'') else None
rows=[[num(x) for x in (r+[None]*8)[:8]] for r in G]; rows=[r for r in rows if any(v is not None for v in r)]
print('grade rows with any value',len(rows))
def paired(i,j,name):
    p=[(r[i],r[j]) for r in rows if r[i] is not None and r[j] is not None]
    d_=[b-a for a,b in p]; m=st.mean(d_); s=st.stdev(d_); t=m/(s/math.sqrt(len(d_)))
    a=st.mean(a for a,b in p); b=st.mean(b for a,b in p)
    ceil=sum(1 for a,b in p if b>=3)/len(p)
    random.seed(20261025); bs=sorted(st.mean(random.choices(d_,k=len(d_))) for _ in range(5000))
    print(f'{name}: pairs {len(p)} mean A1 {a:.2f} A5 {b:.2f} t({len(p)-1})={t:.2f} diff {m:+.2f} [{bs[124]:+.2f},{bs[4874]:+.2f}] | A5 at max(3): {100*ceil:.0f}%  | A1 at max: {100*sum(1 for a,b in p if a>=3)/len(p):.0f}%')
paired(0,4,'Initial Argument'); paired(1,5,'Prompt Engineering'); paired(2,6,'Response to Feedback')
# self-efficacy
S=d['Survey responses']; hdr=S[1]; data=S[2:]
ix={h:i for i,h in enumerate(hdr) if h}
c1=[num((r+[None]*len(hdr))[ix['Time1_CURRENT_SE']]) for r in data]
k5=[h for h in hdr if h and h.startswith('Time2') and 'CURRENT_SE' in h]  # data label Time2 = Assignment 5; print('time5 current cols',k5)
c5=[num((r+[None]*len(hdr))[ix[k5[0]]]) for r in data] if k5 else []
a=[x for x in c1 if x is not None]; b=[x for x in c5 if x is not None]
na,nb=len(a),len(b); sp=((na-1)*st.variance(a)+(nb-1)*st.variance(b))/(na+nb-2); t=(st.mean(b)-st.mean(a))/math.sqrt(sp*(1/na+1/nb))
print(f'SE current: A1 n={na} mean {st.mean(a):.1f}, A5 n={nb} mean {st.mean(b):.1f}; independent t({na+nb-2})={t:.2f}')
pr=[(x,y) for x,y in zip(c1,c5) if x is not None and y is not None]
if len(pr)>2:
    dd=[y-x for x,y in pr]; tp=st.mean(dd)/(st.stdev(dd)/math.sqrt(len(dd))); print(f'SE current paired (students at both): n={len(pr)} diff {st.mean(dd):+.1f} t({len(pr)-1})={tp:.2f}')
