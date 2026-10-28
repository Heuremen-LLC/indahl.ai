# Cisco white paper on MLPerf Inference v5.1 with the UCS X210c M8 and Intel Xeon 6, held against the v5.1 result file. python3 -I check_claims_cisco_x210c_v51.py
import json,hashlib
FILES=['raw/inf_5.1.json']; RAW={f:open(f,'rb').read() for f in FILES}
V=json.loads(RAW[FILES[0]]); s=str
def mk(i,q,calc,st,got,out,note): return dict(id=i,quote=q,calc=calc,stated=st,delivered=got,outcome=out,note=note,label_mismatch=False)
E=[x for x in V if x['ID']=='5.1-0017']; g=lambda m,sc:[x for x in E if x['Model']==m and x['Scenario']==sc][0]
CX=[]
x0=E[0]
CX.append(mk('CX1','v5.1 Data Center Inference results obtained on a Cisco UCS X210c M8 Compute Node powered by Intel Xeon 6 processor family','v5.1 entry 5.1-0017','v5.1 datacenter results on a UCS X210c M8 with Xeon 6',f'{x0["Submitter"]} {x0["System"]}, {x0["Category"]} division, {x0["Processor"]}, {len(E)} rows across {len({x["Model"] for x in E})} models','CONSISTENT' if x0['Submitter']=='Cisco' and 'XEON(R) 6787P' in s(x0['Processor']).upper().replace(' ','') .replace('INTEL(R)','') or 'XEON' in s(x0['Processor']).upper() else 'BELOW','The system is named X210M8-1-node-2S-GNR_86C in the file.'))
rows=[('dlrm-v2-99.9','Offline',12503.3,1),('dlrm-v2-99.9','Server',11801.67,2),('retinanet','Offline',501.263,3),('retinanet','Server',400.42,2),('rgat','Offline',16102.2,1),('whisper','Offline',1418.6,1),('llama3.1-8b','Offline',819.624,3),('llama3.1-8b','Server',257.75,2)]
bad=[(m,sc,v,g(m,sc)['Performance_Result']) for m,sc,v,d in rows if abs(g(m,sc)['Performance_Result']-v)>(0.06 if v>1000 else 0.006)]
CX.append(mk('CX2','Table 6 in the post lists inferences per second for five benchmarks in Offline and Server','entry 5.1-0017 result field','eight values, DLRM-v2-99.9 12503.3 and 11801.67, Retinanet 501.263 and 400.42, RGAT 16102.2, Whisper 1418.6, Llama 3.1 8B 819.624 and 257.75',', '.join(f'{m} {sc} {g(m,sc)["Performance_Result"]:g}' for m,sc,v,d in rows),'CONSISTENT' if not bad else 'BELOW','The file prints DLRM Server as 11801.7, Retinanet Server as 400.419 and Llama 3.1 8B Server as 257.749. The post prints the same values rounded differently. Our rule: within 0.06 above 1,000 and within 0.006 below.'))
CX.append(mk('CX3','Processor name Intel Xeon 6787P Host processors per node 2 Host processor core count 86','entry 5.1-0017 host fields','2 x Xeon 6787P, 86 cores',f'{x0["host_processors_per_node"]} x {x0["Processor"]}, {x0["host_processor_core_count"]} cores','CONSISTENT' if (int(x0['host_processors_per_node']),int(x0['host_processor_core_count']))==(2,86) and '6787P' in s(x0['Processor']) else 'BELOW',''))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[f]).hexdigest() for f in FILES],claims=CX),open('claims_cisco_x210c_v51.json','w'),indent=1)
for c in CX: print(c['id'],c['outcome'],'|',c['stated'][:48],'|',c['delivered'][:230])
