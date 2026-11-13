import sys, json, random, collections as C, datetime as D
sys.path.insert(0,'.')
import recount
R=recount.raw()
base, meta = recount.build('plan', keep_rows=True)
B = json.load(open('/Users/heuremen/bones-forge/social_index/adspend/data/adspend.json'))
bc = {(r['group_key'], r['cycle']): r for r in B['rows'] if r['level']=='cycle'}
featured=[('C00744946',2024),('C00744946',2020),('C00770941',2022),('C00693234',2020),('C00391490',2024),('C00715029',2020)]
dec=sorted(k for k,m in base.items() if m['outcome'] in ('ABOVE','BELOW','CONSISTENT') and k not in featured)
rnd=random.Random(20261110).sample(dec,6)
print('random draw (seed 20261110, from', len(dec), 'decided rows not featured):', rnd)
for k in featured+rnd:
    m=base[k]; b=bc[k]
    a=D.date.fromisoformat(m['window'][0]).toordinal(); e=D.date.fromisoformat(m['window'][1]).toordinal()
    # raw Google weekly sum in window for the group's advertisers, straight from the weekly list
    wsum=sum(v for x in m['advs'] for s,v in R['weekly'].get(x,()) if a<=s<=e)
    rows=m['ggrows']; bycls=C.defaultdict(lambda:[0,0.0]); purp=C.Counter(); memo=0
    for r in rows:
        bycls[r[3]][0]+=1; bycls[r[3]][1]+=r[2]; purp[(r[3],r[8][:30])]+=1; memo+= bool(r[4])
    print(f"\n### {m['name']} {k[1]} ({k[0]}) tier={m['tiers']} window {m['window'][0]}..{m['window'][1]}")
    print(f"  Google: weekly sum in window {wsum:,.0f} | band [{m['G_lo']:,.0f}, {m['G_hi']:,.0f}] | second ruler [{m['G2'][0]:,.0f}, {m['G2'][1]:,.0f}]")
    print(f"  FEC Sched B Google rows: {len(rows)} (memo {memo}) by class: " + '; '.join(f"{c} n={v[0]} ${v[1]:,.2f}" for c,v in sorted(bycls.items())))
    print(f"  top purposes: {purp.most_common(4)}")
    print(f"  Sched E Google raw {m['e_g_raw']:,.2f} dedup {m['e_dd']:,.2f} | D=[{m['D_lo']:,.2f}, {m['D_hi']:,.2f}] pool {m['pool']:,.2f} unseen {m['unseen']:,.2f} (full {m['unseen_full']:,.2f})")
    print(f"  outcome mine {m['outcome']} {m['reason']} / 2nd {m['outcome2']} / full {m['outcome_full']}  | builder {b['outcome']} / {b['outcome_second_ruler']} / {b['outcome_unseen_full']} | builder D_lo {b['fec']['d_lo']:,.2f} G {b['google']['stated_in_window']:,.0f}")
    sa=max(1000,0.1*m['G_hi']); sb=max(1000,0.1*m['G_lo'])
    print(f"  ABOVE margin {m['D_lo']-m['G_hi']:,.0f} vs {sa:,.0f}; BELOW margin {m['G_lo']-(max(m['D_hi'],0)+m['pool']+m['unseen']):,.0f} vs {sb:,.0f}")
