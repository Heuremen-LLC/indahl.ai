import json, re, os, urllib.request, urllib.error, datetime as D, hashlib
D0=os.path.dirname(os.path.abspath(__file__))
T=json.load(open('/Users/heuremen/bones-forge/nodes_repo/drift/targets.json'))
now=D.datetime.now(D.timezone.utc)
UA={'User-Agent':'site-pass-A (read-only)'}
def stamp(d):
    s = d.get('updated') or d.get('read')
    if not isinstance(s,str): return None, s
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})', s)
    if m: return D.datetime(*map(int,m.groups()),tzinfo=D.timezone.utc), s
    m = re.match(r'(\d{1,2}) ([A-Za-z]{3}) (\d{2}):(\d{2})', s)
    if m:
        mo=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'].index(m.group(2).lower())+1
        t=D.datetime(now.year,mo,int(m.group(1)),int(m.group(3)),int(m.group(4)),tzinfo=D.timezone.utc)
        return (t if t<=now+D.timedelta(hours=1) else t.replace(year=now.year-1)), s
    return None, s
out=[]
for f,lim in T['feeds']:
    u='https://indahl.ai/'+f+'?w=1'
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40); b=r.read(); code=r.status; ct=r.headers.get('content-type')
    except urllib.error.HTTPError as e: b=b''; code=e.code; ct=None
    except Exception as e: b=b''; code='ERR'; ct=None
    fn=f.replace('/','_')
    open(D0+'/feeds/'+fn,'wb').write(b)
    try: d=json.loads(b)
    except Exception: d=None
    st=None; raw=None
    if isinstance(d,dict): st,raw=stamp(d)
    age=round((now-st).total_seconds()/3600,2) if st else None
    state='NOSTAMP' if st is None else ('FRESH' if age<=lim else 'STALE')
    out.append((f,code,len(b),ct,raw,age,lim,state, sorted(d.keys())[:6] if isinstance(d,dict) else type(d).__name__))
for o in out: print(o)
print(now.isoformat())
