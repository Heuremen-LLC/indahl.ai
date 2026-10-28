# Supermicro "Data Center Stories" posts on MLPerf v6.0 inference (Whisper) and training (scaling). Run after parse_training_v60.py: python3 -I check_claims_supermicro_v60.py
import json,hashlib,re,math
R=open('raw/inf_6.0.json','rb').read(); D=json.loads(R); T=json.load(open('training_v60_times.json')); TR=open('training_v60_times.json','rb').read()
def cnt(x):
    m=re.findall(r'\(x(\d+)\)',x['Accelerator']); return sum(map(int,m)) if m else x['Total Accelerators']
def mk(cid,quote,calc,stated,got,outcome,note): return dict(id=cid,quote=quote,calc=calc,stated=stated,delivered=got,outcome=outcome,note=note,label_mismatch=False)
w=sorted([x for x in D if x['Model']=='whisper' and x['Scenario']=='Offline' and x['Category']=='closed' and 'datacenter' in x['Suite']],key=lambda x:-x['Performance_Result'])
s=[x for x in w if x['ID']=='6.0-0098'][0]; rank=1+sum(1 for x in w if x['Performance_Result']>s['Performance_Result'])
inf=[mk('U1','Supermicro posted the top result on the Whisper benchmark, achieving over 50,562 samples per second','entry 6.0-0098 against every closed datacenter Whisper offline result in v6.0 ('+str(len(w))+' rows)','top result, over 50,562 samples/s',f'{s["Performance_Result"]:,.1f} samples/s, rank {rank} of {len(w)}. Next: {w[1]["Submitter"]} {w[1]["Performance_Result"]:,.1f} ({w[1]["ID"]})','CONSISTENT' if rank==1 else 'BELOW','Whisper has an offline scenario only. The result is the total for one 8-GPU system.'),
 mk('U2','dual AMD EPYC™ 9575F CPUs','processor columns of entry 6.0-0098','2 x AMD EPYC 9575F',f'{s["Processor"]}, {s["host_processors_per_node"]} per node','CONSISTENT','matches'),
 mk('U3','2.3 TB of HBM3e GPU memory per system','accelerator and platform names of entry 6.0-0098, 8 GPUs','2.3 TB',f'accelerator column {s["Accelerator"]} (8 x 270 GB = 2.16 TB), platform name {s["Platform"]} (8 x 288 GB = 2.30 TB)','CANNOT_TELL','The two names in the entry disagree about the memory per GPU. The stated figure matches the platform name.')]
json.dump(dict(source=['raw/inf_6.0.json'],sha256=[hashlib.sha256(R).hexdigest()],claims=inf),open('claims_supermicro_v60.json','w'),indent=1)
sm=[o for o in T if o['submitter']=='Supermicro']
def best(b,g,pat): 
    c=[o for o in sm if o['benchmark']==b and o['gpus']==g and pat in str(o['accelerator'])]; return min(c,key=lambda o:o['official_style']) if c else None
rows=[]
for b in ('llama31_8b','llama2_70b_lora','gpt_oss_20b'):
    a8=best(b,8,'B300'); a72=best(b,72,'GB300'); a16=best(b,16,'B300')
    rows.append((b,a8,a16,a72))
def eff(a,g):  # speedup over the 8 GPU entry divided by the GPU ratio
    return (rows_b8/a['official_style'])/(g/8)
txt=[];effs=[]
for b,a8,a16,a72 in rows:
    e72=(a8['official_style']/a72['official_style'])/9; effs.append(e72)
    t=f'{b} 8 GPUs {a8["official_style"]:.3f} min, 72 GPUs {a72["official_style"]:.3f} min, speedup {a8["official_style"]/a72["official_style"]:.2f}x for 9x the GPUs ({e72*100:.0f}% of linear)'
    if a16: t+=f', 16 GPUs {a16["official_style"]:.3f} min, speedup {a8["official_style"]/a16["official_style"]:.2f}x for 2x ({a8["official_style"]/a16["official_style"]/2*100:.0f}% of linear)'
    txt.append(t)
tr=[mk('V1','demonstrated linear scaling in training performance for 3 different models, scaling from 8 GPU to 72 B300 GPUs','Supermicro 8 x B300 and 72 x GB300 result sets, official-style time to train (olympic average with scaling factor), benchmarks with both: Llama 3.1 8B, Llama 2 70B LoRA, GPT-OSS 20B','linear scaling for 3 models, 8 to 72 GPUs','; '.join(txt),'BELOW',f'Linear would cut time to train by 9x. The file shows {min(effs)*100:.0f}% to {max(effs)*100:.0f}% of that. The post does not define performance, and larger runs change batch size. Time to train is the primary MLPerf metric.')]
b8=rows[0][1]; b16=rows[0][2]; b72=rows[0][3]
def line(a8,a16,a72):
    s16=a8['official_style']/a16['official_style']; s72=a8['official_style']/a72['official_style']
    lin=1+(s72-1)*(16-8)/(72-8); lg=s72**(math.log(2)/math.log(9))
    return s16,lin,lg
s16,lin,lg=line(b8,b16,b72)
tr.append(mk('V2','2 systems of HGX-B300 showed even better performance than the linear scaling for HGX-B300 to NVL72','Llama 3.1 8B, 16 GPU entry against the straight line (linear axes) and the power-law line (log axes) joining the 8 and 72 GPU entries','16 GPUs above the 8 to 72 GPU scaling line',f'16 GPUs give a {s16:.2f}x speedup over 8 GPUs. The line gives {lin:.2f}x (linear axes) or {lg:.2f}x (log axes)','BELOW','The 16 GPU point sits under the line on both axis choices. The post does not say which axes.'))
c8=rows[1][1]; c16=rows[1][2]; c72=rows[1][3]
s16,lin,lg=line(c8,c16,c72)
tr.append(mk('V3','the 2 systems of HGX-B300 follow the linear scaling of the HGX-B300 to NVL72','Llama 2 70B LoRA, 16 GPU entry against the same two lines','16 GPUs on the 8 to 72 GPU scaling line',f'16 GPUs give a {s16:.2f}x speedup over 8 GPUs. The line gives {lin:.2f}x (linear axes) or {lg:.2f}x (log axes)','BELOW','The post calls the model Llama 3.1 70b. The benchmark in the repository is llama2_70b_lora.'))
cmp_=[]
for b in ('llama31_8b','llama2_70b_lora','gpt_oss_20b','dlrm_dcnv2'):
    a=best(b,8,'B300'); r=best(b,8,'B200-SXM')
    cmp_.append(f'{b} B300 {a["official_style"]:.2f} min against B200 {r["official_style"]:.2f}')
tr.append(mk('V4','B300 performs better than B200 in Training performance','Supermicro 8 GPU entries, official-style time to train, B300 against B200','B300 faster than B200','; '.join(cmp_),'CONSISTENT','B300 is faster on all four benchmarks where Supermicro ran both.'))
json.dump(dict(source=['training_v60_times.json'],sha256=[hashlib.sha256(TR).hexdigest()],claims=tr),open('claims_supermicro_training_v60.json','w'),indent=1)
for c in inf+tr: print(c['id'],c['outcome'],'|',c['stated'],'|',c['delivered'][:260])
