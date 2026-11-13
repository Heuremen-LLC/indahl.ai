# Referee step 2: independent recompute. Shares no code with rank_index/.
import json, re, sys, os
from decimal import Decimal, ROUND_HALF_UP
sys.path.insert(0, os.path.dirname(__file__))
import xl
R=os.path.expanduser('~/bones-forge/rank_index/')
OUT=os.path.expanduser('~/bones-forge/rank_index_referee/step2/out/')
def rnd(x, dp):
    q=Decimal(1).scaleb(-dp)
    return Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP)
def judge(usn, pub):
    """usn: printed string. pub: float or marker string. returns outcome, reason, pubnum"""
    if usn is None or usn in ('N/A','A/V'): return 'CANNOT_TELL','not_printed'
    if pub is None: return 'CANNOT_TELL','not_found'
    s=usn.replace(',','').replace('%','').strip()
    if isinstance(pub,str):
        p=pub.replace('%','').replace(' ','')
        if p in ('*','**','DS','TFS'): return 'CANNOT_TELL','suppressed'
        if p.startswith('>'):
            if s.replace(' ','').startswith('>') and s.replace(' ','')[1:]==p[1:]: return 'MATCH',''  # same bin printed both sides
            return 'CANNOT_TELL','binned_public'
    if s.startswith('>'):
        fl=float(s[1:]); return ('MATCH','') if float(pub)>fl else ('MISMATCH','')
    dp=len(s.split('.')[1]) if '.' in s else 0
    return ('MATCH','') if rnd(pub,dp)==Decimal(s) else ('MISMATCH','')
rows=[]
def add(lst,school,field,usn,uy,pub,py,outcome=None,reason='',note=''):
    if outcome is None:
        if uy is None: outcome,reason='CANNOT_TELL','year'
        elif py is not None and uy!=py: outcome,reason='CANNOT_TELL','year'
        else: outcome,reason=judge(usn,pub)
    rows.append(dict(list=lst,school=school,field=field,usn=usn,usn_year=uy,pub=pub,pub_year=py,outcome=outcome,reason=reason,note=note))

# ---------- HS: US News side from raw ----------
usn={}
for line in open(R+'raw/hs_schoolpages_20261110.txt'):
    if '::' not in line: continue
    name,score,econ,_=[x.strip() for x in line.split('::')]
    d={}
    for part in score.split('|'):
        part=part.strip()
        m=re.match(r'(.*?)\s+(> ?\d+%|\d+%)$',part)
        if m: d[m.group(1).strip()]=m.group(2)
    for part in econ.split('|'):
        part=part.strip(); m=re.match(r'(.*?)\s+(\S+)$',part); d[m.group(1)]=m.group(2)
    usn[name]=d
enr={}
for line in open(R+'raw/hs_national_20261110.txt'):
    if line.startswith('#'):
        f=line.split(';'); enr[f[1]]=f[5]
hs=json.load(open(R+'public/hs_public.json'))
def ccd(s,fig,yr):
    for f in s['nces_ccd']:
        if f['figure']=='CCD '+fig and f['year']==yr: return f['value']
def st(s,i): return s['state_figures'][i]
# referee's own pick of public figure per school: (field, index into state_figures, parser) ; read by eye from the dump
def frac(v): return float(str(v).split()[0])*100
def first(v): return float(str(v).split()[0])
P={
 'Signature School':{'Graduation Rate':(8,frac,'class of 2024'),'Mathematics Proficiency':(1,frac,'2023-24'),'Reading Proficiency':(0,frac,'2023-24'),'Science Proficiency':(3,frac,'2023-24')},
 'Julia R. Masterman Secondary School':{'Graduation Rate':(6,frac,'class of 2024'),'Mathematics Proficiency':(0,first,'2023-24'),'Reading Proficiency':(2,first,'2023-24'),'Science Proficiency':(4,first,'2023-24')},
 'Davidson Academy':{'Graduation Rate':(3,lambda v:v,'2023-24 (class not stated)'),'Mathematics Proficiency':(0,lambda v:v,'2023-24'),'Reading Proficiency':(1,lambda v:v,'2023-24')},
 'School Without Walls High School':{'Graduation Rate':(11,lambda v:'>99','class of 2024'),'Reading Proficiency':(1,first,'2023-24'),'Science Proficiency':(7,first,'2023-24')},
 'Thomas Jefferson High School for Science and Technology':{'Graduation Rate':(8,first,'2023-24 (class not stated)'),'Mathematics Proficiency':(2,lambda v:float(re.search(r'Passed (\d+)',v).group(1)),'2023-24'),'Reading Proficiency':(0,lambda v:float(re.search(r'Passed (\d+)',v).group(1)),'2023-24'),'Science Proficiency':(6,lambda v:float(re.search(r'Passed (\d+)',v).group(1)),'2023-24')},
 'Gwinnett School of Mathematics, Science and Technology':{'Graduation Rate':(8,first,'class of 2024'),'Reading Proficiency':(2,lambda v:(int(re.search(r'Proficient_cnt=(\d+)',v).group(1))+int(re.search(r'Distinguished_cnt=(\d+)',v).group(1)))/int(re.search(r'tested=(\d+)',v).group(1))*100,'2023-24'),'Science Proficiency':(3,lambda v:(int(re.search(r'Proficient_cnt=(\d+)',v).group(1))+int(re.search(r'Distinguished_cnt=(\d+)',v).group(1)))/int(re.search(r'tested=(\d+)',v).group(1))*100,'2023-24')},
 'The School for the Talented and Gifted (TAG)':{'Graduation Rate':(10,first,'class of 2024'),'Reading Proficiency':(0,lambda v:float(re.search(r'Meets=(\d+)',v).group(1)),'2023-24'),'Science Proficiency':(4,lambda v:float(re.search(r'Meets=(\d+)',v).group(1)),'2023-24')},
 'Nikola Tesla Stem High School':{'Mathematics Proficiency':(0,frac,'2023-24'),'Reading Proficiency':(1,lambda v:'*','2023-24'),'Science Proficiency':(2,frac,'2023-24')},
 'Science Academy Stem Magnet':{'Graduation Rate':(6,first,'class of 2024'),'Mathematics Proficiency':(1,first,'2023-24'),'Reading Proficiency':(0,first,'2023-24'),'Science Proficiency':(2,first,'2023-24')},
 'Central Magnet School':{'Graduation Rate':(None,lambda v:'**','class of 2024'),'Reading Proficiency':(None,lambda v:'**','2023-24'),'Science Proficiency':(None,lambda v:'**','2023-24')},
}
def find(name):
    for s in hs:
        a=re.sub(r'[^a-z]','',s['school'].lower()); b=re.sub(r'[^a-z]','',name.lower())
        if a in b or b in a: return s
for name,d in usn.items():
    s=find(name); assert s, name
    for lab,(i,fn,py) in P[name].items():
        uy='class of 2024' if lab=='Graduation Rate' else '2023-24'
        pub=fn(st(s,i)['value'] if i is not None else None)
        u=d.get(lab)
        if py.endswith('(class not stated)'): add('hs',name,lab,u,uy,pub,py,'CANNOT_TELL','year')
        else: add('hs',name,lab,u,uy,pub,py)
    if 'Graduation Rate' not in d and 'Graduation Rate' not in P[name]:
        add('hs',name,'Graduation Rate',None,'class of 2024',None,None,'CANNOT_TELL','not_printed')
    for lab in ('Mathematics Proficiency','Reading Proficiency','Science Proficiency'):
        if lab not in d and lab not in P[name]: pass
    # enrollment 9-12, CCD 2024-25
    g=sum(ccd(s,'enrollment grade %d'%k,'2024-25') for k in (9,10,11,12))
    g23=sum(ccd(s,'enrollment grade %d'%k,'2023-24') for k in (9,10,11,12))
    add('hs',name,'Enrollment 9-12',enr[s['school'] if s['school'] in enr else name] if name in enr else None,'2024-25',g,'2024-25',note='2023-24 sum would be %d'%g23)
    tot=ccd(s,'enrollment','2024-25'); tot23=ccd(s,'enrollment','2023-24')
    for lab,fig in (('Free Lunch','free_lunch'),('Reduced-Price Lunch','reduced_price_lunch'),('Economically Disadvantaged','free_or_reduced_price_lunch')):
        c=ccd(s,fig,'2024-25'); c23=ccd(s,fig,'2023-24')
        pub=None if c is None or c<0 else c/tot*100
        alt='' if c23 is None or c23<0 else '2023-24 alt %.2f'%(c23/tot23*100)
        add('hs',name,lab,d.get(lab),'2024-25',pub,'2024-25',note=alt)

# ---------- LAW ----------
law={}
for line in open(R+'raw/law_pages_20261110.txt'):
    m=re.match(r'([a-z\-]+-\d+): (.*)',line)
    if m: law[m.group(1)]=[x.strip() for x in m.group(2).split('|')]
ABA={'stanford-university-03014':'Stanford University','university-of-chicago-03052':'Chicago, The University of','yale-university-03027':'Yale University','university-of-pennsylvania-03140':'Pennsylvania, University of','university-of-virginia-main-campus-03162':'Virginia, University of','harvard-university-03074':'Harvard University','duke-university-03117':'Duke University','new-york-university-03110':'New York University','columbia-university-03104':'Columbia University','northwestern-university-03050':'Northwestern University','university-of-michigan-ann-arbor-03082':'Michigan, University of'}
D=R+'public/law/downloads/'
def sheet(f): return list(xl.read(D+f).values())[0]
def byname(rows):
    h=rows[0]; return {r[0]:dict(zip(h,r)) for r in rows[1:] if r and r[0]}
fy=byname(sheet('comp509_2025_FirstYearClass.xlsx'))
ft=byname(sheet('bar_2025_First_Time_Bar_Passage.xlsx'))
u21=byname(sheet('bar_2024_Two-Year_Ultimate_Bar_Passage.xlsx'))
u22=byname(sheet('bar_2025_Two-Year_Ultimate_Bar_Passage.xlsx'))
def lk(tab,nm):
    if nm in tab: return tab[nm]
    c=[k for k in tab if k==nm]
    if len(c)!=1: raise KeyError((nm,c))
    return tab[c[0]]
for slug,v in law.items():
    nm=ABA[slug]; a=lk(fy,nm)
    gpa,lsat,acc,ftb,ult=v
    add('law',nm,'GPA median',gpa,'2025 entrants',float(a['All50thPercentileUGPA']),'2025 entrants')
    add('law',nm,'LSAT median',lsat,'2025 entrants',float(a['All50thPercentileLSAT']),'2025 entrants')
    add('law',nm,'Acceptance',acc,'2025 entrants',float(a['Offers'])/float(a['Applications'])*100,'2025 entrants',note='ABA printed %s'%a['AcceptanceRate'])
    f=lk(ft,nm); fv=float(f['AvgSchoolPassPercent*'].rstrip('%'))
    add('law',nm,'First-time bar',ftb,None,fv,'2024 graduates',note='2024 grads %.2f would be %s'%(fv,judge(ftb,fv)[0]))
    x21=float(lk(u21,nm)['%Passers'].rstrip('%')); x22=float(lk(u22,nm)['%Passers'].rstrip('%'))
    avg=(x21+x22)/2
    o=judge(ult,avg)[0]
    add('law',nm,'Ultimate bar 2-yr avg',ult,None,avg,'2021+2022 grads (referee: US News capture prints no year)',note='unweighted avg %.3f -> %s if year accepted; 2021 %.2f 2022 %.2f'%(avg,o,x21,x22))

# ---------- COLLEGES: enrollment vs CDS 2025-26 B1 ----------
cp=json.load(open(R+'public/college/college_public.json'))
listed={}
for f,lst in (('nu_20261110.txt','nu'),('nlac_20261110.txt','nlac')):
    for line in open(R+'raw/'+f):
        if line.startswith('#'):
            p=line.strip().split(';'); listed[p[1]]=(lst,p[4])
for k,v in cp.items():
    nm=v['college']; key=[n for n in listed if n.split(' (')[0][:18].lower()==nm.split(' (')[0][:18].lower()]
    if not key: print('nolist',nm); continue
    lst,e=listed[key[0]]
    usnv=e.split(' (')[0]; uy='fall 2025' if '(fall 2025)' in e else None
    y=(v['cds'].get('years') or {}).get('2025-2026') or {}
    b1=(y.get('B1_total_undergrad') or {}).get('value')
    add(lst,nm,'UG enrollment',usnv,uy,b1,'fall 2025' if b1 else None)
json.dump(rows,open(OUT+'referee_rows.json','w'),indent=1)
from collections import Counter
print(Counter((r['list'],r['outcome'],r['reason']) for r in rows))
