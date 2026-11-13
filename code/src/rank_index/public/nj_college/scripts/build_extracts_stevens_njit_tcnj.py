import json
from decimal import Decimal, ROUND_HALF_UP
def r1(a,b): return float((Decimal(a)*100/Decimal(b)).quantize(Decimal('0.1'),ROUND_HALF_UP))
def r0(a,b): return int((Decimal(a)*100/Decimal(b)).quantize(Decimal('1'),ROUND_HALF_UP))
def c1(a,ad,en): return {"applicants":a,"admits":ad,"enrolled":en,"acceptance_pct_1dp":r1(ad,a),"acceptance_pct_whole":r0(ad,a)}
def i3(v,tot):
    k=["2-9","10-19","20-29","30-39","40-49","50-99","100+"]
    d=dict(zip(k,v)); d["total"]=tot; d["pct_under_20_1dp"]=r1((v[0] or 0)+(v[1] or 0),tot); return d
def grad(cohort,b6,b7,b9,b10,pell,note=None):
    return {"cohort":cohort,"B6_adj_cohort":b6,"B7_4yr":b7,"B9_6yr":b9,"B10_6yr_rate_printed":b10,"rate_4yr_1dp":r1(b7,b6),"pell_6yr_rate":pell}
D="2026-11-10"
base="/Users/heuremen/bones-forge/rank_index/public/nj_college/cds/"
S={"slug":"stevens","college":"Stevens Institute of Technology","cds_index_url":"https://stevens.edu/office-of-institutional-research-and-effectiveness/facts-and-figures","years":{
"2025-2026":{"exists":True,"source_url":"https://assets.stevens.edu/mviowpldu823/3JLtvZX6pLFpRC0HPNpdiW/fa3d7b4c149e41797b0734a1a23e904b/CDS-2025-2026-PDF_Final.pdf","local_file":base+"stevens/CDS-2025-2026-PDF_Final.pdf","date_read":D,
 "B1_total_undergrad":{"value":4206,"item":"B1","note":"Total All Undergraduates box; grand total all students 8367"},
 "C1":c1(10499,5321,1104),
 "C9":{"SAT_comp_25":1370,"SAT_comp_75":1470,"ACT_comp_25":32,"ACT_comp_75":34,"pct_submit_SAT":36.14,"pct_submit_ACT":4.08,"SAT_n":399,"ACT_n":45},
 "I2_ratio":"11 to 1 (based on 4169 students and 388 faculty)",
 "I3":i3([88,232,263,127,133,122,17],982),
 "B_grad":dict(grad("Fall 2019",968,722,858,88.64,87.08),**{"also_fall_2018_cohort":"B6 1006, B7 714, B9 874, six-year 86.88, Pell 81.56"}),
 "B22_retention":{"value":94,"cohort":"Fall 2024 (1054 entered, 995 still enrolled Fall 2025)"},
 "notes":"Page headers in the PDF read 'Common Data Set 2024-2025' on some pages (stale header) but body text says Fall 2025. B22 printed as whole number 94; 995/1054 = 94.4%. Numbers read from rendered PDF pages."},
"2024-2025":{"exists":True,"source_url":"https://assets.stevens.edu/mviowpldu823/6fqw7BFObUMYxkM6oPdZax/28682c7721ed209b5d2e36303127b729/Common_Data_Set_2024-2025_June_-25_Update_PDF.pdf","local_file":base+"stevens/Common_Data_Set_2024-2025_June_-25_Update_PDF.pdf","date_read":D,
 "B1_total_undergrad":{"value":4236,"item":"B1","note":"Total All Undergraduates box; grand total 8469"},
 "C1":c1(10673,5078,1055),
 "C9":{"SAT_comp_25":1390,"SAT_comp_75":1490,"ACT_comp_25":31,"ACT_comp_75":34,"pct_submit_SAT":36.34,"pct_submit_ACT":6.45,"SAT_n":383,"ACT_n":68},
 "I2_ratio":"11 to 1 (student and faculty count boxes blank)",
 "I3":i3([91,218,320,120,114,130,9],1002),
 "B_grad":dict(grad("Fall 2018",1006,714,874,86.88,81.56),**{"also_fall_2017_cohort":"B6 761, B7 522, B9 684, six-year 89.88, Pell 87.41"}),
 "B22_retention":{"value":93.64,"cohort":"Fall 2023"},
 "notes":"File is the June 2025 update. Numbers read from rendered PDF pages."}},"refusals":[]}
N={"slug":"njit","college":"New Jersey Institute of Technology","cds_index_url":"https://www.njit.edu/oie/external-surveys","years":{
"2025-2026":{"exists":True,"source_url":"https://docs.google.com/spreadsheets/d/1Lo2Weqm-I98UN7QdHJ4Vf1zQBm21wPOK/edit (Google Sheet linked as '2025-26 (xlsx)' on the IR page; fetched via the sheet's /export?format=xlsx, no sign-in needed)","local_file":base+"njit/CDS_2025-2026.xlsx","date_read":D,
 "B1_total_undergrad":{"value":9827,"item":"B1","note":"B.176 Total all undergraduates; grand total 12309; undergrad men 6870 + women 2957"},
 "C1":c1(18170,12242,1832),
 "C9":{"SAT_comp_25":1220,"SAT_comp_75":1430,"ACT_comp_25":28,"ACT_comp_75":34,"pct_submit_SAT":44.3,"pct_submit_ACT":3.6,"SAT_n":812,"ACT_n":66},
 "I2_ratio":"15.8968481 to 1 as stored in sheet (based on 11096 students and 689 faculty); sheet display format not captured, rounds to 16 to 1",
 "I3":i3([160,349,597,428,156,82,10],1782),
 "B_grad":grad("Fall 2019",1291,631,931,72.1,68.0),
 "B22_retention":{"value":88.9,"cohort":"Fall 2024 (1554 entered, 1381 enrolled Fall 2025; stored 0.888674)"},
 "notes":"Printed six-year rate stored as 0.72115; Pell 310/456 = 0.6798. Previous-cohort (Fall 2018) block blank in this sheet. Read from the Answer Sheet tab."},
"2024-2025":{"exists":True,"source_url":"https://www.njit.edu/oie/sites/njit.edu.oie/files/CDS_2024-2025_v12.xlsx","local_file":base+"njit/CDS_2024-2025_v12.xlsx","date_read":D,
 "B1_total_undergrad":{"value":10200,"item":"B1","note":"Total all undergraduates; grand total 13247"},
 "C1":c1(15607,10156,1746),
 "C9":{"SAT_comp_25":1235,"SAT_comp_75":1460,"ACT_comp_25":28,"ACT_comp_75":31,"pct_submit_SAT":40,"pct_submit_ACT":3,"SAT_n":695,"ACT_n":60},
 "I2_ratio":"16 to 1 (based on 11166 students and 677 faculty)",
 "I3":i3([152,419,661,366,113,63,9],1783),
 "B_grad":grad("Fall 2018",1226,598,893,72.8,68.4),
 "B22_retention":{"value":90,"cohort":"Fall 2023 (stored as 0.9)"},
 "notes":"Percent submit stored as 0.4 and 0.03 (rounded in sheet). ACT 75th = 31 as entered (same as 50th). Fall 2017 block empty."}},"refusals":[]}
T={"slug":"tcnj","college":"The College of New Jersey","cds_index_url":"https://ira.tcnj.edu/reports/common-data-set-2/","years":{
"2025-2026":{"exists":True,"source_url":"https://ira.tcnj.edu/wp-content/uploads/sites/322/2026/04/CDS-2025-26-03262026.pdf","local_file":base+"tcnj/CDS-2025-26-03262026.pdf","date_read":D,
 "B1_total_undergrad":{"value":7433,"item":"B1","note":"Total all undergraduates; grand total 8288"},
 "C1":c1(12793,7865,1439),
 "C9":{"SAT_comp_25":1140,"SAT_comp_75":1330,"ACT_comp_25":25,"ACT_comp_75":30,"pct_submit_SAT":50,"pct_submit_ACT":3,"SAT_n":718,"ACT_n":29},
 "I2_ratio":"15 to 1 (based on 7862 students and 514 faculty)",
 "I3":i3([47,378,452,266,32,3,None],1178),
 "B_grad":grad("Fall 2019",1601,1178,1365,85.3,80.6),
 "B22_retention":{"value":89.7,"cohort":"Fall 2024 (1559 entered, 1398 retained)"},
 "notes":"Page headers read 'Common Data Set 2024-2025' (stale header), body says Fall 2025. 100+ cell blank in I3 sections row. Printed six-year rate stored as 0.85259 (shown 85.3). Fall 2018 block also present: B6 1548, B7 1174, B9 1329, printed 86%."},
"2024-2025":{"exists":True,"source_url":"https://ira.tcnj.edu/wp-content/uploads/sites/322/2025/04/CDS-2024-2025.pdf","local_file":base+"tcnj/CDS-2024-2025.pdf","date_read":D,
 "B1_total_undergrad":{"value":7435,"item":"B1","note":"Total all undergraduates; grand total 8141"},
 "C1":c1(12766,7959,1563),
 "C9":{"SAT_comp_25":1140,"SAT_comp_75":1320,"ACT_comp_25":26,"ACT_comp_75":31,"pct_submit_SAT":39,"pct_submit_ACT":3,"SAT_n":613,"ACT_n":46},
 "I2_ratio":"14 to 1 (based on 7323 students and 509 faculty)",
 "I3":i3([61,341,407,307,35,3,None],1154),
 "B_grad":grad("Fall 2018",1548,1174,1329,86,85),
 "B22_retention":{"value":91.32,"cohort":"Fall 2023"},
 "notes":"100+ cell blank in I3 sections row. Printed six-year rate and Pell rate are whole percents (86%, 85%). Fall 2017 block also present: B6 1537, B7 1161, six-year 85%."}},"refusals":[]}
S["refusals"]=[]
N["refusals"]=["https://www.njit.edu/institutional-research, /ir, /oir, /institutional-research-and-analytics -> HTTP 404 (guessed paths; real page is /oie/external-surveys)"]
T["refusals"]=["https://ira.tcnj.edu/?p=86 and https://ira.tcnj.edu/wp-content/uploads/sites/322/2025/04/CDS-2024-2025.pdf via curl -> HTTP 403 (site blocks curl). WebFetch (the one permitted retry) returned the PDFs, so no work-around used and no MANUAL_READS row needed. Local copies are the WebFetch-saved binaries."]
for d in (S,N,T): json.dump(d,open(base+d["slug"]+"/cds_extract.json","w"),indent=1)
for d in (S,N,T):
    for y,v in d["years"].items(): print(d["slug"],y,v["C1"],v["I3"]["pct_under_20_1dp"],v["B_grad"]["rate_4yr_1dp"])
