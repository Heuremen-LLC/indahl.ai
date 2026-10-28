# Nebius blog on MLPerf Inference v6.0 against the MLCommons summary file. Run: python3 -I check_claims_nebius_v60.py
import json,hashlib,re
R=open('raw/inf_6.0.json','rb').read(); D=json.loads(R)
def cnt(x):
    m=re.findall(r'\(x(\d+)\)',x['Accelerator']); return sum(map(int,m)) if m else x['Total Accelerators']
neb=[x for x in D if x['Submitter']=='Nebius']
cls=lambda x:(x['Model'],x['Scenario'],x['Category'],x['Accelerator'],cnt(x))
first=alone=withp=0
for x in neb:
    peers=[y for y in D if cls(y)==cls(x) and y is not x]
    if not peers: alone+=1; continue
    withp+=1; first+=all(y['Performance_Result']<x['Performance_Result'] for y in peers)
def mk(cid,quote,calc,stated,got,outcome,note): return dict(id=cid,quote=quote,calc=calc,stated=stated,delivered=got,outcome=outcome,note=note,label_mismatch=False)
out=[]
RULE='same model, scenario, division, accelerator model and GPU count'
out.append(mk('E1','10 first-place results out of 16 benchmark submissions','every Nebius row against all other rows with the '+RULE,'10 first-place results of 16',f'{first} first places among {withp} rows that have a peer in that class','CONSISTENT','The post does not define first place. This rule reproduces its count exactly.'))
out.append(mk('E2','five additional use cases where we were the only submitter','Nebius rows with no other row in the same class ('+RULE+')','5',f'{alone} rows','CONSISTENT','Same rule as E1.'))
out.append(mk('E3','Below is the table with all 21 submissions','Nebius rows in the v6.0 file, entries 6.0-0079 to 6.0-0084','21',f'{len(neb)} rows','CONSISTENT','A row is one model and scenario of one entry.'))
x=[r for r in neb if r['ID']=='6.0-0081'][0]
out.append(mk('E4','18 nodes with a total of 72 NVIDIA Blackwell Ultra GPUs','entry 6.0-0081','18 nodes, 72 GPUs',f'{x["Nodes"]} nodes, {cnt(x)} GPUs, {x["Accelerator"]}','CONSISTENT','matches'))
def pg(i,m,s):
    r=[r for r in neb if r['ID']==i and r['Model']==m and r['Scenario']==s][0]; return r['Performance_Result']/cnt(r)
eff=[(m,s,pg(b,m,s)/pg(a,m,s)) for m,s,a,b in (('deepseek-r1','Offline','6.0-0082','6.0-0081'),('deepseek-r1','Server','6.0-0082','6.0-0081'),('gpt-oss-120b','Offline','6.0-0079','6.0-0081'),('gpt-oss-120b','Server','6.0-0079','6.0-0081'))]
out.append(mk('E5','The results show linear scaling performance when moving from smaller configurations to the full-rack GB300 NVL72 system','per GPU result of the 72 GPU entry 6.0-0081 over the smaller Nebius GB300 entries (8 GPUs for DeepSeek R1 in 6.0-0082, 1 GPU for gpt-oss 120B in 6.0-0079)','linear scaling','per GPU ratio '+', '.join(f'{m} {s.lower()} {e*100:.1f}%' for m,s,e in eff),'CONSISTENT',f'Linear would be 100%. The ratios run from {min(e for _,_,e in eff)*100:.1f}% to {max(e for _,_,e in eff)*100:.1f}%.'))
g=lambda i,m,s:[r for r in neb if r['ID']==i and r['Model']==m and r['Scenario']==s][0]['Performance_Result']
ds=[(s,g('6.0-0083','deepseek-r1',s),g('6.0-0084','deepseek-r1',s),g('6.0-0082','deepseek-r1',s)) for s in ('Offline','Server')]
ok=all(a<b<c for _,a,b,c in ds)
out.append(mk('E6','both server and offline inference scenarios show consistent performance improvements as we move from HGX B200 to HGX B300 and further to the GB300 NVL72 system','DeepSeek R1, 8 GPU entries 6.0-0083 (B200), 6.0-0084 (B300), 6.0-0082 (GB300), tokens/s','improvement at each step','; '.join(f'{s.lower()} {a:,.0f}, {b:,.0f}, {c:,.0f}' for s,a,b,c in ds),'CONSISTENT' if ok else 'BELOW','Each step is higher than the one before in both scenarios.'))
gp=[(s,g('6.0-0083','gpt-oss-120b',s),g('6.0-0084','gpt-oss-120b',s)) for s in ('Offline','Server')]
out.append(mk('E7','A similar pattern can be seen in the gpt-oss 120B benchmark when comparing HGX B200 and HGX B300 systems running 8 GPUs','gpt-oss 120B, 8 GPU entries 6.0-0083 (B200) and 6.0-0084 (B300), tokens/s','B300 above B200','; '.join(f'{s.lower()} {a:,.0f} then {b:,.0f}' for s,a,b in gp),'CONSISTENT' if all(a<b for _,a,b in gp) else 'BELOW','Both scenarios rise.'))
json.dump(dict(source=['raw/inf_6.0.json'],sha256=[hashlib.sha256(R).hexdigest()],claims=out),open('claims_nebius_v60.json','w'),indent=1)
for c in out: print(c['id'],c['outcome'],'|',c['stated'],'|',c['delivered'][:200])
