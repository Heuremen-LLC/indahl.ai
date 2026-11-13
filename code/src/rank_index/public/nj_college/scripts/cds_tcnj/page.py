import sys,pypdf
r=pypdf.PdfReader(sys.argv[1]);w=pypdf.PdfWriter();w.add_page(r.pages[int(sys.argv[2])-1]);w.write(sys.argv[3])
