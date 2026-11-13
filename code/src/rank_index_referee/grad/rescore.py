import json,re
from decimal import Decimal,ROUND_HALF_UP
d=json.load(open('/Users/heuremen/bones-forge/rank_index/data/checks_grad.json'))['checks']
def num(s):
    m=re.match(r'\s*\$?([\d,]+(?:\.\d+)?)',str(s)); return Decimal(m.group(1).replace(',','')) if m else None
def dec(s):
    m=re.match(r'\s*\$?[\d,]*\.(\d+)',str(s)); return len(m.group(1)) if m else 0
def rh(x,p): return x.quantize(Decimal(1).scaleb(-p),rounding=ROUND_HALF_UP)
rows=[]
for r in d:
    u,p=r['usn'],r['pub']; o=r['outcome']; mine=None;why=''
    if o=='DISPLAY': mine='DISPLAY'
    elif u is None or 'not shown' in str(u) or str(u)=='None': mine='CANNOT_TELL';why='not_printed/paid'
    elif p is None or str(p)=='None': mine='CANNOT_TELL';why='not_found'
    else:
        un,pn=num(u),num(p)
        if un is None or pn is None: mine='CANNOT_TELL';why='unparsed'
        else:
            ign=rh(pn,dec(u))==un
            mine=('MATCH' if ign else 'MISMATCH')
            # definition / year flags from desk reason trusted only as flags
            if r['reason'] in('year','definition'): mine='CANNOT_TELL('+r['reason']+') [value-only would be '+mine+']'
    rows.append((r['list'],r['school'],r['field'],u,p,o,r['reason'],mine))
bad=[x for x in rows if (x[5] in('MATCH','MISMATCH') and x[5]!=x[7]) ]
print('disagree on MATCH/MISMATCH:',bad)
for x in rows:
    if x[6] in('definition','year'): print(x[1][:30],'|',x[2][:35],'|',x[3],'|',x[4],'|',x[7])
import collections
print(collections.Counter((x[5],x[6]) for x in rows))
