# Stated vs delivered: NVIDIA MLPerf Inference v5.1 blog claims against the MLCommons summary file.
# Run: python3 -I check_claims.py
import json,hashlib,statistics,re
RAW='raw/inf_5.1.json'
raw=open(RAW,'rb').read()
D=json.loads(raw)
tot=lambda x:x['Nodes']*x['a#']
def rows(**k):
    return [x for x in D if all(x[a]==b for a,b in k.items())]
def pg(i,model,scen,cat='closed'):
    r=[x for x in D if x['ID']==i and x['Model']==model and x['Scenario']==scen and x['Category']==cat]
    assert len(r)==1,(i,model,scen,len(r))
    r=r[0]; assert r['Performance_Units'].startswith('Tokens')
    return r['Performance_Result']/tot(r),r
out=[]
def claim(cid,quote,calc,stated,got,outcome,note):
    out.append(dict(id=cid,quote=quote,calc=calc,stated=stated,delivered=got,outcome=outcome,note=note))
# C1,C2 GB300 vs GB200 DeepSeek-R1
g300o,_=pg('5.1-0072','deepseek-r1','Offline'); g200o,_=pg('5.1-0071','deepseek-r1','Offline')
g300s,_=pg('5.1-0072','deepseek-r1','Server');  g200s,_=pg('5.1-0071','deepseek-r1','Server')
claim('C1','GB300 NVL72 delivered 45% higher performance per GPU on the new DeepSeek-R1 benchmark in the offline scenario','entries 5.1-0072 / 5.1-0071, tokens/s divided by 72',
 '+45%',f'+{(g300o/g200o-1)*100:.1f}% ({g300o:.1f} vs {g200o:.1f} tokens/s/GPU)','CONSISTENT','rounds to the stated figure')
claim('C2','and 25% in the server scenario','entries 5.1-0072 / 5.1-0071, tokens/s divided by 72',
 '+25%',f'+{(g300s/g200s-1)*100:.1f}% ({g300s:.1f} vs {g200s:.1f} tokens/s/GPU)','CONSISTENT','rounds to the stated figure')
# C3 Table 2 GB200/GB300 cells
t2={'GB200 offline':(4024,g200o),'GB200 server':(2327,g200s),'GB300 offline':(5842,g300o),'GB300 server':(2907,g300s)}
bad=[k for k,(s,v) in t2.items() if round(v)!=s]
claim('C3','Table 2: GB200 NVL72 4,024 / 2,327 and GB300 NVL72 5,842 / 2,907 tokens/sec/GPU (offline / server)','four cells recomputed from the summary file',
 '4024, 2327, 5842, 2907',', '.join(f'{v:.2f}' for _,v in t2.values()),'CONSISTENT' if not bad else 'BELOW',f'mismatched cells: {bad}' if bad else 'all four cells match after rounding')
# C4 vs Hopper
hop_o,hop_s=1253,556
pub=[x for x in D if x['Model'].startswith('deepseek') and 'H200' in x['Accelerator']]
assert len(pub)==1; p=pub[0]; pub_pg=p['Performance_Result']/tot(p)
claim('C4','compared to unverified results collected on a Hopper-based system, Blackwell Ultra delivered about 5x higher throughput per GPU','Table 2 Hopper cells (1,253 / 556) vs GB300, and vs the only H200 DeepSeek-R1 row in the file',
 'about 5x',f'{g300o/hop_o:.2f}x offline and {g300s/hop_s:.2f}x server against NVIDIA\'s Hopper cells. {g300o/pub_pg:.2f}x offline against the one published H200 row ({p["ID"]}, {p["Submitter"]}, {p["Category"]}, {pub_pg:.1f} tokens/s/GPU)',
 'CANNOT_TELL','NVIDIA states the Hopper cells are not verified by MLCommons and no closed-division H200 DeepSeek-R1 row exists in the file. Against the published open-division row the ratio is about 5x.')
# C5 / C6 Llama 405B interactive
i71,r71=pg('5.1-0071','llama3.1-405b','Interactive'); i69,r69=pg('5.1-0069','llama3.1-405b','Interactive'); i75,r75=pg('5.1-0075','llama3.1-405b','Interactive')
s71,_=pg('5.1-0071','llama3.1-405b','Server'); s69,_=pg('5.1-0069','llama3.1-405b','Server')
o71,_=pg('5.1-0071','llama3.1-405b','Offline'); o69,_=pg('5.1-0069','llama3.1-405b','Offline')
claim('C5','nearly 1.5x increase in throughput per GPU compared to traditional aggregated serving using in-flight batching on a DGX B200 system','entries 5.1-0071 (72 GPUs) / 5.1-0069 (8 GPUs), Llama 3.1 405B Interactive',
 'nearly 1.5x',f'{i71/i69:.3f}x ({i71:.2f} vs {i69:.2f} tokens/s/GPU). Same two systems, Server: {s71/s69:.3f}x, Offline: {o71/o69:.3f}x',
 'CANNOT_TELL','The ratio holds. The two entries differ in system size and rack, so the file cannot separate disaggregated serving from the 72-GPU system. Whether entry 5.1-0071 used disaggregated serving is not stated in the summary file or the entry README.')
claim('C6','a greater than 5x cumulative improvement compared to in-flight batching results collected on a DGX H200 system','entries 5.1-0071 / 5.1-0075 (8xH200, Nebius, closed), Llama 3.1 405B Interactive',
 'greater than 5x',f'{i71/i75:.2f}x ({i71:.2f} vs {i75:.2f} tokens/s/GPU)','CONSISTENT',f'Hopper row is a verified closed row. Precision differs: weights {r71["weight_data_types"]} against {r75["weight_data_types"]}. The blog names the Hopper system DGX H200 and the file lists the entry as an 8xH200 HGX submission by {r75["Submitter"]}.')
# C7 Table 1 per-GPU records (Llama 3.1 405B)
for scen,stated in (('Offline',224),('Server',170),('Interactive',138)):
    best=None
    for x in D:
        if x['Category']=='closed' and x['Model']=='llama3.1-405b' and x['Scenario']==scen and 'NVIDIA' in x['Accelerator']:
            v=x['Performance_Result']/tot(x)
            if best is None or v>best[0]: best=(v,x)
    v,x=best
    claim('C7'+scen[0],f'Table 1: Llama 3.1 405B {scen} {stated} tokens/sec/GPU, a per-GPU record',f'maximum over all closed NVIDIA-accelerator rows for Llama 3.1 405B {scen} in v5.1',
     str(stated),f'{v:.2f} ({x["ID"]}, {x["Submitter"]}, {x["Accelerator"]})','CONSISTENT' if round(v)==stated else 'ABOVE' if v>stated else 'BELOW','the stated figure is the highest per-GPU value in the closed v5.1 rows')
json.dump(dict(source=RAW,sha256=hashlib.sha256(raw).hexdigest(),rows=len(D),claims=out),open('claims_nvidia_v51.json','w'),indent=1)
for c in out: print(c['id'],c['outcome'],'|',c['stated'],'|',c['delivered'])
print('sha256',hashlib.sha256(raw).hexdigest()[:16])
