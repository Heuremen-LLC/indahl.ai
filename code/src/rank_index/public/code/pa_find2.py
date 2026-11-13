import sys,openpyxl
wb=openpyxl.load_workbook(sys.argv[1],read_only=True)
for ws in wb:
    for i,r in enumerate(ws.iter_rows(values_only=True)):
        if 3<=i<=6 or 'asterman' in str(r) or '126515001' in str(r) and '3808' in str(r): print(ws.title,i+1,r)
