# Cisco blog post on the multi-vendor MLPerf Inference v6.1 submission, held against the v5.0 to v6.1 result files. python3 -I check_claims_cisco_blog_v61.py
import json,hashlib
FILES=['raw/inf_5.0.json','raw/inf_5.1.json','raw/inf_6.0.json','raw/inf_6.1.json']; RAW={f:open(f,'rb').read() for f in FILES}
V5=json.loads(RAW[FILES[0]]); V51=json.loads(RAW[FILES[1]]); V0=json.loads(RAW[FILES[2]]); B=list(json.loads(RAW[FILES[3]]).values()); s=str
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
C=[x for x in B if x['Organization']=='Cisco' and 'H200 x8 + MI350X' in x['SystemName']]
def c(m,sc): r=[x for x in C if x['Model']==m and x['Scenario']==sc]; assert len(r)==1; return r[0]
CM=[]
het61=sorted({(x['Organization'],x['SystemName']) for x in B if '+' in s(x['accelerator_model_name'])}); het_old=sum(1 for L in(V5,V51,V0) for x in L if '+' in s(x['Accelerator']))
CM.append(mk('CM1','We are proud that it is the industry’s first multi-vendor accelerator submission','entries whose accelerator field names more than one accelerator in the v5.0, v5.1, v6.0 and v6.1 files','first multi-vendor accelerator submission',f'v6.1 entries with mixed accelerators: {_and([f'{o} {n}' for o,n in het61])}; earlier rounds in the files: {het_old}','CONSISTENT' if len(het61)==1 and het_old==0 else 'BELOW','Rounds before v5.0 are not in the files.'))
e=C[0]
CM.append(mk('CM2','Cisco connected eight NVIDIA H200 and eight AMD Instinct','Cisco entry in the v6.1 file, accelerator fields','eight H200 and eight MI350X',f'{e["total_accelerators"]} accelerators: {e["accelerator_model_name"]}; framework {e["framework"]}','CONSISTENT' if e['total_accelerators']==16 and 'H200' in s(e['accelerator_model_name']) and 'MI350X' in s(e['accelerator_model_name']) else 'BELOW','The file does not give the split between the two kinds. 16 is the sum.'))
sv,of=c('gpt-oss-120b','Server')['Result'],c('gpt-oss-120b','Offline')['Result']
CM.append(mk('CM3','Running the systems together produced 73,357.62 tokens per second.','Cisco heterogeneous entry, GPT-OSS-120B','73,357.62 tokens/s',f'Server {sv:,.2f}, Offline {of:,.2f}','CONSISTENT' if round(sv,2)==73357.62 or round(sv,1)==73357.6 else 'BELOW','The figure is the Server result. The file prints 73357.6.'))
CM.append(mk('CM4','That was 104.7% of the baseline, an increase of 3,272.14 tokens per second.','arithmetic on the post\'s 73,357.62 and 70,085.48','104.7% and +3,272.14',f'73,357.62 over 70,085.48 = {100*73357.62/70085.48:.2f}%, difference {73357.62-70085.48:,.2f}','CONSISTENT' if round(100*73357.62/70085.48,1)==104.7 and round(73357.62-70085.48,2)==3272.14 else 'BELOW','Checked from the post\'s own numbers.'))
al=[x for x in B if x['Organization']=='Cisco' and x['Model']=='gpt-oss-120b' and x['Scenario']=='Server']
CM.append(mk('CM5','we measured each system separately and added their throughput rates to establish a 70,085.48-token-per-second baseline','Cisco GPT-OSS-120B Server entries in the v6.1 file','a 70,085.48 tokens/s baseline from two standalone measurements',f'Cisco GPT-OSS-120B Server entries: '+', '.join(f'{x["SystemName"]} {x["Result"]:,.1f}' for x in al),'CANNOT_TELL','The two standalone measurements are not entries in the file. Only the combined run is.'))
CM.append(mk('CM6','In the GPT-OSS 120B Server run, the NVIDIA H200 group handled prefill while the AMD Instinct','Cisco heterogeneous entry in the v6.1 file','H200 handled prefill, MI350X handled decode',f'notes field: {e["notes"] or "empty"}; framework: {e["framework"]}','CANNOT_TELL','Which group ran which phase is not a file field.'))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[f]).hexdigest() for f in FILES],claims=CM),open('claims_cisco_blog_v61.json','w'),indent=1)
for c_ in CM: print(c_['id'],c_['outcome'],'|',c_['stated'][:44],'|',c_['delivered'][:240])
