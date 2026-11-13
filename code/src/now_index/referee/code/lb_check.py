import json,re,html,sys
B='/Users/heuremen/bones-forge/now_index/'
d=json.load(open(B+'data/research/longbets.json'))
drop=json.load(open(B+'data/research/drop.json'))
def norm(s):
    s=html.unescape(re.sub(r'<[^>]+>',' ',s))
    s=s.replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"').replace('\xa0',' ')
    return re.sub(r'\s+',' ',s).strip()
n=0
for x in d:
    k='longbets:%s'%x['lb_number']
    if k in drop: continue
    n+=1
    raw=norm(open(B+x['raw_file']).read())
    q=norm(x['quote'])
    ok=q in raw
    print(x['lb_number'],x['lb_type'],'QUOTE_IN_RAW' if ok else 'QUOTE_MISSING',x['who'],'|',x['deadline'],'|',x['said'])
    if not ok: print('   Q:',q[:200])
print(n)
