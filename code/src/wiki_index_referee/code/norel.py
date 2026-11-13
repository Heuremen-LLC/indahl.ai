import sys, gzip, json, collections as C
from decimal import Decimal
sys.path.insert(0, '.')
import recount as R
rows = json.load(gzip.open('out/ref_rows.json.gz','rt'))
for gid in ('WB-POP','WB-GDP','WB-GINI','WB-UNEMP'):
    cur, older, _, _ = R.wb_tables(R.G[gid][2])
    for r in rows:
        if r['group']==gid and r['bin']=='MATCHES_NO_RELEASE_READ':
            vals = [(lab, str(t[(r['iso'][0], r['year'])])) for rid, lab, t in older if t and (r['iso'][0], r['year']) in t]
            # nearest release value
            v = Decimal(r['v'])
            near = min(vals, key=lambda x: abs(Decimal(x[1]) - v)) if vals else None
            print(gid, r['item'], r['iso'], r['year'], r['value'], 'u', r['u'], 'cur', r['current'], 'nearest release', near, 'n releases with value', len(vals), 'default', r['default'])
# legacy codes: codes present in archives but not in the current release, per series
for code in ('SP.POP.TOTL','NY.GDP.MKTP.CD','SI.POV.GINI','SL.UEM.TOTL.ZS','SP.DYN.LE00.IN','SP.DYN.TFRT.IN'):
    arch = R.wb_codes_in_archive(code)
    cur, older, _, _ = R.wb_tables(code)
    curcodes = {k[0] for k in cur}
    extra = {c: n for c, n in arch.items() if c not in curcodes and c not in R.LEGACY}
    print(code, 'archive codes not in current and not mapped:', extra)
