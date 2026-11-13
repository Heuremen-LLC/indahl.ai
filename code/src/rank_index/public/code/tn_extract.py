import sys,openpyxl,json
p=sys.argv[1]
wb=openpyxl.load_workbook(p,read_only=True)
ws=wb.worksheets[0]; ws.reset_dimensions()
out=[]
for i,r in enumerate(ws.iter_rows(values_only=True)):
    if i==0: h=r; continue
    if r[1]==750 and r[3]==15 and r[7]=='All Grades' and r[8]=='All Students':
        d=dict(zip(h,r)); d['row']=i+1; out.append(d)
for d in out: print(json.dumps(d))
