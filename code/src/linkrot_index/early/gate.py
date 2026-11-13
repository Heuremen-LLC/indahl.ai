#!/usr/bin/env python3
"""gate.py: the known-good gate for the LINKROT broader samples (PLAN.md Addendum 3). Run before every pass. If any self-test or
control reads wrong, the pass checks nothing and the summary says the instrument failed its gate.

Self-tests (offline): registered domains, robots.txt matching (RFC 9309, with * and $), every detector signal and its guard against
look-alike names, the similarity rule. Controls (each must read exactly its state):
  LIVE_SAME             https://www.rfc-editor.org/rfc/rfc1149.txt  (an RFC text, fixed since its earliest capture)
  LIVE_CHANGED          https://www.python.org/
  LIVE_NO_BASELINE      https://example.com/?linkrot-control-7q2  (a query never captured)
  REDIRECTED_ELSEWHERE  http://www.ietf.org/rfc/rfc1149.txt  (ends on rfc-editor.org)
  DEAD_DNS              http://made-up-host-7q2.invalid/
  DEAD_HTTP             https://example.com/no-such-page-7q2
  DEAD_CONNECT          a closed local port
  TIMEOUT               a local listener that accepts and never answers
  ROBOTS_DISALLOWED     a local server whose robots.txt disallows every reader
  PARKED_OR_FOR_SALE    a local server whose page says the domain is for sale
  NOTHING_RETURNED      the resolver services forced unreachable
Run `python3 -I gate.py` to see each reading."""
import os, sys, socket, threading, time, http.server
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import linkstate as L

LIVE_CONTROLS = [('https://www.rfc-editor.org/rfc/rfc1149.txt', 'LIVE_SAME'), ('https://www.python.org/', 'LIVE_CHANGED'),
                 ('https://example.com/?linkrot-control-7q2', 'LIVE_NO_BASELINE'), ('http://www.ietf.org/rfc/rfc1149.txt', 'REDIRECTED_ELSEWHERE'),
                 ('http://made-up-host-7q2.invalid/', 'DEAD_DNS'), ('https://example.com/no-such-page-7q2', 'DEAD_HTTP')]

def selftest():
    out = []
    def ok(name, cond): out.append((name, bool(cond)))
    ok('regdom www.bbc.co.uk', L.regdom('www.bbc.co.uk') == 'bbc.co.uk')
    ok('regdom ICANN only: foo.blogspot.com is on blogspot.com', L.regdom('foo.blogspot.com') == 'blogspot.com')
    ok('regdom deep host', L.regdom('a.b.cs.stanford.edu') == 'stanford.edu')
    ok('regdom IP literal', L.regdom('192.0.2.7') == '192.0.2.7')
    g = L.parse_robots('User-agent: *\nDisallow: /private\nAllow: /private/open\n\nUser-agent: HeuremenLLC-linkrot\nDisallow: /x*.pdf$\n')
    ok('robots: our own group is used, not *', L.robots_allows(g, '/private/a') is True and L.robots_allows(g, '/x1.pdf') is False)
    ok('robots: $ anchors the end', L.robots_allows(g, '/x1.pdf?v=2') is True)
    g2 = L.parse_robots('User-agent: *\nDisallow: /private\nAllow: /private/open\n')
    ok('robots: longest match wins', L.robots_allows(g2, '/private/a') is False and L.robots_allows(g2, '/private/open/b') is True)
    ok('robots: empty disallow allows', L.robots_allows(L.parse_robots('User-agent: *\nDisallow:\n'), '/a') is True)
    ok('robots: no group allows', L.robots_allows(L.parse_robots('User-agent: otherbot\nDisallow: /\n'), '/a') is True)
    ok('detector: parking name server', 'ns:sedoparking.com' in L.park_signals('www.ex7q2.com', ['ns1.sedoparking.com'], [], None, None, 0))
    ok('detector: redirect to a marketplace', any(s.startswith('host:afternic.com') for s in L.park_signals('ex7q2.com', [], ['http://ex7q2.com/', 'https://www.afternic.com/forsale/ex7q2.com'], 200, '', 10)))
    ok('detector: godaddy only on sale paths', not L.park_signals('ex7q2.com', [], ['https://www.godaddy.com/help'], 200, '', 10) and L.park_signals('ex7q2.com', [], ['https://www.godaddy.com/domainsearch/find?domainToCheck=ex7q2.com'], 200, '', 10))
    ok('detector: ww1 redirect', 'ww-redirect' in L.park_signals('ex7q2.com', [], ['http://ex7q2.com/', 'http://ww1.ex7q2.com/'], 200, '', 10))
    ok('detector: sale phrase on a short page', 'text:this domain is for sale' in L.park_signals('ex7q2.com', [], [], 200, '<p>this domain is for sale</p>', 5))
    ok('detector: sale phrase ignored on a long page', not L.park_signals('ex7q2.com', [], [], 200, '<p>this domain is for sale</p>', 5000))
    ok('detector: look-alike name jordan.com is not dan.com', not L.park_signals('ex7q2.com', [], [], 200, '<a href="https://www.jordan.com/x">x</a>', 5))
    ok('detector: subdomain asset counts', 'asset:sedoparking.com' in L.park_signals('ex7q2.com', [], [], 200, '<script src="https://img.sedoparking.com/a.js"></script>', 5000))
    ok('detector: a marketplace listed as itself is not parked', not L.park_signals('www.sedo.com', [], ['https://sedo.com/'], 200, '', 10))
    ok('detector: no signal on a plain page', not L.park_signals('ex7q2.com', ['ns1.example.net'], ['http://ex7q2.com/'], 200, '<p>hello world</p>', 2))
    a = b'<html><body>' + b' '.join(b'word%d' % i for i in range(200)) + b'</body></html>'
    c = b'<html><body>' + b' '.join(b'other%d' % i for i in range(200)) + b'</body></html>'
    ok('similarity: identical is 1', L.similarity(a, 'text/html', a, 'text/html')[0] == 1.0)
    ok('similarity: disjoint is 0', L.similarity(a, 'text/html', c, 'text/html')[0] == 0.0)
    ok('similarity: scripts are ignored', L.similarity(a, 'text/html', a.replace(b'<body>', b'<body><script>var x=1;</script>'), 'text/html')[0] == 1.0)
    return out

class _Srv(http.server.BaseHTTPRequestHandler):
    mode = 'parked'
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path == '/robots.txt':
            if self.server.mode == 'disallow': self._send(200, b'User-agent: *\nDisallow: /\n', 'text/plain')
            else: self._send(404, b'not found', 'text/plain')
            return
        if self.server.mode == 'parked': self._send(200, b'<html><head><title>ex</title></head><body><h1>This domain is for sale</h1></body></html>', 'text/html')
        else: self._send(200, b'<html><body>hello</body></html>', 'text/html')
    def _send(self, code, body, ct):
        self.send_response(code); self.send_header('Content-Type', ct); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)

def _serve(mode):
    s = http.server.ThreadingHTTPServer(('127.0.0.1', 0), _Srv); s.mode = mode; threading.Thread(target=s.serve_forever, daemon=True).start(); return s

def _hang():
    ls = socket.socket(); ls.bind(('127.0.0.1', 0)); ls.listen(5); held = []
    def loop():
        while True:
            try: c, _ = ls.accept(); held.append(c)
            except OSError: return
    threading.Thread(target=loop, daemon=True).start(); return ls

def _closed_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close(); return port

def run(verbose=False):
    """Returns (passed, readings). readings: list of (name, expected, got)."""
    rows = [(n, 'pass', 'pass' if c else 'FAIL') for n, c in selftest()]
    for u, want in LIVE_CONTROLS:
        r = L.check(u, first='live', history='none', keep_evidence=False); rows.append((u, want, r['state']))
    pk, ds, hg = _serve('parked'), _serve('disallow'), _hang()
    local = [('http://127.0.0.1:%d/' % _closed_port(), 'DEAD_CONNECT'), ('http://127.0.0.1:%d/' % hg.getsockname()[1], 'TIMEOUT'),
             ('http://127.0.0.1:%d/page' % ds.server_address[1], 'ROBOTS_DISALLOWED'), ('http://127.0.0.1:%d/' % pk.server_address[1], 'PARKED_OR_FOR_SALE')]
    for u, want in local:
        r = L.check(u, first='live', history='none', keep_evidence=False); rows.append((u, want, r['state']))
    saved = L.DOH; L.DOH = ('https://127.0.0.1:%d/dns-query' % _closed_port(),)
    try:
        r = L.check('http://made-up-host-7q2.invalid/', first='live', history='none', keep_evidence=False); rows.append(('resolver services forced unreachable', 'NOTHING_RETURNED', r['state']))
    finally:
        L.DOH = saved
    pk.shutdown(); ds.shutdown(); hg.close()
    passed = all(want == got for _, want, got in rows)
    if verbose:
        for n, want, got in rows: print(('OK   ' if want == got else 'FAIL ') + '%-58s want %-20s got %s' % (n[:58], want, got))
        print('GATE', 'PASSED' if passed else 'FAILED')
    return passed, rows

if __name__ == '__main__':
    sys.exit(0 if run(verbose=True)[0] else 1)
