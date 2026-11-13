import sys, csv, random, collections as C, datetime as D, pickle, os
sys.path.insert(0,'.')
import recount
R=recount.raw(); cm=R['cm']
base, meta = recount.build('plan')
adv=meta['adv']; allg={g['id']:g for g in R['gstats']}
geo_p='geo.pkl'
if os.path.exists(geo_p): geo=pickle.load(open(geo_p,'rb'))
else:
    geo=C.defaultdict(dict)
    for r in csv.DictReader(open('/Users/heuremen/bones-forge/social_index/adspend/data/raw/google/x/google-political-ads-advertiser-geo-spend.csv',newline='',encoding='utf-8')):
        if r['Country']=='US' and float(r['Spend_USD'] or 0)>0: geo[r['Advertiser_ID']][r['Country_Subdivision_Primary']]=float(r['Spend_USD'])
    geo=dict(geo); pickle.dump(geo,open(geo_p,'wb'))
gby=C.defaultdict(list)
for r in R['broad']:
    if recount.is_g(r[4]): gby[r[0]].append(r)
def wk(o): d=D.date.fromordinal(o); return d.year, d.isocalendar()[1]
def evidence(aid, cids):
    g=allg[aid]; w=R['weekly'].get(aid,[])
    first=D.date.fromordinal(w[0][0]).isoformat() if w else None; last=D.date.fromordinal(w[-1][0]).isoformat() if w else None
    gg=geo.get(aid,{}); tot=sum(gg.values()) or 1
    top=sorted(gg.items(), key=lambda kv:-kv[1])[:2]
    out=[]
    for c in cids:
        recs=cm[c]; names=sorted({r['name'] for r in recs.values()}); r=recs[max(recs)]
        candst = r['cand'][2:4] if r['cand'] else ''
        gp=gby.get(c,[]); gweeks={(D.date.fromordinal(x[2]).year, D.date.fromordinal(x[2]).month) for x in gp}
        spweeks={(D.date.fromordinal(s).year, D.date.fromordinal(s).month) for s,v in w if v>0}
        ov=len(gweeks & spweeks)
        out.append(dict(cid=c, names=names[:3], tp=r['tp']+r['dsgn'], st=r['state'], cand=r['cand'], candst=candst, org=r['org'][:30], cycles=sorted(recs), fec_google_rows=len(gp), fec_google_sum=round(sum(x[3] for x in gp)), months_overlap=ov, google_months=len(spweeks)))
    return dict(adv=g['name'], ids=g['ids'][:60], total=g['total'], first=first, last=last, geo=[(k,round(v/tot,2)) for k,v in top]), out
tiers=C.defaultdict(list)
for a,(t,ids) in adv.items(): tiers[t].append(a)
rng=random.Random(20261110)
for t in ('id','candidate id','name'):
    pick=rng.sample(sorted(tiers[t]),10)
    print(f'\n######## tier {t}: 10 random of {len(tiers[t])}')
    for a in pick:
        e,o=evidence(a, adv[a][1]); print(' ADV', e)
        for x in o: print('    CMTE', x)
print('\n######## every decided row whose group holds a name match')
for k,m in sorted(base.items(), key=lambda kv:(kv[1]['cycle'],kv[1]['name'])):
    if m['outcome'] in ('ABOVE','BELOW','CONSISTENT') and 'name' in m['tiers']:
        print(f"\n== {m['outcome']} {m['cycle']} {m['name']} tiers={m['tiers']}")
        for a in m['advs']:
            e,o=evidence(a, adv[a][1]); print('  ADV', adv[a][0], e)
            for x in o: print('     CMTE', x)
