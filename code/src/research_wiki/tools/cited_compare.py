"""Wikidata population statements that cite World Bank Open Data, against the World Bank API now."""
import json, math, collections, os, sys
D = os.path.expanduser('~/bones-forge/research_wiki/samples/cited/')
wd = json.load(open(D + 'wikidata_pop_worldbank.json'))['results']['bindings']
wb = json.load(open(D + 'worldbank_SP.POP.TOTL.json'))[1]
WB = {(r['countryiso3code'], int(r['date'])): r['value'] for r in wb if r['value'] is not None}

# one row per statement value: (item, iso, year, value); keep retrieved dates seen
st = {}
for b in wd:
    item = b['c']['value'].rsplit('/', 1)[1]
    iso = b['iso']['value']
    yr = int(b['t']['value'][:4])
    v = float(b['pop']['value'])
    key = (item, iso, yr, v)
    r = st.setdefault(key, {'retr': set(), 'rank': b['rank']['value'].rsplit('#', 1)[1], 'url': set()})
    if 'retr' in b: r['retr'].add(b['retr']['value'][:10])
    if 'url' in b: r['url'].add(b['url']['value'])
print('statement values', len(st), 'countries', len({k[0] for k in st}))

def wilson(k, n, z=1.96):
    if n == 0: return (float('nan'),) * 2
    p = k / n; d = 1 + z * z / n
    c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)

out = collections.Counter(); rows = []
byvint = collections.defaultdict(collections.Counter)
for (item, iso, yr, v), r in st.items():
    now = WB.get((iso, yr))
    vint = min(r['retr']) [:4] if r['retr'] else 'none'
    if now is None:
        o = 'NO_SOURCE_VALUE'
    elif v == now:
        o = 'MATCH'
    else:
        rel = abs(v - now) / now
        o = 'DIFF_LT_0.1PCT' if rel < 0.001 else ('DIFF_0.1_TO_1PCT' if rel < 0.01 else 'DIFF_GE_1PCT')
    out[o] += 1; byvint[vint][o] += 1
    rows.append({'item': item, 'iso': iso, 'year': yr, 'wikidata': v, 'worldbank_now': now, 'outcome': o,
                 'retrieved': sorted(r['retr']), 'rank': r['rank']})
n = sum(out.values())
print(dict(out), 'n', n)
comp = n - out['NO_SOURCE_VALUE']
diff = comp - out['MATCH']
lo, hi = wilson(diff, comp)
print(f'comparable {comp}, differ {diff} = {diff/comp:.3%}  (Wilson 95% {lo:.3%} to {hi:.3%})')
ge1 = out['DIFF_GE_1PCT']; lo1, hi1 = wilson(ge1, comp)
print(f'differ by 1% or more {ge1} = {ge1/comp:.3%} ({lo1:.3%} to {hi1:.3%})')
print('by first retrieved year:')
for k in sorted(byvint):
    c = byvint[k]; m = sum(c.values())
    print(' ', k, m, dict(c))
# by data year bands
byyr = collections.defaultdict(collections.Counter)
for r in rows:
    band = 'pre-1990' if r['year'] < 1990 else ('1990-2009' if r['year'] < 2010 else ('2010-2019' if r['year'] < 2020 else '2020+'))
    byyr[band][r['outcome']] += 1
print('by data year:')
for k in ['pre-1990', '1990-2009', '2010-2019', '2020+']:
    print(' ', k, dict(byyr[k]))
# largest relative gaps
big = sorted([r for r in rows if r['worldbank_now']], key=lambda r: -abs(r['wikidata'] - r['worldbank_now']) / r['worldbank_now'])[:12]
print('largest gaps:')
for r in big:
    print(' ', r['iso'], r['year'], int(r['wikidata']), r['worldbank_now'], f"{(r['wikidata']-r['worldbank_now'])/r['worldbank_now']:+.2%}", r['retrieved'])
# latest year per country: does Wikidata hold the newest WB year?
latest_wd = collections.defaultdict(int)
for r in rows: latest_wd[r['iso']] = max(latest_wd[r['iso']], r['year'])
latest_wb = collections.defaultdict(int)
for (iso, yr), v in WB.items(): latest_wb[iso] = max(latest_wb[iso], yr)
lag = collections.Counter(latest_wb[i] - latest_wd[i] for i in latest_wd if i in latest_wb)
print('latest WB year minus latest Wikidata WB-cited year, countries:', dict(sorted(lag.items())))
json.dump({'counts': dict(out), 'rows': rows}, open(D + 'cited_compare_rows.json', 'w'))
