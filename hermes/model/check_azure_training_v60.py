# Azure blog post on Llama 3.1 405B in MLPerf Training v6.0, held against the v6.0 training times. python3 -I check_claims_azure_training_v60.py
import json,hashlib
FILES=['training_v60_times.json']; RAW={f:open(f,'rb').read() for f in FILES}
T=json.loads(RAW[FILES[0]]); s=str
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
L=sorted([x for x in T if x['benchmark']=='llama31_405b'],key=lambda x:x['official_style']); az=[x for x in L if x['submitter']=='Azure'][0]
AT=[]
AT.append(mk('AT1','we scaled Llama 3.1 405B (NVFP4) pretraining to 8,192 GB200 GPUs across 128 racks on Azure\'s Fairwater infrastructure, converging in 7.07 minutes','Azure llama31_405b entry in the v6.0 training times, accelerator count and official-style time','8,192 GB200 GPUs, 7.07 minutes',f'{az["gpus"]} GPUs ({az["accelerator"]}), runs {az["runs_minutes"]} minutes, official-style time {az["official_style"]}; {az["gpus"]/128:g} GPUs per rack over 128 racks','CONSISTENT' if az['gpus']==8192 and round(az['official_style'],2)==7.07 else 'BELOW','Racks and NVFP4 are not file fields. The file system name is 2048xAzure_GB200, which is 2,048 nodes of four GPUs.'))
AT.append(mk('AT2','Azure\'s Llama 3.1 405B submission, which achieved a leading result at 8K+ GPU scale','llama31_405b entries in the v6.0 training times, shortest official-style time','leading result at 8K+ GPU scale','order: '+', '.join(f'{x["submitter"]} {x["gpus"]} GPUs {x["official_style"]:.2f} min' for x in L[:5])+f'; Azure ranks {1+[x["submitter"] for x in L].index("Azure")} of {len(L)}','CONSISTENT' if L[0]['submitter']=='Azure' or az['gpus']==max(x['gpus'] for x in L) else 'BELOW','Leading is read as the shortest time, and separately as the largest GPU count.'))
r,g,m,gb,tt=[40,64,112,128],[2560,4096,7168,8192],[24,16,8,8],[960,1024,896,1024],[18.79,12.86,7.75,7.07]
arith=all(g[i]==r[i]*64 and gb[i]==m[i]*r[i] for i in range(4)); eff=(tt[0]/tt[3])/(r[3]/r[0])
AT.append(mk('AT3','Training time drops from 18.79 minutes to 7.07 minutes, representing 83% scaling efficiency relative to the 40-rack baseline as shown in the table below.','arithmetic on the post\'s table: 18.79 over 7.07 divided by 128 over 40','83% scaling efficiency',f'{tt[0]/tt[3]:.3f}x faster on {r[3]/r[0]:.1f}x the racks, efficiency {100*eff:.1f}%; GPUs = racks x 64 and GBS = MiniBS x racks hold in all four rows: {arith}','CONSISTENT' if round(100*eff)==83 and arith else 'BELOW','Checked from the post\'s own numbers. The file holds only the 128-rack run.'))
AT.append(mk('AT4','Scaling table in the post, four scale points at 40, 64, 112 and 128 racks','Azure llama31_405b entries in the v6.0 training times','four runs with times 18.79, 12.86, 7.75 and 7.07 minutes',f'{len([x for x in L if x["submitter"]=="Azure"])} Azure entry in the file, at {az["gpus"]} GPUs','CANNOT_TELL','The 40, 64 and 112 rack points are not Azure entries in the training result files. Only the 8,192 GPU run is. The file has an NVIDIA entry at 2,560 GPUs with 18.79 minutes (system hsg_ngpu2560), the same time the post gives for 2,560 Azure GPUs.'))
AT.append(mk('AT5','Roughly 57% of the training iteration wall time (~733 ms) is spent in compute. GEMM kernels dominate, accounting for 74% of that compute time. The FFN up-projection and down-projection GEMMs alone consume ~54% of total compute (~397 ms).','arithmetic on the post\'s step time of 1.27 s and the times it gives','57% compute, 54% FFN of compute',f'733 ms over 1,270 ms = {100*733/1270:.1f}%; 397 over 733 = {100*397/733:.1f}%','CONSISTENT' if round(100*397/733)==54 and abs(100*733/1270-57)<1 else 'BELOW','Checked from the post\'s own numbers. The 57% is 57.7% by the post\'s times.'))
AT.append(mk('AT6','Llama 3.1, with 405 billion active parameters, has the highest active parameter count among all models in the MLPerf suite.','model parameter counts are not fields in the training result files','highest active parameter count in the suite','no parameter field in the files','CANNOT_TELL',''))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[f]).hexdigest() for f in FILES],claims=AT),open('claims_azure_training_v60.json','w'),indent=1)
for c in AT: print(c['id'],c['outcome'],'|',c['stated'][:44],'|',c['delivered'][:260])
