import json,gzip,collections as C
D=json.load(gzip.open('/Users/heuremen/bones-forge/quake_index/data/quake_rows.json.gz'))['rows']
M=json.load(open('/Users/heuremen/bones-forge/quake_index_referee/out/rows.json'))
key=lambda r:(r['seq'],r['issued'],r['window'],r['mag'],r['kind'])
dd=C.defaultdict(list); mm=C.defaultdict(list)
for r in D: dd[key(r)].append(r)
for r in M: mm[key(r)].append(r)
only_d=[k for k in dd if k not in mm]; only_m=[k for k in mm if k not in dd]
dup=sum(1 for k,v in dd.items() if len(v)>1); dupm=sum(1 for k,v in mm.items() if len(v)>1)
diffs=[]; cdiff=[]
for k in dd:
    if k not in mm: continue
    a=dd[k][0]; b=mm[k][0]
    ao=a.get('outcome') or 'OUTSIDE'; bo=b.get('outcome') if b['status']!='outside' else 'OUTSIDE'
    if ao!=bo: diffs.append((k,ao,bo))
    if a.get('count')!=b.get('count'): cdiff.append((k,a.get('count'),b.get('count')))
# status
sd=sum(1 for k in dd if k in mm and (dd[k][0]['status']=='outside')!=(mm[k][0]['status']=='outside'))
print('desk',len(D),'mine',len(M),'only desk',len(only_d),'only mine',len(only_m),'dup keys desk',dup,'mine',dupm)
print('outcome diffs',len(diffs),'count diffs',len(cdiff),'frame diffs',sd)
print(diffs[:5],cdiff[:5])
json.dump(dict(only_desk=only_d[:50],only_mine=only_m[:50],outcome_diffs=diffs[:100],count_diffs=cdiff[:100],n=dict(od=len(only_d),om=len(only_m),oc=len(diffs),cc=len(cdiff))),open('/Users/heuremen/bones-forge/quake_index_referee/out/diff_vs_desk.json','w'),default=list)
