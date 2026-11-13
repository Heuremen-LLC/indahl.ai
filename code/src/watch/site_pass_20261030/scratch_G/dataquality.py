import json,re,collections
O='/Users/heuremen/bones-forge/oy_index/'
S=json.load(open(O+'schools.json'))
ids=[l.strip().split('/')[-1] for l in open('../lane_G_urls.txt') if '/school/' in l]
mine={s['unitid']:s for s in S if s['unitid'] in ids}
AIW=re.compile(r'\b(AI|A\.I\.|generative|ChatGPT|chatbot|large language|LLM|Copilot|Gemini|Claude)\b')
EV=re.compile(r'\b(survey(?:ed)?|respond(?:ed|ents?)|responses?|n\s?=\s?\d+|pilot|compared|comparison|control group|sections?|p\s?[<=]\s?0?\.\d+|\d+\s?%|\d+\s+percent|results? (?:show|indicate|suggest)|found that|assessment of|evaluat(?:ed|ion)|data (?:show|indicate)|study)\b',re.I)
nsent=0; trunc=[]; boiler=[]; lead=[]; noshow=[]; noai=[]; ev_words=collections.Counter(); amp=[]
BOIL=re.compile(r'(Skip to|Toggle|Menu|Open Search|Search Web|Home About|\| .{3,60} \| |Facebook|Twitter|Instagram|Cookie|Sign In|Log ?in\b|Back to top|Quick Links|Apply Now|Request Info)',re.I)
for u,s in mine.items():
    for h in s['sentences']:
        t=h['sentence']; nsent+=1
        if len(t)>=319: trunc.append((u,s['school'],len(t),t[-60:]))
        if BOIL.search(t): boiler.append((u,s['school'],t[:140]))
        if t!=t.strip(): lead.append((u,s['school']))
        if not AIW.search(t): noai.append((u,s['school'],t[:120]))
        if not (EV.search(t) and re.search(r'\d',t)): noshow.append((u,s['school'],t[:150]))
print('lane sentences',nsent,'schools with',sum(1 for s in mine.values() if s['sentences']))
print('trunc at ~320:',len(trunc))
for x in trunc[:50]: print('  ',x)
print('boilerplate-like:',len(boiler))
for x in boiler: print('  ',x)
print('leading/trailing space:',len(lead))
print('no AI word visible in displayed text:',len(noai))
for x in noai: print('  ',x)
print('displayed text lacks digit or evidence token:',len(noshow))
for x in noshow: print('  ',x)
# sentences_total vs shown cap
cap=[(u,s['school'],s['sentences_total']) for u,s in mine.items() if s['sentences_total']>6]
print('sentences_total>6:',cap)
cc=[(u,s['school'],s['courses_total']) for u,s in mine.items() if s['courses_total']>12]
print('courses_total>12:',cc)
# mismatches site_read vs content
print('sentences but not read=yes:',[(u,s['school'],s['site_read'],len(s['sentences'])) for u,s in mine.items() if s['sentences'] and s['site_read']!='yes'])
print('courses but catalog not readable:',[(u,s['school'],s['catalog'],len(s['courses'])) for u,s in mine.items() if s['courses'] and s['catalog']!='readable'])
print('catalog readable, courses 0, course_lines:',collections.Counter((s['catalog'],bool(s['courses'])) for s in mine.values()))
print('site yes but pages_fetched==0:',[u for u,s in mine.items() if s['site_read']=='yes' and not s['pages_fetched']])
print('site not yes but pages_fetched>0:',[(u,s['pages_fetched']) for u,s in mine.items() if s['site_read']!='yes' and s['pages_fetched']])
