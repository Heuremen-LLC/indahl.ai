import sys,openpyxl
p=sys.argv[1]; pats=sys.argv[2:]
wb=openpyxl.load_workbook(p,read_only=True)
for ws in wb:
    ws.reset_dimensions(); hdr=None
    for i,r in enumerate(ws.iter_rows(values_only=True)):
        if i<3: print(ws.title,i+1,"HDR?",[c for c in r if c is not None][:40])
        if i>2 and any(any(q in str(c) for q in pats) for c in r if c is not None): print(ws.title,i+1,[c for c in r])
