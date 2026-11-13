import json
D="2026-11-10"
def f(figure,value,year,url,file,row,note=""):
    return dict(figure=figure,value=value,year=year,source_url=url,file=file,row_or_table=row,date_read=D,note=note)
P1="https://osse.dc.gov/assessmentresults2024"
B1="https://app.box.com/s/5gs5mber6fgumxraljpx0a3se21295in"
F1="2023-24 School Level DCCAPE and MSAA Data 1.15.2025.xlsx (local files/DC/cape2324_school/school2324.xlsx)"
S1="sheet 'Meeting, Exceeding', school code 466, Metric 'Meeting or Exceeding Expectations', Student Group 'All Students', "
n1="Level threshold: 'Meeting or Exceeding Expectations' (DC CAPE levels 4 and 5). Assessment Name 'All' (DC CAPE plus MSAA). Suppression codes in file: DS, n<10. "
P2="https://osse.dc.gov/assessmentresults2025"
B2="https://app.box.com/s/h1bdtjr77dgxsllrsrmv9p358f6j9ket"
F2="2024-25 Public File School Level DCCAPE and MSAA Data 1.xlsx (local files/DC/cape2425_school/school2425.xlsx)"
SC1="https://osse.dc.gov/node/1745186"
SCF1="DC School Report Card Assessment Science - Metric Scores (2024).xlsx (local files/DC/sci2324/sci2324.xlsx)"
SC1U="https://osse.dc.gov/sites/default/files/dc/sites/osse/page_content/attachments/DC%20School%20Report%20Card%20Assessment%20Science%20-%20Metric%20Scores%20%282024%29%20%281%29.xlsx"
SC2="https://osse.dc.gov/node/1839956"
SC2U="https://osse.dc.gov/sites/default/files/dc/sites/osse/page_content/attachments/2024-25%20Public%20File%20School%20Level%20DCCAPE%20and%20DLM%20Data.xlsx"
G1="https://osse.dc.gov/sites/default/files/dc/sites/osse/service_content/attachments/Public%20SY2324%20ACGR%20Rates.xlsx"
G2="https://osse.dc.gov/sites/default/files/dc/sites/osse/service_content/attachments/Public%20SY2425%20ACGR%20Rates.xlsx"
figs=[
f("Math, all students, % Meeting or Exceeding Expectations (DC CAPE Algebra I, Geometry, Algebra II end-of-course; school total, High School)","67.8 (122 of 180 tested)","2023-24",B1,F1,S1+"Assessment Name 'All', Subject Math, Tested Grade/Subject 'All', row 45164 (page: "+P1+")",n1),
f("ELA, all students, % Meeting or Exceeding Expectations (DC CAPE English I, English II; school total)","97.00 (292 of 301 tested)","2023-24",B1,F1,S1+"Assessment Name 'All', Subject ELA, Tested Grade/Subject 'All', row 20128 as printed: row 45128 (page: "+P1+")",n1),
f("Math by course, % Meeting or Exceeding: Algebra I","64.00 (16 of 25)","2023-24",B1,F1,S1+"Assessment 'DCCAPE', Algebra I, row 45196",n1),
f("Math by course, % Meeting or Exceeding: Geometry","66.4 (91 of 137)","2023-24",B1,F1,S1+"Assessment 'All', Geometry, row 45313",n1),
f("Math by course, % Meeting or Exceeding: Algebra II","83.3 (15 of 18)","2023-24",B1,F1,S1+"Assessment 'All', Algebra II, row 45302",n1),
f("ELA by course, % Meeting or Exceeding: English I","98.7 (147 of 149)","2023-24",B1,F1,S1+"Assessment 'All', English I, row 45165",n1),
f("ELA by course, % Meeting or Exceeding: English II","95.4 (145 of 152)","2023-24",B1,F1,S1+"Assessment 'DCCAPE', English II, row 45438",n1),
f("Science, all students, % Meeting or Exceeding Expectations (DC Science Assessment, Biology)","48.1 (n=154)","2023-24",SC1U,SCF1,"sheet 'School Overall Scores', row 5188, School Code 466, Student Group 'All Report Card Students', Metric 'Meeting or Exceeding Expectations - Science' (page: "+SC1+")","Levels 3 and 4 of 4 on DC Science Assessment. Same file gives Level 1 1.9, Level 2 50.0, Level 3 45.5, Level 4 2.6 (rows 5210-5243); participation 98.7 (n=156)."),
f("Math, all students, % Meeting or Exceeding Expectations","75.3 (119 of 158)","2024-25",B2,F2,"sheet 'Meeting, Exceeding', row 6798, school code 466, Subject Math, Student Group 'All Students', Enrolled Grade or Course 'All' (page: "+P2+")","2024-25, labelled as such. DC CAPE and MSAA, level 'Meeting or Exceeding Expectations'."),
f("ELA, all students, % Meeting or Exceeding Expectations","'>99%' (count DS, total DS)","2024-25",B2,F2,"sheet 'Meeting, Exceeding', row 6839, school code 466, Subject ELA, Student Group 'All Students', Enrolled Grade or Course 'All' (page: "+P2+")","Published as binned '>99%'; counts suppressed (DS)."),
f("Science, all students, % Meeting or Exceeding Expectations (DC Science Assessment, Biology)","70.59 (108 of 153)","2024-25",SC2U,"2024-25 Public File School Level DCCAPE and DLM Data.xlsx (local files/DC/sci2425/s.xlsx)","sheet 'Meeting, Exceeding', row 907, school code 466, Student Group 'All Students' (page: "+SC2+")","2024-25, labelled as such. Performance Level 3 shown as 65.36 (counts DS); participation 95.63 (153 of 160)."),
f("Four-year adjusted cohort graduation rate, class of 2024 (4-Year ACGR, SY2023-24)",">99% (cohort total 139, graduates DS)","2023-24",G1,"Public SY2324 ACGR Rates.xlsx (local files/DC/acgr2324/acgr2324.xlsx)","sheet '2023-24 School Rates', row 21, DCPS, '4-Year ACGR', School Without Walls High School","Binned and suppressed by the state ('>99%', DS). 5-Year ACGR row 41: cohort 150, '>99%'."),
f("Four-year adjusted cohort graduation rate, class of 2025 (4-Year ACGR, SY2024-25)",">99% (cohort total 153, graduates DS)","2024-25",G2,"Public SY2425 ACGR Rates.xlsx (local files/DC/acgr2425/acgr2425.xlsx)","sheet '2024-25 School Rates', row 22","2024-25 extra, labelled as such. Binned and suppressed by the state."),
f("Economically Disadvantaged, percent of enrollment (state label: 'Economically Disadvantaged', Percent Enrolled, rounded to whole number)","7","2023-24","https://osse.dc.gov/page/dc-school-report-card-resource-library","2024 DC School Report Card Aggregate Enrollment Data (2).xlsx (local files/DC/rc_enroll2024/e.xlsx)","sheet 'Ever Enrolled Population', row 2343, school code 466, Student Group 'Economically Disadvantaged', Total Count of Students 602","Ever-enrolled population basis, whole-number percent. File URL: https://osse.dc.gov/sites/default/files/dc/sites/osse/page_content/attachments/2024%20DC%20School%20Report%20Card%20Aggregate%20Enrollment%20Data%20%282%29.xlsx"),
f("Economically Disadvantaged, percent of enrollment (same label)","7","2024-25","https://osse.dc.gov/page/dc-school-report-card-resource-library","DC School Report Card Aggregate Enrollment Data (2025).xlsx (local files/DC/rc_enroll2025/e.xlsx)","sheet 'Ever Enrolled Population', row 2344, Total Count of Students 607","2024-25 extra, labelled as such."),
f("At-Risk students funded in UPSFF (count, not percent; state funding category 'At-Risk')","66 of 598 'Total UPSFF'","2023-24","https://osse.dc.gov/page/2023-24-school-year-enrollment-audit-report-and-data","2023-24 School Year Enrollment Audit Report Data (4.25.24).xlsx (local files/DC/enroll2324/enroll.xlsx)","sheet 'School UPSFF Enr by Spl Need', rows 667 and 673, school code 466","A count from the enrollment audit, different definition from Economically Disadvantaged (state notes At-Risk keeps the overage criterion). Percent not published in this file."),
f("Instructional time per school","Published as daily clock hours only: Monday-Friday '09:00 AM - 03:30 PM' (state field 'Instructional Hours')","2023-24","https://osse.dc.gov/page/dc-school-report-card-resource-library","DC School Report Card School Directory Information (2024) update.xlsx (local files/DC/rc_dir2024/d.xlsx)","sheet 'School Profile Data 2023-2024', School ID 466","Start and end times only. No minutes per year or days per year per school found."),
]
# fix a row note typo
for x in figs:
    x["row_or_table"]=x["row_or_table"].replace("row 20128 as printed: row 45128","row 45128")
out=dict(school="School Without Walls High School",ncessch="110003000131",state_id_used_by_state="LEA 001 (District of Columbia Public Schools), School Code 466",figures=figs,
refused=[{"url":"https://dcschoolreportcard.org/","what":"503 on curl (service unavailable), so figures taken from OSSE data files instead"}],
sources=[{"url":"https://osse.dc.gov/page/data-and-reports","terms_url":"not seen"},{"url":P1,"terms_url":"not seen"},{"url":P2,"terms_url":"not seen"},{"url":SC1,"terms_url":"not seen"},{"url":SC2,"terms_url":"not seen"},{"url":"https://osse.dc.gov/page/dc-school-report-card-resource-library","terms_url":"not seen"},{"url":"https://osse.dc.gov/page/2023-24-school-year-enrollment-audit-report-and-data","terms_url":"not seen"},{"url":"https://app.box.com","terms_url":"OSSE hosts school-level assessment files on Box shared links linked from its pages; downloaded with the shared-link download URL, no login or bot check bypassed"}])
json.dump(out,open("parts/DC.json","w"),indent=1)
