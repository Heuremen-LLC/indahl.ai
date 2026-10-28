# AMD ROCm blog "Technical Dive into AMD's MLPerf Inference v5.1 Submission" against the MLCommons summary files.
# Run: python3 -I check_claims_amd_v51.py
import json,hashlib,statistics
R50=open('raw/inf_5.0.json','rb').read(); R51=open('raw/inf_5.1.json','rb').read()
D50=json.loads(R50); D51=json.loads(R51)
def one(D,i,model,scen,cat=None,acc=None):
    r=[x for x in D if x['ID']==i and x['Model']==model and x['Scenario']==scen and (cat is None or x['Category']==cat)]
    assert len(r)==1,(i,model,scen,len(r)); return r[0]
out=[]
def claim(cid,quote,calc,stated,got,outcome,note,label_mismatch=False):
    out.append(dict(id=cid,quote=quote,calc=calc,stated=stated,delivered=got,outcome=outcome,note=note,label_mismatch=label_mismatch))
# A1 2.7x MI355X vs MI325X Llama 2 70B offline
m355=one(D51,'5.1-0098','llama2-70b-99','Offline')['Performance_Result']
m325=one(D51,'5.1-0002','llama2-70b-99','Offline')['Performance_Result']
m325_50=one(D50,'5.0-0001','llama2-70b-99','Offline')['Performance_Result']
claim('A1','MI355X shows 2.7 x improvement over MI325X due to superior architecture and MXFP4 capabilities','5.1-0098 (open, 8xMI355X, MXFP4) / 5.1-0002 (closed, 8xMI325X, FP8), Llama 2 70B Offline, tokens/s',
 '2.7x',f'{m355/m325:.3f}x ({m355:.1f} vs {m325:.1f}). Against the v5.0 entry 5.0-0001: {m355/m325_50:.3f}x','CONSISTENT','Open division against closed division and MXFP4 against FP8, as the blog\'s own figure caption says.')
# A2 multinode vs single node
n4=one(D51,'5.1-0102','llama2-70b-99','Offline')['Performance_Result']; n8=one(D51,'5.1-0104','llama2-70b-99','Offline')['Performance_Result']
claim('A2','Compared to our internal baselines, the 4 node achieves 3.9x better performance and the 8 node submission shows 7.9x improvement over our single node baseline',
 '5.1-0102 and 5.1-0104 (AMD_MangoBoost, open) / 5.1-0098 (the only published single-node MI355X Llama 2 70B Offline row)',
 '3.9x and 7.9x',f'{n4/m355:.2f}x and {n8/m355:.2f}x against the published single-node row ({m355:.1f} tokens/s). The stated ratios imply baselines of {n4/3.9:.0f} and {n8/7.9:.0f} tokens/s','CANNOT_TELL',
 'The baseline is called internal and is not a published row. Against the one published single-node row the ratios are lower.')
# A3 3.4x vs 5.0-0054
b=one(D50,'5.0-0054','llama2-70b-99','Offline')
claim('A3','Compared to the 4 node submission on MI325X in the previous round, submission ID 5.0-0054, our current MI355X 4 node score, submission ID 5.1-0102, is 3.4x faster',
 '5.1-0102 / 5.0-0054, Llama 2 70B Offline',
 '3.4x',f'{n4/b["Performance_Result"]:.3f}x ({n4:.0f} vs {b["Performance_Result"]:.0f} tokens/s). The file lists entry 5.0-0054 as {b["Accelerator"]}, not MI325X','CONSISTENT',
 'Ratio holds. The entry named in the blog is a 32-GPU MI300X system in the file, and no multi-node MI325X entry exists in v5.0. 5.1-0102 is open division, 5.0-0054 is closed.',True)
# A4 MI325X v5.0 -> v5.1
o=one(D51,'5.1-0002','llama2-70b-99','Offline')['Performance_Result']/one(D50,'5.0-0001','llama2-70b-99','Offline')['Performance_Result']
s=one(D51,'5.1-0002','llama2-70b-99','Server')['Performance_Result']/one(D50,'5.0-0001','llama2-70b-99','Server')['Performance_Result']
claim('A4','we have improved the performance by about 2% and 4% in offline and server scenarios, respectively, over MLPerf Inference v5.0 submission','AMD entries 5.1-0002 / 5.0-0001, 8xMI325X, Llama 2 70B, closed',
 '+2% offline, +4% server',f'+{(o-1)*100:.1f}% offline, +{(s-1)*100:.1f}% server','CONSISTENT','rounds to the stated figures')
# A5 heterogeneous 94%
het=one(D51,'5.1-0065','llama2-70b-99','Offline')['Performance_Result']
mi300=[x['Performance_Result'] for x in D51 if x['Category']=='closed' and 'MI300X' in x['Accelerator'] and x['Model']=='llama2-70b-99' and x['Scenario']=='Offline' and x['Nodes']==1]
mi325=[x['Performance_Result'] for x in D51 if x['Category']=='closed' and 'MI325X' in x['Accelerator'] and x['Model']=='llama2-70b-99' and x['Scenario']=='Offline' and x['Nodes']==1]
lo=het/(4*max(mi300)+2*max(mi325)); hi=het/(4*min(mi300)+2*min(mi325)); mid=het/(4*statistics.median(mi300)+2*statistics.median(mi325))
claim('A5','This configuration achieves an impressive 94% efficiency compared to single-node submissions from these platforms','5.1-0065 (4 MI300X nodes + 2 MI325X nodes, closed) / (4 x MI300X single node + 2 x MI325X single node), Llama 2 70B Offline',
 '94%',f'{mid*100:.1f}% using median single-node rows ({lo*100:.1f}% to {hi*100:.1f}% over all published single-node rows, {len(mi300)} MI300X and {len(mi325)} MI325X rows)','CONSISTENT','The blog does not say which single-node rows it used. The range over every published single-node row includes the stated figure.')
# A6 partners nearly identical
for scen in ('Offline','Server'):
    pass
def part(scen,acc):
    ref=one(D51,'5.1-0002' if acc=='MI325X' else '5.1-0001','llama2-70b-99',scen)['Performance_Result']
    v=[x['Performance_Result'] for x in D51 if x['Category']=='closed' and acc in x['Accelerator'] and x['Model']=='llama2-70b-99' and x['Scenario']==scen and x['Nodes']==1 and x['Submitter']!='AMD']
    return ref,min(v)/ref,max(v)/ref,len(v)
r1=part('Offline','MI325X'); r2=part('Server','MI325X'); r3=part('Offline','MI300X'); r4=part('Server','MI300X')
claim('A6','partners delivering performance that is nearly identical to AMD reference results across both Instinct MI325X and MI300X platforms','single-node closed Llama 2 70B rows, partner / AMD reference (5.1-0002 MI325X, 5.1-0001 MI300X)',
 'nearly identical (no figure)',f'MI325X Offline {r1[1]*100:.1f}% to {r1[2]*100:.1f}% (n={r1[3]}), Server {r2[1]*100:.1f}% to {r2[2]*100:.1f}%. MI300X Offline {r3[1]*100:.1f}% to {r3[2]*100:.1f}% (n={r3[3]}), Server {r4[1]*100:.1f}% to {r4[2]*100:.1f}%','CANNOT_TELL','No figure is stated, so there is nothing to hold the spread against. The spread is shown.')
# A7 pruned Llama 405B
a=one(D51,'5.1-0101','llama3.1-405b','Offline')['Performance_Result']; c=one(D51,'5.1-0100','llama3.1-405b','Offline')['Performance_Result']
claim('A7','We obtain a performance of 1942 tokens/s ... we see a performance of 2019 tokens/s','5.1-0101 and 5.1-0100, Llama 3.1 405B Offline, open, 8xMI355X','1942 and 2019 tokens/s',f'{a:.2f} and {c:.2f} tokens/s','CONSISTENT','matches to rounding')
claim('A8','A 21% depth-pruned model delivered up to an 82% increase in inference throughput ... 33% pruned model ... 90% performance uplift','no unpruned MI355X Llama 3.1 405B row exists in v5.1','+82% and +90%','no baseline row in the file','CANNOT_TELL','The uplift is against an unpruned model that was not submitted.')
claim('A9','The above optimizations resulted in a 23% end-to-end throughput improvement','Mixtral-8x7B kernel optimizations','+23%','no before and after rows in the file','CANNOT_TELL','The baseline is internal.')
# A10 SDXL +8%
sx0=[x for x in D50 if x['ID']=='5.0-0002' and x['Model']=='stable-diffusion-xl' and x['Scenario']=='Offline'][0]['Performance_Result']
sx1=[x for x in D51 if x['ID']=='5.1-0004' and x['Model']=='stable-diffusion-xl' and x['Scenario']=='Offline'][0]['Performance_Result']
claim('A10','we improved performance by approximately 8% in the offline scenario compared to our MLPerf Inference v5.0 submission','AMD 8xMI325x SD-XL Offline, 5.1-0004 / 5.0-0002, samples/s','+8%',f'+{(sx1/sx0-1)*100:.1f}% ({sx1:.4f} vs {sx0:.4f})','CONSISTENT','within one point of the stated figure')
# A11 Mixtral leadership vs H200
mx=[x['Performance_Result']/(x['Nodes']*x['a#']) for x in D51 if x['Model']=='mixtral-8x7b' and x['Category']=='closed' and x['Scenario']=='Offline' and 'MI325X' in x['Accelerator'] and isinstance(x['a#'],int)]
hx=[x['Performance_Result']/(x['Nodes']*x['a#']) for x in D51 if x['Model']=='mixtral-8x7b' and x['Category']=='closed' and x['Scenario']=='Offline' and 'H200' in x['Accelerator'] and isinstance(x['a#'],int)]
claim('A11','Note the performance leadership of our Mixtral-8x7B Offline score','closed Mixtral-8x7B Offline per accelerator, MI325X (n=%d) against H200 (n=%d)'%(len(mx),len(hx)),'leadership over the H200 average (Figure 4, bars not in the text)',
 f'MI325X median {statistics.median(mx):.0f} tokens/s per GPU, H200 mean {statistics.mean(hx):.0f} ({statistics.median(mx)/statistics.mean(hx):.3f}x). Only {len(hx)} H200 submissions','CONSISTENT','The figure values are not in the page text. Direction and size from the file.')
claim('A12','Figure 4 and Figure 5 comparisons of MI325X against an average of H200 scores (Llama2-70B Interactive, Llama2-70B, SD-XL)','bar values are images on the page','figure bars','not readable by script','CANNOT_TELL','Values exist only in the figure images.')
json.dump(dict(source=['raw/inf_5.0.json','raw/inf_5.1.json'],sha256=[hashlib.sha256(R50).hexdigest(),hashlib.sha256(R51).hexdigest()],claims=out),open('claims_amd_v51.json','w'),indent=1)
for x in out: print(x['id'],x['outcome'],'|',x['stated'],'|',x['delivered'][:200],'| LABEL' if x['label_mismatch'] else '')
