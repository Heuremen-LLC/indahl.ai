"""build_carbon.py (28 Oct 2026): ATLAS carbon layer from EPA eGRID2023 (state and subregion total output emission rates). Outputs under electricity/: carbon.json, map_carbon.svg, carbon_rows_text.txt, carbon_summary.json."""
import json,os,sys,datetime
H=os.path.dirname(os.path.abspath(__file__))+'/'
sys.path.insert(0,H); sys.path.insert(0,H+'electricity')
import mapkit as M
from xlsxread import rows,sheets
SH=[s[0] for s in sheets(H+'electricity/raw/egrid2023.xlsx')]
def sheet(n): r=rows(H+'electricity/raw/egrid2023.xlsx',SH.index(n)); return r[1],r[2:]
h,st=sheet('ST23'); ix={c:i for i,c in enumerate(h)}
states={}
for x in st:
    ab=x[ix['PSTATABB']]
    if ab not in M.ABBR2NAME: continue
    states[ab]=dict(name=M.ABBR2NAME[ab],co2_lb_mwh=float(x[ix['STCO2RTA']]),nox_lb_mwh=float(x[ix['STNOXRTA']]),so2_lb_mwh=float(x[ix['STSO2RTA']]),net_generation_mwh=float(x[ix['STNGENAN']]))
h,sr=sheet('SRL23'); jx={c:i for i,c in enumerate(h)}
subs=[dict(code=x[jx['SUBRGN']],name=x[jx['SRNAME']],co2_lb_mwh=float(x[jx['SRCO2RTA']]),nox_lb_mwh=float(x[jx['SRNOXRTA']]),so2_lb_mwh=float(x[jx['SRSO2RTA']]),net_generation_mwh=float(x[jx['SRNGENAN']])) for x in sr if x[jx['SUBRGN']]]
h,us=sheet('US23'); ux={c:i for i,c in enumerate(h)}; u=us[0]
USR=dict(co2_lb_mwh=float(u[ux['USCO2RTA']]),nox_lb_mwh=float(u[ux['USNOXRTA']]),so2_lb_mwh=float(u[ux['USSO2RTA']]),net_generation_mwh=float(u[ux['USNGENAN']]))
f0=lambda v:f'{v:,.0f}'
svg,leg=M.choropleth({a:s['co2_lb_mwh'] for a,s in states.items()},f0,'pounds of CO2 per MWh','Map of the contiguous United States shaded by pounds of carbon dioxide emitted per megawatthour of net generation in 2023, with data center sites over it',0)
open(H+'electricity/map_carbon.svg','w').write(svg)
E=json.load(open(H+'electricity/electricity.json'))['states']
json.dump(dict(built='2026-10-28',data_year=2023,source='EPA eGRID2023 rev 2 (egrid2023_data_rev2.xlsx), sheets ST23, SRL23, US23. Total output emission rates in pounds per megawatthour of net generation, all fuels.',us=USR,states=states,subregions=subs,legend=leg),open(H+'electricity/carbon.json','w'),indent=1)
lines=[f"US {f0(USR['co2_lb_mwh'])} {USR['nox_lb_mwh']:.3f} {USR['so2_lb_mwh']:.3f} {USR['net_generation_mwh']/1e6:,.1f}"]
for ab,s in sorted(states.items(),key=lambda kv:kv[1]['name']):
    lines.append(f"STATE {s['name']} {f0(s['co2_lb_mwh'])} {s['nox_lb_mwh']:.3f} {s['so2_lb_mwh']:.3f} {s['net_generation_mwh']/1e6:,.1f} {E[ab]['data_centers']['epoch_mw']:,}")
for s in sorted(subs,key=lambda s:s['name']):
    lines.append(f"SUB {s['name']} {s['code']} {f0(s['co2_lb_mwh'])} {s['nox_lb_mwh']:.3f} {s['so2_lb_mwh']:.3f} {s['net_generation_mwh']/1e6:,.1f}")
open(H+'electricity/carbon_rows_text.txt','w').write('\n'.join(lines)+'\n')
json.dump(dict(us=USR,states=len(states),subregions=len(subs)),open(H+'electricity/carbon_summary.json','w'),separators=(',',':'),sort_keys=True)
print(USR); print(len(states),'states',len(subs),'subregions'); print(leg); print(lines[:3]); print(sorted(states.items(),key=lambda kv:kv[1]['co2_lb_mwh'])[:2][0][0],sorted(states.items(),key=lambda kv:-kv[1]['co2_lb_mwh'])[0][0])
