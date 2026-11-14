"""Snapshot or compare the live site. snap.py take OUT.json | snap.py compare BEFORE.json AFTER.json | snap.py plant BEFORE.json PLANTED.json"""
import hashlib, json, re, sys, urllib.request, urllib.error, concurrent.futures as cf
sys.argv += [''] * 3
cmd, a1, a2 = sys.argv[1:4]
BASE = 'https://indahl.ai'
class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NoRedir)
INIT = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'snap', 'version': '1'}}}).encode()
def get(p, post=None):
    req = urllib.request.Request(BASE + p, data=post, headers=dict({'user-agent': 'heuremen-field-run/1'}, **({'content-type': 'application/json', 'accept': 'application/json, text/event-stream'} if post else {})))
    try: r = op.open(req, timeout=60); return r.status, r.headers.get('location'), r.headers.get('content-type'), r.read()
    except urllib.error.HTTPError as e: return e.code, e.headers.get('location'), e.headers.get('content-type'), e.read()
    except Exception as e: return None, None, None, str(e).encode()
norm = lambda x: re.sub(rb'"(t|at|time|now|signed_at|ts|generated|updated)":\s*"?[0-9T:.\-Z ]+"?', b'', x)
if cmd == 'take':
    paths = sorted({re.sub(r'^https://indahl\.ai', '', u) or '/' for u in re.findall(r'<loc>([^<]+)</loc>', get('/sitemap.xml')[3].decode())})
    paths += ['/', '/contact', '/connect', '/robots.txt', '/llms.txt', '/favicon.svg', '/r', '/las-fallas.pdf', '/no-such-page-x', '/mcp', '/api/']
    jobs = [(p, None) for p in dict.fromkeys(paths)] + [(p, INIT) for p in ('/mcp', '/mcp/research', '/mcp/models')]
    def one(j):
        s, loc, ct, body = get(*j); return dict(path=j[0], method='POST' if j[1] else 'GET', status=s, location=loc, ctype=ct, sha=hashlib.sha256(norm(body)).hexdigest())
    with cf.ThreadPoolExecutor(6) as ex: rows = list(ex.map(one, jobs))
    json.dump(rows, open(a1, 'w')); print('snapshot: %d urls, %d not 2xx/3xx' % (len(rows), sum(1 for r in rows if not r['status'] or r['status'] >= 400)))
elif cmd in ('compare', 'plant'):
    A = {(r['method'], r['path']): r for r in json.load(open(a1))}; B = {(r['method'], r['path']): r for r in json.load(open(a2))}
    bad = [k for k in A if k in B and (A[k]['status'], A[k]['location'], A[k]['ctype'], A[k]['sha']) != (B[k]['status'], B[k]['location'], B[k]['ctype'], B[k]['sha'])]
    print('compare: %d urls, %d differ' % (len(A), len(bad)))
    for k in bad[:20]: print('  ', k, A[k]['status'], '->', B[k]['status'])
    sys.exit(1 if bad else 0)
