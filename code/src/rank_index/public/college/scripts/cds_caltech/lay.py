import sys,pypdf
r=pypdf.PdfReader(sys.argv[1])
open(sys.argv[2],'w').write('\n'.join(f'\n#### PAGE {i+1}\n'+(p.extract_text(extraction_mode="layout") or '') for i,p in enumerate(r.pages)))
f=r.get_fields()
if f:
    open(sys.argv[2]+'.fields','w').write('\n'.join(f'{k}\t{v.get("/V")}' for k,v in f.items() if v.get("/V") not in (None,'','/Off')))
