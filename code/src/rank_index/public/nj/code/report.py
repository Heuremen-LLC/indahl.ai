import json,sys
d=json.load(open(sys.argv[1]))
def g(s,k,f):
    v=s['summary'].get(k); return (v or {}).get(f,'—') if isinstance(v,dict) else '—'
unsup=[]
for s in d['schools']:
    sm=s['summary']
    print(f"### {s['name']} ({s['district']}; NJ {s['key']}; NCES {s.get('nces_id')})")
    for y in ('2023-24','2024-25'):
        ela=f"{g(s,'ELA '+y,'met_or_exceeded_pct')} (n={g(s,'ELA '+y,'valid_scores')}, part {g(s,'ELA '+y,'pct_students_taking_test') if y=='2023-24' else g(s,'ELA '+y,'participation_rate')})"
        mat=f"{g(s,'Math '+y,'met_or_exceeded_pct')} (n={g(s,'Math '+y,'valid_scores')}, part {g(s,'Math '+y,'pct_students_taking_test') if y=='2023-24' else g(s,'Math '+y,'participation_rate')})"
        if y=='2023-24':
            sc='; '.join(f"g{x['grade']} L3 {x['L3']}/L4 {x['L4']}" for x in sm.get('Science 2023-24 by grade (levels 1-4 %)',[])) or '—'
        else:
            sc=g(s,'Science 2024-25 percentage proficient','value')
        gp=sm.get('NJGPA '+y); gps=f" | NJGPA ELA {gp['ela_grad_ready']} (n={gp['ela_valid']}), Math {gp['math_grad_ready']} (n={gp['math_valid']})" if gp else ''
        rnt=sm.get('Registered/NotTested/Valid '+y,[])
        nt=[x for x in rnt if x['not_tested'] not in ('*','')]
        for x in rnt:
            if x['not_tested'] not in ('*',''): unsup.append((s['name'],y,x))
        ntxt=f"not-tested published for {len(nt)}/{len(rnt)} tests" + (': '+', '.join(f"{x['test']} reg {x['registered_to_test']} NT {x['not_tested']}" for x in nt) if nt else '')
        sd=sm.get('SchoolDay '+y,{})
        print(f"- {y}: ELA {ela}; Math {mat}; Sci {sc}{gps} | {ntxt} | enr {g(s,'Enrollment '+y,'Total')}, ED {g(s,'Economically Disadvantaged Students '+y,'value')} | day {sd.get('LengthOfDay','—')}, instr {sd.get('InstructionFullTime','—')} | NCES enr {g(s,'NCES '+y,'enrollment')} FL {g(s,'NCES '+y,'free_lunch')} RL {g(s,'NCES '+y,'reduced_price_lunch')}")
    if 'Graduation (2023-24 report)' in sm:
        a=sm['Graduation (2023-24 report)']; b=sm.get('Graduation (2024-25 report)',{})
        c23=[x['rate'] for x in sm.get('Graduation trend (2023-24 report)',[]) if x['cohort']=='2023' and x['type']=='4-Year Rate']
        print(f"- Grad 4-yr: class 2023 {c23[0] if c23 else '—'}; class 2024 {a['2024 4-Year Federal Graduation Rate']}; class 2025 {b.get('4YrGraduationRateFederal_School','—')}")
print('UNSUPPRESSED not-tested rows:',len(unsup))
for u in unsup[:30]: print(u)
