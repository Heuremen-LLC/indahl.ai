# Red Hat blog post on MLPerf Inference v5.0 with Supermicro GH200 and OpenShift, held against the v5.0 result file. python3 -I check_claims_redhat_v50.py
import json,hashlib,collections
FILES=['raw/inf_5.0.json','raw/older_rounds_systems.json']; RAW={f:open(f,'rb').read() for f in FILES}
V=json.loads(RAW[FILES[0]]); OLD=json.loads(RAW[FILES[1]]); s=str
def mk(i,q,calc,st,got,out,note): return dict(id=i,quote=q,calc=calc,stated=st,delivered=got,outcome=out,note=note,label_mismatch=False)
O=[x for x in V if 'penShift' in s(x.get('operating_system'))]
ids={x['ID'] for x in O}; e=O[0]
RO=[]
RO.append(mk('RO1','Red Hat OpenShift running on their dual GPU GH200 Grace Hopper Superchip 144GB server','v5.0 file entries whose operating_system field names OpenShift','OpenShift on a dual GH200 144GB server',f'{len(ids)} entries {sorted(ids)}: {e["Submitter"]}, {e["Category"]} division, {e["a#"]} accelerators, {e["System"][:60]}, operating_system {e["operating_system"]}','CONSISTENT' if len(ids)==2 and all(x['a#']==2 and '144GB' in s(x['System']) for x in O) else 'BELOW','The file lists the submitter as Supermicro, in the open division, under entries 5.0-5663 and 5.0-5664 (llama2-70b-99 and 99.9).'))
gh_os=[(r,x['submitter'],x['path'].split('/')[-1][:40]) for r,v in OLD.items() for x in v['selected_systems'] if ('GH200' in x['path'] or 'Grace' in x['path']) and 'penShift' in s(x['operating_system'])]
gh_all=sum(1 for v in OLD.values() for x in v['selected_systems'] if 'GH200' in x['path'] or 'Grace' in x['path'])
RO.append(mk('RO2','This was the first time anyone has submitted an MLPerf result with OpenShift on GH200.','OpenShift entries in the v5.0 file, and system description files with GH200 or Grace in the name in the v3.1, v4.0 and v4.1 repositories','first OpenShift on GH200 submission',f'{len(ids)} OpenShift entries in v5.0 (both this system); in v3.1, v4.0 and v4.1: {gh_all} GH200 or Grace system files, {len(gh_os)} naming OpenShift','CONSISTENT' if not gh_os else 'BELOW','Earlier rounds have no summary file, so the system description files in each repository were read. The v3.1 and v4.0 file lists from the repository API were cut short at the end of the list. Red Hat submitted OpenShift once before, on an L40S system in v4.1.'))
c=collections.defaultdict(set)
for x in V:
    if x['Category']=='closed' and 'datacenter' in x['Suite']: c[x['Model']].add(x['Submitter'])
top=sorted(((len(v),k) for k,v in c.items()),reverse=True); l70=len(c['llama2-70b-99'])
allfam=len({x['Submitter'] for x in V if x['Model'].startswith('llama2-70b')})
RO.append(mk('RO3','there were 17 organizations who submitted Llama 2 70B results, making it the most popular model in this round','closed datacenter v5.0 entries: distinct submitters per model','17 organizations, most popular model',f'llama2-70b-99 has {l70} submitters, next {top[1][1]} {top[1][0]}; {allfam} submitters if open and interactive entries are counted','CONSISTENT' if l70==17 and top[0][1].startswith('llama2-70b') else 'BELOW','The count of 17 matches closed datacenter llama2-70b-99. Counting every llama2-70b variant and division gives 19.'))
RO.append(mk('RO4','The Supermicro MLPerf v5.0 dual GPU GH200 server submission ran OpenShift 4.15 and NVIDIA TRT-LLM for the server stack.','v5.0 entry 5.0-5663 operating_system and Software fields','OpenShift 4.15 and TRT-LLM',f'operating_system {e["operating_system"]}; Software {e["Software"]}','CONSISTENT' if '4.15' in s(e['operating_system']) and 'TensorRT' in s(e['Software']) else 'BELOW','The file names TensorRT 10.8 and CUDA 12.8 and does not use the name TRT-LLM.'))
RO.append(mk('RO5','TRT-LLM uses post-training quantization to quantize llama2-70b to FP8 precision (8-bit floating point).','v5.0 entry 5.0-5663 weight_data_types field','FP8 weights',f'weight_data_types {e["weight_data_types"]}','CONSISTENT' if s(e['weight_data_types']).lower()=='fp8' else 'BELOW',''))
r={(x['Model'],x['Scenario']):x['Performance_Result'] for x in O}
RO.append(mk('RO6','The chart below shows that OpenShift added less than 2% overhead in these four scenarios for Llama2-70b.','OpenShift entries in the v5.0 file against any RHEL 9.4 bare-metal entry for the same system','less than 2% overhead in four scenarios',f'{len(O)} OpenShift rows (Offline {r[("llama2-70b-99","Offline")]:,.1f}, Server {r[("llama2-70b-99","Server")]:,.1f}, same for 99.9); RHEL 9.4 rows for this system in the file: 0','CANNOT_TELL','The overhead is a comparison with a RHEL 9.4 run that is not an entry in the result file. The chart is not a file field.'))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[f]).hexdigest() for f in FILES],claims=RO),open('claims_redhat_v50.json','w'),indent=1)
for c in RO: print(c['id'],c['outcome'],'|',c['stated'][:48],'|',c['delivered'][:230])
