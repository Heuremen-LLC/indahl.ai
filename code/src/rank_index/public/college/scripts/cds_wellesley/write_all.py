import json
B="/Users/heuremen/bones-forge/rank_index/public/college/cds/"
D="2026-11-10"
def pct(a,b):
    x=a/b*100; import decimal as d
    return float(d.Decimal(x).quantize(d.Decimal('0.1'),rounding=d.ROUND_HALF_UP)), int(d.Decimal(x).quantize(d.Decimal('1'),rounding=d.ROUND_HALF_UP))
def c1(a,b,c):
    p1,pw=pct(b,a); return {"applicants":a,"admits":b,"enrolled":c,"acceptance_pct_1dp":p1,"acceptance_pct_whole":pw}
def i3(l):
    t=l[-1]; k=["2-9","10-19","20-29","30-39","40-49","50-99","100+"]
    d=dict(zip(k,l[:7])); d["total"]=t; d["pct_under_20_1dp"]=pct(l[0]+l[1],t)[0]; return d
def gr(coh,a,b4,g,pr,pellp,note=None):
    return {"cohort":coh,"B6_adj_cohort":a,"B7_4yr":b4,"B9_6yr":g,"B10_6yr_rate_printed":pr,"rate_4yr_1dp":pct(b4,a)[0],"pell_6yr_rate":pellp}
out={}
# Wellesley
w={"slug":"wellesley","college":"Wellesley College","cds_index_url":"https://www.wellesley.edu/about-us/offices-departments/office-of-institutional-research/public-data","years":{},"refusals":[]}
w["years"]["2025-2026"]={"exists":True,"source_url":"https://wellesley-college.files.svdcdn.com/production/administrative-departments/OIR/CDS_2025-2026-FINAL.pdf?dm=1773253066","local_file":B+"wellesley/CDS_2025-2026-FINAL.pdf","date_read":D,
 "B1_total_undergrad":{"value":2366,"item":"B1","note":"Total all undergraduates; grand total all students 2,366 (no graduate students). FT 2,303 + PT 63 (F 31 men, 2,329 women, 6 unknown)"},
 "C1":c1(8506,1258,576),
 "C9":{"SAT_comp_25":1460,"SAT_comp_75":1540,"ACT_comp_25":33,"ACT_comp_75":35,"pct_submit_SAT":44,"pct_submit_ACT":18},
 "I2_ratio":"8 to 1 (based on 2324 students)","I3":i3([71,260,138,23,2,2,0,496]),
 "B_grad":gr("Fall 2019",612,481,556,"91%",89,None),
 "B22_retention":{"value":"95.03%","cohort":"Fall 2024 entering cohort (583 cohort, 554 retained, as of Fall 2025)"},
 "notes":"Total-column B4-B11: A=612, B exclusions 0, C=612, D(4yr)=481 (106 Pell+58 sub+317 neither), G=556, H printed 91%. Pell 6yr printed 89% (125 of 141). Text extracted with pypdf layout mode; I-3 sections row = first table (sections), subsections row separate."}
w["years"]["2024-2025"]={"exists":True,"source_url":"https://wellesley-college.files.svdcdn.com/production/administrative-departments/OIR/CDS_2024-2025-FINAL-1.pdf?dm=1762194243","local_file":B+"wellesley/CDS_2024-2025-FINAL-1.pdf","date_read":D,
 "B1_total_undergrad":{"value":2407,"item":"B1","note":"Total all undergraduates = grand total (no grad). FT 2,310 (3 men,2305 women,2 unk... see source), PT 97"},
 "C1":c1(8714,1224,583),
 "C9":{"SAT_comp_25":1470,"SAT_comp_75":1550,"ACT_comp_25":33,"ACT_comp_75":35,"pct_submit_SAT":43,"pct_submit_ACT":18},
 "I2_ratio":"7.5 to 1 (based on 2342 students and 313 faculty)","I3":i3([98,248,145,18,2,1,0,512]),
 "B_grad":gr("Fall 2018",614,477,562,"0.915309446 (91.5%)",91.5),
 "B22_retention":{"value":"96.50%","cohort":"Fall 2023 entering cohort (as of Fall 2024)"},
 "notes":"Pell 6yr = 130/142 (printed 0.9155). Applicants all women (men 0)."}
w["years"]["2024-2025"]["B1_total_undergrad"]["note"]="Total all undergraduates 2,407 = grand total all students (graduate 0); degree-seeking undergrads 2,300"
json.dump(w,open(B+"wellesley/cds_extract.json","w"),indent=1)
# HMC
h={"slug":"harveymudd","college":"Harvey Mudd College","cds_index_url":"https://www.hmc.edu/institutional-research/institutional-statistics/common-data-set/","years":{},"refusals":[]}
h["years"]["2025-2026"]={"exists":True,"source_url":"https://www.hmc.edu/institutional-research/wp-content/uploads/sites/42/2026/03/CDS-HMC-2025.2026_shared.pdf","local_file":B+"harveymudd/CDS-HMC-2025.2026_shared.pdf","date_read":D,
 "B1_total_undergrad":{"value":913,"item":"B1","note":"EN_TOT_UG_N; grand total 913 (graduate 0). Values read from PDF form fields (AcroForm), not visible text layer"},
 "C1":c1(5217,643,236),
 "C9":{"SAT_comp_25":1500,"SAT_comp_75":1560,"ACT_comp_25":35,"ACT_comp_75":36,"pct_submit_SAT":55,"pct_submit_ACT":21},
 "I2_ratio":"8 to 1 (911.67 students / 106.98 FTE faculty)","I3":i3([70,71,49,24,7,8,5,234]),
 "B_grad":gr("Fall 2019",224,185,209,"93.03",87.10),
 "B22_retention":{"value":"95.24%","cohort":"Fall 2024 cohort, 231 cohort, 220 retained (as of Fall 2025)"},
 "notes":"DISCREPANCY: printed six-year rate 93.03 but 209/224 = 93.30. 4yr/5yr/6yr completions 185/20/4. Pell cohort 31, 27 completed (87.10). Applicants men 3452 women 1761 unk 4; admits 276/365/2; enrolled 109/125/2. Test optional policy text in file. ACT submit 21% (49), SAT 55% (130)."}
h["years"]["2024-2025"]={"exists":True,"source_url":"https://www.hmc.edu/institutional-research/wp-content/uploads/sites/42/2024/12/CDS-2024-2025-SharedtoWeb.pdf","local_file":B+"harveymudd/CDS-2024-2025-SharedtoWeb.pdf","date_read":D,
 "B1_total_undergrad":{"value":921,"item":"B1","note":"EN_TOT_UG_N; grand total 921. Values read from PDF form fields"},
 "C1":c1(5094,645,231),
 "C9":{"SAT_comp_25":1510,"SAT_comp_75":1560,"ACT_comp_25":34,"ACT_comp_75":36,"pct_submit_SAT":52,"pct_submit_ACT":16},
 "I2_ratio":"8 to 1 (920 students, 110 faculty)","I3":i3([74,77,54,19,7,6,6,243]),
 "B_grad":gr("Fall 2018",234,189,215,"92 (integer as printed)",94),
 "B22_retention":{"value":"96 (printed integer)","cohort":"Fall 2023 entering cohort (as of Fall 2024); no counts in file"},
 "notes":"Computed 215/234=91.9; Pell 30/32=93.75 printed 94. Applicants men 3424 women 1664 nonbinary 6; admits 293/351/1; enrolled 115/116. SAT submit 119, ACT 36."}
json.dump(h,open(B+"harveymudd/cds_extract.json","w"),indent=1)
# USMA
u={"slug":"usma","college":"United States Military Academy (West Point)","cds_index_url":"https://www.westpoint.edu/about/institutional-accreditation-and-assessment","years":{},"refusals":["https://s3.amazonaws.com/usma-media/inline-images/about/g5/G5OIR_CDS_2025-2026.pdf (guessed URL, not linked on USMA page) -> HTTP 403 AccessDenied from S3; not worked around"]}
u["years"]["2025-2026"]={"exists":False,"source_url":None,"local_file":None,"date_read":D,"notes":"USMA CDS page (westpoint.edu/about/institutional-accreditation-and-assessment) lists only CDS 2024-25, 2023-24, 2022-23, 2021-22. No 2025-26 posted as of date read."}
u["years"]["2024-2025"]={"exists":True,"source_url":"https://s3.amazonaws.com/usma-media/inline-images/about/g5/G5OIR_CDS_2024-2025.pdf","local_file":B+"usma/G5OIR_CDS_2024-2025.pdf","date_read":D,
 "B1_total_undergrad":{"value":4473,"item":"B1","note":"EN_TOT_UG_N; read from PDF form fields"},
 "C1":c1(12316,1534,1195),
 "C9":{"SAT_comp_25":1210,"SAT_comp_75":1420,"ACT_comp_25":27,"ACT_comp_75":33,"pct_submit_SAT":68,"pct_submit_ACT":32},
 "I2_ratio":"6.22 to 1 (4473 students, 718 faculty)","I3":i3([314,1566,62,2,0,0,0,1944]),
 "B_grad":gr("Fall 2018",1190,1003,1036,"87",None),
 "B22_retention":{"value":"95 (printed integer)","cohort":"Fall 2023 entering cohort (as of Fall 2024); no counts in file"},
 "notes":"Initial cohort 1191 less 1 exclusion = 1190; completions 1003/30/3. No Pell/Stafford data (all zeros, all in no-aid column), Pell rate null. Applicants men 8549 women 3771; admits 1175/359; enrolled 931/264. SAT submit 817 (68%), ACT 378 (32%)."}
json.dump(u,open(B+"usma/cds_extract.json","w"),indent=1)
# USNA
n={"slug":"usna","college":"United States Naval Academy","cds_index_url":"https://www.usna.edu/IR/data-rankings.php","years":{"2025-2026":{"exists":False,"source_url":None,"local_file":None,"date_read":D},"2024-2025":{"exists":False,"source_url":None,"local_file":None,"date_read":D}},
 "refusals":[],
 "notes":"USNA Institutional Research pages (usna.edu/IR/, /IR/data-rankings.php, Research Resources, Midshipmen Achievement) link no Common Data Set for any year; data-rankings page offers Student Right to Know, Admissions Class Profile, Graduating Class Profile, Accreditations. Web search of usna.edu found no CDS file. What USNA itself publishes instead (not a CDS): Class of 2029 class portrait (https://www.usna.edu/Admissions/_files/documents/ClassPortrait.pdf, saved at cds/usna/ClassPortrait.pdf): 16,077 applications, 1,416 offers of appointment, 1,197 enrolled (I-Day 26 June 2025); middle 50% SAT EBRW 600-710, SAT Math 610-720, ACT English+Reading 49-66, ACT Math 26-32 (as reported by web search summary, not independently re-read from PDF layout)."}
json.dump(n,open(B+"usna/cds_extract.json","w"),indent=1)
