import json,random,hashlib,re
R=json.load(open('/Users/heuremen/bones-forge/trackrecord/record.json'))['recounts']
L={s['link']:s for s in json.load(open('/Users/heuremen/bones-forge/qia_leads/matrix_page/list.json'))['studies']}
items=[]
for x in R:
    key=x['link'] or ('nolink:'+x['study'])
    codes=sorted(c for c in (L[x['link']]['codes'] if x['link'] in L else x['codes']) if re.match(r'F[1-7]$',c))
    items.append({'id':hashlib.sha1(key.encode()).hexdigest()[:12],'link':x['link'],'study':x['study'],'codes':codes})
items.sort(key=lambda i:(i['link'] or '',i['study']))
assert len({i['id'] for i in items})==len(items)
random.Random(20261112).shuffle(items)
for k,i in enumerate(items): i['split']='dev' if k<98 else 'test'
json.dump({'seed':20261112,'rule':'sorted by link, shuffled random.Random(seed), first 98 dev, rest test','items':items},open('data/gold_split.json','w'),indent=1)
import collections;print(collections.Counter(i['split'] for i in items))
