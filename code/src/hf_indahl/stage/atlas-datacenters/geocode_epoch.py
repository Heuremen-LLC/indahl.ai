"""geocode_epoch.py: US Census geocoder (public, free) for the Epoch AI data center addresses. Writes raw/epoch_us_geocoded.json. Addresses Census cannot match stay without coordinates and are listed, not guessed."""
import csv,json,urllib.parse,subprocess,time
rows=[r for r in csv.DictReader(open('raw/epoch/data_centers.csv',encoding='utf-8')) if r['Country']=='United States']
out=[]
for r in rows:
    a=r['Address'].strip(); res=dict(name=r['Name'],address=a,lat=None,lon=None,match=None)
    if a:
        u='https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?benchmark=Public_AR_Current&format=json&address='+urllib.parse.quote(a)
        p=subprocess.run(['curl','-s','-m','30','-A','heuremen-atlas/1.0',u],capture_output=True,text=True)
        try:
            m=json.loads(p.stdout)['result']['addressMatches']
            if m: res.update(lat=m[0]['coordinates']['y'],lon=m[0]['coordinates']['x'],match=m[0]['matchedAddress'])
        except Exception: pass
        time.sleep(0.3)
    res.update({k:r[k] for k in ('Current power (MW)','Current H100 equivalents','Current total capital cost (2025 USD billions)','Owner','Project','Current chip types')})
    out.append(res)
json.dump(out,open('raw/epoch_us_geocoded.json','w'),indent=0)
print(len(out),'matched',sum(1 for o in out if o['lat']),'no address',sum(1 for o in out if not o['address']))
