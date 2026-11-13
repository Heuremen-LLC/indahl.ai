#!/usr/bin/env python3
"""census_vintages.py: reads data/raw, applies PLAN.md, writes summary_vintages.json. Network only for the PES standard error cross-check (cget.sh, key read at call time, never stored).
Heuremen LLC, 11 Nov 2026. This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.  Run: python3 -I census_vintages.py"""
import csv, json, os, sys, subprocess, hashlib, statistics, datetime
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
R = 'data/raw/'; MULT = 1.645
def sh(*a): return subprocess.run(a, capture_output=True, text=True).stdout.strip()
# seal
seal = json.load(open('data/plan_seal.json')); plan_sha = hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest()
plan_ok = (plan_sha == seal['plan_sha256']) and K.plan_committed('PLAN.md') and sh('git', 'log', '-1', '--format=%H', '--', 'PLAN.md') == seal['plan_commit']
# areas and PES widths (census_coverage summary)
CS = json.load(open(os.path.expanduser('~/bones-forge/census_coverage/summary_coverage.json')))
AREAS = [a['area'] for a in CS['areas']]; PES = {a['area']: a['se'] for a in CS['areas']}
def flat(f, cols):
    d = {}
    for r in csv.DictReader(open(R + f, encoding='latin1')):
        if r['NAME'] in PES: d[r['NAME']] = {c: r.get(c) for c in cols}
    return d
def num(x):
    try: return int(x)
    except Exception: return None
v19 = flat('nst-est2019-alldata.csv', ['POPESTIMATE%d' % y for y in range(2010, 2020)])
v20 = flat('nst-est2020.csv', ['POPESTIMATE%d' % y for y in range(2010, 2021)] + ['POPESTIMATE042020'])
v2x = {}
for v, f, last in ((2022, 'NST-EST2022-ALLDATA.csv', 2022), (2023, 'NST-EST2023-ALLDATA.csv', 2023), (2024, 'NST-EST2024-ALLDATA.csv', 2024), (2025, 'NST-EST2025-ALLDATA.csv', 2025)):
    v2x[v] = flat(f, ['ESTIMATESBASE2020'] + ['POPESTIMATE%d' % y for y in range(2020, last + 1)])
api21 = {r[0]: r for r in json.load(open(R + 'api2021.json'))[1:] if r[0] in PES}
api19 = {}
for r in json.load(open(R + 'api2019.json'))[1:]:
    if r[0] in PES and 3 <= int(r[2]) <= 12: api19[(r[0], 2007 + int(r[2]))] = int(r[1])
census = json.load(open(R + 'census2020_pl_state.json'))
# value tables: VAL[(vintage, year)] -> {area: int}; base: BASE[vintage]
VAL = {}
for y in range(2010, 2020): VAL[('V2019', y)] = {a: num(v19[a]['POPESTIMATE%d' % y]) for a in AREAS if a in v19}
for y in range(2010, 2021): VAL[('V2020', y)] = {a: num(v20[a]['POPESTIMATE%d' % y]) for a in AREAS if a in v20}
for y in (2020, 2021): VAL[('V2021', y)] = {a: num(api21[a][1 if y == 2020 else 2]) for a in AREAS if a in api21}
for v, d in v2x.items():
    for y in range(2020, v + 1): VAL[('V%d' % v, y)] = {a: num(d[a]['POPESTIMATE%d' % y]) for a in AREAS if a in d}
APR20 = {a: num(v20[a]['POPESTIMATE042020']) for a in AREAS if a in v20}
BASE = {'V%d' % v: {a: num(d[a]['ESTIMATESBASE2020']) for a in AREAS if a in d} for v, d in v2x.items()}
CEN = {a: census.get(a) for a in AREAS}
# gates
def pesapi():
    out = subprocess.run([os.path.expanduser('~/bones-forge/census_scout/cget.sh'), 'https://api.census.gov/data/2020/dec/pes?get=NAME,G_STATES_003&for=state:*'], capture_output=True, text=True).stdout
    return {r[0]: float(r[1]) for r in json.loads(out)[1:] if r[1] is not None}
gd = {}
def g_format(_):
    need19 = all(a in v19 and all(num(v19[a]['POPESTIMATE%d' % y]) for y in range(2010, 2020)) for a in AREAS)
    need20 = all(a in v20 and all(num(v20[a]['POPESTIMATE%d' % y]) for y in range(2010, 2021)) and num(v20[a]['POPESTIMATE042020']) for a in AREAS)
    need2x = all(all(a in d and num(d[a]['ESTIMATESBASE2020']) and all(num(d[a]['POPESTIMATE%d' % y]) for y in range(2020, v + 1)) for a in AREAS) for v, d in v2x.items())
    need21 = all(a in api21 and num(api21[a][1]) and num(api21[a][2]) for a in AREAS)
    gd['format'] = dict(v19=need19, v20=need20, v2x=need2x, api21=need21, areas=len(AREAS)); return need19 and need20 and need2x and need21 and len(AREAS) == 51
def g_join(_):
    mism = [(a, y) for a in AREAS for y in range(2010, 2020) if api19.get((a, y)) != VAL[('V2019', y)][a]]
    tot = sum(CEN[a] for a in AREAS); gd['join'] = dict(api19_mismatch=mism, census_total=tot)
    hand = {('California', 'V2019', 2019): 39512223, ('Texas', 'V2019', 2019): 28995881, ('Arkansas', 'V2019', 2019): 3017804}
    hv = {('California', 'V2020', 2020): 39368078, ('Texas', 'V2020', 2020): 29360759, ('Arkansas', 'V2020', 2020): 3030522}
    hand.update(hv)
    for v, ca, tx, ar in (('V2022', 39501653, 29232474, 3014195), ('V2023', 39503200, 29234361, 3014348), ('V2024', 39521958, 29239570, 3014546), ('V2025', 39527808, 29237895, 3014399)):
        hand.update({('California', v, 2020): ca, ('Texas', v, 2020): tx, ('Arkansas', v, 2020): ar})
    bad = [k for k, x in hand.items() if VAL[(k[1], k[2])][k[0]] != x]
    apr = {'California': 39418894, 'Texas': 29286467, 'Arkansas': 3029672}; cen = {'California': 39538223, 'Texas': 29145505, 'Arkansas': 3011524}
    bad += [('apr', a) for a, x in apr.items() if APR20[a] != x] + [('census', a) for a, x in cen.items() if CEN[a] != x]
    gd['join']['hand_mismatch'] = bad; gd['join']['hand_values_checked'] = len(hand) + 6
    s20 = sum(VAL[('V2021', 2020)][x] for x in AREAS); s21 = sum(VAL[('V2021', 2021)][x] for x in AREAS); gd['join']['v2021_sum_2020'] = s20; gd['join']['v2021_sum_2021'] = s21
    return not mism and tot == 331449281 and not bad and s20 == 331501080 and s21 == 331893745
def g_width(_):
    try: api = pesapi()
    except Exception as ex: gd['width'] = dict(error=type(ex).__name__); return False
    mism = [a for a in AREAS if api.get(a) != PES[a]]; gd['width'] = dict(api_rows=len(api), mismatch=mism, min_se=min(PES.values())); return not mism and min(PES.values()) > 0 and len(PES) == 51
# rule
def read_row(anchor, later, se, cls):
    """returns (outcome, reason, half_width)"""
    if cls == 'A': return (K.CANNOT_TELL, 'no width', None)
    if anchor is None or later is None: return (K.CANNOT_TELL, 'no stated or later value', None)
    if se is None or se <= 0: return (K.CANNOT_TELL, 'no PES width', None)
    h = MULT * se / 100.0 * anchor
    if later > anchor + h: return (K.ABOVE, '', h)
    if later < anchor - h: return (K.BELOW, '', h)
    return (K.CONSISTENT, '', h)
def g_rule(_):
    t = [(('B', 1000, 1100, 3.0), 'ABOVE'), (('B', 1000, 900, 3.0), 'BELOW'), (('B', 1000, 1000, 3.0), 'CONSISTENT'), (('C', 1000, 1000 + 1.645 * 3.0 * 10, 3.0), 'CONSISTENT'),
         (('D', 1000, 1000 - 1.645 * 3.0 * 10 - 1, 3.0), 'BELOW'), (('A', 1000, 1000, 3.0), 'CANNOT_TELL'), (('B', None, 1000, 3.0), 'CANNOT_TELL'), (('B', 1000, 1000, 0.0), 'CANNOT_TELL'), (('B', 1000, 1000, None), 'CANNOT_TELL')]
    ok = all(read_row(a, l, s, c)[0] == w for (c, a, l, s), w in t)
    reasons = [read_row(1000, 1000, 3.0, 'A')[1], read_row(None, 1, 3.0, 'B')[1], read_row(1000, 1, 0, 'B')[1]] == ['no width', 'no stated or later value', 'no PES width']
    return ok and reasons and K.selftest.__name__ == 'selftest'
gates = {}
for name, fn in (('format', g_format), ('join', g_join), ('width', g_width), ('rule', g_rule)):
    p, m = K.known_good(fn, None); gates[name] = dict(passed=p, message=m)
sys.stdout = open(os.devnull, 'w'); kit_ok = K.selftest(); sys.stdout = sys.__stdout__
gates['kit_selftest'] = dict(passed=bool(kit_ok), message='passed' if kit_ok else 'FAILED')
passed = all(g['passed'] for g in gates.values()) and plan_ok
# rows
ROWS = []
def add(cls, cell, area, year, stated, later, anchor_label, note=''):
    o, why, h = read_row(stated, later, PES[area], cls)
    ROWS.append(dict(cls=cls, cell=cell, area=area, year=year, stated=stated, later=later, se=PES[area], half=h, outcome=o, reason=why))
for a in AREAS:
    for (va, vb) in [('V2019', 'V2020')] + [('V%d' % i, 'V%d' % j) for i in range(2021, 2026) for j in range(i + 1, 2026)]:
        for y in range(2010, 2026):
            if (va, y) in VAL and (vb, y) in VAL: add('A', '%s to %s' % (va, vb), a, y, VAL[(va, y)].get(a), VAL[(vb, y)].get(a), 'stated')
    for vb in ('V2021', 'V2022', 'V2023', 'V2024', 'V2025'): add('B', 'V2020 to %s, July 1 2020' % vb, a, 2020, VAL[('V2020', 2020)].get(a), VAL[(vb, 2020)].get(a), 'stated')
    add('C', 'V2020 April 1 2020 to the census count', a, 2020, APR20.get(a), CEN.get(a), 'stated')
    for vb in ('V2022', 'V2023', 'V2024', 'V2025'): add('D', 'census count to %s estimates base' % vb, a, 2020, CEN.get(a), BASE[vb].get(a), 'count')
if not passed:
    for r in ROWS: r['outcome_before_gate'] = r['outcome']; r['outcome'] = K.CANNOT_TELL; r['reason'] = 'gate failed'
# cells
cells = []
order = []
for r in ROWS:
    k = (r['cls'], r['cell'])
    if k not in order: order.append(k)
def med(x): return statistics.median(x) if x else None
for cls, cell in order:
    rs = [r for r in ROWS if (r['cls'], r['cell']) == (cls, cell)]
    c = {o: sum(1 for r in rs if r['outcome'] == o) for o in K.OUTCOMES}
    why = {}
    for r in rs:
        if r['outcome'] == K.CANNOT_TELL: why[r['reason']] = why.get(r['reason'], 0) + 1
    ok = [r for r in rs if r['stated'] and r['later'] is not None]
    pct = [100.0 * (r['later'] - r['stated']) / r['stated'] for r in ok]
    hw = [abs(r['later'] - r['stated']) / (MULT * r['se'] / 100.0 * r['stated']) for r in ok if r['se'] and r['se'] > 0]
    neg = sum(1 for p in pct if p < 0); pos = sum(1 for p in pct if p > 0)
    big = max(ok, key=lambda r: abs(r['later'] - r['stated']) / r['stated']) if ok else None
    cells.append(dict(cls=cls, cell=cell, rows=len(rs), counts=c, cannot_tell_why=why, median_abs_pct=med([abs(p) for p in pct]), median_signed_pct=med(pct), n_negative=neg, n_positive=pos, n_zero=len(pct) - neg - pos, n_compared=len(pct), median_abs_in_yardstick_half_widths=med(hw),
                      largest=dict(area=big['area'], year=big['year'], stated=big['stated'], later=big['later'], pct=100.0 * (big['later'] - big['stated']) / big['stated']) if big else None,
                      years=sorted(set(r['year'] for r in rs))))
    if cls in 'BCD':
        sens = {}
        for m in (1.0, 2.0):
            cc = {'ABOVE': 0, 'BELOW': 0, 'CONSISTENT': 0}
            for r in ok:
                h = m * r['se'] / 100.0 * r['stated']
                cc['ABOVE' if r['later'] > r['stated'] + h else ('BELOW' if r['later'] < r['stated'] - h else 'CONSISTENT')] += 1
            sens['x%.1f' % m] = cc
        cells[-1]['sensitivity_multiplier'] = sens
# SECOND RULER, added after the outside referee, not part of the sealed plan and no row outcome uses it.
# Recentre on the state published NCE (percent): gap = (later - stated) / stated x 100, outside when |gap - NCE| > 1.645 x SE.
NCE = {a['area']: a['nce'] for a in CS['areas']}
def second(cell):
    rs = [r for r in ROWS if r['cell'] == cell]; res = {'ABOVE': [], 'BELOW': [], 'CONSISTENT': []}
    for r in rs:
        gap = 100.0 * (r['later'] - r['stated']) / r['stated']; d = gap - NCE[r['area']]
        res['ABOVE' if d > MULT * r['se'] else ('BELOW' if d < -MULT * r['se'] else 'CONSISTENT')].append(r['area'])
    sealed = {o: [r['area'] for r in rs if r['outcome'] == o] for o in ('ABOVE', 'BELOW', 'CONSISTENT')}
    return dict(cell=cell, second={k: dict(count=len(v), areas=sorted(v)) for k, v in res.items()}, sealed={k: dict(count=len(v), areas=sorted(v)) for k, v in sealed.items()})
SECOND = [second('V2020 April 1 2020 to the census count'), second('V2020 to V2025, July 1 2020')]
tot = {o: sum(1 for r in ROWS if r['outcome'] == o) for o in K.OUTCOMES}
byclass = {cl: {o: sum(1 for r in ROWS if r['cls'] == cl and r['outcome'] == o) for o in K.OUTCOMES} for cl in 'ABCD'}
S = dict(generated=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), plan_sha256=plan_sha, plan_sha256_sealed=seal['plan_sha256'], plan_matches_seal=plan_ok,
         plan_commit=seal['plan_commit'], plan_commit_time=seal['plan_commit_time'], multiplier=MULT,
         frame='50 states and the District of Columbia (51 areas), July 1 estimates of V2019 to V2025, the April 1 2020 estimate of V2020, the 2020 Census count and ESTIMATESBASE2020',
         frame_rows=len(ROWS), frame_areas=len(AREAS), counts=tot, counts_by_class=byclass, cells=cells, gates=gates, gates_all_passed=passed, gate_details=gd,
         second_ruler=SECOND, nce={a: NCE[a] for a in AREAS}, pes_se={a: PES[a] for a in AREAS},
         rows=[{k: v for k, v in r.items()} for r in ROWS])
json.dump(S, open('summary_vintages.json', 'w'), indent=1); print('rows', len(ROWS), tot, byclass, 'gates', {k: v['passed'] for k, v in gates.items()}, 'plan_ok', plan_ok)
