import json, sys, collections as C, time
sys.path.insert(0, '.')
import recount
t=time.time()
mine, meta = recount.build('plan')
print('built', len(mine), 'rows in', round(time.time()-t,1), 's; cut', meta['cut_end'], 'amend drops', meta['n_amend'], 'memo drops', meta['n_memo'])
print('tiers', dict(meta['tiers']), 'groups', meta['groups'], 'committees', meta['committees'])
print('unmatched', meta['why'])
B = json.load(open('/Users/heuremen/bones-forge/social_index/adspend/data/adspend.json'))
bc = {(r['group_key'], r['cycle']): r for r in B['rows'] if r['level']=='cycle'}
print('builder cycle rows', len(bc), 'mine', len(mine))
only_b = set(bc)-set(mine); only_m = set(mine)-set(bc)
print('only builder', len(only_b), 'only mine', len(only_m))
for k in list(only_b)[:5]: print(' B-only', k, bc[k]['outcome'], bc[k]['committee_name'])
for k in list(only_m)[:5]: print(' M-only', k, mine[k]['outcome'], mine[k]['name'])
diff = C.Counter(); ex = C.defaultdict(list)
def close(x,y,tol=0.02): return abs((x or 0)-(y or 0))<=tol
for k in set(bc)&set(mine):
    b=bc[k]; m=mine[k]
    checks = dict(G_pt=(b['google']['stated_in_window'],m['G_pt']), G_lo=(b['google']['lo'],m['G_lo']), G_hi=(b['google']['hi'],m['G_hi']),
                  D_lo=(b['fec']['d_lo'],m['D_lo']), D_hi=(b['fec']['d_hi'],m['D_hi']), pool=(b['fec']['pool'],m['pool']),
                  unseen=(b['fec']['unseen'],m['unseen']), unseen_full=(b['fec']['unseen_full'],m['unseen_full']))
    for n,(x,y) in checks.items():
        if not close(x,y): diff[n]+=1; ex[n].append((k, x, y))
    if b['outcome']!=m['outcome']: diff['outcome']+=1; ex['outcome'].append((k,b['outcome'],m['outcome']))
    if b['outcome_second_ruler']!=m['outcome2']: diff['outcome2']+=1; ex['outcome2'].append((k,b['outcome_second_ruler'],m['outcome2']))
    if b['outcome_unseen_full']!=m['outcome_full']: diff['outcome_full']+=1; ex['outcome_full'].append((k,b['outcome_unseen_full'],m['outcome_full']))
    if b['window']!=list(m['window']): diff['window']+=1; ex['window'].append((k,b['window'],m['window']))
    if b['committee_id']!=m['cid']: diff['cid']+=1; ex['cid'].append((k,b['committee_id'],m['cid']))
    if (b['party_field'] or '')!=(m['party'] or ''): diff['party']+=1; ex['party'].append((k,b['party_field'],m['party']))
print('differences', dict(diff))
for n,v in ex.items():
    print('==',n, len(v))
    for z in v[:12]: print('  ', z)
oc = C.Counter(m['outcome'] for m in mine.values())
print('my cycle outcomes', dict(oc))
for c in (2020,2022,2024,2026): print(c, dict(C.Counter(m['outcome'] for m in mine.values() if m['cycle']==c)))
