import json,re,html,collections,os
B='/Users/heuremen/bones-forge/'
D=B+'oy_index/smallpass/'
ids=[l.strip().rsplit('/',1)[1] for l in open(B+'watch/site_pass_20261030/lane_F_urls.txt')]
S={s['unitid']:s for s in json.load(open(B+'oy_index/schools.json'))}
REACH=json.load(open(B+'oy_index/reach.json'))
HR=json.load(open(B+'oy_index/HANDREAD.json'))
# raw logs
logs=collections.defaultdict(list)
for lf in ('run3a.log','run_fast.log','run_www.log','run_retry.log','run3.log','run.log','run2.log','run22.log'):
    p=D+lf
    if not os.path.exists(p): continue
    for l in open(p):
        m=re.match(r'^([\w.-]+\.\w+) (\d+) (\d+) (\d+) (\d+)$',l.strip())
        if m: logs[re.sub(r'^www\.','',m.group(1))].append((lf,)+tuple(int(x) for x in m.groups()[1:]))
hits=collections.defaultdict(list)
for hf in ('hits_p3a.jsonl','hits_fast.jsonl','hits_www.jsonl','hits_retry.jsonl'):
    for l in open(D+hf):
        try:x=json.loads(l)
        except: continue
        hits[re.sub(r'^www\.','',x['domain'])].append((x['url'],x['s'][:320],x['s'],hf))
crs=collections.defaultdict(list)
for cf in ('courses.jsonl','courses_retry.jsonl'):
    for l in open(D+cf):
        try:x=json.loads(l)
        except: continue
        crs[x['domain']].append((x['url'],x['line'],cf))
out=collections.defaultdict(list)
def add(i,k,v): out[k].append((i,v))
for i in ids:
    raw=open(f'pages/{i}.html',encoding='utf-8').read()
    s=S[i]
    main=re.search(r'<main class="wrap">(.*?)</main>',raw,re.S).group(1)
    d=s['domain']; dn=re.sub(r'^www\.','',d)
    # header fields
    m=re.search(r'<p class="meta">(.*?) &middot; (\w\w) &middot; <a href="/oy">All schools</a></p>',main)
    carn,st=html.unescape(m.group(1)),m.group(2)
    if carn!=s['carnegie'] or st!=s['state']: add(i,'carn/state',(carn,st,s['carnegie'],s['state']))
    sm=re.search(r'<h2>School</h2><p>(.*?)\. Private nonprofit\. Site: <a href="https://(.*?)">(.*?)</a>\. Federal ID (\d+)\.',main)
    if html.unescape(sm.group(1))!=s['school'] or sm.group(2)!=d or sm.group(3)!=d or sm.group(4)!=i: add(i,'school-line',sm.groups())
    # N pages
    n=re.search(r'<h2>Site</h2><p>(.*?)\.</p>',main).group(1)
    nm=re.search(r'Read by script \((\d+) pages\)',n)
    L=logs.get(dn,[])
    if s['site_read']=='yes':
        N=int(nm.group(1)); mx=max([x[2] for x in L]) if L else None
        if N!=mx: add(i,'pages!=log-max',(N,L))
        if N!=s['pages_fetched']: add(i,'pages!=json',(N,s['pages_fetched']))
        # also check disagreement between logs
        fs=set(x[2] for x in L)
        if len(fs)>1: add(i,'logs-disagree',L)
        if N==25: add(i,'cap25',N)
        if N==1: add(i,'one-page',N)
    else:
        mx=max([x[2] for x in L]) if L else None
        add(i,'readstate-'+s['site_read'],(n,L,REACH.get(dn) or REACH.get(d)))
    # sentences
    items=re.findall(r'<li>(.*?) <a href="(.*?)">Source</a></li>',re.search(r'<h2>Sentences on the school&rsquo;s own pages</h2>(.*?)<h2>Course titles',main,re.S).group(1),re.S)
    seen=set(); uniq=[]
    for (u,s320,sfull,hf) in hits.get(dn,[]):
        k=s320[:80]
        if k in seen: continue
        seen.add(k); uniq.append((u,s320,sfull,hf))
    if len(uniq)!=s['sentences_total']: add(i,'sentences_total!=raw',(len(uniq),s['sentences_total']))
    if len(items)!=min(6,len(uniq)): add(i,'sentence-count',(len(items),len(uniq)))
    for (t,u),(ru,r320,rfull,hf) in zip(items,uniq[:6]):
        t_un=html.unescape(t); u_un=html.unescape(u)
        if t_un!=r320 or u_un!=ru: add(i,'sentence-mismatch',(t_un[:80],r320[:80],u_un,ru))
        if len(rfull)>320: add(i,'sentence-truncated',(len(rfull),i))
    if len(uniq)>6: add(i,'sentences-capped',(len(uniq),6))
    # courses
    cm=re.search(r'<h2>Course titles in the public catalog</h2>(.*)',main,re.S).group(1)
    citems=re.findall(r'<li>(.*?) <a href="(.*?)">Source</a></li>',cm,re.S)
    # reconstruct filter from build_schools
    KEY2=re.compile(r'(artificial intelligence|machine learning|(?<![-\w])AI(?![-\w])|data ethics|ethics of (?:technology|data|AI|artificial)|technology (?:and|&) (?:society|ethics|human)|science,? technology,? (?:and|&) society|digital humanities|algorithm(?:s|ic)? (?:and|&|bias|justice)|ethics (?:and|&|of) (?:emerging )?tech|human[- ]computer|computational (?:social|thinking|ethics)|critical (?:data|digital|media) (?:studies|literacy)|surveillance|big data|data science|robot(?:s|ics)? (?:and|&) |philosophy of (?:mind|technology|computation)|generative)',re.I)
    def okline(l): return bool(KEY2.search(l)) and '@' not in l and not re.search(r'\d{3}[.\- ]\d{3}[.\- ]\d{4}',l) and len(l)<=170
    seenc=set(); cu=[]
    for (u,l,cf) in crs.get(d,[]):
        if not okline(l) or l in seenc: continue
        seenc.add(l); cu.append((u,l))
    if len(cu)!=s['courses_total']: add(i,'courses_total!=raw',(len(cu),s['courses_total']))
    if len(citems)!=min(12,len(cu)): add(i,'course-count',(len(citems),len(cu)))
    for (t,u),(ru,rl) in zip(citems,cu[:12]):
        if html.unescape(t)!=rl or html.unescape(u)!=ru: add(i,'course-mismatch',(html.unescape(t),rl,u,ru))
    if len(cu)>12: add(i,'courses-capped',(len(cu),12))
    # catalog statement
    if s['catalog']=='readable' and not citems and 'None matched in the catalog pages the script read.' not in cm: add(i,'catalog-text',cm[:100])
    # hand
    hm=re.search(r'<h2>Read by hand</h2><p><b>(.*?)\.</b> (.*?) Read 28 October 2026\.</p>',main,re.S)
    if i in HR:
        if not hm: add(i,'hand-missing',i)
        else:
            if html.unescape(hm.group(1))!=HR[i]['label'] or html.unescape(hm.group(2))!=HR[i]['note']: add(i,'hand-mismatch',(hm.groups(),HR[i]))
            if HR[i]['school']!=s['school']: add(i,'hand-school-name',(HR[i]['school'],s['school']))
    elif hm: add(i,'hand-extra',i)
for k,v in sorted(out.items()):
    print(k,len(v),v[:4] if not k.startswith('readstate') else '')
json.dump(out,open('part2.json','w'),default=str,indent=0)
