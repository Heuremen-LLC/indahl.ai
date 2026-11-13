#!/usr/bin/env python3
"""Referee: 10 seeded rows (stratified by group, seed 20261109) plus the notable rows, read end to end from the live sources.
Wikidata: wbgetclaims by statement id (value, P585, rank, references). Source: the World Bank single-country call for the
current release or the named archived release, or the UIS call for the default or named version."""
import sys, os, json, gzip, time, random, urllib.request, urllib.parse, collections as C
from decimal import Decimal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recount as R
UA = 'HeuremenLLC-research/1.0 (https://indahl.ai)'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'live')
os.makedirs(OUT, exist_ok=True)
_last = [0.0]
def get(url, name):
    p = os.path.join(OUT, name)
    if os.path.exists(p): return json.load(open(p))
    gap = 1.5 - (time.time() - _last[0])
    if gap > 0: time.sleep(gap)
    _last[0] = time.time()
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r: d = json.loads(r.read())
    except Exception as e:
        d = {'_error': str(e)}
    json.dump(d, open(p, 'w'))
    return d

rows = json.load(gzip.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'ref_rows.json.gz'), 'rt'))
vers = {v['value']: v['id'] for v in R.jl(os.path.join(R.RAW, 'wb', 'versions.json.gz'))['source'][0]['concept'][0]['variable']}
uisv = {f"UIS {x['version']} ({x['publicationDate'][:10]})": x['version'] for x in R.jl(os.path.join(R.RAW, 'uis', 'versions.json.gz'))}

rng = random.Random(20261109)
quota = {'WB-POP': 3, 'WB-GDP': 2, 'WB-GINI': 1, 'WB-UNEMP': 1, 'UIS-LE': 2, 'UIS-TFR': 1}
pick = []
for g, n in quota.items():
    pool = sorted([r for r in rows if r['group'] == g], key=lambda r: (r['item'], r['year'], r['value']))
    pick += rng.sample(pool, n)
notable_ids = {'Q958$57892A6F-1C95-4AC6-A154-9ABEEF5679AF', 'Q1183$EC5B5556-0F16-40AE-A9C1-DE78A00BA402', 'Q414$ac3791b9-4b00-e54d-cfaa-f723d08d0fee',
               'Q183$6e4324b9-4a7d-c033-4414-3b58245512e4', 'Q183$eeca0c98-44a5-a1d3-4d06-f3208b13aa06', 'Q958$91B576C8-EE49-4553-9BC7-1A9190F34692',
               'Q798431$C27B27EF-67A6-4E91-BA7B-24EBF4110033', 'Q1246$0C576071-81E4-45D4-9551-BAF8133CAB4E', 'Q1246$70F284D1-5C66-4AB2-9D4D-83B06F0302D3'}
notable = [r for r in rows if set(r['statements']) & notable_ids]
alias = {'DHY': 'BEN', 'XKS': 'XKX'}
out = []
for tag, r in [('random', x) for x in pick] + [('notable', x) for x in notable]:
    prop = R.G[r['group']][0]; src = R.G[r['group']][1]; series = R.G[r['group']][2]
    sid = r['statements'][0]
    d = get('https://www.wikidata.org/w/api.php?action=wbgetclaims&format=json&claim=' + urllib.parse.quote(sid), 'wd_' + sid.replace('$', '_') + '.json')
    c = (d.get('claims', {}).get(prop) or [None])[0]
    if c:
        dv = c['mainsnak']['datavalue']['value']; amt = dv['amount'].lstrip('+'); unit = dv.get('unit', '1').rsplit('/', 1)[-1]
        pit = [q['datavalue']['value']['time'] for q in c.get('qualifiers', {}).get('P585', [])]
        refs = []
        for ref in c.get('references', []):
            sn = ref['snaks']
            refs.append(dict(P248=[s['datavalue']['value']['id'] for s in sn.get('P248', []) if s.get('snaktype') == 'value'],
                             P854=[s['datavalue']['value'] for s in sn.get('P854', []) if s.get('snaktype') == 'value'],
                             P813=[s['datavalue']['value']['time'][1:11] for s in sn.get('P813', []) if s.get('snaktype') == 'value']))
        wd = dict(amount=amt, unit=unit, pit=pit, rank=c['rank'], refs=refs)
    else:
        wd = dict(error=str(d)[:200])
    iso = r['iso'][0]; iso_src = alias.get(iso, iso); y = r['year']
    # source value for the bin's claim
    src_read = {}
    if src == 'WB':
        cu = get(f'https://api.worldbank.org/v2/country/{iso_src}/indicator/{series}?date={y}&format=json&source=2', f'wbcur_{iso_src}_{series}_{y}.json')
        src_read['current'] = cu[1][0]['value'] if isinstance(cu, list) and len(cu) > 1 and cu[1] else None
        if r['hits']:
            vid = vers[r['hits'][-1]]
            a = get(f'https://api.worldbank.org/v2/sources/57/country/{iso_src}/series/{series}/version/{vid}/time/YR{y}?format=json', f'wbarc_{iso_src}_{series}_{vid}_{y}.json')
            dd = a.get('source', {}).get('data') if isinstance(a, dict) else None
            src_read['newest_release'] = (r['hits'][-1], dd[0]['value'] if dd else None)
        elif iso in alias:
            # alias reading: newest release named in the desk's alias row is checked from the archive (look up via recount tables)
            cur, older, _, _ = R.wb_tables(series)
            b, hits, cc = R.bin_of(Decimal(r['v']), Decimal(r['u']), [iso_src], y, cur, older)
            if hits:
                vid = hits[-1][0]
                a = get(f'https://api.worldbank.org/v2/sources/57/country/{iso_src}/series/{series}/version/{vid}/time/YR{y}?format=json', f'wbarc_{iso_src}_{series}_{vid}_{y}.json')
                dd = a.get('source', {}).get('data') if isinstance(a, dict) else None
                src_read['alias_newest_release'] = (hits[-1][1], dd[0]['value'] if dd else None)
    else:
        cu = get(f'https://api.uis.unesco.org/api/public/data/indicators?indicator={series}&geoUnit={iso}&start={y}&end={y}', f'uiscur_{iso}_{series}_{y}.json')
        src_read['current'] = cu['records'][0]['value'] if isinstance(cu, dict) and cu.get('records') else None
        if r['hits']:
            vid = uisv[r['hits'][-1]]
            a = get(f'https://api.uis.unesco.org/api/public/data/indicators?indicator={series}&geoUnit={iso}&start={y}&end={y}&version={vid}', f'uisv_{iso}_{series}_{vid}_{y}.json')
            src_read['newest_release'] = (r['hits'][-1], a['records'][0]['value'] if isinstance(a, dict) and a.get('records') else None)
    # agreement
    ok_wd = 'amount' in wd and Decimal(wd['amount']) == Decimal(r['v']) and any(p[1:5] == str(y) for p in wd['pit'])
    ok_ref = 'refs' in wd and any((('Q21540096' in x['P248']) or any('worldbank.org' in u or 'banquemondiale.org' in u for u in x['P854'])) if src == 'WB'
                                  else (('Q3152127' in x['P248']) or any('uis.unesco.org' in u for u in x['P854'])) for x in wd['refs'])
    cur_v = src_read.get('current')
    ok_cur = (cur_v is None and r['current'] is None) or (cur_v is not None and r['current'] is not None and abs(Decimal(str(cur_v)) - Decimal(r['current'])) <= Decimal('1e-6') * max(1, abs(Decimal(r['current']))))
    bin_ok = None
    if r['bin'] == 'MATCHES_CURRENT': bin_ok = cur_v is not None and R.match(Decimal(r['v']), Decimal(r['u']), Decimal(str(cur_v)))
    elif r['bin'] == 'MATCHES_AN_OLDER_RELEASE':
        nv = src_read.get('newest_release', (None, None))[1]
        bin_ok = nv is not None and R.match(Decimal(r['v']), Decimal(r['u']), Decimal(str(nv))) and not (cur_v is not None and R.match(Decimal(r['v']), Decimal(r['u']), Decimal(str(cur_v))))
    elif r['bin'] == 'MATCHES_NO_RELEASE_READ': bin_ok = not (cur_v is not None and R.match(Decimal(r['v']), Decimal(r['u']), Decimal(str(cur_v))))
    out.append(dict(tag=tag, group=r['group'], item=r['item'], iso=iso, year=y, cited=r['value'], bin=r['bin'], newest=(r['hits'] or [None])[-1], statement=sid,
                    wikidata_live=wd, source_live=src_read, desk_current=r['current'], wikidata_agrees=ok_wd, reference_in_frame=ok_ref, current_agrees=ok_cur, bin_confirmed=bin_ok,
                    rank_desk_default=r['default']))
json.dump(out, open(os.path.join(OUT, '..', 'live_rows.json'), 'w'), indent=1)
for x in out:
    print(f"{x['tag']:8s} {x['group']:8s} {x['item']:8s} {x['iso']} {x['year']} cited {x['cited']:>15s} {x['bin']:26s} newest={x['newest']} | WD amount={x['wikidata_live'].get('amount')} pit={[p[:5] for p in x['wikidata_live'].get('pit', [])]} rank={x['wikidata_live'].get('rank')} "
          f"refs={x['wikidata_live'].get('refs')} | src {x['source_live']} desk_cur={x['desk_current']} | wd_ok={x['wikidata_agrees']} ref_ok={x['reference_in_frame']} cur_ok={x['current_agrees']} bin_ok={x['bin_confirmed']}")
