import json, re, os, sys, html
ROOT = os.path.expanduser('~/bones-forge')
S = os.path.join(ROOT, 'watch/site_pass_20261030/scratch_HEU2')
doc = sys.argv[1]   # pdf text file
surfs = sys.argv[2].split(',')  # ledger surface keys to count as covered
exec(open(os.path.join(S,'chk_paper_rows2.py')).read().split("pdf = open")[0])  # canon, norm_tex
def pre(s):
    s = s.replace('ﬁ','fi').replace('ﬂ','fl').replace('ﬀ','ff').replace('ﬃ','ffi').replace('ﬄ','ffl')
    s = s.replace('◦','°').replace('−','-').replace('–','-').replace('—','-').replace(' ',' ').replace('\xa0',' ')
    s = s.replace('µ','μ').replace('’',"'")
    return s
text = pre(open(os.path.join(S,doc)).read())
# canon with index map
chars=[]; idx=[]
for i,c in enumerate(text):
    if c.isspace(): continue
    chars.append(c.lower()); idx.append(i)
C=''.join(chars)
# remove hyphens between letters
keep=[True]*len(C)
for i in range(1,len(C)-1):
    if C[i]=='-' and C[i-1].isalpha() and C[i+1].isalpha(): keep[i]=False
C2=''.join(c for c,k in zip(C,keep) if k); idx2=[x for x,k in zip(idx,keep) if k]
rows=[json.loads(l) for l in open(os.path.join(ROOT,'ledger/ledger.jsonl'))]
cov=[False]*len(C2)
nsn=0
for r in rows:
    if r['status']!='live': continue
    for s in r['surfaces']:
        if s['surface'] not in surfs: continue
        raw = norm_tex(s['text'])
        parts = raw.split('&') if '&' in raw else [raw]
        for p in parts:
            cp = canon(p)
            if not cp: continue
            start=0
            while True:
                j=C2.find(cp,start)
                if j<0: break
                for k in range(j,j+len(cp)): cov[k]=True
                nsn+=1; start=j+1
numre=re.compile(r'(?<![\w.])[+\-]?\d+\.\d+')
unc=[]; tot=0
for m in numre.finditer(C2):
    tot+=1
    if not all(cov[m.start():m.end()]):
        unc.append(m)
print('decimals in doc',tot,'uncovered',len(unc))
out=[]
for m in unc:
    a=idx2[m.start()]; b=idx2[m.end()-1]
    ctx=text[max(0,a-90):b+60].replace('\n',' ')
    out.append((m.group(0), ctx))
for t,c in out: print(t,'|',c)
