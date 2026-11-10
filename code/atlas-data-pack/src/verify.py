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

METHODS = ('nominatim address', 'nominatim city/zip only')

def place_split(placed):
    """splits the JSON field placed into (place_method, place_match)"""
    if not placed: return '', ''
    if placed in METHODS: return placed, ''
    if placed.startswith('corrected '): return 'corrected', placed[len('corrected '):]
    return 'address match', placed

def place_join(method, match):
    if not method and not match: return ''
    if method in METHODS: return method
    if method == 'corrected': return 'corrected ' + match
    return match

def epoch_rows(d):
    out = []
    for r in d['epoch']:
        m, a = place_split(r['placed']); n = {}
        for k, v in r.items():
            if k == 'placed': n['place_method'] = m; n['place_match'] = a
            else: n[k] = v
        out.append(dict(n, pulled=d['pulled']))
    return out

def cada_rows(d):
    out = []
    for r in d['resolvers']:
        for cp, v in r['checkpoints'].items():
            share, lo, hi = v['wilson'] or (None, None, None)
            out.append({'resolver': r['resolver'], 'checkpoint_s': cp, 'k': v['k'], 'n': v['n'], 'timeouts': v['timeouts'], 'share_pct': share, 'lo_pct': lo, 'hi_pct': hi, 'state': v['state'], 'updated': d['updated']})
    return out

# name: (json file, rows(d), independent row count(d), geo, meta keys)
TABLES = {
    'datacenters_osm': ('datacenters.json', lambda d: with_(d['osm'], pulled=d['pulled']), lambda d: len(d['osm']), True),
    'datacenters_epoch': ('datacenters.json', epoch_rows, lambda d: len(d['epoch']), True),
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
    # WATER (10 Nov 2026): water.json is the desk's live.json as served at /water/live.json, water_rows.json the row file of the same run
    'water_cells': ('water.json', lambda d: with_(d['cells'], updated=d['updated']), lambda d: len(d['cells']), False),
    'water_rows': ('water_rows.json', lambda d: d, lambda d: len(d), False),
    'water_band_sentence_cells': ('water.json', lambda d: with_(d['band_sentence_months']['cells'], updated=d['updated']), lambda d: len(d['band_sentence_months']['cells']), False),
    'water_variants': ('water.json', lambda d: d['variants'], lambda d: len(d['variants']), False),
    'water_notable': ('water.json', lambda d: d['notable'], lambda d: len(d['notable']), False),
    'water_misread_by_era': ('water.json', lambda d: d['misread_by_era'], lambda d: len(d['misread_by_era']), False),
    'water_flagged_groups': ('water.json', lambda d: d['flagged']['groups'], lambda d: len(d['flagged']['groups']), False),
    'water_reservoirs': ('water.json', lambda d: d['live']['others'], lambda d: len(d['live']['others']), False),
    'water_thresholds': ('water.json', lambda d: d['live']['thresholds'], lambda d: len(d['live']['thresholds']), False),
    'water_usgs_revisions': ('water.json', lambda d: with_(d['usgs_revisions']['gauges'], first_read=d['usgs_revisions']['first_read']), lambda d: len(d['usgs_revisions']['gauges']), False),
    # the other desks listed under ATLAS (10 Nov 2026): each JSON is the desk's live.json as served, with updated (UTC, day and month) on every row
    'uptime_vendors': ('uptime.json', lambda d: with_(d['vendors'], updated=d['updated']), lambda d: len(d['vendors']), False),
    'uptime_incidents': ('uptime.json', lambda d: [dict(vendor=v['vendor'], **i) for v in d['vendors'] for i in v['incidents']], lambda d: sum(len(v['incidents']) for v in d['vendors']), False),
    'time_servers': ('time.json', lambda d: with_(d['servers'], updated=d['updated']), lambda d: len(d['servers']), False),
    'cada_checkpoints': ('cada.json', cada_rows, lambda d: sum(len(r['checkpoints']) for r in d['resolvers']), False),
    'cada_answer_classes': ('cada.json', lambda d: [dict({'resolver': r['resolver']}, **r['classes'], updated=d['updated']) for r in d['resolvers']], lambda d: len(d['resolvers']), False),
    'cada_alive': ('cada.json', lambda d: [{'checkpoint_s': k, 'alive': d['alive'][k], 'not_alive': d['not_alive'].get(k), 'updated': d['updated']} for k in d['alive']], lambda d: len(d['alive']), False),
    'secrecords_comparison': ('secrecords.json', lambda d: [dict({'claim': k}, **v, **{'class_' + c: m for c, m in d['classes'].get(k, {}).items()}, updated=d['updated'], listdate=d['listdate']) for k, v in d['comparison'].items()], lambda d: len(d['comparison']), False),
    'secrecords_descriptive': ('secrecords.json', lambda d: with_(keyed(d['descriptive'], 'label'), updated=d['updated']), lambda d: len(d['descriptive']), False),
    'secrecords_dmarc': ('secrecords.json', lambda d: with_(keyed(d['dmarc'], 'policy'), updated=d['updated']), lambda d: len(d['dmarc']), False),
    'secrecords_read_in_full': ('secrecords.json', lambda d: with_(d['disagree_list'], updated=d['updated']), lambda d: len(d['disagree_list']), False),
    'seat_now': ('seat.json', lambda d: with_(keyed(d['now'], 'check'), last_probe=d['last_probe']), lambda d: len(d['now']), False),
    'seat_rolling': ('seat.json', lambda d: with_(keyed(d['rolling'], 'window'), last_probe=d['last_probe']), lambda d: len(d['rolling']), False),
    'seat_incidents': ('seat.json', lambda d: d['incidents'], lambda d: len(d['incidents']), False),
    'seat_feeds': ('seat.json', lambda d: with_(d['feeds'], last_probe=d['last_probe']), lambda d: len(d['feeds']), False),
    'support_all': ('support.json', lambda d: [dict(d['all'], updated=d['updated'])], lambda d: 1, False),
    'support_product_level': ('support.json', lambda d: with_(keyed(d['product_level'], 'reading'), updated=d['updated']), lambda d: len(d['product_level']), False),
    'support_by_product': ('support.json', lambda d: with_(keyed(d['by_product'], 'product'), updated=d['updated']), lambda d: len(d['by_product']), False),
    'support_unreleased_cycles': ('support.json', lambda d: with_(d['silent_list'], updated=d['updated']), lambda d: len(d['silent_list']), False),
    'support_after_eol': ('support.json', lambda d: with_(keyed(d['after_eol'], 'when'), updated=d['updated']), lambda d: len(d['after_eol']), False),
    'change_test': ('change.json', lambda d: [dict(d['test'], updated=d['updated'])], lambda d: 1, False),
    'change_upcoming': ('change.json', lambda d: with_(d['upcoming'], updated=d['updated']), lambda d: len(d['upcoming']), False),
    'change_list': ('change.json', lambda d: with_(d['change_list'], updated=d['updated']), lambda d: len(d['change_list']), False),
    'change_sources': ('change.json', lambda d: with_(d['sources'], updated=d['updated']), lambda d: len(d['sources']), False),
    'change_lifespan': ('change.json', lambda d: with_(keyed(d['lifespan'], 'names'), updated=d['updated']), lambda d: len(d['lifespan']), False),
    'change_notice': ('change.json', lambda d: with_(keyed(d['notice'], 'vendor'), updated=d['updated']), lambda d: len(d['notice']), False),
    'change_kinds': ('change.json', lambda d: with_(keyed(d['changes'], 'kind'), updated=d['updated']), lambda d: len(d['changes']), False),
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
    # a callable picks the fields itself, leaving out the lists that have their own CSV
    'water': lambda d: dict({k: d[k] for k in ('updated', 'gate', 'stale_sources', 'coverage', 'headline_lead6', 'checks_after_data_note', 'measured_cross_checks')},
                            flagged={k: v for k, v in d['flagged'].items() if k != 'groups'}, band_sentence_months={k: v for k, v in d['band_sentence_months'].items() if k != 'cells'},
                            live={k: v for k, v in d['live'].items() if k not in ('others', 'thresholds')}),
    'uptime': ['updated', 'seats', 'seats_counted', 'floor_upper_bound', 'buckets', 'control', 'totals'],
    'time': ['updated', 'seat', 'reference', 'seat_part_ms', 'totals', 'rounds', 'seat2'],
    'cada': ['updated', 'tracked', 'feed_reads'],
    'secrecords': ['updated', 'gate', 'domains', 'awaiting', 'listdate'],
    'seat': ['updated', 'probes', 'failed_controls', 'last_probe', 'flagged_probes', 'not_matching'],
    'support': ['updated', 'gate', 'products', 'no_cycles', 'cycles', 'supported_tested', 'apart'],
    'change': ['updated', 'first_snapshot', 'rows'],
}

def meta_of(ds, d):
    keys = META[ds]
    return keys(d) if callable(keys) else {k: d[k] for k in keys}

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
            if not 0 <= i < len(got): continue   # a short CSV is already a failure on the row count
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
        if t == 'datacenters_epoch':
            back = [place_join(c['place_method'], c['place_match']) for c in got]
            if back != [r['placed'] for r in d['epoch']]: fails.append('datacenters_epoch: place_method and place_match do not rebuild the JSON placed field')
            else: line += ' | place_method + place_match rebuild placed: OK'
        summary.append(line)
    for ds, keys in META.items():
        d = J(ds + '.json'); want = flat_meta(meta_of(ds, d))
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
