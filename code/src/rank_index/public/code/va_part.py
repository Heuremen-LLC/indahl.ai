import json
D="2026-11-10"
U="https://schoolquality.virginia.gov/schools/thomas-jefferson-high-for-science-and-technology"
F="sqp_tjhsst/tjhsst_profile_20261110.html (local files/VA/sqp_tjhsst/)"
def f(fig,val,yr,row,note=""):
    return dict(figure=fig,value=val,year=yr,source_url=U,file=F,row_or_table=row,date_read=D,note=note)
sol="VDOE SOL pass rate = Passed (Advanced + Proficient). Page shows whole-number percents for All Students. "
figs=[
f("EOC English Reading (SOL), all students, pass rate (Passed = Advanced + Proficient)","Advanced 78, Proficient 22, Passed 100, Failed 0","2023-24","Assessment tab, 'EOC English Reading Performance', row All Students, column 2023-2024",sol+"Same row 2024-25: Advanced 84, Proficient 16, Passed 100, Failed 0."),
f("EOC English Reading (SOL), all students, pass rate","Advanced 84, Proficient 16, Passed 100, Failed 0","2024-25","Assessment tab, 'EOC English Reading Performance', All Students, column 2024-2025","2024-25 extra, labelled as such."),
f("Mathematics (SOL, all math tests: EOC Algebra I, Geometry, Algebra II), all students, pass rate","Advanced 52, Proficient 48, Passed 100, Failed 0","2023-24","Assessment tab, 'Mathematics Performance', All Students, column 2023-2024",sol),
f("Mathematics (SOL), all students, pass rate","Advanced 74, Proficient 26, Passed 100, Failed 0","2024-25","Assessment tab, 'Mathematics Performance', All Students, column 2024-2025","2024-25 extra."),
f("Geometry SOL, all students, pass rate","Advanced 57, Proficient 43, Passed 100, Failed 0","2023-24","Assessment tab, 'Geometry Performance', All Students, 2023-2024","2024-25: Advanced 47, Proficient 53, Passed 100, Failed 0."),
f("Algebra II SOL, all students, pass rate","Advanced 50, Proficient 50, Passed 100, Failed 0","2023-24","Assessment tab, 'Algebra II Performance', All Students, 2023-2024","2024-25: Advanced 59, Proficient 41, Passed 100, Failed 0. Algebra I table shows a single column of '100 0 100 0' with the year not distinguishable in the page text, so not recorded."),
f("Science (SOL, all science tests; page lists Biology, Chemistry, Earth Science), all students, pass rate","Advanced 45, Proficient 55, Passed 100, Failed 0","2023-24","Assessment tab, 'Science Performance', All Students, 2023-2024",sol+"Biology 2023-24 identical (45/55/100/0)."),
f("Science (SOL), all students, pass rate","Advanced 55, Proficient 45, Passed 100, Failed 0","2024-25","Assessment tab, 'Science Performance', All Students, 2024-2025","2024-25 extra."),
f("Four-Year Virginia On-Time Graduation Rate, School, all students (series labelled '2023-2024' on the page)","100","2023-24 (page label; cohort/class year not stated on the page)","Graduation tab, chart data chartFourYearData['5'] 'School' first value; Division 94.6, State 92.9 for same label","The page series x-labels are '2023-2024','2024-2025','2025-2026' with School 100,100,100. The page does not state which graduating class each label is, nor is it labelled as the federal 4-year ACGR. Table 'Status of Students After Four Years of High School' (latest label) shows All Students cohort 519, graduates 519, rate 100, completers 519, dropouts 0. The VDOE cohort download files could not be read (403), so class of 2024 ACGR from the download file was not confirmed."),
f("Economically Disadvantaged, fall membership (state label 'Economically Disadvantaged', Fall Membership by Student Group, Sept 30)","279 of 2,017 students = 13.832%","2023-24","Enrollment tab, enrollmentStats['2023'] subgroup_type_id 3 (cnt 279, pct 13.832); total from Fall Membership by Grade 2,017 (2023-2024)","Page displays year as '2023-2024' for key 2023."),
f("Economically Disadvantaged, fall membership","355 of 2,111 = 16.817%","2024-25","Enrollment tab, enrollmentStats['2024'] subgroup 3","2024-25 extra."),
f("Instructional time per school","not published per school on the School Quality Profile","2023-24","Whole profile page searched for minutes, instructional hours, school day: only a generic reference to a 180-day school year in the chronic-absence definition","Looked at schoolquality.virginia.gov profile; VDOE (doe.virginia.gov) pages returned 403 so state files were not checked."),
]
out=dict(school="Thomas Jefferson High School for Science and Technology",ncessch="510126002034",state_id_used_by_state="Division 29 (Fairfax County Public Schools), School Number 1371",figures=figs,
refused=[
 {"url":"https://www.doe.virginia.gov/data-policy-funding/data-reports/statistics-reports/accreditation-agency-reports","what":"403 Forbidden (curl with HeuremenRANK user agent and WebFetch); SOL pass-rate download files not obtained"},
 {"url":"https://www.doe.virginia.gov/data-policy-funding/data-reports/statistics-reports/graduation-completion-reports","what":"403 Forbidden (curl)"},
 {"url":"https://www.doe.virginia.gov/data-policy-funding/data-reports/data-collection/free-reduced-price-lunch-eligibility","what":"403 Forbidden (curl)"},
 {"url":"https://www.doe.virginia.gov/home/showpublisheddocument/76370/639090120489604273","what":"403 Forbidden (curl)"},
 {"url":"https://schoolquality.virginia.gov/schools/thomas-jefferson-high-school-for-science-and-technology","what":"404 (wrong slug; correct slug used)"}],
sources=[{"url":U,"terms_url":"not seen"},{"url":"https://schoolquality.virginia.gov/divisions/fairfax-county-public-schools","terms_url":"not seen"}])
json.dump(out,open("parts/VA.json","w"),indent=1)
