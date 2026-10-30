"""build_schools.py: one record per roster school (27 Oct 2026) -> schools.json. Sources: smallpass/ROSTER.csv + ROSTER22.csv (IPEDS HD2024), the crawl logs and hits files, courses.jsonl.
Counts what the scripts read and found. Nothing here is a hand-read verdict. Run with python3."""
import csv,json,re,os,glob,collections
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'smallpass')+'/'
roster=[]
for f,cls in (('ROSTER.csv','Arts & Sciences focus'),('ROSTER22.csv','Diverse fields')):
    for r in csv.reader(l for l in open(D+f) if not l.startswith('#')):
        if r[2]!='domain': roster.append(dict(school=r[0],state=r[1],domain=r[2],unitid=r[3],carnegie=cls))
cov={}
for lf in ('run3a.log','run_fast.log','run_www.log','run_retry.log'):
    if os.path.exists(D+lf):
        for l in open(D+lf):
            m=re.match(r'^([\w.-]+\.\w+) (\d+) (\d+) (\d+) (\d+)$',l.strip())
            if m:
                dm=re.sub(r'^www\.','',m.group(1))
                if dm in cov and cov[dm]['fetched']>int(m.group(3)): continue
                cov[dm]=dict(urls=int(m.group(2)),fetched=int(m.group(3)),failed=int(m.group(4)),hits=int(m.group(5)))
hits=collections.defaultdict(list)
for hf in ('hits_p3a.jsonl','hits_fast.jsonl','hits_www.jsonl','hits_retry.jsonl'):
    if os.path.exists(D+hf):
        for l in open(D+hf):
            try: x=json.loads(l)
            except Exception: continue
            hits[re.sub(r'^www\.','',x['domain'])].append(dict(url=x['url'],sentence=x['s'][:320],cut=len(x['s'])>320))
KEY2=re.compile(r'(artificial intelligence|machine learning|(?<![-\w])AI(?![-\w])|data ethics|ethics of (?:technology|data|AI|artificial)|(?<![A-Za-z])technology (?:and|&) (?:society|ethics|human)|science,? technology,? (?:and|&) society|digital humanities|algorithm(?:s|ic)? (?:bias|justice|fairness|accountability)|algorithms? (?:and|&) (?:society|bias|justice|ethics|power)|ethics (?:and|&|of) (?:emerging )?tech|human[- ]computer|computational (?:social|thinking|ethics)|critical (?:data|digital|media) (?:studies|literacy)|surveillance|big data|data science|robot(?:s|ics)? (?:and|&) |philosophy of (?:mind|technology|computation)|\bgenerative (?:AI|artificial|models?|text|tools?|systems?))',re.I)
# 30 Oct 2026 site pass (F-1, F-2, F-4, F-5, F-7, F-14): rows the script found that are not what the page says they are. Each filter
# counts what it drops, by reason, per school (core I: count what the gate drops).
SCODE=re.compile(r'[{}]|=>|response\.|function\s*\(|\bvar\s|\bconst\s')
SFURN=re.compile(r'Skip to (?:main|content|footer)|Skip Sub Navigation|Accept Reject|Ok, I agree|cookie|-->|section of webpage',re.I)
SCONTACT=re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+|\(?\d{3}\)?[.\- ]\d{3}[.\- ]\d{4}')
SAI_CLEAR=re.compile(r'\b(AI|A\.I\.|ChatGPT|chatbots?|large language|language models?|Copilot|artificial intelligence)\b|\bgenerative (?:AI|artificial|models?|tools?)',re.I)
SPERSON=re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+ ['\u2019]\d\d\b|\bBy: ")
SRELIG=re.compile(r'\bPope\b')
CDESC=re.compile(r'\b(?:This course|course (?:introduces|provides|covers|explores|examines|focuses)|Topics include|Prerequisites?|students will|must complete|In addition)\b',re.I)
CCODE=re.compile(r'\b[A-Z]{2,5}[- ]?[A-Z]?\d{3,4}[A-Z]?\b')
def sdrop(s):
    if SCODE.search(s): return 'page code'
    if SFURN.search(s): return 'menu or banner text'
    if SCONTACT.search(s): return 'contact details'
    if not SAI_CLEAR.search(s): return 'AI word that means something else here (LLM law degree, Gemini, Claude)'
    if SPERSON.search(s): return 'names a student'
    if SRELIG.search(s): return 'religious text'
    return None
def cdrop(l):
    if re.match(r'^PAGE \d',l): return 'page header'
    if CDESC.search(l): return 'course description, not a title'
    if re.search(r'\b\d{1,2}:\d{2}\b|\b(?:MWF|TTh|MW|TR)\b|\bRoom\b',l): return 'class schedule or room row'
    if len(CCODE.findall(l))>=2: return 'several course codes in one line'
    if len(l)>110: return 'longer than a title'
    return None
def catyear(u):
    m=re.search(r'(20\d\d)\s*[-_\u2013]\s*(?:20)?(\d\d)(?!\d)',u) or re.search(r'(?<![\d])(\d\d)[-_](\d\d)[-_]?[Cc]atalog',u)
    if not m: return None
    a=m.group(1); a=a if len(a)==4 else '20'+a
    return f"{a}-{m.group(2)}"
SENTCUT=re.compile(r'(?:\b[A-Z]|\bDr|\bMr|\bMrs|\bMs|\bSt|\bProf|\bNo|(?<![\d.])\d{1,2})\.$')
def okline(l):
    return bool(KEY2.search(l)) and '@' not in l and not re.search(r'\d{3}[.\- ]\d{3}[.\- ]\d{4}',l) and len(l)<=170
courses=collections.defaultdict(list); ccov={}
REACH=json.load(open(os.path.dirname(os.path.abspath(__file__))+'/reach.json')) if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/reach.json') else {}
for cf in ('courses.jsonl','courses_retry.jsonl'):
  if os.path.exists(D+cf):
    for l in open(D+cf):
        try: x=json.loads(l)
        except Exception: continue
        if okline(x['line']): courses[x['domain']].append(dict(url=x['url'],line=x['line']))
for cl in ('run_courses.log','run_courses_retry.log'):
  if os.path.exists(D+cl):
    for l in open(D+cl):
        m=re.match(r'^([\w.-]+\.\w+) (\d+) (\d+) (\d+)$',l.strip())
        if m and (m.group(1) not in ccov or ccov[m.group(1)]['course_lines']<int(m.group(3))): ccov[m.group(1)]=dict(pages=int(m.group(2)),course_lines=int(m.group(3)),matches=int(m.group(4)))
HR=json.load(open(os.path.dirname(os.path.abspath(__file__))+'/HANDREAD.json')) if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/HANDREAD.json') else {}
# 30 Oct 2026 site pass: names as the schools write them (F-9, F-10), working site links (F-8), canonical source URLs (F-15),
# rows whose start was cut by the sentence splitter (F-7), read dates from the run logs (F-13).
NAME_FIX={'174792':"Saint John's University",'198756':'Johnson C. Smith University','174844':'St. Olaf College','195216':'St. Lawrence University','239716':'St. Norbert College','234173':'Batten University'}
NAME_NOTE={'234173':'Listed in the federal directory as Virginia Wesleyan University. Its old address vwu.edu now forwards to batten.edu.'}
SITE_FIX={'229267':'https://trinity.edu','174844':'https://www.stolaf.edu'}
LINKS=json.load(open(D+'site_links.json')) if os.path.exists(D+'site_links.json') else {}
URL_FIX={'https://live-smithcolleged9-4k.pantheonsite.io/discover-smith/governance/compass-2035/ai-smith-art-inquiry/students':'https://www.smith.edu/discover-smith/governance/compass-2035/ai-smith-art-inquiry/students'}
CUT_START=set(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'cut_start.json')))) if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)),'cut_start.json')) else set()
import datetime as _dt
_lt=[os.path.getmtime(D+f) for f in ('run3a.log','run_fast.log','run_www.log','run_retry.log','run_courses.log','run_courses_retry.log') if os.path.exists(D+f)]
_ds=sorted({_dt.datetime.fromtimestamp(x,_dt.timezone.utc).strftime('%-d %B %Y') for x in _lt})
READ_ON=' and '.join(_ds)+' (UTC, when each read finished)'
out=[]
for s in roster:
    d=s['domain']; c=cov.get(d); cc=ccov.get(d)
    seen=set(); hs=[]; drops=collections.Counter()
    for h in hits.get(d,[]):
        k=h['sentence'][:80]
        if k in seen: continue
        seen.add(k)
        why=sdrop(h['sentence'])
        if why: drops['sentence: '+why]+=1; continue
        h=dict(h); h['url']=URL_FIX.get(h['url'],h['url']); h['cut_end']=bool(h.get('cut') or SENTCUT.search(h['sentence'].strip())); h['cut_start']=(h['url']+'|'+h['sentence'].strip()[:40] in CUT_START) or h['sentence'].strip()[:1].islower()
        hs.append(h)
    cs=[];seenc=set()
    for h in courses.get(d,[]):
        if h['line'] in seenc: continue
        seenc.add(h['line'])
        why=cdrop(h['line'])
        if why: drops['course: '+why]+=1; continue
        ln=re.split(r'\s\((?:\.\d+|\d+(?:\.\d+)?)(?:\s*-\s*\d+)?\)',h['line'])[0].strip()   # keep the title, drop a credits note and the description after it
        cs.append(dict(h,line=ln,year=catyear(h['url'])))
    norm=lambda x: re.sub(r'[^a-z0-9]','',x.lower())
    keep=[]
    for h in cs:
        n=norm(h['line'])
        if any(norm(k['line'])==n for k in keep): drops['course: repeat of another row']+=1; continue
        if any(norm(o['line'])!=n and norm(o['line']).startswith(n) for o in cs): drops['course: cut copy of another row']+=1; continue
        keep.append(h)
    yrs=[h['year'] for h in keep if h['year']]
    if yrs:
        newest=max(yrs); old=[h for h in keep if h['year'] and h['year']<newest]
        if old: drops['course: from an older catalog']+=len(old); keep=[h for h in keep if not (h['year'] and h['year']<newest)]
    cs=keep
    s['ipeds_name']=s['school']; s['school']=NAME_FIX.get(s['unitid'],s['school'])
    s['site_link']=SITE_FIX.get(s['unitid']) or (LINKS.get(d,{}).get('link') or 'https://'+d)
    s['shared_with']=[o['school'] for o in roster if o['domain']==d and o['unitid']!=s['unitid']]
    s['dropped']=dict(drops); s['read_on']=READ_ON
    _L=LINKS.get(d,{}); s['answers_now']=next((v for v in (_L.get('bare'),_L.get('www')) if v and not v.startswith('fail')),None)
    s['pages_failed']=c['failed'] if c else None
    s.update(site_read=('yes' if c and c['fetched']>0 else (('reached' if REACH.get(d,{}).get('reached') else 'not reached') if c else 'pending')),pages_fetched=c['fetched'] if c else None,ai_urls=c['urls'] if c else None,
             sentences=hs[:6],sentences_total=len(hs),courses=cs[:12],courses_total=len(cs),catalog_pages=cc['pages'] if cc else None,catalog_course_lines=cc['course_lines'] if cc else None,
             catalog='pending' if not cc else ('readable' if cc['course_lines']>0 else 'not readable by script'))
    s['hand']=HR.get(s['unitid']); s['name_note']=NAME_NOTE.get(s['unitid'])
    out.append(s)
json.dump(out,open(os.path.dirname(os.path.abspath(__file__))+'/schools.json','w'))
alld=collections.Counter()
for s in out: alld.update(s['dropped'])
print('dropped by reason:',dict(alld)); print('read on:',READ_ON)
st=collections.Counter(s['site_read'] for s in out); print(len(out),dict(st),'with sentences',sum(1 for s in out if s['sentences']),'catalog',dict(collections.Counter(s['catalog'] for s in out)),'course matches',sum(s['courses_total'] for s in out))
