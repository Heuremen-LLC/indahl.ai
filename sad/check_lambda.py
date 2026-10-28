# Lambda blog "Lambda's MLPerf Inference v6.0" against the MLCommons summary files. Run: python3 -I check_claims_lambda_v60.py
import json,hashlib,re
R={v:open(f'raw/inf_{v}.json','rb').read() for v in ('5.1','6.0')}; D={v:json.loads(r) for v,r in R.items()}
def cnt(x):
    m=re.findall(r'\(x(\d+)\)',x['Accelerator']); return sum(map(int,m)) if m else x['Total Accelerators']
def one(v,i,mod,sc,cat='closed'):
    r=[x for x in D[v] if x['ID']==i and x['Model']==mod and x['Scenario']==sc and x['Category']==cat]; assert len(r)==1,(v,i,mod,sc,len(r)); return r[0]
def mk(cid,quote,calc,stated,got,outcome,note): return dict(id=cid,quote=quote,calc=calc,stated=stated,delivered=got,outcome=outcome,note=note,label_mismatch=False)
out=[]
g_o,g_s=one('6.0','6.0-0063','gpt-oss-120b','Offline'),one('6.0','6.0-0063','gpt-oss-120b','Server')
rh=one('6.0','6.0-0091','gpt-oss-120b','Offline'); nb=one('6.0','6.0-0083','gpt-oss-120b','Server')
r_off=g_o['Performance_Result']/(rh['Performance_Result']/2); r_srv=g_s['Performance_Result']/(nb['Performance_Result']/2)
out.append(mk('P1','up to 29% higher iso-GPU throughput than NVIDIA HGX B200 on GPT-OSS-120B','entry 6.0-0063 (4 x GB300) over half of the best closed 8 x B200 results, 6.0-0091 offline and 6.0-0083 server, gpt-oss-120b','up to 29%',
 f'+{(r_off-1)*100:.1f}% offline ({g_o["Performance_Result"]:,.1f} vs {rh["Performance_Result"]/2:,.1f} tokens/s), +{(r_srv-1)*100:.1f}% server ({g_s["Performance_Result"]:,.1f} vs {nb["Performance_Result"]/2:,.1f})','CONSISTENT',
 'The post says no 4-GPU B200 entry exists, so the baseline is an 8-GPU result halved. That estimate is the post\'s own.'))
out.append(mk('P2','60,220 tokens/s (Offline) and 53,463 tokens/s (Server)','entry 6.0-0063, gpt-oss-120b','60,220 offline and 53,463 server tokens/s',f'{g_o["Performance_Result"]:,.1f} offline and {g_s["Performance_Result"]:,.1f} server tokens/s','CONSISTENT','matches to rounding'))
l_s,l_o,l_i=one('6.0','6.0-0062','llama3.1-8b','Server'),one('6.0','6.0-0062','llama3.1-8b','Offline'),one('6.0','6.0-0062','llama3.1-8b','Interactive')
out.append(mk('P3','130,008 tokens/s (Server), 160,403 tokens/s (Offline), and 128,750 tokens/s (Interactive)','entry 6.0-0062, Llama 3.1 8B','130,008 server, 160,403 offline, 128,750 interactive tokens/s',f'{l_s["Performance_Result"]:,.0f} server, {l_o["Performance_Result"]:,.0f} offline, {l_i["Performance_Result"]:,.0f} interactive','CONSISTENT','matches'))
v51=[x for x in D['5.1'] if x['Model']=='llama3.1-8b' and x['Category']=='closed' and 'B200-SXM' in x['Accelerator'] and x['Nodes']*x['a#']==8]
b_o=max((x for x in v51 if x['Scenario']=='Offline'),key=lambda x:x['Performance_Result']); b_s=max((x for x in v51 if x['Scenario']=='Server'),key=lambda x:x['Performance_Result'])
out.append(mk('P4','up to a 9% throughput gain on Llama 3.1 8B','entry 6.0-0062 over the best v5.1 closed 8 x B200 Llama 3.1 8B result in each scenario','up to 9%',f'+{(l_o["Performance_Result"]/b_o["Performance_Result"]-1)*100:.1f}% offline over {b_o["ID"]} ({b_o["Submitter"]}), +{(l_s["Performance_Result"]/b_s["Performance_Result"]-1)*100:.1f}% server over {b_s["ID"]} ({b_s["Submitter"]})','CONSISTENT','The post attributes the gain to a software update from CUDA 12.9 to 13.1. The file lists CUDA 13.1 for 6.0-0062 and CUDA 12.8 for the v5.1 offline entry.'))
bz=one('6.0','6.0-0110','gpt-oss-120b','Server',cat='open')
out.append(mk('P5','reduces time-to-first-token (TTFT) P99 latency by 31% on GPT-OSS-120B','entry 6.0-0110 (open division), gpt-oss-120b server','TTFT P99 down 31%, throughput 16,167 tokens/s',f'the file holds throughput only: {bz["Performance_Result"]:,.1f} tokens/s','CANNOT_TELL','Latency and the baseline run without BLAZE are not in the summary file. The post says these results are not verified by MLCommons Association.'))
out.append(mk('P6','Lambda is the only AI-native cloud to publish official MLPerf results for both inference and training on an NVIDIA Blackwell Ultra platform','Blackwell Ultra entries by submitter in the inference and training results','only','not settled by the inference file','CANNOT_TELL','Needs the training results and a definition of AI-native cloud.'))
p=[x for x in D['6.0'] if x['ID']=='6.0-0063'][0]
out.append(mk('P7','NVIDIA Blackwell Ultra has 279GB of HBM3e per chip','the platform name of entry 6.0-0063','279GB',f'the entry\'s platform name reads {p["Platform"]}','CANNOT_TELL','The file names the part with 288GB. The post may mean usable capacity.'))
q=one('6.0','6.0-0062','llama3.1-8b','Offline')
out.append(mk('P8','Dual Intel Xeon Platinum 8570 (56 cores)','entry 6.0-0062 processor columns','2 processors, 56 cores',f'{q["Processor"]}, {q["host_processors_per_node"]} per node, {q["host_processor_core_count"]} cores','CONSISTENT','Core count is per processor.'))
json.dump(dict(source=[f'raw/inf_{v}.json' for v in R],sha256=[hashlib.sha256(R[v]).hexdigest() for v in R],claims=out),open('claims_lambda_v60.json','w'),indent=1)
for c in out: print(c['id'],c['outcome'],'|',c['stated'],'|',c['delivered'][:230])
