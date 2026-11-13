import json,re,html,sys
def norm(s):
    s=html.unescape(s); s=re.sub(r'\s+',' ',s); s=s.replace('’',"'").replace('‘',"'"); return s.strip()
E=json.load(open('/Users/heuremen/bones-forge/qia_leads/recheck_published/edits.json'))
raw={}
for n in ('qia.html','qia_list.html','qia_key.html'):
    raw[n]=norm(re.sub(r'<[^>]+>',' ',open(n,encoding='utf-8').read()))
for rid,fld,old,new in E:
    o=norm(old); nw=norm(new)
    res=[]
    for n,t in raw.items():
        t2=re.sub(r'\s+',' ',t)
        res.append('%s new=%s old=%s'%(n.split('.')[0], nw in t2, o in t2 and o!=nw and not (nw in t2 and o in nw)))
    print(rid,fld,'|',' ; '.join(res))
