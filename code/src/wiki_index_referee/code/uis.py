import sys, gzip, json, collections as C
from decimal import Decimal
from urllib.parse import urlparse
sys.path.insert(0, '.')
import recount as R
rows = json.load(gzip.open('out/ref_rows.json.gz','rt'))
for gid in ('UIS-LE', 'UIS-TFR'):
    rs = [r for r in rows if r['group'] == gid]
    wcur, wold, _, _ = R.wb_tables(R.G[gid][2])
    print('=====', gid, len(rs))
    print(' url hosts:', C.Counter(tuple(sorted({urlparse(u).netloc for u in r['urls']})) for r in rs).most_common(6))
    print(' url paths:', C.Counter(tuple(sorted(r['urls'])) for r in rs).most_common(4))
    print(' retrieved:', C.Counter((min(r['retrieved'])[1:8] if r['retrieved'] else 'none') for r in rs).most_common(10))
    print(' stated_in UIS:', C.Counter(r['stated_in'] for r in rs))
    sec = C.Counter(); newest = C.Counter(); dec = C.Counter()
    for r in rs:
        dec[len(r['value'].split('.')[1]) if '.' in r['value'] else 0] += 1
        if r['bin'] in ('MATCHES_NO_RELEASE_READ', 'SOURCE_UNREADABLE'):
            b, hits, c = R.bin_of(Decimal(r['v']), Decimal(r['u']), r['iso'], r['year'], wcur, wold)
            sec[(r['bin'], b)] += 1
            if hits: newest[hits[-1][1][:4]] += 1
    print(' secondary WB reading:', dict(sec))
    print(' newest WB release carrying the NOREL figures, by year:', sorted(newest.items()))
    print(' decimals written:', dict(dec))
    print(' years cited:', min(r['year'] for r in rs), max(r['year'] for r in rs), C.Counter(r['year'] for r in rs if r['bin']=='MATCHES_NO_RELEASE_READ').most_common(5))
