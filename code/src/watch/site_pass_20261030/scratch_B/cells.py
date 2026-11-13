import re,html,json
from html.parser import HTMLParser
t=open('qia.html',encoding='utf-8').read()
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.rows=[]; s.cur=None; s.cell=None; s.tab=0; s.tables=[]; s.skip=0
    def handle_starttag(s,tag,a):
        if tag=='table': s.tab+=1; s.tables.append([])
        if tag=='tr': s.cur=[]
        if tag in('td','th'): s.cell=[]
    def handle_endtag(s,tag):
        if tag in('td','th') and s.cell is not None:
            s.cur.append(re.sub(r'\s+',' ',''.join(s.cell)).strip()); s.cell=None
        if tag=='tr' and s.cur is not None:
            if s.tables: s.tables[-1].append(s.cur)
            s.cur=None
    def handle_data(s,d):
        if s.cell is not None: s.cell.append(d)
p=P(); p.feed(t)
print(len(p.tables),[len(x) for x in p.tables])
json.dump(p.tables,open('tables.json','w'))
