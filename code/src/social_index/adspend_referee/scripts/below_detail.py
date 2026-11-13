import sys, collections as C, datetime as D
sys.path.insert(0, '.')
import recount
R = recount.raw()
base, meta = recount.build('plan')
cm, wk, wa = R['cm'], R['wk'], R['wa']
for o in ('BELOW','CONSISTENT'):
    print('=====', o)
    for k, m in sorted(base.items(), key=lambda kv:(kv[1]['cycle'], kv[1]['name'] or '')):
        if m['outcome']!=o: continue
        c = m['cycle']; cid = m['members'][0]
        recs = cm.get(cid, {}); first = min(recs) if recs else None
        nrows = sum(1 for r in R['opp'].get(cid, []) if r[0]==c)
        nie = sum(1 for r in R['ie'].get(cid, []) if r['c']==c)
        ps = '; '.join(f"{p['src']} imp={p.get('imp',0):.0f} it={p.get('it',0):.0f} cov={p['cov'] if p.get('cov') is None else round(p['cov'],3)} u={p.get('u',0):.0f} {'full' if p.get('full') else 'cap'} tp={p.get('tp','')}" for p in m['parts'])
        print(f"{c} {cid} {m['tiers'][:12]:12} {m['tp']}{m['dsgn']} cmfiles={sorted(recs)} win={m['window'][0]}..{m['window'][1]} G={m['G_pt']:.0f}[{m['G_lo']:.0f},{m['G_hi']:.0f}] D=[{m['D_lo']:.0f},{m['D_hi']:.0f}] pool={m['pool']:.0f} un={m['unseen']:.0f}/{m['unseen_full']:.0f} oppexp_rows_c={nrows} ie_rows_c={nie} | {ps} | {m['name'][:40]}")
