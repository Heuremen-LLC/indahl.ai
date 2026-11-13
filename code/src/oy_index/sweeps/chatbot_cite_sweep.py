"""Fetch every source URL in rows/*.md and grep for a chatbot cited as a source. Downloads go to a scratch dir; nothing is executed.
Output: sweeps/chatbot_cite_hits.jsonl (one line per hit) + sweeps/chatbot_cite_coverage.json (fetched / failed counts per row)."""
import re,glob,os,json,hashlib,subprocess,io,html,sys
from multiprocessing import Pool
ROWS=os.path.expanduser('~/bones-forge/oy_index/rows'); OUT=os.path.expanduser('~/bones-forge/oy_index/sweeps')
D='/private/tmp/claude-501/-Users-heuremen/80087010-0cb3-4ae5-9e13-362e6d5086ad/scratchpad/dl_chatbot_sweep'; os.makedirs(D,exist_ok=True)
PAT=re.compile(r'\((?:ChatGPT|OpenAI|Claude|Anthropic|Gemini|Google Bard|Bard|Copilot|Microsoft Copilot)[^()]{0,60}(?:19|20)\d\d[^()]{0,30}\)|\[Large language model\]|\[Generative AI chat\]|According to (?:ChatGPT|Claude|Gemini|Copilot|Bard)|(?:ChatGPT|OpenAI)\.? \((?:20)\d\d[^)]*\)\.?\s*ChatGPT|personal communication[^.]{0,40}(?:ChatGPT|OpenAI)',re.I)
SKIP=re.compile(r'\.(png|jpe?g|gif|mp4|zip|xlsx?|docx?|pptx?)(\?|$)|doi\.org|sciencedirect|springer|wiley|tandfonline|acm\.org|ieee|jstor|arxiv\.org|nature\.com|mdpi|frontiersin|youtube|google\.com/(document|presentation)|sharepoint|box\.com/s/|instagram|facebook|twitter|x\.com|linkedin',re.I)
def text(u):
    f=os.path.join(D,hashlib.md5(u.encode()).hexdigest())
    if not os.path.exists(f): subprocess.run(['curl','-sL','-m','45','-A','Mozilla/5.0','--max-filesize','30000000','-o',f,u],capture_output=True)
    if not os.path.exists(f): return None
    b=open(f,'rb').read()
    if len(b)<500: return None
    if b[:4]==b'%PDF':
        try:
            import pypdf; return ' '.join((p.extract_text() or '') for p in pypdf.PdfReader(io.BytesIO(b)).pages)
        except Exception: return None
    s=b.decode('utf-8','ignore')
    if re.search(r'403 Forbidden|Access Denied|Just a moment',s[:3000]): return None
    s=re.sub(r'(?s)<(script|style).*?</\1>','',s); return html.unescape(re.sub(r'<[^>]+>',' ',s))
def job(a):
    slug,u=a
    try: t=text(u)
    except Exception: t=None
    if t is None: return slug,u,None
    t=re.sub(r'\s+',' ',t)
    return slug,u,[t[max(0,m.start()-250):m.end()+150] for m in PAT.finditer(t)][:10]
if __name__=='__main__':
    work=[]
    for f in sorted(glob.glob(ROWS+'/*.md')):
        slug=os.path.basename(f)[:-3]
        if slug=='SCHOOL_LIST': continue
        urls=sorted(set(u.rstrip('.,;:') for u in re.findall(r'https?://[^\s)|>"\]]+',open(f).read())))
        work+=[(slug,u) for u in urls if not SKIP.search(u)]
    cov={}; hits=open(OUT+'/chatbot_cite_hits.jsonl','w')
    with Pool(4) as p:
        for slug,u,h in p.imap_unordered(job,work):
            c=cov.setdefault(slug,{'fetched':0,'failed':0})
            if h is None: c['failed']+=1; continue
            c['fetched']+=1
            for x in h: hits.write(json.dumps({'slug':slug,'url':u,'ctx':x})+'\n'); hits.flush()
    json.dump({'urls':len(work),'per_row':cov},open(OUT+'/chatbot_cite_coverage.json','w'),indent=0)
    print('urls',len(work),'fetched',sum(c['fetched'] for c in cov.values()),'failed',sum(c['failed'] for c in cov.values()))
