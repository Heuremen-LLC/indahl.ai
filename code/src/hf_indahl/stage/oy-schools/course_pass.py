"""Local, no-agent course-catalog pass (27 Oct 2026). For each domain: probe public catalog paths + sitemap course URLs, fetch <=30 pages (HTML or PDF),
keep course-title lines whose title matches an AI / technology-ethics pattern. Output: courses.jsonl (domain,url,line), courses_coverage.json (pages fetched per domain). Never executes anything fetched. Run with python3 -I."""
import re,sys,os,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import small_pass as sp
from multiprocessing import Pool
OUT=os.path.dirname(os.path.abspath(__file__))+'/'
CODE=r'[A-Z]{2,5}[ -]?\d{2,4}[A-Z]?'
KEY=re.compile(r'(artificial intelligence|machine learning|\bAI\b|data ethics|ethics of (?:technology|data|AI|artificial)|technology (?:and|&) (?:society|ethics|human)|science,? technology,? (?:and|&) society|digital humanities|algorithm(?:s|ic)? (?:and|&|bias|justice)|ethics (?:and|&|of) (?:emerging )?tech|human[- ]computer|computational (?:social|thinking|ethics)|critical (?:data|digital|media) (?:studies|literacy)|surveillance|big data|data science|robot(?:s|ics)? (?:and|&) |philosophy of (?:mind|technology|computation)|generative)',re.I)
LINE=re.compile(r'('+CODE+r')[\s.:\-–—]+([A-Z][^\n]{6,140})')
PATHS=['/catalog','/catalog/','/academics/catalog','/academics/course-catalog','/course-catalog','/courses','/academics/courses','/academics/course-descriptions','/course-descriptions','/registrar/course-descriptions','/academics/registrar/courses','/academics/majors-minors','/academics/departments']
def job(d):
    base='https://'+d; urls=[]
    for h in ('catalog.'+d,'courses.'+d,'bulletin.'+d): urls+= ['https://'+h+'/']
    urls+=[base+p for p in PATHS]
    for s in sp.urls_for(d)[:400] if hasattr(sp,'urls_for') else []:
        if re.search(r'(catalog|course|bulletin|curricul|syllab)',s,re.I): urls.append(s)
    seen=[];hits=[];n=0;i=0;nlines=0
    from urllib.parse import urljoin,urlparse
    while i<len(urls):
        u=urls[i]; i+=1
        if u in seen: continue
        seen.append(u)
        if n>=60: break
        b=sp.fetch(u,25); t=sp.text(b) if b else None
        if not t: continue
        n+=1
        if b[:4]!=b'%PDF' and len(urls)<400:
            raw=b.decode('utf-8','ignore'); host=urlparse(u).netloc.split('.',1)[-1]
            for hh in re.findall(r'href=["\']([^"\'#]+)',raw)[:3000]:
                if not re.search(r'(preview_course|course|catalog|department|program|computer|data-sci|philosoph|ethic|technolog|digital|artificial)',hh,re.I): continue
                v=urljoin(u,hh)
                if urlparse(v).netloc.endswith(host) and v not in seen and v not in urls and not re.search(r'\.(jpg|png|css|js|zip)$',v): urls.append(v)
        for m in LINE.finditer(re.sub(r'\s{2,}',' \n',t)):
            nlines+=1
            if KEY.search(m.group(2)): hits.append({'url':u,'line':(m.group(1)+' '+m.group(2))[:200]})
    return {'domain':d,'pages':n,'course_lines':nlines,'hits':hits[:40]}
if __name__=='__main__':
    src=sys.argv[1] if len(sys.argv)>1 else OUT+'domains_all.txt'
    doms=[l.strip() for l in open(src) if l.strip() and not l.startswith('#')]
    h=open(OUT+'courses.jsonl','w'); cov={}
    with Pool(8) as p:
        for r in p.imap_unordered(job,doms):
            cov[r['domain']]={'pages':r['pages'],'course_lines':r['course_lines'],'matches':len(r['hits'])}
            for x in r['hits']: h.write(json.dumps({'domain':r['domain'],**x})+'\n')
            h.flush(); print(r['domain'],r['pages'],r['course_lines'],len(r['hits']),flush=True)
    json.dump(cov,open(OUT+'courses_coverage.json','w'),indent=0)
