import sys, re, collections as C, datetime as D
sys.path.insert(0,'.')
import recount
R=recount.raw(); cm=R['cm']; wk=R['wk']
base, meta = recount.build('plan')
adv=meta['adv']
def cand_year(cid):
    d=cid[1]
    if not d.isdigit(): return None
    d=int(d); return 2020+d if d<=5 else None      # 2021-2025 unambiguous; 6-9 could be 2016-2019
# cycle-mismatch scan: candidate committees whose candidate id is for a later election than the row
print('rows (decided or NR) whose members candidate id is for a later election than the row cycle:')
for m in base.values():
    if m['outcome'] not in ('ABOVE','BELOW','CONSISTENT','NOTHING_RETURNED'): continue
    for x in m['members']:
        r=cm[x].get(m['cycle'])
        if r and r['cand'] and r['cand'][0] in 'HS':
            y=cand_year(r['cand'])
            if y and y>m['cycle']: print('  ', m['outcome'], m['cycle'], x, m['name'][:40], r['cand'])
# proposed rules
def empty_summary(x,c):
    w=wk[c].get(x)
    return w is not None and w['cvg'] is None and w['ttl_disb']==0
def est_free_dlo(m):
    a=D.date.fromisoformat(m['window'][0]).toordinal(); b=D.date.fromisoformat(m['window'][1]).toordinal(); tot=0.0
    for x in m['members']:
        per=C.defaultdict(C.Counter)
        for r in R['ie'].get(x,[]):
            if (r['exp'] or r['dis']) and recount.is_g(r['pay']) and not re.search('ESTIMAT',(r['pur'] or '').upper()):
                per[(r['exp'] or r['dis'], r['amt'], recount.U(r['pay']), r['cand'], r['so'])][r['fn']]+=1
        tot+=sum(k[1]*max(v.values()) for k,v in per.items() if a<=k[0]<=b)
    return m['D_lo']-m['e_dd']+tot
def glo_without_name(m):
    keep=[a for a in m['advs'] if adv[a][0]!='name']
    a=D.date.fromisoformat(m['window'][0]).toordinal(); b=D.date.fromisoformat(m['window'][1]).toordinal()
    w=C.defaultdict(float)
    for x in keep:
        for s,v in R['weekly'].get(x,()): w[s]+=v
    return sum(max(0,v-100) for s,v in w.items() if s>=a+31 and s+98<=b)
new={}; why=C.Counter()
for k,m in base.items():
    o=m['outcome']; reg=any(m['cycle'] in cm[x] for x in m['members'])
    if o=='NOTHING_RETURNED' and (m['G_pt']==0 or not reg): o='CANNOT_TELL'; why['NR: G zero in window or not registered']+=1
    if o=='BELOW':
        if all(empty_summary(x,m['cycle']) or (m['cycle'] not in cm[x]) for x in m['members']) and not any((x,m['cycle']) in R['anyrow'] for x in m['members']):
            o='NOTHING_RETURNED' if 'name' not in m['tiers'] else 'CANNOT_TELL'; why['BELOW: empty summary']+=1
        elif 'name' in m['tiers'] and glo_without_name(m)-(max(m['D_hi'],0)+m['pool']+m['unseen'])<max(1000,0.1*glo_without_name(m)):
            o='CANNOT_TELL'; why['BELOW: rests on a name-matched advertiser']+=1
    if o=='ABOVE':
        if m['G_pt']==0: o='CANNOT_TELL'; why['ABOVE: Google states nothing in the window']+=1
        elif est_free_dlo(m)-m['G_hi']<max(1000,0.1*m['G_hi']): o='CANNOT_TELL'; why['ABOVE: rests on Schedule E estimates']+=1
    new[k]=o
manual={('C00765412',2020):'cycle mismatch',('C00715938',2020):'wrong entity'}  # handled by hand below if still BELOW
for k,r in manual.items():
    if new.get(k)=='BELOW': new[k]='CANNOT_TELL'; why['BELOW: '+r]+=1
print('\nmoves:', dict(why))
for c in (2020,2022,2024,2026):
    a=C.Counter(base[k]['outcome'] for k in base if k[1]==c); b=C.Counter(new[k] for k in new if k[1]==c)
    print(c, 'now', [a[x] for x in ('ABOVE','BELOW','CONSISTENT','CANNOT_TELL','NOTHING_RETURNED')], '-> proposed', [b[x] for x in ('ABOVE','BELOW','CONSISTENT','CANNOT_TELL','NOTHING_RETURNED')])
tot=C.Counter(new.values()); print('all proposed', dict(tot))
print('BELOW kept:', sorted((k[1],base[k]['name']) for k in new if new[k]=='BELOW'))
# party split and featured lists under the proposed rules
P=lambda m: m['party'] or '(blank)'
for o in ('ABOVE','BELOW','CONSISTENT'):
    print('proposed', o, 'by filed party:', dict(C.Counter(P(base[k]) for k in new if new[k]==o)))
for o in ('CONSISTENT','ABOVE','BELOW'):
    top=sorted([k for k in new if new[k]==o], key=lambda k:-max(base[k]['G_pt'], base[k]['D_lo']))[:6]
    print('featured', o, [(k[1], base[k]['name'][:40]) for k in top])
