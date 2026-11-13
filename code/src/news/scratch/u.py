import json,re
st=json.load(open('steers.json'))
for r in st:
    if r['turn'] in (107239,):
        s=json.dumps(r)
        for m in re.finditer(r'the user',s,re.I): print(r['turn'],'...',s[max(0,m.start()-160):m.end()+120])
    if r['turn'] in (107238,107263):
        print(r['turn'],'S:',r.get('synthesis')); print('   N:',r.get('next'))
