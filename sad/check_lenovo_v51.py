# Lenovo Press article LP2330 on MLPerf Inference v5.1, held against the v5.1 result file. python3 -I check_claims_lenovo_v51.py
import json,hashlib,re
FILES=['raw/inf_5.1.json']; RAW={f:open(f,'rb').read() for f in FILES}
V=json.loads(RAW[FILES[0]]); s=str; P=lambda x:x['Performance_Result']
def n(x):
    m=re.findall(r'\(x(\d+)\)',s(x.get('Accelerator')))
    return sum(map(int,m)) if m else int((x.get('a#') or 0) or 0)*int(x.get('Nodes') or 1)
def mk(i,q,calc,st,got,out,note): return dict(id=i,quote=q,calc=calc,stated=st,delivered=got,outcome=out,note=note,label_mismatch=False)
D=[x for x in V if x['Category']=='closed' and 'datacenter' in x['Suite']]; Ed=[x for x in V if x['Category']=='closed' and x['Suite']=='edge']
def drank(i,m,sc):
    me=[x for x in D if x['ID']==i and x['Model']==m and x['Scenario']==sc]; assert len(me)==1,(i,m,sc,len(me))
    g=[x for x in D if x['Model']==m and x['Scenario']==sc and n(x)==8 and re.search(r'(?<!G)B200',s(x['Accelerator']))]
    return 1+sum(1 for x in g if P(x)>P(me[0])),len(g)
def erank(m,sc):
    me=[x for x in Ed if x['ID']=='5.1-0064' and x['Model']==m and x['Scenario']==sc]; assert len(me)==1,(m,sc)
    g=[x for x in Ed if x['Model']==m and x['Scenario']==sc]; low=sc in('SingleStream','MultiStream')
    return 1+sum(1 for x in g if (P(x)<P(me[0]) if low else P(x)>P(me[0]))),len(g)
fmt=lambda r:f'{r[0]}/{r[1]}'
sr680=[('llama2-70b-99','Server','7/10'),('llama2-70b-99','Offline','1/10'),('llama2-70b-99.9','Server','3/11'),('llama2-70b-99.9','Offline','1/11'),('whisper','Offline','7/14')]
sr780=[('llama3.1-8b','Server','4/9'),('llama3.1-8b','Offline','1/9'),('stable-diffusion-xl','Server','4/8'),('stable-diffusion-xl','Offline','6/9'),('llama3.1-405b','Server','2/13'),('llama3.1-405b','Offline','9/13'),('llama3.1-405b','Interactive','2/10'),('rgat','Offline','4/5'),('whisper','Offline','5/14')]
R680=[(m,sc,st,drank('5.1-0061',m,sc)) for m,sc,st in sr680]; R780=[(m,sc,st,drank('5.1-0062',m,sc)) for m,sc,st in sr780]
ed=[('resnet','SingleStream'),('resnet','MultiStream'),('resnet','Offline'),('retinanet','SingleStream'),('retinanet','MultiStream'),('retinanet','Offline'),('3d-unet-99','SingleStream'),('3d-unet-99','Offline'),('3d-unet-99.9','SingleStream'),('3d-unet-99.9','Offline'),('stable-diffusion-xl','SingleStream'),('stable-diffusion-xl','Offline')]
RED=[(m,sc,erank(m,sc)) for m,sc in ed]
cnt=lambda L,k:sum(1 for r in L if r[-1][0]==k)
f680,f780,fE=cnt(R680,1),cnt(R780,1),cnt(RED,1)
t680=(cnt(R680,1),cnt(R680,2),cnt(R680,3)); t780=(cnt(R780,1),cnt(R780,2),cnt(R780,3)); tE=(cnt(RED,1),cnt(RED,2),cnt(RED,3))
LN=[]
tot=f680+f780+fE
LN.append(mk('LN1','earning Top 3 rankings and 1st place in fifteen categories','first-place counts for the SR680a V3, SR780a V3 and SE100 entries under the rank rule in the notes',"1st place in fifteen categories",f'SR680a {f680}, SR780a {f780}, SE100 {fE} first places, total {tot}','CONSISTENT' if tot==15 else ('BELOW' if tot<15 else 'ABOVE'),'Our rank rule: datacenter entries ranked among the closed 8-accelerator B200 entries for the same model and scenario, which reproduces the field sizes in the list. Edge entries ranked among all closed edge entries for the same model and scenario. Singlestream and multistream rank by lower latency.'))
orgs=len({x['Submitter'] for x in V}); orgs_c=len({x['Submitter'] for x in V if x['Category']=='closed'})
LN.append(mk('LN2','twenty-seven participating organizations','distinct Submitter values in the v5.1 file','twenty-seven participating organizations',f'{orgs} distinct submitter names in the file, {orgs_c} with a closed entry','CANNOT_TELL','Submitter names in the file include combined names such as Dell_Broadcom and Supermicro_MangoBoost, so the count of organizations depends on how those are split. The count of organizations MLCommons announced is not a file field.'))
names=[('AMD','AMD'),('Azure','Azure'),('Broadcom','Broadcom'),('Cisco','Cisco'),('Dell','Dell'),('Google','Google'),('Intel','Intel'),('HPE','HPE')]
miss=[a for a,b in names if not any(b in x['Submitter'] for x in V)]
LN.append(mk('LN3','AMD, Azure, Broadcom, Cisco, Dell, Google, Intel and HPE','Submitter values in the v5.1 file containing each name','eight named participants',f'{len(names)-len(miss)} of {len(names)} found as submitter names or parts of combined names; missing: {miss}','CONSISTENT' if not miss else 'BELOW','Broadcom appears only in combined names (Broadcom_Supermicro, Dell_Broadcom).'))
LN.append(mk('LN4','Table 1 row for ThinkEdge SE100','SE100 closed edge entry 5.1-0064, rank among closed edge entries for each model and scenario','12 categories, 12 first, 0 second, 0 third',f'{len(RED)} categories, {tE[0]} first, {tE[1]} second, {tE[2]} third; fields: '+', '.join(f'{m} {sc} {fmt(r)}' for m,sc,r in RED),'CONSISTENT' if (len(RED),)+tE==(12,12,0,0) else 'BELOW','The list in the post says 1/1 and no competitors for all twelve. The file has other closed edge entries in eight of the twelve, from GATEOverflow and HPE, and one other entry in two more.'))
LN.append(mk('LN5','Table 1 row for ThinkSystem SR680a V3','SR680a V3 entry 5.1-0061, ranks within closed 8-accelerator B200 entries','5 categories, 2 first, 0 second, 1 third',f'{len(R680)} categories, {t680[0]} first, {t680[1]} second, {t680[2]} third','CONSISTENT' if (len(R680),)+t680==(5,2,0,1) else 'BELOW',''))
LN.append(mk('LN6','Table 1 row for ThinkSystem SR780a V3 (Intel)','SR780a V3 entry 5.1-0062, ranks within closed 8-accelerator B200 entries','9 categories, 1 first, 2 second, 2 third',f'{len(R780)} categories, {t780[0]} first, {t780[1]} second, {t780[2]} third','CONSISTENT' if (len(R780),)+t780==(9,1,2,2) else 'BELOW','The ranks listed under the table in the post also give no third place for this system: 4, 1, 4, 6, 2, 9, 2, 4 and 5.'))
ok680=all(fmt(r)==st for m,sc,st,r in R680)
LN.append(mk('LN7','List of SR680a V3 ranks in the post for llama2-70b-99 and 99.9 Server and Offline and whisper','SR680a V3 entry 5.1-0061 ranks within closed 8-accelerator B200 entries','7/10, 1/10, 3/11, 1/11, 7/14',', '.join(f'{m} {sc} {fmt(r)}' for m,sc,st,r in R680),'CONSISTENT' if ok680 else 'BELOW',''))
bad=[(m,sc,st,fmt(r)) for m,sc,st,r in R780 if fmt(r)!=st]
LN.append(mk('LN8','List of SR780a V3 ranks in the post for nine model and scenario pairs','SR780a V3 entry 5.1-0062 ranks within closed 8-accelerator B200 entries','4/9, 1/9, 4/8, 6/9, 2/13, 9/13, 2/10, 4/5, 5/14',', '.join(f'{m} {sc} {fmt(r)}' for m,sc,st,r in R780),'CONSISTENT' if not bad else 'BELOW','Differences from the post: '+'; '.join(f'{m} {sc} stated {st}, file {g}' for m,sc,st,g in bad)+'. The rank itself matches in each case, the field size differs by one.' if bad else ''))
nc=[(m,sc,r) for m,sc,r in RED if r[1]>1]
LN.append(mk('LN9','List of twelve SE100 entries in the post, each marked 1/1 - no competitors','closed edge entries for the same model and scenario as each SE100 entry','12 categories with no competitors',f'{len(nc)} of 12 have other closed edge entries; field sizes: '+', '.join(f'{m} {sc} {r[1]}' for m,sc,r in RED),'CONSISTENT' if not nc else 'BELOW','Rank 1 holds in every one of the twelve (see the Table 1 row). The no competitors label does not.' if all(r[0]==1 for m,sc,r in RED) else 'Rank 1 does not hold in every one of the twelve.'))
json.dump(dict(source=FILES,sha256=[hashlib.sha256(RAW[f]).hexdigest() for f in FILES],claims=LN),open('claims_lenovo_v51.json','w'),indent=1)
for c in LN: print(c['id'],c['outcome'],'|',c['stated'][:50],'|',c['delivered'][:300])
