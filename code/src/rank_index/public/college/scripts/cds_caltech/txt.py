import sys,glob,os,pypdf
out=sys.argv[2]
for f in glob.glob(sys.argv[1]+'/*.pdf'):
    r=pypdf.PdfReader(f)
    open(out+'/'+os.path.basename(f)+'.txt','w').write('\n'.join(f'\n#### PAGE {i+1}\n'+(p.extract_text() or '') for i,p in enumerate(r.pages)))
