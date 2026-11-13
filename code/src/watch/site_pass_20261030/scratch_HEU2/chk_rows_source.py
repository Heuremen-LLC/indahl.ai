import json, re, os, sys
ROOT = os.path.expanduser('~/bones-forge')
rows=[json.loads(l) for l in open(os.path.join(ROOT,'ledger/ledger.jsonl'))]
surf = sys.argv[1]
nrow=0; nosrc=[]; nogrep=[]; valmiss=[]
def nums(x):
    return re.findall(r'[+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?', str(x)) if x is not None else []
for r in rows:
    if r['status']!='live': continue
    if not any(s['surface']==surf for s in r['surfaces']): continue
    nrow+=1
    f=r['source']['file']; sp=f if f.startswith('/') else os.path.join(ROOT,f)
    if not os.path.exists(sp): nosrc.append((r['id'],f)); continue
    txt=open(sp,errors='ignore').read()
    g=r['source']['grep']
    if g not in txt: nogrep.append((r['id'],f,g[:80])); continue
    gl=g
    for k in ('value','lo','hi'):
        v=r.get(k)
        if v in (None,''): continue
        for n in nums(v):
            nn=n.lstrip('+-')
            if nn not in gl.replace(',',' '):
                i=txt.index(g); ls=txt.rfind('\n',0,i)+1; le=txt.find('\n',i); line=txt[ls:le if le>0 else None]
                if nn not in line:
                    valmiss.append((r['id'],k,v,g[:100]))
                    break
print('rows with surface',surf,nrow,'no source file',len(nosrc),'grep absent',len(nogrep),'value-not-in-source-line',len(valmiss))
for x in nosrc: print('NOSRC',x)
for x in nogrep: print('NOGREP',x)
for x in valmiss: print('VAL',x)
