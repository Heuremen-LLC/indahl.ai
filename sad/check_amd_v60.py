# AMD ROCm blog "AMD Instinct GPUs MLPerf Inference v6.0 Submission" against the MLCommons summary files. Run: python3 -I check_claims_amd_v60.py
import json,hashlib,re,statistics
R={v:open(f'raw/inf_{v}.json','rb').read() for v in ('5.0','5.1','6.0')}; D={v:json.loads(r) for v,r in R.items()}; D6=D['6.0']
def cnt(x):
    m=re.findall(r'\(x(\d+)\)',x['Accelerator']); return sum(map(int,m)) if m else x['Total Accelerators']   # the accelerator name states the count (x87 on 11 nodes)
def one(i,mod,sc,cat=None,D_=D6):
    r=[x for x in D_ if x['ID']==i and x['Model']==mod and x['Scenario']==sc and (cat is None or x['Category']==cat)]; assert len(r)==1,(i,mod,sc,len(r)); return r[0]
pg=lambda x:x['Performance_Result']/cnt(x)
out=[]
def claim(cid,quote,calc,stated,got,outcome,note): out.append(dict(id=cid,quote=quote,calc=calc,stated=stated,delivered=got,outcome=outcome,note=note,label_mismatch=False))
# V1 over a million
m1o,m1s,m3o,m3s=one('6.0-0001','llama2-70b-99','Offline'),one('6.0-0001','llama2-70b-99','Server'),one('6.0-0003','gpt-oss-120b','Offline'),one('6.0-0003','gpt-oss-120b','Server')
rivals=[(x['ID'],x['Submitter'],x['Model'],x['Scenario'],x['Performance_Result']) for x in D6 if x['Submitter']!='AMD' and x['Category']=='closed' and x['Model'] in('llama2-70b-99','gpt-oss-120b') and x['Performance_Units'].startswith('Tokens') and x['Performance_Result']>=1e6]
earlier=[(v,x['ID']) for v in ('5.0','5.1') for x in D[v] if x['Model'] in('llama2-70b-99','gpt-oss-120b') and x['Performance_Units'].startswith('Tokens') and x['Performance_Result']>=1e6]
claim('V1','It was the first ever MLPerf submission with over a million tokens/sec for Llama 2 70B (11-nodes) and gpt-oss-120b (12-nodes) in the Closed division.','entries 6.0-0001 (87 GPUs, 11 nodes) and 6.0-0003 (94 GPUs, 12 nodes), closed, tokens/s; every other closed row at or over one million for those models in v5.0, v5.1 and v6.0',
 'over a million tokens/s, first ever',f'Llama 2 70B {m1o["Performance_Result"]:,.0f} offline and {m1s["Performance_Result"]:,.0f} server. gpt-oss-120b {m3o["Performance_Result"]:,.0f} offline and {m3s["Performance_Result"]:,.0f} server. In the same round, {", ".join(sorted({r[1]+" "+r[0] for r in rivals}))} also list closed results over one million for these models. No v5.0 or v5.1 row for them reaches one million ({len(earlier)} rows)','CANNOT_TELL',
 'The figures hold for the offline and server results except gpt-oss-120b server, which is under one million. The file has no submission order, so it cannot say which entry was first within the round.')
# V2, V3 scaling
s1={sc:one('6.0-0002','llama2-70b-99',sc) for sc in ('Offline','Server','Interactive')}; m1={sc:one('6.0-0001','llama2-70b-99',sc) for sc in ('Offline','Server','Interactive')}
eff={sc:pg(m1[sc])/pg(s1[sc]) for sc in s1}
claim('V2','Offline and Server achieving 93% scaling efficiency while Interactive is even better at 98%.','per GPU result of 6.0-0001 (87 GPUs) over per GPU result of the single node entry 6.0-0002 (8 GPUs), Llama 2 70B','93% offline and server, 98% interactive',f'{eff["Offline"]*100:.1f}% offline, {eff["Server"]*100:.1f}% server, {eff["Interactive"]*100:.1f}% interactive','CONSISTENT','Uses 87 GPUs as the entry name states. The count in the file column Total Accelerators is 88.')
s3={sc:one('6.0-0002','gpt-oss-120b',sc) for sc in ('Offline','Server')}; m3={'Offline':m3o,'Server':m3s}
eff3={sc:pg(m3[sc])/pg(s3[sc]) for sc in s3}
claim('V3','The results (see figure below) show an efficient distributed inference with scaling of 92% and 93% over 12 nodes.','per GPU result of 6.0-0003 (94 GPUs) over per GPU result of 6.0-0002 (8 GPUs), gpt-oss-120b','92% and 93%',f'{eff3["Offline"]*100:.1f}% offline, {eff3["Server"]*100:.1f}% server','CONSISTENT','Uses 94 GPUs as the entry name states. The count in the file column Total Accelerators is 96.')
allv=list(eff.values())+list(eff3.values())
claim('V4','This was accomplished with efficient scale-up and scale-out end-to-end ROCm solution stack optimization that achieved a 97-98% scaling efficiency.','the five scaling figures in V2 and V3','97-98%',f'{min(allv)*100:.1f}% to {max(allv)*100:.1f}%, with only Llama 2 70B interactive at {eff["Interactive"]*100:.1f}%','BELOW','The same post gives 93%, 98%, 92% and 93% for these runs.')
# V5 vs B300
def b300(mod,sc): return [x for x in D6 if x['Model']==mod and x['Scenario']==sc and x['Category']=='closed' and re.search(r'B300-SXM',x['Accelerator']) and x['Performance_Units'].startswith('Tokens')]
nv={sc:[x for x in b300('llama2-70b-99',sc) if x['Submitter']=='NVIDIA'] for sc in ('Offline','Server')}
inter=sorted(b300('llama2-70b-99','Interactive'),key=lambda x:-pg(x))
r5={sc:pg(s1[sc])/pg(nv[sc][0]) for sc in nv}; r5i=pg(s1['Interactive'])/pg(inter[0])
claim('V5','Against Nvidia’s B300, AMD’s GPU delivers 92% in offline mode, 93% in server mode, and exceeds with 104% in interactive mode.','AMD 8 x MI355X (6.0-0002) over 8 x B300, per GPU, Llama 2 70B: NVIDIA entry %s offline and server, the best of the %d B300 interactive rows (%s) interactive'%(nv['Offline'][0]['ID'],len(inter),inter[0]['Submitter']),'92% offline, 93% server, 104% interactive',f'{r5["Offline"]*100:.1f}% offline, {r5["Server"]*100:.1f}% server, {r5i*100:.1f}% interactive','CONSISTENT','Against the best B300 offline result from any submitter the ratio is %.1f%%, and server %.1f%%.'%(pg(s1['Offline'])/max(pg(x) for x in b300('llama2-70b-99','Offline'))*100,pg(s1['Server'])/max(pg(x) for x in b300('llama2-70b-99','Server'))*100))
# V6 gpt-oss vs B200
b200={sc:sorted([x for x in D6 if x['Model']=='gpt-oss-120b' and x['Scenario']==sc and x['Category']=='closed' and re.search(r'B200-SXM',x['Accelerator'])],key=lambda x:pg(x)) for sc in ('Offline','Server')}
a6={sc:pg(s3[sc]) for sc in s3}
claim('V6','achieving up to 115% in server mode and 111% in offline mode','AMD 8 x MI355X (6.0-0002) over each of the %d closed 8 x B200 gpt-oss-120b rows, per GPU'%len(b200['Server']),'up to 115% server, 111% offline',f'against the lower B200 row {a6["Server"]/pg(b200["Server"][0])*100:.1f}% server ({b200["Server"][0]["Submitter"]}) and {a6["Offline"]/pg(b200["Offline"][0])*100:.1f}% offline ({b200["Offline"][0]["Submitter"]}). Against the higher B200 row {a6["Server"]/pg(b200["Server"][-1])*100:.1f}% server and {a6["Offline"]/pg(b200["Offline"][-1])*100:.1f}% offline','CONSISTENT',
 'The post says it shows the two best B200 results from NVIDIA partners because NVIDIA submitted none. Against the B300 rows the ratios are below 100%.')
i405=one('6.0-0102','llama3.1-405b','Interactive')
claim('V7','achieved a throughput of 793 tokens/second','entry 6.0-0102, Llama 3.1 405B Interactive, open division, 8 x MI355X','793 tokens/s',f'{i405["Performance_Result"]:.3f} tokens/s','CONSISTENT','Open division, with about 20% of the 126 layers dropped as the post says.')
o48=pg(s1['Offline'])*8; v51=one('5.1-0002','llama2-70b-99','Offline',D_=D['5.1']); v50=one('5.0-0001','llama2-70b-99','Offline',D_=D['5.0']); v51s=one('5.1-0002','llama2-70b-99','Server',D_=D['5.1']); v50s=one('5.0-0001','llama2-70b-99','Server',D_=D['5.0'])
claim('V8','Offline scores improved by 4.4x and Server scores improved by 4.8x.','6.0-0002 over the AMD 8 x MI325X entries of v5.0 (5.0-0001) and v5.1 (5.1-0002), Llama 2 70B','4.4x offline, 4.8x server',f'{s1["Offline"]["Performance_Result"]/v50["Performance_Result"]:.2f}x offline and {s1["Server"]["Performance_Result"]/v50s["Performance_Result"]:.2f}x server over v5.0. {s1["Offline"]["Performance_Result"]/v51["Performance_Result"]:.2f}x and {s1["Server"]["Performance_Result"]/v51s["Performance_Result"]:.2f}x over v5.1. The stated ratios imply earlier scores of {s1["Offline"]["Performance_Result"]/4.4:,.0f} and {s1["Server"]["Performance_Result"]/4.8:,.0f} tokens/s','CANNOT_TELL','The comparison is shown in a figure against earlier rounds, and the earlier AMD result it uses is not in the v5.0 or v5.1 files.')
amdp=sorted({x['Submitter'] for x in D6 if 'AMD Instinct' in x['Accelerator']})
claim('V9','AMD had 9 partners: Oracle, Cisco, Dell, Giga Computing, MangoBoost, MiTAC, HPE, Supermicro, and Red Hat.','submitters of v6.0 entries with an AMD Instinct accelerator, other than AMD','9 partners',f'{len([s for s in amdp if s!="AMD"])} submitter names: {", ".join(s for s in amdp if s!="AMD")}','CONSISTENT','Dell and MangoBoost also appear as one joint name, and Red Hat appears in the joint entry with Supermicro. That makes nine organizations.')
t=one('6.0-0031','llama2-70b-99','Offline')
claim('V10','The joint submission by Dell and MangoBoost is notable for being the first ever MLPerf Inference submission featuring three different GPUs: MI300X, MI325X, and MI355X.','entry 6.0-0031, Llama 2 70B','three GPU types in one entry, first ever',f'entry 6.0-0031 lists {t["Accelerator"]}, {t["Nodes"]} nodes','CANNOT_TELL','The entry exists as described. Whether it is the first is outside the v5.0, v5.1 and v6.0 files.')
json.dump(dict(source=[f'raw/inf_{v}.json' for v in R],sha256=[hashlib.sha256(R[v]).hexdigest() for v in R],claims=out),open('claims_amd_v60.json','w'),indent=1)
for c in out: print(c['id'],c['outcome'],'|',c['stated'],'|',c['delivered'][:230])
