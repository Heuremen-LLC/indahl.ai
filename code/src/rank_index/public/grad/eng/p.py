import sys,pymupdf
d=pymupdf.open(sys.argv[1])
for i,p in enumerate(d):
    print(f"\n#### PAGE {i+1}\n"+p.get_text())
