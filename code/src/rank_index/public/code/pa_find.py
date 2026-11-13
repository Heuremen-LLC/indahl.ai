import sys,openpyxl
p,key=sys.argv[1],sys.argv[2]
wb=openpyxl.load_workbook(p,read_only=True)
for ws in wb:
    for i,r in enumerate(ws.iter_rows(values_only=True)):
        if i<3: print(ws.title,i,r)
        if any(key in str(c) for c in r if c is not None): print(ws.title,i+1,r)
