import sys,pypdf
r=pypdf.PdfReader(sys.argv[1]); open(sys.argv[2],'w').write("\n".join(f"\n#### PAGE {i+1}\n"+(p.extract_text(extraction_mode="layout") or '') for i,p in enumerate(r.pages)))
