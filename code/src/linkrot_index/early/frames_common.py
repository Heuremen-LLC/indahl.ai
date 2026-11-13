"""frames_common.py: shared pieces for building sampling frames and drawing samples (PLAN.md Addendum 3). No link is checked here.
Draw rule: every unit gets the key SHA-256(seed + '|' + sample + '|' + unit id); a sample is the units with the smallest keys, and links
are checked in key order, so any partial pass is itself a random draw. The seed is the randomness of a public drand round published
after the plan was committed (data/early/seed.json)."""
import os, re, json, html, hashlib, urllib.parse, urllib.request, time
UA = 'HeuremenLLC-linkrot/1.0 (https://indahl.ai)'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DATA = os.path.join(ROOT, 'data', 'early')
EXAMPLE_HOSTS = re.compile(r'(^|\.)(example\.(com|net|org|edu)|[^.]*\.example|[^.]*\.invalid|[^.]*\.test|[^.]*\.localhost|localhost)$', re.I)

def seed():
    p = os.path.join(DATA, 'seed.json')
    if not os.path.exists(p): raise SystemExit('no seed yet: run early/seed.py after the plan is committed')
    return json.load(open(p))['randomness']

def key(sd, sample, unit): return hashlib.sha256(('%s|%s|%s' % (sd, sample, unit)).encode()).hexdigest()

def norm(u):
    """Light normalisation of a listed address: whitespace removed, entities decoded, scheme and host lower case, default port and
    fragment dropped, an empty path becomes '/'. Path and query are kept as listed. Returns None for anything that is not http(s)."""
    u = html.unescape(re.sub(r'\s+', '', u or '')).strip('<>"\'')
    try: p = urllib.parse.urlsplit(u)
    except ValueError: return None
    if p.scheme.lower() not in ('http', 'https') or not p.hostname: return None
    host = p.hostname.lower().rstrip('.')
    if not re.match(r'^[a-z0-9.\-\[\]:_]+$', host) and not host.isascii(): return None
    try: port = p.port
    except ValueError: return None
    net = host if port is None or (p.scheme.lower() == 'http' and port == 80) or (p.scheme.lower() == 'https' and port == 443) else '%s:%d' % (host, port)
    return urllib.parse.urlunsplit((p.scheme.lower(), net, p.path or '/', p.query, ''))

def get(url, timeout=60, tries=3, gap=1.0):
    for i in range(tries):
        try:
            time.sleep(gap)
            return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=timeout).read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504): time.sleep(60); continue
            raise
        except Exception:
            time.sleep(10)
    raise RuntimeError('failed after %d tries: %s' % (tries, url))

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path + '.tmp', 'w'), indent=1); os.replace(path + '.tmp', path)
