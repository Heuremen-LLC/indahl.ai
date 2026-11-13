"""For each Wikidata population value citing World Bank Open Data, find which World Bank releases
(WDI current plus WDI Database Archives vintages) carried exactly that value for that country and year."""
import json, glob, os, collections, math, gzip
D = os.path.expanduser('~/bones-forge/research_wiki/samples/cited/')
rows = json.load(open(D + 'cited_compare_rows.json'))['rows']
V = {}
for f in sorted(glob.glob(D + 'wdi_archive/v*.json.gz')):
    ver = os.path.basename(f)[1:7]
    d = json.load(gzip.open(f))['source']['data']
    m = {}
    for r in d:
        if r['value'] is None: continue
        var = {x['concept']: x['id'] for x in r['variable']}
        m[(var['Country'], int(var['Time'][2:]))] = r['value']
    V[ver] = m
vers = sorted(V)
print('vintages', len(vers), vers[0], 'to', vers[-1])

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)

cls = collections.Counter(); last_match = collections.Counter(); first_match = collections.Counter()
examples = collections.defaultdict(list)
for r in rows:
    key = (r['iso'], r['year']); v = r['wikidata']
    hits = [ver for ver in vers if key in V[ver] and abs(V[ver][key] - v) < 0.5]
    near = [ver for ver in vers if key in V[ver] and abs(V[ver][key] - v) / max(V[ver][key], 1) < 0.001]
    if r['outcome'] == 'MATCH':
        c = 'MATCHES_CURRENT'
    elif hits:
        c = 'MATCHES_AN_OLDER_RELEASE'
        last_match[hits[-1][:4]] += 1; first_match[hits[0][:4]] += 1
    elif near:
        c = 'WITHIN_0.1PCT_OF_A_RELEASE'
    else:
        c = 'MATCHES_NO_RELEASE_READ'
    r['vintage_class'] = c; r['vintage_hits'] = hits[:3] + (['...'] if len(hits) > 3 else []) + hits[-2:]
    cls[c] += 1
    if len(examples[c]) < 6: examples[c].append((r['iso'], r['year'], int(v), r['worldbank_now']))
n = sum(cls.values())
for c, k in cls.most_common():
    lo, hi = wilson(k, n)
    print(f'{c:28s} {k:5d} {k/n:7.2%}  ({lo:.2%} to {hi:.2%})')
print('newest release that still carried the value, by year:', dict(sorted(last_match.items())))
for c in examples: print(c, examples[c])
json.dump({'vintages': vers, 'classes': dict(cls), 'rows': rows}, open(D + 'cited_vintage_rows.json', 'w'))
