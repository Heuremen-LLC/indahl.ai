# Adds ledger rows (one per claim, one tally, coverage rows for stated/compared/note) for one SAD source after build_sad.py and build_site.py have run.
# python3 ledger_sad_source.py "NVIDIA v6.1" nv61 raw/nv_blog_v61.txt
import json,subprocess,collections,re,sys,importlib.util,os
LED=os.path.expanduser('~/bones-forge/ledger'); MP=os.path.expanduser('~/bones-forge/mlperf_index')
K,PFX,RAWF=sys.argv[1],sys.argv[2],sys.argv[3]
spec=importlib.util.spec_from_file_location('cl',LED+'/check_ledger.py'); cl=importlib.util.module_from_spec(spec); spec.loader.exec_module(cl)
S=json.load(open(MP+'/sad_claims.json'))['claims']; summ=open(MP+'/sad_summary.json').read(); NEW=[c for c in S if c['source_key']==K]
def run(*a): return subprocess.run(['python3','ledger.py',*a],capture_output=True,text=True,cwd=LED)
def add(i,claim,val,out,grep,snip,src='mlperf_index/sad_claims.json'):
    r=run('add',i,'--claim',claim,'--value',val,'--outcome',out,'--source',src,'--grep',grep,'--on','sad',snip)
    if r.returncode: print(i,(r.stdout+r.stderr).strip()[:150])
for c in NEW: add(f"sad.{PFX}.{c['id'].lower()}",f"{K} statement {c['id']} held against the MLCommons files: {c['stated']}",c['in_file'],c['outcome'],c['in_file'],c['in_file'])
order=['ABOVE','BELOW','CONSISTENT','CANNOT_TELL']; cnt=collections.Counter(c['outcome'] for c in NEW)
txt=f"{len(NEW)} statements checked: "+', '.join(f"{cnt[o]} {o}" for o in order if cnt[o])+'.'
g=re.search(r'"'+re.escape(K)+r'":\{[^}]*\}',summ).group(); add(f'sad.{PFX}.tally',f"{K} statements checked and their outcomes",txt,'COUNT',g,txt,'mlperf_index/sad_summary.json'); print(txt)
page=cl.norm(cl.text_of('sad')); num=re.compile(r'(?<![\w.])[+-]?\d+\.\d+')
def covered(): return ' '.join(cl.norm(s['text']) for l in open(LED+'/ledger.jsonl') for r in [json.loads(l)] if r['status']=='live' for s in r['surfaces'] if s['surface']=='sad')
raw=open(MP+'/'+RAWF.replace('raw/','raw/',1)).read() if not RAWF.startswith('/') else open(RAWF).read(); n=0
for c in NEW:
    for f in ('statement','compared','stated','note'):
        v=c[f]
        if not v or not num.search(v): continue
        if all(x in covered() for x in num.findall(v)) or cl.norm(v) not in page: continue
        first=v.split(' ... ')[0]
        src,gr=(f'mlperf_index/{RAWF}',first) if (f=='statement' and c['verbatim'] and first in raw) else ('mlperf_index/sad_claims.json',v)
        if gr not in open(os.path.expanduser('~/bones-forge/')+src).read(): print('skip',c['id'],f); continue
        r=run('add',f"sad.{PFX}.{c['id'].lower()}.{f}",'--claim',f"{K} statement {c['id']} {f}",'--value',v,'--outcome','RECORD','--source',src,'--grep',gr,'--on','sad',v)
        if r.returncode: print(c['id'],f,(r.stdout+r.stderr).strip()[:140])
        else: n+=1
print('coverage rows',n); t=cl.text_of('sad'); cov=covered(); print('uncovered:',[m.group() for m in num.finditer(t) if m.group() not in cov and not m.group().startswith('2610')])
