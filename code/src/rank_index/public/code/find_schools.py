import json,glob,re,sys
pats={47:r'central magnet',18:r'signature',42:r'masterman',32:r'davidson',11:r'without walls',51:r'thomas jefferson',13:r'gwinnett school of math|mathematics, science',48:r'talented',53:r'tesla',6:r'science academy'}
for f,p in pats.items():
  for fn in sorted(glob.glob(f'files/nces/dir_*_fips{f}_p*.json')):
    for r in json.load(open(fn))['results']:
      if re.search(p,r['school_name'],re.I):
        print(fn.split('/')[-1],r['ncessch'],r['seasch'],r['school_name'],r['lea_name'],r['city_location'],r['enrollment'],r['teachers_fte'],r['free_lunch'],r['reduced_price_lunch'],r['free_or_reduced_price_lunch'],r['direct_certification'],r['lunch_program'])
