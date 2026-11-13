import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ref_xlsx
for p in sys.argv[1:]:
    print('==', os.path.basename(p), ref_xlsx.sheets(p))
    name, rows = ref_xlsx.read(p)
    h = rows[0]
    print(len(rows)-1, 'rows; header', len(h))
    print([x for x in h if 'APR' in x or 'Top' in x or 'fee' in x.lower()][:40])
    for col in [c for c in h if c in ('Purchase APR median','Median APR','Purchase APR min','Minimum APR','Purchase APR max','Maximum APR','Issued by Top 25 Institution','Late Fee','Annual Fee')]:
        i = h.index(col)
        vals = [r[i] if i < len(r) else '' for r in rows[1:]]
        c = collections.Counter(vals)
        print('  ', col, 'blank', c.get('',0), 'distinct', len(c), 'sample', c.most_common(6))
