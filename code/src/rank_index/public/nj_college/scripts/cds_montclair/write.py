import json
from decimal import Decimal,ROUND_HALF_UP
def r1(a,b): return float((Decimal(a)*100/Decimal(b)).quantize(Decimal('0.1'),ROUND_HALF_UP))
def w(a,b): return int((Decimal(a)*100/Decimal(b)).quantize(Decimal('1'),ROUND_HALF_UP))
base="/Users/heuremen/bones-forge/rank_index/public/nj_college/cds/montclair/"
def yr(y,fn,b1,gt,app,adm,enr,sat,satn,ratio,i3,cohort,adj,c4,c6,p6,p6note,ret,retc,n):
    s=sum(i3[:7]); assert s==i3[7]
    return {"exists":True,"source_url":"http://irdata.montclair.edu/institutionalresearch/CDS/"+fn.replace(" ","%20"),"local_file":base+fn.replace(" ","_"),"date_read":"2026-11-10",
    "B1_total_undergrad":{"value":b1,"item":"B1","note":"Total Undergraduate Students (all, degree and non-degree); grand total all students %d"%gt},
    "C1":{"applicants":app,"admits":adm,"enrolled":enr,"acceptance_pct_1dp":r1(adm,app),"acceptance_pct_whole":w(adm,app)},
    "C9":{"SAT_comp_25":sat[0],"SAT_comp_75":sat[2],"SAT_comp_50":sat[1],"ACT_comp_25":None,"ACT_comp_75":None,"pct_submit_SAT":satn[0],"num_submit_SAT":satn[1],"pct_submit_ACT":None},
    "I2_ratio":ratio,
    "I3":dict(zip(["2-9","10-19","20-29","30-39","40-49","50-99","100+","total"],i3),pct_under_20_1dp=r1(i3[0]+i3[1],i3[7])),
    "B_grad":{"cohort":cohort,"B6_adj_cohort":adj,"B7_4yr":c4,"B9_6yr":c6,"B10_6yr_rate_printed":p6,"rate_4yr_1dp":r1(c4,adj),"pell_6yr_rate":p6note},
    "B22_retention":{"value":ret,"cohort":retc},"notes":n}
d={"slug":"montclair","college":"Montclair State University","cds_index_url":"https://inside.montclair.edu/administration/institutional-research-and-effectiveness-office/institutional-reports/common-data-set",
"years":{
"2025-2026":yr("2025-2026","CDS 2025-2026.pdf",19048,23586,26224,23443,3816,(850,1000,1160),("10%",364),"17 to 1 (based on 20950 students and 1203 faculty)",[416,1056,1253,1098,72,49,13,3957],"Fall 2019",3081,1520,2021,"65.60%","63.79%","79.26% (3310/4176)","Fall 2024 cohort","C1 applicants/admits sum male+female (10589+15635; 9288+14155), match residency table; enrolled 1704+2112. ACT composite and pct ACT blank in file (percent 10% SAT, ACT row empty). B6 final cohort 3081 (initial 3082). Pell 6yr = Recipients of Federal Pell Grant column (835/1309). Also in file: Fall 2018 cohort."),
"2024-2025":yr("2024-2025","CDS 2024-2025.pdf",18712,23375,26257,23076,4109,(930,1080,1200),("9%",353),"17.6 to 1 (based on 20,758 students and 1177 faculty)",[427,1025,1233,1072,58,54,12,3881],"Fall 2018",3166,1459,2047,"65%","62% (printed whole percent; 977/1567)","78%","Fall 2023 cohort","C1 applicants 10368+15889, admits 8886+14190; enrolled 4109 (FT+PT). ACT composite blank. Grad rates printed as whole percents in this file.")},
"refusals":[]}
json.dump(d,open(base+"cds_extract.json","w"),indent=1)
for y,v in d["years"].items(): print(y,v["C1"],v["I3"]["pct_under_20_1dp"],v["B_grad"]["rate_4yr_1dp"])
