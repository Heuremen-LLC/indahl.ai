import json,re,html,collections,os,sys
from html.parser import HTMLParser
B='/Users/heuremen/bones-forge/'
ids=[l.strip().rsplit('/',1)[1] for l in open(B+'watch/site_pass_20261030/lane_F_urls.txt')]
S={s['unitid']:s for s in json.load(open(B+'oy_index/schools.json'))}
REACH=json.load(open(B+'oy_index/reach.json'))
VOID={'meta','link','br','hr','img','input','source','area','base','col','embed','param','track','wbr','polygon','circle','path'}
class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=False); s.stack=[];s.err=[];s.links=[];s.text=[];s.inmain=False;s.tags=collections.Counter()
        s.cur_a=None
    def handle_starttag(s,t,a):
        s.tags[t]+=1
        if t not in VOID: s.stack.append(t)
        if t=='main': s.inmain=True
        if t=='a':
            d=dict(a); s.links.append([d.get('href'),'',s.inmain]); s.cur_a=s.links[-1]
    def handle_startendtag(s,t,a): s.handle_starttag(t,a); 
    def handle_endtag(s,t):
        if t in VOID: return
        if t=='a': s.cur_a=None
        if t=='main': s.inmain=False
        if not s.stack or s.stack[-1]!=t:
            s.err.append(f'end </{t}> with stack top {s.stack[-1] if s.stack else None}')
            if t in s.stack:
                while s.stack and s.stack.pop()!=t: pass
        else: s.stack.pop()
    def handle_data(s,d):
        if s.inmain: s.text.append(d)
        if s.cur_a is not None: s.cur_a[1]+=d
    def handle_entityref(s,n):
        s.handle_data('&'+n+';')
    def handle_charref(s,n): s.handle_data('&#'+n+';')
res={}
for i in ids:
    raw=open(f'pages/{i}.html',encoding='utf-8').read()
    p=P(); p.feed(raw); p.close()
    m=re.search(r'<main class="wrap">(.*?)</main>',raw,re.S)
    main=m.group(1) if m else ''
    res[i]=dict(unclosed=p.stack,err=p.err,nlinks=len(p.links))
    res[i]['raw']=raw
print('pages',len(res))
bad=[(i,r['unclosed'],r['err'][:2]) for i,r in res.items() if r['unclosed'] or r['err']]
print('tag-balance faults',len(bad),bad[:5])
# page structure check vs expected template
faults=collections.defaultdict(list)
def add(i,k,v): faults[k].append((i,v))
for i in ids:
    raw=res[i]['raw']; s=S[i]
    m=re.search(r'<main class="wrap">(.*?)</main>',raw,re.S)
    main=m.group(1)
    title=re.search(r'<title>(.*?)</title>',raw).group(1)
    h1=re.search(r'<h1>(.*?)</h1>',raw).group(1)
    nm=html.escape(s['school'])
    if html.unescape(title)!=f"{s['school']} | OY | Heuremen LLC": add(i,'title',title)
    if html.unescape(h1)!=s['school']: add(i,'h1',h1)
    # raw template markers
    txt=re.sub(r'<[^>]+>',' ',main)
    for pat in [r'\{',r'\}',r'undefined',r'\bNaN\b',r'\bnull\b',r'\bNone\b',r'\[object',r'&amp;amp;',r'&amp;#',r'%s',r'â€',r'Ã.',r'\ufffd',r'\\n',r'\\u00',r'\bTODO\b',r'\{\{']:
        if re.search(pat,txt): add(i,'marker:'+pat,re.search(pat,txt).group(0))
    if '@' in txt: add(i,'at-sign',[w for w in txt.split() if '@' in w][:3])
    if ';' in re.sub(r'&[#\w]+;','',txt): add(i,'semicolon',[m_.group(0) for m_ in re.finditer(r'.{25};.{25}',re.sub(r'&[#\w]+;','',txt))][:2])
    # count of h2, structure
    h2=re.findall(r'<h2>(.*?)</h2>',main)
    add(i,'h2seq','|'.join(h2))
    if len(re.findall(r'<li>',main))!=len(s['sentences'])+len(s['courses']): add(i,'li-count',(len(re.findall(r'<li>',main)),len(s['sentences']),len(s['courses'])))
for k,v in faults.items():
    if k=='h2seq':
        print(k,collections.Counter(x[1] for x in v).most_common())
    else: print(k,len(v),v[:6])
json.dump({k:v for k,v in faults.items()},open('part1_faults.json','w'),default=str)
