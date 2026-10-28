# Google Cloud blog on MLPerf Inference v5.0 (AI Hypercomputer inference updates), held against raw/inf_5.0.json. python3 -I check_claims_google_v50.py
import json,hashlib,collections
FILES=['raw/inf_5.0.json']; RAW={f:open(f,'rb').read() for f in FILES}
R=json.loads(RAW[FILES[0]])
def mk(i,q,calc,st,got,out,note): return dict(id=i,quote=q,calc=calc,stated=st,delivered=got,outcome=out,note=note,label_mismatch=False)
G=[r for r in R if r['Submitter']=='Google' and r['Category']=='closed']
ids=sorted({r['ID'] for r in G}); sc=len({(r['ID'],r['Model'],r['Scenario']) for r in G})
fam=lambda m:m.replace('-99.9','').replace('-99','').replace('-interactive','')
sf=len({(r['ID'],fam(r['Model']),r['Scenario']) for r in G}); bf=len({(r['ID'],fam(r['Model'])) for r in G})
C=[]
C.append(mk('GV1','we submitted 15 results, including our first submission with A3 Ultra (NVIDIA H200) and A4 (NVIDIA HGX B200) VMs','Google closed datacenter rows in raw/inf_5.0.json, counted four ways','15 results',f'{len(ids)} entries ({", ".join(ids)}); {bf} system and benchmark pairs; {sf} with scenarios; {sc} with accuracy targets; {len(G)} rows','CANNOT_TELL','The post does not define a result. No counting rule gives 15. The 5.0-0078 entry is named NVIDIA DGX B200 in the file, and the post calls it the A4 VM.'))
cloud=[]
for r in R:
    if 'HGX' in r['System'] or ('B200' in r['Accelerator'] and 'GB200' not in r['Accelerator'] and 'GB200' not in r['System']):
        if 'B200' in r['Accelerator']: cloud.append((r['Submitter'],r['Category'],r['ID']))
cc=collections.Counter((a,b) for a,b,_ in cloud); lam=sorted({i for a,b,i in cloud if a=='Lambda'})
C.append(mk('GV2','Google Cloud was the only cloud provider to submit results on NVIDIA HGX B200 GPUs','submitters with B200 (not GB200) accelerators in raw/inf_5.0.json, by division','only cloud provider on HGX B200','; '.join(f'{a} {b}: {n} rows' for (a,b),n in sorted(cc.items())),'BELOW' if lam else 'CONSISTENT','In the closed division only Google, NVIDIA and Supermicro submitted on eight B200. Lambda, a cloud provider, has open division entries on eight B200 ('+', '.join(lam)+'). CoreWeave submitted GB200.'))
C.append(mk('GV3','Trillium now delivers 3.5x throughput improvement for queries/second on Stable Diffusion XL (SDXL) compared to last performance round for its predecessor, TPU v5e. This further improves throughput by 12% since the MLPerf 4.1 submission.','TPU Trillium SDXL rows in raw/inf_5.0.json','3.5x over v5e and 12% over v4.1',', '.join(f"{r['Scenario']} {float(r['Performance_Result']):.3f}" for r in G if 'stable-diffusion' in r['Model'] and 'TPU' in r['Accelerator']),'CANNOT_TELL','The v5.0 Trillium values are in the file (4 chips). The v4.1 results for TPU v5e and Trillium are not in the files used here.'))
nv={(r['Model']):float(r['Performance_Result']) for r in R if r['ID']=='5.0-0060' and r['Scenario']=='Offline'}
gg={(r['Model']):float(r['Performance_Result']) for r in R if r['ID']=='5.0-0035' and r['Scenario']=='Offline'}
rat=sorted((m,gg[m]/nv[m]) for m in gg if m in nv)
C.append(mk('GV4','Google Cloud\'s A3 Ultra demonstrated highly competitive performance, achieving results comparable to NVIDIA\'s peak GPU submissions across LLMs, MoE, image, and recommendation models','Google 5.0-0035 (A3 Ultra, eight H200) against NVIDIA 5.0-0060 (eight H200), Offline','comparable to NVIDIA peak',', '.join(f'{m} {x:.3f}' for m,x in rat),'CANNOT_TELL','The post gives no threshold for comparable. The ratios run from '+f'{rat[0][1]:.3f}'+' to '+f'{max(x for _,x in rat):.3f}'+'. Peak is read as NVIDIA on the same eight H200.'))
C.append(mk('GV5','JetStream achieves 1703 token/s on Llama 3.1 405B on Trillium','Google internal measurement, not an MLPerf entry','1703 token/s on Llama 3.1 405B','no Trillium Llama 3.1 405B entry in raw/inf_5.0.json','CANNOT_TELL','The post presents Figures 1 to 4 as Google internal data.'))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[x]).hexdigest() for x in FILES],claims=C),open('claims_google_v50.json','w'),indent=1)
for c in C: print(c['id'],c['outcome'],'|',c['stated'][:44],'|',c['delivered'][:300])
