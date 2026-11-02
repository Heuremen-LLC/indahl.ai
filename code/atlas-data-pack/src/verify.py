"""verify.py: recounts every file in the ATLAS Data Pack and checks that the CSV and GeoJSON files match the original JSON.
Standard library only. Run from anywhere: python verify.py   (it reads the folders next to this file)
Checks for each table: row count equals the count taken straight from the JSON, every flattened column of every row equals the CSV cell,
the top-level scalar fields of the first, middle and last record equal the CSV cells, and for point data the GeoJSON has the same
number of features with the same properties and with coordinates in [lon, lat] order."""
import csv, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__))

def slug(k):
    return re.sub(r'[^a-z0-9]+', '_', str(k).lower()).strip('_')

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

def keyed(d, key, extra=None):
    return [dict(extra or {}, **{key: k}, **v) for k, v in d.items()]

def with_(rows, **x):
    return [dict(r, **x) for r in rows]

def planned_generators(d):
    out = []
    for p in d['plants']:
        for i, (yr, mw, fuel) in enumerate(p['years']):
            out.append({'plant_code': p['code'], 'plant_name': p['name'], 'state': p['state'], 'generator_index': i, 'year': yr, 'mw': mw, 'fuel': fuel, 'built': d['built']})
    return out

# name: (json file, rows(d), independent row count(d), geo, meta keys)
TABLES = {
    'datacenters_osm': ('datacenters.json', lambda d: with_(d['osm'], pulled=d['pulled']), lambda d: len(d['osm']), True),
    'datacenters_epoch': ('datacenters.json', lambda d: with_(d['epoch'], pulled=d['pulled']), lambda d: len(d['epoch']), True),
    'electricity_states': ('electricity.json', lambda d: with_(keyed(d['states'], 'state_code'), built=d['built'], price_year=d['price_year'], generation_year=d['generation_year']), lambda d: len(d['states']), False),
    'electricity_us': ('electricity.json', lambda d: [dict({k: v for k, v in d['us'].items() if k != 'ownership'}, built=d['built'], price_year=d['price_year'], generation_year=d['generation_year'])], lambda d: 1, False),
    'electricity_us_ownership': ('electricity.json', lambda d: with_(d['us']['ownership'], built=d['built'], price_year=d['price_year']), lambda d: len(d['us']['ownership']), False),
    'utilities': ('utilities.json', lambda d: with_(d['utilities'], year=d['year']), lambda d: len(d['utilities']), False),
    'plants': ('plants.json', lambda d: with_(d['plants'], built=d['built']), lambda d: len(d['plants']), True),
    'planned': ('planned.json', lambda d: with_(d['plants'], built=d['built']), lambda d: len(d['plants']), True),
    'planned_generators': ('planned.json', planned_generators, lambda d: sum(len(p['years']) for p in d['plants']), False),
    'carbon_states': ('carbon.json', lambda d: with_(keyed(d['states'], 'state_code'), built=d['built'], data_year=d['data_year']), lambda d: len(d['states']), False),
    'carbon_subregions': ('carbon.json', lambda d: with_(d['subregions'], built=d['built'], data_year=d['data_year']), lambda d: len(d['subregions']), False),
    'carbon_us': ('carbon.json', lambda d: [dict(d['us'], built=d['built'], data_year=d['data_year'])], lambda d: 1, False),
    'scale_states': ('scale.json', lambda d: with_(keyed(d['states'], 'state_code'), built=d['built'], price_year=d['price_year']), lambda d: len(d['states']), False),
    'scale_sites': ('scale.json', lambda d: with_(d['sites'], built=d['built'], price_year=d['price_year']), lambda d: len(d['sites']), False),
    'scale_corrections': ('scale.json', lambda d: with_(d['corrections'], built=d['built']), lambda d: len(d['corrections']), False),
}
# top-level keys that go to <dataset>_meta.csv as key,value rows
META = {
    'datacenters': ['pulled'],
    'electricity': ['built', 'price_year', 'generation_year', 'unit', 'method', 'sources', 'legend', 'unplaced_data_centers'],
    'utilities': ['year', 'note'],
    'plants': ['built', 'source'],
    'planned': ['built', 'source'],
    'carbon': ['built', 'data_year', 'source', 'legend'],
    'scale': ['built', 'hours_per_year', 'price_year', 'unit_price', 'unit_cost', 'method', 'sources', 'totals'],
}

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
        if name not in cache:
            with open(os.path.join(H, 'json', name), encoding='utf-8') as f: cache[name] = json.load(f)
        return cache[name]
    for t, (jf, rows, count, geo) in TABLES.items():
        d = J(jf); recs = rows(d); n = count(d)
        got = read_csv(os.path.join(H, 'csv', t + '.csv'))
        ok = len(got) == n == len(recs)
        if not ok: fails.append(f'{t}: csv rows {len(got)}, json rows {n}')
        bad = 0
        for i, (r, c) in enumerate(zip(recs, got)):
            for col, v in flatten(r).items():
                if col not in c or not eq(c[col], v): bad += 1; fails.append(f'{t} row {i} column {col}: csv {c.get(col)!r} json {v!r}') if bad < 4 else None
        for i in sorted({0, len(recs) // 2, len(recs) - 1}):
            for k, v in recs[i].items():
                if not isinstance(v, (dict, list)) and not eq(got[i][slug(k)], v): fails.append(f'{t} sample row {i} field {k}: csv {got[i][slug(k)]!r} json {v!r}')
        line = f'{t}.csv: {len(got)} rows, {len(got[0]) if got else 0} columns, {"OK" if ok and not bad else "FAIL"}'
        if geo:
            with open(os.path.join(H, 'geojson', t + '.geojson'), encoding='utf-8') as f: g = json.load(f)
            feats = g['features']; gb = 0
            if g.get('type') != 'FeatureCollection' or len(feats) != n: fails.append(f'{t}: geojson features {len(feats)}, json rows {n}'); gb += 1
            for r, ft in zip(recs, feats):
                if ft['properties'] != r: gb += 1
                geom = ft['geometry']
                if r.get('lat') is None:
                    if geom is not None: gb += 1
                elif geom['type'] != 'Point' or geom['coordinates'] != [r['lon'], r['lat']]: gb += 1
            if gb: fails.append(f'{t}: {gb} geojson mismatches')
            nul = sum(1 for ft in feats if ft['geometry'] is None)
            line += f' | {t}.geojson: {len(feats)} features ({nul} without coordinates), {"OK" if not gb else "FAIL"}'
        summary.append(line)
    for ds, keys in META.items():
        d = J(ds + '.json'); want = flat_meta({k: d[k] for k in keys})
        got = {r['key']: r['value'] for r in read_csv(os.path.join(H, 'csv', ds + '_meta.csv'))}
        bad = [k for k, v in want.items() if k not in got or not eq(got[k], v)]
        if len(got) != len(want) or bad: fails.append(f'{ds}_meta: {len(got)} rows, expected {len(want)}, mismatched {bad[:3]}')
        summary.append(f'{ds}_meta.csv: {len(got)} rows, {"OK" if not bad and len(got) == len(want) else "FAIL"}')
    print('ATLAS Data Pack verification'); print('\n'.join(summary))
    jf = sorted(os.listdir(os.path.join(H, 'json')))
    print('JSON files: ' + ', '.join(jf))
    if fails:
        print('FAILURES'); print('\n'.join(fails[:40])); sys.exit(1)
    print('All checks passed.')

if __name__ == '__main__':
    main()
