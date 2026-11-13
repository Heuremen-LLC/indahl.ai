import sys,pypdf,json
r=pypdf.PdfReader(sys.argv[1]);f=r.get_fields() or {}
print(len(f),file=sys.stderr)
json.dump({k:(v.get('/V')) for k,v in f.items()},open(sys.argv[2],'w'),indent=0,default=str)
