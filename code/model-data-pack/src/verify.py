"""verify.py: recounts every file in the MODEL Data Pack and checks that the CSV files match the original JSON.
Standard library only. Run from anywhere: python verify.py   (it reads the folders next to this file)
Checks for each table: the row count equals the count taken straight from the JSON, every flattened column of every row equals the CSV cell,
and the top-level scalar fields of the first, middle and last record equal the CSV cells. It then recomputes the counts and groups that the
files state about each other: the outcome counts per source against the claims, and the per-accelerator groups in accelerators_summary.json
against the rows of accelerators.csv."""
import csv, json, os, re, statistics, sys, collections
H = os.path.dirname(os.path.abspath(__file__))

def slug(k):
    return re.sub(r'[^A-Za-z0-9]+', '_', str(k)).strip('_')

def flatten(rec, prefix=''):
    out = {}
    for k, v in rec.items():
        name = (prefix + '_' if prefix else '') + slug(k)
        if isinstance(v, dict):
            out.update(flatten(v, name))
        elif isinstance(v, list):
            out[name + '_json'] = json.dumps(v, separators=(',', ':'), ensure_ascii=False)
        else:
            out[name] = v
    assert len(out) >= len(rec) or not rec
    return out

def cell(v):
    if v is None: return ''
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, str): return v
    return json.dumps(v)

def flat_meta(d, prefix=''):
    out = {}
    for k, v in d.items():
        name = (prefix + '.' if prefix else '') + str(k)
        if isinstance(v, dict): out.update(flat_meta(v, name))
        elif isinstance(v, list): out[name] = json.dumps(v, separators=(',', ':'), ensure_ascii=False)
        else: out[name] = v
    return out

def keyed(d, key):
    return [dict({key: k}, **v) for k, v in d.items()]

def load_json(p):
    with open(p, encoding='utf-8') as f:
        if p.endswith('.jsonl'): return [json.loads(l) for l in f if l.strip()]
        return json.load(f)

TALLY_COLS = ['source_key', 'ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL']

def tally_rows(d):
    return [{c: (v.get(c) if c != 'source_key' else k) for c in TALLY_COLS} for k, v in d['summary']['tally'].items()]

# name: (json file, rows(d), independent row count(d), preferred column order or None)
TABLES = {
    'claims': ('claims.json', lambda d: d['claims'], lambda d: len(d['claims']), None),
    'claims_sources': ('claims.json', lambda d: d['summary']['sources'], lambda d: len(d['summary']['sources']), None),
    'claims_tally': ('claims.json', tally_rows, lambda d: len(d['summary']['tally']), TALLY_COLS),
    'claims_vendor_page_hash': ('claims.json', lambda d: [{'source_key': k, 'sha256': v} for k, v in d['summary']['vendor_page_hash'].items()], lambda d: len(d['summary']['vendor_page_hash']), None),
    'claims_mlcommons_files': ('claims.json', lambda d: keyed(d['summary']['mlcommons_files'], 'version'), lambda d: len(d['summary']['mlcommons_files']), None),
    'accelerators_summary': ('accelerators_summary.json', lambda d: d, lambda d: len(d), None),
    'storage_v30_rows': ('storage_v30_results.json', lambda d: d['rows'], lambda d: len(d['rows']), None),
    'mac_run': ('mac_run.jsonl', lambda d: d, lambda d: len(d), None),
}
# top-level keys that go to <name>_meta.csv as key,value rows: name -> (json file, keys)
META = {
    'claims': ('claims.json', None),   # every key of summary except the ones that have their own table
    'storage_v30': ('storage_v30_results.json', ['source', 'licence']),
}
OWN_TABLE_KEYS = ('tally', 'vendor_page_hash', 'mlcommons_files', 'sources')

def meta_want(ds, d):
    if ds == 'claims': return flat_meta({k: v for k, v in d['summary'].items() if k not in OWN_TABLE_KEYS})
    return flat_meta({k: d[k] for k in META[ds][1]})

def eq(csv_val, v):
    if v is None or v == '': return csv_val == ''
    if isinstance(v, bool): return csv_val == ('true' if v else 'false')
    if isinstance(v, (int, float)): return csv_val != '' and float(csv_val) == float(v)
    return csv_val == v

def read_csv(p):
    with open(p, newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def main():
    cache, fails, summary = {}, [], []
    def J(name):
        if name not in cache: cache[name] = load_json(os.path.join(H, 'json', name))
        return cache[name]
    for t, (jf, rows, count, order) in TABLES.items():
        d = J(jf); recs = rows(d); n = count(d)
        got = read_csv(os.path.join(H, 'csv', t + '.csv'))
        ok = len(got) == n == len(recs)
        if not ok: fails.append(f'{t}: csv rows {len(got)}, json rows {n}')
        bad = 0
        for i, (r, c) in enumerate(zip(recs, got)):
            for col, v in flatten(r).items():
                if col not in c or not eq(c[col], v):
                    bad += 1
                    if bad < 4: fails.append(f'{t} row {i} column {col}: csv {c.get(col)!r} json {v!r}')
        for i in sorted({0, len(recs) // 2, len(recs) - 1}):
            for k, v in recs[i].items():
                if not isinstance(v, (dict, list)) and not eq(got[i][slug(k)], v): fails.append(f'{t} sample row {i} field {k}: csv {got[i][slug(k)]!r} json {v!r}')
        summary.append(f'{t}.csv: {len(got)} rows, {len(got[0]) if got else 0} columns, {"OK" if ok and not bad else "FAIL"}')
    for ds, (jf, keys) in META.items():
        d = J(jf); want = meta_want(ds, d)
        got = {r['key']: r['value'] for r in read_csv(os.path.join(H, 'csv', ds + '_meta.csv'))}
        bad = [k for k, v in want.items() if k not in got or not eq(got[k], v)]
        if len(got) != len(want) or bad: fails.append(f'{ds}_meta: {len(got)} rows, expected {len(want)}, mismatched {bad[:3]}')
        summary.append(f'{ds}_meta.csv: {len(got)} rows, {"OK" if not bad and len(got) == len(want) else "FAIL"}')
    # the files state counts about each other: recompute them
    d = J('claims.json'); cl = d['claims']; s = d['summary']
    if s['claims'] != len(cl): fails.append(f'summary says {s["claims"]} claims, the file has {len(cl)}')
    tally = collections.defaultdict(collections.Counter)
    for c in cl: tally[c['source_key']][c['outcome']] += 1
    if {k: dict(v) for k, v in tally.items()} != s['tally']: fails.append('the tally in the summary differs from the outcomes counted over the claims')
    if set(tally) != {x['key'] for x in s['sources']} or set(tally) != set(s['vendor_page_hash']): fails.append('the source keys of claims, sources and vendor_page_hash differ')
    summary.append(f'claims: {len(cl)} rows in {len(tally)} sources, outcome counts per source recomputed from the rows: {"OK" if "tally" not in " ".join(fails) else "FAIL"}')
    acc = read_csv(os.path.join(H, 'csv', 'accelerators.csv'))
    if len(acc) != s['accelerator_rows']: fails.append(f'accelerators.csv has {len(acc)} rows, the summary says {s["accelerator_rows"]}')
    g = collections.defaultdict(list)
    for r in acc: g[(r['version'], r['model'], r['scenario'], r['accelerator'], r['units'])].append(r)
    asum = J('accelerators_summary.json'); gb = 0
    if len(g) != len(asum) or len(g) != s['accelerator_groups']: fails.append(f'groups: {len(g)} from the rows, {len(asum)} in the summary file, {s["accelerator_groups"]} stated'); gb += 1
    for x in asum:
        rs = g.get((x['version'], x['model'], x['scenario'], x['accelerator'], x['units']), [])
        p = [float(r['per_accelerator']) for r in rs]
        if not p: gb += 1; continue
        best = max(rs, key=lambda r: float(r['per_accelerator']))['id']
        if not (len(rs) == x['submissions'] and len({r['submitter'] for r in rs}) == x['submitters'] and min(p) == x['min'] and max(p) == x['max']
                and abs(statistics.median(p) - x['median']) <= 1e-9 * max(1, abs(x['median'])) and best == x['best_id']): gb += 1
    if gb: fails.append(f'accelerators_summary.json: {gb} groups differ from accelerators.csv')
    summary.append(f'accelerators.csv: {len(acc)} rows in {len(g)} groups, count, submitters, min, median, max and best entry of every group recomputed: {"OK" if not gb else "FAIL"}')
    print('MODEL Data Pack verification'); print('\n'.join(summary))
    print('JSON files: ' + ', '.join(sorted(os.listdir(os.path.join(H, 'json')))))
    if fails:
        print('FAILURES'); print('\n'.join(fails[:40])); sys.exit(1)
    print('All checks passed.')

if __name__ == '__main__':
    main()
