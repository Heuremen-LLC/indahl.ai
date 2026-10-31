import csv,collections,numpy as np,sys
X=sys.argv[1]
J=list(csv.DictReader(open(X+'/experiments/results/grapharm_pairwise_rows.csv')))
R=list(csv.DictReader(open(X+'/humaneval/responses2.csv')))
def winner(r):
    v=r['value']; return r['condition_left'] if v=='A' else r['condition_right'] if v=='B' else 'tie'
rd=collections.defaultdict(list)
for r in R:
    if r['block']=='pairwise' and r['measure']=='better':
        rd[(r['model'],r['story_id'],tuple(sorted((r['condition_left'],r['condition_right']))))].append(winner(r))
def agree(pair,rp):
    out={}
    for r in J:
        if (r['a'],r['b'])!=pair or r['winner']=='tie': continue
        v=[x for x in rd.get((r['model'],r['story_id'],rp),[]) if x!='tie']
        if not v: continue
        c=collections.Counter(v).most_common()
        if len(c)>1 and c[0][1]==c[1][1]: continue
        out[(r['model'],r['story_id'])]=(c[0][0]==r['winner'])
    return out
a=agree(('G1_full_graph','G2_order_only'),('G1_full_graph','G2_order_only')); b=agree(('G1_full_graph','G0_fabula_only'),('G0_fabula_only','G1_full_graph'))
print(len(a),len(b),len(set(a)&set(b)))
for nm,d in (('G2',a),('G0',b)):
    by=collections.defaultdict(list)
    for (m,s),v in d.items(): by[m].append(v)
    print(nm,{m:(len(v),round(np.mean(v),2)) for m,v in by.items()})
# readers per item
print('readers per item', collections.Counter(len(v) for v in rd.values()).most_common(5))
com=sorted(set(a)&set(b)); print('common',len(com))
if com:
    d=np.array([b[k]-a[k] for k in com],float); rng=np.random.default_rng(1); m=d[rng.integers(0,len(d),(20000,len(d)))].mean(1); print('paired diff on common',d.mean(),np.percentile(m,[2.5,97.5]))
# unpaired bootstrap
A=np.array(list(a.values()),float);B=np.array(list(b.values()),float);rng=np.random.default_rng(2)
m=B[rng.integers(0,len(B),(20000,len(B)))].mean(1)-A[rng.integers(0,len(A),(20000,len(A)))].mean(1); print('unpaired diff',B.mean()-A.mean(),np.percentile(m,[2.5,97.5]))
