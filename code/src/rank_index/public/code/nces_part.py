import json,os,sys
base=os.path.expanduser('~/bones-forge/rank_index/public')
ids={"470369002247":(47,"TN"),"180002100319":(18,"IN"),"421899003808":(42,"PA"),"320002100680":(32,"NV"),"110003000131":(11,"DC"),"510126002034":(51,"VA"),"130255003553":(13,"GA"),"481623005865":(48,"TX"),"530423003432":(53,"WA"),"062271013971":(6,"CA")}
CODES="Urban Institute codes: -1 = missing/not reported, -2 = not applicable, -3 = suppressed (educationdata.urban.org documentation)"
out={}
for nid,(f,st) in ids.items():
  figs=[]; sy={2023:"2023-24",2024:"2024-25"}
  for y in (2023,2024):
    fn=f"dir_{y}_fips{f}_p1.json"
    rows=[r for r in json.load(open(f"{base}/files/nces/{fn}"))['results'] if r['ncessch']==nid]
    r=rows[0]
    url=f"https://educationdata.urban.org/api/v1/schools/ccd/directory/{y}/?fips={f}"
    if y==2023: out[nid]={"state":st,"ccd_name":r['school_name'],"lea":r['lea_name'],"seasch":r['seasch'],"state_leaid":r['state_leaid'],"grades":f"{r['lowest_grade_offered']}-{r['highest_grade_offered']}"}
    for k in ["enrollment","teachers_fte","free_lunch","reduced_price_lunch","free_or_reduced_price_lunch","direct_certification","lunch_program"]:
      v=r.get(k); note=""
      if isinstance(v,(int,float)) and v<0: note=CODES
      if v is None: note="null in API response (not yet released for this year)"
      if k=="lunch_program": note="CCD lunch_program code (1=NSLP without Provision, 2=NSLP under CEP/Provision; see Urban codebook)"
      if k=="free_lunch" and nid=="421899003808": note="CCD reports free = total enrollment; lunch_program 2 (school-wide provision, e.g. CEP)"
      figs.append({"figure":f"CCD {k}","value":v,"year":sy[y],"source_url":url,"file":f"files/nces/{fn}","row_or_table":f"results[] where ncessch=={nid}","date_read":"2026-11-10","note":note})
    g=0; parts={}
    for gr in (9,10,11,12):
      e=json.load(open(f"{base}/files/nces/enroll/enr_{y}_g{gr}_{nid}.json"))['results'][0]['enrollment']
      parts[gr]=e
      figs.append({"figure":f"CCD enrollment grade {gr}","value":e,"year":sy[y],"source_url":f"https://educationdata.urban.org/api/v1/schools/ccd/enrollment/{y}/grade-{gr}/?ncessch={nid}&sex=99&race=99","file":f"files/nces/enroll/enr_{y}_g{gr}_{nid}.json","row_or_table":"results[0]","date_read":"2026-11-10","note":""})
  out[nid]["nces_figures"]=figs
json.dump(out,open(f"{base}/parts/nces.json","w"),indent=1)
print("ok")
