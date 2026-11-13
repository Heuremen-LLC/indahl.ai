import json,os
P=os.path.expanduser("~/bones-forge/rank_index/public/")
T="https://www.tn.gov/content/dam/tn/education/"
def f(fig,val,yr,url,file,row,note=""):
    return {"figure":fig,"value":val,"year":yr,"source_url":url,"file":file,"row_or_table":row,"date_read":"2026-11-10","note":note}
# ---- TN
tn=[]
a25=[json.loads(l) for l in open(os.environ["TN25"])]
a24=[json.loads(l) for l in open(os.environ["TN24"])]
for yr,rows,url,fn in (("2023-24 (file year 2024)",a24,T+"accountability/2024/school_assessment_file_suppressed_2024.xlsx","school_assessment_file_suppressed_2024.xlsx"),
                       ("2024-25 (file year 2025) [extra]",a25,T+"accountability/2025/school_assessment_file_suppressed_2025.xlsx","school_assessment_file_suppressed_2025.xlsx")):
    for d in rows:
        if d["subject"] in("Social Studies","US History"): continue
        tn.append(f(f"{d['test']} {d['subject']}, all grades, All Students: pct_met_exceeded ('On Track'+'Mastered' = file columns met/exceeded expectations)",d["pct_met_exceeded"],yr,url,fn,f"Sheet 1 row {d['row']} (system 750, school 15)",
          f"valid_tests={d['valid_tests']}, participation_rate={d['participation_rate']}; pct_below={d['pct_below']}, pct_approaching={d['pct_approaching']}, pct_met={d['pct_met_expectations']}, pct_exceeded={d['pct_exceeded_expectations']}. "+("'**' is the published value; the file carries no legend for it (suppression marker, meaning not documented in file). " if yr.startswith("2023") else "Published as a bin (>95%), suppressed per TDOE. ")+"File test column: "+d['test']+" (EOC = end-of-course; ACH = achievement/TCAP grades 3-8 test row listed for grades 9-12 enrollment at this school)."))
g=T+"data/"
tn.append(f("Four-year adjusted cohort graduation rate, class of 2024 (grad_rate_state, All Students)","**","class of 2024 (2023-24)",g+"2023-24_school_grad_rate_suppressed.xlsx","2023-24_school_grad_rate_suppressed.xlsx","Sheet 1 row 5298","grad_cohort_state=189; grad_count_state='**'; federal rate also '**'. Rate suppressed; cohort count published."))
tn.append(f("Four-year adjusted cohort graduation rate, class of 2025 (grad_rate_state, All Students) [extra]",">99%","class of 2025 (2024-25)",g+"2024-25_school_grad_rate_suppressed.xlsx","2024-25_school_grad_rate_suppressed.xlsx","Sheet 1 row 5443","grad_cohort_state=193; federal rate also '>99%'."))
tn.append(f("economically_disadvantaged_pct (School Profile, By Student Group)","Less than 5%","2023-24",g+"school-profile-2023-2024.xlsx","school-profile-2023-2024.xlsx","By Student Group row 1164","State label 'economically_disadvantaged_pct'; total enrollment K-12 = 1212. Binned and rounded for complementary suppression per file notes."))
tn.append(f("economically_disadvantaged_pct (School Profile, By Student Group) [extra]","Less than 5%","2024-25",g+"school-profile-2024-2025.xlsx","school-profile-2024-2025.xlsx","By Student Group row 1137","total K-12 = 1222."))
tn.append(f("Instructional time per school","not published per school","2023-24","https://www.tn.gov/education/districts/federal-programs-and-oversight/data/data-downloads.html","data-downloads page","page text","Looked at Data Downloads page (only mention of instructional days is in the chronic absenteeism definition) and the school profile/assessment/grad files (no minutes/hours/days columns). Report card site reportcard.tnedu.gov is a script-rendered page, not read."))
json.dump({"school":"Central Magnet School, Murfreesboro, Rutherford County Schools","ncessch":"470369002247","state_id_used_by_state":"system 750 / school 15 (CCD seasch 00750-0015)","figures":tn,
 "refused":[{"url":"https://tdepreportcard.tnedu.gov/","what":"DNS did not resolve (curl); not read"},
  {"url":"https://www.tn.gov/content/dam/tn/education/data/ (grad, profile files) and Data Downloads page","what":"first curl attempts returned HTTP 403, and the 2024 assessment file timed out once; the same URLs returned 200 on later retries with the same HeuremenRANK user agent (intermittent). No workaround used."},
  {"url":"https://www.tn.gov/education/data/data-downloads.html","what":"404"}],
 "sources":[{"url":"https://www.tn.gov/education/districts/federal-programs-and-oversight/data/data-downloads.html","terms_url":""}]},open(P+"parts/TN.json","w"),indent=1)
# ---- IN
I="https://www.in.gov/doe/files/"
inn=[]
def add(*a,**k): inn.append(f(*a,**k))
add("SAT Grade 11, EBRW 'At Benchmark' % (state HS assessment), all students","0.97058823529 (99 of 102 tested)","2023-24 (spring 2024, graduation cohort 2025)",I+"SAT-2024-Grade11-School.xlsx","SAT-2024-Grade11-School.xlsx","sheet EBRW row 423","Columns: Below 2, Approaching 1, At Benchmark 99, Total Tested 102, Benchmark % 0.9706. Proficiency level name: 'At Benchmark'.")
add("SAT Grade 11, Math 'At Benchmark' %, all students","0.83333333333 (85 of 102 tested)","2023-24",I+"SAT-2024-Grade11-School.xlsx","SAT-2024-Grade11-School.xlsx","sheet Math row 423","Below 1, Approaching 16, At Benchmark 85, Total 102.")
add("SAT Grade 11, both EBRW and Math at benchmark %","0.83333333333 (85 of 102)","2023-24",I+"SAT-2024-Grade11-School.xlsx","SAT-2024-Grade11-School.xlsx","sheet Both row 423")
add("ILEARN Biology, 'Total Proficient' % (At + Above Proficiency), all students","0.96739130434 (89 of 92 tested)","2023-24",I+"ILEARN-2024-Biology-Final-School-1.xlsx","ILEARN-2024-Biology-Final-School-1.xlsx","sheet Biology row 502","Below 0, Approaching 3, At 7, Above 82, Total Proficient 89, Total Tested 92. Science = ILEARN Biology (end-of-course). No ILEARN grade 10 ELA/math file found on the data center; HS math/EBRW measured by SAT.")
add("SAT Grade 11, EBRW 'At Benchmark' % [extra]","0.96511627906 (83 of 86)","2024-25 (spring 2025, graduation cohort 2026)",I+"SAT-2025-Grade11-School_a.xlsx","SAT-2025-Grade11-School_a.xlsx","sheet EBRW row 435","Below 1, Approaching 2, At 83, Total 86.")
add("SAT Grade 11, Math 'At Benchmark' % [extra]","0.8488372093 (73 of 86)","2024-25",I+"SAT-2025-Grade11-School_a.xlsx","SAT-2025-Grade11-School_a.xlsx","sheet Math row 435","Below 2, Approaching 11, At 73, Total 86.")
add("SAT Grade 11, both at benchmark % [extra]","0.82558139534 (71 of 86)","2024-25",I+"SAT-2025-Grade11-School_a.xlsx","SAT-2025-Grade11-School_a.xlsx","sheet Both row 435")
add("ILEARN Biology Total Proficient % [extra]","0.96907216494 (94 of 97 tested)","2024-25",I+"ILEARN-2025-Biology-Final-School.xlsx","ILEARN-2025-Biology-Final-School.xlsx","sheet Biology row 515","Below 0, Approaching 3, At 6, Above 88, Total Proficient 94, Total Tested 97.")
add("Four-year graduation rate (state), Total, class of 2024","1 (cohort 84, graduates 84)","class of 2024 (2023-24)",I+"2024-Indiana-State-Graduation-Rate-.xlsx","2024-Indiana-State-Graduation-Rate-.xlsx","sheet 'School Pub Disagg' row 393 (Total columns); federal-method file not read","Published as 1 (decimal). Non-waiver rate same row of 'School Pub NonWaiver Disagg': 84/84, 1.")
add("Four-year graduation rate (state), Total, class of 2025 [extra]","1 (cohort 98, graduates 98)","class of 2025 (2024-25)",I+"2025-Indiana-State-Graduation-Rate.xlsx","2025-Indiana-State-Graduation-Rate.xlsx","sheet 'School Pub Disagg' row 403 (Total columns)")
add("Free/Reduced Price Meals count and total enrollment (state publishes counts, not a percent)","Free/Reduced Price Meals 34; Paid Meals 344; TOTAL ENROLLMENT 378","sheet '2024' of 2006-26 file (school year label ambiguous: sheet named 2024, read as 2023-24)",I+"school-enrollment-ethnicity-and-free-reduced-price-meal-status-2006-26-final.xlsx","school-enrollment-ethnicity-and-free-reduced-price-meal-status-2006-26-final.xlsx","sheet 2024 row 1789","State label 'Free/Reduced Price Meals'. Percent is not published; 34/378 arithmetic = 8.99% (our computation, not state-published). Sheet-year convention is not stated in the file; sheet 2026 carries the newest year.")
add("Free/Reduced Price Meals count and total enrollment [extra]","Free/Reduced 41; Paid 343; TOTAL 384","sheet '2025' (read as 2024-25)",I+"school-enrollment-ethnicity-and-free-reduced-price-meal-status-2006-26-final.xlsx","same file","sheet 2025 row 1802","Same sheet-year ambiguity. 41/384 = 10.7% (our arithmetic).")
add("Instructional time per school","not published per school","2023-24","https://www.in.gov/doe/it/data-center-and-reports/","Data Center page and archive page","page link lists","Looked at the Data Center and Reports page and its archive link list; no instructional minutes/hours/days file listed. INview not read (DNS did not resolve).")
json.dump({"school":"Signature School Inc, Evansville (charter)","ncessch":"180002100319","state_id_used_by_state":"corp 9315 / school 8295 (CCD seasch 9315-8295)","figures":inn,
 "refused":[{"url":"https://inview.doe.in.gov/","what":"DNS did not resolve (curl); not read"}],
 "sources":[{"url":"https://www.in.gov/doe/it/data-center-and-reports/","terms_url":""},{"url":"https://www.in.gov/doe/it/data-center-and-reports/data-reports-archive","terms_url":""}]},open(P+"parts/IN.json","w"),indent=1)
