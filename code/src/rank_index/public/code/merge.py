import json,os,glob
B=os.path.expanduser('~/bones-forge/rank_index/public')
order=[("TN","470369002247","Central Magnet School","Murfreesboro","Rutherford County Schools"),
("IN","180002100319","Signature School","Evansville","Signature School Inc (charter)"),
("PA","421899003808","Julia R. Masterman Secondary School","Philadelphia","School District of Philadelphia"),
("NV","320002100680","Davidson Academy","Reno","Davidson Academy"),
("DC","110003000131","School Without Walls High School","Washington","DC Public Schools"),
("VA","510126002034","Thomas Jefferson High School for Science and Technology","Alexandria","Fairfax County Public Schools"),
("GA","130255003553","Gwinnett School of Mathematics, Science and Technology","Lawrenceville","Gwinnett County Public Schools"),
("TX","481623005865","School for the Talented and Gifted","Dallas","Dallas ISD"),
("WA","530423003432","Nikola Tesla STEM High School","Redmond","Lake Washington School District"),
("CA","062271013971","Science Academy STEM Magnet","North Hollywood","Los Angeles Unified")]
nces=json.load(open(f"{B}/parts/nces.json"))
br=json.load(open(f"{B}/parts/blueribbon.json")); brs=json.load(open(f"{B}/parts/blueribbon_supp.json"))
out=[]
for i,(st,nid,name,city,dist) in enumerate(order):
  n=nces[nid]
  p=f"{B}/parts/{st}.json"
  sp=json.load(open(p)) if os.path.exists(p) else {"figures":[],"refused":[],"sources":[],"missing":"state part not produced"}
  b=[br[i]]
  supmap={"DC":"School Without Walls","TX":"School for the Talented","GA":"Gwinnett","TN":"Central Magnet","IN":"Signature"}
  bs=[x for x in brs if st in supmap and x['school'].startswith(supmap[st])]
  out.append({"school":name,"city":city,"state":st,"district":dist,
   "ids":{"ncessch":nid,"nces_seasch":n["seasch"],"nces_state_leaid":n["state_leaid"],"state_id_used_by_state":sp.get("state_id_used_by_state"),"ccd_name":n["ccd_name"],"ccd_grades_offered":n["grades"],
          "source_url":f"https://educationdata.urban.org/api/v1/schools/ccd/directory/2023/","note":"Urban Institute Education Data API returns NCES CCD values; API 'year' 2023 = school year 2023-24, 2024 = 2024-25"},
   "nces_ccd":n["nces_figures"],
   "state_figures":sp.get("figures",[]),
   "blue_ribbon":{"official_reads":bs,"agent_search":b[0] if b else None},
   "refused":sp.get("refused",[]),"sources":sp.get("sources",[])})
json.dump(out,open(f"{B}/hs_public.json","w"),indent=1,ensure_ascii=False)
print(len(out),[ (o['state'],len(o['state_figures']),len(o['blue_ribbon']['official_reads']),bool(o['blue_ribbon']['agent_search'])) for o in out])
