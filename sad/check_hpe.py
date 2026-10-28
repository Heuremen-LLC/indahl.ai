# HPE blog post on MLPerf Inference v6.0 results. Reads raw/inf_6.0.json and raw/inf_5.1.json. python3 -I check_claims_hpe_v60.py
import json,hashlib,re
R0=open('raw/inf_6.0.json','rb').read(); R5=open('raw/inf_5.1.json','rb').read()
A=json.loads(R0); V5=json.loads(R5)
D=[x for x in A if x['Category']=='closed' and 'datacenter' in x['Suite']]
def n(x):
    m=re.findall(r'\(x(\d+)\)',x['Accelerator']); return sum(map(int,m)) if m else x['Total Accelerators']
P=lambda x:x['Performance_Result']
def row(i,m,s,L=D): r=[x for x in L if x['ID']==i and x['Model']==m and x['Scenario']==s]; assert len(r)==1,(i,m,s); return r[0]
def cls(x,L=D): return [y for y in L if y['Model']==x['Model'] and y['Scenario']==x['Scenario'] and y['Accelerator']==x['Accelerator'] and n(y)==n(x)]
def first(x,L=D): return not any(P(y)>P(x) for y in cls(x,L) if y is not x)
def mk(i,q,calc,st,got,out,note): return dict(id=i,quote=q,calc=calc,stated=st,delivered=got,outcome=out,note=note,label_mismatch=False)
C=[]
H=[x for x in A if x['Submitter']=='HPE']; cnt={}
for x in A: cnt[x['Submitter']]=cnt.get(x['Submitter'],0)+1
top=sorted(cnt.items(),key=lambda kv:-kv[1])[:3]
Hd=[x for x in D if x['Submitter']=='HPE']; f1=sum(1 for x in Hd if first(x)); f2=sum(1 for x in Hd if first(x) and len(cls(x))>1); fa=sum(1 for x in Hd if not any(P(y)>P(x) for y in D if y['Model']==x['Model'] and y['Scenario']==x['Scenario'] and y is not x))
C.append(mk('H1','claimed 18 No. 1 rankings across a wide spectrum of AI workloads','HPE closed datacenter rows in v6.0 ('+str(len(Hd))+'), ranked within rows of the same model, scenario, accelerator model and accelerator count, and ranked across all rows of the same model and scenario','18 No. 1 rankings',
 f'First in the same-accelerator, same-count group: {f1} rows. The same count when the group has at least two entries: {f2}. First across every system for its model and scenario: {fa}','CANNOT_TELL','The post does not say how a ranking is defined. No simple rule gives 18.'))
C.append(mk('H2','submitted the highest total number of results—an impressive 862','rows per submitter in the v6.0 file ('+str(len(A))+' rows)','highest total, 862',
 'Rows per submitter: '+', '.join(f'{k} {v}' for k,v in top)+f'. HPE has {len({x["ID"] for x in H})} entries','CANNOT_TELL','HPE has the most rows of any submitter. The file lists 86 rows for HPE and we cannot reproduce 862. The post does not say what it counts.'))
# DL380a
a=[x for x in D if x['ID']=='6.0-0047']; ll=[x for x in a if x['Model'].startswith('llama')]
C.append(mk('H3','Our flagship HPE ProLiant Compute DL380a Gen12 claimed eight No. 1 positions in Llama-focused tests','Llama rows of entry 6.0-0047 (8 x RTX PRO 6000) in the v6.0 file, ranked within the same accelerator and count','eight No. 1 positions in Llama tests',
 f'Entry 6.0-0047 has {len(ll)} Llama rows. First in group: {sum(1 for x in ll if first(x))} of {len(ll)}. Including Whisper: {sum(1 for x in a if first(x) and (x["Model"].startswith("llama") or x["Model"]=="whisper"))}','BELOW' if len(ll)<8 else 'CONSISTENT','The file has no Llama 2 70B Interactive row for this entry. At most seven Llama rows exist, so eight cannot be reached.'))
i0=row('6.0-0047','llama3.1-8b','Interactive'); as_=row('6.0-0004','llama3.1-8b','Interactive'); nb=sorted([y for y in cls(i0) if y is not i0],key=lambda y:-P(y))[0]
C.append(mk('H4','outperforming the next-best system by 29% in the Llama3.1-8B interactive benchmark','entry 6.0-0047 against entry 6.0-0004 (the second entry cited in the post, 8 x RTX PRO 6000), Llama 3.1-8B Interactive',
 '+29%',f'{P(i0):,.1f} against {P(as_):,.1f} ({100*(P(i0)/P(as_)-1):+.1f}%). The next-best entry with the same accelerator and count is {nb["ID"]}','CONSISTENT' if nb['ID']=='6.0-0004' and abs(100*(P(i0)/P(as_)-1)-29)<0.6 else 'ABOVE',''))
xs=[(m,s) for (m,s) in sorted({(x['Model'],x['Scenario']) for x in a}) if m.startswith('llama') and any(y['ID']=='6.0-0023' and y['Model']==m and y['Scenario']==s for y in D)]
win=[(m,s) for m,s in xs if P(row('6.0-0047',m,s))>P(row('6.0-0023',m,s))]
C.append(mk('H5',"surpassing Dell’s PowerEdge XE7745 in six separate Llama scenarios",'Llama rows shared by entries 6.0-0047 and 6.0-0023 (Dell XE7745, 8 x RTX PRO 6000)','six Llama scenarios',
 f'{len(win)} of {len(xs)} shared Llama rows are higher for HPE: '+', '.join(f'{m} {s} {P(row("6.0-0047",m,s)):,.0f} against {P(row("6.0-0023",m,s)):,.0f}' for m,s in win),'CONSISTENT' if len(win)==6 else 'BELOW',''))
d4=[x for x in D if x['ID']=='6.0-0054' and x['Model'].startswith('llama')]; d2=[x for x in D if x['ID']=='6.0-0052']
four=[('llama3.1-8b','Offline'),('llama3.1-8b','Interactive'),('llama2-70b-99.9','Server'),('llama2-70b-99.9','Offline')]
f4=sum(1 for m,s in four if first(row('6.0-0054',m,s))); f2_=sum(1 for m,s in four if first(row('6.0-0052',m,s)))
C.append(mk('H6','the HPE ProLiant DL385 Gen11, equipped with four NVIDIA RTX PRO™ 6000 Blackwell Server Edition GPUs, secured four No. 1 spots in Llama benchmarks','the four benchmarks listed in footnote 6 (Llama 3.1-8B Offline and Interactive, Llama 2 70B 99.9 Server and Offline), for the four-GPU entry 6.0-0054 and for the two-GPU entry 6.0-0052 that the footnote cites','four No. 1 spots, four GPUs',
 f'First in group for the four-GPU entry 6.0-0054: {f4} of 4. First in group for the two-GPU entry 6.0-0052: {f2_} of 4. Two of the four rows are sole entrants in their group','CANNOT_TELL','The footnote cites 6.0-0052, which has two GPUs. The text says four GPUs. The result depends on which entry is meant.'))
pg=lambda x:P(x)/n(x)
q2=pg(row('6.0-0052','llama3.1-8b','Interactive'))/pg(as_); q4=pg(row('6.0-0054','llama3.1-8b','Interactive'))/pg(as_)
C.append(mk('H7','delivered 24% higher performance than the next-best submission','Llama 3.1-8B Interactive per GPU: entries 6.0-0052 and 6.0-0054 against 6.0-0004 (8 GPUs)','+24%',
 f'6.0-0052 (2 GPUs) {pg(row("6.0-0052","llama3.1-8b","Interactive")):,.0f} per GPU, {100*(q2-1):+.1f}% against 6.0-0004 at {pg(as_):,.0f}. 6.0-0054 (4 GPUs) {pg(row("6.0-0054","llama3.1-8b","Interactive")):,.0f} per GPU, {100*(q4-1):+.1f}%','CANNOT_TELL','The 24% reproduces for the two-GPU entry that the footnote cites and not for the four-GPU entry the text names. Per GPU, entry 6.0-0047 is higher than both.'))
x8=[x for x in D if x['ID']=='6.0-0048']
f5=[(m,s) for m,s in [('llama3.1-8b','Server'),('llama2-70b-99','Server'),('llama2-70b-99','Offline'),('llama2-70b-99.9','Server'),('llama2-70b-99.9','Offline')] if first(row('6.0-0048',m,s)) and len(cls(row('6.0-0048',m,s)))>1]
so=[(m,s) for m,s in [('llama2-70b-99','Interactive'),('llama2-70b-99.9','Interactive')] if len(cls(row('6.0-0048',m,s)))==1]
C.append(mk('H8','including five No. 1 results and two solo results, when compared to other systems featuring 8 NVIDIA Blackwell / B200 SXM GPUs','entry 6.0-0048 (XD685, 8 x B200 SXM) ranked among v6.0 rows with the same model, scenario, accelerator and count','five No. 1 and two solo',
 f'First among at least two entries: {len(f5)} of 5 listed rows. Only entry in its group: {len(so)} of 2 listed rows','CONSISTENT' if len(f5)==5 and len(so)==2 else 'BELOW',''))
sm=lambda m,s:row('6.0-0099',m,s)
wins=[(m,s) for m,s in [('llama2-70b-99','Server'),('llama2-70b-99','Offline'),('llama2-70b-99.9','Server'),('llama2-70b-99.9','Offline'),('whisper','Offline')] if P(row('6.0-0048',m,s))>P(sm(m,s))]
C.append(mk('H9','In five scenarios, the HPE ProLiant Compute XD685 surpassed Supermicro SYS-822GS-NBRT results','entry 6.0-0048 against entry 6.0-0099 (Supermicro SYS-822GS-NBRT)','five scenarios, Whisper Offline 46033.9 against 42389.7',
 f'{len(wins)} of 5 rows higher for HPE. Whisper Offline {P(row("6.0-0048","whisper","Offline")):,.1f} against {P(sm("whisper","Offline")):,.1f}','CONSISTENT' if len(wins)==5 else 'BELOW',''))
w=[x for x in D if x['Model']=='whisper' and x['Scenario']=='Offline' and n(x)]; me=row('6.0-0052','whisper','Offline')
lowr=[y for y in w if 'RTX PRO 6000' in y['Accelerator'] and y['Submitter']!='HPE' and pg(y)<pg(me)]
C.append(mk('H10','outperforming four competitive systems with an outstanding 4712 samples per second, yielding 2356 samples per second per GPU on a two-GPU configuration','entry 6.0-0052 Whisper Offline, per GPU, against other closed datacenter Whisper Offline entries with the same accelerator','4,712 total, 2,356 per GPU, ahead of four systems',
 f'{P(me):,.2f} total, {pg(me):,.1f} per GPU on {n(me)} GPUs. Non-HPE entries with the same accelerator and a lower per-GPU result: {len(lowr)}','CONSISTENT' if abs(P(me)-4712)<1 and abs(pg(me)-2356)<1 and len(lowr)>=4 else 'BELOW','The post does not say which four. The file shows more than four.'))
tb=[('6.0-0054','6.0-0014')]
H_=[('llama3.1-8b','Server'),('llama3.1-8b','Offline'),('llama2-70b-99','Server'),('llama2-70b-99','Offline'),('whisper','Offline')]
st=[(23227,23424),(23557,24014),(12822,13029),(13362,13530),(9228,9099)]
ok=all(round(P(row('6.0-0054',m,s)))==h and round(P(row('6.0-0014',m,s)))==c for (m,s),(h,c) in zip(H_,st))
C.append(mk('H11','Table 1. HPE ProLiant DL385 Gen11 vs. Cisco UCS X215c M8 results','entries 6.0-0054 (HPE DL385, 4 x RTX PRO 6000) and 6.0-0014 (Cisco UCS X215c M8, 4 x RTX PRO 6000), ten values','Table 1 values',
 '; '.join(f'{m} {s}: HPE {P(row("6.0-0054",m,s)):,.1f}, Cisco {P(row("6.0-0014",m,s)):,.1f}' for m,s in H_),'CONSISTENT' if ok else 'ABOVE','All ten values reproduce. Cisco is higher in the four Llama rows by 0.8% to 2.0%. HPE is higher in Whisper by 1.4%.'))
C.append(mk('H12','the power of the GPUs in the DL385 Gen11 was limited to a maximum of 450 watts, and the comparable Cisco UCS X215c M8 utilized GPUs operating at higher power (600 watts). The DL385 Gen11 produced almost identical inference results across key benchmarks, demonstrating superior performance-per-watt economics','power fields of entries 6.0-0054 and 6.0-0014','450 W against 600 W, superior performance per watt',
 'Neither entry has power results (has_power is false for both) and the summary file has no GPU power limit','CANNOT_TELL','Performance per watt needs a power measurement. The file has none for these two entries. MLCommons states that power figures such as a TDP are not measured or validated by MLCommons.'))
r45=sorted({(x['Submitter'],x['ID']) for x in A if '4500' in x['Accelerator']})
C.append(mk('H13','HPE was the only vendor in MLPerf® v6.0 to submit systems using the NVIDIA RTX PRO 4500 Blackwell Server Edition GPU','every v6.0 row whose accelerator is RTX PRO 4500','only vendor with RTX PRO 4500',
 'Entries with that accelerator: '+', '.join(f'{s} {i}' for s,i in r45),'CONSISTENT' if {s for s,i in r45}=={'HPE'} else 'BELOW','Footnote 15 cites 6.0-0043 (DL145) and 6.0-0050 (DL380 Gen12). Neither is a DL385.'))
n5=lambda x:int(x['a#'])
W5=[x for x in V5 if x['Category']=='closed' and 'datacenter' in x['Suite'] and x['Model']=='whisper' and x['Scenario']=='Offline']
m5=[x for x in W5 if x['ID']=='5.1-0052'][0]; c5=[y for y in W5 if y['Accelerator']==m5['Accelerator'] and n5(y)==n5(m5)]
rk=1+sum(1 for y in c5 if P(y)>P(m5)); top5=sorted(W5,key=lambda y:-P(y))[0]
C.append(mk('H14','In MLPerf® Inference v5.1, the DL385 Gen11 secured the No. 1 position in the Whisper speech-to-text benchmark','entry 5.1-0052, v5.1 closed datacenter Whisper Offline','No. 1 in Whisper, v5.1',
 f'{P(m5):,.1f} samples/s. Rank {rk} of {len(c5)} among entries with the same accelerator and count. Highest overall: {top5["Submitter"]} {P(top5):,.1f}','CONSISTENT' if rk==1 else 'BELOW','Rank across all entries is not first. The post gives no group.'))
json.dump(dict(source=['raw/inf_6.0.json','raw/inf_5.1.json'],sha256=[hashlib.sha256(R0).hexdigest(),hashlib.sha256(R5).hexdigest()],claims=C),open('claims_hpe_v60.json','w'),indent=1)
for c in C: print(c['id'],c['outcome'],'|',c['stated'],'|',c['delivered'][:240])
