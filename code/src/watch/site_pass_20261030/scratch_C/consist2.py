import re, json, glob, os, html, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parse as P
B = os.path.expanduser('~/bones-forge/qia_leads/matrix_page/')
book = json.load(open(B + 'book_calibrated.json'))
pages = {os.path.basename(f)[:-5]: P.parse(f) for f in sorted(glob.glob('pages/*.html'))}
def norm_id(s): return s.replace(':', '-') if s else None
bymap = {}
for r in book:
    for k in (r['study_id'], r.get('also')):
        if k: bymap.setdefault(norm_id(k), []).append(r)
bymap['ibm-qaoa-tutorial-ibm-quantum-documentation-run-'] = [r for r in book if r['id'] == 'ibm_qaoa_tutorial']
def T(h): return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', h)).split())
def N(s):
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('–', '-').replace('—', '-')
    return re.sub(r'\s+', ' ', s).strip()
diff = collections.defaultdict(list)
for n, p in pages.items():
    r = bymap[n][0]
    s = p['sections']
    pg = {'org': T(re.search(r'<b>(.*?)</b>', s['Work'], re.S).group(1)),
          'published': T(s['Published']), 'measured': T(s['Measured or recounted']), 'how': T(re.sub(r'<p class="meta">.*', '', s['How'], flags=re.S)),
          'cal': T(s['QIA Calibration'])}
    cal_txt = pg['cal']
    # strip leading codes
    codes = re.findall(r'class="code"[^>]*>([^<]+)<', s['QIA Calibration'])
    for c in codes:
        cal_txt = cal_txt.replace(c, '', 1).strip()
    exp = {'org': r['organisation'], 'published': r['published'], 'measured': r['measured'], 'how': r['how'], 'cal': r['qia_calibration']}
    for k in exp:
        a, b = N(pg[k] if k != 'cal' else cal_txt), N(html.unescape(re.sub(r'^(?:[FQ]\d+\s+)+','',exp[k]) if k=='cal' else exp[k]))
        if a != b:
            diff[k].append((n, r['id'], a, b))
for k, v in diff.items():
    print('FIELD', k, len(v))
    for n, i, a, b in v[:200]:
        print('  ', n, i)
        print('     page:', a[:300])
        print('     book:', b[:300])
