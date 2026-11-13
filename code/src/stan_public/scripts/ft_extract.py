"""Step 1a of the full-text ceiling: pypdf extraction (run with the interpreter that has pypdf 6.21.1)."""
import json,sys,pypdf
S='/Users/heuremen/bones-forge/stan'
cov=json.load(open(S+'/data/fulltext_coverage.json'))['per_id']
out={}
for i,v in cov.items():
    if v['split']!='dev' or v['result']!='FETCHED': continue
    try:
        r=pypdf.PdfReader(v['file']); pages=[(p.extract_text() or '') for p in r.pages]
    except Exception as e:
        out[i]={'error':str(e)}; continue
    t='\f'.join(pages)
    open(S+'/ceiling_ft/text/%s.txt'%i,'w').write(t)
    out[i]={'pages':len(pages),'chars':len(t)}
json.dump({'pypdf':pypdf.__version__,'python':sys.version.split()[0],'papers':out},open(S+'/ceiling_ft/extract_log.json','w'),indent=1)
print(pypdf.__version__,len(out))
