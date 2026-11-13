"""Keep a dated local copy + sha256 of every URL quoted in rows/*.md (receipts survive page edits). Reuses the sweep / receipt-check caches.
Writes receipts/MANIFEST.jsonl (url, slugs, sha256, bytes, fetched_utc, source) ; files in receipts/files/<sha256> (gitignored)."""
import re,glob,os,json,hashlib,subprocess,shutil,time
B=os.path.expanduser('~/bones-forge/oy_index/'); OUT=B+'receipts/'; F=OUT+'files/'
S='/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/'
CACHES=[S+'dl_chatbot_sweep/',S+'dl_oy_check/']
done={}
if os.path.exists(OUT+'MANIFEST.jsonl'):
    for l in open(OUT+'MANIFEST.jsonl'): d=json.loads(l); done[d['url']]=d
urls={}
for f in sorted(glob.glob(B+'rows/*.md')):
    slug=os.path.basename(f)[:-3]
    if slug=='SCHOOL_LIST': continue
    for u in set(re.findall(r'https?://[^\s)|>"\]]+',open(f).read())):
        urls.setdefault(u.rstrip('.,;:'),set()).add(slug)
man=open(OUT+'MANIFEST.jsonl','a'); n_new=n_fail=0
for u,slugs in sorted(urls.items()):
    if u in done: continue
    h=hashlib.md5(u.encode()).hexdigest(); src=None
    for c in CACHES:
        if os.path.exists(c+h) and os.path.getsize(c+h)>500: src=c+h; how='cache'; break
    if not src:
        tmp=F+'.tmp'; r=subprocess.run(['curl','-sL','-m','40','-A','Mozilla/5.0','--max-filesize','30000000','-o',tmp,u],capture_output=True)
        if os.path.exists(tmp) and os.path.getsize(tmp)>500: src=tmp; how='fetched'
    if not src:
        n_fail+=1; man.write(json.dumps({'url':u,'slugs':sorted(slugs),'sha256':None,'note':'fetch failed or <500 bytes','fetched_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})+'\n'); continue
    b=open(src,'rb').read(); sh=hashlib.sha256(b).hexdigest()
    if not os.path.exists(F+sh): shutil.copyfile(src,F+sh)
    if src.endswith('.tmp'): os.remove(src)
    man.write(json.dumps({'url':u,'slugs':sorted(slugs),'sha256':sh,'bytes':len(b),'source':how,'fetched_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})+'\n'); man.flush(); n_new+=1
print('urls',len(urls),'archived_now',n_new,'failed_now',n_fail,'already',len(done))
