import re,html,json
B='/Users/heuremen/bones-forge/now_index/'
d=json.load(open(B+'data/research/longbets.json'));drop=json.load(open(B+'data/research/drop.json'))
def txt(n):
    s=open(B+'data/raw/longbets/%s.html'%n).read()
    s=re.sub(r'<(script|style)[^>]*>.*?</\1>','',s,flags=re.S)
    t=html.unescape(re.sub(r'<[^>]+>','\n',s));return re.sub(r'\n\s*\n+','\n',t)
for x in d:
    if 'longbets:%s'%x['lb_number'] in drop: continue
    t=txt(x['lb_number'])
    m=re.search(r'Duration\s*\n(.*?)\n\s*\((\d+)-(\d+)\)',t,re.S)
    pm=re.search(r'PREDICTOR\n(.*?)\nCHALLENGER\n(.*?)\nSTAKES',t,re.S)
    pm2=re.search(r'PREDICTOR\n(.*?)\n(?:CHALLENGER|STAKES|Unchallenged)',t,re.S)
    win='Winner' in t
    badge=re.findall(r'.{0,60}Winner.{0,60}',t.replace('\n',' | '))
    print(x['lb_number'],'| dur:',m.groups() if m else None,'| pred:',(pm.group(1).strip(),pm.group(2).strip()) if pm else (pm2.group(1) if pm2 else None),'| json:',x['who'],'|',x['deadline'],'|',badge[:2])
