# Reads the MLCommons v6.1 summary spreadsheet (datacenter closed tab) into raw/v61_ids.json: entry ID, submitter, system, accelerator, count and every result. python3 -I build_v61_ids.py
import sys,json,os
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.expanduser('~/bones-forge/atlas/electricity'))
import xlsxread
R=xlsxread.rows(os.path.join(HERE,'raw','summary_v61.xlsx'),0)
model=[None]*len(R[1]); last=None
for j in range(16,len(R[1])):
    if R[1][j] is not None: last=R[1][j]
    model[j]=last
out={}
for r in R[5:]:
    if not r or not r[0] or not str(r[0]).startswith('6.1-'): continue
    res={}
    for j in range(17,len(r)):
        if r[j] is not None and model[j] and R[2][j]: res[f'{model[j]}|{R[2][j]}']=r[j]
    out[r[0]]=dict(submitter=r[4],availability=r[5],system=r[6],accelerator=r[10],per_node=r[11],total_accelerators=r[12],results=res)
json.dump(out,open(os.path.join(HERE,'raw','v61_ids.json'),'w'),indent=1); print(len(out))
