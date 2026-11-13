import json
D="2026-11-10"
def yr(url,loc,b1,b1note,a,ad,en,s25,s75,a25,a75,ps,pa,ratio,sec,coh,b6,b7,b9,b10,pell,ret,retc,notes,grand=None):
    t=sec[-1];u20=round((sec[0]+sec[1])/t*100,1)
    ac=ad/a*100
    from decimal import Decimal,ROUND_HALF_UP
    return {"exists":True,"source_url":url,"local_file":loc,"date_read":D,
     "B1_total_undergrad":{"value":b1,"item":"B1","note":b1note,"grand_total":grand},
     "C1":{"applicants":a,"admits":ad,"enrolled":en,"acceptance_pct_1dp":round(ac,1),"acceptance_pct_whole":int(Decimal(ac).quantize(Decimal(1),rounding=ROUND_HALF_UP))},
     "C9":{"SAT_comp_25":s25,"SAT_comp_75":s75,"ACT_comp_25":a25,"ACT_comp_75":a75,"pct_submit_SAT":ps,"pct_submit_ACT":pa},
     "I2_ratio":ratio,
     "I3":dict(zip(["2-9","10-19","20-29","30-39","40-49","50-99","100+","total"],sec),pct_under_20_1dp=u20),
     "B_grad":{"cohort":coh,"B6_adj_cohort":b6,"B7_4yr":b7,"B9_6yr":b9,"B10_6yr_rate_printed":b10,"rate_4yr_1dp":round(b7/b6*100,1),"pell_6yr_rate":pell},
     "B22_retention":{"value":ret,"cohort":retc},"notes":notes}
base="/Users/heuremen/bones-forge/rank_index/public/college/cds/"
out={}
out["bowdoin"]={"slug":"bowdoin","college":"Bowdoin College","cds_index_url":"https://www.bowdoin.edu/ir/data/index.html","years":{
 "2025-2026":yr("https://www.bowdoin.edu/ir/pdf/bowdoin-cds_2025-2026.pdf",base+"bowdoin/cds_2025-26.pdf",1841,"EN_TOT_UG_N form field; FT 1837 + PT 4; grand total also 1841",14045,957,515,1470,1540,33,35,"34.76% (179)","17.28% (89)","8.32 to 1 (1838 students / 221 faculty; printed as 8.32 in form field)",[84,176,39,72,11,6,0,388],"Fall 2019",498,360,462,"92.77%","92.11%","97.63%","Fall 2024 (495/507)","Values read from fillable PDF form fields. C1 men 6690/440/250, women 7355/517/265, other 0. Class subsections not counted (0).",1841),
 "2024-2025":yr("https://www.bowdoin.edu/ir/pdf/bowdoin-cds_2024-2025.pdf",base+"bowdoin/cds_2024-25.pdf",1881,"EN_TOT_UG_N form field",13265,946,507,1470,1540,33,35,"31.164% (158)","16.77% (85)","8.69 to 1 (1876 students / 216 faculty)",[95,165,61,67,10,4,0,402],"Fall 2018",508,368,484,"95.28%","92.59%","96.83%","Fall 2023","Values from fillable PDF form fields. C1 men 6244/434/232, women 7013/511/275, non-binary 8/1/0 (totals 13265/946 match form's own total fields).",1881)},
 "refusals":[]}
out["cmc"]={"slug":"cmc","college":"Claremont McKenna College","cds_index_url":"https://www.cmc.edu/institutional-research/common-data-set","years":{
 "2025-2026":yr("https://www.cmc.edu/sites/default/files/CDS_2025-26.pdf",base+"cmc/cds_2025-26.pdf",1378,"Total all undergraduates; men 701 + women 677",6939,655,335,1480,1540,33,35,"34% (115)","14% (48)","8 to 1 (based on 1376 students and 178.3333 faculty)",[38,256,46,0,0,4,0,344],"Fall 2019",327,230,294,"89.91%","92.31%","97.92%","Fall 2024 (337 initial, 330 retained; count read from the file)","Page headers in the file read 'Common Data Set 2024-2025' on some pages but the content is fall 2025 (cohort 2019, Fall 2025 dates). Also an annotated version downloaded: cds_2025-26_annotated.pdf (not used for numbers).",1380),
 "2024-2025":yr("https://www.cmc.edu/sites/default/files/CDS_2024-2025.pdf",base+"cmc/cds_2024-25.pdf",1390,"Total all undergraduates",6529,626,337,1490,1550,33,35,"26% (87)","13% (45)","8 to 1 (based on 1390 students and 183.67 faculty)",[26,235,65,4,1,4,0,335],"Fall 2018",325,244,296,"91.08%","91.94%","98.13%","Fall 2023 (315/321)","C1 applicant/admit/enrolled totals 6529/626/337 as printed. I3 printed %<20 = 77.91%.",1393)},
 "refusals":[]}
out["swarthmore"]={"slug":"swarthmore","college":"Swarthmore College","cds_index_url":"https://www.swarthmore.edu/institutional-effectiveness-research-assessment/common-data-set","years":{
 "2025-2026":yr("https://www.swarthmore.edu/sites/default/files/assets/documents/institutional-effectiveness-research-assessment/Swarthmore-CDS-2025-26.pdf",base+"swarthmore/cds_2025-26.pdf",1631,"EN_TOT_UG_N form field",12995,977,426,1480,1550,33,35,"40.14% (171)","14.79% (63)","7.9 to 1 (1630.3 students / 207.3 faculty)",[132,163,78,22,12,9,3,419],"Fall 2019",417,302,382,"91.61%","89.29%","98.1%","Fall 2024 (419/427)","Fillable PDF form fields. C1 men 5709/472/201, women 7286/505/225; other-gender fields blank.",1631),
 "2024-2025":yr("https://www.swarthmore.edu/sites/default/files/assets/documents/institutional-effectiveness-research-assessment/Swarthmore-CDS-2024-2025-fillable-pdf-version.pdf",base+"swarthmore/cds_2024-25.pdf",1623,"Total All Undergraduates form field",13065,975,427,1500,1550,33,35,"39.34% (168)","16.16% (69)","7.4 to 1 (1621 students / 216.7 faculty)",[137,156,68,33,9,9,3,415],"Fall 2018",414,314,382,"92.27%","92.05%","93.98%","Fall 2023 (single form field on the retention page; counts not shown)","Fillable PDF form fields. C1 applicants = men 5746 + women 7311 + unknown 8 (no printed total row); admits = men 465 + women 510 (no other rows filled); enrolled men 203 + women 224. Old 'Swarthmore-College-CDS-2024-2025.pdf' URL returned 404; the fillable version listed on the IR page was used.",1623)},
 "refusals":["https://www.swarthmore.edu/sites/default/files/assets/documents/institutional-effectiveness-research-assessment/Swarthmore-College-CDS-2024-2025.pdf -> HTTP 404 (replaced by fillable-pdf-version link from IR page)"]}
out["pomona"]={"slug":"pomona","college":"Pomona College","cds_index_url":"https://www.pomona.edu/administration/institutional-research/information-center/common-data-set","years":{
 "2025-2026":{"exists":True,"source_url":"https://tableau.campus.pomona.edu/views/CDS2025-26/A_GeneralInformation","local_file":base+"pomona/2025-26_B_EnrollmentandPersistence.csv","date_read":D,
  "B1_total_undergrad":{"value":1617,"item":"B1","note":"All/Total row: men 733 (717 FT + 16 PT) + women 884 (879 FT + 5 PT); from dashboard CSV export"},
  "C1":None,"C9":None,"I2_ratio":None,"I3":None,"B_grad":None,"B22_retention":None,
  "notes":"Pomona publishes 2024-25 and 2025-26 only as Tableau dashboards (no PDF). The public .csv export returns only the first sheet of each dashboard (B1 and I-faculty table); I could not enumerate the other dashboard names (C, B-grad, I3) without probing the Tableau portal API, which the permission system denied. First-time first-year FT men 199 + women 221 = 420."},
 "2024-2025":{"exists":True,"source_url":"https://tableau.campus.pomona.edu/views/CDS2024-25/A_GeneralInformation","local_file":base+"pomona/2024-25_B_EnrollmentandPersistence.csv","date_read":D,
  "B1_total_undergrad":{"value":1766,"item":"B1","note":"All/Total row: men 783 + women 983; from dashboard CSV export"},
  "C1":None,"C9":None,"I2_ratio":None,"I3":None,"B_grad":None,"B22_retention":None,
  "notes":"Same limitation as 2025-26; only B1 and I-faculty counts obtained. First-time first-year FT men 194 + women 242 = 436."}},
 "refusals":["Pomona: Tableau dashboard views other than the first sheet not reachable via public csv; portal API probe denied by permission system, not retried"]}
out["amherst"]={"slug":"amherst","college":"Amherst College","cds_index_url":"https://www.amherst.edu/about/facts/common_data_sets","years":{
 "2025-2026":{"exists":None,"source_url":None,"local_file":None,"date_read":D,"notes":"Not retrieved: amherst.edu returns HTTP 405 with x-amzn-waf-action: captcha (bot check). Not worked around."},
 "2024-2025":{"exists":None,"source_url":None,"local_file":None,"date_read":D,"notes":"Not retrieved, same bot check."}},
 "refusals":["https://www.amherst.edu/about/facts/common_data_sets -> HTTP 405, WAF captcha (curl)","same URL via WebFetch -> HTTP 405","https://amherst.edu/system/files/A%2520General%2520Information_5.pdf -> HTTP 405 (curl)"]}
for s,o in out.items():
    json.dump(o,open(base+s+"/cds_extract.json","w"),indent=1)
    print(s,"ok")
