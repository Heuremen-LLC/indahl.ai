#!/usr/bin/env python3
"""RANK step one: build data/rank.json from the raw US News captures in raw/ (read 2026-11-10 in a signed-in browser session).
Every rank, name and place comes from a raw line. Weights are the method lines quoted in raw/*_method_*.txt, typed here once and checked
against the raw file text below (a weight not found in its raw file stops the build). Standard library only. Heuremen LLC."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
READ = '2026-11-10'

def rows_semis(path, start=None, stop=None):
    """Lines '#N;name;place;...' (optionally only between two '== url' headers)."""
    out, on = [], start is None
    for ln in open(path, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if ln.startswith('== '):
            on = start is not None and start in ln
            continue
        if not on or not ln.startswith('#'): continue
        p = ln.split(';')
        if '(next row' in ln: continue
        m = re.match(r'#(\d+)( \(tie\))?$', p[0]); rank = int(m.group(1)); tie = bool(m.group(2))
        if len(p) > 3 and p[3].endswith('(tie)'): tie = True
        out.append(dict(rank=rank, tie=tie, name=p[1], place=p[2] if len(p) > 2 else '', extra=p[3:]))
    return out

def tie_fix(rows):
    """A rank printed by more than one school is a tie, whatever the row label says."""
    from collections import Counter
    c = Counter(r['rank'] for r in rows)
    for r in rows: r['tie'] = c[r['rank']] > 1
    return rows

def check_weights(raw, weights):
    t = open(raw, encoding='utf-8').read()
    for label, w in weights:
        needle = f'{label} ({w}'
        if needle not in t and f'{label} (weighted {w}' not in t:
            sys.exit(f'weight not in raw capture {raw}: {needle!r}')

US = 'https://www.usnews.com'
L = []

# High schools
hs = rows_semis('raw/hs_national_20261110.txt')
for r in hs:
    grad, cr, enr, path = r['extra']
    r.update(grad=grad, college_readiness=cr, enrollment=enr, url=f'{US}/education/best-high-schools/{path}'); del r['extra']
W = [('College Readiness', '30%'), ('College Curriculum Breadth', '10%'), ('State Assessment Proficiency', '20%'), ('State Assessment Performance', '20%'), ('Underserved Student Performance', '10%'), ('Graduation Rate', '10%')]
check_weights('raw/hs_method_20261110.txt', W)
L.append(dict(key='hs', title='Best High Schools', scope='national', edition='2026-2027', list_url=f'{US}/education/best-high-schools/national-rankings',
              method_url=f'{US}/education/best-high-schools/articles/how-us-news-calculated-the-rankings', weights=W, rows=tie_fix(hs), raw='raw/hs_national_20261110.txt',
              data_years='US News states that state assessment data are from 2023-2024, AP and IB data are for 2023-2024 12th graders, and graduation rates are for 2024 (2023 or 2022 where 2024 was not available).',
              printed=['graduation rate', 'college readiness', 'enrollment, grades 9 to 12']))

# Elementary and middle: no national list
KW = [('Mathematics and reading proficiency', '50%'), ('Mathematics and reading performance', '50%')]
check_weights('raw/k8_method_20261110.txt', KW)
for key, title in (('elem', 'Best Elementary Schools'), ('middle', 'Best Middle Schools')):
    L.append(dict(key=key, title=title, scope='none', edition='2027', list_url=f'{US}/education/k12/' + ('elementary-school' if key == 'elem' else 'middle-school'),
                  method_url=f'{US}/education/k12/articles/how-us-news-calculated-the-rankings', weights=KW, rows=[], raw='raw/k8_method_20261110.txt',
                  quote='There is no national ranking', quote_more='rankings calculated at the state and district levels'))

# Colleges
for key, title, raw, url in (('nu', 'National Universities', 'raw/nu_20261110.txt', f'{US}/best-colleges/rankings/national-universities'),
                             ('nlac', 'National Liberal Arts Colleges', 'raw/nlac_20261110.txt', f'{US}/best-colleges/rankings/national-liberal-arts-colleges')):
    rows = rows_semis(raw)
    for r in rows:
        r['enrollment'] = r['extra'][1] if len(r['extra']) > 1 else ''; del r['extra']
    if key == 'nu':   # the tie at No. 9 continues past the first page of the list (raw/grad_20261110.txt, Load More)
        assert 'University of Chicago' in open('raw/grad_20261110.txt').read()
        cp = open('raw/college_pages_20261110.txt').read(); m = re.search(r'university-of-chicago-1774: ([\d,]+) \|', cp)
        rows.append(dict(rank=9, tie=True, name='University of Chicago', place='Chicago, IL', enrollment=m.group(1) + ' (fall 2025)'))
    CW = [('Student outcomes', '52%'), ('Peer assessment', '20%'), ('Faculty resources', '11%' if key == 'nu' else '15%'), ('Financial resources', '8%'), ('Standardized tests', '5%')] + ([('Faculty research', '4%')] if key == 'nu' else [])
    check_weights('raw/colleges_method_20261110.txt', [w if w[0] != 'Faculty resources' else ('Faculty resources', '11-15%') for w in CW])
    L.append(dict(key=key, title=f'Best Colleges, {title}', scope='national', edition='2027', list_url=url, method_url=f'{US}/education/best-colleges/articles/how-us-news-calculated-the-rankings',
                  weights=CW, rows=tie_fix(rows), raw=raw, printed=['undergraduate enrollment, fall 2025'],
                  weights_note=('US News states faculty resources as 11 to 15 percent: student-faculty ratio 3, full-time faculty 2 and faculty salaries 6 for National Universities, and 4, 3 and 8 for other categories. Faculty research is counted for National Universities only.' if key == 'nu' else 'US News states faculty resources as 11 to 15 percent: student-faculty ratio 4, full-time faculty 3 and faculty salaries 8 outside National Universities.')))

# Graduate schools
G = 'raw/grad_20261110.txt'
grad_lists = [
    ('mba', 'Best Business Schools (full-time MBA)', '/best-graduate-schools/top-business-schools/mba-rankings', 'business-schools-methodology',
     [('Attainment success', '50%'), ('Quality assessment', '25%'), ('Student selectivity', '25%')]),
    ('law', 'Best Law Schools', '/best-graduate-schools/top-law-schools/law-rankings', 'law-schools-methodology',
     [('Placement success and bar passage', '58%'), ('Quality assessment', '25%'), ('Selectivity', '10%'), ('Faculty and library resources', '7%')]),
    ('eng', 'Best Engineering Schools', '/best-graduate-schools/top-engineering-schools/eng-rankings', 'engineering-schools-methodology',
     [('Research activity', '50%'), ('Quality assessment', '25%'), ('Faculty resources', '20%'), ('Student selectivity', '5%')]),
    ('edu', 'Best Education Schools', '/best-graduate-schools/top-education-schools/edu-rankings', 'education-schools-methodology',
     [('Research activity', '50%'), ('Quality assessment', '25%'), ('Faculty resources', '20%'), ('Student selectivity', '5%')]),
]
for key, title, path, meth, W in grad_lists:
    rows = rows_semis(G, start=path)
    check_weights('raw/grad_method_20261110.txt', W)
    L.append(dict(key=key, title=title, scope='national', edition='2026', list_url=US + path, method_url=f'{US}/education/best-graduate-schools/articles/{meth}', weights=W, rows=tie_fix(rows), raw=G))
# Medicine: tiers
txt = open(G, encoding='utf-8').read()
tier1 = [s.strip() for s in txt.split('Tier 1 in page order:\n', 1)[1].split('\n', 1)[0].split(';')]
medplaces = dict(x.split('=') for x in txt.split('MEDPLACES: ', 1)[1].split('\n', 1)[0].split(';'))
MW = [('Research Activity', '60%'), ('Faculty resources', '20% in research')]
check_weights('raw/grad_method_20261110.txt', MW)
MW2 = [('Research activity', '60%'), ('Median MCAT score', '13%'), ('Median undergraduate GPA', '5%'), ('Acceptance rate', '2%'), ('Faculty resources', '20%')]
check_weights('raw/grad_method_20261110.txt', [('Median MCAT score', '13% in research'), ('Median undergraduate GPA', '5% in research'), ('Acceptance rate', '2% in research')])
L.append(dict(key='med', title='Best Medical Schools (Research)', scope='tiers', edition='2026', list_url=US + '/best-graduate-schools/top-medical-schools/research-rankings',
              method_url=f'{US}/education/best-graduate-schools/articles/medical-schools-methodology', weights=MW2,
              rows=[dict(rank=None, tie=False, name=n, place=medplaces[n]) for n in tier1], raw=G, quote='U.S. News uses evaluative tiers instead of traditional ordinal rankings', tier_def='Tier 1: Highest-performing (85th-99th percentile)'))

for l in L:
    for r in l['rows']:
        r['check'] = 'check in progress'
        r['slug'] = l['key'] + '-' + re.sub(r'[^a-z0-9]+', '-', r['name'].lower()).strip('-')
os.makedirs('data', exist_ok=True)
json.dump(dict(read=READ, step='listing', lists=L), open('data/rank.json', 'w'), indent=1, ensure_ascii=False)
print('lists', len(L), 'rows', sum(len(l['rows']) for l in L), {l['key']: len(l['rows']) for l in L})
