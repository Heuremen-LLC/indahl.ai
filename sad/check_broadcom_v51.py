# Broadcom VCF blog on MLPerf Inference v5.1, held against raw/inf_5.1.json. python3 -I check_claims_broadcom_v51.py
import json,hashlib
FILES=['raw/inf_5.1.json']; RAW={f:open(f,'rb').read() for f in FILES}
R=json.loads(RAW[FILES[0]])
def mk(i,q,calc,st,got,out,note): return dict(id=i,quote=q,calc=calc,stated=st,delivered=got,outcome=out,note=note,label_mismatch=False)
def rows(**k): return [r for r in R if all(r[a]==b for a,b in k.items())]
def val(i,m,s):
    r=[x for x in R if x['ID']==i and x['Model']==m and x['Scenario']==s and x['Category']=='closed']; return float(r[0]['Performance_Result']) if r else None
pct=lambda a,b:100*(a-b)/b
C=[]
t3=[('llama3.1-405b','Server',277),('llama3.1-405b','Offline',547),('llama2-70b-99','Server',33385),('llama2-70b-99','Offline',34301),('llama2-70b-99.9','Server',33371),('llama2-70b-99.9','Offline',34486),('stable-diffusion-xl','Server',17.95),('stable-diffusion-xl','Offline',18.64)]
g=[(m,s,val('5.1-0029',m,s),v) for m,s,v in t3]
ok=lambda a,v:a is not None and abs(a-v)<=0.5*10**-(len(str(v).split('.')[1]) if '.' in str(v) else 0)*1.0001
bad=[x for x in g if not ok(x[2],x[3])]
C.append(mk('BV1','Table 3 in the post, MLPerf Inference 5.1 results using eight vGPUs in VCF 9.0 on a Dell PowerEdge XE9680 with eight H200 GPUs','raw/inf_5.1.json, entry 5.1-0029 (Dell_Broadcom), closed datacenter','277, 547, 33385, 34301, 33371, 34486, 17.95 and 18.64','; '.join(f'{m} {s} {v:.2f}' for m,s,v,_ in g),'CONSISTENT' if not bad else 'BELOW','The post prints whole tokens per second for the Llama rows. Mismatches: '+(', '.join(f'{m} {s} printed {v} file {a:.1f}' for m,s,a,v in bad) or 'none')+'. A printed value that is the file value cut off instead of rounded differs by less than 1 token per second.'))
pairs=[('llama2-70b-99','Server'),('llama2-70b-99','Offline'),('llama2-70b-99.9','Server'),('llama2-70b-99.9','Offline')]
d=[(m,s,pct(val('5.1-0029',m,s),val('5.1-0026',m,s))) for m,s in pairs]
C.append(mk('BV2','VCF and bare metal are only 1% or 2% different in performance','Dell_Broadcom 5.1-0029 against Dell 5.1-0026 (PowerEdge XE9680, eight H200), Llama 2 70B','1% or 2% different',', '.join(f'{m} {s} {x:+.2f}%' for m,s,x in d),'CONSISTENT' if all(abs(x)<2.5 for *_,x in d) else 'BELOW','Two of four Llama 2 70B Offline differences round to 3% and 2%. The Offline 99 difference is '+f'{d[1][2]:+.2f}%.'))
dm=sorted({r['Model'] for r in R if r['ID']=='5.1-0026' and r['Category']=='closed'}); bm=sorted({r['Model'] for r in R if r['ID']=='5.1-0029' and r['Category']=='closed'})
C.append(mk('BV3','Because Dell submitted only Llama 2 70B results','models in Dell entry 5.1-0026 and Dell_Broadcom entry 5.1-0029','Dell submitted only Llama 2 70B on this system',f'Dell 5.1-0026: {", ".join(dm)}; Broadcom 5.1-0029: {", ".join(bm)}','BELOW' if set(dm)-{'llama2-70b-99','llama2-70b-99.9'} else 'CONSISTENT','Dell 5.1-0026 also holds RetinaNet. Broadcom did not submit RetinaNet on this system, so Llama 2 70B is the only model in common.'))
has405i=[r for r in rows(Submitter='Broadcom_Supermicro',Model='llama3.1-405b',Scenario='Interactive')]
C.append(mk('BV4','Llama 3.1 405B Interactive scenario result is unverified by MLCommons Association. Broadcom & SuperMicro did not submit it as it was not required.','Broadcom_Supermicro rows with Llama 3.1 405B Interactive','no Interactive submission',f'{len(has405i)} Interactive rows for Broadcom_Supermicro','CONSISTENT' if not has405i else 'BELOW','Whether it was required is not in the files. The file holds no such row.'))
sdxl=[r for r in R if r['Submitter']=='Supermicro' and 'stable-diffusion' in r['Model'] and r['a#'] in (8,'8') and 'B200' in r['Accelerator'] and r['Category']=='closed']
C.append(mk('BV5','Stable Diffusion benchmark results were not submitted by SuperMicro on a bare metal platform','Supermicro closed datacenter rows with SDXL on eight B200','no SuperMicro bare metal SDXL on eight B200',f'{len(sdxl)} rows','CONSISTENT' if not sdxl else 'BELOW','The comparison the post makes instead is to a different submitter, which Figure 1 shows and the text does not number.'))
vs=[('llama3.1-405b','Offline'),('llama3.1-405b','Server'),('whisper','Offline')]
dd=[(m,s,pct(val('5.1-0009',m,s),val('5.1-0087',m,s))) for m,s in vs]
C.append(mk('BV6','AI/ML Inference workloads from diverse domains of LLM (Llama 3.1 with 405 billion parameters, Speech2Text (Whisper from OpenAI), Text2Images (Stable Diffusion XL)) get on par bare metal performance in VCF','Broadcom_Supermicro 5.1-0009 against Supermicro bare metal 5.1-0087 (SYS-422GA-NBRT-LCC)','on par bare metal',', '.join(f'{m} {s} {x:+.2f}%' for m,s,x in dd),'CANNOT_TELL','The post gives no threshold for on par. Figure 1 values are not printed. SDXL has no bare metal pair on the same hardware.'))
ints=[('llama3.1-8b','Offline'),('llama3.1-8b','Server'),('rgat','Offline'),('whisper','Offline')]
di=[(m,s,pct(val('5.1-0059',m,s),val('5.1-0058',m,s))) for m,s in ints]
C.append(mk('BV7','achieving near bare-metal performance while benefiting from VCF’s manageability and flexibility','Intel_VMware 5.1-0059 against Intel 5.1-0058 (1-node-2S-GNR_86C), same processor','near bare-metal',', '.join(f'{m} {s} {x:+.2f}%' for m,s,x in di),'CANNOT_TELL','The post gives no threshold for near. The differences run from '+f'{min(x for *_,x in di):+.1f}% to {max(x for *_,x in di):+.1f}%.'))
r9=[r for r in R if r['ID']=='5.1-0009'][0]
C.append(mk('BV8','SuperMicro GPU SuperServer AS-4126GS-NBR-LCC with eight NVIDIA NVLinked NVIDIA HGX B200 GPUs in DirectPath I/O','System and processor fields of entry 5.1-0009','virtual system is AS-4126GS-NBR-LCC',f"System field: {r9['System']}; processor {r9['Processor']}; platform {r9['Platform'][:40]}",'CANNOT_TELL','The entry names SYS-422GA-NBRT-LCC and lists the AMD processor that the post gives for the virtual system. The post names AS-4126GS-NBR-LCC, which is a separate Supermicro bare metal entry (5.1-0086).'))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[x]).hexdigest() for x in FILES],claims=C),open('claims_broadcom_v51.json','w'),indent=1)
for c in C: print(c['id'],c['outcome'],'|',c['stated'][:44],'|',c['delivered'][:250])
