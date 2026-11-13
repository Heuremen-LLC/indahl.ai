import json,subprocess
def cg(u):
    t=subprocess.run(['/Users/heuremen/bones-forge/census_scout/cget.sh',u],capture_output=True,text=True).stdout
    try: return json.loads(t)
    except Exception: return t[:200]
for yr in [2023]:
  for geo,lab in [('for=state:06','CA'),('for=state:48','TX'),('for=state:05','AR'),('for=county:037&in=state:06','LA Co'),('for=county:031&in=state:17','Cook Co'),('for=county:201&in=state:48','Harris Co')]:
    s=cg(f"https://api.census.gov/data/timeseries/poverty/saipe?get=NAME,SAEPOVRTALL_PT,SAEPOVRTALL_LB90,SAEPOVRTALL_UB90,SAEPOVALL_PT,SAEPOVALL_LB90,SAEPOVALL_UB90&{geo}&time={yr}")
    a=cg(f"https://api.census.gov/data/{yr}/acs/acs1/subject?get=NAME,S1701_C03_001E,S1701_C03_001M,S1701_C02_001E,S1701_C02_001M&{geo}")
    print(lab,yr,'SAIPE',s[1][:7] if isinstance(s,list) else s)
    print('    ACS1 S1701 (rate E,MOE90; count E,MOE90)',a[1][:5] if isinstance(a,list) else a)
