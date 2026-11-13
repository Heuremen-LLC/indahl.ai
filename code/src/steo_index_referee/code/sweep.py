import json, sys
sys.path.insert(0, '.')
import boot as B
out = []
for mode in ('primary', 'add1'):
    for label, src in (('corrected', B.mine), ('as_desk', B.desk)):
        rows = B.prep(src, mode)
        for blk in (6, 12, 24):
            res = B.cells(rows, block=blk)
            print('%-8s %-9s block %2d' % (mode, label, blk), ' | '.join('%s %s %s[%.3f,%.3f]' % (s, nm, v['outcome'][:4], v['lo'] or 0, v['hi'] or 0) for (s, nm), v in res.items() if nm == 'all'))
        if label == 'corrected':
            # other seeds at block 12
            flips = {}
            for seed in range(1, 21):
                res = B.cells(rows, block=12, seed=seed)
                for k, v in res.items(): flips.setdefault(k, set()).add(v['outcome'])
            print('   seeds 1..20 block 12, cells whose outcome varies:', {str(k): sorted(v) for k, v in flips.items() if len(v) > 1})
            print('   seeds, all-leads outcomes:', {str(k): sorted(v) for k, v in flips.items() if k[1] == 'all'})
            for blk in (6, 24):
                res0 = B.cells(rows, block=blk); ch = []
                res12 = B.cells(rows, block=12)
                for k in res0:
                    if res0[k]['outcome'] != res12[k]['outcome']: ch.append((k, res12[k]['outcome'], res0[k]['outcome']))
                print('   cells changing vs block 12 at block', blk, ch)
