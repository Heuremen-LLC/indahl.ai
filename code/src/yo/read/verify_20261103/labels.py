import sys,os,json,re,collections
sys.path.insert(0, os.path.expanduser('~/bones-forge/yo/read')); import yr_data as Y
M=Y.Q+'matrix_page/'; ro=open
Y.open=lambda p,*a,**k: ro(M+'list.json.pre-removal-20261102' if p.endswith('matrix_page/list.json') else p,*a,**k)
P=Y.papers(); c=collections.defaultdict(set)
for k,r,p in P:
    sp=Y.split(k); f4=[x.lower() for x in r.get('basis',{}).get('F4',[])]; t=Y.truth(r)
    if t['LINK']=='YES' and any(re.search(r'no url, doi or repositor|prints no data link|no (?:data|code)[^.]{0,40}(?:url|link|repositor)',x) for x in f4): c[('LINK wording missed',sp)].add(k)
    if t['REQUEST']=='YES' and all(re.search(r'none found|not found|no .{0,30}request',x) for x in f4 if 'request' in x): c[('REQUEST from negated line',sp)].add(k)
for key,v in sorted(c.items()): print(key,len(v), sorted(v) if key[1]=='TEST' else '')
