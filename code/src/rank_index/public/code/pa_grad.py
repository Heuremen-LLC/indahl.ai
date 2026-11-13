import sys,openpyxl
wb=openpyxl.load_workbook(sys.argv[1],read_only=True)
ws=wb['Grad Rate by School']
for i,r in enumerate(ws.iter_rows(values_only=True)):
    if i==5: print(i+1,r)
    if r[2]=='126515001' and str(r[4]).strip() in('3808','03808','000003808'): print(i+1,r)
ws=wb['Notes and Definitions']
for r in ws.iter_rows(values_only=True):
    if r[0]: print(str(r[0])[:300])
