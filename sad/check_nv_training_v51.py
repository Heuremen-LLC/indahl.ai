# NVIDIA technical blog on MLPerf Training v5.1, held against the v5.0 and v5.1 training times. python3 -I check_claims_nv_training_v51.py
import json,hashlib
FILES=['training_v51_times.json','training_v50_times.json']; RAW={f:open(f,'rb').read() for f in FILES}
T=json.loads(RAW[FILES[0]]); U=json.loads(RAW[FILES[1]]); s=str
def mk(i,q,calc,st,got,out,note): return dict(id=i,quote=q,calc=calc,stated=st,delivered=got,outcome=out,note=note,label_mismatch=False)
dp=lambda v:len(s(v).split('.')[1]) if '.' in s(v) else 0
ok=lambda a,v:abs(a-v)<=0.5*10**-dp(v)*1.0001
NV=lambda x:'NVIDIA' in x['accelerator']
def best(b,pool=T,f=NV):
    r=sorted([x for x in pool if x['benchmark']==b and f(x)],key=lambda x:x['official_style'])[0]; return r
def one(pool,b,g,acc,sub=None):
    r=[x for x in pool if x['benchmark']==b and x['gpus']==g and acc in x['accelerator'] and (sub is None or x['submitter']==sub)]
    return sorted(r,key=lambda x:x['official_style'])[0]['official_style'] if r else None
NV51=[]
cells=[('llama31_405b',10,'5,120'),('llama31_8b',5.2,'512'),('llama2_70b_lora',0.40,'512'),('flux1',12.5,'1,152'),('dlrm_dcnv2',0.71,'64'),('rgat',0.84,'256'),('retinanet',1.4,'512')]
got=[];bad=[]
for b,v,g in cells:
    r=best(b,U) if b=='dlrm_dcnv2' else best(b); got.append(f"{b} {r['submitter']} {r['gpus']} GPUs {r['official_style']:.3f}")
    if not ok(r['official_style'],v) or f"{r['gpus']:,}"!=g: bad.append(b)
NV51.append(mk('NW1','Table 1 in the post, time to train and maximum submission scale on seven benchmarks','training_v51_times.json, fastest entry per benchmark on NVIDIA accelerators (DLRM-DCNv2 from the v5.0 file), official-style time and GPU count','10, 5.2, 0.40, 12.5, 0.71, 0.84 and 1.4 minutes at 5,120, 512, 512, 1,152, 64, 256 and 512 GPUs','; '.join(got),'CONSISTENT' if not bad else 'BELOW','Mismatches: '+(', '.join(bad) or 'none')+f". The scale is the GPU count of the fastest entry. The DLRM-DCNv2 row is the v5.0 entry (the post footnote lists 5.0-0082) and the fastest v5.1 DLRM entry is {best('dlrm_dcnv2')['official_style']:.2f} min."))
f=lambda b:best(b)['submitter']
allfast=[]
for b in ('llama31_405b','llama31_8b','llama2_70b_lora','flux1','dlrm_dcnv2','rgat','retinanet'):
    ov=sorted([x for x in T if x['benchmark']==b],key=lambda x:x['official_style'])[0]; allfast.append((b,ov['submitter'],NV(ov)))
NV51.append(mk('NW2','The NVIDIA Blackwell architecture powered the fastest time to train across every MLPerf Training v5.1 benchmark','fastest entry per benchmark in training_v51_times.json, any submitter, NVIDIA accelerators counted as the NVIDIA platform','fastest time to train on every benchmark',', '.join(f'{b}: {a} {"NVIDIA accel" if n else "other"}' for b,a,n in allfast),'CONSISTENT' if all(n for *_,n in allfast) else 'BELOW','The post says at maximum scale and at each submitted scale. Only the maximum scale (fastest overall) is recomputed here.'))
fl=sorted({(x['submitter'],x['accelerator']) for x in T if x['benchmark']=='flux1'})
NV51.append(mk('NW3','NVIDIA was also the only platform to submit to this benchmark','accelerators of all FLUX.1 entries in training_v51_times.json','only the NVIDIA platform submitted to FLUX.1','; '.join(f'{a} on {c[:34]}' for a,c in fl),'CONSISTENT' if all('NVIDIA' in c for _,c in fl) else 'BELOW','Other submitters appear, all on NVIDIA accelerators. Platform is read as accelerator.'))
pb=sorted([x for x in U if x['benchmark']=='llama31_405b' and 'Blackwell' in x['accelerator']],key=lambda x:x['official_style'])[0]
nb=best('llama31_405b'); r27=pb['official_style']/nb['official_style']
NV51.append(mk('NW4','NVIDIA set a new time-to-train record of 10 minutes powered by 5,120 Blackwell GPUs. This is a 2.7x increase compared to the fastest submission using Blackwell GPUs last round','fastest Blackwell Llama 3.1 405B entry in training_v50_times.json over the v5.1 5,120 GPU entry',"10 minutes, 2.7x",f"v5.1 {nb['official_style']:.3f} min on {nb['gpus']} GPUs; v5.0 fastest Blackwell {pb['official_style']:.2f} min on {pb['gpus']} GPUs ({pb['submitter']}); ratio {r27:.3f}x",'CONSISTENT' if ok(nb['official_style'],10) and abs(r27-2.7)<0.05 else 'BELOW','The v5.0 entry was submitted by IBM, CoreWeave and NVIDIA together.'))
h=one(U,'llama31_405b',2560,'H100'); b2560=one(T,'llama31_405b',2560,'Blackwell')
r3=h/b2560
NV51.append(mk('NW5','the submission using 2,560 Blackwell GPUs achieved a score of 18.79 minutes. This is 3x faster than the previous NVIDIA submissions with the same number of NVIDIA Hopper architecture GPUs','2,560 GPU Blackwell entry in training_v51_times.json and 2,560 GPU H100 entry in training_v50_times.json','18.79 minutes, 3x',f'Blackwell {b2560:.3f}; H100 {h:.2f}; ratio {r3:.2f}x','CONSISTENT' if ok(b2560,18.79) and abs(r3-3)<0.1 else 'BELOW','3.06x rounds to 3x.'))
b2496=pb['official_style'] if pb['gpus']==2496 else None
pg=(b2496/b2560)*(2496/2560)
NV51.append(mk('NW6','Effective performance per Blackwell GPU also increased by 42%, when comparing the performance of the 2,496 Blackwell GPU submission last round to the 2,560 Blackwell GPU submission this round','27.34 over 18.79 times 2,496 over 2,560, from the two entries','42%',f'{b2496} min on 2,496 GPUs and {b2560:.3f} min on 2,560 GPUs give {100*(pg-1):.1f}%','CONSISTENT' if round(100*(pg-1))==42 else 'BELOW','The post says performance per GPU is derived by dividing the ratios of delivered performance and scales submitted.'))
e512=one(T,'llama31_405b',512,'Blackwell GPU (GB200)')
eff=(e512/nb['official_style'])/10
NV51.append(mk('NW7','Scaling efficiency, which is the amount of performance increase with additional GPUs, scaled by 10x from 512 Blackwell GPUs to 5,120 Blackwell GPUs, was 85%','512 GPU GB200 entry over 5,120 GPU entry, divided by 10',"85%",f"512 GPUs {e512:.2f} min, 5,120 GPUs {nb['official_style']:.3f} min, efficiency {100*eff:.1f}%",'CONSISTENT' if round(100*eff)==85 else 'BELOW','The 512 GPU Blackwell Ultra entry (64.6 min) is a different accelerator and is not used.'))
NV51.append(mk('NW8','NVIDIA makes the industry’s first FP4 training submissions with NVFP4','no earlier training rounds record numeric formats in the files','first FP4 training submissions','the times files do not hold numeric formats','CANNOT_TELL','Numeric format is in the submission code, which is not in the files used here.'))
NV51.append(mk('NW9','Figure 1. Relative Llama 3.1 405B pretraining and Llama 2 70B LoRA fine-tuning performance at 512-GPU and 8-GPU scales, respectively','figure values are not printed in the post','figure 1 relative performance','figure values not in the text','CANNOT_TELL','The post cites entries 4.1-0050, 5.0-0076, 5.0-0067, 5.1-0058 and 5.1-0060 and prints no numbers for the figure.'))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[x]).hexdigest() for x in FILES],claims=NV51),open('claims_nv_training_v51.json','w'),indent=1)
for c in NV51: print(c['id'],c['outcome'],'|',c['stated'][:44],'|',c['delivered'][:300])
