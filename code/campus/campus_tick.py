#!/usr/bin/env python3
"""campus_tick.py: CAMPUS per PLAN.md. Every external source on the OY page, read and kept pass after pass."""
import os, sys, re, json, time, html, hashlib, io, threading, http.server, socketserver, subprocess, urllib.request, urllib.error, urllib.parse, collections
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data/text', exist_ok=True)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('campus: plan not committed'); sys.exit(0)
import pypdf, fcntl
_l = open('data/.lock', 'w')
try: fcntl.flock(_l, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError: print('campus: another run holds the lock'); sys.exit(0)
UA = {'User-Agent': 'heuremen-campus/0.1 (+https://indahl.ai/campus)'}; W = os.path.expanduser('~/bones-forge/cloudflare-workers/heuremen-door')
OWN = ('indahl.ai', 'heuremen.org')
def get(u, n=3, to=30):
    """-> (status, final_url, ctype, body bytes). status None = no connection."""
    for i in range(n):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=to); return r.status, r.geturl(), r.headers.get('Content-Type', ''), r.read(6000000)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < n - 1: time.sleep(4 * (i + 1)); continue
            return e.code, u, (e.headers.get('Content-Type', '') if e.headers else ''), b''
        except Exception: time.sleep(2 * (i + 1))
    return None, u, '', b''
def extract_links(page):
    """-> {url: [institution, ...]}; institution = first cell of the table row, else nearest heading."""
    out = {}; pos = 0; heading = ''
    for m in re.finditer(r'<h[1-4][^>]*>(.*?)</h[1-4]>|<tr[^>]*>(.*?)</tr>|<a [^>]*href="(https?://[^"]+)"', page, flags=re.S):
        if m.group(1) is not None: heading = html.unescape(re.sub(r'<[^>]+>', ' ', m.group(1))).strip()
        elif m.group(2) is not None:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', m.group(2), flags=re.S); inst = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', cells[0] if cells else ''))).strip()
            for u in re.findall(r'href="(https?://[^"]+)"', m.group(2)):
                h = urllib.parse.urlparse(html.unescape(u)).hostname or ''
                if not any(h == o or h.endswith('.' + o) for o in OWN): out.setdefault(html.unescape(u), set()).add(inst or heading)
    for m in re.finditer(r'<a [^>]*href="(https?://[^"]+)"', page):   # links outside rows
        u = html.unescape(m.group(1)); h = urllib.parse.urlparse(u).hostname or ''
        if not any(h == o or h.endswith('.' + o) for o in OWN) and u not in out: out[u] = {heading}
    return {u: sorted(x for x in v if x) for u, v in out.items()}
class TextOf(html.parser.HTMLParser if hasattr(html, 'parser') else object): pass
import html.parser
class TextOf(html.parser.HTMLParser):
    def __init__(s): super().__init__(); s.skip = 0; s.out = []
    def handle_starttag(s, t, a):
        if t in ('script', 'style', 'noscript', 'template'): s.skip += 1
    def handle_endtag(s, t):
        if t in ('script', 'style', 'noscript', 'template') and s.skip: s.skip -= 1
    def handle_data(s, d):
        if not s.skip: s.out.append(d)
def words_of(body, ctype, url):
    kind = 'pdf' if (body[:4] == b'%PDF' or 'pdf' in ctype.lower() or url.lower().split('?')[0].endswith('.pdf')) else ('html' if ('html' in ctype.lower() or body[:200].lstrip().lower().startswith((b'<!doctype', b'<html'))) else 'other')
    if kind == 'pdf':
        try: t = '\n'.join((p.extract_text() or '') for p in pypdf.PdfReader(io.BytesIO(body)).pages)
        except Exception: t = ''
    elif kind == 'html':
        p = TextOf()
        try: p.feed(body.decode('utf-8', 'replace'))
        except Exception: pass
        t = ' '.join(p.out)
    else: t = ''
    return kind, re.findall(r"[a-z0-9']+", t.lower())
def shingles(w): return {' '.join(w[i:i + 3]) for i in range(len(w) - 2)}
def overlap(a, b):
    A, B = shingles(a), shingles(b); return len(A & B) / len(A | B) if A | B else 0.0
def pair_class(prev, cur, pw, cw):
    """prev, cur: dicts(status, final, nwords); pw, cw: word lists. -> class"""
    if cur['status'] in (401, 403, 429): return 'BLOCKED'
    if cur['status'] in (404, 410): return 'GONE' if prev.get('status') == 200 else 'ERROR'
    if cur['status'] is None: return 'GONE' if prev.get('status') is None else 'ERROR'
    if cur['status'] != 200: return 'ERROR'
    if prev.get('status') != 200: return 'ERROR'
    if len(pw) >= 30 and len(cw) >= 30: return 'SAME' if overlap(pw, cw) >= 0.90 else 'CHANGED'
    return 'SAME' if prev.get('size') == cur.get('size') else 'CHANGED'
# ---- known-good
class Fix(http.server.BaseHTTPRequestHandler):
    pages = {}
    def do_GET(s):
        st, body = Fix.pages.get(s.path, (404, b'')); s.send_response(st); s.send_header('Content-Type', 'text/html'); s.end_headers(); s.wfile.write(body)
    def log_message(s, *a): pass
def gate():
    base = ' '.join('word%d alpha beta gamma' % i for i in range(60)); w = re.findall(r"[a-z0-9']+", base)
    w2 = w[:]
    for i in range(0, len(w2), 80): w2[i] = 'changedword%d' % i
    ok = overlap(w, w) == 1.0 and overlap(w, re.findall(r"[a-z0-9']+", ' '.join('zebra%d quokka llama' % i for i in range(60)))) < 0.05 and 0.90 <= overlap(w, w2) < 1.0
    srv = socketserver.TCPServer(('127.0.0.1', 0), Fix); port = srv.server_address[1]; threading.Thread(target=srv.serve_forever, daemon=True).start()
    u = 'http://127.0.0.1:%d/p' % port; Fix.pages['/p'] = (200, ('<html><body>' + base + '</body></html>').encode())
    def rd(): st, fin, ct, b = get(u, n=1, to=5); k, wd = words_of(b, ct, u); return dict(status=st, final=fin, size=len(b), nwords=len(wd)), wd
    a, aw = rd(); Fix.pages['/p'] = (200, ('<html><body>' + base + '</body></html>').encode()); b_, bw = rd(); ok &= pair_class(a, b_, aw, bw) == 'SAME'
    Fix.pages['/p'] = (200, ('<html><body>' + ' '.join('zebra%d quokka llama' % i for i in range(60)) + '</body></html>').encode()); c, cw = rd(); ok &= pair_class(b_, c, bw, cw) == 'CHANGED'
    Fix.pages['/p'] = (404, b''); d, dw = rd(); ok &= pair_class(c, d, cw, dw) == 'GONE'
    Fix.pages['/p'] = (403, b''); e, ew = rd(); ok &= pair_class(c, e, cw, ew) == 'BLOCKED'
    srv.shutdown()
    page = '<h2>Heading A</h2><table><tr><td>School One</td><td><a href="https://one.example.edu/ai-policy">x</a></td></tr><tr><td>School Two</td><td><a href="https://indahl.ai/qia">y</a><a href="https://two.example.edu/p.pdf">z</a></td></tr></table><a href="https://heuremen.org/x">h</a>'
    L = extract_links(page); ok &= set(L) == {'https://one.example.edu/ai-policy', 'https://two.example.edu/p.pdf'} and L['https://one.example.edu/ai-policy'] == ['School One']
    print('campus: gate', 'passed' if ok else 'FAILED', flush=True); return bool(ok)
if not gate(): sys.exit(1)
# ---- read
now = time.time(); stamp = time.strftime('%Y%m%dT%H%M', time.gmtime(now))
st0, _, _, pb = get('https://indahl.ai/oy?x=%d' % now)
if st0 != 200: print('campus: OY page not read'); sys.exit(1)
links = extract_links(pb.decode('utf8', 'replace')); print('campus: external sources', len(links), flush=True)
reads = [json.loads(l) for l in open('data/reads.jsonl')] if os.path.exists('data/reads.jsonl') else []
prev = reads[-1]['items'] if reads else {}; items = {}; pairs = {}; lasthost = {}
for i, (u, insts) in enumerate(sorted(links.items())):
    host = urllib.parse.urlparse(u).hostname or ''
    wait = 0.5 - (time.time() - lasthost.get(host, 0))
    if wait > 0: time.sleep(wait)
    st, fin, ct, body = get(u); lasthost[host] = time.time(); time.sleep(0.5)
    kind, wd = words_of(body, ct, fin) if st == 200 else ('other', [])
    it = dict(status=st, final=fin, ctype=ct.split(';')[0], size=len(body), kind=kind, nwords=len(wd), institutions=insts); items[u] = it
    tf = 'data/text/' + hashlib.sha256(u.encode()).hexdigest() + '.txt'
    if u in prev:
        pw = open(tf).read().split() if os.path.exists(tf) else []
        pc = pair_class(prev[u], it, pw, wd); moved = bool(st == 200 and prev[u].get('final') and fin != prev[u]['final'])
        pairs[u] = dict(cls=pc, moved=moved, overlap=round(overlap(pw, wd), 3) if len(pw) >= 30 and len(wd) >= 30 else None)
    if st == 200 and wd: open(tf, 'w').write(' '.join(wd))
    if i % 50 == 49: print('campus: read', i + 1, 'of', len(links), flush=True)
open('data/reads.jsonl', 'a').write(json.dumps(dict(t=now, stamp=stamp, items=items, pairs=pairs)) + '\n')
# ---- summary
passno = len(reads) + 1
def stnow(it):
    s = it['status']
    if s == 200: return 'resolves'
    if s in (401, 403, 429): return 'blocked'
    if s in (404, 410): return 'gone'
    return 'error'
now_c = collections.Counter(stnow(v) for v in items.values()); moved = sum(1 for v in pairs.values() if v['moved'])
pc = collections.Counter(v['cls'] for v in pairs.values())
hc = json.load(open('data/hand_checked.json')) if os.path.exists('data/hand_checked.json') else {}
listed = [dict(source=u, school=', '.join(items[u]['institutions'])[:80], found=pairs[u]['cls'], overlap=pairs[u]['overlap'], note=hc[u]) for u in pairs if u in hc]
await_ = len([u for u, v in pairs.items() if (v['cls'] == 'GONE' or (v['cls'] == 'CHANGED' and (v['overlap'] is None or v['overlap'] < 0.5))) and u not in hc])
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime(now)), gate='passed', pass_number=passno, sources=len(links), institutions=len({x for v in items.values() for x in v['institutions']}),
           state_now={'Opens (HTTP 200)': now_c['resolves'], 'Blocked (401, 403, 429)': now_c['blocked'], 'Not found (404, 410)': now_c['gone'], 'Other error or no answer': now_c['error']},
           since_previous=({'Same text': pc['SAME'], 'Text changed': pc['CHANGED'], 'Moved address (resolves)': moved, 'Gone': pc['GONE'], 'Blocked': pc['BLOCKED'], 'Error': pc['ERROR']} if pairs else None),
           first_pass=(passno == 1), awaiting_hand_check=await_, listed=listed)
json.dump(out, open('summary_campus.json', 'w'), indent=1)
env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
pr = subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', 'campus_live', '--path', os.path.join(H, 'summary_campus.json'), '--namespace-id', 'ecb59d96b07c43bdac14271687eae5af', '--remote'], cwd=W, env=env, capture_output=True, text=True)
with open('history.jsonl', 'a') as f: f.write(json.dumps(dict(t=out['updated'], pass_number=passno, sources=len(links), opens=now_c['resolves'], gone=now_c['gone'], blocked=now_c['blocked'], error=now_c['error'], changed=pc['CHANGED'])) + '\n')
print('campus: pass', passno, dict(now_c), dict(pc), 'published' if pr.returncode == 0 else 'publish FAILED ' + (pr.stderr or pr.stdout)[-200:], flush=True)
