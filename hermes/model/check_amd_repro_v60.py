# AMD ROCm blog on reproducing the MLPerf Inference v6.0 submission, held against the v5.0, v5.1 and v6.0 result files. python3 -I check_claims_amd_repro_v60.py
import json,hashlib
FILES=['raw/inf_5.0.json','raw/inf_5.1.json','raw/inf_6.0.json','raw/older_rounds_systems.json']; RAW={f:open(f,'rb').read() for f in FILES}
V5=json.loads(RAW[FILES[0]]); V51=json.loads(RAW[FILES[1]]); V0=json.loads(RAW[FILES[2]]); OLD=json.loads(RAW[FILES[3]]); s=str; P=lambda x:x['Performance_Result']
import re as _re
_KEEP={'bert','rgat','retinanet','resnet','dlrm','unet','sdxl'}
def _and(L): return L[0] if len(L)==1 else ', '.join(L[:-1])+' and '+L[-1]
def _pl(s,prose=False):   # a table cell as plain text: no semicolons, and in the data cells no Python list, True/False or None
    if not isinstance(s,str): return s
    if not prose:
        s=_re.sub(r"\[((?:'[^']*'(?:, )?)+)\]",lambda m:_and(_re.findall(r"'([^']*)'",m.group(1))),s).replace('[]','none')
        s=_re.sub(r'\bTrue\b','yes',s); s=_re.sub(r'\bFalse\b','no',s); s=_re.sub(r'\bNone\b','none',s)
    return _re.sub(r'; ([a-z]+)\b(?![-_./])',lambda m:'. '+(m.group(1) if m.group(1) in _KEEP else m.group(1).capitalize()),s).replace('; ','. ')
def _dir(*d): return 'CONSISTENT' if not any(d) else ('ABOVE' if min(d)>=0 else ('BELOW' if max(d)<=0 else 'CANNOT_TELL'))   # direction of the file against the statement: file minus stated, per item. ABOVE = the file shows more, BELOW = less, both = CANNOT_TELL
def mk(i,q,calc,st,got,out,note): return dict(id=i,quote=q,calc=_pl(calc),stated=_pl(st),delivered=_pl(got),outcome=out,note=_pl(note,True),label_mismatch=False)
AM=[x for x in V0 if x['Submitter']=='AMD' and x['Category']=='closed']
AR=[]
av={x['Submitter'] for x in V0 if 'Instinct' in s(x['Accelerator']) and x['Submitter']!='AMD' and x['Availability']=='available'}
orgs=set()
for n in av: orgs|=set(n.replace('ORACLE','Oracle').split('_'))
AR.append(mk('AR1','Nine AMD partners submitted results on Instinct platforms in the “Available” category.','v6.0 entries on AMD Instinct from submitters other than AMD, available category, combined submitter names split into organizations','nine partners',f'{len(av)} submitter names ({sorted(av)}) which split into {len(orgs)} organizations: {sorted(orgs)}','CONSISTENT' if len(orgs)==9 else 'BELOW','Our rule: a combined name such as Dell_MangoBoost or Supermicro_RedHat counts as two organizations. The file has 10 submitter names.'))
c={}
for x in AM: c.setdefault((x['ID'],x['Model']),int(x['Total Accelerators']))
mn=sorted({v for v in c.values() if v>8})
AR.append(mk('AR2','Llama 2 70B WMXFP4 MI355X 87 ... gpt-oss-120b WMXFP4 MI355X 94','AMD multi-node entries 6.0-0001 and 6.0-0003 in the v6.0 file, Total Accelerators field','87 GPUs for Llama 2 70B and 94 GPUs for gpt-oss-120b',f'file lists {c[("6.0-0001","llama2-70b-99")]} accelerators for Llama 2 70B and {c[("6.0-0003","gpt-oss-120b")]} for gpt-oss-120b',_dir(c[('6.0-0001','llama2-70b-99')]-87,c[('6.0-0003','gpt-oss-120b')]-94),'The file counts whole platforms, 11 x 8 and 12 x 8. The post says some GPUs were unhealthy and not used, so it gives 87 and 94.'))
AR.append(mk('AR3','Each MI355X platform comes with 8 MI355X GPUs. In the clusters where the multi-node benchmarks were run, some GPUs were not in a healthy state. Therefore, the submissions did not use all GPUs in the cluster.','AMD multi-node entries in the v6.0 file, accelerators divided by 8','whole platforms of 8, fewer GPUs used',f'{mn[0]} = {mn[0]//8} x 8 and {mn[1]} = {mn[1]//8} x 8 in the file','CANNOT_TELL','The file records the platform size, not how many GPUs ran. Whether fewer GPUs were used is not a file field.'))
AR.append(mk('AR4','For multi-node submissions, 11 or 12 systems are required.','AMD multi-node entries in the v6.0 file, accelerators divided by 8','11 or 12 systems',f'{mn[0]//8} and {mn[1]//8} platforms','CONSISTENT' if (mn[0]//8,mn[1]//8)==(11,12) else 'BELOW',''))
rd=[n for L,n in((V5,'5.0'),(V51,'5.1'),(V0,'6.0')) if any(x['Submitter']=='AMD' for x in L)]
rd_old=[r[1:] for r,v in OLD.items() if 'AMD' in v['submitters']]
AR.append(mk('AR5','MLPerf Inference v6.0 marked AMD’s fourth round of submissions to MLPerf Inference.','rounds with an AMD submission: the v5.0, v5.1 and v6.0 result files and the v3.1, v4.0 and v4.1 repositories','fourth round',f'AMD appears in {sorted(rd_old+rd)}','CONSISTENT' if len(rd_old+rd)==4 else 'BELOW','Earlier rounds have no summary file, so the closed division system description files in each repository were read. AMD sorts first in the file list, so the cut-short lists for v3.1 and v4.0 would show it. The open division of those two rounds is not covered.'))
o=[x for x in AM if x['ID']=='6.0-0002' and x['Model']=='llama2-70b-99' and x['Scenario']=='Offline'][0]
AR.append(mk('AR6','Samples per second: 365.738 Tokens per second: 103480','AMD entry 6.0-0002, Llama 2 70B 99 Offline','103480 tokens per second in the sample output',f'{P(o):,.0f} tokens/s, {o["Performance_Units"]}','CONSISTENT' if round(P(o))==103480 else 'BELOW','The sample output is from a run on the reader\'s system and the post says results depend on the system. It equals the AMD entry. The samples per second figure is not a file field.'))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[f]).hexdigest() for f in FILES],claims=AR),open('claims_amd_repro_v60.json','w'),indent=1)
for c_ in AR: print(c_['id'],c_['outcome'],'|',c_['stated'][:44],'|',c_['delivered'][:260])
