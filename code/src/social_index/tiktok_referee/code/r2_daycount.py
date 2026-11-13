import re, glob, duckdb, json
P = '/Users/heuremen/bones-forge/social_index/tiktok/data/'
pub = {}
for f in glob.glob(P + 'raw/dsa_pages/tiktok_p30_page*.html'):
    for d, n in re.findall(r'header="Date">(\d{4}-\d\d-\d\d)</td>\s*<td[^>]*header="Statements of reasons">([^<]+)</td>', open(f).read()):
        pub[d] = int(re.sub(r'[^\d]', '', n.replace('&nbsp;', '')) or 0)
con = duckdb.connect()
fs = sorted(glob.glob(P + 'raw/dsa_tiktok/complete_*.parquet'))
agg = {str(d): int(n) for d, n in con.execute("select created_day, sum(n) from read_parquet([%s], union_by_name=true) group by 1" % ','.join("'%s'" % f for f in fs)).fetchall()}
po = {d: pub[d] for d in pub if d not in agg}
print('pub-only days', len(po), 'nonzero', {d: v for d, v in po.items() if v})
eq = sum(1 for d in pub if pub[d] == agg.get(d, 0))
print('published days', len(pub), 'equal incl. zero days', eq, 'differ', len(pub) - eq)
ph = json.load(open(P + 'posthoc_daycheck.json'))
print({k: (v if not isinstance(v, (dict, list)) else type(v).__name__ + str(len(v))) for k, v in ph.items()})
