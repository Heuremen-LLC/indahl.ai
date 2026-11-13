import sys, gzip, json, collections as C
from decimal import Decimal
sys.path.insert(0, '.')
import recount as R
rows = json.load(gzip.open('out/ref_rows.json.gz','rt'))
for gid in ('WB-POP', 'WB-GDP', 'WB-GINI', 'WB-UNEMP', 'UIS-LE', 'UIS-TFR'):
    if R.G[gid][1] == 'WB': cur, older, _, _ = R.wb_tables(R.G[gid][2])
    else: cur, older, *_ = R.uis_tables(R.G[gid][2])
    rs = [r for r in rows if r['group'] == gid]
    res = C.Counter(); whole = C.Counter()
    for r in rs:
        for dy in (-2, 2):
            b = R.bin_of(Decimal(r['v']), Decimal(r['u']), r['iso'], r['year'] + dy, cur, older)[0]
            key = 'match' if b in ('MATCHES_CURRENT', 'MATCHES_AN_OLDER_RELEASE') else ('nomatch' if b == 'MATCHES_NO_RELEASE_READ' else 'unread')
            res[key] += 1
            if '.' not in r['value'] and gid in ('WB-UNEMP', 'WB-GINI'): whole[key] += 1
    n = res['match'] + res['nomatch']
    print(f"{gid}: year shifted by 2, a release value matches in {res['match']} of {n} ({100*res['match']/n:.1f}%)" + (f" | whole-number figures: {whole['match']} of {whole['match']+whole['nomatch']}" if whole else ''))
