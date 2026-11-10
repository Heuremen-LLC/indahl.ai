#!/usr/bin/env python3
"""RANK step two: per-figure checks, US News as printed against the public record, by the sealed rule (rule.py, PLAN.md b25e87f).
Inputs: raw/hs_schoolpages_20261110.txt, raw/hs_national_20261110.txt, raw/law_pages_20261110.txt, raw/college_pages*.txt (US News, read 2026-11-10)
        public/hs_public.json, public/law/law_public.json, public/law/downloads/*.xlsx, public/college/college_public.json (public record)
Output: data/checks.json. Every public value is read from its file here, by an explicit map below that names the figure it must be.
Arithmetic done here and named on the page: a percent from a count over a total (CCD lunch counts over CCD enrollment), grades 9 to 12 summed,
Georgia Proficient plus Distinguished counts over tested, a share stored as 0 to 1 turned into a percent, the law two-cohort average US News names.
Standard library only. Heuremen LLC."""
import json, os, re, subprocess, sys
from decimal import Decimal
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); sys.path.insert(0, HERE)
from rule import compare

OUT = []
def add(lst, school, field, usn, usn_year, pub, pub_year, source, note='', same=True, shown_pub=None):
    oc, why = compare(usn, pub, usn_year, pub_year, same)
    note = note.replace('; ', ', ').replace(';', ',')
    OUT.append(dict(list=lst, school=school, field=field, usn=usn, usn_year=usn_year, pub=shown_pub if shown_pub is not None else pub,
                    pub_year=pub_year, source=source, note=note, outcome=oc, reason=why))

# ---------- High schools ----------
HSU = {}
for ln in open('raw/hs_schoolpages_20261110.txt', encoding='utf-8'):
    if ' :: ' not in ln or ln.startswith('read:'): continue
    name, rest = ln.split(' :: ', 1)
    d = {}
    for k, pat in (('grad', r'Graduation Rate ([>\d% ]+?)(?: \||$| ::)'), ('math', r'Mathematics Proficiency (\d+%)'), ('read', r'Reading Proficiency (\d+%)'),
                   ('sci', r'Science Proficiency (\d+%)'), ('ed', r'Economically Disadvantaged ([\dA/V%]+)'), ('free', r'Free Lunch ([\dA/V%]+)'), ('red', r'Reduced-Price Lunch ([\dA/V%]+)')):
        m = re.search(pat, rest); d[k] = m.group(1).strip() if m else None
    HSU[name.strip()] = d
ENR = {}
for ln in open('raw/hs_national_20261110.txt', encoding='utf-8'):
    if ln.startswith('#'):
        p = ln.split(';'); ENR[p[1]] = p[5]
P = json.load(open('public/hs_public.json', encoding='utf-8'))
NAME = {'TN': 'Central Magnet School', 'IN': 'Signature School', 'PA': 'Julia R. Masterman Secondary School', 'NV': 'Davidson Academy', 'DC': 'School Without Walls High School',
        'VA': 'Thomas Jefferson High School for Science and Technology', 'GA': 'Gwinnett School of Mathematics, Science and Technology', 'TX': 'The School for the Talented and Gifted (TAG)',
        'WA': 'Nikola Tesla Stem High School', 'CA': 'Science Academy Stem Magnet'}
def sch(st): return next(s for s in P if s['state'] == st)
def fig(st, idx, must):
    """The one 2023-24 (or class of 2024) figure whose name contains `must`; extras for other years are skipped. idx is kept only as a hint."""
    c = [f for f in sch(st)['state_figures'] if must.lower() in f['figure'].lower() and 'extra' not in f['figure'].lower()
         and (not str(f.get('year', '')).startswith(('2024-25', 'class of 2025')) or 'class of 2024' in f['figure'])]
    assert len(c) == 1, (st, must, [f['figure'][:60] for f in c])
    return c[0]
def first_num(v):
    m = re.search(r'-?\d+(?:\.\d+)?', str(v)); return m.group(0) if m else None
def pct_of_share(v):   # 0.9706 -> 97.06
    x = Decimal(first_num(v)) * 100
    return format(x.quantize(Decimal('0.0001')), 'f').rstrip('0').rstrip('.')
def counts(v):
    m = re.search(r'(\d+) of (\d+)', str(v)) or re.search(r'Grads (\d+), Cohort (\d+)', str(v)) or re.search(r'graduates (\d+)\)?.*?cohort (\d+)', str(v), re.I)
    if not m: m2 = re.search(r'cohort (\d+), graduates (\d+)', str(v)); return f' ({m2.group(2)} of {m2.group(1)})' if m2 else ''
    return f' ({m.group(1)} of {m.group(2)})'
def ccd(st, figure, year):
    for f in sch(st)['nces_ccd']:
        if f['figure'] == figure and f['year'] == year: return f['value']
    return None
SRC = lambda st, f: f.get('source_url', '') + (' (' + str(f.get('file')) + ')' if f.get('file') else '')

# state assessment, 2023-24 (US News names 2023-2024 state assessment data); (state, field) -> (index, must contain, how)
HSMAP = {
 ('TN', 'read'): (4, 'TNReady ELA,', 'raw'), ('TN', 'sci'): (10, 'TNReady Science,', 'raw'), ('TN', 'grad'): (20, 'class of 2024', 'raw'),
 ('IN', 'read'): (0, "EBRW 'At Benchmark' % (state", 'share'), ('IN', 'math'): (1, "Math 'At Benchmark' %, all", 'share'), ('IN', 'sci'): (3, "ILEARN Biology, 'Total", 'share'), ('IN', 'grad'): (8, 'class of 2024', 'share'),
 ('PA', 'math'): (0, '2023-24 Keystone Algebra I', 'raw'), ('PA', 'read'): (2, '2023-24 Keystone Literature', 'raw'), ('PA', 'sci'): (4, '2023-24 Keystone Biology', 'raw'), ('PA', 'grad'): (6, 'class of 2024', 'share'),
 ('NV', 'math'): (0, '2023-24 Mathematics', 'raw'), ('NV', 'read'): (1, '2023-24 Reading', 'raw'), ('NV', 'grad'): (3, '2023-24 Four-year', 'raw_year_unresolved'),
 ('DC', 'read'): (1, 'ELA, all students, %', 'raw'), ('DC', 'sci'): (7, 'Science, all students', 'raw'), ('DC', 'grad'): (11, 'class of 2024', 'bin'),
 ('VA', 'read'): (0, 'English Reading', 'passed'), ('VA', 'math'): (2, 'Mathematics (SOL, all math', 'passed'), ('VA', 'sci'): (6, 'Science (SOL', 'passed'), ('VA', 'grad'): (8, 'On-Time Graduation', 'raw_year_unresolved'),
 ('GA', 'read'): (2, 'EOC American Literature', 'ga'), ('GA', 'sci'): (3, 'EOC Biology', 'ga'), ('GA', 'grad'): (8, 'Four-year adjusted cohort graduation rate, All Students', 'raw'),
 ('TX', 'read'): (0, 'STAAR EOC English I,', 'tx2'), ('TX', 'sci'): (4, 'STAAR EOC Biology', 'tx'), ('TX', 'grad'): (10, 'class of 2024', 'raw'),
 ('WA', 'math'): (0, 'grade 10 mathematics', 'share'), ('WA', 'read'): (1, 'grade 10 ELA', 'supp'), ('WA', 'sci'): (2, 'grade 11 science', 'share'), ('WA', 'grad'): (6, 'class of 2024', 'bin'),
 ('CA', 'read'): (0, 'grade 11 ELA', 'raw'), ('CA', 'math'): (1, 'grade 11 mathematics', 'raw'), ('CA', 'sci'): (2, 'CAST', 'raw'), ('CA', 'grad'): (6, 'class of 2024', 'raw'),
}
LABEL = {'grad': 'Graduation rate', 'math': 'Mathematics proficiency', 'read': 'Reading proficiency', 'sci': 'Science proficiency'}
for st, name in NAME.items():
    u = HSU[name]
    for k in ('grad', 'math', 'read', 'sci'):
        usn = u.get(k)
        uy = 'class of 2024' if k == 'grad' else '2023-24'
        if (st, k) not in HSMAP:
            if usn: add('hs', name, LABEL[k], usn, uy, None, None, '', 'No public counterpart was mapped.')
            continue
        idx, must, how = HSMAP[(st, k)]; f = fig(st, idx, must); v = f['value']; note = ''
        py = uy
        if how == 'raw': pub = str(v).split(' ')[0].rstrip(';')
        elif how == 'share': pub = pct_of_share(v); note = f'Published as a share of 1{counts(v)}, shown here as a percent.'
        elif how == 'bin': m = re.search(r"[>≥]\s*[\d.]+%?", str(v)); pub = m.group(0).replace('%', '') if m else str(v)
        elif how == 'passed': pub = re.search(r'Passed (\d+)', str(v)).group(1); note = 'Virginia publishes a pass rate (Advanced plus Proficient).'
        elif how == 'raw_year_unresolved': pub = str(v).split(' ')[0]; py = 'labelled ' + str(f.get('year')).split(' ')[0]; note = 'The state page does not say which graduating class the figure is for.'
        elif how == 'ga':
            t, pr, di = (int(re.search(fr'{x}=(\d+)', str(v)).group(1)) for x in ('tested', 'Proficient_cnt', 'Distinguished_cnt'))
            pub = str((Decimal(pr + di) * 100 / Decimal(t)).quantize(Decimal('0.0001'))); note = f'Proficient {pr} plus Distinguished {di} of {t} tested (Georgia Milestones counts).'
        elif how in ('tx', 'tx2'):
            a = re.search(r'Approaches=(\d+)', str(v)).group(1); m_ = re.search(r'Meets=(\d+)', str(v)).group(1)
            if how == 'tx2':
                f2 = fig(st, 1, 'STAAR EOC English II'); a2 = re.search(r'Approaches=(\d+)', str(f2['value'])).group(1); m2 = re.search(r'Meets=(\d+)', str(f2['value'])).group(1)
                pub = a if (a == m_ == a2 == m2) else None; note = f'English I and English II: Approaches {a} and {a2}, Meets {m_} and {m2}.'
            else:
                pub = a if a == m_ else None; note = f'Approaches {a}, Meets {m_}.'
        elif how == 'supp': pub = '*'; note = 'The state does not publish this figure for the school.'
        add('hs', name, LABEL[k], usn, uy, pub, py, SRC(st, f), note)
    # enrollment 9 to 12 and lunch shares, 2024-25 CCD (US News: profile data pertain to 2024-2025)
    g = [ccd(st, f'CCD enrollment grade {n}', '2024-25') for n in (9, 10, 11, 12)]
    if all(isinstance(x, int) and x >= 0 for x in g):
        add('hs', name, 'Enrollment, grades 9 to 12', ENR[name], '2024-25', str(sum(g)), '2024-25', 'NCES CCD via educationdata.urban.org', f'Grades 9, 10, 11, 12: {", ".join(map(str, g))}.')
    tot = ccd(st, 'CCD enrollment', '2024-25')
    for k, figname, lab in (('free', 'CCD free_lunch', 'Free lunch share'), ('red', 'CCD reduced_price_lunch', 'Reduced-price lunch share'), ('ed', 'CCD free_or_reduced_price_lunch', 'Economically disadvantaged share (free or reduced-price lunch)')):
        usn = u.get(k); c = ccd(st, figname, '2024-25')
        if c is None or (isinstance(c, int) and c < 0):
            add('hs', name, lab, usn, '2024-25', None, '2024-25', 'NCES CCD via educationdata.urban.org', 'CCD reports this count as missing.'); continue
        pub = str((Decimal(c) * 100 / Decimal(tot)).quantize(Decimal('0.0001')))   # rounded once, by the rule, to US News's precision
        add('hs', name, lab, usn, '2024-25', pub, '2024-25', 'NCES CCD via educationdata.urban.org', f'{c} of {tot} enrolled.')

# ---------- Law ----------
L = json.load(open('public/law/law_public.json', encoding='utf-8'))
LAWU = {}
for ln in open('raw/law_pages_20261110.txt', encoding='utf-8'):
    m = re.match(r'([a-z0-9-]+): (.+)$', ln.strip())
    if m and ' | ' in m.group(2): LAWU[m.group(1)] = [x.strip() for x in m.group(2).split(' | ')]
LAWNAME = {'stanford-university-03014': 'Stanford', 'university-of-chicago-03052': 'Chicago', 'yale-university-03027': 'Yale', 'university-of-pennsylvania-03140': 'Pennsylvania',
           'university-of-virginia-main-campus-03162': 'Virginia', 'harvard-university-03074': 'Harvard', 'duke-university-03117': 'Duke', 'new-york-university-03110': 'New York University',
           'columbia-university-03104': 'Columbia', 'northwestern-university-03050': 'Northwestern', 'university-of-michigan-ann-arbor-03082': 'Michigan'}
def xl(path, pat):
    o = subprocess.run([sys.executable, '-I', 'scripts_law/xlsx_dump.py', path, pat], capture_output=True, text=True).stdout
    return [l for l in o.splitlines() if not l.startswith('==') and ' A=School' not in l]
LKEY = {'stanford-university-03014': 'stanford', 'university-of-chicago-03052': 'chicago', 'yale-university-03027': 'yale', 'university-of-pennsylvania-03140': 'penn',
        'university-of-virginia-main-campus-03162': 'uva', 'harvard-university-03074': 'harvard', 'duke-university-03117': 'duke', 'new-york-university-03110': 'nyu',
        'columbia-university-03104': 'columbia', 'northwestern-university-03050': 'northwestern', 'university-of-michigan-ann-arbor-03082': 'michigan'}
U21 = {}   # ABA Two-Year Ultimate Bar Passage, report 2024 = 2021 graduates (same ABA backend file family, downloaded by the law pull)
for l in xl('public/law/downloads/bar_2024_Two-Year_Ultimate_Bar_Passage.xlsx', '.'):
    m = re.match(r'\d+ A=(.+?) \| B=.*\| E=([\d.]+)%', l)
    if m: U21[m.group(1)] = m.group(2)
for slug, (gpa, lsat, acc, ft, ult) in LAWU.items():
    s = L['schools'][LKEY[slug]]; F = s['figures']; nm = s['name']
    src509 = 'ABA Standard 509, 2025 (' + F['median_ugpa_all']['file'] + ')'
    add('law', nm, 'Median undergraduate GPA', gpa, '2025 entrants', F['median_ugpa_all']['value'], '2025 entrants', src509)
    add('law', nm, 'Median LSAT', lsat, '2025 entrants', F['median_lsat_all']['value'], '2025 entrants', src509)
    add('law', nm, 'Acceptance rate', acc, '2025 entrants', F['acceptance_rate_aba_pct']['value'], '2025 entrants', src509,
        f"ABA acceptance rate, {F['offers']['value']} offers of {F['applications']['value']} applications.")
    f23 = F['first_time_grads_2023']['school_pass_pct']['value'].rstrip('%'); f24 = F['first_time_grads_2024']['school_pass_pct']['value'].rstrip('%')
    avg = (Decimal(f23) + Decimal(f24)) / 2
    oc24 = compare(ft, f24, 'x', 'x')[0]; ocav = compare(ft, str(avg), 'x', 'x')[0]
    add('law', nm, 'First-time bar passage', ft, None, f24, '2024 graduates', 'ABA First-Time Bar Passage, reports 2024 and 2025',
        f"The school page prints no year for this figure. US News's method names a two-year nonweighted average of the 2023 and 2024 graduating classes for its first-time bar indicator. ABA: 2023 graduates {f23}, 2024 graduates {f24}, average {avg.quantize(Decimal('0.01'))}. The printed figure agrees with the 2024 graduates' rate after rounding: {'yes' if oc24 == 'MATCH' else 'no'}. With the two-year average: {'yes' if ocav == 'MATCH' else 'no'}. Shown after the data, not scored.")
    u21 = U21[s['aba_name']]; u22 = F['ultimate_2022_graduates']['pass_pct']['value'].rstrip('%')
    uav = ((Decimal(u21) + Decimal(u22)) / 2)
    add('law', nm, 'Ultimate bar passage, two-year average', ult, '2021 and 2022 graduates', str(uav), '2021 and 2022 graduates',
        'ABA Two-Year Ultimate Bar Passage, reports 2024 and 2025', f'US News method: a two-year nonweighted average of 2021 and 2022 graduates. ABA: 2021 graduates {u21}, 2022 graduates {u22}, average {uav.quantize(Decimal("0.001"))}.')
# ---------- Colleges ----------
C = json.load(open('public/college/college_public.json', encoding='utf-8'))
CKEY = {'massachusetts-institute-of-technology-2178': 'mit', 'princeton-university-2627': 'princeton', 'harvard-university-2155': 'harvard', 'yale-university-1426': 'yale',
        'california-institute-of-technology-1131': 'caltech', 'stanford-university-1305': 'stanford', 'university-of-pennsylvania-3378': 'penn', 'duke-university-2920': 'duke',
        'jhu-2077': 'jhu', 'northwestern-university-1739': 'northwestern', 'university-of-chicago-1774': 'uchicago', 'williams-college-2229': 'williams', 'amherst-college-2115': 'amherst',
        'bowdoin-college-2038': 'bowdoin', 'claremont-mckenna-college-1170': 'cmc', 'pomona-college-1173': 'pomona', 'swarthmore-college-3370': 'swarthmore',
        'united-states-naval-academy-2101': 'usna', 'harvey-mudd-college-1171': 'harveymudd', 'west-point-2893': 'usma', 'wellesley-college-2224': 'wellesley'}
CU = {}
for f, cols in (('raw/college_pages_20261110.txt', ['enr', 'acc', 'sat', 'act', 'ratio_first']), ('raw/college_pages2_20261110.txt', ['grad4', 'ratio', 'small'])):
    for ln in open(f, encoding='utf-8'):
        m = re.match(r'([a-z0-9-]+-\d+): (.+)$', ln.strip())
        if m and m.group(1) in CKEY:
            CU.setdefault(m.group(1), {}).update(dict(zip(cols, [x.strip().split(' ')[0] for x in m.group(2).split(' | ')])))
def cds_gap(key):
    r = ' '.join(map(str, (C[key].get('cds') or {}).get('refusals') or []))
    if 'box' in r.lower(): why = 'the college posts it as a file that needs a sign-in'
    elif re.search(r'40[35]|captcha|bot check|Cloudflare', r, re.I): why = 'the college page refused our reader'
    elif 'tableau' in r.lower(): why = 'the college posts it as an interactive dashboard only'
    else: why = 'no 2025-26 edition was found'
    return f'No Common Data Set 2025-26 was read for this college: {why}.'
def cds25(key):
    c = C.get(key, {}).get('cds') or {}
    y = (c.get('years') or {}).get('2025-2026') or {}
    return y if y.get('exists') else None
for slug, u in CU.items():
    key = CKEY[slug]
    if key not in C: raise KeyError(key)
    nm = C[key]['college']; y = cds25(key); src = (y or {}).get('source_url', '')
    lst = 'nu' if slug in list(CKEY)[:11] else 'nlac'
    b1 = str(y['B1_total_undergrad']['value']) if y and isinstance(y.get('B1_total_undergrad'), dict) else None
    add(lst, nm, 'Undergraduate enrollment', u['enr'], 'fall 2025', b1, 'fall 2025' if b1 else None, 'Common Data Set 2025-26, item B1 ' + src,
        '' if b1 else cds_gap(key))
    # the other printed figures carry no year on the US News page: scored CANNOT_TELL (year), with the CDS 2025-26 reading shown beside them
    disp = []
    if y:
        c1 = y.get('C1') or {}; c9 = y.get('C9') or {}; i3 = y.get('I3') or {}; bg = y.get('B_grad') or {}
        def fmt(v):
            return v if not re.match(r'^\d+\.\d{3,}$', v) else str(Decimal(v).quantize(Decimal('0.1')))
        def chk(lab, usn, pub):
            if usn in (None, '', '?') or pub in (None, ''): disp.append(f'{lab}: not compared'); return
            disp.append(f'{lab} {usn}, Common Data Set {fmt(pub)}, equal after rounding ' + ('yes' if compare(usn, pub, 'x', 'x')[0] == 'MATCH' else 'no'))
        if c1.get('applicants') and c1.get('admits'): chk('acceptance rate', u.get('acc'), str(Decimal(c1['admits']) * 100 / Decimal(c1['applicants'])))
        if c9.get('SAT_comp_25'): chk('SAT', u.get('sat'), f"{c9['SAT_comp_25']}-{c9['SAT_comp_75']}")
        if c9.get('ACT_comp_25'): chk('ACT', u.get('act'), f"{c9['ACT_comp_25']}-{c9['ACT_comp_75']}")
        r = re.match(r'\s*([\d.]+)', str(y.get('I2_ratio') or ''))
        if r: chk('student/faculty ratio', u.get('ratio'), r.group(1) + ':1')
        if i3.get('total'): chk('classes under 20', u.get('small'), str(Decimal(i3['2-9'] + i3['10-19']) * 100 / Decimal(i3['total'])))
        if bg.get('B6_adj_cohort') and bg.get('B7_4yr'): chk('4-year graduation rate', u.get('grad4'), str(Decimal(bg['B7_4yr']) * 100 / Decimal(bg['B6_adj_cohort'])) )
    for lab, k in (('Acceptance rate', 'acc'), ('SAT range', 'sat'), ('ACT range', 'act'), ('Student/faculty ratio', 'ratio'), ('Classes with fewer than 20 students', 'small'), ('4-year graduation rate', 'grad4')):
        add(lst, nm, lab, u.get(k), None, 'see the Common Data Set note', None, 'Common Data Set 2025-26 ' + src, 'The US News page prints no year for this figure.', shown_pub='')
    OUT.append(dict(list=lst, school=nm, field='_display_cds2025', note=('; '.join(disp) if disp else ('Only item B1 could be read from the college posting' if b1 else 'No Common Data Set 2025-26 was read')), outcome='DISPLAY', reason='after the data, not scored'))

OUTLAW = [o for o in OUT if o['list'] == 'law']
json.dump(dict(read='2026-11-10', checks=OUT), open('data/checks.json', 'w'), indent=1, ensure_ascii=False)
from collections import Counter
print(Counter((o['list'], o['outcome'], o['reason']) for o in OUT))
