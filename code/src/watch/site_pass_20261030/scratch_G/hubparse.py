import re,html,json,collections
t=open('pages/oy.html',encoding='utf-8').read()
def sect(h2id):
    m=re.search(r'<section>\s*<h2 id="%s">.*?</section>'%h2id,t,re.S); return m.group(0)
def rows(sec):
    out=[]
    for tr in re.findall(r'<tr>(.*?)</tr>',re.search(r'<tbody>(.*?)</tbody>',sec,re.S).group(1),re.S):
        out.append(re.findall(r'<td[^>]*>(.*?)</td>',tr,re.S))
    return out
H={}
H['findings']=rows(sect('findings'))
H['toc']=rows(sect('table-of-findings'))
H['list']=rows(sect('the-list'))
H['schools']=rows(sect('small-private-colleges'))
json.dump(H,open('hub_rows.json','w'))
for k,v in H.items(): print(k,len(v))
