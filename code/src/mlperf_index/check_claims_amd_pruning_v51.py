# AMD ROCm blog on pruning and fine-tuning Llama 3.1 405B for MLPerf Inference v5.1, held against the v5.1 result file. python3 -I check_claims_amd_pruning_v51.py
import json,hashlib
FILES=['raw/inf_5.1.json']; RAW={f:open(f,'rb').read() for f in FILES}
V=json.loads(RAW[FILES[0]]); s=str; P=lambda x:x['Performance_Result']
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
def acc(x):
    d={}
    for t in s(x['Accuracy']).replace(':',' ').split():
        pass
    a=s(x['Accuracy']); r=float(a.split('ROUGEL:')[1].split()[0]); e=float(a.split('exact_match:')[1].split()[0]); return r,e
o=[x for x in V if x['Submitter']=='AMD' and x['Model']=='llama3.1-405b']
byid={x['ID']:x for x in o}; a0,a1=acc(byid['5.1-0100']),acc(byid['5.1-0101'])
cl=[acc(x) for x in V if x['Model']=='llama3.1-405b' and x['Category']=='closed' and x['Scenario']=='Offline' and 'exact_match' in s(x['Accuracy'])]
mr=sum(c[0] for c in cl)/len(cl); me=sum(c[1] for c in cl)/len(cl)
PR=[]
PR.append(mk('PR1','pruning 26 layers (~21%) from the original 126-layer Llama 3.1 405B model ... pruning 42 layers (33.3%)','arithmetic on the post\'s layer counts','~21% and 33.3% of 126 layers',f'26 of 126 = {100*26/126:.1f}%, 42 of 126 = {100*42/126:.1f}%','CONSISTENT' if round(100*26/126)==21 and round(100*42/126,1)==33.3 else 'BELOW','Checked from the post\'s own numbers.'))
PR.append(mk('PR2','In its original BF16 format, the model is 756 GB. Thanks to the MI355X’s support for MXFP4 quantization, we can quantize the model to approximately 207 GB.','arithmetic: 405 billion parameters at 16 bits and at 4.25 bits (4 bits plus one 8-bit scale per 32 values)','756 GB in BF16 and about 207 GB in MXFP4',f'BF16 {405e9*2/1e9:.0f} GB decimal or {405e9*2/2**30:.0f} GiB; MXFP4 {405e9*4.25/8/1e9:.0f} GB decimal or {405e9*4.25/8/2**30:.0f} GiB','CANNOT_TELL','Not a result file field. The BF16 figure matches the binary unit. The MXFP4 figure lies between the two computed values.'))
PR.append(mk('PR3','with Exact Match accuracy above 96.7% and RougeL accuracy above 97.7% ... above 96% for Exact Match and above 99.6% for RougeL metrics','accuracy fields of AMD open entries 5.1-0100 (2019.04 tokens/s) and 5.1-0101 (1942.15 tokens/s), and of the closed Llama 3.1 405B entries','accuracy percentages relative to the reference score',f'5.1-0100: ROUGEL {a0[0]:.3f}, exact match {a0[1]:.2f}; 5.1-0101: ROUGEL {a1[0]:.3f}, exact match {a1[1]:.2f}; mean of {len(cl)} closed entries: ROUGEL {mr:.3f}, exact match {me:.2f}','CANNOT_TELL',f'The percentages are relative to a reference score that is not a field in the file. Against the closed-entry mean the exact match ratios are {100*a0[1]/me:.1f}% and {100*a1[1]/me:.1f}% and the ROUGEL ratios are {100*a0[0]/mr:.1f}% and {100*a1[0]/mr:.1f}%.'))
PR.append(mk('PR4','with generated tokens/s ranging from 2,307 to 2,921 and Exact Match accuracy from 78.35% to 88.78%','Table 1 experiments in the post; AMD open entries in the v5.1 file','2,307 to 2,921 tokens/s across pruning strategies',f'submitted open entries: {P(byid["5.1-0101"]):,.2f} and {P(byid["5.1-0100"]):,.2f} tokens/s','CANNOT_TELL','Table 1 is an experiment table and not a submission. The submitted entries are lower than the experiment range.'))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[f]).hexdigest() for f in FILES],claims=PR),open('claims_amd_pruning_v51.json','w'),indent=1)
for c in PR: print(c['id'],c['outcome'],'|',c['stated'][:44],'|',c['delivered'][:300])
