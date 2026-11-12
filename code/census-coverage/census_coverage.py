#!/usr/bin/env python3
"""census_coverage.py: reads data/raw (no network, no key), applies the rules in PLAN.md (sealed, data/plan_seal.json), writes summary_coverage.json and data/known_good_rows.json.
--selftest: rule checks only. One run at a time (lock).
This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."""
import json, os, sys, re, fcntl, hashlib, datetime
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H)
import heuremen_kit as K
_LK = open('.coverage.lock', 'a')
try: fcntl.flock(_LK, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('another run holds the lock'); sys.exit(2)
Z = 1.645
RAW = 'data/raw/'
SENT = -9999.9

def num(x):
    if x is None: return None
    try: v = float(str(x).replace('–', '-').replace('*', '').replace(',', '').strip())
    except ValueError: return None
    return v

def interval(est, se):
    if est is None or se is None or se <= 0 or se == SENT: return None
    return (est - Z * se, est + Z * se)

# 12 Nov 2026, Faults and Guards 2.0 (PLAN_ADDENDUM_std2.md): zero (and a national component value) is a point figure with no tolerance and no size that matters is named,
# so a reading is ABOVE, BELOW, or CANNOT_TELL with STRADDLES_EDGE. CONSISTENT is not available. The desk's own causes (no estimate, no SE, SE zero or the sentinel) are NO_INTERVAL_FORMABLE.
DETAIL = {}   # last plain cause of a NO_INTERVAL_FORMABLE, read by the caller as reason_detail
def read_vs_zero(est, se):
    """returns (outcome, reason, lo, hi). reason is a closed code or None. Rule of PLAN_ADDENDUM_std2.md."""
    DETAIL['d'] = ''
    if est is None: DETAIL['d'] = 'no estimate'; return K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE, None, None
    if se is None: DETAIL['d'] = 'no standard error'; return K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE, None, None
    if se == SENT or se <= 0: DETAIL['d'] = 'standard error zero or not served'; return K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE, None, None
    lo, hi = interval(est, se)
    o, r = K.read(lo, hi, bound=0.0)
    return o, r, lo, hi

def read_vs_point(est, se, point):
    DETAIL['d'] = ''
    if est is None or se is None or se == SENT or se <= 0 or point is None:
        DETAIL['d'] = 'no standard error' if (se is None or se == SENT or (se is not None and se <= 0)) else 'no estimate'
        return K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE, None, None
    lo, hi = interval(est, se)
    o, r = K.read(lo, hi, bound=point)
    return o, r, lo, hi

def da_cell(series):
    """series: low, middle, high NCE in percent, read as a range against zero (a range of scenarios, not an interval). Returns (outcome, reason)."""
    v = [x for x in series if x is not None]
    if len(v) < 3: return K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE
    return K.read(min(v), max(v), bound=0.0)

def rule_selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok; ok &= bool(cond); print(('OK   ' if cond else 'FAIL ') + name)
    chk('wholly below zero is BELOW (Arkansas -5.04 SE 2.21)', read_vs_zero(-5.04, 2.21)[0] == K.BELOW)
    chk('wholly above zero is ABOVE (Hawaii 6.79 SE 1.68)', read_vs_zero(6.79, 1.68)[0] == K.ABOVE)
    chk('interval holds zero is CANNOT_TELL STRADDLES_EDGE, never CONSISTENT (California 0.47 SE 0.65)', read_vs_zero(0.47, 0.65)[:2] == (K.CANNOT_TELL, K.STRADDLES_EDGE))
    chk('edge at zero is CANNOT_TELL STRADDLES_EDGE', read_vs_zero(-1.645, 1.0)[:2] == (K.CANNOT_TELL, K.STRADDLES_EDGE) and read_vs_zero(1.645, 1.0)[:2] == (K.CANNOT_TELL, K.STRADDLES_EDGE))
    chk('just past the edge reads BELOW and ABOVE', read_vs_zero(-1.65, 1.0)[0] == K.BELOW and read_vs_zero(1.65, 1.0)[0] == K.ABOVE)
    chk('no SE is CANNOT_TELL NO_INTERVAL_FORMABLE with its plain cause', read_vs_zero(1.0, None)[:2] == (K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE) and DETAIL['d'] == 'no standard error')
    chk('no estimate is CANNOT_TELL NO_INTERVAL_FORMABLE with its plain cause', read_vs_zero(None, 1.0)[:2] == (K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE) and DETAIL['d'] == 'no estimate')
    chk('SE of zero is CANNOT_TELL', read_vs_zero(1.0, 0.0)[0] == K.CANNOT_TELL)
    chk('sentinel -9999.9 is CANNOT_TELL', read_vs_zero(1.0, SENT)[0] == K.CANNOT_TELL and read_vs_point(1.0, SENT, 1.0)[0] == K.CANNOT_TELL)
    chk('component against national point: below, above, straddles', read_vs_point(4.4, 0.6, 5.8)[0] == K.BELOW and read_vs_point(6.0, 2.0, 5.8)[:2] == (K.CANNOT_TELL, K.STRADDLES_EDGE) and read_vs_point(9.9, 0.5, 5.8)[0] == K.ABOVE)
    chk('DA range: all under zero BELOW, all over ABOVE, mixed STRADDLES_EDGE, missing NO_INTERVAL_FORMABLE', da_cell([-1, -.5, -.1])[0] == K.BELOW and da_cell([.1, .2, .3])[0] == K.ABOVE and da_cell([.22, -.35, -1.21]) == (K.CANNOT_TELL, K.STRADDLES_EDGE) and da_cell([.2, None, -1]) == (K.CANNOT_TELL, K.NO_INTERVAL_FORMABLE))
    chk('num reads the Census en dash and asterisk', num('*–5.04') == -5.04 and num('4,896,000') == 4896000 and num('X') is None)
    return ok, 'rule selftest ' + ('PASSED' if ok else 'FAILED')

if '--selftest' in sys.argv:
    ok, t = rule_selftest(); print(t); sys.exit(0 if ok and K.selftest() else 1)

# ---------------- load raw
def table(path):
    d = json.load(open(path)); h = d[0]; return h, [dict(zip(h, r)) for r in d[1:]]
_, G = table(RAW + 'pes_g_states.json')
hh, Hrows = table(RAW + 'pes_H_STATES.json')
PL = json.load(open(RAW + 'census2020_pl_state.json'))
a = json.load(open(RAW + 'pes_A_TOTUS.json')); A = dict(zip(a[0], a[1]))
b = json.load(open(RAW + 'pes_B_TOTUS.json')); B = dict(zip(b[0], b[1]))
FIPS_STATES = {str(i).zfill(2) for i in range(1, 57)} - {'03', '07', '14', '43', '52'}
PDF = open(RAW + 'census-coverage-estimates-for-people-in-the-united-states-by-state-and-census-operations.txt').read()
REL = open(RAW + 'census_release_20220310.html').read()

# ---------------- parse the Census PDF, Appendix Tables 3 and 4
def parse_pdf():
    L = [x.strip() for x in PDF.split('\n')]
    def seg(title):
        for i, x in enumerate(L):
            if x.startswith('Appendix Table ' + title) and 'Net Coverage Error Rates for the Household Population in the United States by State' in ' '.join(L[i:i + 4]) if title == '3.' else (x.startswith('Appendix Table ' + title) and 'by State' in ' '.join(L[i:i + 4]) and 'Components' in ' '.join(L[i:i + 4])):
                j = next(k for k in range(i + 1, len(L)) if L[k].startswith('Source:')); return L[i:j]
        return []
    out3 = {}; s = seg('3.'); i = 0
    while i < len(s) - 3:
        m = re.match(r'^(.+?)[\s.]*$', s[i])
        if m and re.search(r'[A-Za-z]', s[i]) and re.search(r'^\d{1,3}(,\d{3})+$', s[i + 1] or ''):
            name = re.sub(r'[\s.]+$', '', s[i]); out3[name] = dict(count=num(s[i + 1]), nce=num(s[i + 2]), se=num(s[i + 3]), star='*' in s[i + 2]); i += 4
        else: i += 1
    return out3
PDF3 = parse_pdf()
def pdf_row_tokens(state):
    L = [x.strip() for x in PDF.split('\n')]
    for i, x in enumerate(L):
        if re.match(r'^%s[\s.]*$' % re.escape(state), x) and i > 1700 and re.search(r'^\d{1,3}(,\d{3})+$', L[i + 1] or '') and re.match(r'^\d\d\.\d$', L[i + 2] or ''): return L[i + 1:i + 20]
    return []

# ---------------- areas
areas = []
for r in G:
    if r['state'] not in FIPS_STATES: continue
    name = r['NAME']; est = num(r['G_STATES_002']); se = num(r['G_STATES_003']); cnt = num(r['G_STATES_001'])
    o, why, lo, hi = read_vs_zero(est, se)
    areas.append(dict(area=name, fips=r['state'], household_count=cnt, resident_total=PL.get(name), nce=est, se=se, lo90=lo, hi90=hi, outcome=o, reason=why, reason_detail=DETAIL['d']))
areas.sort(key=lambda x: x['area'])

# components by state
Hc = {}
for r in Hrows:
    if r['state'] in FIPS_STATES: Hc.setdefault(r['NAME'], {})[r['H_STATES_001']] = r
NAT = {'omissions': ('H_STATES_010', num(B['B_TOTUS_COL3_R13']), num(B['B_TOTUS_COL4_R13'])),
       'duplication': ('H_STATES_006', num(B['B_TOTUS_COL3_R8']), num(B['B_TOTUS_COL4_R8'])),
       'other_erroneous': ('H_STATES_007', num(B['B_TOTUS_COL3_R9']), num(B['B_TOTUS_COL4_R9']))}
comp = []; comp_counts = {k: {o: 0 for o in K.OUTCOMES} for k in NAT}; comp_why = {k: {} for k in NAT}
for ar in areas:
    row = dict(area=ar['area']); cs = Hc.get(ar['area'], {})
    for k, (f, npt, nse) in NAT.items():
        est = num(cs.get('COUNT', {}).get(f)); se = num(cs.get('SE', {}).get(f))
        o, why, lo, hi = read_vs_point(est, se, npt)
        row[k] = dict(est=est, se=se, lo90=lo, hi90=hi, outcome=o, reason=why, reason_detail=DETAIL['d']); comp_counts[k][o] += 1
        if why: comp_why[k][why] = comp_why[k].get(why, 0) + 1
    row['nce_h_states'] = num(cs.get('COUNT', {}).get('H_STATES_011')); comp.append(row)

# ---------------- cells
counts = {o: sum(1 for x in areas if x['outcome'] == o) for o in K.OUTCOMES}
why_ct = {}
for x in areas:
    if x['reason'] and x['outcome'] == K.CANNOT_TELL: why_ct[x['reason']] = why_ct.get(x['reason'], 0) + 1
below = [x['area'] for x in areas if x['outcome'] == K.BELOW]; above = [x['area'] for x in areas if x['outcome'] == K.ABOVE]
flo = K.floor(counts[K.BELOW] + counts[K.ABOVE], len(areas), 0.10)
us_est, us_se = num(A['A_TOTUS_COL4_R1']), num(A['A_TOTUS_COL5_R1'])
us_o, us_why, us_lo, us_hi = read_vs_zero(us_est, us_se)
DA = dict(low=0.22, middle=-0.35, high=-1.21)
da_o, da_r = da_cell([DA['low'], DA['middle'], DA['high']])
pes_inside_da = (min(DA.values()) <= us_est <= max(DA.values()))
pes_int_inside_da = (us_lo is not None and min(DA.values()) <= us_lo and us_hi <= max(DA.values()))

# ---------------- known-good gates
kg = {}; details = {}
def gate_reader():
    miss = []; n = 0
    for x in areas:
        p = PDF3.get(x['area']); n += 1
        if not p or p['count'] != x['household_count'] or p['nce'] != x['nce'] or p['se'] != x['se']: miss.append(x['area'])
    details['reader_areas_compared'] = n; details['reader_mismatch'] = miss
    return n == 51 and not miss
def gate_flags():
    star_b = sorted(k for k, v in PDF3.items() if v['star'] and v['nce'] < 0); star_a = sorted(k for k, v in PDF3.items() if v['star'] and v['nce'] > 0)
    census_named_b = sorted(['Arkansas', 'Florida', 'Illinois', 'Mississippi', 'Tennessee', 'Texas'])
    census_named_a = sorted(['Delaware', 'Hawaii', 'Massachusetts', 'Minnesota', 'New York', 'Ohio', 'Rhode Island', 'Utah'])
    details['asterisk_undercount'] = star_b; details['asterisk_overcount'] = star_a
    return star_b == census_named_b == sorted(below) and star_a == census_named_a == sorted(above)
def gate_join():
    bad = [x['area'] for x, c in zip(areas, comp) if c['nce_h_states'] != x['nce']]
    details['join_h_states_mismatch'] = bad
    us_ok = num(B['B_TOTUS_COL3_R14']) == us_est and num(B['B_TOTUS_COL4_R14']) == us_se
    ark = Hc['Arkansas']; t4 = pdf_row_tokens('Arkansas'); details['arkansas_pdf_table4_tokens'] = t4[:19]
    # tokens: count, 003 v,se, 004 v,se, 005 v,se, 006 v,se, 007 v,se, 008 v,X, 009 v,se, 010 v,se, nce, se
    ark_ok = bool(t4) and num(ark['COUNT']['H_STATES_010']) == num(t4[15]) == 10.1 and num(ark['SE']['H_STATES_010']) == num(t4[16]) == 2.0 and num(ark['COUNT']['H_STATES_006']) == num(t4[7]) and num(ark['COUNT']['H_STATES_007']) == num(t4[9])
    return (not bad) and us_ok and ark_ok
def gate_da():
    return all(s in REL for s in ('0.22', '-0.35', '-1.21', '-0.24', '0.25')) and 'Table 1. Post-Enumeration Survey (PES) and Demographic Analysis (DA)' in re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', REL)) and (DA['low'], DA['middle'], DA['high']) == (0.22, -0.35, -1.21)
HAND = {'Arkansas': (2929000, -5.04, 2.21, K.BELOW), 'Texas': (28540000, -1.92, 0.82, K.BELOW), 'California': (38620000, 0.47, 0.65, K.CANNOT_TELL), 'Hawaii': (1415000, 6.79, 1.68, K.ABOVE), 'Florida': (21070000, -3.48, 0.91, K.BELOW)}
def gate_hand():
    for s, (c, n, e, o) in HAND.items():
        x = next(y for y in areas if y['area'] == s)
        if (x['household_count'], x['nce'], x['se'], x['outcome']) != (c, n, e, o): return False
    return True
kg['reader'] = K.known_good(lambda c: gate_reader(), None)
kg['census_flags'] = K.known_good(lambda c: gate_flags(), None)
kg['join'] = K.known_good(lambda c: gate_join(), None)
kg['hand_five_states'] = K.known_good(lambda c: gate_hand(), None)
kg['da_source'] = K.known_good(lambda c: gate_da(), None)
rs_ok, rs_msg = rule_selftest(); kg['rule'] = (rs_ok and K.selftest(), rs_msg)
gates_ok = all(v[0] for v in kg.values())
if not gates_ok:
    areas = K.apply_gate(False, areas)
    for x in areas: x['reason'] = K.NO_INTERVAL_FORMABLE; x['reason_detail'] = 'known-good gate failed'
    for k in counts: counts[k] = 0
    counts[K.CANNOT_TELL] = len(areas); why_ct = {K.NO_INTERVAL_FORMABLE: len(areas)}
    da_o = K.CANNOT_TELL; da_r = K.NO_INTERVAL_FORMABLE; us_o = K.CANNOT_TELL; us_why = K.NO_INTERVAL_FORMABLE

seal = json.load(open('data/plan_seal.json'))
plan_sha = hashlib.sha256(open('PLAN.md', 'rb').read()).hexdigest()
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
if seal.get('first_computed_reading') is None and gates_ok is not None:
    seal['first_computed_reading'] = now
    # the seal file is written once, the first time a reading is computed
    json.dump(seal, open('data/plan_seal.json', 'w'), indent=1); open('data/plan_seal.json', 'a').write('\n')
S = dict(generated=now, plan_sha256=plan_sha, plan_sha256_sealed=seal['plan_sha256'], plan_matches_seal=(plan_sha == seal['plan_sha256']), plan_commit=seal['plan_commit'], plan_commit_time=seal['plan_commit_time'], first_computed_reading=seal['first_computed_reading'],
         multiplier=Z, frame='50 states and the District of Columbia (51 areas), household population, excludes group quarters and Remote Alaska',
         counts=counts, cannot_tell_why=why_ct, below=below, above=above, floor=flo,
         us_pes=dict(household_count_thousands=num(A['A_TOTUS_COL1_R1']), nce=us_est, se=us_se, lo90=us_lo, hi90=us_hi, outcome=us_o, reason=us_why),
         da=dict(low=DA['low'], middle=DA['middle'], high=DA['high'], outcome=da_o, reason=da_r, pes_national_point_inside_range=pes_inside_da, pes_national_interval_inside_range=pes_int_inside_da, source='Census Bureau release CB22-CN.02, 10 March 2022, Table 1'),
         components=dict(national={k: dict(est=v[1], se=v[2]) for k, v in NAT.items()}, counts=comp_counts, cannot_tell_why=comp_why),
         gates={k: dict(passed=v[0], message=v[1]) for k, v in kg.items()}, gate_details=details, gates_all_passed=gates_ok,
         req13=K.req13(areas, nothing_returned=0), components_req13={k: K.req13([c[k] for c in comp], nothing_returned=0) for k in NAT},
         areas=areas, component_rows=comp)
json.dump(S, open('summary_coverage.json', 'w'), indent=1); open('summary_coverage.json', 'a').write('\n')
json.dump(dict(hand_five=HAND, pdf_appendix3_areas=len(PDF3)), open('data/known_good_rows.json', 'w'), indent=1)
print('gates', {k: v[0] for k, v in kg.items()})
print('counts', counts, 'why', why_ct); print('BELOW', below); print('ABOVE', above); print('floor', flo)
print('US', us_est, us_se, us_o, 'DA', da_o, DA, 'PES point inside DA range', pes_inside_da, 'interval inside', pes_int_inside_da)
print('components', comp_counts, comp_why)
