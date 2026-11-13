import json,subprocess,csv
base='files/'
R=[]
def add(school,item,value,year,definition,url,file,where,quote=None,method=None):
    d=dict(school=school,item=item,value=value,year=year,definition=definition,url=url,file=file,where=where)
    if quote: d['quote']=quote
    if method: d['method']=method
    R.append(d)
S={'MIT':'MIT School of Engineering','Stanford':'Stanford School of Engineering','Berkeley':'UC Berkeley College of Engineering','GaTech':'Georgia Tech College of Engineering','Purdue':'Purdue University College of Engineering (West Lafayette)','Caltech':'Caltech Division of Engineering and Applied Science','UIUC':'UIUC Grainger College of Engineering','UTAustin':'UT Austin Cockrell School of Engineering','UCSD':'UC San Diego Jacobs School of Engineering','CMU':'Carnegie Mellon College of Engineering'}
# HERD
out=subprocess.run(['python3','-I','x.py','files/herd24/nsf26304-tab021.xlsx'],capture_output=True,text=True).stdout.splitlines()
names={'MIT':'Massachusetts Institute of Technology','Stanford':'Stanford U.','Berkeley':'U. California, Berkeley','GaTech':'Georgia Institute of Technology','Purdue':'Purdue U., West Lafayette','Caltech':'California Institute of Technology','UIUC':'U. Illinois, Urbana-Champaign','UTAustin':'U. Texas, Austin','UCSD':'U. California, San Diego','CMU':'Carnegie Mellon U.'}
HU='https://ncses.nsf.gov/pubs/nsf26304/assets/data-tables/tables/nsf26304-tab021.xlsx'
for k,n in names.items():
    row=[l for l in out if l.startswith(n+' |')][0].split(' | ')
    rank=row[1]; tot=row[2:10]  # v,flag pairs 2021..2024
    vals={2021:(tot[0],tot[1]),2022:(tot[2],tot[3]),2023:(tot[4],tot[5]),2024:(tot[6],tot[7])}
    for fy in (2024,2023):
        v,fl=vals[fy]; v=str(int(float(v)))
        add(S[k],'NSF HERD engineering R&D expenditures, total all sources (whole-institution engineering field)',v+(' (flag "i" printed beside value)' if fl.strip()=='i' else ''),'FY %d'%fy,'Table 21: total higher education R&D expenditures in engineering, standard form survey population, dollars in thousands; HERD counts the whole institution\'s engineering field, not the school. Flag meaning not stated in the xlsx read.',HU,'files/herd24/nsf26304-tab021.xlsx','Table 21, institution row "%s", rank %d in FY2024 column group Total'%(n,int(float(rank))),method='parsed from xlsx; value in thousands of dollars as printed')
add('ALL','NSF HERD FY2025',None,'FY 2025','not published in the documents read','https://ncses.nsf.gov/surveys/higher-education-research-development/2025','files/herd2024_page.html','HTTP 404 on 2025 survey page on 2026-11-10; FY2024 page is the latest',method='not published in the documents read; URLs checked: https://ncses.nsf.gov/surveys/higher-education-research-development/2025 (404)')
# IPEDS
sums=json.load(open('files/ipeds_cip14_sums.json'))
ids={'MIT':166683,'Stanford':243744,'Berkeley':110635,'GaTech':139755,'Purdue':243780,'Caltech':110404,'UIUC':145637,'UTAustin':228778,'UCSD':110680,'CMU':211440}
ipn={'MIT':'MIT','Stanford':'Stanford','Berkeley':'Berkeley','GaTech':'GaTech','Purdue':'Purdue','Caltech':'Caltech','UIUC':'UIUC','UTAustin':'UTAustin','UCSD':'UCSD','CMU':'CMU'}
for k in S:
    for ay,f,z in (('2023-24','C2024_a.csv','C2024_A.zip'),('2022-23','C2023_a.csv','C2023_A.zip')):
        for lvl,lab in (('17',"doctor's degree - research/scholarship (AWLEVEL 17)"),('7',"master's degree (AWLEVEL 7)")):
            s=sums['%s|%d|%s|%s'%(k,ids[k],ay,lvl)]
            add(S[k],'IPEDS Completions CIP family 14 (Engineering), first majors, '+lab,str(s['sum']),'AY '+ay,'IPEDS Completions by CIP 6-digit, summed over all CIPCODE 14.xxxx rows with MAJORNUM=1 (file has no CIP 14 2-digit total row); by CIP family at the institution (UNITID %d), not the school; excludes computer science (CIP 11)'%ids[k],'https://nces.ed.gov/ipeds/datacenter/data/'+z,'files/'+z+' -> files/'+('x2024/' if '2024' in f else 'x2023/')+f,'UNITID %d, AWLEVEL %s, CIPCODE 14.*, sum of CTOTALT over %d rows'%(ids[k],lvl,s['rows']),method='computed sum of printed CTOTALT cells; row count %d'%s['rows'])
add('ALL','IPEDS Completions AY2024-25 (C2025_A)',None,'AY 2024-25','not published in the documents read','https://nces.ed.gov/ipeds/datacenter/data/C2025_A.zip','files/C2025_A_404.html','HTTP 404 on 2026-11-10',method='not published in the documents read; URL checked: https://nces.ed.gov/ipeds/datacenter/data/C2025_A.zip (404)')
json.dump(R,open('_herd_ipeds.json','w'),indent=1)
print(len(R))
