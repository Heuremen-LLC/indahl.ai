#!/usr/bin/env python3
"""RANK, New Jersey (PLAN Addendum 1): US News figures against NJ School Performance Reports (SPR), NCES CCD and college Common Data Sets,
plus who is in the proficiency figure (participation) and SPR's school-day figures beside published schedules. Same rule (rule.py).
Output: data/checks_nj.json. Values are read from public/nj/nj_public.json (SPR summary blocks, each with its file, sheet and row),
public/nj/ccd_grades/*.json (CCD 2024-25 enrollment by grade), public/nj_college/nj_college_public.json, public/nj_claims/schedules.json.
Arithmetic done here and named on the page: grade 9-12 sums, CCD lunch counts over CCD enrollment, SPR science levels 3 plus 4 (each printed
as a whole percent, so the sum can differ from an unrounded figure by up to 1), and 100 minus the participation rate. Heuremen LLC."""
import json, os, re, sys
from decimal import Decimal
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); sys.path.insert(0, HERE)
from rule import compare
OUT = []
def add(lst, school, field, usn, uy, pub, py, source, note='', shown_pub=None):
    oc, why = compare(usn, pub, uy, py)
    OUT.append(dict(list=lst, school=school, field=field, usn=usn, usn_year=uy, pub=shown_pub if shown_pub is not None else pub, pub_year=py, source=source,
                    note=note.replace('; ', ', ').replace(';', ','), outcome=oc, reason=why))
NJ = json.load(open('public/nj/nj_public.json', encoding='utf-8'))['schools']
def spr(name):
    k = re.sub(r'[^a-z0-9]', '', name.lower().replace('dr. ronald e mcnair', 'dr ronald mcnair'))
    c = [s for s in NJ if re.sub(r'[^a-z0-9]', '', s['name'].lower()).startswith(k[:18])]
    assert len(c) == 1, (name, [s['name'] for s in c]); return c[0]
def num(v): m = re.search(r'-?\d+(?:\.\d+)?', str(v)); return m.group(0) if m else None
SPRURL = 'https://www.nj.gov/education/sprreports/download/DataFiles/'

# ---------- High schools ----------
U = {}
sec = False
for ln in open('raw/nj_hs_20261110.txt', encoding='utf-8'):
    if ln.startswith('== school pages'): sec = True; continue
    if sec and ': ' in ln and ' | ' in ln:
        n, rest = ln.split(': ', 1); U[n.strip()] = [x.strip() for x in rest.split(' | ')]
G = {g: {r['ncessch']: r['enrollment'] for r in json.load(open(f'public/nj/ccd_grades/enr_2024_g{g}.json'))['results']} for g in (9, 10, 11, 12)}
for name, (m, r_, sci, grad, enr, ed, fr, rd) in U.items():
    s = spr(name); S = s['summary']; nid = s['nces_id']
    e23, m23 = S.get('ELA 2023-24', {}), S.get('Math 2023-24', {})
    def trow(sheet):
        rr = [x for x in s['records'] if x.get('sheet') == sheet and x.get('school_year') == '2023-24' and x['values'].get('Subgroup') == 'Total']
        return rr[0] if rr else None
    sc = trow('SC11')
    if sc and num(sc['values'].get('L3 Percent')) is not None and num(sc['values'].get('L4 Percent')) is not None and sc['values'].get('Valid Scores', '*') != '*':
        v = sc['values']; pub = str(Decimal(num(v['L3 Percent'])) + Decimal(num(v['L4 Percent'])))
        add('nj_hs', name, 'Science proficiency', None if sci == '-' else sci, '2023-24', pub, '2023-24', sc['source_url'] + f", row {sc['row']}",
            f"NJSLA Science grade 11 file, all students: level 3 {v['L3 Percent']} plus level 4 {v['L4 Percent']} percent of {v['Valid Scores']} valid scores.")
    else:
        add('nj_hs', name, 'Science proficiency', None if sci == '-' else sci, '2023-24', '*', '2023-24', 'NJSLA Science grade 11 file 2023-24', 'The state file suppresses this school\'s science row.')
    # display only: valid-score-weighted met or exceeded (levels 4 and 5) across the high school math test files
    tot = met = 0; parts = []; supp = False
    for sh in ('ALG01', 'GEO01', 'ALG02'):
        t = trow(sh)
        if not t: continue
        v = t['values']
        if v.get('Valid Scores', '*') == '*' or num(v.get('L4 Percent')) is None: supp = True; parts.append(f'{sh} suppressed'); continue
        n = int(v['Valid Scores']); pm = Decimal(num(v['L4 Percent'])) + Decimal(num(v['L5 Percent']))
        tot += n; met += pm * n / 100; parts.append(f'{sh} {pm} percent of {n}')
    malt = str((met * 100 / tot).quantize(Decimal('0.0001'))) if tot and not supp else None
    t2 = m2 = 0; s2 = False
    for sh in ('GEO01', 'ALG02'):
        t = trow(sh)
        if not t: continue
        v = t['values']
        if v.get('Valid Scores', '*') == '*' or num(v.get('L4 Percent')) is None: s2 = True; continue
        n = int(v['Valid Scores']); t2 += n; m2 += (Decimal(num(v['L4 Percent'])) + Decimal(num(v['L5 Percent']))) * n / 100
    malt2 = str((m2 * 100 / t2).quantize(Decimal('0.1'))) if t2 and not s2 else None
    srcm = 'NJSLA 2023-24 mathematics files ALG01, GEO01, ALG02 (https://www.nj.gov/education/assessment/results/reports/2324/spring/)'
    note_m = f"State test files, all students, levels 4 and 5 (met or exceeded), weighted by valid scores: {', '.join(parts)}. SPR's school-wide figure: {num(m23.get('met_or_exceeded_pct'))}. US News does not state which mathematics tests it counts. Without Algebra I the files give {malt2 if malt2 else 'no figure'}."
    usn_m = None if m == '-' else m
    if malt and usn_m and compare(usn_m, malt, 'x', 'x')[0] != 'MATCH':
        add('nj_hs', name, 'Mathematics proficiency', usn_m, '2023-24', 'see note', None, srcm, note_m + ' The readings differ, and the tests counted are not stated, so this reads cannot tell.', shown_pub=malt)
        OUT[-1]['outcome'], OUT[-1]['reason'], OUT[-1]['pub_year'] = 'CANNOT_TELL', 'definition', '2023-24'
    else:
        add('nj_hs', name, 'Mathematics proficiency', usn_m, '2023-24', malt if malt else ('*' if supp else None), '2023-24', srcm, note_m)
    e9 = trow('ELA09')
    if e9 and e9['values'].get('Valid Scores', '*') != '*' and num(e9['values'].get('L4 Percent')) is not None:
        v = e9['values']; pe = str(Decimal(num(v['L4 Percent'])) + Decimal(num(v['L5 Percent'])))
        add('nj_hs', name, 'Reading proficiency', None if r_ == '-' else r_, '2023-24', pe, '2023-24', e9['source_url'] + f", row {e9['row']}",
            f"NJSLA ELA grade 9 file, all students: level 4 {v['L4 Percent']} plus level 5 {v['L5 Percent']} percent of {v['Valid Scores']} valid scores. SPR's school-wide ELA figure: {num(e23.get('met_or_exceeded_pct'))}.")
    else:
        add('nj_hs', name, 'Reading proficiency', None if r_ == '-' else r_, '2023-24', '*', '2023-24', 'NJSLA ELA grade 9 file 2023-24', "The state file suppresses this school's ELA row.")
    gr = (S.get('Graduation (2023-24 report)') or {}).get('2024 4-Year Federal Graduation Rate')
    add('nj_hs', name, 'Graduation rate', grad, 'class of 2024', num(gr) if gr and num(gr) else gr, 'class of 2024', SPRURL + '2023-2024/Database_SchoolDetail.xlsx, ' + (S.get('Graduation (2023-24 report)') or {}).get('cite', ''), 'SPR 2024 four-year federal graduation rate.')
    g = [G[x].get(nid) for x in (9, 10, 11, 12)]
    add('nj_hs', name, 'Enrollment, grades 9 to 12', enr, '2024-25', str(sum(g)) if all(isinstance(x, int) and x >= 0 for x in g) else None, '2024-25', 'NCES CCD via educationdata.urban.org', f'Grades 9, 10, 11, 12: {", ".join(map(str, g))}.')
    c = S.get('NCES 2024-25') or {}
    for usn, key, lab in ((fr, 'free_lunch', 'Free lunch share'), (rd, 'reduced_price_lunch', 'Reduced-price lunch share'), (ed, None, 'Economically disadvantaged share (free or reduced-price lunch)')):
        cnt = (c.get('free_lunch', -1) + c.get('reduced_price_lunch', -1)) if key is None and c.get('free_lunch', -1) >= 0 and c.get('reduced_price_lunch', -1) >= 0 else c.get(key, -1) if key else -1
        if cnt is None or cnt < 0 or not c.get('enrollment'):
            add('nj_hs', name, lab, usn, '2024-25', None, '2024-25', 'NCES CCD', 'CCD reports this count as missing.'); continue
        add('nj_hs', name, lab, usn, '2024-25', str((Decimal(cnt) * 100 / Decimal(c['enrollment'])).quantize(Decimal('0.0001'))), '2024-25', 'NCES CCD via educationdata.urban.org', f"{cnt} of {c['enrollment']} enrolled.")

# ---------- Elementary and middle ----------
K = {}; sec = False
for ln in open('raw/nj_k8_20261110.txt', encoding='utf-8'):
    if ln.startswith('== profiles'): sec = True; continue
    if sec and ': ' in ln and ' | ' in ln:
        n, rest = ln.split(': ', 1); K[n.strip()] = [x.strip().split(' ')[0] for x in rest.split(' | ')]
SLUGNAME = {}
for ln in open('raw/nj_k8_20261110.txt', encoding='utf-8'):
    if ln.startswith('#'):
        p = ln.strip().split(';'); SLUGNAME[re.sub(r'-\d+$', '', p[7])] = p[1]
for slug, (enr, m, r_, ed) in K.items():
    name = SLUGNAME[slug]; s = spr(name); S = s['summary']
    def wtd(prefixes, year):
        tot = met = 0; supp = []; n_t = 0
        for x in s['records']:
            if x.get('family') != 'assess' or x.get('school_year') != year or x['values'].get('Subgroup') != 'Total': continue
            if not str(x.get('sheet', '')).startswith(prefixes): continue
            v = x['values']; n_t += 1
            if v.get('Valid Scores', '*') == '*' or num(v.get('L4 Percent')) is None or num(v.get('L5 Percent')) is None: supp.append(x['sheet']); continue
            n = int(v['Valid Scores']); tot += n; met += (Decimal(num(v['L4 Percent'])) + Decimal(num(v['L5 Percent']))) * n / 100
        if not n_t: return None, 'no test rows'
        if supp: return None, 'suppressed rows: ' + ', '.join(sorted(set(supp)))
        return str((met * 100 / tot).quantize(Decimal('0.0001'))), f'{tot} valid scores'
    for lab, usn, key, pre in (('Mathematics proficiency', m, 'Math', ('MAT', 'ALG', 'GEO')), ('Reading proficiency', r_, 'ELA', ('ELA',))):
        a, b = S.get(f'{key} 2023-24', {}), S.get(f'{key} 2024-25', {})
        va, vb = num(a.get('met_or_exceeded_pct')), num(b.get('met_or_exceeded_pct'))
        (ta, na), (tb, nb) = wtd(pre, '2023-24'), wtd(pre, '2024-25')
        yn = lambda v: ('yes' if compare(usn, v, 'x', 'x')[0] == 'MATCH' else 'no') if v else 'not compared'
        fm = lambda v: str(Decimal(v).quantize(Decimal('0.1'))) if v else 'none'
        add('nj_k8', name, lab, usn, None, 'see note', None, 'NJSLA test files and SPR, 2023-24 and 2024-25',
            f"US News's method page names no test year. State test files, levels 4 and 5 weighted by valid scores: 2023-24 {fm(ta)} ({na}), 2024-25 {fm(tb)} ({nb}). Equal after rounding: 2023-24 {yn(ta)}, 2024-25 {yn(tb)}. SPR school-wide: 2023-24 {va}, 2024-25 {vb}. Shown after the data, not scored.", shown_pub='')
    c23, c24 = S.get('NCES 2023-24') or {}, S.get('NCES 2024-25') or {}
    def sh(c):
        return str((Decimal(c['free_lunch'] + c['reduced_price_lunch']) * 100 / Decimal(c['enrollment'])).quantize(Decimal('0.1'))) if c.get('free_lunch', -1) >= 0 and c.get('reduced_price_lunch', -1) >= 0 and c.get('enrollment') else None
    a, b = sh(c23), sh(c24); usn = None if ed == '-' else ed
    eq = lambda v: ('yes' if compare(usn, v, 'x', 'x')[0] == 'MATCH' else 'no') if (v and usn) else 'not compared'
    add('nj_k8', name, 'Economically disadvantaged share (free or reduced-price lunch)', usn, None, 'see note', None, 'NCES CCD via educationdata.urban.org',
        f"The profile figure carries no year. The method names CCD 2023-24 for the model inputs, not for the profile. CCD free or reduced-price lunch over enrollment: 2023-24 {a}, 2024-25 {b}. Equal after rounding: 2023-24 {eq(a)}, 2024-25 {eq(b)}. Shown after the data, not scored.", shown_pub='')

# ---------- Who is in the proficiency figure ----------
PART = []
for s in NJ:
    S = s['summary']; row = dict(school=s['name'], code='-'.join(s['nj_codes'].values()))
    for key in ('ELA', 'Math'):
        for y, fld in (('2023-24', 'pct_students_taking_test'), ('2024-25', 'participation_rate')):
            v = num((S.get(f'{key} {y}') or {}).get(fld)); row[f'{key} {y}'] = v
            row[f'{key} {y} not in figure'] = str((Decimal(100) - Decimal(v)).quantize(Decimal('0.1'))) if v else None
    nt = [x.get('not_tested') for y in ('2023-24', '2024-25') for x in (S.get(f'Registered/NotTested/Valid {y}') or [])]
    row['not tested counts'] = 'suppressed (*) in every test file row' if nt and all(x == '*' for x in nt) else ', '.join(map(str, nt))
    aa = []
    for y, keys in (('2023-24', ('SPR alternate assessment 2023-24',)), ('2024-25', ('SPR DLM 2024-25',))):
        vals = sorted({str(x.get('ELAStudentsTested')) for k_ in keys for x in (S.get(k_) or [])})
        aa.append(f"{y}: " + (' or '.join(vals) if vals else 'not printed'))
    row['alternate assessment'] = ', '.join(aa)
    PART.append(row)

# ---------- School day ----------
def yl(t):
    m = re.match(r'(\d{4}-\d{2})', str(t or ''))
    return (m.group(1) + (' (year inferred from dates on the calendar)' if 'inferred' in str(t) else '')) if m else 'year not printed'
SCH = json.load(open('public/nj_claims/schedules.json', encoding='utf-8'))
DAY = []
for s in NJ:
    S = s['summary']; d23, d24 = S.get('SchoolDay 2023-24') or {}, S.get('SchoolDay 2024-25') or {}
    nk = lambda t: re.sub(r'[^a-z0-9]', '', t.lower().replace('dr. ronald e. mcnair academic', 'dr ronald mcnair').replace('dr ronald e mcnair', 'dr ronald mcnair'))[:12]
    k = nk(s['name'])
    pubs = [x for x in SCH if (lambda o: o.startswith(k) or k.startswith(o))(nk(str(x.get('school', ''))))]
    DAY.append(dict(school=s['name'], spr_2023_24=f"{d23.get('TypicalStartTime')} to {d23.get('TypicalEndTime')}, day {d23.get('LengthOfDay')}, instruction {d23.get('InstructionFullTime')}" if d23 else '',
                    spr_2024_25=f"{d24.get('TypicalStartTime')} to {d24.get('TypicalEndTime')}, day {d24.get('LengthOfDay')}, instruction {d24.get('InstructionFullTime')}" if d24 else '',
                    published=[dict(year=yl(x.get('school_year')), states=x.get('quote'), url=x.get('url')) for x in pubs]))

# ---------- New Jersey colleges ----------
CN = json.load(open('public/nj_college/nj_college_public.json', encoding='utf-8'))
CKEY = {'princeton-university-2627': 'princeton', 'rutgers-new-brunswick-6964': 'rutgers_nb', 'stevens-institute-of-technology-2639': 'stevens', 'rutgers-university-newark-2631': 'rutgers_newark',
        'njit-2621': 'njit', 'rutgers-university-camden-4741': 'rutgers_camden', 'montclair-state-university-2617': 'montclair', 'seton-hall-university-new-jersey-2632': 'setonhall',
        'monmouth-university-2616': 'monmouth', 'rowan-university-2609': 'rowan', 'drew-university-2603': 'drew', 'the-college-of-new-jersey-2642': 'tcnj'}
sec = False
for ln in open('raw/nj_colleges_20261110.txt', encoding='utf-8'):
    if ln.startswith('== profiles'): sec = True; continue
    m = re.match(r'([a-z0-9-]+-\d+): (.+)$', ln.strip())
    if not (sec and m and m.group(1) in CKEY): continue
    enr, acc, sat, act, g4, ratio, small = [x.strip() for x in m.group(2).split(' | ')]
    c = CN[CKEY[m.group(1)]]; nm = c['college']; y = ((c.get('cds') or {}).get('years') or {}).get('2025-2026') or {}
    y = y if y.get('exists') else {}
    b1 = str(y['B1_total_undergrad']['value']) if isinstance(y.get('B1_total_undergrad'), dict) else None
    add('nj_col', nm, 'Undergraduate enrollment', enr, 'fall 2025', b1, 'fall 2025' if b1 else None, 'Common Data Set 2025-26, item B1 ' + y.get('source_url', ''),
        '' if b1 else 'No Common Data Set 2025-26 is posted on the college site, or it was not read.')
    disp = []
    if y:
        c1, c9, i3, bg = y.get('C1') or {}, y.get('C9') or {}, y.get('I3') or {}, y.get('B_grad') or {}
        def chk(lab, usn, pub):
            if usn in (None, '', '?') or pub in (None, ''): return
            pv = pub if not re.match(r'^\d+\.\d{3,}$', pub) else str(Decimal(pub).quantize(Decimal('0.1')))
            disp.append(f'{lab} {usn}, Common Data Set {pv}, equal after rounding ' + ('yes' if compare(usn, pub, 'x', 'x')[0] == 'MATCH' else 'no'))
        if c1.get('applicants') and c1.get('admits'): chk('acceptance rate', acc, str(Decimal(c1['admits']) * 100 / Decimal(c1['applicants'])))
        if c9.get('SAT_comp_25'): chk('SAT', sat, f"{c9['SAT_comp_25']}-{c9['SAT_comp_75']}")
        if c9.get('ACT_comp_25'): chk('ACT', act, f"{c9['ACT_comp_25']}-{c9['ACT_comp_75']}")
        r = re.match(r'\s*([\d.]+)', str(y.get('I2_ratio') or ''))
        if r: chk('student/faculty ratio', ratio, r.group(1) + ':1')
        if i3.get('total'): chk('classes under 20', small, str(Decimal(i3['2-9'] + i3['10-19']) * 100 / Decimal(i3['total'])))
        if bg.get('B6_adj_cohort') and bg.get('B7_4yr'): chk('4-year graduation rate', g4, str(Decimal(bg['B7_4yr']) * 100 / Decimal(bg['B6_adj_cohort'])))
    for lab, v in (('Acceptance rate', acc), ('SAT range', sat), ('ACT range', act), ('4-year graduation rate', g4), ('Student/faculty ratio', ratio), ('Classes with fewer than 20 students', small)):
        add('nj_col', nm, lab, v, None, 'see note', None, 'Common Data Set 2025-26 ' + y.get('source_url', ''), 'The US News page prints no year for this figure.' if v not in (None, '', '?') else 'US News prints no figure here.', shown_pub='')
    OUT.append(dict(list='nj_col', school=nm, field='_display_cds2025', note='; '.join(disp) if disp else ('Only item B1 could be read' if b1 else 'No Common Data Set 2025-26 was read'), outcome='DISPLAY', reason='after the data, not scored'))

json.dump(dict(read='2026-11-10', checks=OUT, participation=PART, school_day=DAY), open('data/checks_nj.json', 'w'), indent=1, ensure_ascii=False)
from collections import Counter
print(Counter((o['list'], o['outcome'], o['reason']) for o in OUT))
