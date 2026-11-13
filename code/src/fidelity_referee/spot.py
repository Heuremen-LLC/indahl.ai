import json,urllib.request,os
key=open(os.path.expanduser('~/Documents/Heuremen LLC/ACCOUNTS/census_api_key.txt')).read().strip()
R={(r['ev'],r['st'],r['y']):r for r in json.load(open('my_rows.json'))}
FIPS={'Texas':'48','Louisiana':'22','Nevada':'32','Georgia':'13','Hawaii':'15','Delaware':'10','Ohio':'39','Vermont':'50','Florida':'12','Illinois':'17'}
spots=[('DIVORCE','Texas',2022),('DIVORCE','Louisiana',2022),('MARRIAGE','Nevada',2015),('DIVORCE','Georgia',2019),('MARRIAGE','Hawaii',2017),('DIVORCE','Delaware',2018),('MARRIAGE','Ohio',2013),('DIVORCE','Vermont',2021),('DIVORCE','Illinois',2016),('MARRIAGE','Florida',2023)]
for ev,st,y in spots:
    t='B12503' if ev=='DIVORCE' else 'B12501'
    u='https://api.census.gov/data/%d/acs/acs1?get=NAME,%s_005E,%s_005M,%s_010E,%s_010M&for=state:%s&key=%s'%(y,t,t,t,t,FIPS[st],key)
    try: d=json.loads(urllib.request.urlopen(u,timeout=60).read())[1]
    except Exception as e: d=type(e).__name__
    r=R[(ev,st,y)]; print(ev,st,y,'API',d[:5] if isinstance(d,list) else d,'| mine',r['me'],r['mmoe'],r['e'],r['moe'],'NCHS',r['n'],r['w'])
