import json,math
def pct(a,b): return round(a/b*100+1e-9,1)
def whole(a,b): return int(math.floor(a/b*100+0.5))
def year(url,local,B1,b1note,app,adm,enr,c9,i2,i3,grad,ret,notes):
    t=sum(i3[:7]); assert t==i3[7],(t,i3)
    k=["2-9","10-19","20-29","30-39","40-49","50-99","100+","total"]
    d=dict(zip(k,i3)); d["pct_under_20_1dp"]=pct(i3[0]+i3[1],i3[7])
    return {"exists":True,"source_url":url,"local_file":local,"date_read":"2026-11-10",
     "B1_total_undergrad":{"value":B1,"item":"B1","note":b1note},
     "C1":{"applicants":app,"admits":adm,"enrolled":enr,"acceptance_pct_1dp":pct(adm,app),"acceptance_pct_whole":whole(adm,app)},
     "C9":c9,"I2_ratio":i2,"I3":d,
     "B_grad":dict(grad,rate_4yr_1dp=pct(grad["B7_4yr"],grad["B6_adj_cohort"])),
     "B22_retention":ret,"notes":notes}
base="/Users/heuremen/bones-forge/rank_index/public/college/cds/"
def w(slug,obj): json.dump(obj,open(base+slug+"/cds_extract.json","w"),indent=1)
nu="https://www.enrollment.northwestern.edu/data/"
w("northwestern",{"slug":"northwestern","college":"Northwestern University","cds_index_url":"https://www.enrollment.northwestern.edu/data/common-data-set.html","years":{
"2025-2026":year(nu+"2025-2026.pdf",base+"northwestern/2025-2026.pdf",9039,"B1 'Total All Undergraduates' 9,039 (4,207 M + 4,802 F + 30 unknown); grand total all students 23,312",52676,3933,2139,
 {"SAT_comp_25":1520,"SAT_comp_75":1560,"ACT_comp_25":34,"ACT_comp_75":35,"pct_submit_SAT":48,"pct_submit_ACT":25},"6 to 1 (based on 8,925 students and 1,401 faculty)",[1061,753,208,133,45,121,42,2363],
 {"cohort":"Fall 2019","B6_adj_cohort":2006,"B7_4yr":1712,"B9_6yr":1928,"B10_6yr_rate_printed":"96%","pell_6yr_rate":"96% printed (394/409)"},
 {"value":"98%","cohort":"Fall 2024 (2,045 of 2,097)"},
 "C1 applicants = 25,258 M + 27,390 F + 28 unknown; admits 1,828 M + 2,105 F; enrolled 1,000 M + 1,139 F. Pell 6yr count 394 of 409."),
"2024-2025":year(nu+"2024-2025.pdf",base+"northwestern/2024-2025.pdf",9060,"B1 'Total All Undergraduates' 9,060; grand total all students 23,431",49474,3806,2105,
 {"SAT_comp_25":1510,"SAT_comp_75":1560,"ACT_comp_25":34,"ACT_comp_75":35,"pct_submit_SAT":46,"pct_submit_ACT":23},"6 to 1 (based on 8923 students and 1413 faculty)",[948,728,203,126,51,107,41,2204],
 {"cohort":"Fall 2018","B6_adj_cohort":1929,"B7_4yr":1609,"B9_6yr":1835,"B10_6yr_rate_printed":"95%","pell_6yr_rate":"94% printed (372/397)"},
 {"value":"98%","cohort":"Fall 2023"},
 "CDS 2024-25 reports Fall 2018 cohort (B grid). C1 applicants = 23,774 men + 25,686 women + 14 another gender + 0 unknown; admits 1,735 + 2,070 + 1; enrolled 977 + 1,127 + 1.")},
"refusals":[]})
uc="https://data.uchicago.edu/files/"
w("uchicago",{"slug":"uchicago","college":"University of Chicago","cds_index_url":"https://data.uchicago.edu/common-data-set","years":{
"2025-2026":year(uc+"2026/08/CDS_2025-2026_to_publish-1.pdf",base+"uchicago/CDS_2025-2026_to_publish-1.pdf",7453,"B1 'Total all undergraduates' 7,453 (4,202 M + 3,251 F); grand total all students 16,406",45533,2039,1786,
 {"SAT_comp_25":1500,"SAT_comp_75":1560,"ACT_comp_25":34,"ACT_comp_75":35,"pct_submit_SAT":57,"pct_submit_ACT":25},"7 to 1 (based on 10979 students and 1587 faculty)",[798,465,190,92,39,91,19,1694],
 {"cohort":"Fall 2019","B6_adj_cohort":1724,"B7_4yr":1468,"B9_6yr":1638,"B10_6yr_rate_printed":"95.0%","pell_6yr_rate":"95.2% printed (218/229)"},
 {"value":"99%","cohort":"Fall 2024 (1,715 of 1,726)"},
 "File's page headers read 'Common Data Set 2024-2025' but body text says Fall 2025/2025-2026 and cohorts Fall 2019/2024. C1 applicants = 19,929 M + 24,578 F + 1,026 unknown; admits 1,169 M + 870 F; enrolled 1,042 M + 744 F. Extracted with pypdf layout mode."),
"2024-2025":year(uc+"2025/08/CDS_2024-2025_to_publish.pdf",base+"uchicago/CDS_2024-2025_to_publish.pdf",7519,"B1 'Total all undergraduates' 7,519 (4,085 M + 3,434 F); grand total all students 16,221",43612,1955,1726,
 {"SAT_comp_25":1510,"SAT_comp_75":1560,"ACT_comp_25":34,"ACT_comp_75":35,"pct_submit_SAT":49,"pct_submit_ACT":27},"5 to 1 (based on 7515 students and 1565 faculty)",[758,545,182,45,32,86,26,1674],
 {"cohort":"Fall 2018","B6_adj_cohort":1808,"B7_4yr":1577,"B9_6yr":1733,"B10_6yr_rate_printed":"95.9%","pell_6yr_rate":"91.7% printed (187/204)"},
 {"value":"99.00%","cohort":"Fall 2023"},
 "C1 applicants = 19,195 men + 23,636 women + 0 another + 781 unknown; admits 1,070 + 885; enrolled 955 + 771. I2 note: 5 to 1 is printed against 7,515 students/1,565 faculty.")},
"refusals":[]})
for s,n,idx in (("jhu","Johns Hopkins University","https://oira.jhu.edu/common-data-set"),("williams","Williams College","https://www.williams.edu/institutional-research/common-data-set/")):
    ref=[idx+" -> curl HTTP 403 (bot check/block page) and WebFetch HTTP 403; not worked around"]
    if s=="jhu": ref+=["https://oira.jhu.edu/wp-content/uploads/CDS_2024-2025_JHU-2.pdf -> curl HTTP 403 (URL from search result)","https://oira.jhu.edu/wp-content/uploads/2025-2026-CDS-Johns-Hopkins-University-v2.pdf -> curl HTTP 403 (URL cited by a third-party site, unverified)"]
    else: ref+=["https://www.williams.edu/institutional-research/files/2026/04/Williams-CDS-2025-2026-V2.pdf -> curl HTTP 403 (URL cited by a third-party site, unverified)"]
    w(s,{"slug":s,"college":n,"cds_index_url":idx,"years":{y:{"exists":None,"source_url":None,"local_file":None,"date_read":"2026-11-10","notes":"Own IR site refused automated access (403); file not downloaded, no figures recorded. Existence not confirmed from the college's own site."} for y in ("2025-2026","2024-2025")},"refusals":ref})
