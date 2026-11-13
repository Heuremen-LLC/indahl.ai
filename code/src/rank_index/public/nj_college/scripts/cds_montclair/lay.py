import sys,pypdf
r=pypdf.PdfReader(sys.argv[1])
for i in map(int,sys.argv[2:]):
    print("=====PAGE",i); print(r.pages[i-1].extract_text(extraction_mode="layout"))
