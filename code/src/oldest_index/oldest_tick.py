#!/usr/bin/env python3
"""oldest_tick.py: OLDEST per PLAN.md. Registration age (RDAP), first archive capture, and continuity of the home page for the first 30,000 domains of Tranco list Y83YG."""
import os, sys, re, json, time, math, collections, html.parser, urllib.request, urllib.parse, urllib.error, datetime, random, statistics
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H); sys.path.insert(0, H); os.makedirs('data', exist_ok=True)
import heuremen_kit as K
if not K.plan_committed(os.path.join(H, 'PLAN.md')): print('oldest: plan not committed'); sys.exit(0)
UA = {'User-Agent': 'heuremen-oldest/0.1 (+https://indahl.ai/oldest)'}; N = 30000; LIST = 'Y83YG'; CUT = '2000-01-01'
def fetch(u, n=3, to=30, maxb=600000, headers=None):
    """-> (status, final_url, body bytes). status None = no connection."""
    for i in range(n):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=dict(UA, **(headers or {}))), timeout=to); return r.status, r.geturl(), r.read(maxb)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < n - 1: time.sleep(4 * (i + 1)); continue
            return e.code, u, b''
        except Exception: time.sleep(2 * (i + 1))
    return None, u, b''
class TextOf(html.parser.HTMLParser):
    def __init__(s): super().__init__(); s.skip = 0; s.out = []
    def handle_starttag(s, t, a):
        if t in ('script', 'style', 'noscript', 'template'): s.skip += 1
    def handle_endtag(s, t):
        if t in ('script', 'style', 'noscript', 'template') and s.skip: s.skip -= 1
    def handle_data(s, d):
        if not s.skip: s.out.append(d)
def words(b):
    p = TextOf()
    try: p.feed(b.decode('utf-8', 'replace'))
    except Exception: pass
    return re.findall(r"[a-z0-9']+", ' '.join(p.out).lower())
def shingles(w): return {' '.join(w[i:i + 3]) for i in range(len(w) - 2)}
PARK = ('this domain is for sale', 'domain for sale', 'buy this domain', 'parked free', 'domain parking')
def classify(first_b, now_b):
    a, b = words(first_b), words(now_b)
    if any(p in ' '.join(b) for p in PARK): return 'PARKED', None
    if len(a) < 30 or len(b) < 30: return 'NO_TEXT', None
    A, B = shingles(a), shingles(b); j = len(A & B) / len(A | B) if A | B else 0
    return ('MATCHES' if j >= 0.30 else 'CHANGED'), round(j, 3)
def rdap_base():
    d = json.loads(fetch('https://data.iana.org/rdap/dns.json')[2] or b'{}'); m = {}
    for svc in d.get('services', []):
        for t in svc[0]: m[t] = svc[1][0]
    return m
def rdap_reg(base, dom):
    st, _, b = fetch(base.rstrip('/') + '/domain/' + dom)
    if st == 200:
        try:
            for e in json.loads(b).get('events', []):
                if e.get('eventAction') == 'registration': return e['eventDate'][:10], None
        except Exception: pass
        return None, 'no registration event'
    return None, 'RDAP status %s' % st
def cdx(dom):
    """-> (first_ts, first_url, years, reason). NOTHING_RETURNED reasons never read as no capture."""
    for host in (dom, 'www.' + dom):
        st, _, b = fetch('https://web.archive.org/cdx/search/cdx?url=%s&output=json&filter=statuscode:200&collapse=timestamp:4&fl=timestamp,original&limit=300' % host, to=60)
        if st != 200 or not b.strip().startswith(b'['): return None, None, 0, 'archive answered %s' % st
        rows = json.loads(b)[1:]
        if rows: return rows[0][0], rows[0][1], len(rows), None
        time.sleep(1)
    return None, None, 0, 'no capture'
# ---- known-good
def gate():
    ok = True; why = []
    base = rdap_base(); r, _ = rdap_reg(base.get('com', ''), 'symbolics.com'); g1 = r == '1985-03-15'; ok &= g1
    ts, _, yrs, rs = cdx('info.cern.ch'); g2 = bool(ts and ts <= '19980101'); ok &= g2
    t1 = b'<html><body>' + (' '.join('alpha%d beta gamma delta' % i for i in range(60))).encode() + b'</body></html>'
    c1 = classify(t1, t1)
    t2 = b'<p>' + (' '.join('zebra%d quokka llama' % i for i in range(60))).encode() + b'</p>'; c2 = classify(t1, t2)
    ws = words(t1); ws2 = ws[:]; 
    for i in range(0, len(ws2), 10): ws2[i] = 'changed%d' % i
    c3 = classify(t1, ('<p>' + ' '.join(ws2) + '</p>').encode())
    g3 = c1 == ('MATCHES', 1.0) and c2[0] == 'CHANGED' and c2[1] < 0.05 and c3[0] in ('MATCHES', 'CHANGED') and 0.40 <= (c3[1] or 0) <= 0.90
    g4 = classify(t1, b'<p>This domain is for sale. ' + b'word ' * 60 + b'</p>')[0] == 'PARKED' and classify(t1, b'<p>short page</p>')[0] == 'NO_TEXT'
    ok &= g3 and g4
    print('oldest: gate', 'passed' if ok else 'FAILED', dict(rdap=g1, cdx=g2, text=g3, bins=g4, symbolics=r, cern=ts), flush=True); return ok
if not gate(): sys.exit(1)
# ---- population
lp = 'data/tranco_%s_%d.csv' % (LIST, N)
if not os.path.exists(lp):
    st, _, b = fetch('https://tranco-list.eu/download/%s/1000000' % LIST, maxb=80000000, to=300)
    rows = b.decode().split('\n')[:N]; open(lp, 'w').write('\n'.join(rows) + '\n')
doms = [l.split(',')[1].strip() for l in open(lp) if ',' in l][:N]; print('oldest: population', len(doms), flush=True)
base = rdap_base(); rd = json.load(open('data/rdap.json')) if os.path.exists('data/rdap.json') else {}
for i, d in enumerate(doms):
    if d in rd: continue
    tld = d.rsplit('.', 1)[-1]; b = base.get(tld)
    if not b: rd[d] = dict(reg=None, why='no RDAP service for .' + tld, cls='NOT_COMPARABLE')
    else:
        reg, why = rdap_reg(b, d); rd[d] = dict(reg=reg, why=why, cls='OK' if reg else 'NOTHING_RETURNED'); time.sleep(0.3)
    if i % 500 == 499: json.dump(rd, open('data/rdap.json', 'w')); print('oldest: rdap', i + 1, flush=True)
json.dump(rd, open('data/rdap.json', 'w'))
old = sorted([d for d in doms if rd[d].get('reg') and rd[d]['reg'] < CUT], key=lambda d: rd[d]['reg']); print('oldest: registered before %s: %d' % (CUT, len(old)), flush=True)
oc = json.load(open('data/old.json')) if os.path.exists('data/old.json') else {}
for i, d in enumerate(old):
    if d in oc: continue
    rec = dict(reg=rd[d]['reg'])
    st, fin, body = None, None, b''
    for u in ('https://%s/' % d, 'http://%s/' % d):
        st, fin, body = fetch(u, n=2); 
        if st: break
    host = (urllib.parse.urlparse(fin).hostname or '') if st else ''
    if st is None: rec['live'] = 'UNREACHABLE'
    elif st >= 400: rec['live'] = 'ERROR'; rec['status'] = st
    elif host == d or host.endswith('.' + d): rec['live'] = 'LIVE_SAME_HOST'
    else: rec['live'] = 'LIVE_ELSEWHERE'; rec['final_host'] = host
    time.sleep(0.3)
    ts, url, yrs, why = cdx(d); rec.update(first=ts, years=yrs, cdx_why=why)
    if rec['live'] == 'LIVE_SAME_HOST' and ts:
        s2, f2, fb = fetch('https://web.archive.org/web/%sid_/%s' % (ts, url), to=60); time.sleep(1)
        if s2 == 200: rec['cont'], rec['overlap'] = classify(fb, body)
        else: rec['cont'], rec['overlap'] = 'NOTHING_RETURNED', None
    oc[d] = rec
    if i % 20 == 19: json.dump(oc, open('data/old.json', 'w')); print('oldest: old set', i + 1, 'of', len(old), flush=True)
json.dump(oc, open('data/old.json', 'w'))
cls = collections.Counter(v['live'] for v in oc.values()); cont = collections.Counter(v.get('cont') for v in oc.values() if v['live'] == 'LIVE_SAME_HOST')
cmp = cont['MATCHES'] + cont['CHANGED']; lo, hi = K.wilson(cont['MATCHES'], cmp) if cmp else (0, 1)
dec = collections.Counter((rd[d]['reg'][:3] + '0s') for d in doms if rd[d].get('reg'))
top = [dict(domain=d, registered=rd[d]['reg'], today=oc[d]['live'], first_capture=(oc[d].get('first') or '')[:8] or None, years_with_capture=oc[d].get('years'), page=oc[d].get('cont'), overlap=oc[d].get('overlap')) for d in old[:100] if d in oc]
out = dict(updated=time.strftime('%d %b %H:%M', time.gmtime()), gate='passed', list_id=LIST, population=len(doms), with_registration=sum(1 for v in rd.values() if v.get('reg')), nothing_returned=sum(1 for v in rd.values() if v['cls'] == 'NOTHING_RETURNED'), no_rdap=sum(1 for v in rd.values() if v['cls'] == 'NOT_COMPARABLE'),
           old_set=len(old), today=dict(cls), continuity=dict(cont), matches_share=dict(of=cmp, n=cont['MATCHES'], share=round(cont['MATCHES'] / cmp, 4) if cmp else None, share_lo=round(lo, 4), share_hi=round(hi, 4)), decades=dict(sorted(dec.items())), oldest=top)
json.dump(out, open('summary_oldest.json', 'w'), indent=1)
print('oldest: done;', len(old), 'old;', dict(cls), dict(cont), flush=True)
