"""STAGED (not shipped) Recount Matrix: Learning Research page, built from WALL_S0.md + rows/*.md with indahl.ai's own page() and CSS.
Writes matrix_page/staged/learning-matrix.html + style.css. Nothing here touches indahl-ai/ or ledger/ship.sh.
Text rules: per institution only the bin (our label), our own verified cell text where the table has one, and one source link. No adjectives, no scores, alphabetical."""
import os, re, sys, html, glob
B = os.path.expanduser('~/bones-forge/oy_index/'); SITE = os.path.expanduser('~/bones-forge/indahl-ai/')
sys.path.insert(0, SITE)
sys.path.insert(0, os.path.expanduser('~/bones-forge/heuremen_kit')); import heuremen_kit as K   # 12 Nov 2026: REQ-13 line, see PLAN_ADDENDUM_std2.md
try: import build_site as bs
except Exception as _e:   # 30 Oct 2026: build_site.py is edited by others while this runs. oy_body.html does not need it, only the staged preview does.
    bs = None; print('build_site import failed, staged preview skipped:', repr(_e)[:160])
AS_OF = '25 October 2026'; AS_OF_SHORT = '25 Oct 2026'   # the date every row of the Wall was read (WALL_S0.md); site pass 30 Oct 2026 G-2, G-11
OWN = 'heuremen/OY (row 0)'   # our own row: listed first and counted in the 148 rows. The page says so (site pass G-1: 148 rows, one of them ours)
LV = ['MEASURED-POLICY', 'TRIAL REPORTED WITHOUT NUMBERS', 'PLANNED ONLY', 'USAGE-OR-ATTITUDE ONLY', 'NONE FOUND', 'UNREACHED']
# 10 Nov 2026 (our newsletter audit, research/nl_audit_oy_social_20261110.md): the bins are policy level, so the labels say pilots are counted in their own row.
# UNREACHED is new: a row whose provost or teaching-centre pages refused our reader or need a login is never folded into None found (RETRIEVAL_BARRIERS.md).
LABEL = {'MEASURED-POLICY': 'Measured its own policy, guidance or a centrally provided tool', 'TRIAL REPORTED WITHOUT NUMBERS': 'Outcome reported without counts',
         'PLANNED ONLY': 'Plans to measure its own policy (pilots counted in their own row)', 'USAGE-OR-ATTITUDE ONLY': 'Surveys of use or attitudes, no measure of its own policy (pilots counted in their own row)',
         'NONE FOUND': 'None found', 'UNREACHED': 'Not reached: its pages refused our reader or need a login'}
SHORT = {'MEASURED-POLICY': 'Measured its own policy or a central tool', 'TRIAL REPORTED WITHOUT NUMBERS': 'Outcome reported without counts', 'PLANNED ONLY': 'Plans to measure',
         'USAGE-OR-ATTITUDE ONLY': 'Usage or attitude surveys, no measure', 'NONE FOUND': 'None found', 'UNREACHED': 'Not reached'}
import json as _json
RF = _json.load(open(B + 'S0_REFILE_20261110.json', encoding='utf-8'))   # 10 Nov 2026: the refiling, read here so every count below comes from the rows
HOLD = set()   # 25 Oct (his word): Bones reviewed P3-16 (unm, temple) and P3-18 (stjohnfisher) himself; tags kept internal, not on the page
PUB_FINDING = {   # public text per single-institution row: our label + verified figures only (internal notes stay in WALL_S0.md)
 'unm': 'Measured its own policy or tool: Turnitin AI detector audit, December 2025. 3 of 84 human-written texts flagged. 42 of 63 AI or AI-assisted texts missed.',
 'temple': 'Measured its own policy or tool: Turnitin AI indicator test, August 2023, 120 texts. Human 28 of 30 correct. AI-used 77 of 90 flagged. Hybrid 13 of 30.',
 'stjohnfisher': 'Measured its own policy or tool: AI syllabus policy, 3,300+ syllabi over five semesters. Syllabi with no AI policy stated: 19.5% to 2.7%.',
 'wsu': 'Outcome reported without counts: \u201cBetween 2023-2025, 33% of all Academic Integrity Hearing Board cases related to allegations of inappropriate AI use led to a finding of not responsible because AI detection was submitted independent of any other supporting evidence.\u201d The memo gives no case count.',
 'gsu': 'Outcome reported without counts: a Studiosity evaluation is stated. No count is published.',
 # 10 Nov 2026: filed at policy level under the one rule (a tool a central office provides for use beyond one course), as unm and temple
 'umd': 'Measured a tool a central office provides: Virtual Study Assistant from the Division of IT, randomized across 30 instructors, Fall 2025, 2,379 students. Final grade \u22120.37 SD in the exact-match sample.',
 'cmu': 'Measured a tool a central office provides: GenAI learning modules from the Eberly Center, course-randomized, 1,368 students. AI competency above on three outcomes, cannot tell (NO_INTERVAL_FORMABLE) on two.',
 'msu': 'Measured a tool a central office provides: Khanmigo licences funded by the Office of Undergraduate Education. One course, 87 students. p = 0.12: cannot tell (NO_INTERVAL_FORMABLE).',
}
PUB_PILOT = {
 'umd': 'Randomized, own study assistant, Fall 2025, 2,379 students. Final grade \u22120.37 SD in the exact-match sample.',
 'harvard': 'Crossover, 194 students. Post-test above active learning. Topic and week confounded.',
 'cmu': 'Course-randomized AI modules, 1,368 students. AI competency above on three outcomes, cannot tell (NO_INTERVAL_FORMABLE) on two.',
 'msu': 'Khanmigo, one course, 87 students. p = 0.12: cannot tell (NO_INTERVAL_FORMABLE).',
 'pitt': 'Hybrid anatomy course, 129 students. Final grades not significantly different: cannot tell (NO_INTERVAL_FORMABLE).',
 'jhu': 'Pre-college course, 22 students. No significant differences: cannot tell (NO_INTERVAL_FORMABLE).',
 'unc': 'Peer-feedback study, 129 randomized. Feedback quality above (not learning).',
 'gatech': 'Socratic Mind, 173 of 579 assigned. Quiz above (self-selected). Tests cannot tell (NO_INTERVAL_FORMABLE).',
 'pomona': 'Human vs AI feedback, 10 students: cannot tell (NO_INTERVAL_FORMABLE).',
 'berkeley': '61A Bot, over 2,000 students. Homework time down against prior terms (not learning).',
 'princeton': 'Randomized CubBot assessment, 134 students. We have not read the results.',
 'rochester': 'GoodNurse course. Users 95.1% vs non-users 88.8%. The paper is behind a paywall and we have not read the number of students.',
}
UNREAD_PILOTS = {'princeton', 'rochester'}
# 31 Oct 2026 (notices inventory): each pilot's figures now link the pilot's own source, the document they were read from (rows/<slug>.md);
# before, the pilot text sat beside the institution's S0 link only, so Harvard's Kestin figures appeared next to a library survey.
PILOT_SRC = {
 'umd': 'https://edworkingpapers.com/sites/default/files/ai26-1598.pdf',
 'harvard': 'https://github.com/HarvardAItutor/Study-Data-v4',
 'cmu': 'https://www.cmu.edu/teaching/gaitar/gaitaratscale/asynchronouslearningmodules.html',
 'msu': 'https://doi.org/10.17613/3yyd2-t3r81',
 'pitt': 'https://www.lrdc.pitt.edu/departments-and-services/communications-news-media/supplemental-ai-hybrid-human-anatomy-course-and-its-effect-student-performance-and-engagement',
 'jhu': 'https://doi.org/10.1177/1932202X251356323',
 'unc': 'https://cfe.unc.edu/wp-content/uploads/sites/1381/2025/06/Noel_Manuscript_GenAI-CFE-Grant_FINAL-DRAFT.docx',
 'gatech': 'https://doi.org/10.1007/s10758-026-10007-6',
 'pomona': 'https://ritg.pomona.edu/events/the-2026-hahn-grant-showcase-review/',
 'berkeley': 'https://arxiv.org/abs/2406.05600',
 'princeton': 'https://doi.org/10.1145/3770761.3777156',
 'rochester': 'https://doi.org/10.1097/NNE.0000000000002178',
}
assert set(PILOT_SRC) == set(PUB_PILOT), set(PILOT_SRC) ^ set(PUB_PILOT)
def pilot_cell(r): return (E(r["pilot"]) + ((' (<a href="' + E(PILOT_SRC[r['slug']]) + '">pilot source</a>)') if r['slug'] in PILOT_SRC else '')) if r["pilot"] else "&ndash;"
   # pilots whose results or sample size we have not read: shown, not counted
def name_of(slug):
    if slug == 'heuremen/OY (row 0)': return 'Heuremen (our own row)'
    if slug == 'cornell': return 'Cornell University'
    f = B + 'rows/' + slug + '.md'
    if not os.path.exists(f): return slug
    h = open(f).readline().strip().lstrip('#').strip()
    h = re.sub(r'^(The Wall \(OY\) - Row:|Row -|Row:)\s*', '', h)
    return re.split(r'\s+\(|\s+-\s+THE WALL', h)[0].strip()

def _full(u, t):   # 25 Oct sweep: a URL with parentheses was cut at the first ")"; extend it from the text up to whitespace
    if u.count('(') > u.count(')'):
        i = t.find(u)
        if i >= 0:
            m = re.match(r'[^\s|>"\]]+', t[i:])
            if m: u = m.group(0).rstrip('.,;:')
    return u
# 30 Oct 2026 site pass G-15: Cornell has no rows/ file, so its institution link is set here (WALL.md row S1: the Spring 2025 survey results page)
SRC_OVERRIDE = {'cornell': 'https://academicinnovation.cornell.edu/gen-ai/generative-ai-impact-on-learning-spring-2025-surveys/'}
# 30 Oct 2026 site pass G-15: where the institution link goes to a page the institution does not host, say what it is, beside the name
KIND_HOST = {'arxiv.org': 'preprint', 'www.socialscienceregistry.org': 'registry entry', 'www.jowr.org': 'journal article', 'www.rpajournal.com': 'journal article',
             'journals.library.ualberta.ca': 'journal article', 'joidat.scholasticahq.com': 'journal article', 'www.sciencedirect.com': 'journal article',
             'onetwentyseven.blog': 'faculty blog post', 'causeweb.org': 'conference slides'}
KIND_DOI = {'10.17613': 'repository copy of its report', '10.15766': 'journal article'}
def kind_of(u):
    if not u: return ''
    from urllib.parse import urlparse
    pu = urlparse(u)
    if pu.netloc in ('doi.org', 'dx.doi.org'): return KIND_DOI.get(pu.path.lstrip('/').split('/')[0], 'journal article')
    return KIND_HOST.get(pu.netloc, '')
# 30 Oct 2026 site pass G-11/G-12: public AI policy or guidance column. Links that the first-URL rule gets wrong or cannot find (row files read, not edited).
S1_OVERRIDE = {
 'miami': ('Link, archived copy of 8 Oct 2024', 'https://web.archive.org/web/20241008182540/https://petal.miami.edu/teaching-guides-and-policies/teaching-and-learning-with-ai/index.html'),   # the live PETAL page is gone (404). The current copy is on a Miami sign-in SharePoint site.
 'mit': ('Link', 'https://sites.mit.edu/ai-use/ai-committee-final-report-aug-13/'),   # rows/mit.md S1 names the committee report, its link sits on the S0 line
 'cornell': ('Link', 'https://teaching.cornell.edu/generative-artificial-intelligence/cu-committee-report-generative-artificial-intelligence-education'),   # SWEEP_ivies.md, Cornell, CU Committee Report 18 Jul 2023
}
S1_NONE = {OWN}   # rows where we looked and the row says none found (rows/ and WALL.md, read 25 Oct 2026)
def source_of(slug):
    if slug in SRC_OVERRIDE: return SRC_OVERRIDE[slug]
    f = B + 'rows/' + slug + '.md'
    if not os.path.exists(f): return None
    t = open(f).read(); m = re.search(r'^[#\- ]*S0[^\n]*', t, re.M)
    seg = t[m.start():m.start() + 3000] if m else t
    u = re.findall(r'https?://[^\s)|>"\]]+', seg) or re.findall(r'https?://[^\s)|>"\]]+', t)
    return _full(u[0].rstrip('.,;:'), t) if u else None
rows = []
for l in open(B + 'WALL_S0.md'):
    if l.startswith('| ') and not l.startswith('| school'):
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        lv = next(k for k in LV if c[1].startswith(k))
        for n in [x.strip() for x in c[0].split(',')]:
            detail = PUB_FINDING.get(n, '')
            pilot = PUB_PILOT.get(n, '')
            rows.append(dict(slug=n, name=name_of(n), lv=lv, detail=detail, pilot=pilot, src=source_of(n)))
for r in rows:   # 10 Nov 2026 refiling (S0_REFILE_20261110.json)
    if r['slug'] in RF['policy_central_tool']: r['lv'] = 'MEASURED-POLICY'
    if r['slug'] in RF['unreached']: assert r['lv'] == RF['unreached'][r['slug']]['from'], r['slug']; r['lv'] = 'UNREACHED'
    r['orig'] = RF['original_rule'].get(r['slug'], {}).get('outcome', '')
    r['learn_pol'] = r['lv'] == 'MEASURED-POLICY' and RF['policy_central_tool'].get(r['slug'], {}).get('learning', False)
assert set(RF['original_rule']) <= {r['slug'] for r in rows} and set(RF['policy_central_tool']) <= {r['slug'] for r in rows}
rows.sort(key=lambda r: (r['slug'] != OWN, r['name'].lower()))
count_ = {k: sum(1 for r in rows if r['lv'] == k) for k in LV}
E = html.escape
def cell(r):
    d = E(r['detail']) if r['detail'] else E(LABEL[r['lv']])
    if r['slug'] in HOLD: d += ' <span class="hold">[held until outside referee]</span>'
    return d
trs = '\n'.join(
    f'<tr><td>{E(r["name"])}</td><td>{cell(r)}</td><td>{pilot_cell(r)}</td>'
    f'<td>{("<a href=" + chr(34) + E(r["src"]) + chr(34) + ">source</a>") if r["src"] else "&ndash;"}</td></tr>' for r in rows)

sys.path.insert(0, B + 'matrix_page'); import findings as F
# 25 Oct (his word): headline data first, then a table of findings with every school linked, then the list. Restacked from what is on file; nothing new looked up.
import re as _re, glob as _glob, collections as _co
def _s1(slug):
    f = B + 'rows/' + slug + '.md'
    if not os.path.exists(f): return None
    t = open(f, errors='ignore').read(); m = _re.search(r'^[#\- ]*S1\b[^\n]*\n?(.*?)(?=^[#\- ]*S2\b)', t, _re.S | _re.M)
    if not m: return None
    u = _re.findall(r'https?://[^\s)|>"\]]+', m.group(0)); return _full(u[0].rstrip('.,;:'), t) if u else None
S3 = {}
for _l in open(B + 'WALL_S3.md'):
    _m = _re.match(r'- (\S+): \[([^\]]+)\]', _l)
    if _m: S3[_m.group(1)] = 'none' if _m.group(2).startswith('NONE') else ('agg' if _m.group(2).startswith('AGG') else ('micro' if _m.group(2).startswith('MICRO') else 'hand'))
S3.update({'harvard': 'none', 'miami': 'none', 'nyu': 'none', 'unt': 'none', 'unm': 'agg', 'cornell': 'agg'})
assert _co.Counter(S3.values()) == _co.Counter({'none': 76, 'agg': 38}), _co.Counter(S3.values())
L_ = lambda name, url: f'<a href="{E(url)}">{E(name)}</a>' if url else E(name)
LK = lambda name, url: L_(name, url) + (f' <span class="srckind">({E(kind_of(url))})</span>' if kind_of(url) else '')   # G-15
BY = {r['slug']: r for r in rows}
def names(lst): return ', '.join(lst) if lst else '&mdash;'
def det(items): return f'<details><summary>what we found</summary><ul>' + ''.join(f'<li><b>{n}</b>: {t}</li>' for n, t in items) + '</ul></details>'
FT = []
NROWS = len(rows)
FT.append(('Chatbot cited as a source', f'{len(set(i for i, d, q, u in F.CHATBOT))} of {NROWS}', names([L_(html.unescape(i), u) for i, d, q, u in F.CHATBOT])))
for k in LV:
    lst = [r for r in rows if r['lv'] == k]
    cell_ = names([LK(r['name'], r['src']) for r in lst])
    if k in ('MEASURED-POLICY', 'TRIAL REPORTED WITHOUT NUMBERS'): cell_ += det([(E(r['name']), E(r['detail'])) for r in lst if r['detail']])
    if k == 'UNREACHED': cell_ += det([(E(r['name']), E(RF['unreached'][r['slug']]['why'][:1].upper() + RF['unreached'][r['slug']]['why'][1:] + '.')) for r in lst])
    FT.append((E(LABEL[k]), f'{len(lst)} of {NROWS}', cell_))
# 10 Nov 2026: both readings counted from the rows (no number is typed here). The original rule leads, the later rule sits beside it with its timing.
ORIG = [r for r in rows if r['orig']]; LPOL = [r for r in rows if r['learn_pol']]; UNR = [r for r in rows if r['lv'] == 'UNREACHED']
NREAD = NROWS - len(UNR)   # 12 Nov 2026 (addendum): a school not reached is NOTHING_RETURNED, outside numerator and denominator of a headline share
LPOL_CT = [r for r in rows if r['slug'] in RF.get('policy_cannot_tell', {})]   # rows the later rule cannot settle from the record: the count is printed as a range
R13 = K.req13([{'outcome': 'CANNOT_TELL', 'reason': K.NO_INTERVAL_FORMABLE} if r['slug'] in RF.get('policy_cannot_tell', {}) else {'outcome': 'FILED', 'reason': None} for r in rows if r['lv'] != 'UNREACHED'], nothing_returned=[r['slug'] for r in UNR])
NPOL = f'{len(LPOL)} to {len(LPOL) + len(LPOL_CT)}' if LPOL_CT else f'{len(LPOL)}'
_none_ = lambda: f'None found in any row. As of {AS_OF}.'
FT.insert(0, ('Grade or learning outcome of its own AI policy, guidance, tool or pilot. Rule written before any school was read', f'{len(ORIG)} of {NREAD}',
              (names([LK(r['name'], r['src']) for r in ORIG]) + det([(E(r['name']), E(r['orig'])) for r in ORIG])) if ORIG else _none_()))
FT.insert(1, ('Grade or learning outcome of its own policy, guidance or a centrally provided tool. Rule set after the first 41 schools were read', f'{NPOL} of {NREAD}',
              (names([LK(r['name'], r['src']) for r in LPOL + LPOL_CT]) + (det([(E(r['name']), 'Cannot tell (NO_INTERVAL_FORMABLE). ' + E(RF['policy_cannot_tell'][r['slug']]['why'])) for r in LPOL_CT]) if LPOL_CT else '')) if LPOL + LPOL_CT else _none_()))
N_S3 = len(S3); MICRO = sorted(s_ for s_, v in S3.items() if v == 'micro')
FT.append((f'Released microdata from its own survey or evaluation of AI use or outcomes (of {N_S3} read)', f'{len(MICRO)} of {N_S3}',
           names([LK(BY.get(s_, {}).get('name') or name_of(s_), BY.get(s_, {}).get('src')) for s_ in MICRO]) if MICRO else f'None found. As of {AS_OF}.'))
for key, lab in (('agg', 'Released summary tables or an instrument only (of 114 read)'), ('none', 'Released nothing (of 114 read)')):
    lst = sorted([s_ for s_, v in S3.items() if v == key], key=lambda s_: (BY.get(s_, {}).get('name') or name_of(s_)).lower())
    FT.append((lab, f'{len(lst)} of 114', names([LK(BY.get(s_, {}).get('name') or name_of(s_), BY.get(s_, {}).get('src')) for s_ in lst])))
pil = [s_ for s_ in PUB_PILOT if s_ not in UNREAD_PILOTS]
FT.append(('Pilots run or funded by the institution, results read', f'{len(pil)} of {NROWS}', names([LK(BY.get(s_, {}).get('name') or name_of(s_), BY.get(s_, {}).get('src')) for s_ in pil]) + det([(E(BY.get(s_, {}).get('name') or name_of(s_)), E(PUB_PILOT[s_]) + ' (<a href="' + E(PILOT_SRC[s_]) + '">pilot source</a>)') for s_ in pil])))
FT.append(('Studies checked against their own data', len(F.RECOUNTS), names([L_(html.unescape(st), u) for st, t, u in F.RECOUNTS]) + det([(st, t) for st, t, u in F.RECOUNTS])))
FT.append(('Own documents, own numbers', len(F.OWN_NUMBERS), names([LK(html.unescape(i), u) for i, t, u in F.OWN_NUMBERS]) + det([(i, t) for i, t, u in F.OWN_NUMBERS])))
FT.append(('Studies by the school&rsquo;s own faculty or staff', len(F.THAT_SCHOOL), names([LK(html.unescape(i), u) for i, t, u in F.THAT_SCHOOL]) + det([(i, t) for i, t, u in F.THAT_SCHOOL])))
ft_rows = ''.join(f'<tr><td>{a}</td><td class="n">{b}</td><td>{c}</td></tr>' for a, b, c in FT)
DREL = {'agg': 'Summary tables or an instrument only', 'none': 'Nothing', 'hand': 'See source'}
REREAD = RF.get('reached_in_browser', {})   # 10 Nov 2026: rows read again in a browser, dated by that read
def mon(r): return E(SHORT[r['lv']]) + (', ' + (REREAD[r['slug']]['read'] if r['slug'] in REREAD else AS_OF_SHORT) if r['lv'] in ('NONE FOUND', 'UNREACHED') else '')   # G-11: a None found says when we looked
def s1cell(r):   # G-11, G-12. 10 Nov 2026 (newsletter audit): the cell is the first document our notes cite, not a judgement that it is a policy, so it says Link
    sl = r['slug']
    if sl in RF['first_document_none']: return 'None found, ' + AS_OF_SHORT + '. Teaching-centre pages need a login'
    if sl in S1_OVERRIDE: return L_(*S1_OVERRIDE[sl])
    u = _s1(sl)
    if u: return L_('Link', u)
    if sl in S1_NONE: return 'None found, ' + AS_OF_SHORT
    return 'Not looked for yet'
trs = '\n'.join(
    f'<tr><td>{LK(r["name"], r["src"])}</td><td>{s1cell(r)}</td><td>{mon(r)}</td>'
    f'<td>{DREL.get(S3.get(r["slug"]), "Not read")}</td><td>{pilot_cell(r)}</td></tr>' for r in rows)
# 30 Oct 2026 site pass G-1, G-2: the date, the method and the rule for how the institutions were picked, above the counts
METHOD = (f'<section><h2>How these rows were read</h2><p>This page is as of {AS_OF}. It is one pass. On 10 November 2026 we read again, in a browser, the pages of {len(REREAD)} schools that had refused our reader, and those rows are dated 10 Nov 2026. The <a href=\"/campus\">CAMPUS</a> page reads the documents these rows cite every few hours and shows which have changed or gone since. For each institution we looked for what it has published about AI in teaching and learning. '
          'We read its own public pages and checked scholarly indexes for studies by its faculty. For most rows a general web search was not run. '
          'Where we write none found, we did not find it in those places on that date. That does not show that none exists. '
          'Where the provost or teaching-centre pages refused our reader or needed a login, the row says not reached, not none found. '
          'Two rules count a measured outcome. We wrote the first at about 10:10 on 25 October, before reading any school. It counts a grade or learning outcome of the institution&rsquo;s own AI policy, guidance, tools or pilots, including a faculty pilot in one of its own courses, with a stated number of students and a comparison, such as before and after or one group against another. '
          'We set the second at 11:35 the same day, after the first 41 schools were read. It counts only the institution&rsquo;s own policy, guidance or a tool that a central office, such as IT, a teaching centre, the provost or undergraduate education, provides for use beyond one course, and files a tool used inside one course as a pilot. We print both. '
          'We chose the institutions ourselves, in batches. Research universities came first, then other doctoral universities, then liberal arts colleges, '
          'plus one small private university added for a published study. They are not a random sample and not every college. '
          f'The list has {NROWS} rows, one of them ours. The counts below are out of {NROWS} rows and include our own. The two rule counts are out of the {NREAD} rows that were read, because a school that was not reached is listed apart. {R13["line"]}</p></section>')
CHAT = F.table(["Institution", "Document", "Text", "Source"], [(i, d, q, F.A(u)) for i, d, q, u in F.CHATBOT])
body = f'''
{METHOD}
<section><h2>Chatbot cited as a source in official publications.</h2>{CHAT}</section>
<section><h2>Table of findings</h2><div class="scroll"><table class="mtx"><thead><tr><th>Finding</th><th class="n">Rows</th><th>Which</th></tr></thead><tbody>{ft_rows}</tbody></table></div></section>
<section><h2>The list</h2>
<p class="meta">Read {AS_OF}. None found means we looked and found nothing. Not reached means the pages refused our reader or needed a login. Not looked for yet means we have not looked. First document cited is the first link in our notes on the institution&rsquo;s AI documents. It is not a judgement that the document is a policy.</p>
<div class="scroll"><table class="mtx"><thead><tr><th>Institution</th><th>First document cited</th><th>Measures its own AI policy</th><th>Released its own AI data</th><th>Pilot results read</th></tr></thead>
<tbody>
{trs}
</tbody></table></div></section>
'''
EXTRA = '''<style>.mtx{border-collapse:collapse;width:100%;font-size:15px;line-height:1.45}.mtx th{text-align:left;font-family:Cinzel,Georgia,serif;letter-spacing:.08em;font-size:13px;color:var(--mid);border-bottom:2px solid var(--ink);padding:8px 10px}
.mtx td{border-bottom:1px solid #e6dac0;padding:9px 10px;vertical-align:top}.mtx td:first-child{font-weight:600}.mtx .n{text-align:right}.mtx.small{max-width:520px}
.scroll{overflow-x:auto}.idx{display:flex;gap:12px;margin:0 0 24px;max-width:720px}.idx input[name=url]{flex:1;font:400 17px/1.4 Lora,Georgia,serif;color:var(--ink);background:#fffaf0;border:1px solid #c9b994;border-radius:2px;padding:11px 12px}.idx .btn{border:0;cursor:pointer}.hold{color:#9a2b1e;font-family:Cinzel,Georgia,serif;font-size:12px;letter-spacing:.06em}.mtx .srckind{font-weight:400;font-size:13px;color:var(--mid)}</style>'''
if bs:
    doc = bs.page('/oy/matrix', 'Recount Matrix: Learning Research | OY | Indahl',
                  'Working draft: what United States institutions have published about measuring their own policies on AI in teaching and learning, with a source for every row.',
                  body, bs.hero('OY', 'Recount Matrix: Learning Research', ''))
    doc = doc.replace('</head>', EXTRA + '\n</head>').replace('href="/style.css"', 'href="style.css"')
    out = B + 'matrix_page/staged/'
    open(out + 'learning-matrix.html', 'w', encoding='utf-8').write(doc); open(out + 'style.css', 'w').write(bs.CSS)
open(B + 'matrix_page/oy_body.html', 'w', encoding='utf-8').write(EXTRA + '\n' + body)   # build_site.py reads this for /oy
# 10 Nov 2026: the headline is built with the page from the same counts, so the page, the headline feed and the data pack say the same thing.
N_CHAT = len(set(i for i, d, q, u in F.CHATBOT))
HL = {'big': f'{len(ORIG)} of {NREAD}',
      'line': (f'listed colleges and universities had published a measured grade or learning outcome of their own AI policy, guidance, tool or pilot, by the rule we wrote before reading any school. '
               f'By a narrower rule we set after the first 41 schools were read, which counts only a policy, guidance or a tool a central office provides, {NPOL} of {NREAD} had. '
               f'We read each school on {AS_OF}, and on 10 November 2026 we read again in a browser {len(REREAD)} schools whose pages had refused our reader. The {NROWS} rows include our own, and the shares are out of the {NREAD} rows that were read. For {len(UNR)} school{"" if len(UNR) == 1 else "s"} the pages need a login, and {"it is" if len(UNR) == 1 else "they are"} listed apart as not reached. {R13["line"]} '
               f'{N_CHAT} cite a chatbot as a source in official documents.'),
      'req13': R13, 'counts': {'read': NREAD, 'original_rule': len(ORIG), 'policy_rule_learning': len(LPOL), 'policy_rule_cannot_tell': len(LPOL_CT), 'unreached': len(UNR), 'rows': NROWS, **{k: count_[k] for k in LV}}}
assert ';' not in HL['line']
_json.dump(HL, open(B + 'matrix_page/oy_headline.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('rows', len(rows), count_, 'original rule', len(ORIG), 'policy rule learning', NPOL, 'unreached', len(UNR), 'no source:', [r['slug'] for r in rows if not r['src']])
