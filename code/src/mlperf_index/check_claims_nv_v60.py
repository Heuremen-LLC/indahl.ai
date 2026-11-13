# NVIDIA technical blog on MLPerf Inference v6.0, held against the v5.0, v5.1 and v6.0 result files. python3 -I check_claims_nv_v60.py
import json,hashlib,re,collections
FILES=['raw/inf_5.0.json','raw/inf_5.1.json','raw/inf_6.0.json']; RAW={f:open(f,'rb').read() for f in FILES}
V5=json.loads(RAW[FILES[0]]); V1=json.loads(RAW[FILES[1]]); V0=json.loads(RAW[FILES[2]]); s=str; pc=lambda x,y:100*(x/y-1); P=lambda x:x['Performance_Result']
import re as _re
_KEEP={'bert','rgat','retinanet','resnet','dlrm','unet','sdxl'}
def _and(L): return L[0] if len(L)==1 else ', '.join(L[:-1])+' and '+L[-1]
def _pl(s,prose=False):   # a table cell as plain text: no semicolons, and in the data cells no Python list, True/False or None
    if not isinstance(s,str): return s
    if not prose:
        s=_re.sub(r"\[((?:'[^']*'(?:, )?)+)\]",lambda m:_and(_re.findall(r"'([^']*)'",m.group(1))),s).replace('[]','none')
        s=_re.sub(r'\bTrue\b','yes',s); s=_re.sub(r'\bFalse\b','no',s); s=_re.sub(r'\bNone\b','none',s)
    return _re.sub(r'; ([a-z]+)\b(?![-_./])',lambda m:'. '+(m.group(1) if m.group(1) in _KEEP else m.group(1).capitalize()),s).replace('; ','. ')
def n(x):
    m=re.findall(r'\(x(\d+)\)',s(x.get('Accelerator'))); return sum(map(int,m)) if m else int(x.get('a#') or x.get('Total Accelerators') or 0)*int(x.get('Nodes') or 1)
def mk(i,q,calc,st,got,out,note): return dict(id=i,quote=q,calc=_pl(calc),stated=_pl(st),delivered=_pl(got),outcome=out,note=_pl(note,True),label_mismatch=False)
def e(L,i,m,sc,cat='closed'): r=[x for x in L if x['ID']==i and x['Model']==m and x['Scenario']==sc and x['Category']==cat]; assert len(r)==1,(i,m,sc,len(r)); return r[0]
NZ=[]
T1=[('deepseek-r1','Offline',2494310,'6.0-0076','tokens/s'),('deepseek-r1','Server',1555110,'6.0-0076','tokens/s'),('deepseek-r1','Interactive',250634,'6.0-0078','tokens/s'),('gpt-oss-120b','Offline',1046150,'6.0-0081','tokens/s'),('gpt-oss-120b','Server',1096770,'6.0-0081','tokens/s'),('gpt-oss-120b','Interactive',677199,'6.0-0078','tokens/s'),('qwen3-vl-235b-a22b','Offline',79,'6.0-0094','samples/s'),('qwen3-vl-235b-a22b','Server',68,'6.0-0094','queries/s'),('wan-2.2-t2v-a14b','Offline',0.059,'6.0-0073','samples/s'),('wan-2.2-t2v-a14b','SingleStream',21,'6.0-0039','s'),('dlrm-v3','Offline',104637,'6.0-0075','samples/s'),('dlrm-v3','Server',99997,'6.0-0075','queries/s')]
bad=[]
for m,sc,v,i,u in T1:
    f=P(e(V0,i,m,sc)); d=3 if v<1 else 0
    if round(f,d)!=v: bad.append((m,sc,v,i,f))
NZ.append(mk('NZ1','Table 1 in the post, NVIDIA platform throughput on the newly added workloads','entries 6.0-0039, 6.0-0073, 6.0-0075, 6.0-0076, 6.0-0078, 6.0-0081 and 6.0-0094 in the v6.0 file, result field rounded to the digits printed','twelve values','; '.join(f'{m} {sc} {P(e(V0,i,m,sc)):,.10g}' for m,sc,v,i,u in T1)+f'. Values not matching to the digits printed: {bad}','CONSISTENT' if not bad else 'BELOW','The cited entries are not all NVIDIA submissions: 6.0-0081 is Nebius, 6.0-0039 is GigaComputing and 6.0-0094 is Red Hat, all on NVIDIA accelerators. The table mixes systems of 8, 72 and 288 accelerators.'))
nb=e(V0,'6.0-0081','deepseek-r1','Server'); old=e(V1,'5.1-0072','deepseek-r1','Server')
NZ.append(mk('NZ2','This round, NVIDIA GB300 NVL72—launched last year—delivered up to 2.7x higher token throughput compared to its debut submissions just six months ago on the server scenario of the DeepSeek-R1 benchmark','Nebius entry 6.0-0081 and NVIDIA entry 5.1-0072, DeepSeek-R1 Server, both 72 GB300','up to 2.7x, cost per token down more than 60%',f'{P(nb):,.0f} over {P(old):,.0f} = {P(nb)/P(old):.2f}x; cost per token falls {100*(1-P(old)/P(nb)):.0f}%','CONSISTENT' if round(P(nb)/P(old),1) in (2.7,2.8) and (1-P(old)/P(nb))>0.6 else 'BELOW','The ratio is 2.75x. The cost figure is arithmetic on that ratio.'))
rows=[('DeepSeek-R1 Server',2907,8064,'5.1-0072','deepseek-r1','Server','6.0-0082',8),('DeepSeek-R1 Offline',5842,9821,'5.1-0072','deepseek-r1','Offline','6.0-0017',8),('Llama 3.1 405B Server',170,259,'5.1-0072','llama3.1-405b','Server','6.0-0078',72),('Llama 3.1 405B Offline',224,271,'5.1-0072','llama3.1-405b','Offline','6.0-0078',72)]
res=[];ok=True
for nm,a,b,i1,m,sc,i0,g in rows:
    x1=e(V1,i1,m,sc); x0=e(V0,i0,m,sc); pa=P(x1)/n(x1); pb=P(x0)/n(x0); res.append((nm,pa,pb,pb/pa,n(x0))); ok&=(int(pa+0.5)==a and int(pb+0.5)==b)
NZ.append(mk('NZ3','Table 2 in the post, GB300 NVL72 per-GPU throughput in v5.1 and v6.0','entries 5.1-0072, 6.0-0017, 6.0-0078 and 6.0-0082, result divided by accelerator count','eight per-GPU values and four speedups','; '.join(f'{nm}: {pa:,.0f} to {int(pb+0.5):,} ({r:.2f}x, v6.0 entry on {g} accelerators)' for nm,pa,pb,r,g in res),'CONSISTENT' if ok else 'BELOW','The values reproduce. The v5.1 entry has 72 accelerators. The v6.0 DeepSeek-R1 values come from entries with 8 accelerators (Nebius 6.0-0082 and CoreWeave 6.0-0017). At 72 accelerators the v6.0 DeepSeek-R1 Server value is 5,562 for NVIDIA 6.0-0078 and 7,994 for Nebius 6.0-0081.'))
def partners(L,key,acc): return sorted({x[key] for x in L if x['Category']=='closed' and 'NVIDIA' in s(x['Accelerator']) and x[key]!='NVIDIA'})
p0,p1,p5=partners(V0,'Submitter',1),partners(V1,'Submitter',1),partners(V5,'Submitter',1)
named={'ASUSTeK','Cisco','CoreWeave','Dell','GigaComputing','Google','HPE','Lenovo','Nebius','Netweb_technologies','Quanta_Cloud_Technology','RedHat','Supermicro','Lambda_SIT'}
NZ.append(mk('NZ4','the largest number of partners submitting on any platform','closed entries on NVIDIA accelerators by submitters other than NVIDIA, v5.0, v5.1 and v6.0 files','14 partners, the largest number','v6.0: '+str(len(p0))+' submitters; v5.1: '+str(len(p1))+'; v5.0: '+str(len(p5))+f'; the 14 named partners present in v6.0: {len(named&set(p0))}; other v6.0 submitters: {sorted(set(p0)-named)}','CONSISTENT' if named<=set(p0) and len(p0)>=max(len(p1),len(p5)) else 'BELOW','Rounds before v5.0 are not in the files. Two more submitters on NVIDIA accelerators in v6.0, GATEOverflow and Krai, are not among the 14 named. In v5.1 the combined names Broadcom_Supermicro and Dell_Broadcom split into organizations give 19, or 16 if GATEOverflow, The_Stage and University-of-Florida are left out.'))
mx=max(n(x) for x in V0); mxe=max(max(n(x) for x in V5),max(n(x) for x in V1))
NZ.append(mk('NZ5','With 288 Blackwell Ultra GPUs—the largest scale ever submitted to any benchmark in MLPerf Inference','largest accelerator count in the v5.0, v5.1 and v6.0 files','288 GPUs, the largest scale ever',f'v6.0 largest {mx}; v5.0 and v5.1 largest {mxe}','CONSISTENT' if mx==288 and mxe<288 else 'BELOW','As of v6.0. Crusoe later submitted 512 GPUs in v6.1. Rounds before v5.0 are not in the files.'))
newm=['deepseek-r1','qwen3-vl-235b-a22b','gpt-oss-120b','wan-2.2-t2v-a14b','dlrm-v3']
ven={m:{('NVIDIA' if 'NVIDIA' in s(x['Accelerator']) else 'AMD' if 'AMD' in s(x['Accelerator']) else 'other') for x in V0 if x['Model']==m and x['Category']=='closed'} for m in newm}
top={}
for m,sc in(('gpt-oss-120b','Offline'),('gpt-oss-120b','Server'),('gpt-oss-120b','Interactive'),('wan-2.2-t2v-a14b','Offline')):
    r=sorted([(P(x),'NVIDIA' if 'NVIDIA' in s(x['Accelerator']) else 'AMD') for x in V0 if x['Model']==m and x['Scenario']==sc and x['Category']=='closed'],reverse=True); top[(m,sc)]=r[0][1]
NZ.append(mk('NZ6','Only the NVIDIA platform submitted results on all newly added models and scenarios this round, and delivered the highest performance across all of them.','closed v6.0 entries for the five new models by accelerator vendor, and the highest result for the models where another vendor submitted','only NVIDIA on all new models, highest on all',f'accelerator vendors per new model: '+'; '.join(f'{m} {sorted(v)}' for m,v in ven.items())+'; highest result by vendor: '+', '.join(f'{m} {sc} {w}' for (m,sc),w in top.items()),'CONSISTENT' if all('NVIDIA' in v for v in ven.values()) and sum(1 for v in ven.values() if v!={'NVIDIA'})==1 and all(v=='NVIDIA' for v in top.values()) else 'BELOW','AMD submitted GPT-OSS-120B and an open Wan entry and none of the other new models. The Wan single stream open entry from AMD is not in the closed comparison.'))
dsv=collections=None
ds51={('NVIDIA' if 'NVIDIA' in s(x['Accelerator']) else 'other') for x in V1 if x['Model']=='deepseek-r1'}
NZ.append(mk('NZ7','NVIDIA was the first and only platform to submit DeepSeek-R1 results on MLPerf Inference when the benchmark debuted last year.','accelerator vendors of v5.1 DeepSeek-R1 entries','only NVIDIA accelerators in v5.1',f'vendors: {sorted(ds51)}','CONSISTENT' if ds51=={'NVIDIA'} else 'BELOW',''))
di={('NVIDIA' if 'NVIDIA' in s(x['Accelerator']) else 'other') for x in V0 if x['Model']=='deepseek-r1' and x['Scenario']=='Interactive'}
NZ.append(mk('NZ8','was once again the only platform to submit on the newly added interactive scenario','accelerator vendors of v6.0 DeepSeek-R1 Interactive entries','only NVIDIA accelerators',f'vendors: {sorted(di)}','CONSISTENT' if di=={'NVIDIA'} else 'BELOW',''))
x1=e(V1,'5.1-0072','llama3.1-405b','Server'); x0=e(V0,'6.0-0078','llama3.1-405b','Server'); sp=(P(x0)/n(x0))/(P(x1)/n(x1))
NZ.append(mk('NZ9','GB300 NVL72 performance increased by 1.5x in the server scenario','NVIDIA entries 5.1-0072 and 6.0-0078, Llama 3.1 405B Server per accelerator','1.5x',f'{sp:.2f}x ({P(x1)/n(x1):.1f} to {P(x0)/n(x0):.1f} tokens/s per GPU)','CONSISTENT' if round(sp,1)==1.5 else 'BELOW',''))
NZ.append(mk('NZ10','This brings the cumulative NVIDIA MLPerf training and inference wins since 2018 to 291, which is 9x of all other submitters combined.','wins are not fields in the result files','291 cumulative wins, 9x all other submitters','no win count in the files','CANNOT_TELL','A win depends on a ranking rule the post does not state.'))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[f]).hexdigest() for f in FILES],claims=NZ),open('claims_nv_v60.json','w'),indent=1)
for c in NZ: print(c['id'],c['outcome'],'|',c['stated'][:44],'|',c['delivered'][:380])
