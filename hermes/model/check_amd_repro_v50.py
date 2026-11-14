# AMD ROCm blog on reproducing the MLPerf Inference v5.0 submission, held against the v5.0 result file and the v4.1 repository. python3 -I check_claims_amd_repro_v50.py
import json,hashlib
FILES=['raw/inf_5.0.json','raw/older_rounds_systems.json']; RAW={f:open(f,'rb').read() for f in FILES}
V5=json.loads(RAW[FILES[0]]); OLD=json.loads(RAW[FILES[1]]); s=str; pc=lambda x,y:100*(x/y-1); P=lambda x:x['Performance_Result']
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
A=[x for x in V5 if x['Submitter']=='AMD']; e1=[x for x in A if x['ID']=='5.0-0001'][0]; e2=[x for x in A if x['ID']=='5.0-0002'][0]
g=lambda i,m,sc:[P(x) for x in A if x['ID']==i and x['Model']==m and x['Scenario']==sc][0]
RA=[]
RA.append(mk('RA1','The AMD MLPerf Inference v5.0 submission includes results that were generated on a system with 8 x MI325X GPUs and 2 x AMD EPYC 9655 CPUs.','AMD v5.0 entries 5.0-0001 (Llama 2 70B) and 5.0-0002 (SDXL), processor and accelerator fields','8 x MI325X and 2 x EPYC 9655',f'5.0-0001 Llama 2 70B: {e1["host_processors_per_node"]} x {e1["Processor"]}, {e1["a#"]} {s(e1["Accelerator"])}; 5.0-0002 SDXL: {e2["host_processors_per_node"]} x {e2["Processor"]}, {e2["a#"]} {s(e2["Accelerator"])}','CONSISTENT' if '9655' in s(e1['Processor']) and '9655' in s(e2['Processor']) else 'BELOW','The SDXL system has the EPYC 9655. The Llama 2 70B system in the file has the EPYC 9575F.'))
RA.append(mk('RA2','These results are submitted in the Available category, showcasing AMD hardware and software that are already available to customers.','availability and category fields of the AMD v5.0 entries','available category',f'availability {sorted({x["Availability"] for x in A})}; division {sorted({x["Category"] for x in A})}','CONSISTENT' if {x['Availability'] for x in A}=={'available'} else 'BELOW',''))
RA.append(mk('RA3','AMD has submitted results for two popular models','models in the AMD v5.0 entries','two models',f'models {sorted({x["Model"] for x in A})}','CONSISTENT' if {x['Model'].split('-9')[0] for x in A}=={'llama2-70b','stable-diffusion-xl'} else 'BELOW','Llama 2 70B appears at both 99 and 99.9 accuracy. SDXL is the second model.'))
amd41='AMD' in OLD['v4.1']['submitters']
RA.append(mk('RA4','Building upon the success of our MLPerf Inference v4.1 submission','AMD in the v4.1 repository','a v4.1 submission',f'AMD in v4.1 repository: {amd41}','CONSISTENT' if amd41 else 'BELOW',''))
chk=[('Llama 2 70B Offline',33396.9,g('5.0-0001','llama2-70b-99','Offline')),('Llama 2 70B Server',29522.56,g('5.0-0001','llama2-70b-99','Server')),('SDXL Offline',17.0963,g('5.0-0002','stable-diffusion-xl','Offline'))]
RA.append(mk('RA5','Tokens per second: 33396.9 ... Completed tokens per second: 29522.56 ... Samples per second: 17 .0963','AMD v5.0 entries 5.0-0001 and 5.0-0002, result field','three sample outputs',', '.join(f'{n}: post {a:g}, file {f:g} ({pc(a,f):+.2f}%)' for n,a,f in chk),'CONSISTENT' if all(abs(pc(a,f))<2 for n,a,f in chk) else 'BELOW','Sample outputs come from a run on the reader\'s system. Our rule: within 2% of the file entry. Llama 2 70B Server is 3.9% below.'))
RA.append(mk('RA6','ROCm 6.3.3 or later','Software field of the AMD v5.0 entry 5.0-0001','ROCm 6.3.3 or later for reproduction',f'the submitted Llama 2 70B run lists {s(e1["Software"]).split(",")[-1].strip()}; the SDXL entry lists {e2["Software"]}','CANNOT_TELL','The post asks for a later ROCm than the one the Llama 2 70B entry lists. The SDXL entry names no ROCm version.'))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[f]).hexdigest() for f in FILES],claims=RA),open('claims_amd_repro_v50.json','w'),indent=1)
for c in RA: print(c['id'],c['outcome'],'|',c['stated'][:44],'|',c['delivered'][:300])
