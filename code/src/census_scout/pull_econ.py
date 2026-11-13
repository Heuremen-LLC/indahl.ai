import json,subprocess,urllib.request
def cg(u): return json.loads(subprocess.run(['/Users/heuremen/bones-forge/census_scout/cget.sh',u],capture_output=True,text=True).stdout)
def alf(sid,vdate,obs):
    u=f"https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={sid}&vintage_date={vdate}&cosd={obs}-01&coed={obs}-01"
    t=urllib.request.urlopen(u,timeout=60).read().decode().strip().splitlines()[-1]
    return t.split(',')[1]
def nxt(ym,k):
    y,m=map(int,ym.split('-')); m+=k
    while m>12: y+=1; m-=12
    return f"{y}-{m:02d}"
B="https://api.census.gov/data/timeseries/eits/"
out={}
for ym in ['2024-12','2025-03','2025-06']:
    r={}
    r['RSAFS']=dict(first=alf('RSAFS',nxt(ym,1)+'-20',ym),second=alf('RSAFS',nxt(ym,2)+'-20',ym),
        cur=cg(B+f"marts?get=cell_value&time={ym}&error_data=no&time_slot_id=0&seasonally_adj=yes&category_code=44X72&data_type_code=SM")[1][0],
        cv_pct=cg(B+f"marts?get=cell_value&time={ym}&error_data=yes&time_slot_id=0&seasonally_adj=yes&category_code=44X72&data_type_code=E_SM")[1][0],
        se_mom_pp=cg(B+f"marts?get=cell_value&time={ym}&error_data=yes&time_slot_id=0&seasonally_adj=yes&category_code=44X72&data_type_code=E_MPCSM")[1][0])
    r['HOUST']=dict(first=alf('HOUST',nxt(ym,1)+'-20',ym),second=alf('HOUST',nxt(ym,2)+'-20',ym),
        cur=[x for x in cg(B+f"resconst?get=cell_value,data_type_code,geo_level_code,seasonally_adj&time={ym}&error_data=no&time_slot_id=0&seasonally_adj=yes&category_code=ASTARTS") if x[1]=='TOTAL' and x[2]=='US'][0][0],
        err=[x for x in cg(B+f"resconst?get=cell_value,data_type_code,geo_level_code,seasonally_adj&time={ym}&error_data=yes&time_slot_id=0&seasonally_adj=yes&category_code=ASTARTS") if x[1]=='E_TOTAL' and x[2]=='US'])
    r['HSN1F']=dict(first=alf('HSN1F',nxt(ym,1)+'-25',ym),second=alf('HSN1F',nxt(ym,2)+'-25',ym),
        cur=[x for x in cg(B+f"ressales?get=cell_value,data_type_code,geo_level_code,seasonally_adj&time={ym}&error_data=no&time_slot_id=0&seasonally_adj=yes&category_code=ASOLD") if x[1]=='TOTAL' and x[2]=='US'][0][0],
        err=[x for x in cg(B+f"ressales?get=cell_value,data_type_code,geo_level_code,seasonally_adj&time={ym}&error_data=yes&time_slot_id=0&seasonally_adj=yes&category_code=ASOLD") if x[1]=='E_TOTAL' and x[2]=='US'])
    out[ym]=r
json.dump(out,open('/Users/heuremen/bones-forge/census_scout/raw/econ_examples.json','w'),indent=1)
print(json.dumps(out,indent=1))
