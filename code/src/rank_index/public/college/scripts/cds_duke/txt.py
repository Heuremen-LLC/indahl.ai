import sys,glob,os,pymupdf
for f in glob.glob(sys.argv[1]+'/*.pdf'):
    d=pymupdf.open(f); open('/private/tmp/claude-501/-Users-heuremen/ba08385b-5844-4963-b441-21052a55d90b/scratchpad/'+os.path.basename(f)+'.txt','w').write('\n'.join(f'\n#### PAGE {i+1}\n'+p.get_text() for i,p in enumerate(d)))
