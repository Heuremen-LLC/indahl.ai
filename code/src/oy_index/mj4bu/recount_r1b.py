# R1 sensitivity (post-hoc, labelled): UNPARSED calls treated as missing; gap vs their null (identity copies) with a base-clustered bootstrap.
import csv,sys,collections,random
D=sys.argv[1]; random.seed(20261025)
def load(fn):
    rows=list(csv.DictReader(open(D+'/data/'+fn,encoding='utf-8-sig')))
    V=collections.defaultdict(list); meta={}
    for r in rows: V[r['variant_id']].append(r['tag']); meta[r['variant_id']]=(r['base_aid'],r['direction'])
    return V,meta
def rate(ts,drop_unp):
    t=[x for x in ts if not(drop_unp and x=='UNPARSED')]
    return None if not t else sum(x=='[通過]' for x in t)/len(t)
for drop in (False,True):
    V,meta=load('perturb_results.csv')
    base={meta[v][0]:rate(V[v],drop) for v in V if meta[v][1]=='original'}
    pairs=[(meta[v][0],rate(V[v],drop)) for v in V if meta[v][1]=='to_synonym']
    pairs=[(b,p) for b,p in pairs if p is not None and base[b] is not None and base[b]>0.5]
    k=sum(p<=0.5 for b,p in pairs); n=len(pairs)
    NV,nmeta=load('perturb_null_results.csv'); print('null directions',collections.Counter(d for _,d in nmeta.values()))
    nbase={nmeta[v][0]:rate(NV[v],drop) for v in NV if nmeta[v][1]=='original'}
    npairs=[(nmeta[v][0],rate(NV[v],drop)) for v in NV if nmeta[v][1]!='original']
    npairs=[(b,p) for b,p in npairs if p is not None and nbase.get(b) is not None and nbase[b]>0.5]
    nk=sum(p<=0.5 for b,p in npairs); nn=len(npairs)
    # cluster bootstrap by base answer
    gb=collections.defaultdict(list); [gb[b].append(p<=0.5) for b,p in pairs]
    ngb=collections.defaultdict(list); [ngb[b].append(p<=0.5) for b,p in npairs]
    B=list(gb); NB=list(ngb); diffs=[]
    for _ in range(5000):
        s=[x for b in random.choices(B,k=len(B)) for x in gb[b]]; t=[x for b in random.choices(NB,k=len(NB)) for x in ngb[b]]
        diffs.append(sum(s)/len(s)-sum(t)/len(t))
    diffs.sort()
    print(f"UNPARSED {'dropped' if drop else 'as fail (theirs)'}: synonym pass->fail {k}/{n} = {k/n:.3f} over {len(B)} bases; null {nk}/{nn} = {nk/nn:.3f}; gap {k/n-nk/nn:+.3f} [{diffs[124]:+.3f}, {diffs[4874]:+.3f}]")
