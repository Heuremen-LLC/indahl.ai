import csv, sys, collections, numpy as np, itertools
X=sys.argv[1]
J=list(csv.DictReader(open(f'{X}/experiments/results/grapharm_pairwise_rows.csv')))
for pair in (('G1_full_graph','G0_fabula_only'),('G1_full_graph','G2_order_only')):
    c=collections.Counter(r['winner'] for r in J if (r['a'],r['b'])==pair); print('judge',pair,dict(c))
R=list(csv.DictReader(open(f'{X}/humaneval/responses2.csv')))
def winner(r):
    v=r['value']; return r['condition_left'] if v=='A' else r['condition_right'] if v=='B' else 'tie'
rd=collections.defaultdict(list); rep={}
for r in R:
    if r['block']!='pairwise': continue
    pair=tuple(sorted((r['condition_left'],r['condition_right'])))
    if r['measure']=='better': rd[(r['model'],r['story_id'],pair)].append((r['participant_id'],winner(r)))
    if r['measure'] in ('better','better_repeat'): rep.setdefault((r['participant_id'],r['model'],r['story_id'],pair),{})[r['measure']]=winner(r)
for pair in (('G1_full_graph','G2_order_only'),('G0_fabula_only','G1_full_graph')):
    w=[x for k,v in rd.items() if k[2]==pair for _,x in v]; dec=[x for x in w if x!='tie']
    print('readers',pair,'n',len(w),'decisive',len(dec),'G1 share %.1f%%'%(100*np.mean([x=='G1_full_graph' for x in dec])))
rng=np.random.default_rng(20261025)
def ci(a):
    a=np.array(a,float); i=rng.integers(0,len(a),(20000,len(a))); m=a[i].mean(1); lo,hi=np.percentile(m,[2.5,97.5]); return '%.3f [%.3f, %.3f] n=%d'%(a.mean(),lo,hi,len(a))
print('--- B1 judge vs reader majority (items decisive for both)')
for jp,rp in ((('G1_full_graph','G2_order_only'),('G1_full_graph','G2_order_only')),(('G1_full_graph','G0_fabula_only'),('G0_fabula_only','G1_full_graph'))):
    ag=[]
    for r in J:
        if (r['a'],r['b'])!=jp or r['winner']=='tie': continue
        v=[x for _,x in rd.get((r['model'],r['story_id'],rp),[]) if x!='tie']
        if not v: continue
        c=collections.Counter(v).most_common(); 
        if len(c)>1 and c[0][1]==c[1][1]: continue
        ag.append(c[0][0]==r['winner'])
    print(' ',jp[1],'judge-reader agreement',ci(ag))
print('--- B2 ceilings')
tr=[v['better']==v['better_repeat'] for v in rep.values() if 'better_repeat' in v and v['better']!='tie' and v['better_repeat']!='tie']
print('  reader test-retest (decisive both times)',ci(tr))
rr=[]
for k,v in rd.items():
    d=[x for _,x in v if x!='tie']
    for a,b in itertools.combinations(d,2): rr.append(a==b)
print('  reader-vs-reader, same item (pairs, not independent)',ci(rr))
