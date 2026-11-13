import json
R=json.load(open('_herd_ipeds.json'))
S={'ALL':'ALL','MIT':'MIT School of Engineering','Stanford':'Stanford School of Engineering','Berkeley':'UC Berkeley College of Engineering','GaTech':'Georgia Tech College of Engineering','Purdue':'Purdue University College of Engineering (West Lafayette)','Caltech':'Caltech Division of Engineering and Applied Science','UIUC':'UIUC Grainger College of Engineering','UTAustin':'UT Austin Cockrell School of Engineering','UCSD':'UC San Diego Jacobs School of Engineering','CMU':'Carnegie Mellon College of Engineering'}
def a(k,item,value,year,defn,url,file,where,quote=None,method=None):
    d=dict(school=S[k],item=item,value=value,year=year,definition=defn,url=url,file=file,where=where)
    if quote:d['quote']=quote
    if method:d['method']=method
    R.append(d)
def na(k,item,year,urls,why='not published in the documents read'):
    a(k,item,None,year,why,urls[0],'', '',method='not published in the documents read; URLs checked: '+'; '.join(urls))
# MIT
mu='https://facts.mit.edu/enrollment-statistics/'; mf='files/mit_facts_enroll.html'
a('MIT','Graduate enrollment, master\'s','961 (376 shared with Computing)','2025-2026 (Fall 2025)','Graduate Students by School/College; students in joint programs with the College of Computing included in Engineering, shared count in parentheses',mu,mf,'Table "Graduate Students by School/College, 2025-2026", row Engineering*, column Master\'s','Engineering* | 961 (376) | 2,234** (776) | 114')
a('MIT','Graduate enrollment, doctoral','2,234 (776 shared with Computing); includes 181 Harvard-degree HST students','2025-2026 (Fall 2025)','same table, column Doctoral; footnote ** includes 181 students working on Harvard degrees only through Harvard-MIT HST',mu,mf,'same table, row Engineering*, column Doctoral','** Includes 181 students working on Harvard degrees only through the Harvard-MIT Health Sciences and Technology Program.')
a('MIT','Graduate enrollment, special','114','2025-2026 (Fall 2025)','same table, column Special',mu,mf,'same table, row Engineering*, column Special','Engineering* | 961 (376) | 2,234** (776) | 114')
a('MIT','Graduate enrollment, total (master\'s + doctoral + special)','3,309 (computed, not printed)','2025-2026 (Fall 2025)','computed 961+2,234+114; MIT does not print an Engineering graduate total in the page read',mu,mf,'derived from row above',method='computed sum of the three printed cells')
a('MIT','Tenured/tenure-track faculty (faculty count printed)','391* (146 shared with Schwarzman College of Computing)','October 2025','Distribution of Faculty by School/College; MIT counts professors, associate and assistant professors as Faculty, tenure status not split on the page','https://facts.mit.edu/employees/faculty/','files/mit_facts_faculty.html','Table "Distribution of Faculty by School/College, October 2025", row School of Engineering','School of Engineering | 391*')
a('MIT','Graduate applications / offers / enrolled (institution-wide only; not by school)','39,985 applications; 3,754 offers (9%); 2,275 first-year registered in advanced degree programs (61%)','Fall 2025','Selected Fall 2025 Graduate Admissions Statistics, whole MIT, not Engineering','https://facts.mit.edu/graduate-student-admission/','files/mit_facts_gradadm.html','box "Selected Fall 2025 Graduate Admissions Statistics"','39,985 Applications for graduate study; 3,754 Offers of admission (9%)')
na('MIT','Graduate applicants/admits/enrolled for Engineering only; master\'s vs Ph.D. split','Fall 2025',['https://facts.mit.edu/graduate-student-admission/','https://ir.mit.edu/','https://registrar.mit.edu/statistics-reports/enrollment-statistics-year (department enrollment counts only)'])
na('MIT','Engineering research expenditures (school level)','FY2025',['https://facts.mit.edu/operating-financials/ (sponsored research for whole Institute only)'])
# Stanford
a('Stanford','Graduate students, share in School of Engineering','39% (percentage only; headcount not printed)','Fall 2025','Graduate student majors range from 6% Law to 39% Engineering; matriculated graduate students 10,025 (university)','https://facts.stanford.edu/academics/graduate-education/graduate-student-profile/','files/stanford_facts_gradprofile.html','Graduate Student Profile, Fall 2025, "Graduate Students by School" table, row School of Engineering','School of Engineering | 39%')
a('Stanford','Faculty count, School of Engineering','280 (approximate wording "280 faculty"; tenure status not stated)','not stated (page copy accompanies Fall 2025 profile)','School description: nearly 5,000 graduate and undergraduate students and 280 faculty across nine departments','https://facts.stanford.edu/academics','files/stanford_facts_enroll.html','section School of Engineering description','With nearly 5,000 graduate and undergraduate students and 280 faculty across nine departments')
for it in ('Graduate engineering enrollment total (headcount)','Master\'s enrollment','Doctoral enrollment'):
    na('Stanford',it,'Fall 2025',['https://irds.stanford.edu/data-findings/enrollment (Tableau dashboard, not readable by curl; manual read)','https://engineering.stanford.edu/about','https://engineering.stanford.edu/about/engineering-community'])
na('Stanford','Graduate applicants, admits, enrolled; acceptance rate','Fall 2025',['https://engineering.stanford.edu/about','https://irds.stanford.edu/data-findings/cds (Common Data Set is university-wide)'])
na('Stanford','Engineering research expenditures (school level)','FY2025',['https://facts.stanford.edu/research/','https://engineering.stanford.edu/about'])
# Berkeley
bu='https://engineering.berkeley.edu/about/facts-and-figures/'; bf='files/berkeley_eng_facts.html'
a('Berkeley','Graduate students enrolled (total headcount)','2,368','Fall 2026 (as printed on page retrieved 2026-11-10; Fall 2025 not shown)','Enrollment: Fall 2026; note: total headcount may not equal sum of components because of duplication',bu,bf,'section Students, "Enrollment: Fall 2026"','Graduate students: 2,368')
a('Berkeley','Ladder-rank faculty','248','not dated on page','Faculty types: Ladder-rank faculty; Teaching faculty (LSOE) 12',bu,bf,'section Faculty, "Faculty types"','Ladder-rank faculty | 248')
a('Berkeley','Degree recipients: doctoral / master\'s / professional master\'s','254 / 199 / 875','2025-26','Degree recipients 2025-26 as printed',bu,bf,'section "Degree recipients: 2025-26"','Doctoral degrees: 254; Master\'s degrees: 199; Professional master\'s degrees: 875')
for it in ('Master\'s enrollment','Doctoral enrollment'):
    na('Berkeley',it,'Fall 2025',[bu,'https://engineering.berkeley.edu/about/facts-and-figures/ (Graduate At-A-Glance PDF linked, not fetched: only brochure link on page)','Cal Answers public dashboards (manual read)'])
na('Berkeley','Graduate applicants, admits, enrolled; acceptance rate','Fall 2025',[bu])
na('Berkeley','Engineering research expenditures (school level)','FY2025',[bu])
# GT
gu='https://irp.gatech.edu/sites/default/files/FactBook/2025_FactBook_Final.pdf'; gf='files/gt_2025_FactBook.pdf (text: files/gt_2025_FactBook.txt)'
a('GaTech','Graduate enrollment, master\'s (MS)','9,818','Fall 2025','Graduate Enrollment by College and Degree, Fall 2025, College of Engineering, MS',gu,gf,'Fact Book p.12 of 42 (PDF page 15), College of Engineering row MS, Total','College of Engineering MS ... 9,818')
a('GaTech','Graduate enrollment, doctoral (PhD)','2,560','Fall 2025','same table, PhD',gu,gf,'Fact Book p.12 of 42, College of Engineering row PhD, Total','PhD ... 2,560')
a('GaTech','Graduate enrollment, total (MS + PhD)','12,378 (computed, not printed)','Fall 2025','computed 9,818+2,560',gu,gf,'derived',method='computed sum of printed cells')
a('GaTech','Graduate enrollment, master\'s / PhD','9,337 / 2,501','Fall 2024','Graduate Enrollment by College and Degree, Fall Term History, 2024 column',gu,gf,'Fact Book p.11 of 42 (PDF page 14)','College of Engineering MS 9,337; PhD 2,501')
a('GaTech','Graduate applicants / accepted / enrolled; acceptance rate (master\'s and Ph.D. combined)','13,150 / 5,054 (38.4%) / 3,534 (69.9% of accepted enrolled)','Fall 2025','Graduate Admissions by Year and College, Fall Terms; Graduate Admissions Data Retrieved December 16, 2025; MS/PhD not split in this table',gu,gf,'Fact Book p.6 of 42 (PDF page 9), Fall 2025 College of Engineering','College of Engineering 13,150 5,054 38.4% 3,534 69.9%')
a('GaTech','Graduate applicants / accepted / enrolled','12,770 / 5,349 (41.9%) / 3,660 (68.4%)','Fall 2024','same table, Fall 2024 row',gu,gf,'Fact Book p.6 of 42, Fall 2024 College of Engineering','College of Engineering 12,770 5,349 41.9% 3,660 68.4%')
a('GaTech','Tenured/tenure-track faculty','403 (Regents Professor 21, Professor 221, Associate 82, Assistant 79)','Fall 2025','Tenured/Tenure-Track Faculty as of Fall 2025, College of Engineering',gu,gf,'Fact Book p.40 of 42, table "Tenured/ Tenure-Track Faculty as of Fall 2025"','College of Engineering 21 221 82 79 403')
a('GaTech','Sponsored research new awards (awards, not expenditures)','$311,568,045','Fiscal Year 2025','New Awards by Unit - Fiscal Year 2025, Office of Sponsored Programs; awards for research, instruction and other sponsored activities, not R&D expenditures',gu,gf,'Fact Book p.37 of 42 (PDF page 40), College of Engineering','College of Engineering $311,568,045')
na('GaTech','Engineering research expenditures (expenditure definition)','FY2025',[gu+' (only awards printed, see row above)'])
# Purdue
pu='https://engineering.purdue.edu/Engr/AboutUs/FactsFigures'; pf='files/purdue_eng_facts.html'
a('Purdue','Graduate enrollment, total (includes Agricultural and Biological Engineering)','5,617','Fall 2024 (page label "Fall Enrollment (2024*)")','Fall Enrollment table, Graduate row; * includes Agricultural and Biological Engineering',pu,pf,'section "Fall Enrollment (2024*)", row Graduate','Graduate | 5,617 | 23.4% | 8.0%')
a('Purdue','Degrees awarded: master\'s / PhD','1,298 / 361','2023-24','Degrees Awarded (2023-24*) incl. Agricultural and Biological Engineering',pu,pf,'section "Degrees Awarded (2023-24*)"','Masters 1,298; PhD 361')
a('Purdue','Faculty count (tenure status not stated)','494 ("494 faculty and 16,423 students")','not dated on page','College of Engineering facts list; the student figure 16,423 does not equal 13,688 + 5,617 so the line is probably from another year',pu,pf,'College of Engineering facts list, first bullet','494 faculty and 16,423 students')
a('Purdue','System-wide research expenditures (university, all fields, not engineering)','$647.3 million','not dated on page','University facts and figures: System-wide research expenditures total $647.3 million',pu,pf,'University facts and figures list','System-wide research expenditures total $647.3 million')
for it in ('Master\'s enrollment (separate from doctoral)','Doctoral enrollment (separate from master\'s)'):
    na('Purdue',it,'Fall 2025',['https://www.purdue.edu/datadigest/ (Tableau; manual read)',pu])
na('Purdue','Graduate applicants, admits, enrolled; acceptance rate','Fall 2025',['https://www.purdue.edu/datadigest/',pu])
na('Purdue','Engineering research expenditures (school level)','FY2025',[pu])
# Caltech
cu='https://www.eas.caltech.edu/about'; cf='files/caltech_eas.html'
a('Caltech','Graduate students in EAS','487 (of 1,285 graduates, institute-wide)','not stated (copy with 308 full time faculty)','EAS About page sentence; year not stated',cu,cf,'About page, first paragraph','308 full time faculty (75 in EAS), 948 undergraduates (411 in EAS), 1,285 graduates (487 in EAS)')
a('Caltech','Faculty: tenured / non-tenured professorial in EAS','70 / 10','not stated','Faculty & Research block on EAS About page',cu,cf,'section Faculty & Research','Tenured professorial faculty: 70; Non-tenured professorial faculty: 10')
a('Caltech','Graduate students, institute-wide (context only)','1282','Fall 2026-27 (as printed)','Registrar Fall Enrollment 2026-27, Graduate Total, Caltech whole','https://registrar.caltech.edu/records/enrollment-statistics','files/caltech_reg.html','Fall Enrollment table, Graduate Total','Graduate Total 1282')
for it in ('Master\'s enrollment','Doctoral enrollment'):
    na('Caltech',it,'Fall 2025',['https://registrar.caltech.edu/records/enrollment-statistics (institute-wide only)',cu])
na('Caltech','Graduate applicants, admits, enrolled; acceptance rate (EAS)','Fall 2025',[cu,'https://www.caltech.edu/about/at-a-glance','https://www.ir.caltech.edu/ (connection failed)'])
na('Caltech','Engineering research expenditures (division level)','FY2025',[cu])
# UIUC
gr='https://grainger.illinois.edu/about'
a('UIUC','Total research expenditures (college)','$300M ("in total research expenditures"; year and definition not stated)','not stated','Grainger About page headline statistic',gr,'files/grainger_about.html','About page statistics block','$300M in total research expenditures')
a('UIUC','Faculty count (tenure status not stated)','600+ ("expert faculty")','not stated','Grainger About page headline statistic',gr,'files/grainger_about.html','About page statistics block','600+ expert faculty leading breakthrough research')
for it in ('Graduate engineering enrollment total','Master\'s enrollment','Doctoral enrollment'):
    na('UIUC',it,'Fall 2025',['https://dair.illinois.edu/access-data/student-enrollment/ (Tableau; manual read)','https://dair.illinois.edu/access-data/campus-profile/ (Tableau; manual read)','https://grainger.illinois.edu/about/facts-and-rankings'])
na('UIUC','Graduate applicants, admits, enrolled; acceptance rate','Fall 2025',['https://dair.illinois.edu/access-data/common-data-set/ (campus-wide, not fetched)','https://grainger.illinois.edu/about/facts-and-rankings'])
na('UIUC','Tenured/tenure-track faculty count','Fall 2025',[gr,'https://grainger.illinois.edu/about/facts-and-rankings'])
# UT
tu='https://cockrell.utexas.edu/about/facts-and-rankings/'; tf='files/cockrell_facts_rankings.html'
a('UTAustin','Tenure/tenure-track faculty','297','not dated on page','Facts page: 297 tenure/tenure-track faculty members',tu,tf,'opening paragraph','With 297 tenure/tenure-track faculty members, 668 staff members, 8,517 students')
a('UTAustin','Graduate students enrolled (approximate)','Approximately 2,000','not dated on page','Facts page bullet, rounded',tu,tf,'bullet list','Approximately 2,000 graduate students enrolled')
for it in ('Master\'s enrollment','Doctoral enrollment'):
    na('UTAustin',it,'Fall 2025',['https://reports.utexas.edu/spotlight-data/students (dashboard; manual read)','https://reports.utexas.edu/statistical-handbook (static handbooks end 2020)',tu])
na('UTAustin','Graduate applicants, admits, enrolled; acceptance rate','Fall 2025',['https://reports.utexas.edu/common-data-set (not fetched for grad detail)',tu])
na('UTAustin','Engineering research expenditures (school level)','FY2025',[tu])
# UCSD
ju='https://jacobsschool.ucsd.edu/about/rankings'; jf='files/jacobs_rankings.html'
a('UCSD','Graduate enrollment, master\'s','2,631','Fall 2025','Jacobs School Statistics: Engineering Students (FALL 2025) 10,240 split bachelors/masters/PhD',ju,jf,'Jacobs School Statistics block, Masters Students','2,631 Masters Students')
a('UCSD','Graduate enrollment, doctoral','1,354','Fall 2025','same block, PhD Students',ju,jf,'Jacobs School Statistics block, PhD Students','1,354 PhD Students')
a('UCSD','Graduate enrollment, total (computed)','3,985 (computed, not printed)','Fall 2025','2,631+1,354',ju,jf,'derived',method='computed sum of printed cells')
a('UCSD','Professors (tenure status not stated)','276','Fall 2026 (as printed)','Jacobs School Statistics: Professors (Fall 2026)',ju,jf,'Jacobs School Statistics block','276 Professors (Fall 2026)')
a('UCSD','Research expenditures','$329M (federal, state and industry research expenditures)','2024-2025 Fiscal Year','"With $329 million in federal, state and industry research expenditures"; also tile "$329M In Research Expenditures (2024-2025 Fiscal Year)"',ju,jf,'page lead and statistics tiles','$329M In Research Expenditures (2024-2025 Fiscal Year)')
a('UCSD','Degrees conferred: master\'s / PhD','1,637 / 252','2025-2026 School Year (as printed)','Degrees Awarded (2025-2026 School Year)',ju,jf,'Jacobs School Statistics block','1,637 Masters degrees conferred; 252 PhD degrees conferred')
na('UCSD','Graduate applicants, admits, enrolled; acceptance rate','Fall 2025',[ju,'https://jacobsschool.ucsd.edu/about','https://ir.ucsd.edu/ (dashboards)'])
# CMU
cm='https://www.cmu.edu/ira/images/quickfacts/26_cmu_quickfacts.pdf'; cmf='files/cmu_quickfacts.pdf (page image check: files/cmu_quickfacts_p2.png)'
a('CMU','Graduate enrollment, master\'s','1,960','2025-2026 enrollment (Fall 2025)','Quick Facts 2025-2026: 2025-2026 ENROLLMENT, College row CoE, column Master\'s (columns Undergrad | Master\'s | PH.D. | Other)',cm,cmf,'PDF page 2, enrollment block, College, CoE','CoE 1,901 | 1,960 | 813 | 58')
a('CMU','Graduate enrollment, doctoral','813','2025-2026 enrollment (Fall 2025)','same row, PH.D. column',cm,cmf,'PDF page 2, CoE row','CoE 1,901 | 1,960 | 813 | 58')
a('CMU','Graduate enrollment, total (computed)','2,773 (computed, not printed)','2025-2026 enrollment','1,960+813 (Other 58 excluded)',cm,cmf,'derived',method='computed sum of printed cells')
a('CMU','Tenure-track faculty','165 (teaching track 44; research faculty 13; special faculty 27)','2025-2026 (Quick Facts edition)','FACULTY AND STAFF table, row CoE, column Tenure Track',cm,cmf,'PDF page 2, Faculty and Staff table, CoE','CoE 165 | 44 | 13 | 27')
a('CMU','Degrees awarded: master\'s / PhD','1,306 / 140','2024-2025','2024-2025 DEGREES, College row CoE',cm,cmf,'PDF page 2, degrees block, CoE row','CoE 500 | 1,306 | 140 | 46')
na('CMU','Graduate applicants, admits, enrolled; acceptance rate (College of Engineering)','Fall 2025',[cm+' (only undergraduate cohort admissions given)','https://www.cmu.edu/ira/'])
na('CMU','Engineering research expenditures (college level)','FY2025',[cm])
# ASEE
a('ALL','ASEE Engineering and Engineering Technology by the Numbers (profiles)',None,'2024','login required / automated read refused','https://profiles.asee.org/','files/asee.html','HTTP 403 to curl on 2026-11-10',method='manual read; HTTP 403, not bypassed')
json.dump(R,open('eng_public.json','w'),indent=1)
m=[
 ('https://profiles.asee.org/','HTTP 403 to automated read','ASEE profiles: graduate/doctoral/master\'s enrollment, faculty, research expenditures per school'),
 ('https://irds.stanford.edu/data-findings/enrollment','Tableau dashboard, no static data in page','Stanford School of Engineering Fall 2025 enrollment by degree level'),
 ('https://www.purdue.edu/datadigest/','Tableau dashboard, no static data in page','Purdue College of Engineering Fall 2025 master\'s/doctoral enrollment, grad applicants/admits'),
 ('https://dair.illinois.edu/access-data/student-enrollment/','Tableau dashboard (tableau.admin.uillinois.edu) not readable by curl; csv export URL did not connect','Grainger Fall 2025 graduate enrollment by level'),
 ('https://dair.illinois.edu/access-data/campus-profile/','Tableau dashboard','Grainger faculty/enrollment/research'),
 ('https://reports.utexas.edu/spotlight-data/students','Interactive dashboard; static statistical handbooks discontinued after 2020','Cockrell Fall 2025 master\'s/doctoral enrollment'),
 ('https://reports.utexas.edu/spotlight-data/faculty','Interactive dashboard (not fetched)','Cockrell tenure/tenure-track faculty Fall 2025'),
 ('https://ir.ucsd.edu/','Dashboards (not readable as static)','Jacobs applicants/admits/enrolled'),
 ('https://calanswers.berkeley.edu/','Cal Answers public dashboards (not attempted, interactive)','Berkeley Engineering Fall 2025 master\'s/doctoral enrollment and applicants/admits'),
 ('https://www.ir.caltech.edu/','Connection failed (HTTP 000)','Caltech EAS enrollment/applicants'),
 ('Stanford/MIT/Berkeley/Caltech/UIUC/UT/UCSD/CMU engineering research expenditures by school','No school-level expenditure figure found in public pages read (HERD gives whole-institution engineering field)','school-level engineering research expenditures'),
]
json.dump([dict(url=u,refusal=r,figure_sought=f) for u,r,f in m],open('manual_reads.json','w'),indent=1)
print(len(R))
