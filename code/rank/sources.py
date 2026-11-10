#!/usr/bin/env python3
"""RANK: where each indicator's data comes from, per list, written from the US News method pages captured in raw/ (quoted there).
public: 'public' = the figure is published per school by the source named. 'public inputs, US News calculation' = the inputs are published,
the scoring is US News's own. 'not public' = a survey US News runs, a model US News fits, licensed data, or school-submitted data not published per school.
Heuremen LLC."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
PUB, CALC, NOT = 'public', 'public inputs, US News calculation', 'not public'
HS = [('College readiness', '30%', 'AP and IB exam results of 2023-24 12th graders, from College Board and IB', NOT),
      ('College curriculum breadth', '10%', 'AP and IB exam results of 2023-24 12th graders (same source)', NOT),
      ('State assessment proficiency', '20%', 'State math, reading and science assessment results, 2023-24', CALC),
      ('State assessment performance', '20%', 'The same results compared with what US News predicted for a school with its demographic characteristics (CCD lunch and ethnicity data)', NOT),
      ('Underserved student performance', '10%', 'State assessment results of Black, Hispanic and low-income students compared with nonunderserved students in the state', CALC),
      ('Graduation rate', '10%', 'Four-year graduation rate of students who entered ninth grade in 2020-21', PUB)]
K8 = [('Mathematics and reading proficiency', '50%', 'State assessment results, the share of test-takers at each performance level, weighted and summed', CALC),
      ('Mathematics and reading performance', '50%', 'The same results in the context of socioeconomic characteristics, from a model US News fits (CCD lunch and ethnicity data)', NOT)]
def COL(nu):
    return [('Graduation rate', '16%', 'Bachelor\'s graduation rate, reported by schools and in IPEDS', PUB), ('First-year retention', '5%', 'Reported by schools and in IPEDS', PUB),
            ('Graduation performance', '10%', 'Graduation rate against a rate US News predicts', NOT), ('Pell graduation rate', '5.5%', 'Graduation rate of Pell recipients (IPEDS)', PUB),
            ('Pell graduation performance', '5.5%', 'Pell graduation rate against what US News expects', NOT), ('Graduates earning more than high school graduates', '5%', 'College Scorecard, U.S. Treasury earnings of Title IV students', PUB),
            ('Earnings by major', '5%', 'College Scorecard', PUB), ('Peer assessment', '20%', 'Presidents, provosts and deans rate institutions, a survey US News runs', NOT),
            ('Student-faculty ratio', '3%' if nu else '4%', 'Reported by schools, and in the Common Data Set where a school posts one', PUB), ('Full-time faculty share', '2%' if nu else '3%', 'Reported by schools, and in the Common Data Set where a school posts one', PUB),
            ('Faculty salaries', '6%' if nu else '8%', 'Reported by schools to US News, aligned with IPEDS', CALC), ('Financial resources per student', '8%', 'Spending reported by schools, aligned with IPEDS', CALC),
            ('Standardized tests', '5%', 'Median SAT and ACT of the entering class, with adjustments US News makes for higher reporting', CALC)] + ([('Faculty research', '4%', 'Elsevier bibliometric data, 2021-2025', NOT)] if nu else [])
MBA = [('Employment and salary of graduates', '50%', 'Reported by schools to US News, many schools also publish employment reports', CALC), ('Peer and recruiter assessments', '25%', 'Surveys US News runs', NOT),
       ('GMAT and GRE, GPA, acceptance rate', '25%', 'Reported by schools to US News, class profiles published by many schools', CALC)]
LAW = [('Employment 10 months after graduation', '33%', 'ABA employment summary reports', PUB), ('First-time and ultimate bar passage', '25%', 'ABA bar passage reports', PUB),
       ('Peer and lawyers and judges assessments', '25%', 'Surveys US News runs', NOT), ('LSAT and GRE, GPA, acceptance rate', '10%', 'ABA Standard 509 reports', PUB),
       ('Student-faculty ratio and library resources', '7%', 'ABA Standard 509 reports and school reports', CALC)]
ENG = [('Research expenditures, total and per faculty member', '40%', 'Reported by schools to US News', NOT), ('Faculty research (citations and journal measures)', '10%', 'Elsevier bibliometric data', NOT),
       ('Peer and recruiter assessments', '25%', 'Surveys US News runs', NOT), ('Doctoral degrees and doctorate-to-faculty ratio', '15%', 'Reported by schools, doctoral degrees also in IPEDS', CALC),
       ('Faculty in the National Academy of Engineering', '5%', 'NAE member directory and school counts', CALC), ('Acceptance rate', '5%', 'Reported by schools to US News', NOT)]
EDU = [('Research expenditures, total and per faculty member', '50%', 'Reported by schools to US News', NOT), ('Peer and educational professionals assessments', '25%', 'Surveys US News runs', NOT),
       ('Doctoral degrees, student-faculty ratio, faculty awards, degrees per faculty', '20%', 'Reported by schools to US News, doctoral degrees also in IPEDS', CALC), ('Acceptance rate', '5%', 'Reported by schools to US News', NOT)]
MED = [('Research activity, total and per faculty member, and NIH grants', '60%', 'Reported by schools to US News, NIH grant totals are also published by NIH', CALC),
       ('Median MCAT, median GPA, acceptance rate', '20%', 'Reported by schools to US News', NOT), ('Faculty resources (a faculty ratio described on the method page)', '20%', 'Reported by schools to US News', NOT)]
S = {'hs': HS, 'nj_hs': HS, 'elem': K8, 'middle': K8, 'nj_elem': K8, 'nj_middle': K8, 'nu': COL(True), 'nlac': COL(False), 'nj_col': COL(True), 'mba': MBA, 'law': LAW, 'eng': ENG, 'edu': EDU, 'med': MED}
json.dump(S, open(os.path.join(HERE, 'data', 'sources.json'), 'w'), indent=1)
print({k: f"{sum(1 for x in v if x[3] == NOT)} of {len(v)} not public" for k, v in S.items()})
