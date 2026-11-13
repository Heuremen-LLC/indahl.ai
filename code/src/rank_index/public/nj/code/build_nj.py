"""Build nj_public.json from the extracted CSVs (made by xlsx_stream.py).
usage: python3 -I build_nj.py <nj_dir>
Every record = one published row, all cells as published, keyed by the state's own column headers,
with provenance (source URL, file, sheet, xlsx row, date read). No figures are computed here except
in the clearly-labelled 'summary' block, which only copies published cells.
"""
import sys, os, csv, json, re, glob

NJ = sys.argv[1]
FILES = os.path.join(NJ, 'files')
DATE_READ = {'spr': '2026-11-10', 'assess': '2026-11-10', 'nces': '2026-11-10'}
SPR_URL = 'https://www.nj.gov/education/sprreports/download/DataFiles/{y}/Database_SchoolDetail.xlsx'
KEEP_YEARS = {'2023-24', '2024-25'}

keys = [l.strip() for l in open(os.path.join(NJ, 'code', 'keys.txt')) if l.strip()]


def norm(v, w):
    v = (v or '').strip()
    if v.endswith('.0'):
        v = v[:-2]
    return v.zfill(w) if v.isdigit() else v


def year_norm(v):
    v = (v or '').strip()
    m = re.match(r'^(20\d\d)-(20)?(\d\d)$', v)
    if m:
        return f'{m.group(1)}-{m.group(3)}'
    return v


def assess_urls():
    out = {}
    for y in ('2324', '2425'):
        html = open(os.path.join(FILES, f'assess_{y}', '_index_page.html'), errors='replace').read()
        for p in re.findall(r'href="(/education/assessment/results/reports/%s/[^"]+\.xlsx)"' % y, html):
            fn = os.path.basename(p).replace('%20', '_')
            out[(y, fn)] = 'https://www.nj.gov' + p
    return out


def read_sheet(path):
    rows = list(csv.reader(open(path, newline='')))
    hdr_i = None
    for i, r in enumerate(rows):
        if any(re.fullmatch(r'county[ _]?code', (c or '').strip(), re.I) for c in r[1:3]):
            hdr_i = i
            break
    if hdr_i is None:
        return None, [], []
    header = [re.sub(r'\s+', ' ', h).strip() for h in rows[hdr_i][1:]]
    data, notes = [], []
    for r in rows[hdr_i + 1:]:
        cells = r[1:]
        if not any(c.strip() for c in cells):
            continue
        c0 = norm(cells[0], 2)
        if len(cells) >= 5 and len(c0) == 2 and c0.isdigit():
            k = '|'.join([c0, norm(cells[2], 4), norm(cells[4], 3)])
            if k in keys:
                data.append((int(r[0]), k, cells))
        elif c0 not in ('State',) and cells[0].strip() not in ('end of worksheet',) and not cells[0].strip().startswith('State'):
            txt = ' '.join(c for c in cells if c.strip())
            if txt and not re.match(r'^(State|end of worksheet)', txt):
                notes.append(re.sub(r'\s+', ' ', txt))
    # also keep pre-header notes (titles, suppression notes)
    pre = [re.sub(r'\s+', ' ', ' '.join(c for c in r[1:] if c.strip())) for r in rows[:hdr_i]]
    return header, data, [p for p in pre if p] + notes


schools = {k: {'nj_codes': dict(zip(('county_code', 'district_code', 'school_code'), k.split('|'))),
               'records': []} for k in keys}
sheet_notes = {}


def add(path, src_url, file_label, sheet, default_year, fam):
    header, data, notes = read_sheet(path)
    if header is None:
        return
    sheet_notes[f'{file_label} :: {sheet}'] = notes
    yi = None
    for i, h in enumerate(header):
        if h.lower().replace(' ', '') == 'schoolyear':
            yi = i
    for rnum, k, cells in data:
        yr = year_norm(cells[yi]) if yi is not None and yi < len(cells) else default_year
        if yr not in KEEP_YEARS:
            continue
        rec = {h: (cells[i] if i < len(cells) else '') for i, h in enumerate(header) if h}
        has_supp = any(v.strip() in ('*', 'N') or v.strip().startswith(('<', '>', '≤')) or 'Fewer' in v for v in rec.values())
        schools[k]['records'].append({
            'family': fam, 'school_year': yr, 'source_url': src_url, 'file': file_label,
            'sheet': sheet, 'row': rnum, 'date_read': DATE_READ[fam.split(':')[0]],
            'suppression_note': 'row contains suppression/range markers as published (*, N, <, >, ≤, "Fewer then 10 ...")' if has_supp else '',
            'values': rec})
        if 'name' not in schools[k]:
            schools[k]['name'] = cells[5]
            schools[k]['district'] = cells[3]


# SPR databases
for y, d, label in (('2023-24', 'extract_2324', '2023-2024'), ('2024-25', 'extract_2425', '2024-2025')):
    for p in sorted(glob.glob(os.path.join(FILES, d, '*.csv'))):
        sh = os.path.basename(p)[:-4]
        add(p, SPR_URL.format(y=label), f'Database_SchoolDetail.xlsx ({label})', sh, y, 'spr')

# Assessment results files
au = assess_urls()
for yy, y in (('2324', '2023-24'), ('2425', '2024-25')):
    for d in sorted(glob.glob(os.path.join(FILES, f'assess_extract_{yy}', '*'))):
        fn = os.path.basename(d) + '.xlsx'
        url = au.get((yy, fn), '')
        for p in sorted(glob.glob(os.path.join(d, '*.csv'))):
            sh = os.path.basename(p)[:-4]
            add(p, url, fn, sh, y, 'assess')

# NCES CCD via Urban Institute Education Data API
ND = os.path.join(FILES, 'nces_urban_20261110')
GR = ['pk', 'k'] + [str(i) for i in range(1, 14)] + ['99']
for apiy, y in ((2023, '2023-24'), (2024, '2024-25')):
    dr = {r['seasch']: r for r in json.load(open(os.path.join(ND, f'dir_{apiy}.json')))['results']}
    enr = {}
    for g in GR:
        for r in json.load(open(os.path.join(ND, f'enr_{apiy}_g{g}.json')))['results']:
            if r.get('race') == 99 and r.get('sex') == 99:
                enr.setdefault(r['ncessch'], {})[g] = r['enrollment']
    for k in keys:
        c, dd, s = k.split('|')
        r = dr.get(f'{c}{dd}-{s}')
        if not r:
            continue
        vals = {f: r.get(f) for f in ('ncessch', 'school_name', 'seasch', 'lea_name', 'enrollment', 'free_lunch',
                                       'reduced_price_lunch', 'free_or_reduced_price_lunch', 'direct_certification',
                                       'lunch_program', 'lowest_grade_offered', 'highest_grade_offered', 'charter', 'magnet')}
        schools[k]['nces_id'] = r['ncessch']
        schools[k]['records'].append({
            'family': 'nces', 'school_year': y,
            'source_url': f'https://educationdata.urban.org/api/v1/schools/ccd/directory/{apiy}/?fips=34&per_page=10000',
            'file': f'dir_{apiy}.json', 'sheet': 'results', 'row': f'seasch={r["seasch"]}',
            'date_read': DATE_READ['nces'],
            'suppression_note': 'Urban API codes: -1 missing/not reported, -2 not applicable, -3 suppressed',
            'values': vals})
        schools[k]['records'].append({
            'family': 'nces', 'school_year': y,
            'source_url': f'https://educationdata.urban.org/api/v1/schools/ccd/enrollment/{apiy}/grade-<g>/?fips=34&per_page=10000 (g in pk,k,1..13,99)',
            'file': f'enr_{apiy}_g<g>.json', 'sheet': 'results', 'row': f'ncessch={r["ncessch"]}, race=99, sex=99',
            'date_read': DATE_READ['nces'],
            'suppression_note': 'grade 13 = ungraded/adult per Urban codebook; 99 = total; -1 missing, -2 n/a, -3 suppressed',
            'values': {('grade_' + g): enr.get(r['ncessch'], {}).get(g) for g in GR}})


# ---------- summary (copies of published cells only) ----------
def recs(k, sheet=None, year=None, file_sub=None, **match):
    out = []
    for r in schools[k]['records']:
        if sheet and r['sheet'] != sheet:
            continue
        if year and r['school_year'] != year:
            continue
        if file_sub and file_sub not in r['file']:
            continue
        if all(r['values'].get(a) == b for a, b in match.items()):
            out.append(r)
    return out


def cite(r):
    return f"{r['file']} / {r['sheet']} / row {r['row']}"


for k, S in schools.items():
    sm = {}
    # ELA/Math school-wide
    for subj, sh24, sh25 in (('ELA', 'ELAParticipationPerformance', 'ELAParticipationPerformance'),
                              ('Math', 'MathParticipationPerformance', 'MathParticipationPerformance')):
        for r in recs(k, sh24, '2023-24', '2023-2024', **{'Student Groups': 'Schoolwide'}):
            v = r['values']
            sm[f'{subj} 2023-24'] = {'met_or_exceeded_pct': v.get('School: % of testers met/exceeded expecations') or v.get('School: % of testers met/exceeded expectations'),
                                     'valid_scores': v.get('Valid Scores'), 'pct_students_taking_test': v.get('% of Students taking test'), 'cite': cite(r)}
        for r in recs(k, sh25, '2024-25', '2024-2025', StudentGroup='All Students'):
            v = r['values']
            sm[f'{subj} 2024-25'] = {'met_or_exceeded_pct': v.get('MetExceededExpectations_School'), 'valid_scores': v.get('ValidScores_School'),
                                     'participation_rate': v.get('ParticipationRate_School'), 'cite': cite(r)}
    # Science
    for r in recs(k, 'ScienceAssessmentByGrade', '2023-24', '2023-2024', **{'Student Group': 'Schoolwide'}):
        v = r['values']
        sm.setdefault('Science 2023-24 by grade (levels 1-4 %)', []).append(
            {'grade': v.get('Grade'), 'L1': v.get('% Level 1'), 'L2': v.get('% Level 2'), 'L3': v.get('% Level 3'), 'L4': v.get('% Level 4'), 'cite': cite(r)})
    for r in recs(k, 'OverallNJSLAScience', None, '2024-2025', StudentGroup='All Students'):
        sm[f"Science {r['school_year']} percentage proficient"] = {'value': r['values'].get('PercentageProficient_School'), 'cite': cite(r)}
    # NJGPA
    for r in recs(k, 'NJGPA', '2023-24', '2023-2024', StudentGroup='Schoolwide'):
        v = r['values']
        sm['NJGPA 2023-24'] = {'ela_valid': v.get('ElaValidScores'), 'ela_grad_ready': v.get('School%Graduation: Ela'),
                               'math_valid': v.get('MathValidScores'), 'math_grad_ready': v.get('School%Graduation: Math'), 'cite': cite(r)}
    for r in recs(k, 'NJGPA', '2024-25', '2024-2025', StudentGroup='All Students'):
        v = r['values']
        sm['NJGPA 2024-25'] = {'ela_valid': v.get('ELAValidScores_School'), 'ela_grad_ready': v.get('ELAGraduationReadyPct_School'),
                               'math_valid': v.get('MathValidScores_School'), 'math_grad_ready': v.get('MathGraduationReadyPct_School'), 'cite': cite(r)}
    # Registered / not tested per test (assessment files, Total/All Students)
    for r in S['records']:
        if r['family'] == 'assess' and r['values'].get('Subgroup Type') == 'All Students' and 'Registered To Test' in r['values']:
            v = r['values']
            sm.setdefault(f"Registered/NotTested/Valid {r['school_year']}", []).append(
                {'test': r['sheet'], 'registered_to_test': v.get('Registered To Test'), 'not_tested': v.get('Not Tested ** (See Below)'),
                 'valid_scores': v.get('Valid Scores'), 'cite': cite(r)})
        if r['family'] == 'assess' and r['file'].startswith('DLM') and r['values'].get('Subgroup Type') == 'All Students':
            sm.setdefault(f"DLM valid scores {r['school_year']}", []).append(
                {'file': r['file'], 'grade': r['sheet'], 'valid_scores': r['values'].get('Valid Scores'), 'cite': cite(r)})
    for r in recs(k, 'AlternateAssessmentParticipatio', '2023-24'):
        v = r['values']
        sm.setdefault('SPR alternate assessment 2023-24', []).append({'grade': v.get('Grade'), 'ELAStudentsTested': v.get('ELAStudentsTested'),
                     'ELAStudentPercentage': v.get('ELAStudentPercentage'), 'MathStudentsTested': v.get('MathStudentsTested'),
                     'MathStudentPercentage': v.get('MathStudentPercentage'), 'cite': cite(r)})
    for r in recs(k, 'DLMTrends', None, '2024-2025'):
        v = r['values']
        sm.setdefault(f"SPR DLM {r['school_year']}", []).append({'grade': v.get('Grade'), 'ELAStudentsTested': v.get('ELAStudentsTested'),
                     'ELAParticipationRate': v.get('ELAParticipationRate'), 'MathStudentsTested': v.get('MathStudentsTested'),
                     'MathParticipationRate': v.get('MathParticipationRate'), 'cite': cite(r)})
    # Graduation
    for r in recs(k, 'FederalGraduationRates', '2023-24', '2023-2024', StudentGroup='Schoolwide'):
        v = r['values']
        sm['Graduation (2023-24 report)'] = {'2024 4-Year Federal Graduation Rate': v.get('2024 4-Year Federal Graduation Rate'),
                                             '2023 5-Year Federal Graduation Rate': v.get('2023 5-Year Federal Graduation Rate'), 'cite': cite(r)}
    for r in recs(k, 'GraduationRateTrendsProgress', '2023-24', '2023-2024'):
        v = r['values']
        sm.setdefault('Graduation trend (2023-24 report)', []).append({'cohort': v.get('CohortYear'), 'type': v.get('GraduationRateType'), 'rate': v.get('GraduationRate'), 'cite': cite(r)})
    for r in recs(k, 'FederalGraduationRates', '2024-25', '2024-2025', StudentGroup='All Students'):
        v = r['values']
        sm['Graduation (2024-25 report)'] = {'4YrCohort': v.get('4YrCohort'), '4YrGraduationRateFederal_School': v.get('4YrGraduationRateFederal_School'),
                                             '5YrCohort': v.get('5YrCohort'), '5YrGraduationRateFederal_School': v.get('5YrGraduationRateFederal_School'), 'cite': cite(r)}
    # Enrollment + econ dis
    for y, fl in (('2023-24', '2023-2024'), ('2024-25', '2024-2025')):
        for r in recs(k, 'EnrollmentTrendsbyGrade', y, fl):
            sm[f'Enrollment {y}'] = {'Total': r['values'].get('Total'), 'cite': cite(r)}
        for r in recs(k, 'EnrollmentTrendsByStudentGroup', y, fl):
            sm[f'Economically Disadvantaged Students {y}'] = {'value': r['values'].get('Economically Disadvantaged Students'), 'cite': cite(r)}
        for r in recs(k, 'SchoolDay', y, fl):
            v = r['values']
            sm[f'SchoolDay {y}'] = {'LengthOfDay': v.get('LengthOfDay'), 'InstructionFullTime': v.get('InstructionFullTime'),
                                    'InstructionSharedTime': v.get('InstructionSharedTime'), 'TypicalStartTime': v.get('TypicalStartTime'),
                                    'TypicalEndTime': v.get('TypicalEndTime'), 'cite': cite(r)}
        for r in S['records']:
            if r['family'] == 'nces' and r['school_year'] == y and 'enrollment' in r['values']:
                v = r['values']
                sm[f'NCES {y}'] = {'ncessch': v['ncessch'], 'enrollment': v['enrollment'], 'free_lunch': v['free_lunch'],
                                   'reduced_price_lunch': v['reduced_price_lunch'], 'cite': r['source_url']}
    S['summary'] = sm

out = {'generated': '2026-11-10', 'desk': 'RANK (indahl.ai)', 'scope': '26 NJ public schools, school years 2023-24 and 2024-25',
       'notes': 'Every record copies one published row with the state column headers. Summary copies published cells only. '
                'Suppression markers kept as published. No student-level data.',
       'sheet_notes': sheet_notes,
       'schools': [dict(key=k, **v) for k, v in schools.items()]}
json.dump(out, open(os.path.join(NJ, 'nj_public.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('schools', len(schools), 'records', sum(len(v['records']) for v in schools.values()))
for k, v in schools.items():
    print(k, v.get('name'), len(v['records']), v.get('nces_id'))
