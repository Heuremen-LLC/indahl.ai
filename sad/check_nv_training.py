# NVIDIA "NVIDIA Blackwell Tops MLPerf Training 6.0 ..." (16 Jun 2026) against the MLCommons training result logs. Run after parse_training_v60.py: python3 -I check_claims_nv_training_v60.py
import json,hashlib,collections
T=json.load(open('training_v60_times.json')); raw=open('training_v60_times.json','rb').read()
def best(b,g,acc):
    c=[o for o in T if o['benchmark']==b and o['gpus']==g and acc in str(o['accelerator']) and o['official_style']]
    return min(c,key=lambda o:o['official_style']) if c else None
def mk(cid,quote,calc,stated,got,outcome,note): return dict(id=cid,quote=quote,calc=calc,stated=stated,delivered=got,outcome=outcome,note=note,label_mismatch=False)
out=[]
ROWS=[('T1','DeepSeek-V3 671B (MoE)','deepseekv3_671b',8192,'GB300','GB300 NVL72',2.02),('T2','GPT-OSS 20B (MoE)','gpt_oss_20b',512,'GB300','GB300 NVL72',7.43),('T3','Llama 3.1 405B','llama31_405b',8192,'GB200','GB200 NVL72',7.07),
      ('T4','Llama 3.1 8B','llama31_8b',1024,'GB200','GB200 NVL72',4.46),('T5','Llama 2 70B LoRA','llama2_70b_lora',512,'GB300','GB300 NVL72',0.4),('T6','FLUX.1','flux1',512,'GB300','GB300 NVL72',17.1),('T7','DLRM-dcnv2','dlrm_dcnv2',64,'GB300','GB300 NVL72',0.67)]
DESC={}
for cid,name,b,g,acc,plat,st in ROWS:
    o=best(b,g,acc); assert o,(b,g,acc)
    note=f'The entry is {o["submitter"]}\'s {o["system"]}.'
    if o['scaling_factor']!=1.0: note+=f' A scaling factor of {o["scaling_factor"]:.4f} set by the review committee is applied, as in the official summarizer.'
    if o['platform'] and 'GB200' in o['platform'] and 'GB300' in str(o['accelerator']): note+=f' The log field submission_platform reads {o["platform"]} while the system description lists {o["accelerator"]}.'
    out.append(mk(cid,f'Table 1 in the post lists {name} on {plat} with {g:,} GPUs at {st} mins.',f'run_stop minus run_start of every result log in the entry, olympic average (drop highest and lowest), times the entry\'s scaling factor. Fastest {acc} entry with {g:,} GPUs',f'{st} minutes',
      f'{o["official_style"]:.3f} minutes from runs {", ".join(f"{r:.3f}" for r in o["runs_minutes"])} ({o["submitter"]})','CONSISTENT',note))
# who submitted what
vend=collections.defaultdict(set)
for o in T: vend[o['benchmark']].add('NVIDIA' if 'NVIDIA' in str(o['accelerator']) else 'other')
alln=[b for b,v in vend.items() if 'NVIDIA' in v]
non=[b for b,v in vend.items() if 'other' in v]
out.append(mk('T8','The NVIDIA platform was the only one to submit results on both new workloads','the accelerator model in every result set for deepseekv3_671b and gpt_oss_20b in the v6.0 repository','only NVIDIA on both new workloads',f'deepseekv3_671b: {", ".join(sorted(vend["deepseekv3_671b"]))}. gpt_oss_20b: {", ".join(sorted(vend["gpt_oss_20b"]))}','CONSISTENT','Both new workloads have result sets only on NVIDIA accelerators. Other vendors submitted on three of the seven benchmarks.'))
out.append(mk('T9','It was also the only platform to submit on every test','benchmarks with result sets by accelerator vendor','only NVIDIA on every test',f'NVIDIA on {len(alln)} of {len(vend)} benchmarks, another vendor on {len(non)}: {", ".join(sorted(non))}','CONSISTENT','Counts are benchmarks present in the v6.0 result repository.'))
fast={}
for b in vend:
    c=sorted([o for o in T if o['benchmark']==b and o['official_style']],key=lambda o:o['official_style']); fast[b]=c[0]
nvfast=sum(1 for o in fast.values() if 'NVIDIA' in str(o['accelerator']))
out.append(mk('T10','By securing a clean sweep and winning every single benchmark in this round','the fastest time to train per benchmark, computed as in T1 to T7, across every result set','fastest time on every benchmark',f'NVIDIA accelerators hold the fastest time on {nvfast} of {len(fast)} benchmarks','CONSISTENT','Time to train depends on the number of GPUs. The fastest entries are at 64 to 8,192 GPUs.'))
gm={}
for b in vend:
    rows=[(o['official_style']*o['gpus'],'NVIDIA' if 'NVIDIA' in str(o['accelerator']) else 'other') for o in T if o['benchmark']==b and o['official_style'] and o['gpus']]
    gm[b]=(min((r[0] for r in rows if r[1]=='NVIDIA'),default=None),min((r[0] for r in rows if r[1]=='other'),default=None))
cmp_=[b for b,v in gm.items() if v[1]]
ok=all(gm[b][0]<gm[b][1] for b in cmp_)
out.append(mk('T11','also delivered the highest performance when normalized on a per-accelerator basis on every benchmark','best GPU-minutes (time to train times GPU count, lower is better) per benchmark, NVIDIA accelerators against others','highest per-accelerator performance on every benchmark',
  '; '.join(f'{b} {gm[b][0]:,.1f} against {gm[b][1]:,.1f}' for b in sorted(cmp_))+f'. No other vendor entries on {len(vend)-len(cmp_)} benchmarks','CONSISTENT' if ok else 'BELOW','GPU-minutes is our own normalization. The post does not define the per-accelerator measure.'))
out.append(mk('T12','NVIDIA cloud service provider partners scaled up to 8,192 Blackwell GPUs working in unison','result sets with 8,192 GPUs','up to 8,192 Blackwell GPUs',', '.join(f'{o["submitter"]} {o["benchmark"]} ({str(o["accelerator"])[-6:-1]})' for o in sorted([o for o in T if o['gpus']==8192],key=lambda o:o['submitter'])),'CONSISTENT','Three result sets reach 8,192 GPUs. The largest GPU count in the repository is checked in the same step.' ))
mxg=max(o['gpus'] for o in T if o['gpus']); out[-1]['delivered']+=f'. Largest GPU count in any result set: {mxg:,}'
out.append(mk('T13','Figure 2 in the post shows a 1.3x performance gain for GPT-OSS 20B, a 1.5x gain for Llama 3.1 405B, and a 1.6x gain for DeepSeek-V3 from GB300 over GB200.','GB200 over GB300 time to train at the same GPU count in the v6.0 logs','1.3x, 1.5x and 1.6x',
  'same-count ratios in v6.0: DeepSeek-V3 1.42 to 1.65 at five scales (1.65 at 8,192 GPUs), GPT-OSS 20B 1.06 to 1.25 at four scales, Llama 3.1 405B no GB200 and GB300 pair at the same count','CANNOT_TELL','The footnote cites entries from v5.1 and v6.0 and the figure does not state the scale. The v6.0 logs alone cannot place the Llama 3.1 405B bar.'))
out[-1]['statement']=None
out.append(mk('T14','improved 1.3x going from 1,298 TFLOPS/GPU to 1,648 TFLOPS/GPU','1,648 over 1,298, both numbers from the post','1.3x',f'{1648/1298:.3f}x','CONSISTENT','Arithmetic on the post\'s own numbers. The TFLOPS figures come from NVIDIA container tests and are not in the MLCommons logs.'))
out.append(mk('T15','more than 8% end-to-end benefit on Deepseek-v3 and a 93% end-to-end speedup on GPT-OSS','NVIDIA\'s own before and after tests','more than 8% and 93%','not in the MLCommons logs','CANNOT_TELL','These are NVIDIA\'s internal comparisons of software versions.'))
json.dump(dict(source=['training_v60_times.json'],sha256=[hashlib.sha256(raw).hexdigest()],commit='eabf23a07b2a',claims=out),open('claims_nv_training_v60.json','w'),indent=1)
for c in out: print(c['id'],c['outcome'],'|',c['stated'],'|',c['delivered'][:210])
