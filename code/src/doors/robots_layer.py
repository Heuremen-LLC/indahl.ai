#!/usr/bin/env python3
"""DOORS, layer 1: what each site's robots.txt says to AI agents. Read from the site's own file, dated and hashed.

  robots_layer.py run      fetch every site in sources.json, write rows to rows_robots.jsonl and raw files to raw/
  robots_layer.py selftest

A row says, per agent, whether the file lets it fetch "/" and whether the file names that agent itself (NAMED) or leaves it to the
"*" group (DEFAULT). A missing robots.txt (404) is its own state, ALLOWED_BY_ABSENCE, and a file that cannot be read is CANNOT_TELL.
This layer reads the stated policy only. Terms of service and agent policies are layer 2.
"""
import hashlib, json, os, re, sys, time, urllib.request, urllib.robotparser, urllib.error

D = os.path.dirname(os.path.abspath(__file__))
UA = 'Mozilla/5.0 (compatible; heuremen-doors/0.1; +https://indahl.ai)'
AGENTS = ['GPTBot', 'ChatGPT-User', 'OAI-SearchBot', 'ClaudeBot', 'Claude-User', 'Claude-SearchBot', 'anthropic-ai', 'PerplexityBot',
          'Perplexity-User', 'Google-Extended', 'Googlebot', 'Applebot-Extended', 'Amazonbot', 'meta-externalagent', 'CCBot', 'Bytespider', 'cohere-ai']


def named_agents(text):
    return {m.strip().lower() for m in re.findall(r'(?im)^\s*user-agent\s*:\s*([^#\r\n]+)', text)}


def read_rules(text):
    rp = urllib.robotparser.RobotFileParser(); rp.parse(text.splitlines())
    names = named_agents(text); out = {}
    for a in AGENTS:
        ok = rp.can_fetch(a, '/')
        out[a] = dict(root='ALLOWED' if ok else 'DISALLOWED', group='NAMED' if a.lower() in names else 'DEFAULT')
    return out


def fetch(site):
    """Tries https://www.<site> first, then the bare name (14 Nov: bare united.com redirects and bare delta.com refuses connections,
    which first read as CANNOT_TELL for the site when it was our fetcher). Returns the last attempt, with its error text kept."""
    last = None
    for host in ('www.' + site, site):
        url = 'https://%s/robots.txt' % host
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return url, r.status, r.read(), r.geturl(), None
        except urllib.error.HTTPError as e:
            last = (url, e.code, b'', url, 'HTTP %d' % e.code)
            if e.code in (404, 410): return last
        except Exception as e:
            last = (url, None, b'', url, '%s: %s' % (type(e).__name__, str(e)[:160]))
    return last


def row(site, status, body, final, at, err=None):
    base = dict(site=site, read_at=at, http_status=status, final_url=final, sha256=hashlib.sha256(body).hexdigest() if body else None)
    if err: base['fetch_error'] = err
    if status == 200 and body:
        text = body.decode('utf-8', 'replace')
        if '<html' in text[:500].lower():
            return dict(base, state='CANNOT_TELL', why='the robots.txt address returned a web page, not a robots file')
        return dict(base, state='READ', agents=read_rules(text))
    if status in (404, 410):
        return dict(base, state='ALLOWED_BY_ABSENCE', why='no robots.txt (HTTP %d), so no stated rule' % status)
    return dict(base, state='CANNOT_TELL', why='could not read the file (HTTP %s)' % status)


def run():
    srcs = json.load(open(os.path.join(D, 'sources.json')))
    os.makedirs(os.path.join(D, 'raw'), exist_ok=True)
    at = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    with open(os.path.join(D, 'rows_robots.jsonl'), 'a') as out:
        for s in srcs['sites']:
            url, status, body, final, err = fetch(s['site'])
            r = row(s['site'], status, body, final, at, err); r['sector'] = s['sector']
            if body and status == 200:
                open(os.path.join(D, 'raw', '%s_%s.txt' % (s['site'], r['sha256'][:12])), 'wb').write(body)
            out.write(json.dumps(r) + '\n'); print(s['site'], r['state'], status)
            time.sleep(1)


def selftest():
    bad = 0
    def want(n, got, exp):
        nonlocal bad; ok = got == exp; bad += not ok; print(('PASS ' if ok else 'FAIL ') + n + ('' if ok else ' -> %r' % (got,)))
    t = 'User-agent: GPTBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n'
    r = read_rules(t)
    want('a named disallow reads DISALLOWED, NAMED', r['GPTBot'], dict(root='DISALLOWED', group='NAMED'))
    want('an unnamed agent falls to the default group', r['ClaudeBot'], dict(root='ALLOWED', group='DEFAULT'))
    r = read_rules('User-agent: *\nDisallow: /\n')
    want('a blanket disallow covers every agent as DEFAULT', r['Claude-User'], dict(root='DISALLOWED', group='DEFAULT'))
    want('404 reads ALLOWED_BY_ABSENCE, not ALLOWED', row('x', 404, b'', 'u', 't')['state'], 'ALLOWED_BY_ABSENCE')
    want('a server error reads CANNOT_TELL', row('x', 503, b'', 'u', 't')['state'], 'CANNOT_TELL')
    want('an HTML page at robots.txt reads CANNOT_TELL', row('x', 200, b'<html><body>hi</body></html>', 'u', 't')['state'], 'CANNOT_TELL')
    want('a read row carries the file hash', row('x', 200, t.encode(), 'u', 't')['sha256'], hashlib.sha256(t.encode()).hexdigest())
    print('selftest: %s' % ('all pass' if not bad else '%d FAILED' % bad)); return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:] or ['selftest']
    sys.exit(selftest() if a[0] == 'selftest' else run() if a[0] == 'run' else print(__doc__))
