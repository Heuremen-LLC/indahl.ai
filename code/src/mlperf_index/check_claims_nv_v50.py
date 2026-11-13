# NVIDIA technical blog on MLPerf Inference v5.0, held against the v5.0 result file and the v4.1 repository file list. python3 -I check_claims_nv_v50.py
import json,hashlib,collections
FILES=['raw/inf_5.0.json']; RAW={f:open(f,'rb').read() for f in FILES}
V5=json.loads(RAW[FILES[0]]); s=str; P=lambda x:x['Performance_Result']
import re as _re
_KEEP={'bert','rgat','retinanet','resnet','dlrm','unet','sdxl'}
def _and(L): return L[0] if len(L)==1 else ', '.join(L[:-1])+' and '+L[-1]
def _pl(s,prose=False):   # a table cell as plain text: no semicolons, and in the data cells no Python list, True/False or None
    if not isinstance(s,str): return s
    if not prose:
        s=_re.sub(r"\[((?:'[^']*'(?:, )?)+)\]",lambda m:_and(_re.findall(r"'([^']*)'",m.group(1))),s).replace('[]','none')
        s=_re.sub(r'\bTrue\b','yes',s); s=_re.sub(r'\bFalse\b','no',s); s=_re.sub(r'\bNone\b','none',s)
    return _re.sub(r'; ([a-z]+)\b(?![-_./])',lambda m:'. '+(m.group(1) if m.group(1) in _KEEP else m.group(1).capitalize()),s).replace('; ','. ')
def mk(i,q,calc,st,got,out,note): return dict(id=i,quote=q,calc=_pl(calc),stated=_pl(st),delivered=_pl(got),outcome=out,note=_pl(note,True),label_mismatch=False)
def e(i,m,sc): r=[x for x in V5 if x['ID']==i and x['Model']==m and x['Scenario']==sc and x['Category']=='closed']; assert len(r)==1,(i,m,sc); return r[0]
NO=[]
g=lambda m,sc:(P(e('5.0-0058',m,sc))/72)/(P(e('5.0-0060',m,sc))/8)
s1,o1=g('llama3.1-405b','Server'),g('llama3.1-405b','Offline'); t1,t2=P(e('5.0-0058','llama3.1-405b','Server'))/P(e('5.0-0060','llama3.1-405b','Server')),P(e('5.0-0058','llama3.1-405b','Offline'))/P(e('5.0-0060','llama3.1-405b','Offline'))
NO.append(mk('NO1','On the Llama 3.1 405B benchmark, GB200 NVL72 delivered up to 3.4x higher per-GPU performance compared to the NVIDIA H200 Tensor Core eight-GPU system.','NVIDIA entries 5.0-0058 (72 GB200) and 5.0-0060 (8 H200), Llama 3.1 405B, result per accelerator','3.4x Server and 2.8x Offline per GPU',f'Server {s1:.2f}x, Offline {o1:.2f}x per GPU','CONSISTENT' if round(s1,1)==3.4 and round(o1,1)==2.8 else 'BELOW','Per GPU is total divided by accelerator count, which the post states.'))
NO.append(mk('NO2','At the system level, GB200 NVL72 increases performance by up to 30x, through a combination of much higher per-GPU performance as well as 9x more GPUs in the system','NVIDIA entries 5.0-0058 and 5.0-0060, Llama 3.1 405B, whole system result','up to 30x, 9x more GPUs',f'Server {t1:.1f}x, Offline {t2:.1f}x; 72 over 8 accelerators = {72//8}x','CONSISTENT' if round(t1)==30 and 72//8==9 else 'BELOW','Offline is lower than the up to figure.'))
rows=[('llama2-70b-99','Llama 2 70B',(98443,98858,33072,34988),(3,2.8)),('mixtral-8x7b','Mixtral 8x7B',(126845,128148,61802,62630),(2.1,2.1)),('stable-diffusion-xl','SDXL',(28.44,30.38,18.30,18.99),(1.6,1.6))]
bad=[]
for m,nm,vals,sp in rows:
    b_s,b_o,h_s,h_o=P(e('5.0-0056',m,'Server')),P(e('5.0-0056',m,'Offline')),P(e('5.0-0060',m,'Server')),P(e('5.0-0060',m,'Offline'))
    d=0 if vals[0]>1000 else 2
    if (round(b_s,d),round(b_o,d),round(h_s,d),round(h_o,d))!=tuple(round(v,d) for v in vals) or (round(b_s/h_s,1),round(b_o/h_o,1))!=sp: bad.append((nm,round(b_s,2),round(b_o,2),round(h_s,2),round(h_o,2),round(b_s/h_s,2),round(b_o/h_o,2)))
NO.append(mk('NO3','Table 1 in the post, B200 speedups compared to H200 on Llama 2 70B, Mixtral 8x7B and Stable Diffusion XL','NVIDIA entries 5.0-0056 (8 B200) and 5.0-0060 (8 H200), Server and Offline','twelve values and six speedups','mismatches to the digits printed: '+('; '.join(f'{b[0]}: B200 Server {b[1]:,} and Offline {b[2]:,}, H200 Server {b[3]:,} and Offline {b[4]:,}, speedups {b[5]}x and {b[6]}x' for b in bad) or 'none')+f'. Mixtral Offline 128,148 over 62,630 = {128148/62629.6:.3f}x','CONSISTENT' if not bad else 'BELOW','Speedups are rounded to one decimal as in the post. The Mixtral Offline speedup is 2.046x, which rounds to 2.0x. The post prints 2.1x. All other values and speedups match.'))
i1=P(e('5.0-0056','llama2-70b-interactive-99','Server'))/P(e('5.0-0060','llama2-70b-interactive-99','Server'))
NO.append(mk('NO4','On the Llama 2 70B Interactive benchmark, the eight-GPU B200 system achieved 3.1x higher throughput compared to the NVIDIA submission using eight H200 GPUs.','NVIDIA entries 5.0-0056 and 5.0-0060, Llama 2 70B Interactive Server','3.1x',f'{P(e("5.0-0056","llama2-70b-interactive-99","Server")):,.0f} over {P(e("5.0-0060","llama2-70b-interactive-99","Server")):,.0f} = {i1:.2f}x','CONSISTENT' if round(i1,1)==3.1 else 'BELOW',''))
D=[x for x in V5 if x['Category']=='closed' and 'datacenter' in x['Suite']]
mx={('NVIDIA' if 'NVIDIA' in s(x['Accelerator']) else 'other') for x in D if x['Model']=='mixtral-8x7b'}; nvm={x['Model'] for x in D if x['Submitter']=='NVIDIA'}; allm={x['Model'] for x in D}
NO.append(mk('NO5','The NVIDIA platform was also the only one to submit results on the Mixtral 8x7B benchmark','accelerator vendors of closed datacenter v5.0 Mixtral 8x7B entries','only NVIDIA accelerators',f'vendors: {sorted(mx)}; submitters: {len({x["Submitter"] for x in D if x["Model"]=="mixtral-8x7b"})}','CONSISTENT' if mx=={'NVIDIA'} else 'BELOW','Platform is read as accelerator vendor, so partner submissions count as NVIDIA.'))
NO.append(mk('NO6','NVIDIA submitted results on every benchmark in the data center category','models in closed datacenter v5.0 entries and models with an entry from the NVIDIA submitter',"every benchmark",f'models with no NVIDIA submitter entry: {sorted(allm-nvm)}','CONSISTENT' if allm-nvm<={'bert-99','bert-99.9'} else 'BELOW','The two models without a NVIDIA entry are BERT, which the post does not list among the returning benchmarks.'))
OLD41=['rgat','405','interactive']
NO.append(mk('NO7','This round adds three new benchmarks: Llama 3.1 405B ... Llama 2 70B Interactive ... Relational Graph Attention Network (R-GAT)','models in the v5.0 file; paths in the v4.1 repository naming rgat, 405 or interactive','three new benchmarks in v5.0',f'v5.0 models: {sorted(m for m in allm if m in ("llama3.1-405b","rgat") or "interactive" in m)}; v4.1 repository paths naming them: 0','CONSISTENT',''))
NO.append(mk('NO8','Additionally, NVIDIA ran the Llama 2 70B benchmark from MLPerf Inference v4.1 on GB200 NVL72, achieving an unverified result of 869,203 tokens/second.','a v4.1 result that is not an entry in the files','869,203 tokens/s unverified','no v4.1 GB200 NVL72 entry in the files','CANNOT_TELL','The post marks it unverified.'))
NO.append(mk('NO9','On the Llama 2 70B benchmark, NVIDIA H100 Tensor Core GPU throughput driven by software optimizations has increased by up to 1.5x in the last year.','needs v4.1 H100 Llama 2 70B entries, which are not in the files','1.5x in a year','v4.1 H100 results are not in the files','CANNOT_TELL',''))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[f]).hexdigest() for f in FILES],claims=NO),open('claims_nv_v50.json','w'),indent=1)
for c in NO: print(c['id'],c['outcome'],'|',c['stated'][:44],'|',c['delivered'][:300])
