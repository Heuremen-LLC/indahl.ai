"""rows_text.py: writes the text of every table row printed on /atlas/electricity from electricity.json and utilities.json, formatted independently of the page builder.
The ledger rows for the tables point here. Run: python3 -I rows_text.py"""
import json,os
H=os.path.dirname(os.path.abspath(__file__))+'/'
E=json.load(open(H+'electricity.json')); U=json.load(open(H+'utilities.json'))['utilities']
f=lambda v: '—' if v is None else '%.1f'%v
lines=[]
for ab,v in sorted(E['states'].items(),key=lambda kv:kv[1]['name']):
    g=v['generation']; sh=[f(g['share'][k]) for k in ('coal','gas','nuclear','hydro','wind','solar','other')] if g else ['—']*7
    lines.append(f"STATE {v['name']} {f(v['sectors']['industrial']['price'])} {f(v['sectors']['commercial']['price'])} {f(v['sectors']['residential']['price'])} {' '.join(sh)} {v['data_centers']['epoch_mw']:,} {v['data_centers']['osm_features']:,}")
top=sorted([u for u in U if u['commercial_sales_mwh']+u['industrial_sales_mwh']>0 and u['utility_number']!=99999],key=lambda u:-(u['commercial_sales_mwh']+u['industrial_sales_mwh']))[:40]
for u in top:
    lines.append(f"UTILITY {u['name']} {u['state']} {u['ownership']} {f(u['industrial_price'])} {f(u['commercial_price'])} {f(u['residential_price'])} {(u['commercial_sales_mwh']+u['industrial_sales_mwh'])/1e6:,.1f}")
open(H+'rows_text.txt','w').write('\n'.join(lines)+'\n'); print(len(lines),'lines'); print(lines[0]); print(lines[-1])
