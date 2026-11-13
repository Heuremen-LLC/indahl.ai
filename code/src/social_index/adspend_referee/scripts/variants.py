import json, sys, collections as C
sys.path.insert(0, '.')
import recount
B = json.load(open('/Users/heuremen/bones-forge/social_index/adspend/data/adspend.json'))
bc = {(r['group_key'], r['cycle']): r for r in B['rows'] if r['level']=='cycle'}
base, meta = recount.build('plan', keep_rows=True)
# the two numeric differences
for k in [('C00883157',2024),('C00864926',2024)]:
    m=base[k]; print(k, m['name'], 'D_lo', m['D_lo'], 'pool', m['pool'], 'outcome', m['outcome'], 'builder', bc[k]['fec']['d_lo'], bc[k]['fec']['pool'], bc[k]['outcome'])
    for r in m['ggrows']: print('   ', r[0], recount.iso(r[1]), r[2], r[3], r[7][:40], '|', r[8][:50])
code, _ = recount.build('code')
print('code-variant D_lo C00883157 2024 =', code[('C00883157',2024)]['D_lo'])
def flips(a, b, label):
    dec = {'ABOVE','BELOW','CONSISTENT'}
    ch = [(k, a[k]['outcome'], b[k]['outcome']) for k in a if k in b and a[k]['outcome']!=b[k]['outcome']]
    out_dec = [z for z in ch if z[1] in dec]; in_dec=[z for z in ch if z[2] in dec and z[1] not in dec]
    print(f'{label}: rows changed {len(ch)}; decided->other {len(out_dec)}; other->decided {len(in_dec)}; decided total {sum(1 for v in b.values() if v["outcome"] in dec)}')
    for z in ch[:40]: print('    ', z[0], base[z[0]]['name'][:50], z[1], '->', z[2])
    return ch
flips(base, code, 'builder payee words (code) vs PLAN words')
v,_ = recount.build('plan', sched_e_mixed_in_dlo=False); flips(base, v, 'Sched E mixed payees out of D_lo')
v,_ = recount.build('plan', itm_dedup=True); flips(base, v, 'itemized total after amendment rule (unseen)')
for th in (0.8, 0.85, 0.95, 0.99, 1.0):
    v,_ = recount.build('plan', threshold=th); flips(base, v, f'threshold {th}')
for cap in (200.0, 600.0, 800.0, 1200.0):
    v,_ = recount.build('plan', cap=cap); flips(base, v, f'cap {cap}')
