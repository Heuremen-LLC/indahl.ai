import sys,openpyxl
wb=openpyxl.load_workbook(sys.argv[1],read_only=True)
for ws in wb:
    for i,r in enumerate(ws.iter_rows(values_only=True)):
        if i<4 or 'asterman' in str(r): print(ws.title,i+1,r)
