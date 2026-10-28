# Dell Technologies post on MLPerf Inference v6.1 (PowerEdge R770 and R770AP). Reads raw/inf_6.0.json and raw/inf_6.1.json. python3 -I check_claims_dell_v61.py
import json,hashlib
R0=open('raw/inf_6.0.json','rb').read(); R1=open('raw/inf_6.1.json','rb').read()
V0=json.loads(R0); V1=list(json.loads(R1).values())
def v1(org,model,scen,sysname):
    r=[x for x in V1 if x['Organization']==org and x['Model']==model and x['Scenario']==scen and x['Division']=='closed' and sysname in x['SystemName']]
    assert len(r)==1,(org,model,scen,sysname,len(r)); return r[0]['Result']
def v0(id_,model,scen):
    r=[x for x in V0 if x['ID']==id_ and x['Model']==model and x['Scenario']==scen and x['Category']=='closed']
    assert len(r)==1,(id_,model,scen); return r[0]['Performance_Result']
pct=lambda a,b: 100*(a/b-1)
f=lambda x:f'{x:,.2f}'.rstrip('0').rstrip('.') if x<100 else f'{x:,.1f}'
def mk(i,q,calc,st,got,out,note): return dict(id=i,quote=q,calc=calc,stated=st,delivered=got,outcome=out,note=note,label_mismatch=False)
S86='R770_86C'; S128='R770AP_128C'
d=lambda m,s:v1('Dell',m,s,S86)
# generational
g={('llama3_1-8b','Server'):('llama3.1-8b',245.6,516.0,110.1),('llama3_1-8b','Offline'):('llama3.1-8b',807.7,1228.0,52.0),('rgat','Offline'):('rgat',14283.7,16042.8,12.3),('whisper','Offline'):('whisper',1414.3,1539.5,8.9)}
old=lambda m,s:v0('6.0-0018',m,s)
gen={}
for (m1,s),(m0,a,b,p) in g.items(): gen[(m1,s)]=(old(m0,s),d(m1,s),pct(d(m1,s),old(m0,s)),p)
C=[]
def gline(k): o,n,u,p=gen[k]; return f'v6.0 entry 6.0-0018 {o:,.2f}, v6.1 entry 6.1-0032 {n:,.2f}, change {u:+.1f}%'
C.append(mk('D1','Llama 3.1-8B Server throughput on the R770 more than double generation-over-generation (+110.1%).','Dell R770 (Xeon 6787P, 2 x 86 cores) Llama 3.1-8B Server, v6.0 entry 6.0-0018 against v6.1 entry 6.1-0032','+110.1%',gline(('llama3_1-8b','Server')),'CONSISTENT' if abs(gen[('llama3_1-8b','Server')][2]-110.1)<0.06 else 'ABOVE','The ratio is '+f"{gen[('llama3_1-8b','Server')][1]/gen[('llama3_1-8b','Server')][0]:.3f}"+'.'))
C.append(mk('D2','Llama 3.1-8B Offline Tokens/sec 807.7 1,228.0 +52.0%','same two entries, Llama 3.1-8B Offline','+52.0%',gline(('llama3_1-8b','Offline')),'CONSISTENT' if abs(gen[('llama3_1-8b','Offline')][2]-52.0)<0.06 else 'ABOVE',''))
C.append(mk('D3','RGAT Offline Samples/sec 14,283.7 16,042.8 +12.3%','same two entries, RGAT Offline','+12.3%',gline(('rgat','Offline')),'CONSISTENT' if abs(gen[('rgat','Offline')][2]-12.3)<0.06 else 'ABOVE',''))
C.append(mk('D4','Whisper Offline Tokens/sec 1,414.3 1,539.5 +8.9%','same two entries, Whisper Offline','+8.9%',gline(('whisper','Offline')),'CONSISTENT' if abs(gen[('whisper','Offline')][2]-8.9)<0.06 else 'ABOVE','The post labels the Whisper unit tokens/sec. The files list samples/s.'))
# vs same CPU competitor (the only other 86 core 2 x Xeon 6787P CPU-only entry in the v6.1 file is Supermicro 1-node-2S-GNR_86C)
sm=lambda m,s:v1('Supermicro',m,s,'1-node-2S-GNR_86C')
rows=[('llama3_1-8b','Server'),('llama3_1-8b','Offline'),('rgat','Offline'),('whisper','Offline')]
cmp={k:(sm(*k),d(*k),pct(d(*k),sm(*k))) for k in rows}
cs='; '.join(f'{k[0]} {k[1]}: {a:,.2f} against {b:,.2f} ({p:+.2f}%)' for k,(a,b,p) in cmp.items())
leads=sum(1 for a,b,p in cmp.values() if p>0.05)
C.append(mk('D5','The R770 outperformed a same-CPU competitive system on 3 of 4 workloads, by as much as +20.8% on RGAT.','Dell R770 entries against the Supermicro entry 6.1-0096 (1-node-2S-GNR_86C), which is the only other Xeon 6787P entry in the v6.1 file. The post does not name Vendor B',
 '3 of 4 workloads, up to +20.8%','Supermicro against Dell: '+cs,'CONSISTENT' if leads==3 else 'BELOW',f'Dell leads on {leads} of 4. RGAT is {cmp[("rgat","Offline")][2]:+.2f}%, which the post rounds down to +20.8%. We take the competitor to be the Supermicro entry because its four values match the Vendor B column of the post.'))
sv=cmp[('llama3_1-8b','Server')]
C.append(mk('D6','The R770 server leads on 3 of 4 workloads with zero performance losses.','Llama 3.1-8B Server in the same two entries','zero losses, Llama Server a statistical tie',f'Dell {sv[1]:,.3f} against {sv[0]:,.3f}, Dell lower by {abs(sv[2]):.3f}%','CANNOT_TELL','The Dell value is lower by a few thousandths of a percent. The files hold one result per entry and no spread between runs, so a tie cannot be tested.'))
# R770AP
i0=lambda m,s:v0('6.0-0057',m,s); s0=lambda m,s:v0('6.0-0096',m,s)
ll=[x for x in V1 if x['Organization']=='Dell' and S128 in x['SystemName'] and x['Model']=='llama3_1-8b']
intel61=v1('Intel','llama3_1-8b','Offline','1-node-2S-GNR_128C')
C.append(mk('D7',"The R770AP's debut submission posted a +38.7% Llama Offline gain over the Intel reference baseline.",'Dell R770AP entry 6.1-0031 in the v6.1 file, Llama 3.1-8B; v6.0 Intel entry 6.0-0057 Llama Offline 1,229.56',
 '+38.7%, 1,706.45 tokens/s',f'No Dell R770AP Llama 3.1-8B entry in the v6.1 file ({len(ll)} rows). The file lists Dell R770AP for RGAT and Whisper only. Intel on the same CPU is listed at {intel61:,.2f} in v6.1','CANNOT_TELL','The post says elsewhere that it did not publish Llama on the R770AP. The 1,706.45 value is not in the file.'))
r_i=pct(v1('Dell','rgat','Offline',S128),i0('rgat','Offline')); r_s=pct(v1('Dell','rgat','Offline',S128),s0('rgat','Offline'))
w_i=pct(v1('Dell','whisper','Offline',S128),i0('whisper','Offline')); w_s=pct(v1('Dell','whisper','Offline',S128),s0('whisper','Offline'))
C.append(mk('D8','RGAT Offline Intel v6.0 24,149.80 Vendor B v6.0 25,192.70 Dell R770AP v6.1 21,835.40 -9.5% vs. Intel -13.3% vs. Vendor B','Dell R770AP entry 6.1-0031 RGAT Offline 21,835.4 against v6.0 Intel 6.0-0057 and Supermicro 6.0-0096 (same CPU, 128 cores)','-9.5% and -13.3%',
 f'{v1("Dell","rgat","Offline",S128):,.1f} against Intel {i0("rgat","Offline"):,.1f} ({r_i:+.2f}%) and Supermicro {s0("rgat","Offline"):,.1f} ({r_s:+.2f}%)','CONSISTENT' if abs(r_i+9.5)<0.11 and abs(r_s+13.3)<0.11 else 'ABOVE','The Intel change rounds to -9.6% against the stated -9.5%.'))
C.append(mk('D9','Whisper Offline Intel v6.0 2,200.80 Vendor B v6.0 2,091.60 Dell R770AP v6.1 2,275.93 +3.4% vs. Intel +8.8% vs. Vendor B','Dell R770AP entry 6.1-0031 Whisper Offline 2,275.93 against v6.0 Intel 6.0-0057 and Supermicro 6.0-0096','+3.4% and +8.8%, Vendor B v6.0 at 2,091.60',
 f'Intel {i0("whisper","Offline"):,.2f} ({w_i:+.2f}%). Supermicro v6.0-0096 is {s0("whisper","Offline"):,.2f} ({w_s:+.2f}%). No v6.0 row has 2,091.60','BELOW' if abs(w_s-8.8)>0.2 else 'CONSISTENT','The Intel row matches. The Vendor B baseline in the post differs from the Supermicro v6.0 entry on the same CPU.'))
vb=v1('Supermicro','whisper','Offline','1-node-2S-GNR_128C'); wv=pct(v1('Dell','whisper','Offline',S128),vb)
C.append(mk('D10','Dell comes out ahead on Whisper Offline (+1.2%)','Dell R770AP v6.1 Whisper Offline against Supermicro entry 6.1-0095 (128 cores), Whisper Offline','+1.2%',f'{v1("Dell","whisper","Offline",S128):,.2f} against {vb:,.2f} ({wv:+.2f}%)','CONSISTENT' if abs(wv-1.2)<0.06 else 'ABOVE',''))
rg=sorted((x['Organization'],x['Result']) for x in V1 if x['Model']=='rgat' and x['Division']=='closed' and '6980P' in x['host_processor_model_name'])
C.append(mk('D11','is the only other RGAT submitter on this platform','every closed RGAT entry on the Xeon 6980P in v6.1','Dell the only other RGAT submitter besides Vendor B',', '.join(f'{o} {r:,.1f}' for o,r in rg),'CONSISTENT','Two submitters list RGAT on this CPU, Intel and Dell. Supermicro lists none. We read "other" as other than Intel.'))
C.append(mk('D12',"Vendor B's configuration used 24x96 GB MRDIMMs running at 8,800 MT/s, versus the R770AP's 24x96 GB RDIMMs at 6,400 MT/s",'memory fields of the Supermicro 128 core v6.1 entries and the Dell R770AP entry','MRDIMM 8,800 MT/s against RDIMM 6,400 MT/s',
 'The Dell entry name reads 24x96GB (6400 MT/s). The Supermicro entry name and notes carry no memory description','CANNOT_TELL','The Supermicro memory type and speed are not in the summary file. The statement that Intel confirmed the cause is not in any file.'))
cfg=[x for x in V1 if x['Organization']=='Dell' and x['host_processor_model_name'] and 'R770' in x['SystemName']]
C.append(mk('D13','Dell PowerEdge R770 Intel Xeon 6787P 86 Cores per socket 16 x 64 GB RDIMM, 6400 MT/s. Dell PowerEdge R770AP Intel Xeon 6980P 128 Cores per socket 24 x 96 GB RDIMM, 6400 MT/s','processor, cores and system name of the Dell R770 and R770AP v6.1 entries','6787P 86 cores 16x64 GB at 6400. 6980P 128 cores 24x96 GB at 6400',
 '; '.join(sorted({f'{x["SystemName"]}, {x["host_processor_model_name"]}, {x["host_processors_per_node"]} x {x["host_processor_core_count"]} cores' for x in cfg})),'CONSISTENT','All six entries are closed division, datacenter and available.'))
json.dump(dict(source=['raw/inf_6.0.json','raw/inf_6.1.json'],sha256=[hashlib.sha256(R0).hexdigest(),hashlib.sha256(R1).hexdigest()],claims=C),open('claims_dell_v61.json','w'),indent=1)
for c in C: print(c['id'],c['outcome'],'|',c['stated'],'|',c['delivered'][:230])
