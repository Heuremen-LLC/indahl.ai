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
MBA = [('Employment rate at graduation', '7%', 'Share of 2024 and 2025 job-seeking graduates employed at graduation, reported by schools to US News. Schools publish employment reports, many under the MBA CSEA standards', CALC),
       ('Employment rate three months after graduation', '13%', 'Same, three months after graduation, from school reports and published employment reports', CALC),
       ('Mean starting salary and bonus', '20%', 'Salary and bonus of 2024 and 2025 graduates, reported by schools. Employment reports publish salary, some as a median only', CALC),
       ('Salary by profession', '10%', 'Salaries by job type reported by schools, combined by US News', CALC),
       ('Peer assessment', '12.5%', 'A survey US News runs among business school deans and program directors', NOT),
       ('Recruiter assessment', '12.5%', 'A survey US News runs among recruiters', NOT),
       ('Median GMAT and GRE scores', '13%', 'Fall 2025 full-time entrants, reported by schools. Class profiles publish GMAT and GRE figures, not always the median', CALC),
       ('Median undergraduate GPA', '10%', 'Fall 2025 full-time entrants, reported by schools. Class profiles publish GPA, some as an average', PUB),
       ('Acceptance rate', '2%', 'Fall 2025 full-time applicants offered admission, reported by schools. Not every class profile prints admits', CALC)]
LAW = [('Employment 10 months after graduation', '33%', 'ABA employment summary reports', PUB), ('First-time and ultimate bar passage', '25%', 'ABA bar passage reports', PUB),
       ('Peer and lawyers and judges assessments', '25%', 'Surveys US News runs', NOT), ('LSAT and GRE, GPA, acceptance rate', '10%', 'ABA Standard 509 reports', PUB),
       ('Student-faculty ratio and library resources', '7%', 'ABA Standard 509 reports and school reports', CALC)]
ENG = [('Total research expenditures', '25%', 'Externally funded engineering research, fiscal 2024 and 2025, by the ASEE definition, reported by schools to US News. NSF HERD publishes engineering research spending for the whole institution, a different scope', NOT),
       ('Research expenditures per faculty member', '15%', 'The same spending over tenured and tenure-track faculty reported by schools', NOT),
       ('Faculty research (citations and journal measures)', '10%', 'Elsevier SciVal bibliometric data, 2021 to 2025, licensed', NOT),
       ('Peer assessment', '12.5%', 'A survey US News runs among engineering deans', NOT), ('Recruiter assessment', '12.5%', 'A survey US News runs among recruiters', NOT),
       ('Doctoral degrees awarded', '9%', 'Doctoral degrees in 2024-25, reported by schools. IPEDS publishes engineering doctorates by field for the whole institution, a different scope', CALC),
       ('Doctorate-to-faculty ratio', '6%', 'Fall 2025 doctoral students over tenured and tenure-track faculty, reported by schools', NOT),
       ('Faculty in the National Academy of Engineering', '5%', 'NAE membership and school faculty counts', CALC),
       ('Acceptance rate', '5%', 'Doctoral applicants offered admission for fall 2025, reported by schools. Few schools publish it', NOT)]
EDU = [('Total research expenditures', '30%', 'Education school research spending, fiscal 2024 and 2025, reported by schools to US News. NSF HERD publishes education-field research spending for the whole institution, a different scope', NOT),
       ('Research expenditures per faculty member', '20%', 'The same spending over tenured and tenure-track faculty reported by schools', NOT),
       ('Peer assessment', '12.5%', 'A survey US News runs among education deans', NOT), ('Educational professionals assessment', '12.5%', 'A survey US News runs among school superintendents and other professionals', NOT),
       ('Total doctoral degrees granted', '8%', 'Education doctorates in 2024-25, reported by schools. IPEDS publishes education doctorates by field for the whole institution, a different scope', CALC),
       ('Student-faculty ratio', '5%', 'Weighted student and faculty counts for 2025, reported by schools, with a log transform by US News', NOT),
       ('Percentage of faculty with awards', '5%', 'Awards and journal editorships US News selects, over faculty reported by schools', NOT),
       ('Graduate degrees granted-faculty ratio', '2%', 'Weighted degree counts over faculty, reported by schools', NOT),
       ('Acceptance rate', '5%', 'Doctoral applicants offered admission for 2025-26, reported by schools. Few schools publish it', NOT)]
MED = [('Total research activity', '20%', 'Research spending fiscal 2023 and 2024, as schools report it to the LCME (Part 1-A Schedule B) and to US News. Not published per school', NOT),
       ('Research activity per faculty member', '10%', 'The same over full-time faculty reported by schools', NOT),
       ('NIH research grants, medical school and affiliated hospitals', '20%', 'NIH awards fiscal 2024 and 2025, reported by schools. NIH RePORTER publishes awards per organization, and the hospital share depends on which affiliates a school counts', CALC),
       ('NIH research grants per faculty member', '10%', 'The same over full-time faculty reported by schools', CALC),
       ('Median MCAT score', '13%', '2025 entering class, reported by schools. AAMC publishes it per school only in a paid guide. Some schools publish it in a class profile', CALC),
       ('Median undergraduate GPA', '5%', '2025 entering class, reported by schools, as for the MCAT', CALC),
       ('Acceptance rate', '2%', 'Applicants offered admission to the 2025 entering class. AAMC publishes applicants and matriculants per school, not offers', NOT),
       ('Faculty resources', '20%', 'Full-time faculty over full-time MD students in 2025. AAMC publishes enrollment per school, faculty counts are school-reported (LCME)', CALC)]
S = {'hs': HS, 'nj_hs': HS, 'elem': K8, 'middle': K8, 'nj_elem': K8, 'nj_middle': K8, 'nu': COL(True), 'nlac': COL(False), 'nj_col': COL(True), 'mba': MBA, 'law': LAW, 'eng': ENG, 'edu': EDU, 'med': MED}
json.dump(S, open(os.path.join(HERE, 'data', 'sources.json'), 'w'), indent=1)
print({k: f"{sum(1 for x in v if x[3] == NOT)} of {len(v)} not public" for k, v in S.items()})
