# Supermicro press release on MLPerf Inference v5.0 with NVIDIA HGX B200, held against the v5.0 result file. python3 -I check_claims_supermicro_v50.py
import json,hashlib,re
FILES=['raw/inf_5.0.json']; RAW={f:open(f,'rb').read() for f in FILES}
V=json.loads(RAW[FILES[0]]); s=str; P=lambda x:x['Performance_Result']
import re as _re
_KEEP={'bert','rgat','retinanet','resnet','dlrm','unet','sdxl'}
def _and(L): return L[0] if len(L)==1 else ', '.join(L[:-1])+' and '+L[-1]
def _pl(s,prose=False):   # a table cell as plain text: no semicolons, and in the data cells no Python list, True/False or None
    if not isinstance(s,str): return s
    if not prose:
        s=_re.sub(r"\[((?:'[^']*'(?:, )?)+)\]",lambda m:_and(_re.findall(r"'([^']*)'",m.group(1))),s).replace('[]','none')
        s=_re.sub(r'\bTrue\b','yes',s); s=_re.sub(r'\bFalse\b','no',s); s=_re.sub(r'\bNone\b','none',s)
    return _re.sub(r'; ([a-z]+)\b(?![-_./])',lambda m:'. '+(m.group(1) if m.group(1) in _KEEP else m.group(1).capitalize()),s).replace('; ','. ')
def n(x):
    m=re.findall(r'\(x(\d+)\)',s(x.get('Accelerator'))); return sum(map(int,m)) if m else int(x.get('a#') or 0)*int(x.get('Nodes') or 1)
def mk(i,q,calc,st,got,out,note): return dict(id=i,quote=q,calc=_pl(calc),stated=_pl(st),delivered=_pl(got),outcome=out,note=_pl(note,True),label_mismatch=False)
D=[x for x in V if x['Category']=='closed' and 'datacenter' in x['Suite']]
def sm(i,m,sc): r=[x for x in D if x['ID']==i and x['Model']==m and x['Scenario']==sc]; assert len(r)==1,(i,m,sc); return P(r[0])
def top8(m,sc,f): return sorted([(P(x),x['Submitter'],x['ID']) for x in D if x['Model']==m and x['Scenario']==sc and n(x)==8 and f(x)],reverse=True)
b200=lambda x:'B200' in s(x['Accelerator']) and 'GB' not in s(x['Accelerator'])[:6]; h200=lambda x:'H200-SXM' in s(x['Accelerator'])
AIR,LCC='5.0-0074','5.0-0072'
SP=[]
ratios=[]
for m,sc in(('llama2-70b-99','Offline'),('llama2-70b-99','Server'),('llama3.1-405b','Offline'),('llama3.1-405b','Server')):
    best=max(max(sm(AIR,m,sc),sm(LCC,m,sc))for _ in(0,)); h=top8(m,sc,h200)[0][0]; ratios.append((m,sc,best,h,best/h))
SP.append(mk('SP1','Supermicro demonstrated more than 3 times the tokens per second (Token/s) generation for Llama2-70B and Llama3.1-405B benchmarks compared to H200 8-GPU systems.','best Supermicro B200 entry against the best eight H200 SXM entry in the v5.0 file, four model and scenario rows','more than 3 times for Llama 2 70B and Llama 3.1 405B',', '.join(f'{m} {sc} {b:,.1f} over {h:,.1f} = {r:.2f}x' for m,sc,b,h,r in ratios),'CONSISTENT' if all(r>3 for *_,r in ratios) else 'BELOW','Llama 2 70B is read as llama2-70b-99. Server for the 405B model is above 3x. The other three rows are 2.7x to 3.0x.'))
ok=(round(sm(AIR,'stable-diffusion-xl','Server'),2),round(sm(AIR,'llama2-70b-interactive-99','Server'),2),round(sm(AIR,'llama3.1-405b','Server'),2),round(sm(LCC,'mixtral-8x7b','Server')),round(sm(LCC,'mixtral-8x7b','Offline')))==(28.92,62265.70,1080.31,129047,128795)
firsts=[top8('stable-diffusion-xl','Server',b200)[0][2],top8('llama2-70b-interactive-99','Server',b200)[0][2],top8('llama3.1-405b','Server',b200)[0][2],top8('mixtral-8x7b','Server',b200)[0][2],top8('mixtral-8x7b','Offline',b200)[0][2]]
SP.append(mk('SP2','Stable Diffusion XL (Server) SYS-A21GE-NBRT (8x B200-SXM-180GB) #1 queries/s, 28.92 ... llama2-70b-interactive-99 (Server) SYS-A21GE-NBRT (8x B200-SXM-180GB) #1 Tokens/s, 62,265.70 ... Llama3.1-405b (Server) SYS-A21GE-NBRT (8x B200-SXNM-180GB) #1 Tokens/s, 1080.31 (for an 8-GPU node) ... mixtral-8x7b (Server) SYS-421GE-NBRT-LCC (8x B200-SXM-180GB) #1 Tokens/s, 129,047.00 ... mixtral-8x7b (Offline) SYS-421GE-NBRT-LCC (8x B200-SXM-180GB) #1 Tokens/s, 128,795.00','Supermicro entries 5.0-0074 (SYS-A21GE-NBRT) and 5.0-0072 (SYS-421GE-NBRT-LCC), five rows, ranked among closed datacenter v5.0 entries with eight accelerators','five #1 results with the printed values and systems',f'values {sm(AIR,"stable-diffusion-xl","Server")}, {sm(AIR,"llama2-70b-interactive-99","Server")}, {sm(AIR,"llama3.1-405b","Server")}, {sm(LCC,"mixtral-8x7b","Server")}, {sm(LCC,"mixtral-8x7b","Offline")}; first place entries {firsts}','CONSISTENT' if ok and firsts==[AIR,AIR,AIR,LCC,LCC] else 'BELOW','Our rule: first among the entries with eight accelerators. Each row matches the entry and system the post names.'))
a405,l405=sm(AIR,'llama3.1-405b','Offline'),sm(LCC,'llama3.1-405b','Offline'); t405=top8('llama3.1-405b','Offline',b200)
SP.append(mk('SP3','Llama3.1-405b (offline) SYS-421GE-NBRT-LCC (8xB200-SXM-180GB) #1 Tokens/s 1521.74','Supermicro entries 5.0-0072 and 5.0-0074, Llama 3.1 405B Offline, against closed datacenter v5.0 entries with eight B200','#1 at 1521.74 on the liquid-cooled system',f'1521.74 is entry 5.0-0074 (SYS-A21GE-NBRT), not the liquid-cooled 5.0-0072, which is {l405:,.2f}. Eight-B200 Offline order: '+', '.join(f'{v:,.2f} {sb} {i}' for v,sb,i in t405[:4]),'CONSISTENT' if round(l405,2)==1521.74 and t405[0][2]==LCC else 'BELOW','1521.74 is third among eight-B200 entries behind 1538.17 (Supermicro, liquid-cooled) and 1526.29 (NVIDIA). The liquid-cooled system is first at 1538.17.'))
vend=sorted({x['Submitter'] for x in D if b200(x) and n(x)==8})
SP.append(mk('SP4','Supermicro is the only system vendor publishing record MLPerf inference performance (on select benchmarks) for both the air-cooled and liquid-cooled NVIDIA HGX B200 8-GPU systems.','submitters of eight B200 entries in the v5.0 file; Supermicro entries 5.0-0072 (LCC in the name) and 5.0-0074','only system vendor with both cooling types',f'submitters with eight B200: {vend}; Supermicro has two entries ({LCC}, {AIR})','CONSISTENT' if vend==['Google','NVIDIA','Supermicro'] else 'BELOW','Cooling type is read from the system name only. Google and NVIDIA are the other two submitters and are not system vendors in the post sense.'))
diffs=[]
for m,sc in(('llama2-70b-99','Offline'),('llama2-70b-99','Server'),('llama3.1-405b','Offline'),('llama3.1-405b','Server'),('mixtral-8x7b','Offline'),('mixtral-8x7b','Server'),('stable-diffusion-xl','Server'),('llama2-70b-interactive-99','Server')):
    try: a_,l_=sm(AIR,m,sc),sm(LCC,m,sc)
    except AssertionError: continue
    diffs.append((m,sc,100*(a_/l_-1)))
SP.append(mk('SP5','Within the operating margin, the Supermicro air-cooled NVIDIA HGX B200 system exhibited the same level of performance as the liquid-cooled HGX B200 system.','air-cooled 5.0-0074 against liquid-cooled 5.0-0072, eight model and scenario rows','same performance within the operating margin',', '.join(f'{m} {sc} {d:+.1f}%' for m,sc,d in diffs)+f'; largest gap {max(abs(d) for *_,d in diffs):.1f}%','CANNOT_TELL','The operating margin is not defined in the post. Rows where both systems have a result are compared. The air-cooled system is higher in some rows and lower in others.'))
SP.append(mk('SP6','showed performance leadership running the Mixtral 8x7B Inference, Mixture of Experts benchmarks with 129,000 tokens/second ... delivered over 1,000 tokens/second inference for the large Llama3.1-405b model','Supermicro B200 entries, Mixtral 8x7B and Llama 3.1 405B','129,000 tokens/s on Mixtral, over 1,000 tokens/s on Llama 3.1 405B',f'Mixtral Server {sm(LCC,"mixtral-8x7b","Server"):,.0f}, Offline {sm(LCC,"mixtral-8x7b","Offline"):,.0f}; Llama 3.1 405B Server {sm(AIR,"llama3.1-405b","Server"):,.2f}, Offline {l405:,.2f}','CONSISTENT' if sm(LCC,'mixtral-8x7b','Server')>129000 and sm(AIR,'llama3.1-405b','Server')>1000 and l405>1000 else 'BELOW',''))
mx=top8('llama2-70b-99','Offline',b200); sysv=[r for r in mx if r[1] not in('Google','NVIDIA')]
SP.append(mk('SP7','using the LLAMA2-70b benchmark, a Supermicro system with the NVIDIA HGX B200 SXM-180GB installed shows the highest performance from a Tier 1 system supplier','closed datacenter v5.0 Llama 2 70B 99 Offline entries with eight B200, by submitter','highest Llama 2 70B performance from a Tier 1 system supplier',f'eight-B200 Offline order: '+', '.join(f'{v:,.0f} {sb}' for v,sb,i in mx[:4])+f'; best from a submitter other than Google and NVIDIA: {sysv[0][1]}','CONSISTENT' if sysv and sysv[0][1]=='Supermicro' else 'BELOW','Tier 1 is not defined. Supermicro is the only B200 submitter that is a system vendor. NVIDIA is first at 98,858.'))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[f]).hexdigest() for f in FILES],claims=SP),open('claims_supermicro_v50.json','w'),indent=1)
for c in SP: print(c['id'],c['outcome'],'|',c['stated'][:44],'|',c['delivered'][:330])
