#!/usr/bin/env python3
"""RANK Addendum 2 (sealed 04f16e5): graduate school checks. US News school pages as read 2026-11-10 (raw/grad_pages_20261110.txt, free tier)
against each school's own published reports and national files (public/grad/<list>/<list>_public.json, every value traced to a saved file).
Every comparison goes through rule.compare (the sealed rule). Each scored public value is picked by an explicit map below (PICK), naming
school, item and class or year. Paid-tier figures are one CANNOT_TELL (paid_tier) row per school and indicator, with the public figure shown.
Output: data/checks_grad.json. Standard library only. Heuremen LLC."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); sys.path.insert(0, HERE)
from rule import compare
U = json.loads(open('raw/grad_pages_20261110.txt', encoding='utf-8').read().split('JSON:\n', 1)[1])
for _k, _v in json.loads(open('raw/grad_pages_fix_20261110.txt', encoding='utf-8').read().split('JSON:\n', 1)[1]).items(): U[_k].update(_v)   # values under 100 re-read after the referee
R = json.load(open('data/rank.json', encoding='utf-8'))
ROWS = {l['key']: [r['name'] for r in l['rows']] for l in R['lists'] if l['key'] in ('mba', 'eng', 'edu', 'med')}
SLUG = {k: [s for s in U if s.startswith(k + '/')] for k in ROWS}   # same order as the list pages
NAME = {s: ROWS[k][i] for k in ROWS for i, s in enumerate(SLUG[k])}
OUT = []
def add(lst, school, field, usn, usn_year, pub, pub_year, source, note='', same=True, shown_pub=None, outcome=None, reason=None):
    oc, why = compare(usn, pub, usn_year, pub_year, same)
    if outcome: oc, why = outcome, reason or ''
    OUT.append(dict(list=lst, school=school, field=field, usn=usn, usn_year=usn_year, pub=shown_pub if shown_pub is not None else pub,
                    pub_year=pub_year, source=source, note=note.replace(';', ','), outcome=oc, reason=why))
from rule import decimals, rnd, _num
from decimal import Decimal
def J(lst): return json.load(open(f'public/grad/{lst}/{lst}_public.json', encoding='utf-8'))
PUB = {k: J(k) for k in ('mba', 'eng', 'edu', 'med')}
def rec(lst, school, item, year=None):
    """The one public record for this school, item (exact) and class or year (substring). Stops if none or more than one."""
    c = [x for x in PUB[lst] if x['school'].startswith(school) and x['item'] == item and (year is None or year in str(x.get('class_or_year') or x.get('year') or ''))]
    assert len(c) == 1, (lst, school, item, year, len(c))
    return c[0]
def src(r): return (r.get('url') or '') + (f" (public/grad/{r.get('file')})" if r.get('file') else '')
def cmp_coarse(usn, pub, uy, py, same=True):
    """rule.compare, plus: a public percent printed coarser than US News prints it cannot settle the US News figure.
    If US News, rounded to the public precision, equals the public figure: CANNOT_TELL (precision). Otherwise MISMATCH."""
    try:
        if same and uy == py and pub not in (None, '') and usn not in (None, '') and decimals(pub) < decimals(usn):
            return ('CANNOT_TELL', 'precision') if rnd(_num(usn), decimals(pub)) == _num(pub) else ('MISMATCH', '')
    except Exception: pass
    return compare(usn, pub, uy, py, same)
def score(lst, school, field, usn, uy, pub, py, source, note='', same=True, reason=None, shown=None):
    if reason:   # a reason fixed by the addendum (paid tier, definition, not found), named in the note
        oc, why = 'CANNOT_TELL', reason
    else:
        oc, why = cmp_coarse(usn.replace('$', '') if isinstance(usn, str) else usn, pub.replace('$', '') if isinstance(pub, str) else pub, uy, py, same)
    if shown is None and isinstance(pub, str) and pub.isdigit() and len(pub) >= 4: shown = f'{int(pub):,}'
    OUT.append(dict(list=lst, school=school, field=field, usn=usn, usn_year=uy, pub=shown if shown is not None else pub, pub_year=py, source=source,
                    note=note.replace(';', ','), outcome=oc, reason=why))
def display(lst, school, field, usn, pub, py, source, note=''):
    OUT.append(dict(list=lst, school=school, field=field, usn=usn, usn_year='', pub=pub, pub_year=py, source=source, note=note.replace(';', ','), outcome='DISPLAY', reason=''))
def pct(a, b, places=1): return format(rnd(Decimal(a) * 100 / Decimal(b), places), 'f')
def usd(s): return None if s in (None, 'N/A') else s.replace('$', '')
PAID = 'not shown without a paid subscription on the US News page'

# ---------------- MBA ----------------
FALL, C25 = 'fall 2025 entrants', 'class of 2025'
M = {  # school row name -> pulled public figures (record selectors). None = not published in the documents read.
 'Stanford University': dict(prefix='Stanford', apps=('applicants', '2027'), enrolled=('new students (class size)', '2027'),
     grad=('offers ACCEPTED, at graduation', '2025'), m3=('offers ACCEPTED, by 3 months', '2025'), sal=('base salary median / mean', '2025'), salpos=1,
     gmat=('GMAT (classic) average', '2027'), gpa=('undergraduate GPA average', '2027')),
 'University of Pennsylvania (Wharton)': dict(prefix='Wharton'),
 'University of Chicago (Booth)': dict(prefix='Chicago', apps=('applications', '2027'), enrolled=('class size', 'Class of 2027'), gmat=('GMAT (classic) average / median', '2027'), gpa=('undergraduate GPA average', 'Class of 2027')),
 'Harvard University': dict(prefix='Harvard', apps=('class size; applications', '2027'), enrolled=('class size; applications', '2027'), gmat=('GMAT 10th Edition median (Total)', '2027'), gpa=('undergraduate GPA average', '2027')),
 'Northwestern University (Kellogg)': dict(prefix='Kellogg', enrolled=('class size', '2027'), gmat=('GMAT Legacy average (middle 80%)', '2027'), gpa=('undergraduate GPA average', '2027')),
 'Massachusetts Institute of Technology (Sloan)': dict(prefix='MIT'),
 'Columbia University': dict(prefix='Columbia'),
 'New York University (Stern)': dict(prefix='NYU'),
 'Dartmouth College (Tuck)': dict(prefix='Tuck', enrolled=('class size', '2027'), gmat=('GMAT average (10th Edition); GPA average', '2027')),
 'University of California, Berkeley (Haas)': dict(prefix='Berkeley', enrolled=('students enrolled', None), gmat=('GMAT (classic) median (middle 80%)', None), gpa=('undergraduate GPA average (middle 80%)', None)),
}
def first_int(s, k=0):
    v = re.findall(r'\d[\d,]*', str(s)); return v[k].replace(',', '') if len(v) > k else None
def first_pct(s, k=0):
    v = re.findall(r'(\d+(?:\.\d+)?)%', str(s)); return v[k] if len(v) > k else None
for slug in SLUG['mba']:
    nm, u, m = NAME[slug], U[slug], M[NAME[slug]]; p = m['prefix']
    def R(key):
        sel = m.get(key); return rec('mba', p, sel[0], sel[1]) if sel else None
    # admissions: applicants, new entrants, acceptance rate
    r = R('apps')
    if r: score('mba', nm, 'Applicants, full-time', u['applicants_ft'], FALL, first_int(r['value'], 1 if 'applications' in r['item'] and 'class size' in r['item'] else 0), FALL, src(r), f"Class profile: {r['value']}.")
    else: score('mba', nm, 'Applicants, full-time', u['applicants_ft'], FALL, None, '', '', 'Not published in the class profile pages read.')
    r = R('enrolled')
    if r and p == 'Chicago':
        score('mba', nm, 'New entrants, full-time', u['enrolled_ft'], FALL, '635', FALL, src(r), 'Booth class profile, Class of 2027: 635 "Full-Time MBA Students" as the headline figure, 60 "Joint Degree Students" beside it, and percentages "calculated out of 695 students". US News prints 695. The headline 635 leaves out joint degree students.', reason='definition')
    elif r: score('mba', nm, 'New entrants, full-time', u['enrolled_ft'], FALL, first_int(r['value']), FALL, src(r), f"Class profile: {r['value']}.")
    else: score('mba', nm, 'New entrants, full-time', u['enrolled_ft'], FALL, None, '', '', 'The class profile page read shows a later class, or no profile for the class entering fall 2025 was found.')
    score('mba', nm, 'Acceptance rate, full-time', u['acceptance'], FALL, None, '', '', 'No admits count or acceptance rate for the class entering fall 2025 in the pages read.'
          + (f" US News's own counts give {pct(u['accepted_ft'].replace(',', ''), u['applicants_ft'].replace(',', ''))} percent ({u['accepted_ft']} of {u['applicants_ft']})." if u.get('accepted_ft') else ''))
OUT_MBA_ADM = len(OUT)
E = {  # employment, class of 2025: (record selector, how to read it). Percent of job seekers with an accepted offer.
 'Stanford University': dict(grad=('Stanford', 'offers ACCEPTED, at graduation', '2025', 'count'), m3=('Stanford', 'offers ACCEPTED, by 3 months', '2025', 'count'), sal=('Stanford', 'base salary median / mean', '2025', 1)),
 'Northwestern University (Kellogg)': dict(grad=('Kellogg', 'offers ACCEPTED at graduation / by 3 months', '2025', 0), m3=('Kellogg', 'offers ACCEPTED at graduation / by 3 months', '2025', 1), sal=('Kellogg', 'base salary median / mean', '2025', 1)),
 'Massachusetts Institute of Technology (Sloan)': dict(grad=('MIT', 'offers RECEIVED / ACCEPTED at graduation', 'Class of 2025', 1), m3=('MIT', 'offers RECEIVED / ACCEPTED, 3 months', 'Class of 2025', 1), sal=('MIT', 'base salary mean / median', 'Class of 2025', 0)),
 'New York University (Stern)': dict(grad=('NYU', 'offers RECEIVED / ACCEPTED at graduation', '2025', 1), m3=('NYU', 'offers RECEIVED / ACCEPTED, 3 months', '2025', 1), sal=('NYU', 'base salary average / median', 'Class of 2025', 0)),
 'University of California, Berkeley (Haas)': dict(grad=('Berkeley', 'offers ACCEPTED at graduation / by 3 months', '2025', 'count0'), m3=('Berkeley', 'offers ACCEPTED at graduation / by 3 months', '2025', 'count1'), sal=('Berkeley', 'base salary median / mean', '2025', 1)),
 'Dartmouth College (Tuck)': dict(m3=('Tuck', 'offers RECEIVED / ACCEPTED, 3 months', '2025', 'tuck')),
}
DEF = {  # figures published but not the same quantity, named in the note (reason definition)
 'University of Pennsylvania (Wharton)': dict(m3=(rec('mba', 'Wharton', 'offers RECEIVED / ACCEPTED (seeking students)', 'Class of 2025'), '87.0 (529 of 608 job seekers)', 'The report gives the share of job seekers reporting an accepted offer and does not say at what point after graduation.'),
     sal=(rec('mba', 'Wharton', 'base salary median', 'Class of 2025'), '185,000 (median)', 'The report gives a median base salary. US News prints an average.')),
 'University of Chicago (Booth)': dict(m3=(rec('mba', 'Chicago', 'offers RECEIVED within 3 months', 'Class of 2025'), '89.1 (offers received)', 'The school gives the share with offers received within three months, not offers accepted.'),
     sal=(rec('mba', 'Chicago', 'base salary median', 'Class of 2025'), '175,000 (median)', 'The school gives a median base salary. US News prints an average.')),
 'Harvard University': dict(m3=(dict(url='https://www.hbs.edu/recruiting/employment-data/Pages/default.aspx', file=None), '84 ("Accepted an Offer")', 'Read in a browser (raw/manual/grad/hbs_employment_20261110.txt). The page shows 90 percent of job seekers received an offer and, below that, 84 percent accepted an offer, as of three months, and does not say whether 84 percent is of job seekers or of those with an offer.'),
     sal=(dict(url='https://www.hbs.edu/recruiting/employment-data/Pages/default.aspx', file=None), '184,500 (median)', 'The page gives a median base salary. US News prints an average.')),
 'Columbia University': dict(m3=(dict(url='https://business.columbia.edu/recruiters/employment-report', file=None), '90 (acceptances, three months)', 'Read in a browser (raw/manual/grad/columbia_employment_20261110.txt). The school says its employment report includes sponsored students, and that what it sends to ranking publications follows the CSEA standards, which treat sponsored students apart.'),
     sal=(dict(url='https://business.columbia.edu/recruiters/employment-report', file=None), '175,000 (median)', 'The page gives a median base salary. US News prints an average.')),
 'Dartmouth College (Tuck)': dict(sal=(rec('mba', 'Tuck', 'base salary median', 'Class of 2025'), '175,000 (median)', 'The school gives a median base salary. US News prints an average.')),
}
def emp_value(sel):
    p, item, yr, how = sel; r = rec('mba', p, item, yr); v = r['value']
    if how == 'count':   # "144 of 268 (54%)"
        a, b = re.search(r'(\d+) of (\d+)', v).groups(); return pct(a, b, 4), f'{a} of {b} job seekers ({pct(a, b)} percent)', r
    if how in ('count0', 'count1'):   # "114 (62.6%) / 153 (84.1%) of 182"
        k = int(how[-1]); a = re.findall(r'(\d+) \(', v)[k]; b = re.search(r'of (\d+)', v).group(1); return pct(a, b, 4), f'{a} of {b} job seekers ({pct(a, b)} percent)', r
    if how == 'tuck':   # "242 (90%) / 233 (87%) of 268"
        a = re.findall(r'(\d+) \(', v)[1]; b = re.search(r'of (\d+)', v).group(1); return pct(a, b, 4), f'{a} of {b} job seekers ({pct(a, b)} percent), printed as 87%', r
    x = first_pct(v, how); return x, f'{x} percent as printed', r
for slug in SLUG['mba']:
    nm, u = NAME[slug], U[slug]; e_, d_ = E.get(nm, {}), DEF.get(nm, {})
    for key, field, usn in (('grad', 'Employed at graduation, share of job seekers', u['emp_grad']), ('m3', 'Employed three months after graduation, share of job seekers', u['emp_3m'])):
        if key in e_:
            v, shown, r = emp_value(e_[key]); score('mba', nm, field, usn, C25, v, C25, src(r), f'Employment report, class of 2025: {shown}.', shown=format(rnd(Decimal(v), 1), 'f'))
        elif key in d_:
            r, shown, why = d_[key]; score('mba', nm, field, usn, C25, shown, C25, src(r), why, reason='definition')
        else:
            score('mba', nm, field, usn, C25, None, '', '', 'Not published for the class of 2025 in the documents read.')
    if 'sal' in e_:
        p, item, yr, k = e_['sal']; r = rec('mba', p, item, yr); v = r['value'].split(' / ')[k].replace('$', '').replace(',', '')
        score('mba', nm, 'Average base salary', u['avg_base_salary'], C25, v, C25, src(r), f"Employment report, class of 2025, mean base salary {r['value'].split(' / ')[k]}.", shown=r['value'].split(' / ')[k])
    elif 'sal' in d_:
        r, shown, why = d_['sal']; score('mba', nm, 'Average base salary', u['avg_base_salary'], C25, shown, C25, src(r), why, reason='definition')
    else:
        score('mba', nm, 'Average base salary', u['avg_base_salary'], C25, None, '', '', 'Not published for the class of 2025 in the documents read.')
    # paid tier: median GMAT/GRE and median GPA of fall 2025 entrants
    m = M[nm]; p = m['prefix']
    for key, field in (('gmat', 'Median GMAT and GRE'), ('gpa', 'Median undergraduate GPA')):
        sel = m.get(key); r = rec('mba', p, sel[0], sel[1]) if sel else None
        val = r['value'] if r else None
        if r and key == 'gpa' and 'GPA' not in r['item']: val = None
        if r and key == 'gmat' and 'GPA' in r['item'] and 'GMAT' in r['item']: val = r['value'].split(';')[0].strip()
        if key == 'gpa' and nm == 'Dartmouth College (Tuck)':
            r = rec('mba', 'Tuck', 'GMAT average (10th Edition); GPA average', '2027'); val = r['value'].split(';')[1].strip()
        score('mba', nm, field, PAID, FALL, val, FALL if r else '', src(r) if r else '', (f"School figure: {r['item']}, {val}. " if r else 'No school figure found. ') + 'US News uses the median, the US News figure was not read.', reason='paid_tier', shown=val or '')
# two-year averages, shown beside and not scored: job seekers of 2024 and 2025 weighted by each class's job seekers (US News's weighting is not stated)
TWO = {'Stanford University': (('Stanford', 'offers ACCEPTED, at graduation', '2025'), ('Stanford', 'offers ACCEPTED, at graduation / by 3 months', '2024')),}
def seekers(p, item, yr):
    m_ = re.search(r'(\d+) (?:seeking|sought)', rec('mba', p, item, yr)['value']); assert m_, (p, item, yr); return int(m_.group(1))
two = {
 'Stanford University': ((144, 268, 217), (144, 249, 198), ('Stanford', '2025', '2024')),
 'Northwestern University (Kellogg)': ((298, 429, 367), (299, 423, 369), ('Kellogg', '2025', '2024')),
 'University of California, Berkeley (Haas)': ((114, 182, 153), (136, 207, 173), ('Berkeley', '2025', '2024')),
}
wh1 = re.search(r'/ (\d+) \(', rec('mba', 'Wharton', 'offers RECEIVED / ACCEPTED (seeking students)', 'Class of 2025')['value']).group(1)
wh2 = re.search(r'/ (\d+) \(', rec('mba', 'Wharton', 'offers RECEIVED / ACCEPTED (seeking students)', 'Class of 2024')['value']).group(1)
ws1, ws2 = seekers('Wharton', 'students in class; seeking employment', 'Class of 2025'), seekers('Wharton', 'students in class; seeking employment', 'Class of 2024')
_u = U[[s_ for s_ in SLUG['mba'] if NAME[s_] == 'University of Pennsylvania (Wharton)'][0]]
display('mba', 'University of Pennsylvania (Wharton)', 'Two-year average, employed three months after (US News) and accepted offers, timing not stated (report)', _u['emp_3m_2yr'], pct(int(wh1) + int(wh2), ws1 + ws2), 'classes of 2024 and 2025',
        src(rec('mba', 'Wharton', 'offers RECEIVED / ACCEPTED (seeking students)', 'Class of 2025')), f'Accepted offers over job seekers, {wh1}+{wh2} of {ws1}+{ws2}. The report does not say at what point after graduation.')
for nm, (a, b, (p, y1, y2)) in two.items():
    slug = [s for s in SLUG['mba'] if NAME[s] == nm][0]; u = U[slug]
    g = pct(a[0] + b[0], a[1] + b[1]); t = pct(a[2] + b[2], a[1] + b[1])
    display('mba', nm, 'Two-year average, employed at graduation and three months after', f"{u['emp_grad_2yr']} and {u['emp_3m_2yr']}", f'{g} and {t}', 'classes of 2024 and 2025',
            src(rec('mba', p, 'offers ACCEPTED, at graduation' if p == 'Stanford' else 'offers ACCEPTED at graduation / by 3 months', y1)),
            f'Accepted offers over job seekers, both classes summed: at graduation {a[0]}+{b[0]} of {a[1]}+{b[1]}, three months {a[2]}+{b[2]} of {a[1]}+{b[1]}.' + (' Counts are the workbook\'s unrounded shares times job seekers.' if p == 'Kellogg' else ''))
for nm, (p, ia, ib, ra, rb, ka, kb) in {
 'New York University (Stern)': ('NYU', 'total graduates; seeking employment', None, 'Class of 2025', 'Class of 2024', 0, 1),
 'Massachusetts Institute of Technology (Sloan)': ('MIT', None, None, 'Class of 2025', 'Class of 2024', 0, 1)}.items():
    slug = [s for s in SLUG['mba'] if NAME[s] == nm][0]; u = U[slug]
    if p == 'Kellogg':
        s1, s2 = seekers(p, ia, ra), seekers(p, ia, rb); r1, r2 = rec('mba', p, ib, ra)['value'], rec('mba', p, ib, rb)['value']
    elif p == 'NYU':
        s1, s2 = seekers(p, ia, ra), seekers(p, ia, rb)
        r1 = rec('mba', p, 'offers RECEIVED / ACCEPTED at graduation', ra)['value'].split(' / ')[1] + ' / ' + rec('mba', p, 'offers RECEIVED / ACCEPTED, 3 months', ra)['value'].split(' / ')[1]
        r2 = rec('mba', p, 'offers RECEIVED / ACCEPTED at graduation', rb)['value'].split(' / ')[1] + ' / ' + rec('mba', p, 'offers RECEIVED / ACCEPTED, 3 months', rb)['value'].split(' / ')[1]
    else:
        s1, s2 = seekers(p, 'class members; sought employment', ra), seekers(p, 'class members; seeking', rb)
        r1 = rec('mba', p, 'offers RECEIVED / ACCEPTED at graduation', ra)['value'].split(' / ')[1] + ' / ' + rec('mba', p, 'offers RECEIVED / ACCEPTED, 3 months', ra)['value'].split(' / ')[1]
        r2 = rec('mba', p, 'offers RECEIVED / ACCEPTED at graduation', rb)['value'].split(' / ')[1] + ' / ' + rec('mba', p, 'offers RECEIVED / ACCEPTED by 3 months', rb)['value'].split(' / ')[1]
    f = lambda s: [Decimal(x) for x in re.findall(r'(\d+(?:\.\d+)?)%', s)]
    (g1, t1), (g2, t2) = f(r1), f(r2)
    g = format(rnd((g1 * s1 + g2 * s2) / (s1 + s2), 1), 'f'); t = format(rnd((t1 * s1 + t2 * s2) / (s1 + s2), 1), 'f')
    r25 = rec('mba', p, 'offers RECEIVED / ACCEPTED at graduation', ra)
    display('mba', nm, 'Two-year average, employed at graduation and three months after', f"{u['emp_grad_2yr']} and {u['emp_3m_2yr']}", f'{g} and {t}', 'classes of 2024 and 2025', src(r25),
            f'Printed rates weighted by each class\'s job seekers ({s1} in 2025, {s2} in 2024): 2025 {r1}, 2024 {r2}. The reports print rates to one decimal and no counts, so a figure worked from them can differ by 0.1 from one worked from counts.')

# ---------------- Engineering ----------------
F25 = 'fall 2025'
CS = ('US News counts computer science with engineering for research spending and publications even where it sits outside the engineering school (method page). '
      'The school figure is for the engineering school alone, and the US News page does not say which units this figure counts.')
EP = {'Massachusetts Institute of Technology': 'MIT School', 'Stanford University': 'Stanford S', 'University of California, Berkeley': 'UC Berkele', 'Georgia Institute of Technology': 'Georgia Te',
      'Purdue University--Main Campus': 'Purdue Uni', 'California Institute of Technology': 'Caltech Di', 'University of Illinois Urbana-Champaign (Grainger)': 'UIUC Grain',
      'University of Texas--Austin (Cockrell)': 'UT Austin', 'University of California--San Diego (Jacobs)': 'UC San Die', 'Carnegie Mellon University (Carnegie)': 'Carnegie M'}
def er(p, item, yr=None): return rec('eng', p, item, yr)
def enroll_row(nm, p, u):
    usn = u['enroll']
    if p == 'MIT School':
        r = er(p, "Graduate enrollment, total (master's + doctoral + speci" + [x['item'] for x in PUB['eng'] if x['school'].startswith(p) and x['item'].startswith("Graduate enrollment, total (master's + doctoral + speci")][0][55:])
        return score('eng', nm, 'Total graduate engineering enrollment', usn, F25, '3309', F25, src(r), 'MIT Registrar, School of Engineering, fall 2025: 961 master\'s, 2,234 doctoral, 114 special, summed (MIT prints no engineering total). Of these, 376 master\'s and 776 doctoral students are shared with the College of Computing. ' + CS, reason='definition', shown='3,309')
    if p == 'UC San Die':
        r = er(p, 'Graduate enrollment, total (computed)')
        return score('eng', nm, 'Total graduate engineering enrollment', usn, F25, '3985', F25, src(r), 'Jacobs School statistics, fall 2025: 2,631 master\'s and 1,354 Ph.D. students, summed. The same page states $329 million in research expenditures for fiscal 2024-25.', shown='3,985')
    if p == 'Georgia Te':
        r = er(p, 'Graduate enrollment, total (MS + PhD)')
        return score('eng', nm, 'Total graduate engineering enrollment', usn, F25, '12378', F25, src(r), 'Georgia Tech Fact Book, College of Engineering, fall 2025: 9,818 MS and 2,560 PhD, summed. ' + CS, reason='definition', shown='12,378')
    if p == 'Carnegie M':
        r = er(p, 'Graduate enrollment, total (computed)')
        return score('eng', nm, 'Total graduate engineering enrollment', usn, F25, '2773', '2025-26', src(r), 'Carnegie Mellon Quick Facts 2025-2026, College of Engineering: 1,960 master\'s and 813 Ph.D., summed. Computer science is a separate school at Carnegie Mellon. ' + CS, reason='definition', shown='2,773')
    if p == 'UC Berkele':
        r = er(p, 'Graduate students enrolled (total headcount)')
        return score('eng', nm, 'Total graduate engineering enrollment', usn, F25, '2368', 'labelled Fall 2026', src(r), 'Berkeley Engineering facts page, labelled "Enrollment: Fall 2026" when read on 2026-11-10.', shown='2,368')
    if p == 'Caltech Di':
        r = er(p, 'Graduate students in EAS')
        return score('eng', nm, 'Total graduate engineering enrollment', usn, F25, '487', 'not stated', src(r), 'Engineering and Applied Science page, no year printed.', shown='487')
    if p == 'Purdue Uni':
        r = er(p, 'Graduate enrollment, total (includes Agricultural and Biological Engineering)')
        return score('eng', nm, 'Total graduate engineering enrollment', usn, F25, '5617', 'fall 2024', src(r), 'Purdue College of Engineering, fall 2024, including Agricultural and Biological Engineering.', shown='5,617')
    if p == 'UT Austin':
        r = er(p, 'Graduate students enrolled (approximate)')
        return score('eng', nm, 'Total graduate engineering enrollment', usn, F25, 'Approximately 2,000', 'not stated', src(r), 'Cockrell School facts page, rounded and undated.', reason='definition')
    return score('eng', nm, 'Total graduate engineering enrollment', usn, F25, None, '', '', 'Not published as a headcount in the pages read' + (' (Stanford prints only a share, 39 percent of graduate students in engineering).' if p == 'Stanford S' else '.'))
def faculty_row(nm, p, u):
    usn = u['faculty_tt']; f = 'Tenured or tenure-track faculty'
    if p == 'Georgia Te':
        r = er(p, 'Tenured/tenure-track faculty'); return score('eng', nm, f, usn, F25, '403', F25, src(r), 'Georgia Tech Fact Book, College of Engineering, fall 2025. ' + CS, reason='definition')
    if p == 'Carnegie M':
        r = er(p, 'Tenure-track faculty'); return score('eng', nm, f, usn, F25, '165', '2025-26', src(r), 'Quick Facts 2025-2026, College of Engineering. ' + CS, reason='definition')
    if p == 'MIT School':
        r = er(p, 'Tenured/tenure-track faculty (faculty count printed)'); return score('eng', nm, f, usn, F25, '391', 'October 2025', src(r), 'MIT faculty by school, October 2025, 146 shared with the College of Computing, professors to assistant professors. ' + CS, reason='definition')
    if p == 'UT Austin':
        r = er(p, 'Tenure/tenure-track faculty'); return score('eng', nm, f, usn, F25, '297', 'not stated', src(r), 'Cockrell School facts page, no year printed.')
    if p == 'UC Berkele':
        r = er(p, 'Ladder-rank faculty'); return score('eng', nm, f, usn, F25, '248', 'not stated', src(r), 'Berkeley Engineering facts page, ladder-rank faculty, no year printed.')
    if p == 'UC San Die':
        r = er(p, 'Professors (tenure status not stated)'); return score('eng', nm, f, usn, F25, '276', 'labelled Fall 2026', src(r), 'Jacobs School statistics, "Professors (Fall 2026)", tenure status not stated.', reason='definition')
    if p == 'Caltech Di':
        r = er(p, 'Faculty: tenured / non-tenured professorial in EAS'); return score('eng', nm, f, usn, F25, '80 (70 tenured, 10 not tenured)', 'not stated', src(r), 'Engineering and Applied Science page, tenured and non-tenured professorial faculty, no year printed.', reason='year')
    if p == 'Stanford S':
        r = er(p, 'Faculty count, School of Engineering'); return score('eng', nm, f, usn, F25, '280', 'not stated', src(r), 'School description, tenure status and year not stated.', reason='definition')
    if p == 'Purdue Uni':
        r = er(p, 'Faculty count (tenure status not stated)'); return score('eng', nm, f, usn, F25, '494', 'not stated', src(r), 'College facts list, tenure status and year not stated.', reason='definition')
    if p == 'UIUC Grain':
        r = er(p, 'Faculty count (tenure status not stated)'); return score('eng', nm, f, usn, F25, '600+', 'not stated', src(r), 'Grainger About page, tenure status and year not stated.', reason='definition')
for slug in SLUG['eng']:
    nm, u = NAME[slug], U[slug]; p = EP[nm]
    # acceptance rate: no school publishes the engineering master's and doctoral rate; Georgia Tech publishes a college graduate rate
    if p == 'Georgia Te':
        r = er(p, 'Graduate applicants / accepted / enrolled; acceptance rate (MS + PhD)' if False else [x['item'] for x in PUB['eng'] if x['school'].startswith(p) and x['item'].startswith('Graduate applicants / accepted / enrolled; acceptance r')][0], 'Fall 2025')
        score('eng', nm, "Acceptance rate (master's and doctoral)", u['acceptance'], F25, '38.4', F25, src(r), f"Georgia Tech Fact Book, College of Engineering graduate admissions, fall 2025: {r['value']}. US News's own counts on the same page: {u['applicants_ms']} master's and {u['applicants_phd']} Ph.D. applicants, against 13,150 in the Fact Book. " + CS, reason='definition')
    else:
        score('eng', nm, "Acceptance rate (master's and doctoral)", u['acceptance'], F25, None, '', '', 'No engineering graduate acceptance rate or admits count for fall 2025 in the pages read.')
    enroll_row(nm, p, u)
    faculty_row(nm, p, u)
    h = er(p, 'NSF HERD engineering R&D expenditures, total all sources (whole-institution engineering field)', 'FY 2024')
    score('eng', nm, 'Total research expenditures', PAID, 'fiscal 2024 and 2025 average', f"{int(first_int(h['value'])):,} thousand dollars" + (' (HERD prints the flag i)' if 'flag' in str(h['value']) else ''), 'fiscal 2024', src(h),
          'Shown: NSF HERD fiscal 2024, engineering field, whole institution, all sources. US News uses externally funded engineering research by the ASEE definition, averaged over fiscal 2024 and 2025, a different scope. HERD fiscal 2025 is not released.', reason='paid_tier')
    i = er(p, "IPEDS Completions CIP family 14 (Engineering), first majors, doctor's degree - research/scholarship (AWLEVEL 17)", 'AY 2023-24')
    score('eng', nm, 'Doctoral degrees awarded', PAID, '2024-25', i['value'], '2023-24', src(i),
          'Shown: IPEDS completions 2023-24, engineering (CIP 14), research doctorates, first majors, whole institution, computer science not included. IPEDS 2024-25 is not released.', reason='paid_tier')

# ---------------- Education ----------------
DP = {'University of Wisconsin--Madison': 'UW-Madison', 'Northwestern University': 'Northwestern', 'University of Florida': 'University of Florida', 'University of Michigan--Ann Arbor (Marsal)': 'University of Michigan',
      'Vanderbilt University (Peabody)': 'Vanderbilt', 'Harvard University': 'Harvard', 'New York University (Steinhardt)': 'NYU', 'Teachers College, Columbia University': 'Teachers College',
      'University of California, Berkeley': 'UC Berkeley', 'University of California--Los Angeles': 'UCLA', 'University of Texas--Austin': 'UT Austin', 'University of Virginia': 'University of Virginia'}
Y25 = '2025-26'
for slug in SLUG['edu']:
    nm, u = NAME[slug], U[slug]; p = DP[nm]
    score('edu', nm, 'Acceptance rate, as US News prints it', u['acceptance'], Y25, None, '', '', f"No admits count or acceptance rate for 2025-26 in the pages read. US News's own counts on the same page: {u['accepted']} of {u['applicants']}.")
    if p == 'Vanderbilt':
        r = rec('edu', p, 'total enrollment')
        score('edu', nm, 'Total enrollment', u['total_enroll'], 'fall 2025', '2,699', 'not stated', src(r), 'Peabody College about page, "2,699 Students", no year, and the same page says the college enrolls nearly 1,500 undergraduates. US News counts graduate students.', reason='definition')
    else:
        score('edu', nm, 'Total enrollment', u['total_enroll'], 'fall 2025', None, '', '', 'No education school graduate enrollment in the pages read.')
    if u.get('faculty_tt') and p == 'Vanderbilt':
        r = rec('edu', p, 'full-time faculty')
        score('edu', nm, 'Tenured or tenure-track faculty', u['faculty_tt'], 'fall 2025', '189 (full-time faculty)', 'not stated', src(r), 'Peabody College about page, "189 Full-time Faculty", no tenure split and no year.', reason='definition')
    elif u.get('faculty_tt'):
        score('edu', nm, 'Tenured or tenure-track faculty', u['faculty_tt'], 'fall 2025', None, '', '', 'No tenured or tenure-track faculty count in the pages read.')
    if u.get('assessment_takers'):
        score('edu', nm, 'Students who took a licensure assessment', u['assessment_takers'], '2024-25', None, '', '', 'Title II institution report cards (title2.ed.gov) were not read in this pass.')
    h = rec('edu', p, 'NSF HERD R&D expenditures, field Education (non-S&E), institution-wide', 'FY2024')
    note = 'Shown: NSF HERD fiscal 2024, education field, whole institution. US News uses the education school\'s research spending averaged over fiscal 2024 and 2025, as reported by schools, a different scope. HERD fiscal 2025 is not released.'
    if p == 'Teachers College': note += ' Teachers College\'s own HERD row prints 0 in education and 54 thousand dollars in other non-science fields.'
    if p == 'Vanderbilt': note += ' The HERD row is Vanderbilt University with Vanderbilt University Medical Center.'
    score('edu', nm, 'Total research expenditures', PAID, 'fiscal 2024 and 2025 average', f"{int(first_int(h['value'])):,} thousand dollars", 'fiscal 2024', src(h), note, reason='paid_tier')
    i = rec('edu', p, 'IPEDS completions CIP 13 (Education), AWLEVEL 17 doctor\'s research/scholarship, first major, total', '2023-24')
    i18 = rec('edu', p, 'IPEDS completions CIP 13 (Education), AWLEVEL 18 doctor\'s professional practice, first major, total', '2023-24')
    extra = '' if str(i18['value']) in ('no row', 'None') else f" Professional practice doctorates (EdD and similar) in the same file: {i18['value']}."
    score('edu', nm, 'Doctoral degrees granted', PAID, '2024-25', i['value'], '2023-24', src(i), 'Shown: IPEDS completions 2023-24, education (CIP 13), research doctorates, first majors, whole institution.' + extra + ' IPEDS 2024-25 is not released.', reason='paid_tier')

# ---------------- Medicine (Tier 1) ----------------
MP = {'Baylor College of Medicine': 'Baylor', 'Case Western Reserve University': 'Case Western', 'Emory University': 'Emory', 'Mayo Clinic School of Medicine (Alix)': 'Mayo',
      'Ohio State University': 'Ohio State', 'University of California--Los Angeles (Geffen)': 'UCLA', 'University of California--San Diego': 'UC San Diego', 'University of California--San Francisco': 'UCSF',
      'University of Colorado': 'University of Colorado', 'University of Florida': 'University of Florida', 'University of Pittsburgh': 'University of Pittsburgh', 'University of Rochester': 'University of Rochester',
      'University of South Florida (Morsani)': 'USF', 'University of Texas Southwestern Medical Center': 'UT Southwestern', 'Vanderbilt University': 'Vanderbilt', 'Yale University': 'Yale'}
E25 = '2025 entering class'
def mr(p, item, yr=None):
    c = [x for x in PUB['med'] if x['school'].startswith(p) and x['item'] == item and (yr is None or yr in str(x.get('year') or ''))]
    return c[0] if len(c) == 1 else None
for slug in SLUG['med']:
    nm, u = NAME[slug], U[slug]; p = MP[nm]
    a1 = mr(p, 'AAMC A-1 applications (to school)', '2025-2026'); m1 = mr(p, 'AAMC A-1 matriculants', '2025-2026')
    aamc = f" AAMC FACTS A-1, 2025-26: {a1['value']} applications, {m1['value']} matriculants (AAMC does not publish offers by school)." if a1 and m1 else ''
    if p == 'Yale':
        r = mr(p, 'school class profile: acceptance rate')
        score('med', nm, 'Acceptance rate', u['acceptance'], E25, '4.4', E25, src(r), 'Yale School of Medicine, MD Class of 2029 profile: acceptance rate 4.4%, 6,206 applicants, class size 104.' + aamc, shown='4.4%')
    elif p == 'Mayo':
        r = next((x for x in PUB['med'] if x['school'].startswith('Mayo') and x.get('file') and 'mayo_profile' in str(x.get('file'))), None)
        score('med', nm, 'Acceptance rate', u['acceptance'], E25, '3.5%', '2026 entering class', src(r) if r else 'https://college.mayo.edu/', 'Mayo Clinic Alix School of Medicine profile page (saved copy public/grad/med/files/schools/mayo_profile.html) prints a 2026 acceptance rate of 3.5% (6,061 applications, 215 offers). No 2025 figure on the page.' + aamc, reason='year')
    elif p == 'University of Pittsburgh':
        r = mr(p, 'school class profile: offers of acceptance')
        score('med', nm, 'Acceptance rate', u['acceptance'], E25, pct(317, 11888, 4), E25, src(r), 'Pitt School of Medicine, 2025 admissions statistics (Class of 2029): 317 offers of acceptance, 11,888 applicants, 151 matriculants, worked as 317 over 11,888.' + aamc, shown=pct(317, 11888) + '%')
    else:
        score('med', nm, 'Acceptance rate', u['acceptance'], E25, None, '', '', 'No offers count or acceptance rate for the 2025 entering class on the school pages read.' + aamc)
    b = mr(p, 'AAMC B-1.2 total MD enrollment (All)', '2025-2026')
    score('med', nm, 'Total medical school enrollment', u['enroll'], '2025', b['value'], '2025-26 (October 31 count)', src(b),
          'AAMC FACTS B-1.2 counts all MD students enrolled on October 31, students on leave included. US News\'s method uses full-time MD students in 2025. The two are printed side by side.', reason='definition')
    if p == 'Yale':
        r = mr(p, 'faculty: total faculty (all types)')
        score('med', nm, 'Full-time faculty', u['faculty_ft'], '2025', '5,485 (all types)', 'not stated', src(r), 'Yale facts page: total faculty of all types (ladder 2,506, research 801, lecturer and instructor 222, visiting 63, emeritus 187, voluntary and adjunct 1,706), no full-time count labelled.', reason='definition')
    elif p == 'Baylor':
        score('med', nm, 'Full-time faculty', u['faculty_ft'], '2025', None, '', '', 'No full-time faculty count could be read in the school documents saved.')
    else:
        score('med', nm, 'Full-time faculty', u['faculty_ft'], '2025', None, '', '', 'No full-time faculty count on the school pages read. US News uses the count schools report to the LCME, which is not published by school.')
    mc = mr(p, 'school class profile: median MCAT'); gp = mr(p, 'school class profile: median GPA') or mr(p, 'school class profile: median cumulative GPA')
    score('med', nm, 'Median MCAT score', PAID, E25, mc['value'] if mc else None, E25 if mc else '', src(mc) if mc else '', ('Shown: school class profile, median MCAT of the 2025 entering class. ' if mc else 'No school figure found. AAMC publishes MCAT by school only in a paid guide. ') + 'The US News figure was not read.', reason='paid_tier', shown=(mc['value'] if mc else ''))
    score('med', nm, 'Median undergraduate GPA', PAID, E25, gp['value'] if gp else None, E25 if gp else '', src(gp) if gp else '', ('Shown: school class profile, median GPA of the 2025 entering class. ' if gp else 'No school figure found. ') + 'The US News figure was not read.', reason='paid_tier', shown=(gp['value'] if gp else ''))
    n24 = mr(p, 'NIH RePORTER FY total, awards typed School of Medicine', 'FY2024'); n25 = mr(p, 'NIH RePORTER FY total, awards typed School of Medicine', 'FY2025')
    t24 = mr(p, 'NIH RePORTER FY total, all awards to organization name', 'FY2024'); t25 = mr(p, 'NIH RePORTER FY total, all awards to organization name', 'FY2025')
    if n24 and n24.get('value') and n25 and n25.get('value'):
        shown = f"{n24['value']} (fiscal 2024), {n25['value']} (fiscal 2025)"; what = 'awards typed School of Medicine'
    else:
        shown = f"{t24['value']} (fiscal 2024), {t25['value']} (fiscal 2025)"; what = 'all awards to the organization (no awards typed School of Medicine)'
    note = (f'Shown: NIH RePORTER, {what}, summed by award amount for each fiscal year (method in public/grad/med/SOURCES.md). All awards to the organization: {t24["value"]} and {t25["value"]}. '
            'US News uses the medical school and its affiliated hospitals as each school reports them, averaged over fiscal 2024 and 2025, a different scope.')
    if p == 'Vanderbilt':
        v24 = mr(p, 'NIH RePORTER FY total, VANDERBILT UNIVERSITY MEDICAL CENTER (separate org name, typed Independent Hospitals)', 'FY2024'); v25 = mr(p, 'NIH RePORTER FY total, VANDERBILT UNIVERSITY MEDICAL CENTER (separate org name, typed Independent Hospitals)', 'FY2025')
        note += f' Vanderbilt University Medical Center is a separate NIH organization: {v24["value"]} and {v25["value"]}.'
    score('med', nm, 'NIH research grants', PAID, 'fiscal 2024 and 2025', shown, 'fiscal 2024 and 2025', src(n25 or t25), note, reason='paid_tier')

SHOWN_TEXT = {
 'mba': 'US News prints two-year averages of the employment rates. Its method weights the classes of 2024 and 2025 by size and does not say whether graduates or job seekers are counted, so these are shown and not scored. The public side is worked from each school\'s two employment reports.',
}
json.dump({'read': '2026-11-10', 'plan': 'PLAN.md Addendum 2 (04f16e5)', 'checks': OUT, 'shown_text': SHOWN_TEXT}, open('data/checks_grad.json', 'w', encoding='utf-8'), indent=1)
if __name__ == '__main__':
    from collections import Counter
    c = Counter((o['list'], o['outcome']) for o in OUT); r = Counter((o['list'], o['reason']) for o in OUT if o['outcome'] == 'CANNOT_TELL')
    for k in ('mba', 'eng', 'edu', 'med'):
        print(k, c[(k, 'MATCH')], 'match', c[(k, 'MISMATCH')], 'mismatch', c[(k, 'CANNOT_TELL')], 'cannot tell', c[(k, 'DISPLAY')], 'shown |', {w: n for (l, w), n in r.items() if l == k})
