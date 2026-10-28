# Intel newsroom posts on MLPerf Inference v5.1 and v6.0 against the MLCommons summary files. Run: python3 -I check_claims_intel.py
import json,hashlib,re,collections
R={v:open(f'raw/inf_{v}.json','rb').read() for v in ('5.1','6.0')}; D={v:json.loads(r) for v,r in R.items()}
def row(v,i,mod,sc):
    r=[x for x in D[v] if x['ID']==i and x['Model']==mod and x['Scenario']==sc and x['Category']=='closed']; assert len(r)==1,(v,i,mod,sc,len(r)); return r[0]
def mk(cid,quote,calc,stated,got,outcome,note): return dict(id=cid,quote=quote,calc=calc,stated=stated,delivered=got,outcome=outcome,note=note,label_mismatch=False)
# ---- v5.1
i56o,i56s=row('5.1','5.1-0056','llama3.1-8b','Offline'),row('5.1','5.1-0056','llama3.1-8b','Server')
rtx=[(x['Scenario'],x['Performance_Result'],x['a#']) for x in D['5.1'] if x['ID']=='5.1-0051' and x['Model']=='llama3.1-8b' and x['Scenario'] in('Offline','Server')]
l40=[(x['Scenario'],x['Performance_Result'],x['a#']) for x in D['5.1'] if x['ID']=='5.1-0082' and x['Model']=='llama3.1-8b' and x['Scenario'] in('Offline','Server')]
v51=[mk('N1','performance per dollar advantages of up to 1.25x and up to 4x compared to NVIDIA RTX Pro 6000 and L40S respectively','Llama 3.1 8B, closed: Intel entry 5.1-0056 against the only RTX PRO 6000 entry (5.1-0051) and the only L40S entry (5.1-0082) in the file','up to 1.25x and up to 4x performance per dollar',
 f'Throughput only, no prices in the file. Intel {i56o["Performance_Result"]:,.2f} offline and {i56s["Performance_Result"]:,.2f} server tokens/s with 4 cards. RTX PRO 6000 entry {rtx[0][1]:,.1f} and {rtx[1][1]:,.1f} with {rtx[0][2]} cards. L40S entry {l40[0][1]:,.2f} and {l40[1][1]:,.2f} with {l40[0][2]} card','CANNOT_TELL',
 'The post says the cost figures are Intel internal estimates from public and partner sourcing for one named configuration as of September 2025. The prices are not in the MLCommons file, so the file cannot settle a performance per dollar ratio.'),
 mk('N2','Intel Xeon 6 with P-cores achieved 1.9x performance improvement gen-over-gen in MLPerf Inference v5.1','Xeon 6 entries in v5.1 against the previous Xeon generation','1.9x generation over generation','the previous generation is not in the v5.0, v5.1 or v6.0 files','CANNOT_TELL','The earlier-generation Xeon results are in older rounds that these files do not cover.')]
# ---- v6.0
mods=[('gpt-oss-120b','Offline'),('gpt-oss-120b','Server'),('llama2-70b-99','Offline'),('llama2-70b-99','Server'),('llama3.1-8b','Offline'),('llama3.1-8b','Server')]
ratios=[]
for m,s in mods:
    b70=row('6.0','6.0-0101',m,s)['Performance_Result']; b60=row('6.0','6.0-0059',m,s)['Performance_Result']; ratios.append((b70/b60,m,s,b70,b60))
w70=row('6.0','6.0-0101','whisper','Offline')['Performance_Result']; w60=row('6.0','6.0-0059','whisper','Offline')['Performance_Result']; ratios.append((w70/w60,'whisper','Offline',w70,w60))
mx=max(ratios); off=max(r for r in ratios if r[2]=='Offline')
v60=[mk('N3','the Arc Pro B70 providing up to 1.8x higher inference performance than the Arc Pro B60','entries 6.0-0101 (4 x Arc Pro B70) over 6.0-0059 (4 x Arc Pro B60), same host CPU, every closed model and scenario they both ran','up to 1.8x',
 'ratios '+', '.join(f'{r[1]} {r[2].lower()} {r[0]:.2f}x' for r in ratios)+f'. Largest offline ratio {off[0]:.2f}x ({off[1]}). Largest of all {mx[0]:.2f}x ({mx[1]} {mx[2].lower()})','ABOVE','The statement says up to. The largest offline ratio matches it and the largest server ratio is higher. The post names the B60 comparison system as 2 Dual GPU cards, 4 B60 equivalent.')]
pairs=[('llama2-70b-99','Offline'),('llama2-70b-99','Server'),('llama3.1-8b','Offline'),('llama3.1-8b','Server')]
r2=[(row('6.0','6.0-0060',m,s)['Performance_Result']/row('5.1','5.1-0056',m,s)['Performance_Result'],m,s) for m,s in pairs]
v60.append(mk('N4','up to 1.18x higher gains on the same Intel Arc Pro B60 hardware versus MLPerf v5.1','entries 6.0-0060 over 5.1-0056, 4 x Arc Pro B60 Dual GPU cards each, every model and scenario both ran','up to 1.18x','ratios '+', '.join(f'{m} {s.lower()} {r:.3f}x' for r,m,s in r2)+f'. Largest {max(r2)[0]:.3f}x','CONSISTENT','The host CPU differs, a Xeon w9-3475X in v5.1 and a Xeon 698X in v6.0.'))
v60.append(mk('N5','powering up to 1.6x as much KV cache capacity when running larger models','a memory capacity comparison with competing GPUs','up to 1.6x KV cache capacity','not an MLPerf measurement','CANNOT_TELL','The MLCommons files hold throughput results, not cache capacity.'))
ids=collections.defaultdict(list)
for x in D['6.0']: ids[x['ID']].append(x)
xe=sum(1 for r in ids.values() if any('xeon' in x['Processor'].lower() for x in r)); xr=sum(1 for x in D['6.0'] if 'xeon' in x['Processor'].lower())
cl=[i for i,r in ids.items() if any(x['Category']=='closed' and 'datacenter' in x['Suite'] for x in r)]; xc=sum(1 for i in cl if any('xeon' in x['Processor'].lower() for x in ids[i] if x['Category']=='closed' and 'datacenter' in x['Suite']))
v60.append(mk('N6','with over half of MLPerf 6.0 submissions powered by Xeon','the Processor column of the v6.0 file, entries and rows with Xeon in the processor name','over half',f'{xe} of {len(ids)} entries ({xe/len(ids)*100:.1f}%), {xr} of {len(D["6.0"])} rows ({xr/len(D["6.0"])*100:.1f}%), {xc} of {len(cl)} closed datacenter entries ({xc/len(cl)*100:.1f}%)','BELOW','Every count of the processor field in the file is under half. If powered by means something other than the processor field, the file cannot show it.'))
v60.append(mk('N7','Intel Xeon 6 processors with P-cores delivered up to a 1.9x generational performance gain in MLPerf Inference v5.1','Xeon 6 entries against the previous Xeon generation','up to 1.9x generational gain','the previous generation is not in the v5.0, v5.1 or v6.0 files','CANNOT_TELL','Same statement as the v5.1 post.'))
for f,c in (('claims_intel_v51.json',v51),('claims_intel_v60.json',v60)):
    json.dump(dict(source=[f'raw/inf_{v}.json' for v in R],sha256=[hashlib.sha256(R[v]).hexdigest() for v in R],claims=c),open(f,'w'),indent=1)
    for x in c: print(x['id'],x['outcome'],'|',x['stated'],'|',x['delivered'][:260])
