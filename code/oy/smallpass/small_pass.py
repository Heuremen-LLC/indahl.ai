"""Local, no-agent crawl of small private school sites for AI-in-learning EVIDENCE sentences.
For each domain: sitemap.xml (+children) and WordPress REST search -> AI-ish URLs -> fetch <=25 pages -> sentences with AI word AND an evidence token.
Output: smallpass/hits.jsonl (domain,url,sentence) and smallpass/coverage.json. Downloads cached in scratchpad. Never executes anything fetched. Run with python3 -I."""
import re,sys,os,json,time,hashlib,html,subprocess,io
from multiprocessing import Pool
OUT='./'; C='./cache'; os.makedirs(C,exist_ok=True)
AIURL=re.compile(r'(?:^|[/\-_.])(ai|artificial-intelligence|generative|genai|gen-ai|chatgpt|llm|copilot|claude|gemini)(?:[/\-_.]|$)',re.I)
AIW=re.compile(r'\b(AI|A\.I\.|generative|ChatGPT|chatbot|large language|LLM|Copilot|Gemini|Claude)\b')
EV=re.compile(r'\b(survey(?:ed)?|respond(?:ed|ents?)|responses?|n\s?=\s?\d+|pilot|compared|comparison|control group|sections?|p\s?[<=]\s?0?\.\d+|\d+\s?%|\d+\s+percent|results? (?:show|indicate|suggest)|found that|assessment of|evaluat(?:ed|ion)|data (?:show|indicate)|study)\b',re.I)
NUM=re.compile(r'\d')
def fetch(u,t=30):
    f=C+hashlib.md5(u.encode()).hexdigest()
    if not os.path.exists(f):
        subprocess.run(['curl','-sL','-m',str(t),'-A','Mozilla/5.0 (research crawler; contact via heuremen.org)','--max-filesize','15000000','-o',f,u],capture_output=True); time.sleep(0.4)
    try: b=open(f,'rb').read()
    except Exception: return None
    return b
def text(b):
    if not b or len(b)<300: return None
    if b[:4]==b'%PDF':
        try:
            import pypdf; return ' '.join((p.extract_text() or '') for p in pypdf.PdfReader(io.BytesIO(b)).pages[:60])
        except Exception: return None
    s=b.decode('utf-8','ignore')
    if re.search(r'Just a moment|Attention Required|403 Forbidden|Access Denied',s[:4000]): return None
    s=re.sub(r'(?s)<(script|style|nav|footer|header).*?</\1>','',s); return html.unescape(re.sub(r'<[^>]+>',' ',s))
def urls_for(d):
    found=set(); base='https://'+d
    for sm in [base+'/sitemap.xml',base+'/sitemap_index.xml',base+'/wp-sitemap.xml']:
        b=fetch(sm,20)
        if not b: continue
        s=b.decode('utf-8','ignore'); locs=re.findall(r'<loc>\s*([^<\s]+)\s*</loc>',s)
        kids=[l for l in locs if l.endswith('.xml')][:25]
        for l in locs:
            if not l.endswith('.xml') and AIURL.search(l): found.add(l)
        for k in kids:
            kb=fetch(k,20)
            if kb:
                for l in re.findall(r'<loc>\s*([^<\s]+)\s*</loc>',kb.decode('utf-8','ignore')):
                    if not l.endswith('.xml') and AIURL.search(l): found.add(l)
        if found: break
    for path in ['/ai','/ai/','/genai','/gen-ai','/generative-ai','/artificial-intelligence','/academics/ai','/academics/artificial-intelligence','/teaching/ai','/ctl/ai','/teaching-and-learning/ai','/library/ai','/its/ai','/technology/ai','/provost/ai','/academic-affairs/ai','/about/ai','/ai-at-'+d.split('.')[0]]:
        b=fetch(base+path,20)
        if b and len(b)>1500 and b[:4]!=b'%PDF':
            t0=b.decode('utf-8','ignore')
            if not re.search(r'Just a moment|Attention Required|403 Forbidden|Access Denied|404|Page not found',t0[:3000]):
                found.add(base+path)
                for l in re.findall(r'href="([^"#?]+)"',t0):
                    if l.startswith('/'): l=base+l
                    if l.startswith(base) and AIURL.search(l) and not re.search(r'\.(jpg|png|css|js|gif)$',l): found.add(l)
    for q in ['generative%20AI%20survey','artificial%20intelligence%20results']:
        b=fetch(base+'/wp-json/wp/v2/search?per_page=20&search='+q,20)
        if b:
            try:
                for it in json.loads(b.decode('utf-8','ignore')):
                    if isinstance(it,dict) and it.get('url'): found.add(it['url'])
            except Exception: pass
    return sorted(found)
def sentences(t):
    t=re.sub(r'\s+',' ',t); return re.split(r'(?<=[.!?])\s+(?=[A-Z“"])',t)
def job(d):
    res={'domain':d,'urls':0,'fetched':0,'failed':0,'hits':[]}
    try:
        us=urls_for(d); res['urls']=len(us)
        for u in us[:25]:
            t=text(fetch(u))
            if t is None: res['failed']+=1; continue
            res['fetched']+=1
            n=0
            for s in sentences(t):
                if 40<len(s)<500 and AIW.search(s) and EV.search(s) and NUM.search(s):
                    res['hits'].append({'url':u,'s':s}); n+=1
                    if n>=6: break
    except Exception as e: res['err']=str(e)[:120]
    return res
if __name__=='__main__':
    doms=[l.strip() for l in open(OUT+'domains.txt') if l.strip() and not l.startswith('#')]
    h=open(OUT+'hits.jsonl','w'); cov={}
    with Pool(4) as p:
        for r in p.imap_unordered(job,doms):
            cov[r['domain']]={k:r[k] for k in ('urls','fetched','failed')}|({'err':r['err']} if 'err' in r else {})
            for x in r['hits']: h.write(json.dumps({'domain':r['domain'],**x})+'\n')
            h.flush(); print(r['domain'],r['urls'],r['fetched'],r['failed'],len(r['hits']),flush=True)
    json.dump(cov,open(OUT+'coverage.json','w'),indent=0)
