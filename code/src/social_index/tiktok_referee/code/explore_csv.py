import zipfile, csv, io, hashlib, json, sys, collections
RAW = '/Users/heuremen/bones-forge/social_index/tiktok/data/raw/tiktok_cger/'
src = json.load(open('/Users/heuremen/bones-forge/social_index/tiktok/data/sources.json'))['tiktok']
def rows(q):
    p = RAW + q + '.zip'
    h = hashlib.sha256(open(p,'rb').read()).hexdigest()
    assert h == src[q]['sha256'], (q, h)
    z = zipfile.ZipFile(p)
    n = [x for x in z.namelist() if x.lower().endswith('.csv') and not x.startswith('__MACOSX')]
    assert len(n) == 1, n
    return list(csv.DictReader(io.TextIOWrapper(z.open(n[0]), encoding='utf-8-sig'))), n[0]
for q in sys.argv[1:]:
    R, name = rows(q)
    print('==', q, name, len(R), 'cols', list(R[0].keys()))
    iss = 'Issue' if 'Issue' in R[0] else 'Issue policy'
    c = collections.Counter()
    for r in R:
        if r['Metric'] in ('Proactive removal rate','Removal rate within 24 hours','Total videos removed') and r['Location']=='Market':
            c[(r['Metric'], r['Policy type'], r[iss] if r[iss]=='All' else 'x', r['Task type'], r['Task'])] += 1
    for k,v in sorted(c.items()): print('  ', k, v)
    print('  periods', sorted(set(r['Period'] for r in R))[-6:])
    print('  locations', collections.Counter(r['Location'] for r in R))
