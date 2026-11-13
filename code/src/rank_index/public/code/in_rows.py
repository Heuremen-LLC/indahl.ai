import sys,openpyxl
p=sys.argv[1]
wb=openpyxl.load_workbook(p,read_only=True)
for ws in wb:
    ws.reset_dimensions(); n=0
    for i,r in enumerate(ws.iter_rows(values_only=True)):
        if i<4 and r and sum(c is not None for c in r)>3: print(ws.title,i+1,"H",r)
        if r and any(("8295" in str(c)) or ("Signature School" in str(c)) for c in r): print(ws.title,i+1,"ROW",r)
