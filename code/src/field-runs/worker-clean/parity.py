"""Parity crawl: the same URLs against two bases; compare status, redirect target, content type and body sha256. Usage: parity.py BASE_A BASE_B OUT.json"""
import hashlib, json, re, sys, urllib.request, urllib.error, concurrent.futures as cf
A, B, OUT = sys.argv[1:4]
M = '/Users/heuremen/bones-forge/public_mirror/indahl.ai'
paths = sorted({re.sub(r'^https://indahl\.ai', '', u) or '/' for u in re.findall(r'<loc>([^<]+)</loc>', urllib.request.urlopen(A + '/sitemap.xml', timeout=60).read().decode())})
paths += ['/', '/contact', '/connect', '/robots.txt', '/llms.txt', '/favicon.svg', '/sitemap.xml', '/r', '/las-fallas.pdf', '/faults.pdf', '/no-such-page-x', '/mcp', '/mcp/research', '/api/']
class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NoRedir)
def get(base, p, post=None):
    req = urllib.request.Request(base + p, data=post, headers={'content-type': 'application/json', 'accept': 'application/json, text/event-stream'} if post else {})
    try: r = op.open(req, timeout=60); return r.status, r.headers.get('location'), r.headers.get('content-type'), r.read()
    except urllib.error.HTTPError as e: return e.code, e.headers.get('location'), e.headers.get('content-type'), e.read()
    except Exception as e: return None, None, None, str(e).encode()
INIT = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'parity', 'version': '1'}}}).encode()
jobs = [(p, None) for p in dict.fromkeys(paths)] + [(p, INIT) for p in ('/mcp', '/mcp/research', '/mcp/models')]
def one(j):
    p, post = j; a, b = get(A, p, post), get(B, p, post)
    norm = lambda x: re.sub(rb'"(t|at|time|now|signed_at|ts)":\s*"?[0-9T:.\-Z]+"?', b'', x)   # live clocks in JSON bodies
    ka = (a[0], a[1], a[2], hashlib.sha256(norm(a[3])).hexdigest()); kb = (b[0], b[1], b[2], hashlib.sha256(norm(b[3])).hexdigest())
    return dict(path=p, method='POST' if post else 'GET', same=ka == kb, a=ka[:3], b=kb[:3], body_same=ka[3] == kb[3])
with cf.ThreadPoolExecutor(8) as ex: rows = list(ex.map(one, jobs))
bad = [r for r in rows if not r['same']]
json.dump(dict(a=A, b=B, checked=len(rows), mismatches=bad), open(OUT, 'w'), indent=1)
print('parity %s vs %s: %d checked, %d mismatches' % (A, B, len(rows), len(bad)))
for r in bad[:15]: print('  ', r['method'], r['path'], r['a'], '|', r['b'], 'body same' if r['body_same'] else 'body differs')
sys.exit(1 if bad else 0)
