import csv,json,subprocess
R='/Users/heuremen/bones-forge/census_scout/raw/'
def rows(f): return {r['NAME']:r for r in csv.DictReader(open(R+f,encoding='latin1'))}
v19=rows('nst-est2019-alldata.csv'); v20=rows('nst-est2020.csv')
v22=rows('NST-EST2022-ALLDATA.csv'); v23=rows('NST-EST2023-ALLDATA.csv'); v24=rows('NST-EST2024-ALLDATA.csv'); v25=rows('NST-EST2025-ALLDATA.csv')
pes={r[0]:r for r in json.load(open(R+'pes_g_states.json'))[1:]}
cen=json.loads(subprocess.run(['/Users/heuremen/bones-forge/census_scout/cget.sh','https://api.census.gov/data/2020/dec/pl?get=NAME,P1_001N&for=state:*'],capture_output=True,text=True).stdout)
cen={r[0]:int(r[1]) for r in cen[1:]}
json.dump(cen,open(R+'census2020_pl_state.json','w'))
for s in ['California','Texas','Arkansas']:
    print(s)
    print(' V2019 Jul2019',v19[s]['POPESTIMATE2019'],' V2020 Apr2020',v20[s]['POPESTIMATE042020'],' V2020 Jul2020',v20[s]['POPESTIMATE2020'])
    print(' Census Apr2020',cen[s],' PES NCE%',pes[s][5],'SE%',pes[s][7],' PES census count(thousands-rounded)',pes[s][3])
    print(' Jul2020 by vintage: V2022',v22[s]['POPESTIMATE2020'],'V2023',v23[s]['POPESTIMATE2020'],'V2024',v24[s]['POPESTIMATE2020'],'V2025',v25[s]['POPESTIMATE2020'])
    print(' Jul2022 by vintage: V2022',v22[s]['POPESTIMATE2022'],'V2023',v23[s]['POPESTIMATE2022'],'V2024',v24[s]['POPESTIMATE2022'],'V2025',v25[s]['POPESTIMATE2022'])
    print(' base2020 by vintage V2022',v22[s]['ESTIMATESBASE2020'],'V2024',v24[s]['ESTIMATESBASE2020'],'V2025',v25[s]['ESTIMATESBASE2020'])
