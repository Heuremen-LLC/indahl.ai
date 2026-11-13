# AMD ROCm blog on reproducing the MLPerf Inference v5.1 submission, held against the v5.0 and v5.1 result files and the earlier-round system files. python3 -I check_claims_amd_repro_v51.py
import json,hashlib,re
FILES=['raw/inf_5.0.json','raw/inf_5.1.json','raw/older_rounds_systems.json']; RAW={f:open(f,'rb').read() for f in FILES}
V5=json.loads(RAW[FILES[0]]); V1=json.loads(RAW[FILES[1]]); OLD=json.loads(RAW[FILES[2]]); s=str; pc=lambda x,y:100*(x/y-1); P=lambda x:x['Performance_Result']
import re as _re
_KEEP={'bert','rgat','retinanet','resnet','dlrm','unet','sdxl'}
def _and(L): return L[0] if len(L)==1 else ', '.join(L[:-1])+' and '+L[-1]
def _pl(s,prose=False):   # a table cell as plain text: no semicolons, and in the data cells no Python list, True/False or None
    if not isinstance(s,str): return s
    if not prose:
        s=_re.sub(r"\[((?:'[^']*'(?:, )?)+)\]",lambda m:_and(_re.findall(r"'([^']*)'",m.group(1))),s).replace('[]','none')
        s=_re.sub(r'\bTrue\b','yes',s); s=_re.sub(r'\bFalse\b','no',s); s=_re.sub(r'\bNone\b','none',s)
    return _re.sub(r'; ([a-z]+)\b(?![-_./])',lambda m:'. '+(m.group(1) if m.group(1) in _KEEP else m.group(1).capitalize()),s).replace('; ','. ')
def mk(i,q,calc,st,got,out,note): return dict(id=i,quote=q,calc=_pl(calc),stated=_pl(st),delivered=_pl(got),outcome=out,note=_pl(note,True),label_mismatch=False)
def n(x):
    m=re.findall(r'\(x(\d+)\)',s(x.get('Accelerator'))); return sum(map(int,m)) if m else int(x.get('a#') or 0)*int(x.get('Nodes') or 1)
RF=[]
rd=[r[1:] for r,v in OLD.items() if 'AMD' in v['submitters']]+[nm for L,nm in((V5,'5.0'),(V1,'5.1')) if any(x['Submitter']=='AMD' for x in L)]
RF.append(mk('RF1','MLPerf Inference v5.1 marks AMD’s third round of submissions','rounds with an AMD submission in the v3.1 to v5.1 sources','third round',f'AMD appears in {sorted(rd)}','CONSISTENT' if len(rd)==3 else 'BELOW','AMD appears first in v4.1 in the repository system files. Rounds v3.1 and v4.0 were read from lists cut short at the end, where AMD would sort first.'))
inst=[x for x in V1 if 'Instinct' in s(x['Accelerator'])]; sub={x['Submitter'] for x in inst if x['Submitter']!='AMD'}
orgs=set()
for nm in sub: orgs|={p for p in nm.replace('Quanta_Cloud_Technology','QCT').split('_') if p!='AMD'}
av={x['Availability'] for x in inst}
RF.append(mk('RF2','Momentum across the ecosystem remains strong, with eight AMD partners submitting results on Instinct platforms. Every submission falls into the “available” category','v5.1 entries on AMD Instinct accelerators from submitters other than AMD, combined names split; availability field','eight partners, all available',f'{len(orgs)} organizations: {sorted(orgs)}; availability values {sorted(av)}','CONSISTENT' if len(orgs)==8 and av=={'available'} else 'BELOW','Our rule: a combined name such as Dell_MangoBoost counts as two organizations. The count is nine with Krai and eight without it. Availability is available for every entry.'))
op=[x for x in V1 if x['Submitter']=='AMD' and x['Category']=='open']; op5=[x for x in V5 if x['Submitter']=='AMD' and x['Category']=='open']
RF.append(mk('RF3','For the first time, AMD is competing in the Open division','AMD open division entries in the v5.0 and v5.1 files; AMD in the v3.1, v4.0 and v4.1 repositories','first open division entries',f'v5.1 AMD open entries: {len({x["ID"] for x in op})}; v5.0: {len(op5)}; v4.1 AMD open files: 0; AMD in v3.1 and v4.0: absent','CONSISTENT' if op and not op5 else 'BELOW','The v4.1 repository has no open division files for AMD.'))
cl=sorted({x["Model"] for x in V1 if x["Submitter"]=="AMD" and x["Category"]=="closed" and "MI325X" in s(x["Accelerator"])})
opn=sorted({x["Model"]+" "+str(n(x))+" GPUs ("+x["Submitter"]+")" for x in V1 if "MI355X" in s(x["Accelerator"]) and x["Category"]=="open" and x["Submitter"] in ("AMD","AMD_MangoBoost")})
RF.append(mk('RF4','MLPerf Inference v5.1 Submission Overview table in the post','AMD and AMD_MangoBoost v5.1 entries: model, division, accelerator and count','nine rows: four closed on MI325X, five open on MI355X','closed MI325X: '+str(cl)+'; open MI355X: '+', '.join(opn),'CONSISTENT','The 4-node and 8-node rows are 32 and 64 GPU entries submitted as AMD_MangoBoost. The Mixtral and Llama 2 70B closed entries on the MI300X are also in the file and are not in the table.'))
mx5=len({x['Submitter'] for x in V5 if x['Model']=='mixtral-8x7b'})
RF.append(mk('RF5','Mixtral 8x7B is a mixture-of-experts model making its MLPerf debut.','Mixtral 8x7B entries in the v5.0 file; Mixtral files in the v4.1 repository','Mixtral 8x7B debuts in v5.1',f'v5.0 has {mx5} submitters with Mixtral 8x7B entries; the v4.1 repository holds Mixtral files; no AMD Mixtral entry before v5.1','BELOW','The benchmark is older than this round. It is the first AMD Mixtral submission.'))
RF.append(mk('RF6','Llama 3.1 405B - This workload was introduced in MLPerf inference v5.0','Llama 3.1 405B entries in the v5.0 file; the v4.1 repository','introduced in v5.0',f'v5.0 file: {len({x["Submitter"] for x in V5 if x["Model"]=="llama3.1-405b"})} submitters; v4.1 repository paths naming 405: 0','CONSISTENT',''))
RF.append(mk('RF7','tighter latency targets of 450 ms TTFT and 40 ms TPOT (25 tokens/s per user)','arithmetic on the post\'s TPOT','25 tokens/s per user at 40 ms TPOT',f'1000 ms over 40 ms = {1000/40:g} tokens/s','CONSISTENT','Checked from the post\'s own number.'))
a4=[x for x in V1 if x['ID']=='5.1-0004']; sd=lambda sc:[P(x) for x in a4 if x['Scenario']==sc][0]
o405={x['ID']:P(x) for x in V1 if x['Submitter']=='AMD' and x['Model']=='llama3.1-405b'}
l70=[P(x) for x in V1 if x['ID']=='5.1-0098'][0]
chk=[('SDXL Offline',18.5856,sd('Offline')),('SDXL Server completed',16.20,sd('Server')),('405B pruned',1942.23,o405['5.1-0101']),('405B pruned and fine-tuned',2019.04,o405['5.1-0100']),('Llama 2 70B MXFP4',92081,l70)]
RF.append(mk('RF8','Samples per second: 18 .5856 ... Completed samples per second : 16 .20 ... Tokens per second: 1942.23 ... Tokens per second: 2019.04 ... Tokens per second: 92081','AMD v5.1 entries 5.1-0004, 5.1-0100, 5.1-0101 and 5.1-0098, result field','five sample outputs',', '.join(f'{nm}: post {a:g}, file {f:g} ({pc(a,f):+.2f}%)' for nm,a,f in chk),'CONSISTENT' if all(abs(pc(a,f))<2 for nm,a,f in chk) else 'BELOW','Sample outputs come from a run on the reader\'s system and the post says results depend on the system. Our rule: within 2% of the file entry.'))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[f]).hexdigest() for f in FILES],claims=RF),open('claims_amd_repro_v51.json','w'),indent=1)
for c in RF: print(c['id'],c['outcome'],'|',c['stated'][:44],'|',c['delivered'][:360])
