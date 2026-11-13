import json,os
from decimal import Decimal,ROUND_HALF_UP
def r1(x): return float(Decimal(str(x)).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP))
def acc(a,d,e):
    p=d/a*100
    return {"applicants":a,"admits":d,"enrolled":e,"acceptance_pct_1dp":r1(p),"acceptance_pct_whole":int(Decimal(str(p)).quantize(Decimal('1'),rounding=ROUND_HALF_UP))}
def i3(v):
    t=sum(v[:7]); assert t==v[7],(t,v)
    k=["2-9","10-19","20-29","30-39","40-49","50-99","100+","total"]
    d=dict(zip(k,v)); d["pct_under_20_1dp"]=r1((v[0]+v[1])/v[7]*100); return d
def gr(cohort,adj,four,six,rate,pell):
    return {"cohort":cohort,"B6_adj_cohort":adj,"B7_4yr":four,"B9_6yr":six,"B10_6yr_rate_printed":rate,"rate_4yr_1dp":r1(four/adj*100),"pell_6yr_rate":pell}
D="2026-11-10"
def yr(url,loc,b1,c1,c9,i2,i3v,g,b22,notes,b1note=None):
    return {"exists":True,"source_url":url,"local_file":loc,"date_read":D,"B1_total_undergrad":{"value":b1,"item":"B1","note":b1note},"C1":c1,"C9":c9,"I2_ratio":i2,"I3":i3(i3v),"B_grad":g,"B22_retention":b22,"notes":notes}
base="/Users/heuremen/bones-forge/rank_index/public/college/cds/"
out={}
out["caltech"]={"slug":"caltech","college":"California Institute of Technology","cds_index_url":"https://iro.caltech.edu/data","years":{
"2025-2026":yr("https://iro.caltech.edu/documents/35129/Caltech_CDS_2025-26_August_2026.pdf",base+"caltech/Caltech_CDS_2025-26_August_2026.pdf",971,
 acc(7772+3513,224+204,136+112),
 {"SAT_comp_25":None,"SAT_comp_75":None,"ACT_comp_25":35,"ACT_comp_75":36,"pct_submit_SAT":78.0,"pct_submit_ACT":22.0},
 "7 to 1 (printed, based on 2369 students and 333 faculty; file also notes undergraduate ratio 3 to 1 based on 971 undergraduates)",
 [78,94,44,21,13,13,10,273],
 gr("Fall 2019",235,182,211,89.79,92.59),
 {"value":96,"cohort":"Fall 2024 (218 cohort, 209 still enrolled)"},
 "C1 printed by gender only (men 7772, women 3513 applied; 224/204 admitted; 136/112 enrolled), totals are sums, no total line. C9 SAT composite row blank; SAT EBRW 760/780 and Math 790/800 printed. SAT n=190, ACT n=55. Pell 6yr: 25 of 27. Residency C1 table totals 0. Text digits read from rendered page images."),
"2024-2025":yr("https://iro.caltech.edu/documents/31491/Caltech_CDS_2024-2025_May_2025.pdf",base+"caltech/Caltech_CDS_2024-2025_May_2025.pdf",987,
 acc(9401+4446+9,166+190,218),
 {"SAT_comp_25":None,"SAT_comp_75":None,"ACT_comp_25":None,"ACT_comp_75":None,"pct_submit_SAT":None,"pct_submit_ACT":None},
 "3 to 1 (printed, based on 987 students and 337 faculty)",
 [97,114,32,24,11,12,9,299],
 gr("Fall 2018",231,178,218,94.40,96.30),
 {"value":97.40,"cohort":"Fall 2023"},
 "C9 entirely blank in file (all SAT/ACT percent, number and percentile cells empty). C1 applicants = 9401 men + 4446 women + 9 another gender; admits 166+190; enrolled 107+111. B1 total all undergraduates 987 (541 men + 446 women).")}}
out["stanford"]={"slug":"stanford","college":"Stanford University","cds_index_url":"https://irds.stanford.edu/data-findings/cds","years":{
"2025-2026":yr("https://drive.google.com/file/d/1GIPKgVj1d86dkmLkHI_mZVCk_iY6kiCp/view?usp=sharing (linked from IR page; downloaded via drive.google.com/uc?export=download&id=1GIPKgVj1d86dkmLkHI_mZVCk_iY6kiCp)",base+"stanford/stanford_cds_2025-26.pdf",7346,
 {"applicants":60646,"admits":2302,"enrolled":1839,"acceptance_pct_1dp":r1(2302/60646*100),"acceptance_pct_whole":4},
 {"SAT_comp_25":1520,"SAT_comp_75":1570,"ACT_comp_25":34,"ACT_comp_75":36,"pct_submit_SAT":55.57,"pct_submit_ACT":20.94},
 "10 to 1 (printed, based on 14,211 students and 1,359 faculty)",
 [599,627,168,80,61,144,80,1759],
 gr("Fall 2019",1698,770,1556,91.64,89.46),
 {"value":97.46,"cohort":"Fall 2024 (1,693 cohort, 1,650 still enrolled)"},
 "SAT n=1022, ACT n=385. B1 total all undergraduates 7,346 (3,604 men + 3,742 women). Grand total 18,121."),
"2024-2025":yr("https://drive.google.com/file/d/12MjIqdzzHiECf6hfRlbU3RmmIy14hl1H/view?usp=sharing (downloaded via drive.google.com/uc?export=download&id=12MjIqdzzHiECf6hfRlbU3RmmIy14hl1H)",base+"stanford/stanford_cds_2024-25.pdf",7904,
 {"applicants":57326,"admits":2067,"enrolled":1693,"acceptance_pct_1dp":r1(2067/57326*100),"acceptance_pct_whole":4},
 {"SAT_comp_25":1510,"SAT_comp_75":1570,"ACT_comp_25":34,"ACT_comp_75":35,"pct_submit_SAT":50.3,"pct_submit_ACT":19.0},
 "6 to 1 (printed, based on 7,671 students and 1,374 faculty)",
 [625,696,193,82,80,123,85,1884],
 gr("Fall 2018",1696,862,1559,91.9,87.6),
 {"value":98.2,"cohort":"Fall 2023"},
 "SAT n=857, ACT n=324. B1 total all undergraduates 7,904 (3,840 men + 4,064 women); grand total 18,625. B1 and I2 bases differ noticeably from 2025-26 file as printed.")}}
out["duke"]={"slug":"duke","college":"Duke University","cds_index_url":"https://ir.provost.duke.edu/duke-numbers/common-data-sets/","years":{
"2025-2026":yr("https://ir.provost.duke.edu/sites/default/files/CDS_PDF_2025-2026-20260622-website-published-version.pdf",base+"duke/CDS_PDF_2025-2026-20260622-website-published-version.pdf",6525,
 acc(25641+29900,1390+1520,833+916),
 {"SAT_comp_25":1510,"SAT_comp_75":1570,"ACT_comp_25":34,"ACT_comp_75":35,"pct_submit_SAT":48.0,"pct_submit_ACT":27.0},
 "7 to 1 (printed, based on 9263 students and 1283 faculty)",
 [464,651,178,113,47,76,42,1571],
 gr("Fall 2019",1730,1469,1663,96.1,91.1),
 {"value":97.0,"cohort":"Fall 2024 (1,740 cohort, 1,687 still enrolled)"},
 "C1 total-line cells in the file are blank, totals are sums of the male and female lines (25641+29900; 1390+1520; 833+916). SAT n=843, ACT n=473. B1 total all undergraduates 6,525 (3,063+3,460+2 unknown). Initial 2019 cohort 1,731 less 1 exclusion = 1,730."),
"2024-2025":yr("https://ir.provost.duke.edu/sites/default/files/CDS-2024-25-Final-2.pdf",base+"duke/CDS-2024-25-Final-2.pdf",6523,
 acc(24298+27497,1388+1569,824+916),
 {"SAT_comp_25":None,"SAT_comp_75":None,"ACT_comp_25":34,"ACT_comp_75":35,"pct_submit_SAT":48.0,"pct_submit_ACT":30.0},
 "5 to 1 (printed, based on 6490 students and 1244 faculty)",
 [470,690,182,101,57,80,45,1625],
 gr("Fall 2018",1740,1513,1684,96.8,95.6),
 {"value":98.0,"cohort":"Fall 2023"},
 "C1 men/women lines summed (a separate table with in-state/out-of-state/international columns also prints 51795 applied, 2957 admitted, 1740 enrolled). C9 SAT composite row blank in file; SAT EBRW 740/770 and Math 760/800 printed. SAT n=824, ACT n=526. Initial 2018 cohort 1,745 less 5 exclusions = 1,740. B1 total all undergraduates 6,523.")}}
out["penn"]={"slug":"penn","college":"University of Pennsylvania","cds_index_url":"https://ira.upenn.edu/penn-numbers/common-data-set","years":{
"2025-2026":{"exists":True,"source_url":"https://upenn.box.com/s/woo7d85yxpol6j9e2o121aucjc6dc1k5","local_file":None,"date_read":D,"notes":"Listed on Penn IRA page as '2025-26 Penn Common Data Set (PDF)' (Box file UPenn-Common-Data-Set-2025-26-June-2026.pdf) but not downloadable without a Box session/token (public.boxcloud.com content endpoint returned HTTP 401). No figures extracted."},
"2024-2025":{"exists":True,"source_url":"https://upenn.box.com/s/ckv4frz37rzxa4u6bdiv2h4yzykqm4ef","local_file":None,"date_read":D,"notes":"Listed on Penn IRA page as '2024-25 Penn Common Data Set (PDF)' (Box). Same Box block, not fetched. No figures extracted."}},
"refusals":["https://upenn.box.com/s/woo7d85yxpol6j9e2o121aucjc6dc1k5 -> Box shared-link viewer is JS-only; boxcloud content endpoint HTTP 401 (needs token). Stopped, no workaround.","https://upenn.box.com/s/ckv4frz37rzxa4u6bdiv2h4yzykqm4ef -> same Box wall, not attempted past the page"]}
for s,o in out.items():
    o.setdefault("refusals",[])
    json.dump(o,open(base+s+"/cds_extract.json","w"),indent=1)
    print(s,"ok")
