#!/usr/bin/env python3
"""ailuminate_tick.py: AILUMINATE per PLAN.md. Reads the AILuminate Safety results page and the Detailed Results PDF of each system, keeps every read."""
import os, sys, re, json, time, html, hashlib, subprocess, urllib.request, urllib.error, statistics, random, io, datetime
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data/raw', exist_ok=True)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('ailuminate: plan not committed'); sys.exit(0)
import pypdf
PAGE = 'https://mlcommons.org/ailuminate/safety/results/'; FOLDER = '1hRjh2gALmmlpNMIDuoASBKMHUO7V0T95'
CATS = ['Violent Crimes', 'Sex-Related Crimes', 'Child Sexual Exploitation', 'Suicide and Self-Harm', 'Indiscriminate Weapons', 'Intellectual Property', 'Defamation', 'Non-Violent Crimes', 'Hate', 'Privacy', 'Specialized Advice', 'Sexual Content']
UA = {'User-Agent': 'heuremen-ailuminate/0.1 (+https://indahl.ai/ailuminate)'}; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
def fetch(u, n=3, to=60):
    for i in range(n):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=to).read()
        except Exception: time.sleep(3 * (i + 1))
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
# ---- known-good
def gate():
    ok = all(ordinal(a) == v for a, v in (('1st', 1), ('2nd', 2), ('3rd', 3), ('11th', 11), ('12th', 12), ('13th', 13), ('21st', 21), ('100th', 100)))
    ok &= ordinal('11st') is None and ordinal('2th') is None
    rows = ''.join('%s %s percentile\n' % (c, ord_str(50 + i)) for i, c in enumerate(CATS))
    good = 'AILUMINATE ™ SAFETY 1.2.1 · OFFICIAL DETAILED RESULTS · ENGLISH (US)  \nTest System X\nOfficial result · published October 29, 2026\nSYSTEM  Test System X RELEASED  May 2026\nSYSTEM TYPE  Open-weight model\nAll Hazard Categories 77th percentile\n' + rows
    p = parse_pdf(good); ok &= bool(p and p['overall'] == 77 and p['cats']['Hate'] == 58 and p['name'] == 'Test System X' and p['release'] == 'May 2026')
    ok &= parse_pdf(good.replace('Hate 58th percentile\n', '')) is None
    pg = parse_page('<h2>Open-weight models</h2><p>Name</p>\n<p>Alpha</p>\n<p>Released June 2025</p>\n<p>86th percentile</p><h2>Guardrail systems</h2><p>Beta</p>\n<p>Released May 2024</p>\n<p>100th percentile</p>')
    ok &= pg == {'Alpha': dict(type='Open-weight model', release='June 2025', overall=86), 'Beta': dict(type='Guardrail system', release='May 2024', overall=100)}
    print('ailuminate: gate', 'passed' if ok else 'FAILED', flush=True); return bool(ok)
if not gate(): sys.exit(1)
# ---- read
now = time.time(); stamp = time.strftime('%Y%m%dT%H%M', time.gmtime(now)); rawd = 'data/raw/' + stamp; os.makedirs(rawd, exist_ok=True)
pb = fetch(PAGE)
if not pb: print('ailuminate: results page not read'); sys.exit(1)
open(rawd + '/page.html', 'wb').write(pb); hashes = {'page.html': hashlib.sha256(pb).hexdigest()}
page = parse_page(pb.decode('utf8', 'replace')); print('ailuminate: page systems', len(page), flush=True)
fb = fetch('https://drive.google.com/embeddedfolderview?id=' + FOLDER)
items = re.findall(r'<a href="https://drive\.google\.com/file/d/([^/]+)/view[^"]*"[^>]*>.*?<div class="flip-entry-title">(.*?)</div>', (fb or b'').decode('utf8', 'replace'), flags=re.S)
systems = {}; unread = []
for fid, title in items:
    title = html.unescape(title); m = re.match(r'\d+ - (.+?) - AILuminate Safety', title)
    name = m.group(1) if m else title; b = fetch('https://drive.google.com/uc?export=download&id=' + fid, to=120); time.sleep(1)
    if not b or b[:4] != b'%PDF': unread.append(name); continue
    open(rawd + '/%s.pdf' % re.sub(r'[^A-Za-z0-9]+', '_', name), 'wb').write(b); hashes[name] = hashlib.sha256(b).hexdigest()
    try: p = parse_pdf(pdf_text(b))
    except Exception: p = None
    if not p: unread.append(name); continue
    systems[name] = p
print('ailuminate: reports parsed', len(systems), 'unread', len(unread), flush=True)
rows = []
for name in sorted(set(page) | set(systems)):
    pg, pd = page.get(name), systems.get(name)
    if not pg or not pd: rows.append(dict(name=name, cls='NOTHING_RETURNED', why='on the page only' if pg and not pd else 'report only')); continue
    dis = [k for k, a, b in (('overall', pg['overall'], pd['overall']), ('release', pg['release'], pd['release']), ('type', pg['type'], pd['type'])) if a != b]
    cats = pd['cats']; mean = sum(cats.values()) / 12
    rows.append(dict(name=name, cls='DISAGREE' if dis else 'AGREE', differs=dis, type=pd['type'], release=pd['release'], overall_page=pg['overall'], overall_pdf=pd['overall'], mean_cats=round(mean, 1), diff=round(pd['overall'] - mean, 1), min_cat=min(cats.values()), max_cat=max(cats.values()), cats=cats))
open('data/reads.jsonl', 'a').write(json.dumps(dict(t=now, stamp=stamp, hashes=hashes, systems={r['name']: dict(release=r.get('release'), overall=r.get('overall_pdf'), cats=r.get('cats')) for r in rows if r['cls'] != 'NOTHING_RETURNED'}, unread=unread)) + '\n')
reads = [json.loads(l) for l in open('data/reads.jsonl')]
cmp = [r for r in rows if r['cls'] in ('AGREE', 'DISAGREE')]; nd = sum(1 for r in cmp if r['cls'] == 'DISAGREE'); lo, hi = K.wilson(nd, len(cmp)) if cmp else (0, 1)
def oc(lo, hi): return K.ABOVE if lo > 0.05 else (K.CONSISTENT if hi < 0.15 else K.CANNOT_TELL)
A = dict(of=len(cmp), n=nd, share=round(nd / len(cmp), 4) if cmp else None, share_lo=round(lo, 4), share_hi=round(hi, 4), outcome=oc(lo, hi) if cmp else 'NOTHING_RETURNED')
first = {}
for rd in reads:
    for n, v in rd['systems'].items(): first.setdefault(n, (v, rd['stamp'], 0))
count = {}
for rd in reads:
    for n in rd['systems']: count[n] = count.get(n, 0) + 1
chg = []; seen2 = []
for n, v in reads[-1]['systems'].items():
    if count.get(n, 0) >= 2:
        seen2.append(n)
        if v != first[n][0]: chg.append(n)
lo2, hi2 = K.wilson(len(chg), len(seen2)) if seen2 else (0, 1)
B = dict(of=len(seen2), n=len(chg), share=round(len(chg) / len(seen2), 4) if seen2 else None, share_lo=round(lo2, 4), share_hi=round(hi2, 4), outcome=oc(lo2, hi2) if seen2 else 'NOTHING_RETURNED', reads=len(reads), first_read=reads[0]['stamp'], changed=sorted(chg))
rs = sorted([r for r in rows if r['cls'] == 'DISAGREE'] + [], key=lambda r: r['name'])
samp = random.Random(7).sample([r['name'] for r in cmp], min(10, len(cmp))) if cmp else []
json.dump(dict(sample_seed7=samp, disagree=[r['name'] for r in rs], unread=unread), open('data/hand_check.json', 'w'), indent=1)
hc = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), gate='passed', systems_on_page=len(page), reports_parsed=len(systems), reports_not_read=len(unread), reads=len(reads), headline=A, headline_n=A['n'], headline_of=A['of'],
           stability=B, awaiting_hand_check=len([r for r in rs if r['name'] not in hc]),
           table={r['name']: dict(type=r['type'], release=r['release'], overall=r['overall_pdf'], mean_cats=r['mean_cats'], diff=r['diff'], lowest=r['min_cat'], highest=r['max_cat'], agree=r['cls']) for r in cmp},
           disagree_list=[dict(system=r['name'], differs=', '.join(r['differs']), note=hc.get(r['name'])) for r in rs if r['name'] in hc])
json.dump(out, open('summary_ailuminate.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'ailuminate_live', '--path', os.path.join(H, 'summary_ailuminate.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
print('ailuminate: A', A, '| B', {k: B[k] for k in ('of', 'n', 'outcome', 'reads')}, 'published' if pr.returncode == 0 else 'publish FAILED', flush=True)
