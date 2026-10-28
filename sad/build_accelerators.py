# Per-accelerator throughput from MLCommons summary_results.json (Apache-2.0). python3 -I build_perchip.py
import json,csv,hashlib,statistics,collections,re
FILES=[('v5.0','raw/inf_5.0.json'),('v5.1','raw/inf_5.1.json'),('v6.0','raw/inf_6.0.json')]
rows=[];meta={};noacc=collections.Counter();namecount=collections.Counter()
for ver,f in FILES:
    raw=open(f,'rb').read(); meta[ver]=dict(file=f,sha256=hashlib.sha256(raw).hexdigest())
    D=json.loads(raw)
    mism=0
    for x in D:
        n=x['Nodes']*x['a#'] if isinstance(x['a#'],int) else 0
        named=[int(v) for v in re.findall(r'\(x(\d+)\)',x['Accelerator'])]   # the accelerator name states the count when it differs from nodes times accelerators per node, for example (x87) on an 11 node system
        if named and sum(named)!=n: namecount[ver]+=1; n=sum(named)
        ta=x.get('Total Accelerators')
        if isinstance(ta,int) and isinstance(x['a#'],int) and ta!=x['Nodes']*x['a#']: mism+=1
        if isinstance(ta,int) and not isinstance(x['a#'],int): n=ta
        if x['Category']=='closed' and 'datacenter' in x['Suite'] and n<=0:
            noacc[ver]+=1
        if x['Category']!='closed' or 'datacenter' not in x['Suite'] or n<=0: continue
        if not str(x['Performance_Units']).startswith(('Tokens','Samples','Queries')): continue
        rows.append(dict(version=ver,id=x['ID'],submitter=x['Submitter'],accelerator=x['Accelerator'],model=x['Model'],scenario=x['Scenario'],
            units=x['Performance_Units'],total=n,result=x['Performance_Result'],per_accelerator=x['Performance_Result']/n,
            availability=x['Availability'],dtype=str(x['weight_data_types']),system=x['System']))
    meta[ver]['nodes_times_a_vs_total_accelerators_mismatch']=mism; meta[ver]['rows']=len(D); meta[ver]['closed_datacenter_rows_without_accelerator_count_excluded']=noacc[ver]; meta[ver]['rows_counted_from_accelerator_name']=namecount[ver]
json.dump(dict(meta=meta,rows=rows),open('perchip_rows.json','w'))
with open('perchip_rows.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
g=collections.defaultdict(list)
for r in rows: g[(r['version'],r['model'],r['scenario'],r['accelerator'],r['units'])].append(r)
summ=[]
for k,v in sorted(g.items()):
    p=[r['per_accelerator'] for r in v]
    summ.append(dict(version=k[0],model=k[1],scenario=k[2],accelerator=k[3],units=k[4],submissions=len(v),submitters=len({r['submitter'] for r in v}),
        min=min(p),median=statistics.median(p),max=max(p),best_id=max(v,key=lambda r:r['per_accelerator'])['id']))
json.dump(summ,open('perchip_summary.json','w'),indent=0)
print(meta); print(len(rows),'rows',len(summ),'groups')
big=[s for s in summ if s['submissions']>=5 and s['max']/s['min']>1.15]
print('groups with >=5 submissions and max/min>1.15:',len(big))
for s in sorted(big,key=lambda s:-s['max']/s['min'])[:12]: print(s['version'],s['model'],s['scenario'],s['accelerator'],s['submissions'],round(s['min'],1),round(s['median'],1),round(s['max'],1),round(s['max']/s['min'],2))
