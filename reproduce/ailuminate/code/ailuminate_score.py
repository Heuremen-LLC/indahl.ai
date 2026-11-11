"""ailuminate_score.py: the scoring of ailuminate_index/ailuminate_tick.py on its newest read, offline. CATS, ordinal(), ord_str(), parse_page(),
parse_pdf() and pdf_text() are copied from the tick as written, and the rows, table and test A follow its lines for rows, cmp, oc() and A. The
newest read is the last line of data/reads.jsonl. Its folder data/raw/<stamp>/ holds the results page and every Detailed Results PDF as read, and
each PDF is matched to its system by the sha256 the read recorded. Writes out.json."""
import os as _o, sys as _s; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import os, re, io, json, html, hashlib, glob
import pypdf
import heuremen_kit as K
CATS = ['Violent Crimes', 'Sex-Related Crimes', 'Child Sexual Exploitation', 'Suicide and Self-Harm', 'Indiscriminate Weapons', 'Intellectual Property', 'Defamation', 'Non-Violent Crimes', 'Hate', 'Privacy', 'Specialized Advice', 'Sexual Content']
def ordinal(s):
    m = re.fullmatch(r'\s*(\d+)(st|nd|rd|th)\s*', s)
    if not m: return None
    n = int(m.group(1)); suf = 'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return n if suf == m.group(2) else None
def ord_str(n): return '%d%s' % (n, 'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))
def parse_page(htmltext):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', htmltext, flags=re.S); t = re.sub(r'<[^>]+>', '\n', t); t = html.unescape(re.sub(r'\n\s*\n+', '\n', t))
    g = t.find('Guardrail systems'); out = {}
    for m in re.finditer(r'\n([^\n]+)\nReleased ([A-Z][a-z]+ \d{4})\n(\d+(?:st|nd|rd|th)) percentile', t):
        out[m.group(1).strip()] = dict(type='Guardrail system' if g >= 0 and m.start() > g else 'Open-weight model', release=m.group(2), overall=ordinal(m.group(3)))
    return out
def parse_pdf(text):
    """-> dict(name, release, type, overall, cats) or None"""
    nm = re.search(r'ENGLISH \(US\)\s*\n(.+?)\s*\nOfficial result', text); rel = re.search(r'RELEASED\s+([A-Z][a-z]+ \d{4})', text); ty = re.search(r'SYSTEM TYPE\s+(.+)', text)
    ov = re.search(r'All Hazard Categories\s+(\d+(?:st|nd|rd|th)) percentile', text); cats = {}
    for c in CATS:
        m = re.search(re.escape(c) + r'\s+(\d+(?:st|nd|rd|th)) percentile', text)
        if m and ordinal(m.group(1)) is not None: cats[c] = ordinal(m.group(1))
    if not (nm and rel and ov and ordinal(ov.group(1)) is not None) or len(cats) != 12: return None
    return dict(name=nm.group(1).strip(), release=rel.group(1), type=(ty.group(1).strip() if ty else None), overall=ordinal(ov.group(1)), cats=cats)
def pdf_text(b):
    r = pypdf.PdfReader(io.BytesIO(b)); return '\n'.join((p.extract_text() or '') for p in r.pages)

last = None
for l in open('data/reads.jsonl'):
    if l.strip(): last = json.loads(l)
rawd = 'data/raw/' + last['stamp']
pb = open(rawd + '/page.html', 'rb').read()
if hashlib.sha256(pb).hexdigest() != last['hashes']['page.html']: _s.exit('page.html is not the page the read recorded')
page = parse_page(pb.decode('utf8', 'replace'))
by_sha = {hashlib.sha256(open(f, 'rb').read()).hexdigest(): f for f in glob.glob(rawd + '/*.pdf')}
systems = {}
for name, h in last['hashes'].items():
    if name == 'page.html': continue
    f = by_sha.get(h)
    if f is None: _s.exit('no PDF in the read folder has the sha256 recorded for ' + name)
    try: p = parse_pdf(pdf_text(open(f, 'rb').read()))
    except Exception: p = None
    if p: systems[name] = p
rows = []
for name in sorted(set(page) | set(systems)):
    pg, pd = page.get(name), systems.get(name)
    if not pg or not pd: rows.append(dict(name=name, cls='NOTHING_RETURNED')); continue
    dis = [k for k, a, b in (('overall', pg['overall'], pd['overall']), ('release', pg['release'], pd['release']), ('type', pg['type'], pd['type'])) if a != b]
    rows.append(dict(name=name, cls='DISAGREE' if dis else 'AGREE', overall_pdf=pd['overall']))
cmp = [r for r in rows if r['cls'] in ('AGREE', 'DISAGREE')]; nd = sum(1 for r in cmp if r['cls'] == 'DISAGREE'); lo, hi = K.wilson(nd, len(cmp)) if cmp else (0, 1)
def oc(lo, hi): return K.ABOVE if lo > 0.05 else (K.CONSISTENT if hi < 0.15 else K.CANNOT_TELL)
A = dict(of=len(cmp), n=nd, share=round(nd / len(cmp), 4) if cmp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc(lo, hi) if cmp else 'NOTHING_RETURNED')
json.dump(dict(read=last['stamp'], headline=A, table={r['name']: dict(overall=r['overall_pdf'], agree=r['cls']) for r in cmp}), open('out.json', 'w'), indent=1)
