import sys,openpyxl
p,pat=sys.argv[1],sys.argv[2]
wb=openpyxl.load_workbook(p,read_only=True)
for ws in wb:
    ws.reset_dimensions()
    for i,r in enumerate(ws.iter_rows(values_only=True)):
        if i==0: print(ws.title,"HDR",r)
        if i>0 and any(pat in str(c) for c in r if c is not None): print(ws.title,i+1,r)
