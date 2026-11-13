# Recount R1 (synonym perturbation) from perturb_results.csv with our own code (stdlib only).
import csv,sys,collections
D=sys.argv[1]
rows=list(csv.DictReader(open(D+'/data/perturb_results.csv',encoding='utf-8-sig')))
print('tags',collections.Counter(r['tag'] for r in rows).most_common())
byd=collections.defaultdict(collections.Counter)
for r in rows: byd[r['direction']][r['tag']]+=1
for d,c in byd.items(): print(' ',d,dict(c))
V=collections.defaultdict(list); meta={}
for r in rows: V[r['variant_id']].append(r['tag']); meta[r['variant_id']]=(r['base_aid'],r['direction'])
P={v:sum(t=='[通過]' for t in ts)/len(ts) for v,ts in V.items()}
U={v:sum(t=='UNPARSED' for t in ts)/len(ts) for v,ts in V.items()}
base={meta[v][0]:P[v] for v in V if meta[v][1]=='original'}
for d in ['to_synonym','to_standard']:
    vs=[v for v in V if meta[v][1]==d]; pb=[v for v in vs if base[meta[v][0]]>0.5]; pf=[v for v in pb if P[v]<=0.5]
    fp=[v for v in vs if base[meta[v][0]]<=0.5 and P[v]>0.5]
    print(d,'variants',len(vs),'pass->fail',len(pf),'/',len(pb),'fail->pass',len(fp),'/',len(vs)-len(pb),
          '| failing variants with >=2/3 UNPARSED:',sum(U[v]>=2/3 for v in pf),'| failing tags:',collections.Counter(t for v in pf for t in V[v]).most_common())
