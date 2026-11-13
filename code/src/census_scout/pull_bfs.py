import json,subprocess,collections
def cg(u): return json.loads(subprocess.run(['/Users/heuremen/bones-forge/census_scout/cget.sh',u],capture_output=True,text=True).stdout)
B="https://api.census.gov/data/timeseries/eits/bfs?get=cell_value,data_type_code&for=us:*&error_data=no&seasonally_adj=no&time_slot_id=0&category_code=TOTAL&time=from+2004-07"
d=cg(B); h=d[0]; ti=h.index('time')
S=collections.defaultdict(dict)
for r in d[1:]: S[r[ti]][r[1]]=float(r[0])
json.dump(S,open('/Users/heuremen/bones-forge/census_scout/raw/bfs_us_total_nsa.json','w'))
ms=sorted(S); print(len(ms),ms[0],ms[-1])
for m in ['2019-03','2021-03','2023-03','2024-09','2025-06']:
    s=S.get(m,{}); print(m,{k:s.get(k) for k in ['BF_PBF4Q','BF_BF4Q','BF_SBF4Q','BF_PBF8Q','BF_BF8Q','BA_BA']})
print(sum(1 for m in ms if 'BF_PBF4Q' in S[m] and 'BF_BF4Q' in S[m]),'months both')
print(sum(1 for m in ms if S[m].get('BF_PBF4Q') is not None and S[m].get('BF_BF4Q') is not None and S[m]['BF_PBF4Q']!=S[m]['BF_BF4Q']),'differ')
